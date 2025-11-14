from typing import TypeVar, Generic, Optional, List, Sequence
from .nodes import LinkedListNodes

T = TypeVar("T", bound=float)

def bucket_sort(items: Sequence[float], bucket_size: int = 5) -> List[float]:
    """
    Bucket sort for floats in [0, 1), returns a new sorted list.

    Args:
        items (Sequence[float]): Sequence of floats. Values must be in [0, 1).
        bucket_size (int, optional): Approximate bucket granularity (default=5).

    Returns:
        List[float]: Sorted list.

    Raises:
        TypeError: If items is not a sequence, or bucket_size is not an int.
        ValueError: If any element is not a float in [0, 1).
        ValueError: If bucket_size is not a positive integer.

    Notes:
        - Time: O(n + k) on uniform distributions.
        - Space: O(n + k).
        - Stable: Yes if underlying sort is stable.
        - Only suitable for floats in [0, 1).

    Examples:
        >>> bucket_sort([0.93, 0.14, 0.52, 0.4, 0.75])
        [0.14, 0.4, 0.52, 0.75, 0.93]
        >>> bucket_sort([])
        []
        >>> bucket_sort([0.7, 1.1])
        Traceback (most recent call last):
            ...
        ValueError: All elements must be floats in [0, 1).
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input items must be a sequence.")
    if not isinstance(bucket_size, int) or bucket_size < 1:
        raise ValueError("bucket_size must be a positive integer.")

    if not items:
        return []

    for x in items:
        if not isinstance(x, (float, int)):
            raise TypeError("All elements must be of float type.")
        if not (0 <= float(x) < 1):
            raise ValueError("All elements must be floats in [0, 1).")

    buckets = [[] for _ in range(bucket_size)]
    for x in items:
        idx = int(float(x) * bucket_size)
        buckets[min(idx, bucket_size - 1)].append(float(x))
    result = []
    for b in buckets:
        result.extend(sorted(b))
    return result

class SinglyLinkedList(Generic[T]):
    """
    Singly linked list.

    Args:
        items (Optional[List[T]]): Initial items.

    Attributes:
        head (Optional[LinkedListNodes.SinglyNode[T]]): Head node.

    Examples:
        >>> ll = SinglyLinkedList([0.2, 0.4, 0.1])
        >>> ll.to_list()
        [0.2, 0.4, 0.1]
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

def bucket_sort_singly(ll: SinglyLinkedList[T], bucket_size: int = 5) -> None:
    """
    Bucket sort for floats in [0, 1), modifies linked list in-place (values only).

    Args:
        ll (SinglyLinkedList[T]): Linked list of floats in [0, 1).
        bucket_size (int, optional): Number of buckets (default=5).

    Returns:
        None

    Raises:
        TypeError: If values are not float type or bucket_size not int.
        ValueError: If any value not in [0, 1) or if bucket_size not positive.

    Notes:
        - Time: O(n + k) on uniform distributions.
        - Space: O(n + k).
        - Stable: Yes if bucket sort uses stable sort.
        - Only valid for floats in [0, 1).

    Examples:
        >>> ll = SinglyLinkedList([0.93, 0.14, 0.52, 0.4, 0.75])
        >>> bucket_sort_singly(ll)
        >>> ll.to_list()
        [0.14, 0.4, 0.52, 0.75, 0.93]
    """
    arr = ll.to_list()
    if not isinstance(bucket_size, int) or bucket_size < 1:
        raise ValueError("bucket_size must be a positive integer.")
    if not arr:
        return
    for x in arr:
        if not isinstance(x, (float, int)):
            raise TypeError("All elements must be of float type.")
        if not (0 <= float(x) < 1):
            raise ValueError("All elements must be floats in [0, 1).")
    buckets = [[] for _ in range(bucket_size)]
    for x in arr:
        idx = int(float(x) * bucket_size)
        buckets[min(idx, bucket_size - 1)].append(float(x))
    result = []
    for b in buckets:
        result.extend(sorted(b))
    # Write back to linked list
    node = ll.head
    for value in result:
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

def bucket_sort_doubly(ll: DoublyLinkedList[T], bucket_size: int = 5) -> None:
    """
    Bucket sort for floats in [0, 1), modifies linked list in-place (values only).

    Args:
        ll (DoublyLinkedList[T]): Linked list of floats in [0, 1).
        bucket_size (int, optional): Number of buckets (default=5).

    Returns:
        None

    Raises:
        TypeError: If values not float/integer or bucket_size not int.
        ValueError: If not in [0, 1) or if bucket_size not positive.

    Notes:
        - Time: O(n + k) on uniform.
        - Space: O(n + k).
        - Stable: Yes if stable sort.
        - Only for floats in [0, 1).

    Examples:
        >>> dl = DoublyLinkedList([0.93, 0.14, 0.52, 0.4, 0.75])
        >>> bucket_sort_doubly(dl)
        >>> dl.to_list()
        [0.14, 0.4, 0.52, 0.75, 0.93]
    """
    arr = ll.to_list()
    if not isinstance(bucket_size, int) or bucket_size < 1:
        raise ValueError("bucket_size must be a positive integer.")
    if not arr:
        return
    for x in arr:
        if not isinstance(x, (float, int)):
            raise TypeError("All elements must be of float type.")
        if not (0 <= float(x) < 1):
            raise ValueError("All elements must be floats in [0, 1).")
    buckets = [[] for _ in range(bucket_size)]
    for x in arr:
        idx = int(float(x) * bucket_size)
        buckets[min(idx, bucket_size - 1)].append(float(x))
    result = []
    for b in buckets:
        result.extend(sorted(b))
    # Write back
    node = ll.head
    for value in result:
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

def bucket_sort_circular(ll: CircularLinkedList[T], bucket_size: int = 5) -> None:
    """
    Bucket sort for floats in [0, 1), modifies circular linked list in-place (values only).

    Args:
        ll (CircularLinkedList[T]): Circular linked list of floats in [0, 1).
        bucket_size (int, optional): Number of buckets (default=5).

    Returns:
        None

    Raises:
        TypeError: If values not float/integer or bucket_size not int.
        ValueError: If not in [0, 1) or if bucket_size not positive.

    Notes:
        - Time: O(n + k) on uniform.
        - Space: O(n + k).
        - Stable: Yes if stable sort.
        - Only for floats in [0, 1).

    Examples:
        >>> cl = CircularLinkedList([0.93, 0.14, 0.52, 0.4, 0.75])
        >>> bucket_sort_circular(cl)
        >>> cl.to_list()
        [0.14, 0.4, 0.52, 0.75, 0.93]
    """
    arr = ll.to_list()
    if not isinstance(bucket_size, int) or bucket_size < 1:
        raise ValueError("bucket_size must be a positive integer.")
    if not arr:
        return
    for x in arr:
        if not isinstance(x, (float, int)):
            raise TypeError("All elements must be of float type.")
        if not (0 <= float(x) < 1):
            raise ValueError("All elements must be floats in [0, 1).")
    buckets = [[] for _ in range(bucket_size)]
    for x in arr:
        idx = int(float(x) * bucket_size)
        buckets[min(idx, bucket_size - 1)].append(float(x))
    result = []
    for b in buckets:
        result.extend(sorted(b))
    # Write back to circular linked list
    node = ll.head
    for value in result:
        node.value = value
        node = node.next
        if node == ll.head:
            break