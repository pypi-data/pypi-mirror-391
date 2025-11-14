from typing import TypeVar, Generic, Optional, List, Sequence
from .nodes import LinkedListNodes

T = TypeVar("T")

def timsort(items: Sequence[T]) -> List[T]:
    """
    TimSort (stable, O(n log n)), Python's built-in sorting algorithm.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n log n) worst.
        - Space: O(n).
        - Stable: Yes.
        - Used by Python's built-in sorted() and .sort().

    Examples:
        >>> timsort([3, 1, 2])
        [1, 2, 3]
        >>> timsort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> timsort(['c', 'a', 'b'])
        ['a', 'b', 'c']
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")
    try:
        return sorted(items)
    except Exception as e:
        raise TypeError("Elements must be comparable for sorting.") from e

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

def timsort_singly(ll: SinglyLinkedList[T]) -> None:
    """
    TimSort (stable, O(n log n)), sorts singly linked list in place using Python sorted.

    Args:
        ll (SinglyLinkedList[T]): Linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n log n) worst.
        - Space: O(n).
        - Stable: Yes.
        - Used by Python's built-in sorted() and .sort().

    Examples:
        >>> ll = SinglyLinkedList([3, 1, 2])
        >>> timsort_singly(ll)
        >>> ll.to_list()
        [1, 2, 3]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    try:
        arr = sorted(arr)
    except Exception as e:
        raise TypeError("Elements must be comparable for sorting.") from e
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

def timsort_doubly(ll: DoublyLinkedList[T]) -> None:
    """
    TimSort (stable, O(n log n)), sorts doubly linked list in place.

    Args:
        ll (DoublyLinkedList[T]): Doubly linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n log n) worst.
        - Space: O(n).
        - Stable: Yes.

    Examples:
        >>> dl = DoublyLinkedList([3, 1, 2])
        >>> timsort_doubly(dl)
        >>> dl.to_list()
        [1, 2, 3]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    try:
        arr = sorted(arr)
    except Exception as e:
        raise TypeError("Elements must be comparable for sorting.") from e
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

def timsort_circular(ll: CircularLinkedList[T]) -> None:
    """
    TimSort (stable, O(n log n)), sorts circular linked list in place.

    Args:
        ll (CircularLinkedList[T]): Circular linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n log n) worst.
        - Space: O(n).
        - Stable: Yes.

    Examples:
        >>> cl = CircularLinkedList([3, 1, 2])
        >>> timsort_circular(cl)
        >>> cl.to_list()
        [1, 2, 3]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    try:
        arr = sorted(arr)
    except Exception as e:
        raise TypeError("Elements must be comparable for sorting.") from e
    node = ll.head
    for value in arr:
        node.value = value
        node = node.next
        if node == ll.head:
            break