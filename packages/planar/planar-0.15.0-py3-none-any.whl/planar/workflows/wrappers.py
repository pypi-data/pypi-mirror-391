from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable, Coroutine, Generic
from uuid import UUID

from planar.utils import P, R, T, U
from planar.workflows.models import Workflow


@dataclass(kw_only=True)
class Wrapper(Generic[P, T, U, R]):
    original_fn: Callable[P, Coroutine[T, U, R]]
    wrapped_fn: Callable[P, Coroutine[T, U, R]]
    __doc__: str | None

    def __post_init__(self):
        self.__doc__ = self.original_fn.__doc__

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Coroutine[T, U, R]:
        return self.wrapped_fn(*args, **kwargs)

    @property
    def name(self):
        return self.wrapped_fn.__name__

    @property
    def __name__(self):
        return self.original_fn.__name__


@dataclass
class CronSchedule:
    """Represents a single cron schedule for a workflow."""

    cron_expr: str
    args: list
    kwargs: dict
    idempotency_key_suffix: str
    window: timedelta | None
    start_time: datetime | None = None


@dataclass(kw_only=True)
class WorkflowWrapper(Wrapper[P, T, U, R]):
    function_name: str
    start: Callable[P, Coroutine[T, U, Workflow]]
    start_step: Callable[P, Coroutine[T, U, UUID]]
    wait_for_completion: Callable[[UUID], Coroutine[T, U, R]]
    is_interactive: bool
    cron_schedules: list[CronSchedule] = field(default_factory=list)


@dataclass(kw_only=True)
class StepWrapper(Wrapper[P, T, U, R]):
    wrapper: Callable[P, Coroutine[T, U, R]]
    auto_workflow: WorkflowWrapper[P, T, U, R]
