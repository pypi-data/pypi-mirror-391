from typing import TypeVar, Generic, Optional, List, Sequence
from .nodes import LinkedListNodes

T = TypeVar("T")

def pancake_sort(items: Sequence[T]) -> List[T]:
    """
    Pancake sort (O(n^2)), sorts by repeatedly flipping largest unsorted element to the front.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n^2)
        - Space: O(n)
        - Stable: Yes.

    Examples:
        >>> pancake_sort([3, 6, 1, 8, 4])
        [1, 3, 4, 6, 8]
        >>> pancake_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> pancake_sort(['c', 'a', 'b'])
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

    for curr_size in range(n, 1, -1):
        try:
            mi = max(range(curr_size), key=lambda x: arr[x])
        except Exception as e:
            raise TypeError("Elements must be comparable for sorting.") from e
        if mi != curr_size - 1:
            arr[:mi + 1] = reversed(arr[:mi + 1])
            arr[:curr_size] = reversed(arr[:curr_size])
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

def pancake_sort_singly(ll: SinglyLinkedList[T]) -> None:
    """
    Pancake sort (O(n^2)), sorts singly linked list in place (values only) using flips.

    Args:
        ll (SinglyLinkedList[T]): Linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements are not comparable.
        ValueError: If empty.

    Notes:
        - Time: O(n^2).
        - Space: O(1).
        - Stable: Yes.

    Examples:
        >>> ll = SinglyLinkedList([3, 6, 1, 8, 4])
        >>> pancake_sort_singly(ll)
        >>> ll.to_list()
        [1, 3, 4, 6, 8]
    """
    arr = ll.to_list()
    n = len(arr)
    if n == 0:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] > arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    for curr_size in range(n, 1, -1):
        try:
            mi = max(range(curr_size), key=lambda x: arr[x])
        except Exception as e:
            raise TypeError("Elements must be comparable for sorting.") from e
        if mi != curr_size - 1:
            arr[:mi + 1] = reversed(arr[:mi + 1])
            arr[:curr_size] = reversed(arr[:curr_size])
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

def pancake_sort_doubly(ll: DoublyLinkedList[T]) -> None:
    """
    Pancake sort (O(n^2)), sorts doubly linked list in place (values only).

    Args:
        ll (DoublyLinkedList[T]): Linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements are not comparable.
        ValueError: If empty.

    Notes:
        - Time: O(n^2).
        - Space: O(1).
        - Stable: Yes.

    Examples:
        >>> dl = DoublyLinkedList([3, 6, 1, 8, 4])
        >>> pancake_sort_doubly(dl)
        >>> dl.to_list()
        [1, 3, 4, 6, 8]
    """
    arr = ll.to_list()
    n = len(arr)
    if n == 0:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] > arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    for curr_size in range(n, 1, -1):
        try:
            mi = max(range(curr_size), key=lambda x: arr[x])
        except Exception as e:
            raise TypeError("Elements must be comparable for sorting.") from e
        if mi != curr_size - 1:
            arr[:mi + 1] = reversed(arr[:mi + 1])
            arr[:curr_size] = reversed(arr[:curr_size])
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

def pancake_sort_circular(ll: CircularLinkedList[T]) -> None:
    """
    Pancake sort (O(n^2)), sorts circular linked list in place (values only).

    Args:
        ll (CircularLinkedList[T]): List to sort.

    Returns:
        None

    Raises:
        TypeError: If elements are not comparable.
        ValueError: If empty.

    Notes:
        - Time: O(n^2).
        - Space: O(1).
        - Stable: Yes.

    Examples:
        >>> cl = CircularLinkedList([3, 6, 1, 8, 4])
        >>> pancake_sort_circular(cl)
        >>> cl.to_list()
        [1, 3, 4, 6, 8]
    """
    arr = ll.to_list()
    n = len(arr)
    if n == 0:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] > arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    for curr_size in range(n, 1, -1):
        try:
            mi = max(range(curr_size), key=lambda x: arr[x])
        except Exception as e:
            raise TypeError("Elements must be comparable for sorting.") from e
        if mi != curr_size - 1:
            arr[:mi + 1] = reversed(arr[:mi + 1])
            arr[:curr_size] = reversed(arr[:curr_size])
    node = ll.head
    for value in arr:
        node.value = value
        node = node.next
        if node == ll.head:
            break