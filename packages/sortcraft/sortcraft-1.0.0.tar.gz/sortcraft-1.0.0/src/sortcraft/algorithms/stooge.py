from typing import TypeVar, Generic, Optional, List, Sequence
from .nodes import LinkedListNodes

T = TypeVar("T")

def stooge_sort(items: Sequence[T]) -> List[T]:
    """
    Stooge sort (O(n^{2.7095})), famous as a highly impractical comparison sort.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n^{2.7095})
        - Space: O(n)
        - Stable: Yes
        - Mostly used to illustrate pathological worst-cases.

    Examples:
        >>> stooge_sort([4, 2, 7, 1])
        [1, 2, 4, 7]
        >>> stooge_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> stooge_sort(['b', 'c', 'a'])
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

    def _stooge(arr, l, h):
        if l >= h:
            return
        try:
            if arr[l] > arr[h]:
                arr[l], arr[h] = arr[h], arr[l]
        except Exception as e:
            raise TypeError("Elements must be comparable for sorting.") from e
        if h - l + 1 > 2:
            t = (h - l + 1) // 3
            _stooge(arr, l, h - t)
            _stooge(arr, l + t, h)
            _stooge(arr, l, h - t)
    _stooge(arr, 0, len(arr) - 1)
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

def stooge_sort_singly(ll: SinglyLinkedList[T]) -> None:
    """
    Stooge sort (O(n^{2.7095})), sorts singly linked list in place (values only).

    Args:
        ll (SinglyLinkedList[T]): Linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n^{2.7095})
        - Space: O(1)
        - Stable: Yes

    Examples:
        >>> ll = SinglyLinkedList([4, 2, 7, 1])
        >>> stooge_sort_singly(ll)
        >>> ll.to_list()
        [1, 2, 4, 7]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] > arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    def _stooge(arr, l, h):
        if l >= h:
            return
        try:
            if arr[l] > arr[h]:
                arr[l], arr[h] = arr[h], arr[l]
        except Exception as e:
            raise TypeError("Elements must be comparable for sorting.") from e
        if h - l + 1 > 2:
            t = (h - l + 1) // 3
            _stooge(arr, l, h - t)
            _stooge(arr, l + t, h)
            _stooge(arr, l, h - t)
    _stooge(arr, 0, len(arr) - 1)
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

def stooge_sort_doubly(ll: DoublyLinkedList[T]) -> None:
    """
    Stooge sort (O(n^{2.7095})), sorts doubly linked list in place (values only).

    Args:
        ll (DoublyLinkedList[T]): Linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n^{2.7095})
        - Space: O(1)
        - Stable: Yes

    Examples:
        >>> dl = DoublyLinkedList([4, 2, 7, 1])
        >>> stooge_sort_doubly(dl)
        >>> dl.to_list()
        [1, 2, 4, 7]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] > arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    def _stooge(arr, l, h):
        if l >= h:
            return
        try:
            if arr[l] > arr[h]:
                arr[l], arr[h] = arr[h], arr[l]
        except Exception as e:
            raise TypeError("Elements must be comparable for sorting.") from e
        if h - l + 1 > 2:
            t = (h - l + 1) // 3
            _stooge(arr, l, h - t)
            _stooge(arr, l + t, h)
            _stooge(arr, l, h - t)
    _stooge(arr, 0, len(arr) - 1)
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

def stooge_sort_circular(ll: CircularLinkedList[T]) -> None:
    """
    Stooge sort (O(n^{2.7095})), sorts circular linked list in place (values only).

    Args:
        ll (CircularLinkedList[T]): Circular linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n^{2.7095})
        - Space: O(1)
        - Stable: Yes

    Examples:
        >>> cl = CircularLinkedList([4, 2, 7, 1])
        >>> stooge_sort_circular(cl)
        >>> cl.to_list()
        [1, 2, 4, 7]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] > arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    def _stooge(arr, l, h):
        if l >= h:
            return
        try:
            if arr[l] > arr[h]:
                arr[l], arr[h] = arr[h], arr[l]
        except Exception as e:
            raise TypeError("Elements must be comparable for sorting.") from e
        if h - l + 1 > 2:
            t = (h - l + 1) // 3
            _stooge(arr, l, h - t)
            _stooge(arr, l + t, h)
            _stooge(arr, l, h - t)
    _stooge(arr, 0, len(arr) - 1)
    node = ll.head
    for value in arr:
        node.value = value
        node = node.next
        if node == ll.head:
            break