import asyncio
import functools
import itertools
import json
import linecache
from adaptive_harmony.core.rich_counter import ProgressCounter, get_progress_counter_or_wrapper
from adaptive_harmony.metric_logger import Logger, StdoutLogger
import numpy as np
import random

from loguru import logger
from pathlib import Path
from rich.progress import Progress, TaskID
from tqdm.auto import tqdm
from typing import Callable, Iterator, Iterable, TypedDict, NamedTuple, List, Dict, Any, Coroutine, TypeVar

from adaptive_harmony import InferenceModel, TrainingModel, StringThread


S = TypeVar("S")
T = TypeVar("T")


def describe_coroutine(coro):
    """
    Extracts and returns the current line of code being executed in a coroutine.

    Args:
        coro: The coroutine object to inspect

    Returns:
        str: The current line of code being executed, or None if the coroutine
             has finished execution
    """

    frame = getattr(coro, "cr_frame", None)
    if frame is None:
        return

    filename = frame.f_code.co_filename
    lineno = frame.f_lineno

    # Try to get the exact source line
    line = linecache.getline(filename, lineno).strip().replace("[", "\\[")

    return line


async def wrap_coroutine_with_progress[T](coroutine: Coroutine[Any, Any, T], progress_counter: ProgressCounter) -> T:
    """
    Wraps a coroutine with progress tracking functionality.

    This function executes a coroutine while tracking its progress using the
    provided progress tracker. It handles the coroutine's execution state and
    ensures proper progress updates.

    Args:
        coroutine: The coroutine to wrap and execute
        progress_tracker: Progress tracking instance to use for updates

    Returns:
        The final result of the coroutine execution

    Raises:
        RuntimeError: If asyncio.wait returns no done tasks
    """
    result_to_send_into_target = None
    coro_name = getattr(coroutine, "__name__", "anonymous_coroutine")

    try:
        while True:
            yielded = coroutine.send(result_to_send_into_target)
            coroutine_desc = describe_coroutine(coroutine) or "Unknown"

            # Handle a bare `yield` (i.e., result is None): relinquish control
            # for one event loop iteration and then resume by sending None.
            if yielded is None:
                await asyncio.sleep(0)
                progress_counter.increment_task(coroutine_desc)
                result_to_send_into_target = None
                continue

            # If the coroutine yielded an awaitable/future, await it and send
            # the resulting value back into the coroutine on the next step.
            if asyncio.isfuture(yielded):
                done_tasks, pending_tasks = await asyncio.wait([yielded])
                progress_counter.increment_task(coroutine_desc)
                assert len(done_tasks) == 1
                assert len(pending_tasks) == 0

                if not done_tasks:
                    raise RuntimeError(
                        f"asyncio.wait returned no done tasks for {coro_name} " f"while awaiting {yielded}"
                    )

                completed_task = done_tasks.pop()
                result_to_send_into_target = completed_task.result()
                continue
            # Any other yielded object is invalid.
            raise RuntimeError(
                f"{coro_name} got bad yield: {yielded!r}, only expect Futures or None in case of bare yield (asyncio.sleep(0))"
            )

    except StopIteration as e:
        progress_counter.increment_total_counter()
        return e.value
    finally:
        coroutine.close()


