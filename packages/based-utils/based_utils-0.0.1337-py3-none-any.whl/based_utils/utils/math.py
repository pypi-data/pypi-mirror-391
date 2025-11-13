import math
from functools import cached_property


def trim(n: float, lower: float, upper: float) -> float:
    return min(max(lower, n), upper)


class Bounds:
    def __init__(self, begin: float, end: float) -> None:
        self._begin = begin
        self._end = end

    @cached_property
    def _span(self) -> float:
        return self._end - self._begin

    def interpolate(self, f: float) -> float:
        return self._begin + self._span * f

    def inverse_interpolate(self, n: float, *, inside: bool = True) -> float:
        try:
            f = (n - self._begin) / self._span
        except ZeroDivisionError:
            return 0.0
        return trim(f, 0.0, 1.0) if inside else f


class CyclicBounds(Bounds):
    def __init__(self, begin: float, end: float, period: float = math.pi * 2) -> None:
        begin, end = begin % period, end % period

        # To ensure interpolation over the smallest angle,
        # phase shift {begin} over whole periods, such that the
        # (absolute) difference between {begin} <-> {end} <= 1/2 {period}.
        #
        #                          v------ period ------v
        #    -1                    0                    1                    2
        #     |                    |                    |     begin < end:   |
        # Old:|                    |   B ~~~~~~~~~> E   |                    |
        # New:|                    |                E <~|~~ B' = B + period  |
        #     |    begin > end:    |                    |                    |
        # Old:|                    |   E <~~~~~~~~~ B   |                    |
        # New:|  B - period =  B'~~|~> E                |                    |

        if abs(end - begin) > period / 2:
            begin += period if begin < end else -period

        super().__init__(begin, end)
        self._period = period

    def interpolate(self, f: float) -> float:
        return super().interpolate(f) % self._period

    def inverse_interpolate(self, n: float, *, inside: bool = True) -> float:
        return super().inverse_interpolate(n % self._period, inside=inside)
