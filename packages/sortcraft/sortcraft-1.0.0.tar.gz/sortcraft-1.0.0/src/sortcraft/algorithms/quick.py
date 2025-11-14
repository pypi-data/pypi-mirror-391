from __future__ import annotations
from typing import TypeVar, Generic, Optional, List, Sequence
from .nodes import LinkedListNodes

T = TypeVar("T")

def quick_sort(items: Sequence[T]) -> List[T]:
    """
    Quick sort (Lomuto partition), returns a new sorted list.

    Args:
        items (Sequence[T]): A finite sequence of comparable items.

    Returns:
        List[T]: A new list in non-decreasing order.

    Raises:
        TypeError: If items is not a sequence or its elements are not comparable.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n log n) average, O(n^2) worst (already-sorted + bad pivot).
        - Space: O(log n) average recursion depth.
        - Stable: No.

    Examples:
        >>> quick_sort([3, 2, 1])
        [1, 2, 3]
        >>> quick_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> quick_sort(['c', 'a', 'b'])
        ['a', 'b', 'c']
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")
    try:
        _ = items[0] <= items[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    arr = list(items)
    _qs(arr, 0, len(arr) - 1)
    return arr

def _qs(a: List[T], lo: int, hi: int) -> None:
    if lo >= hi:
        return
    p = _partition(a, lo, hi)
    _qs(a, lo, p - 1)
    _qs(a, p + 1, hi)

def _partition(a: List[T], lo: int, hi: int) -> int:
    pivot = a[hi]
    i = lo
    for j in range(lo, hi):
        try:
            if a[j] <= pivot:
                a[i], a[j] = a[j], a[i]
                i += 1
        except Exception as e:
            raise TypeError("Elements must be comparable for sorting.") from e
    a[i], a[hi] = a[hi], a[i]
    return i

class SinglyLinkedList(Generic[T]):
    """
    Singly linked list.

    Args:
        items (Optional[List[T]]): Initial items.
    """
    def __init__(self, items: Optional[List[T]] = None):
        self.head: Optional[LinkedListNodes.SinglyNode[T]] = None
        if items:
            for item in reversed(items):
                node = LinkedListNodes.SinglyNode(item)
                node.next = self.head
                self.head = node

    def to_list(self) -> List[T]:
        result = []
        node = self.head
        while node:
            result.append(node.value)
            node = node.next
        return result

def quick_sort_singly(ll: SinglyLinkedList[T]) -> None:
    """
    Quick sort (Lomuto partition, O(n log n) avg, O(n^2) worst) for singly linked list, sorts values.

    Args:
        ll (SinglyLinkedList[T]): Linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If not comparable.
        ValueError: If empty.

    Notes:
        - Time: O(n log n) average, O(n^2) worst.
        - Space: O(log n).
        - Stable: No.

    Examples:
        >>> ll = SinglyLinkedList([3, 2, 1])
        >>> quick_sort_singly(ll)
        >>> ll.to_list()
        [1, 2, 3]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] <= arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    def _qs(a: List[T], lo: int, hi: int) -> None:
        if lo >= hi:
            return
        p = _partition(a, lo, hi)
        _qs(a, lo, p - 1)
        _qs(a, p + 1, hi)

    def _partition(a: List[T], lo: int, hi: int) -> int:
        pivot = a[hi]
        i = lo
        for j in range(lo, hi):
            try:
                if a[j] <= pivot:
                    a[i], a[j] = a[j], a[i]
                    i += 1
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        a[i], a[hi] = a[hi], a[i]
        return i
    _qs(arr, 0, len(arr) - 1)
    node = ll.head
    for value in arr:
        node.value = value
        node = node.next

class DoublyLinkedList(Generic[T]):
    """
    Doubly linked list.

    Args:
        items (Optional[List[T]]): Initial items.
    """
    def __init__(self, items: Optional[List[T]] = None):
        self.head: Optional[LinkedListNodes.DoublyNode[T]] = None
        self.tail: Optional[LinkedListNodes.DoublyNode[T]] = None
        if items:
            for item in items:
                node = LinkedListNodes.DoublyNode(item)
                if not self.head:
                    self.head = self.tail = node
                else:
                    self.tail.next = node
                    node.prev = self.tail
                    self.tail = node

    def to_list(self) -> List[T]:
        result = []
        node = self.head
        while node:
            result.append(node.value)
            node = node.next
        return result

def quick_sort_doubly(ll: DoublyLinkedList[T]) -> None:
    """
    Quick sort (Lomuto, O(n log n) avg, O(n^2) worst) for doubly linked list, sorts values.

    Args:
        ll (DoublyLinkedList[T]): Linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If not comparable.
        ValueError: If empty.

    Notes:
        - Time: O(n log n) average, O(n^2) worst.
        - Space: O(log n).
        - Stable: No.

    Examples:
        >>> dl = DoublyLinkedList([3, 2, 1])
        >>> quick_sort_doubly(dl)
        >>> dl.to_list()
        [1, 2, 3]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] <= arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    def _qs(a: List[T], lo: int, hi: int) -> None:
        if lo >= hi:
            return
        p = _partition(a, lo, hi)
        _qs(a, lo, p - 1)
        _qs(a, p + 1, hi)

    def _partition(a: List[T], lo: int, hi: int) -> int:
        pivot = a[hi]
        i = lo
        for j in range(lo, hi):
            try:
                if a[j] <= pivot:
                    a[i], a[j] = a[j], a[i]
                    i += 1
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        a[i], a[hi] = a[hi], a[i]
        return i
    _qs(arr, 0, len(arr) - 1)
    node = ll.head
    for value in arr:
        node.value = value
        node = node.next

class CircularLinkedList(Generic[T]):
    """
    Circular singly linked list.

    Args:
        items (Optional[List[T]]): Initial items.
    """
    def __init__(self, items: Optional[List[T]] = None):
        self.head: Optional[LinkedListNodes.CircularNode[T]] = None
        if items:
            nodes = [LinkedListNodes.CircularNode(item) for item in items]
            n = len(nodes)
            if n > 0:
                for i in range(n):
                    nodes[i].next = nodes[(i + 1) % n]
                self.head = nodes[0]

    def to_list(self) -> List[T]:
        result = []
        node = self.head
        if not node:
            return result
        start = node
        while True:
            result.append(node.value)
            node = node.next
            if node == start:
                break
        return result

def quick_sort_circular(ll: CircularLinkedList[T]) -> None:
    """
    Quick sort (Lomuto, O(n log n) avg, O(n^2) worst) for circular linked list, sorts values.

    Args:
        ll (CircularLinkedList[T]): Circular linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If not comparable.
        ValueError: If empty.

    Notes:
        - Time: O(n log n) average, O(n^2) worst.
        - Space: O(log n).
        - Stable: No.

    Examples:
        >>> cl = CircularLinkedList([3, 2, 1])
        >>> quick_sort_circular(cl)
        >>> cl.to_list()
        [1, 2, 3]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] <= arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    def _qs(a: List[T], lo: int, hi: int) -> None:
        if lo >= hi:
            return
        p = _partition(a, lo, hi)
        _qs(a, lo, p - 1)
        _qs(a, p + 1, hi)

    def _partition(a: List[T], lo: int, hi: int) -> int:
        pivot = a[hi]
        i = lo
        for j in range(lo, hi):
            try:
                if a[j] <= pivot:
                    a[i], a[j] = a[j], a[i]
                    i += 1
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        a[i], a[hi] = a[hi], a[i]
        return i
    _qs(arr, 0, len(arr) - 1)
    node = ll.head
    for value in arr:
        node.value = value
        node = node.next
        if node == ll.head:
            break