async def async_map_batch[S, T](
    f: Callable[[S], Coroutine[Any, Any, T]],
    data: Iterator[S],
    batch_size: int,
    max_failure_fraction: float = 0.5,
) -> List[T]:
    """
    Process items from an iterator in batches using concurrent coroutines.

    This function processes items from an iterator in batches, executing the
    provided coroutine function concurrently for each item. It excludes failing
    samples until it can create a new batch of results of size # batch size.
    If more than max_failure_fraction % of # batch size tasks fail in the process
    of creating a new batch, the function will raise the last exception encountered.
    Results are not ordered.

    Args:
        f: Coroutine function to apply to each item
        data: Iterator of items to process
        batch_size: Number of items to process in each batch

    Returns:
        List of results from successful task executions

    Note:
        - Failed tasks are not retried
        - If more than max_failure_fraction of # batch size tasks fail, the function fails
        - Tasks are automatically cancelled if the function exits early
    """
    batch_items_from_iterator = list(itertools.islice(data, batch_size))
    num_items = len(batch_items_from_iterator)

    with get_progress_counter_or_wrapper(f"async_map_batch({f.__name__})", batch_size) as counter:
        final_results: list[Any] = [None] * num_items
        active_tasks_this_batch: Dict[asyncio.Task, int] = {}

        num_retries = 0

        for i, item_value in enumerate(batch_items_from_iterator):
            task: asyncio.Task[T] = asyncio.create_task(wrap_coroutine_with_progress(f(item_value), counter))
            active_tasks_this_batch[task] = i

        try:
            while active_tasks_this_batch:
                done_tasks, _ = await asyncio.wait(active_tasks_this_batch.keys(), return_when=asyncio.FIRST_COMPLETED)

                for task_item in done_tasks:
                    original_batch_slot_idx = active_tasks_this_batch.pop(task_item)

                    try:
                        result: T = await task_item
                        final_results[original_batch_slot_idx] = result
                    except Exception as ex:
                        try:
                            if num_retries > batch_size * max_failure_fraction:
                                # if more than 50% of a batch fail we'll just go on.
                                raise ex

                            logger.debug(ex)
                            retry_item_value: S = next(data)
                            new_retry_task: asyncio.Task[T] = asyncio.create_task(
                                wrap_coroutine_with_progress(f(retry_item_value), counter)
                            )
                            active_tasks_this_batch[new_retry_task] = original_batch_slot_idx
                            num_retries += 1
                        except StopIteration:
                            ...
        finally:
            tasks_to_cancel = list(active_tasks_this_batch.keys())
            for task_to_cancel in tasks_to_cancel:
                task_to_cancel.cancel()

            if tasks_to_cancel:
                await asyncio.gather(*tasks_to_cancel, return_exceptions=True)

        if num_retries > 0:
            print(f"WARNING: had to retry {num_retries} times to get a batch of {batch_size}")
        ret = [res for res in final_results if res is not None]

        print(f"Final number tasks with non-None results: {len(ret)}")

        return ret


