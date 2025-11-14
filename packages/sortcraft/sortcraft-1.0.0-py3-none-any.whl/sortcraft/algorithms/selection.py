from typing import TypeVar, Generic, Optional, List, Sequence
from .nodes import LinkedListNodes

T = TypeVar("T")

def selection_sort(items: Sequence[T]) -> List[T]:
    """
    Selection sort algorithm (unstable, O(n^2)), returns a new sorted list.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list from the input sequence.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n^2) worst/average.
        - Space: O(n).
        - Stable: No.

    Examples:
        >>> selection_sort([2, 1, 3])
        [1, 2, 3]
        >>> selection_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> selection_sort(['c', 'a', 'b'])
        ['a', 'b', 'c']
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")

    arr = list(items)
    n = len(arr)
    try:
        _ = arr[0] < arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    for i in range(n):
        idx_min = i
        for j in range(i + 1, n):
            try:
                if arr[j] < arr[idx_min]:
                    idx_min = j
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        arr[i], arr[idx_min] = arr[idx_min], arr[i]
    return arr

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

def selection_sort_singly(ll: SinglyLinkedList[T]) -> None:
    """
    Selection sort (unstable, O(n^2)), sorts singly linked list in-place (values only).

    Args:
        ll (SinglyLinkedList[T]): Linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n^2).
        - Space: O(1).
        - Stable: No.

    Examples:
        >>> ll = SinglyLinkedList([2, 1, 3])
        >>> selection_sort_singly(ll)
        >>> ll.to_list()
        [1, 2, 3]
    """
    arr = ll.to_list()
    n = len(arr)
    if n == 0:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] < arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    for i in range(n):
        idx_min = i
        for j in range(i + 1, n):
            try:
                if arr[j] < arr[idx_min]:
                    idx_min = j
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        arr[i], arr[idx_min] = arr[idx_min], arr[i]
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

def selection_sort_doubly(ll: DoublyLinkedList[T]) -> None:
    """
    Selection sort (unstable, O(n^2)), sorts doubly linked list in-place (values only).

    Args:
        ll (DoublyLinkedList[T]): Linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n^2).
        - Space: O(1).
        - Stable: No.

    Examples:
        >>> dl = DoublyLinkedList([2, 1, 3])
        >>> selection_sort_doubly(dl)
        >>> dl.to_list()
        [1, 2, 3]
    """
    arr = ll.to_list()
    n = len(arr)
    if n == 0:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] < arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    for i in range(n):
        idx_min = i
        for j in range(i + 1, n):
            try:
                if arr[j] < arr[idx_min]:
                    idx_min = j
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        arr[i], arr[idx_min] = arr[idx_min], arr[i]
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

def selection_sort_circular(ll: CircularLinkedList[T]) -> None:
    """
    Selection sort (unstable, O(n^2)), sorts circular linked list in-place (values only).

    Args:
        ll (CircularLinkedList[T]): Circular linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n^2).
        - Space: O(1).
        - Stable: No.

    Examples:
        >>> cl = CircularLinkedList([2, 1, 3])
        >>> selection_sort_circular(cl)
        >>> cl.to_list()
        [1, 2, 3]
    """
    arr = ll.to_list()
    n = len(arr)
    if n == 0:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] < arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    for i in range(n):
        idx_min = i
        for j in range(i + 1, n):
            try:
                if arr[j] < arr[idx_min]:
                    idx_min = j
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        arr[i], arr[idx_min] = arr[idx_min], arr[i]
    node = ll.head
    for value in arr:
        node.value = value
        node = node.next
        if node == ll.head:
            break