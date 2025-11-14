from typing import TypeVar, Generic, Optional, List, Sequence
from .nodes import LinkedListNodes

T = TypeVar("T")

def insertion_sort(items: Sequence[T]) -> List[T]:
    """
    Insertion sort algorithm (stable, O(n^2)), returns a new sorted list.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list from the input sequence.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n^2) worst/average, best O(n) when nearly sorted.
        - Space: O(n).
        - Stable: Yes.

    Examples:
        >>> insertion_sort([2, 1, 3])
        [1, 2, 3]
        >>> insertion_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> insertion_sort(['c', 'a', 'b'])
        ['a', 'b', 'c']
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")

    arr = list(items)
    try:
        _ = arr[0] > arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0:
            try:
                if arr[j] > key:
                    arr[j + 1] = arr[j]
                    j -= 1
                else:
                    break
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        arr[j + 1] = key
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

def insertion_sort_singly(ll: SinglyLinkedList[T]) -> None:
    """
    Insertion sort (stable, O(n^2)), sorts singly linked list in place.

    Args:
        ll (SinglyLinkedList[T]): Linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n^2), best O(n) when nearly sorted.
        - Space: O(1).
        - Stable: Yes.

    Examples:
        >>> ll = SinglyLinkedList([2, 1, 3])
        >>> insertion_sort_singly(ll)
        >>> ll.to_list()
        [1, 2, 3]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] > arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0:
            try:
                if arr[j] > key:
                    arr[j + 1] = arr[j]
                    j -= 1
                else:
                    break
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        arr[j + 1] = key
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

def insertion_sort_doubly(ll: DoublyLinkedList[T]) -> None:
    """
    Insertion sort (stable, O(n^2)), sorts doubly linked list in place.

    Args:
        ll (DoublyLinkedList[T]): Linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n^2), best O(n) when nearly sorted.
        - Space: O(1).
        - Stable: Yes.

    Examples:
        >>> dl = DoublyLinkedList([2, 1, 3])
        >>> insertion_sort_doubly(dl)
        >>> dl.to_list()
        [1, 2, 3]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] > arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0:
            try:
                if arr[j] > key:
                    arr[j + 1] = arr[j]
                    j -= 1
                else:
                    break
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        arr[j + 1] = key
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

def insertion_sort_circular(ll: CircularLinkedList[T]) -> None:
    """
    Insertion sort (stable, O(n^2)), sorts circular linked list in place.

    Args:
        ll (CircularLinkedList[T]): List to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n^2), best O(n) when nearly sorted.
        - Space: O(1).
        - Stable: Yes.

    Examples:
        >>> cl = CircularLinkedList([2, 1, 3])
        >>> insertion_sort_circular(cl)
        >>> cl.to_list()
        [1, 2, 3]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] > arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0:
            try:
                if arr[j] > key:
                    arr[j + 1] = arr[j]
                    j -= 1
                else:
                    break
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        arr[j + 1] = key
    node = ll.head
    for value in arr:
        node.value = value
        node = node.next
        if node == ll.head:
            break