def log_args(func):
    """
    A Python decorator that logs the arguments of the decorated function
    to experiment tracking tools (wandb, mlflow) or stdout.

    Attempts to log to wandb if available and initialized, then to mlflow
    if available and has an active run. If neither is available, logs to stdout.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import inspect

        # Helper to check serializability and prepare value
        def prepare_value(value):
            # we need to log the model builder args here because they are not serializable by default
            if isinstance(value, list) and len(value) > 100:
                # exclude long lists since we want to skip datasets
                return None
            if isinstance(value, InferenceModel) or isinstance(value, TrainingModel):
                return value.get_builder_args()
            else:
                # Check if the value itself is a complex object that might not be fully serializable
                try:
                    json.dumps({"test_key": value})
                    return value
                except (TypeError, OverflowError):
                    return None

        # Get function arguments once
        sig = inspect.signature(func)
        bound_args = sig.bind_partial(*args, **kwargs)
        bound_args.apply_defaults()
        all_args = bound_args.arguments

        # find the loggers that are given to recipe, if None are found, we will log to stdout
        loggers = [v for v in all_args.values() if isinstance(v, Logger)]
        if not loggers:
            loggers.append(StdoutLogger())

        # get loggable args only
        loggable_args = {k: new_v for k, v in all_args.items() if (new_v := prepare_value(v)) is not None}

        for logger_instance in loggers:
            logger_instance.log_config(loggable_args)

        return func(*args, **kwargs)

    return wrapper


async def async_map[S, T](f: Callable[[S], Coroutine[Any, Any, T]], data: Iterable[S]) -> list[T]:
    """
    Process all items in an iterable concurrently using the provided coroutine function.

    Args:
        f: Coroutine function to apply to each item
        data: Iterable of items to process

    Returns:
        List of results from all task executions
    """

    # Check if a Progress bar is already active
    with get_progress_counter_or_wrapper(f"async_map({f.__name__})", len(list(data))) as counter:
        all_tasks = [asyncio.create_task(wrap_coroutine_with_progress(f(item), counter)) for item in data]
        results = await asyncio.gather(*all_tasks)
    return results


async def async_map_fallible[S, T](f: Callable[[S], Coroutine[Any, Any, T]], data: Iterable[S]) -> list[T]:
    """
    Process all items in an iterable concurrently using the provided coroutine function.

    Args:
        f: Coroutine function to apply to each item
        data: Iterable of items to process

    Returns:
        List of results from all task executions
    """

    async def wrap_coroutine_with_error_handling(coro: Coroutine[Any, Any, T]) -> tuple[T, bool]:
        try:
            result = await coro
            return result, True
        except Exception:
            return None, False  # type: ignore

    with get_progress_counter_or_wrapper(f"async_map_fallible({f.__name__})", len(list(data))) as counter:
        all_tasks = [
            asyncio.create_task(wrap_coroutine_with_error_handling(wrap_coroutine_with_progress(f(item), counter)))
            for item in data
        ]
        results = await asyncio.gather(*all_tasks)

    return [result for result, success in results if success]


def get_minibatches[T](dataset: list[T], mini_batch_size: int, number_of_epochs: int) -> list[list[T]]:
    all_batches: list[list[T]] = []

    for _ in range(number_of_epochs):
        shuffled_dataset = random.sample(dataset, k=len(dataset))

        epoch_batches: list[list[T]] = []
        for i in range(0, len(shuffled_dataset), mini_batch_size):
            batch = shuffled_dataset[i : i + mini_batch_size]
            epoch_batches.append(batch)
        all_batches.extend(epoch_batches)

    return all_batches


def sample_data[T](data: list[T], epochs: float) -> list[T]:
    num_samples = len(data) * epochs
    return [data[x] for x in np.random.permutation(len(data))[: int(num_samples)]]


def weighted_mean(values: list[list[float]], weights: list[list[float]]) -> float:
    return np.average(np.concatenate(values), weights=np.concatenate(weights)).item()


def stringify_thread(thread: StringThread, sep: str = "\n\n") -> str:
    """Convert StringThread to readable text format."""
    turns = thread.get_turns()
    return sep.join([f"[{turn.role}]\n{turn.content}" for turn in turns])


SingleTurnShot = TypedDict("SingleTurnShot", {"user": dict[str, str], "assistant": dict[str, str]})


class TurnTemplates(NamedTuple):
    system: str | None
    user: str | None
    assistant: str | None
    shots: list[SingleTurnShot] | None


def turn_templates_from_dir(root_dir: str) -> TurnTemplates:
    """
    Returns system, user and assistant turn string templates from a directory, as well as a list of shot dicts.
    Expects files to be named system.md, user.md, assistant.md and shots.jsonl.
    Returns None for any turn template file that does not exist.
    """
    root_path = Path(root_dir)
    expected_files = ["system.md", "user.md", "assistant.md", "shots.jsonl"]
    missing_templates = []
    turn_templates: list[str | list[SingleTurnShot] | None] = []

    for file in expected_files:
        path = root_path / file
        if not path.exists():
            missing_templates.append(file)
            turn_templates.append(None)
        else:
            if file == "shots.jsonl":
                shots = []
                for line in path.read_text().splitlines():
                    data = json.loads(line)
                    shot = SingleTurnShot(user=data["user"], assistant=data["assistant"])
                    shots.append(shot)
                turn_templates.append(shots)
            else:
                turn_templates.append(path.read_text())

    # Ensure proper typing: first 3 are str|None, last is list[SingleTurnShot]|None
    system, user, assistant, shots = turn_templates
    return TurnTemplates(
        system=system if isinstance(system, str) else None,
        user=user if isinstance(user, str) else None,
        assistant=assistant if isinstance(assistant, str) else None,
        shots=shots if isinstance(shots, list) else None,
    )
