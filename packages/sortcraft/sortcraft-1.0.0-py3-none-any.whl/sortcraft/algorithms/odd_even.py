from typing import TypeVar, Generic, Optional, List, Sequence
from .nodes import LinkedListNodes

T = TypeVar("T")

def odd_even_sort(items: Sequence[T]) -> List[T]:
    """
    Odd-Even sort (parity sort, O(n^2)), returns a new sorted list.

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
        >>> odd_even_sort([4, 3, 2, 1])
        [1, 2, 3, 4]
        >>> odd_even_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> odd_even_sort(['c', 'b', 'a'])
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

    sorted_ = False
    while not sorted_:
        sorted_ = True
        for i in range(1, n, 2):
            try:
                if arr[i - 1] > arr[i]:
                    arr[i - 1], arr[i] = arr[i], arr[i - 1]
                    sorted_ = False
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        for i in range(1, n - 1, 2):
            try:
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    sorted_ = False
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

def odd_even_sort_singly(ll: SinglyLinkedList[T]) -> None:
    """
    Odd-Even sort (stable, O(n^2)), sorts singly linked list in place by values.

    Args:
        ll (SinglyLinkedList[T]): Linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n^2).
        - Space: O(1).
        - Stable: Yes.

    Examples:
        >>> ll = SinglyLinkedList([4, 3, 2, 1])
        >>> odd_even_sort_singly(ll)
        >>> ll.to_list()
        [1, 2, 3, 4]
    """
    arr = ll.to_list()
    n = len(arr)
    if n == 0:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] > arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    sorted_ = False
    while not sorted_:
        sorted_ = True
        for i in range(1, n, 2):
            try:
                if arr[i - 1] > arr[i]:
                    arr[i - 1], arr[i] = arr[i], arr[i - 1]
                    sorted_ = False
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        for i in range(1, n - 1, 2):
            try:
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    sorted_ = False
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

def odd_even_sort_doubly(ll: DoublyLinkedList[T]) -> None:
    """
    Odd-Even sort (stable, O(n^2)), sorts doubly linked list in place by values.

    Args:
        ll (DoublyLinkedList[T]): Doubly linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n^2).
        - Space: O(1).
        - Stable: Yes.

    Examples:
        >>> dl = DoublyLinkedList([4, 3, 2, 1])
        >>> odd_even_sort_doubly(dl)
        >>> dl.to_list()
        [1, 2, 3, 4]
    """
    arr = ll.to_list()
    n = len(arr)
    if n == 0:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] > arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    sorted_ = False
    while not sorted_:
        sorted_ = True
        for i in range(1, n, 2):
            try:
                if arr[i - 1] > arr[i]:
                    arr[i - 1], arr[i] = arr[i], arr[i - 1]
                    sorted_ = False
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        for i in range(1, n - 1, 2):
            try:
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    sorted_ = False
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

def odd_even_sort_circular(ll: CircularLinkedList[T]) -> None:
    """
    Odd-Even sort (stable, O(n^2)), sorts circular linked list in place by values.

    Args:
        ll (CircularLinkedList[T]): Circular linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n^2).
        - Space: O(1).
        - Stable: Yes.

    Examples:
        >>> cl = CircularLinkedList([4, 3, 2, 1])
        >>> odd_even_sort_circular(cl)
        >>> cl.to_list()
        [1, 2, 3, 4]
    """
    arr = ll.to_list()
    n = len(arr)
    if n == 0:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] > arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    sorted_ = False
    while not sorted_:
        sorted_ = True
        for i in range(1, n, 2):
            try:
                if arr[i - 1] > arr[i]:
                    arr[i - 1], arr[i] = arr[i], arr[i - 1]
                    sorted_ = False
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        for i in range(1, n - 1, 2):
            try:
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    sorted_ = False
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
    node = ll.head
    for value in arr:
        node.value = value
        node = node.next
        if node == ll.head:
            break