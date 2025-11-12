"""
IntegerSet datastructure.  A sparse representation of sets of integers.
"""

from itertools import chain
from collections import deque
from copy import deepcopy
from sortedcontainers import SortedList
from .interval import Interval


class IntervalSortAdapter(Interval):
    """
    This class adapts Interval in a way that is sortable by SortedList key
    function.  The Interval class treats __lt__ (<) as a subset test, but we
    want to sort the intervals based on start/end so we can binary search
    later.  This class overrides the __lt__ method so they can be sorted.
    """

    def __init__(self, interval):
        super().__init__(interval.start, interval.end)

    def __lt__(self, other):
        """
        Compare primarily based on start, use end as a tie-breaker.
        """
        if self.start == other.start:
            return self.end < other.end

        return self.start < other.start


class IntegerSet:
    """
    Set of integers with a sparse implementation.  This is suitable for sets
    with a large number of contiguous integers.
    """

    def __init__(self, *intervals):
        intervals = map(lambda interval: Interval(*interval), intervals)
        self.intervals = SortedList(intervals, key=self._interval_sort_function)
        self.consolidate_intervals()

    def __repr__(self):
        intervals = ", ".join(str(range_) for range_ in self.intervals)
        return f"IntegerSet({intervals})"

    def __iter__(self):
        for interval in self.intervals:
            yield from range(interval.start, interval.end + 1)

    def __eq__(self, other):
        """
        An integer set is equal if all of their intervals are equal.
        """
        return self.intervals == other.intervals

    def __or__(self, other):
        """
        Union.
        """
        return self.union(other)

    def __and__(self, other):
        """
        Intersection.
        """
        return self.intersection(other)

    def __sub__(self, other):
        """
        Subtraction.
        """
        return self.difference(other)

    def __xor__(self, other):
        """
        Symmetric difference.
        """
        return self.symmetric_difference(other)

    def __ior__(self, other):
        """
        In-place union.
        """
        for other_interval in other.intervals:
            for interval in self._generate_overlaps(other_interval):
                other_interval |= interval
                self.intervals.remove(interval)
            self.intervals.add(other_interval)
        self.consolidate_intervals()

        return self

    def __iand__(self, other):
        """
        In-place intersection.
        """
        new_intervals = []
        for other_interval in other.intervals:
            for interval in self._generate_overlaps(other_interval):
                new_intervals.append(other_interval & interval)
        self.intervals = SortedList(new_intervals, key=self._interval_sort_function)
        return self

    def __isub__(self, other):
        """
        In-place subtraction.
        """
        for other_interval in other.intervals:
            for interval in self._generate_overlaps(other_interval):
                self.intervals.update(interval - other_interval)
                self.intervals.remove(interval)
        return self

    def __ixor__(self, other):
        """
        In-place xor/symmetric difference.
        """
        new_intervals = ((self - other) | (other - self)).intervals
        self.intervals = SortedList(new_intervals, key=self._interval_sort_function)
        self.consolidate_intervals()
        return self

    def __contains__(self, element):
        """
        Check if self contain element.  Treat the element as a set of length
        one.  Perform a bisection to find the insertion point.  Check the
        interval to the left and right for membership.
        """
        idx = self.intervals.bisect_left(Interval(element, element))
        contains = False

        try:
            contains |= element in self.intervals[idx]
        except IndexError:
            pass

        try:
            contains |= element in self.intervals[idx - 1]
        except IndexError:
            pass

        return contains

    def __le__(self, other):
        """
        Check if self is a subset of other.  Self is a subset of other if the
        intersection of self and other is the same size as self.
        """
        return len(self) == len(self & other)

    def __lt__(self, other):
        """
        Check if self is a proper subset of other.  Self is a proper subset of
        other if it is a subset of other, and self is not equal to other.
        """
        return self <= other and self != other

    def __ge__(self, other):
        """
        Check if self is a superset of other.  Self is a superset of other if
        the intersection of self and other is the same size as self.
        """
        return len(other) == len(other & self)

    def __gt__(self, other):
        """
        Check if self is a proper superset of other.  Self is a proper superset
        of other if it is a superset of other, and self is not equal to other.

        """
        return self >= other and self != other

    def __len__(self):
        """
        Return number of elements in the set.
        """
        return sum(len(interval) for interval in self.intervals)

    def union(self, *others):
        """
        self | other_0 | other_1 | ...
        """
        copy = deepcopy(self)
        for other in others:
            copy |= other
        return copy

    def intersection(self, *others):
        """
        self & other_0 & other_1 & ...
        """
        copy = deepcopy(self)
        for other in others:
            copy &= other
        return copy

    def difference(self, *others):
        """
        self - other_0 - other_1 - ...
        """
        copy = deepcopy(self)
        for other in others:
            copy -= other
        return copy

    def symmetric_difference(self, other):
        """
        self ^ other
        """
        copy = deepcopy(self)
        copy ^= other
        return copy

    def issubset(self, other):
        """
        Method version of <= operator.
        """
        return self <= other

    def isdisjoint(self, other):
        """
        Return true if self has no common elements with other.
        """
        return len(self & other) == 0

    def issuperset(self, other):
        """
        Method version of >= operator.
        """
        return self >= other

    def copy(self):
        """
        Return a copy.
        """
        return deepcopy(self)

    def update(self, *others):
        """
        In-place union with multiple sets.
        """
        for other in others:
            self |= other

    def intersection_update(self, *others):
        """
        In-place intersection with multiple sets.
        """
        for other in others:
            self &= other

    def difference_update(self, *others):
        """
        In-place difference with multiple sets.
        """
        for other in others:
            self -= other

    def symmetric_difference_update(self, other):
        """
        In-place symmetric difference.
        """
        self ^= other

    def add(self, element):
        """
        Add a new integer to the set.
        """
        self |= IntegerSet((element, element))

    def remove(self, element):
        """
        Remove an integer from the set.  Raise KeyError if it isn't present.
        """
        if element not in self:
            raise KeyError
        self -= IntegerSet((element, element))

    def discard(self, element):
        """
        Remove specified element.
        """
        self -= IntegerSet((element, element))

    def pop(self):
        """
        Remove/return an arbitrary element.
        """
        if len(self) == 0:
            raise KeyError
        element = self.intervals[0].start
        self -= IntegerSet((element, element))
        return element

    def clear(self):
        """
        Remove all elements.
        """
        self.intervals.clear()

    @staticmethod
    def _interval_sort_function(interval):
        return IntervalSortAdapter(interval)

    def _generate_overlaps(self, interval_1):
        """
        Yield every interval of self that overlaps with other interval.  The
        implementation takes advantage of the fact that the intervals are sorted
        to stop iteration at the first self interval that does not overlap with
        other interval.
        """
        idx = self.intervals.bisect_left(interval_1)
        yield from chain(
            self._generate_greater(interval_1, idx),
            self._generate_lesser(interval_1, idx),
        )

    def _generate_greater(self, interval_1, idx=None):
        """
        Yield overlapping intervals greater than the supplied interval.  Stop
        iterating at the first non overlapping self interval.
        """
        idx = self.intervals.bisect_left(interval_1) if idx is None else idx
        overlaps = deque()
        while idx < len(self.intervals):
            interval_0 = self.intervals[idx]
            if interval_0.overlap(interval_1):
                overlaps.append(interval_0)
            else:
                break
            idx += 1
        yield from overlaps

    def _generate_lesser(self, interval_1, idx=None):
        """
        Yield overlapping intervals less than the supplied interval.  Stop
        iterating at the first non overlapping self interval.
        """
        idx = self.intervals.bisect_left(interval_1) if idx is None else idx
        overlaps = deque()
        while idx > 0:
            idx -= 1
            interval_0 = self.intervals[idx]
            if interval_0.overlap(interval_1):
                overlaps.append(interval_0)
            else:
                break
        yield from overlaps

    def consolidate_intervals(self):
        """
        Consolidate adjacent/overlapping intervals into one larger interval.

        Ex:
        >>> iset = IntegerSet((0, 10), (11, 20))
        >>> # iset.consolidate_intervals() called in the constructor
        >>> iset
        IntegerSet((0, 20))
        """
        new_intervals = []
        intervals = deque(self.intervals)

        while len(intervals) > 1:
            interval_0 = intervals.popleft()
            interval_1 = intervals.popleft()

            if interval_0.end + 1 in interval_1:
                interval = Interval(interval_0.start, interval_1.end)
                intervals.appendleft(interval)

            else:
                new_intervals.append(interval_0)
                intervals.appendleft(interval_1)

        new_intervals.extend(intervals)
        self.intervals = SortedList(new_intervals, key=self._interval_sort_function)
