from collections.abc import Callable
from time import perf_counter_ns


def timed[T](func: Callable[[], T]) -> tuple[T, int]:
    """Measure the runtime of a function."""
    start = perf_counter_ns()
    return func(), perf_counter_ns() - start


def human_readable_duration(nanoseconds: int) -> str:
    minutes = int(nanoseconds // 60_000_000_000)
    nanoseconds %= 60_000_000_000
    seconds = int(nanoseconds // 1_000_000_000)
    nanoseconds %= 1_000_000_000
    milliseconds = int(nanoseconds // 1_000_000)
    nanoseconds %= 1_000_000
    microseconds = int(nanoseconds // 1_000)
    nanoseconds %= 1_000
    if minutes:
        return f"{minutes:d}:{seconds:02d}.{milliseconds:03d} minutes"
    if seconds:
        return f"{seconds:d}.{milliseconds:03d} seconds"
    if milliseconds:
        return f"{milliseconds:d}.{microseconds:03d} ms"
    return f"{microseconds:d}.{nanoseconds:03d} µs"
