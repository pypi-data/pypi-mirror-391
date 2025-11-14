from __future__ import annotations
from typing import TypeVar, Generic, Optional, List, Protocol, Sequence
from .nodes import LinkedListNodes

class SupportsLT(Protocol):
    def __lt__(self, other: "SupportsLT", /) -> bool: ...

T = TypeVar("T", bound=SupportsLT)

def merge_sort(items: Sequence[T]) -> List[T]:
    """
    Stable, O(n log n) merge sort that returns a new sorted list.

    Args:
        items (Sequence[T]): A finite sequence of comparable items.

    Returns:
        List[T]: A new list containing the items in non-decreasing order.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If items is empty.

    Notes:
        - Time: O(n log n) average/worst.
        - Space: O(n) auxiliary.
        - Stable: Yes.

    Examples:
        >>> merge_sort([3, 1, 2])
        [1, 2, 3]
        >>> merge_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> merge_sort(['z', 'a', 'x'])
        ['a', 'x', 'z']
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")
    try:
        _ = items[0] < items[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    n = len(items)
    if n <= 1:
        return list(items)
    mid = n // 2
    left = merge_sort(items[:mid])
    right = merge_sort(items[mid:])
    return _merge(left, right)

def _merge(a: List[T], b: List[T]) -> List[T]:
    i = j = 0
    out: List[T] = []
    while i < len(a) and j < len(b):
        try:
            if b[j] < a[i]:  # maintain stability
                out.append(b[j]); j += 1
            else:
                out.append(a[i]); i += 1
        except Exception as e:
            raise TypeError("Elements must be comparable for sorting.") from e
    if i < len(a): out.extend(a[i:])
    if j < len(b): out.extend(b[j:])
    return out

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

def merge_sort_singly(ll: SinglyLinkedList[T]) -> None:
    """
    Stable, O(n log n) merge sort for singly linked list. Modifies values in place.

    Args:
        ll (SinglyLinkedList[T]): Linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n log n).
        - Space: O(n).
        - Stable: Yes.

    Examples:
        >>> ll = SinglyLinkedList([3, 1, 2])
        >>> merge_sort_singly(ll)
        >>> ll.to_list()
        [1, 2, 3]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] < arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    def _merge(a: List[T], b: List[T]) -> List[T]:
        i = j = 0
        result = []
        while i < len(a) and j < len(b):
            try:
                if b[j] < a[i]:
                    result.append(b[j])
                    j += 1
                else:
                    result.append(a[i])
                    i += 1
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        if i < len(a):
            result.extend(a[i:])
        if j < len(b):
            result.extend(b[j:])
        return result

    def _merge_sort(items: List[T]) -> List[T]:
        n = len(items)
        if n <= 1:
            return items
        mid = n // 2
        left = _merge_sort(items[:mid])
        right = _merge_sort(items[mid:])
        return _merge(left, right)
    sorted_arr = _merge_sort(arr)
    node = ll.head
    for value in sorted_arr:
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

def merge_sort_doubly(ll: DoublyLinkedList[T]) -> None:
    """
    Stable, O(n log n) merge sort for doubly linked list, modifies values inplace.

    Args:
        ll (DoublyLinkedList[T]): Doubly linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n log n).
        - Space: O(n).
        - Stable: Yes.

    Examples:
        >>> dl = DoublyLinkedList([3, 1, 2])
        >>> merge_sort_doubly(dl)
        >>> dl.to_list()
        [1, 2, 3]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] < arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    def _merge(a: List[T], b: List[T]) -> List[T]:
        i = j = 0
        result = []
        while i < len(a) and j < len(b):
            try:
                if b[j] < a[i]:
                    result.append(b[j])
                    j += 1
                else:
                    result.append(a[i])
                    i += 1
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        if i < len(a):
            result.extend(a[i:])
        if j < len(b):
            result.extend(b[j:])
        return result

    def _merge_sort(items: List[T]) -> List[T]:
        n = len(items)
        if n <= 1:
            return items
        mid = n // 2
        left = _merge_sort(items[:mid])
        right = _merge_sort(items[mid:])
        return _merge(left, right)
    sorted_arr = _merge_sort(arr)
    node = ll.head
    for value in sorted_arr:
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

def merge_sort_circular(ll: CircularLinkedList[T]) -> None:
    """
    Stable, O(n log n) merge sort for circular linked list, modifies values inplace.

    Args:
        ll (CircularLinkedList[T]): Circular linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n log n).
        - Space: O(n).
        - Stable: Yes.

    Examples:
        >>> cl = CircularLinkedList([3, 1, 2])
        >>> merge_sort_circular(cl)
        >>> cl.to_list()
        [1, 2, 3]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] < arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    def _merge(a: List[T], b: List[T]) -> List[T]:
        i = j = 0
        result = []
        while i < len(a) and j < len(b):
            try:
                if b[j] < a[i]:
                    result.append(b[j])
                    j += 1
                else:
                    result.append(a[i])
                    i += 1
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        if i < len(a):
            result.extend(a[i:])
        if j < len(b):
            result.extend(b[j:])
        return result

    def _merge_sort(items: List[T]) -> List[T]:
        n = len(items)
        if n <= 1:
            return items
        mid = n // 2
        left = _merge_sort(items[:mid])
        right = _merge_sort(items[mid:])
        return _merge(left, right)
    sorted_arr = _merge_sort(arr)
    node = ll.head
    for value in sorted_arr:
        node.value = value
        node = node.next
        if node == ll.head:
            break