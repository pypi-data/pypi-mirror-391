from typing import TypeVar, Generic, Optional, List, Sequence
from .nodes import LinkedListNodes

T = TypeVar("T")

def gnome_sort(items: Sequence[T]) -> List[T]:
    """
    Gnome sort (stable, O(n^2)), returns a new sorted list.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n^2).
        - Space: O(n).
        - Stable: Yes.

    Examples:
        >>> gnome_sort([3, 2, 1])
        [1, 2, 3]
        >>> gnome_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> gnome_sort(['b', 'c', 'a'])
        ['a', 'b', 'c']
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")

    arr = list(items)
    try:
        _ = arr[0] <= arr[0]  # Check if comparable
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    i = 0
    while i < len(arr):
        try:
            if i == 0 or arr[i - 1] <= arr[i]:
                i += 1
            else:
                arr[i], arr[i - 1] = arr[i - 1], arr[i]
                i -= 1
        except Exception as e:
            raise TypeError("Elements must be comparable for sorting.") from e
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

def gnome_sort_singly(ll: SinglyLinkedList[T]) -> None:
    """
    Gnome sort (stable, O(n^2)), sorts singly linked list in place (values only).

    Args:
        ll (SinglyLinkedList[T]): Linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements are not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n^2).
        - Space: O(1).
        - Stable: Yes.

    Examples:
        >>> ll = SinglyLinkedList([3, 2, 1])
        >>> gnome_sort_singly(ll)
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
    i = 0
    while i < len(arr):
        try:
            if i == 0 or arr[i - 1] <= arr[i]:
                i += 1
            else:
                arr[i], arr[i - 1] = arr[i - 1], arr[i]
                i -= 1
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

def gnome_sort_doubly(ll: DoublyLinkedList[T]) -> None:
    """
    Gnome sort (stable, O(n^2)), sorts doubly linked list in place (values only).

    Args:
        ll (DoublyLinkedList[T]): Linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements are not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n^2).
        - Space: O(1).
        - Stable: Yes.

    Examples:
        >>> dl = DoublyLinkedList([9, 2, 5, 1])
        >>> gnome_sort_doubly(dl)
        >>> dl.to_list()
        [1, 2, 5, 9]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] <= arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e
    i = 0
    while i < len(arr):
        try:
            if i == 0 or arr[i - 1] <= arr[i]:
                i += 1
            else:
                arr[i], arr[i - 1] = arr[i - 1], arr[i]
                i -= 1
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

def gnome_sort_circular(ll: CircularLinkedList[T]) -> None:
    """
    Gnome sort (stable, O(n^2)), sorts circular linked list in place (values only).

    Args:
        ll (CircularLinkedList[T]): List to sort.

    Returns:
        None

    Raises:
        TypeError: If elements are not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n^2).
        - Space: O(1).
        - Stable: Yes.

    Examples:
        >>> cl = CircularLinkedList([2, 1, 3])
        >>> gnome_sort_circular(cl)
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
    i = 0
    while i < len(arr):
        try:
            if i == 0 or arr[i - 1] <= arr[i]:
                i += 1
            else:
                arr[i], arr[i - 1] = arr[i - 1], arr[i]
                i -= 1
        except Exception as e:
            raise TypeError("Elements must be comparable for sorting.") from e
    node = ll.head
    for value in arr:
        node.value = value
        node = node.next
        if node == ll.head:
            break