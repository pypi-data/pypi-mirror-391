from typing import TypeVar, Generic, Optional, List, Sequence
from .nodes import LinkedListNodes

T = TypeVar("T")

def bubble_sort(items: Sequence[T]) -> List[T]:
    """
    Bubble sort algorithm (stable, O(n^2)), returns a new sorted list.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list from the input sequence.

    Raises:
        TypeError: If items is not a sequence or its elements are not comparable.
        ValueError: If the input sequence is empty.

    Notes:
        - Time: O(n^2) worst/average.
        - Space: O(n).
        - Stable: Yes.

    Examples:
        >>> bubble_sort([2, 1, 3])
        [1, 2, 3]
        >>> bubble_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> bubble_sort(["b", "a", "c"])
        ['a', 'b', 'c']
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")

    arr = list(items)
    n = len(arr)
    try:
        _ = arr[0] > arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    for i in range(n):
        for j in range(n - 1 - i):
            try:
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
    return arr

class SinglyLinkedList(Generic[T]):
    """
    Singly linked list.

    Args:
        items (Optional[List[T]]): Initial items (as Python list, optional).

    Attributes:
        head (Optional[LinkedListNodes.SinglyNode[T]]): Head node of the list.

    Examples:
        >>> ll = SinglyLinkedList([3, 2, 1])
        >>> ll.to_list()
        [3, 2, 1]
    """

    def __init__(self, items: Optional[List[T]] = None):
        self.head: Optional[LinkedListNodes.SinglyNode[T]] = None
        if items:
            for item in reversed(items):
                node = LinkedListNodes.SinglyNode(item)
                node.next = self.head
                self.head = node

    def to_list(self) -> List[T]:
        """
        Convert linked list to Python list.

        Returns:
            List[T]: List containing linked list elements (in order).
        """
        result = []
        node = self.head
        while node:
            result.append(node.value)
            node = node.next
        return result

def bubble_sort_singly(ll: SinglyLinkedList[T]) -> None:
    """
    Bubble sort for singly linked list (in-place, stable, O(n^2)).

    Args:
        ll (SinglyLinkedList[T]): Linked list to sort (modified in-place).

    Returns:
        None

    Raises:
        TypeError: If elements are not comparable.

    Notes:
        - Time: O(n^2) worst/average.
        - Space: O(1).
        - Stable: Yes.

    Examples:
        >>> ll = SinglyLinkedList([3, 2, 1])
        >>> bubble_sort_singly(ll)
        >>> ll.to_list()
        [1, 2, 3]
    """
    if not ll.head:
        return
    try:
        _ = ll.head.value > ll.head.value
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e
    changed = True
    while changed:
        changed = False
        node = ll.head
        while node and node.next:
            try:
                if node.value > node.next.value:
                    node.value, node.next.value = node.next.value, node.value
                    changed = True
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
            node = node.next

class DoublyLinkedList(Generic[T]):
    """
    Doubly linked list.

    Args:
        items (Optional[List[T]]): Initial items.

    Attributes:
        head (Optional[LinkedListNodes.DoublyNode[T]]): Head node.
        tail (Optional[LinkedListNodes.DoublyNode[T]]): Tail node.

    Examples:
        >>> dl = DoublyLinkedList([3, 1, 2])
        >>> dl.to_list()
        [3, 1, 2]
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
        """
        Convert linked list to Python list.

        Returns:
            List[T]: List with elements in order.
        """
        result = []
        node = self.head
        while node:
            result.append(node.value)
            node = node.next
        return result

def bubble_sort_doubly(ll: DoublyLinkedList[T]) -> None:
    """
    Bubble sort for doubly linked list (in-place, stable, O(n^2)).

    Args:
        ll (DoublyLinkedList[T]): Linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.

    Notes:
        - Time: O(n^2).
        - Space: O(1).
        - Stable: Yes.

    Examples:
        >>> dl = DoublyLinkedList([3, 2, 1])
        >>> bubble_sort_doubly(dl)
        >>> dl.to_list()
        [1, 2, 3]
    """
    if not ll.head:
        return
    try:
        _ = ll.head.value > ll.head.value
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e
    changed = True
    while changed:
        changed = False
        node = ll.head
        while node and node.next:
            try:
                if node.value > node.next.value:
                    node.value, node.next.value = node.next.value, node.value
                    changed = True
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
            node = node.next

class CircularLinkedList(Generic[T]):
    """
    Circular singly linked list.

    Args:
        items (Optional[List[T]]): Initial items.

    Attributes:
        head (Optional[LinkedListNodes.CircularNode[T]]): Head node.

    Examples:
        >>> cl = CircularLinkedList([2, 1, 3])
        >>> cl.to_list()
        [2, 1, 3]
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
        """
        Convert circular linked list to Python list.

        Returns:
            List[T]: List of elements in order starting at head.
        """
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

def bubble_sort_circular(ll: CircularLinkedList[T]) -> None:
    """
    Bubble sort for circular singly linked list (in-place, stable, O(n^2)).

    Args:
        ll (CircularLinkedList[T]): Circular linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.

    Notes:
        - Time: O(n^2).
        - Space: O(1).
        - Stable: Yes.

    Examples:
        >>> cl = CircularLinkedList([3, 2, 1])
        >>> bubble_sort_circular(cl)
        >>> cl.to_list()
        [1, 2, 3]
    """
    if not ll.head or ll.head.next == ll.head:
        return
    try:
        _ = ll.head.value > ll.head.value
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e
    changed = True
    while changed:
        changed = False
        node = ll.head
        start = ll.head
        while True:
            next_node = node.next
            if next_node == start:
                break
            try:
                if node.value > next_node.value:
                    node.value, next_node.value = next_node.value, node.value
                    changed = True
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
            node = next_node