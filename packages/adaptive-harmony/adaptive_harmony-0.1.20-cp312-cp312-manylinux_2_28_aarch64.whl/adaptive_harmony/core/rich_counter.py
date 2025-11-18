#!/usr/bin/env python

"""
Demonstrates a progress bar on the left and a simple execution counter
(without a total) on the right.
"""

from dataclasses import dataclass
from rich.live import Live
from rich.panel import Panel
from rich.console import Group
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    TaskID,
)
from rich.table import Table


class ProgressCounterRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._main_counter_instance: "ProgressCounter | None" = None
        self._wrappers: dict[str, "ProgressCounterWrapper"] = {}
        self._initialized = True

    def get_main_counter(self) -> "ProgressCounter | None":
        return self._main_counter_instance

    def set_main_counter(self, counter: "ProgressCounter | None"):
        self._main_counter_instance = counter

    def get_wrappers(self) -> dict[str, "ProgressCounterWrapper"]:
        return self._wrappers

    def clear_wrappers(self):
        self._wrappers.clear()

    def get_wrapper(self, key: str) -> "ProgressCounterWrapper | None":
        return self._wrappers.get(key)

    def set_wrapper(self, key: str, wrapper: "ProgressCounterWrapper"):
        self._wrappers[key] = wrapper

    def reset(self):
        self._main_counter_instance = None
        self._wrappers.clear()


@dataclass
class CoroutineGroup:

    def __init__(self):
        self.progress = Progress(
            "{task.description}",
            SpinnerColumn(),
            TextColumn("[magenta]{task.completed:n} steps"),
        )
        self.coro_desc_to_task_id: dict[str, TaskID] = {}

    def __contains__(self, s: str):
        return s in self.coro_desc_to_task_id

    def create_coro(self, desc: str):
        self.coro_desc_to_task_id[desc] = self.progress.add_task(desc)

    def increment_coro(self, desc: str):
        if desc not in self.coro_desc_to_task_id:
            self.create_coro(desc)
        self.progress.advance(self.coro_desc_to_task_id[desc])


class ProgressCounter:

    def __init__(self, main_job_name: str, total_tasks: int):
        registry = ProgressCounterRegistry()
        assert registry.get_main_counter() is None, "Only one main counter instance is allowed"
        self.total_tasks = total_tasks

        # construct the left pannel that will give the state of the batch at a glance
        self.overall_progress = Progress(
            "{task.description}",
            BarColumn(),
            TextColumn("[magenta]{task.completed:n} steps"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
        )
        self.overall_task = self.overall_progress.add_task(main_job_name, total=self.total_tasks)
        self.overall_panel = Panel(
            self.overall_progress, title="Overall Progress", border_style="green", padding=(1, 1, 0, 1)
        )
        self.additional_padding_for_overall_panel = 0

        # construct the right panel, we are rendering a bunch of groups, that way if during an async_map we encounter
        # a second async map we can nest the progress report in a group
        self.coro_groups: dict[str, CoroutineGroup] = {}
        self.groups = Group()
        self.jobs_panel = Panel(self.groups, title="[b]Jobs", border_style="red", padding=(1, 2))
        # we add the main group of coroutines, it is destined for all awaits encountered in the body of the async map
        # (but not those that are nested)
        self._create_coroutine_group("main", False)

        # Construct the general table
        self.progress_table = Table.grid()
        self.progress_table.add_row(self.overall_panel, self.jobs_panel)

    def _create_coroutine_group(self, group_name: str, add_progress_for_group: bool):
        new_group = CoroutineGroup()
        self.groups.renderables.append(new_group.progress)
        self.coro_groups[group_name] = new_group
        if add_progress_for_group:
            self._create_task(group_name, group_name)

    def _create_task(self, task_description: str, group_name: str):
        group = self.coro_groups[group_name]
        group.create_coro(task_description)
        self.additional_padding_for_overall_panel += 1
        self.overall_panel.padding = (1, 1, self.additional_padding_for_overall_panel, 1)

    def _increment_task(self, task_description: str, group_name: str):
        if task_description not in self.coro_groups[group_name]:
            self._create_task(task_description, group_name)
        self.coro_groups[group_name].increment_coro(task_description)

    def create_task(self, task_description: str):
        return self._create_task(task_description, group_name="main")

    def increment_task(self, task_description: str):
        return self._increment_task(task_description, group_name="main")

    def increment_total_counter(self):
        self.overall_progress.advance(0)

    def is_done(self):
        return self.overall_progress.finished

    def __enter__(self):
        self.live = Live(self.progress_table, refresh_per_second=10).__enter__()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.live.__exit__(exc_type, exc_value, exc_traceback)
        registry = ProgressCounterRegistry()
        assert registry.get_main_counter() is not None, "Weird state"
        # we clear both the main counter and any wrapper that would point to the old counter
        registry.reset()


class ProgressCounterWrapper(ProgressCounter):
    """Used to wrap a preexisting counter, needed to have simple logic in case an async_map is used inside an async_map_batch"""

    def wrap_task_description(self, s: str):
        return f"  {s}"

    def __init__(self, inner: ProgressCounter, main_function_name: str):
        self.inner = inner
        self.inner._create_coroutine_group(main_function_name, True)
        self.main_function_name = main_function_name

    def create_task(self, task_description: str):
        return self.inner._create_task(self.wrap_task_description(task_description), group_name=self.main_function_name)

    def increment_task(self, task_description: str):
        return self.inner._increment_task(
            self.wrap_task_description(task_description), group_name=self.main_function_name
        )

    def increment_total_counter(self):
        return self.inner._increment_task(self.main_function_name, self.main_function_name)

    def __enter__(self):
        # do nothing, the inner progress counter has already been initialized
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # do nothing, the inner progress counter will be exited later
        ...


def get_progress_counter_or_wrapper(main_job_name: str, total_samples: int):
    registry = ProgressCounterRegistry()
    main_counter = registry.get_main_counter()

    if main_counter is None:
        main_counter = ProgressCounter(main_job_name, total_samples)
        registry.set_main_counter(main_counter)
        return main_counter
    else:
        wrapper = registry.get_wrapper(main_job_name)
        if wrapper is None:
            wrapper = ProgressCounterWrapper(main_counter, main_job_name)
            registry.set_wrapper(main_job_name, wrapper)
        return wrapper
