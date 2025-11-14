from typing import TypeVar, Generic, Optional, List, Sequence
from .nodes import LinkedListNodes

T = TypeVar("T")

def bitonic_sort(items: Sequence[T]) -> List[T]:
    """
    Bitonic sort (O(n log^2 n)), suitable for parallel hardware or powers of two.

    Args:
        items (Sequence[T]): Sequence of comparable items. For optimal parallelization,
            length should be a power of two. Non-power-of-two lengths will still work,
            but performance characteristics may differ.

    Returns:
        List[T]: Sorted list of items.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If the sequence is empty.

    Notes:
        - Best for parallel architectures.
        - Time: O(n log^2 n).
        - Space: O(n).
        - Stable: No.

    Examples:
        >>> bitonic_sort([5, 1, 3, 2])
        [1, 2, 3, 5]

        >>> bitonic_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.

        >>> bitonic_sort([2, 2, 2, 2])
        [2, 2, 2, 2]
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")
    try:
        arr = list(items)
    except Exception as e:
        raise TypeError("Could not convert input to list.") from e

    def _bitonic_sort(arr: List[T], low: int, cnt: int, up: bool) -> None:
        if cnt > 1:
            k = cnt // 2
            _bitonic_sort(arr, low, k, True)
            _bitonic_sort(arr, low + k, k, False)
            _bitonic_merge(arr, low, cnt, up)

    def _bitonic_merge(arr: List[T], low: int, cnt: int, up: bool) -> None:
        if cnt > 1:
            k = cnt // 2
            for i in range(low, low + k):
                try:
                    comparison = arr[i] > arr[i + k]
                except Exception as e:
                    raise TypeError("Elements must be comparable.") from e
                if comparison == up:
                    arr[i], arr[i + k] = arr[i + k], arr[i]
            _bitonic_merge(arr, low, k, up)
            _bitonic_merge(arr, low + k, k, up)

    _bitonic_sort(arr, 0, len(arr), True)
    return arr

class SinglyLinkedList(Generic[T]):
    """
    Singly linked list.

    Args:
        items (Optional[List[T]]): Initial items.

    Attributes:
        head (Optional[LinkedListNodes.SinglyNode[T]]): Head node.

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

def bitonic_sort_singly(ll: SinglyLinkedList[T]) -> None:
    """
    Bitonic sort for singly linked list (O(n log^2 n), not stable, not in-place by node).

    Args:
        ll (SinglyLinkedList[T]): Linked list to sort (modified in-place).

    Returns:
        None

    Raises:
        TypeError: If elements are not comparable.
        ValueError: If the linked list is empty.

    Notes:
        - Not stable.
        - Not in-place (nodes not shuffled, values are).
        - Time: O(n log^2 n).
        - Space: O(n).

    Examples:
        >>> ll = SinglyLinkedList([5, 1, 3, 2])
        >>> bitonic_sort_singly(ll)
        >>> ll.to_list()
        [1, 2, 3, 5]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")

    def _bitonic_sort(arr, low, cnt, up):
        if cnt > 1:
            k = cnt // 2
            _bitonic_sort(arr, low, k, True)
            _bitonic_sort(arr, low + k, k, False)
            _bitonic_merge(arr, low, cnt, up)

    def _bitonic_merge(arr, low, cnt, up):
        if cnt > 1:
            k = cnt // 2
            for i in range(low, low + k):
                try:
                    comparison = arr[i] > arr[i + k]
                except Exception as e:
                    raise TypeError("Elements must be comparable.") from e
                if comparison == up:
                    arr[i], arr[i + k] = arr[i + k], arr[i]
            _bitonic_merge(arr, low, k, up)
            _bitonic_merge(arr, low + k, k, up)

    _bitonic_sort(arr, 0, len(arr), True)
    # write result back to linked list
    node = ll.head
    for value in arr:
        node.value = value
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

def bitonic_sort_doubly(ll: DoublyLinkedList[T]) -> None:
    """
    Bitonic sort for doubly linked list (O(n log^2 n), not stable, not in-place by node).

    Args:
        ll (DoublyLinkedList[T]): Doubly linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.
        ValueError: If the linked list is empty.

    Notes:
        - Not stable.
        - Not in-place by nodes.
        - Time: O(n log^2 n).
        - Space: O(n).

    Examples:
        >>> dl = DoublyLinkedList([5, 3, 1, 2])
        >>> bitonic_sort_doubly(dl)
        >>> dl.to_list()
        [1, 2, 3, 5]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")

    def _bitonic_sort(arr, low, cnt, up):
        if cnt > 1:
            k = cnt // 2
            _bitonic_sort(arr, low, k, True)
            _bitonic_sort(arr, low + k, k, False)
            _bitonic_merge(arr, low, cnt, up)

    def _bitonic_merge(arr, low, cnt, up):
        if cnt > 1:
            k = cnt // 2
            for i in range(low, low + k):
                try:
                    comparison = arr[i] > arr[i + k]
                except Exception as e:
                    raise TypeError("Elements must be comparable.") from e
                if comparison == up:
                    arr[i], arr[i + k] = arr[i + k], arr[i]
            _bitonic_merge(arr, low, k, up)
            _bitonic_merge(arr, low + k, k, up)

    _bitonic_sort(arr, 0, len(arr), True)
    # write back to linked list
    node = ll.head
    for value in arr:
        node.value = value
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

def bitonic_sort_circular(ll: CircularLinkedList[T]) -> None:
    """
    Bitonic sort for circular singly linked list (O(n log^2 n), not stable, not in-place by node).

    Args:
        ll (CircularLinkedList[T]): Circular linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.
        ValueError: If the linked list is empty.

    Notes:
        - Not stable.
        - Not in-place by nodes.
        - Time: O(n log^2 n).
        - Space: O(n).

    Examples:
        >>> cl = CircularLinkedList([4, 2, 1, 3])
        >>> bitonic_sort_circular(cl)
        >>> cl.to_list()
        [1, 2, 3, 4]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")

    def _bitonic_sort(arr, low, cnt, up):
        if cnt > 1:
            k = cnt // 2
            _bitonic_sort(arr, low, k, True)
            _bitonic_sort(arr, low + k, k, False)
            _bitonic_merge(arr, low, cnt, up)

    def _bitonic_merge(arr, low, cnt, up):
        if cnt > 1:
            k = cnt // 2
            for i in range(low, low + k):
                try:
                    comparison = arr[i] > arr[i + k]
                except Exception as e:
                    raise TypeError("Elements must be comparable.") from e
                if comparison == up:
                    arr[i], arr[i + k] = arr[i + k], arr[i]
            _bitonic_merge(arr, low, k, up)
            _bitonic_merge(arr, low + k, k, up)

    _bitonic_sort(arr, 0, len(arr), True)
    # write back to circular linked list
    node = ll.head
    for value in arr:
        node.value = value
        node = node.next
        if node == ll.head:
            break