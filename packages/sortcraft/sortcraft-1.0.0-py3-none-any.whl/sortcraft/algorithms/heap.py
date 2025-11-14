from typing import TypeVar, Generic, Optional, List, Sequence
from .nodes import LinkedListNodes

T = TypeVar("T")

def heap_sort(items: Sequence[T]) -> List[T]:
    """
    Heap sort (unstable, O(n log n)), returns a new sorted list.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list from the input sequence.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n log n) worst/average.
        - Space: O(n).
        - Stable: No.

    Examples:
        >>> heap_sort([2, 1, 3])
        [1, 2, 3]
        >>> heap_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> heap_sort(['c', 'b', 'a'])
        ['a', 'b', 'c']
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")

    arr = list(items)
    try:
        _ = arr[0] < arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    _heapify(arr)
    end = len(arr) - 1
    while end > 0:
        arr[end], arr[0] = arr[0], arr[end]
        end -= 1
        _sift_down(arr, 0, end)
    return arr

def _heapify(arr: List[T]) -> None:
    n = len(arr)
    for i in reversed(range(n // 2)):
        _sift_down(arr, i, n - 1)

def _sift_down(arr: List[T], start: int, end: int) -> None:
    root = start
    while True:
        child = 2 * root + 1
        if child > end:
            break
        swap = root
        try:
            if arr[swap] < arr[child]:
                swap = child
            if child + 1 <= end and arr[swap] < arr[child + 1]:
                swap = child + 1
        except Exception as e:
            raise TypeError("Elements must be comparable for sorting.") from e
        if swap == root:
            return
        arr[root], arr[swap] = arr[swap], arr[root]
        root = swap

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

def heap_sort_singly(ll: SinglyLinkedList[T]) -> None:
    """
    Heap sort (unstable, O(n log n)), sorts singly linked list in place (values only).

    Args:
        ll (SinglyLinkedList[T]): Linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements are not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n log n) worst/average.
        - Space: O(n).
        - Stable: No.

    Examples:
        >>> ll = SinglyLinkedList([2, 1, 3])
        >>> heap_sort_singly(ll)
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
    _heapify(arr)
    end = len(arr) - 1
    while end > 0:
        arr[end], arr[0] = arr[0], arr[end]
        end -= 1
        _sift_down(arr, 0, end)
    node = ll.head
    for value in arr:
        node.value = value
        node = node.next

def _heapify(arr: List[T]) -> None:
    n = len(arr)
    for i in reversed(range(n // 2)):
        _sift_down(arr, i, n - 1)

def _sift_down(arr: List[T], start: int, end: int) -> None:
    root = start
    while True:
        child = 2 * root + 1
        if child > end:
            break
        swap = root
        try:
            if arr[swap] < arr[child]:
                swap = child
            if child + 1 <= end and arr[swap] < arr[child + 1]:
                swap = child + 1
        except Exception as e:
            raise TypeError("Elements must be comparable for sorting.") from e
        if swap == root:
            return
        arr[root], arr[swap] = arr[swap], arr[root]
        root = swap

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

def heap_sort_doubly(ll: DoublyLinkedList[T]) -> None:
    """
    Heap sort (unstable, O(n log n)), sorts doubly linked list in place (values only).

    Args:
        ll (DoublyLinkedList[T]): Doubly linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements are not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n log n) worst/average.
        - Space: O(n).
        - Stable: No.

    Examples:
        >>> dl = DoublyLinkedList([2, 1, 3])
        >>> heap_sort_doubly(dl)
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
    _heapify(arr)
    end = len(arr) - 1
    while end > 0:
        arr[end], arr[0] = arr[0], arr[end]
        end -= 1
        _sift_down(arr, 0, end)
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

def heap_sort_circular(ll: CircularLinkedList[T]) -> None:
    """
    Heap sort (unstable, O(n log n)), sorts circular linked list in place (values only).

    Args:
        ll (CircularLinkedList[T]): Circular linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements are not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n log n) worst/average.
        - Space: O(n).
        - Stable: No.

    Examples:
        >>> cl = CircularLinkedList([2, 1, 3])
        >>> heap_sort_circular(cl)
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
    _heapify(arr)
    end = len(arr) - 1
    while end > 0:
        arr[end], arr[0] = arr[0], arr[end]
        end -= 1
        _sift_down(arr, 0, end)
    node = ll.head
    for value in arr:
        node.value = value
        node = node.next
        if node == ll.head:
            break