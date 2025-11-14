from typing import Generic, Optional, List, TypeVar, Sequence
from .nodes import LinkedListNodes

T = TypeVar("T")

def pigeonhole_sort(items: Sequence[int]) -> List[int]:
    """
    Pigeonhole sort (O(n + k)), for finite-range integers.

    Args:
        items (Sequence[int]): Sequence of integers (ideally small/finite range).

    Returns:
        List[int]: Sorted list.

    Raises:
        TypeError: If items is not a sequence or elements are not integers.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n + k), where k is the range of values.
        - Space: O(n + k).
        - Stable: Yes.
        - Only works for integers with small/known range.

    Examples:
        >>> pigeonhole_sort([8, 3, 2, 7, 4, 6, 8])
        [2, 3, 4, 6, 7, 8, 8]
        >>> pigeonhole_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> pigeonhole_sort(['a', 2, 3])
        Traceback (most recent call last):
            ...
        TypeError: All elements must be integers.
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")
    for x in items:
        if not isinstance(x, int):
            raise TypeError("All elements must be integers.")

    mini, maxi = min(items), max(items)
    size = maxi - mini + 1
    holes = [0] * size
    for x in items:
        holes[x - mini] += 1
    out = []
    for i, count in enumerate(holes):
        out.extend([i + mini] * count)
    return out

class SinglyLinkedList(Generic[T]):
    """
    Singly linked list of integers.

    Args:
        items (Optional[List[int]]): Initial items.
    """
    def __init__(self, items: Optional[List[int]] = None):
        self.head: Optional[LinkedListNodes.SinglyNode[int]] = None
        if items:
            for item in reversed(items):
                node = LinkedListNodes.SinglyNode(item)
                node.next = self.head
                self.head = node

    def to_list(self) -> List[int]:
        result = []
        node = self.head
        while node:
            result.append(node.value)
            node = node.next
        return result

def pigeonhole_sort_singly(ll: SinglyLinkedList) -> None:
    """
    Pigeonhole sort (O(n + k)), sorts singly linked list of integers.

    Args:
        ll (SinglyLinkedList): Linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If not integer.
        ValueError: If input is empty.

    Notes:
        - Time: O(n + k), k is range.
        - Space: O(n + k).
        - Stable: Yes.

    Examples:
        >>> ll = SinglyLinkedList([8, 3, 2, 7, 4, 6, 8])
        >>> pigeonhole_sort_singly(ll)
        >>> ll.to_list()
        [2, 3, 4, 6, 7, 8, 8]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    for x in arr:
        if not isinstance(x, int):
            raise TypeError("All elements must be integers.")
    mini, maxi = min(arr), max(arr)
    size = maxi - mini + 1
    holes = [0] * size
    for x in arr:
        holes[x - mini] += 1
    out = []
    for i, count in enumerate(holes):
        out.extend([i + mini] * count)
    node = ll.head
    for value in out:
        node.value = value
        node = node.next

class DoublyLinkedList(Generic[T]):
    """
    Doubly linked list of integers.

    Args:
        items (Optional[List[int]]): Initial items.
    """
    def __init__(self, items: Optional[List[int]] = None):
        self.head: Optional[LinkedListNodes.DoublyNode[int]] = None
        self.tail: Optional[LinkedListNodes.DoublyNode[int]] = None
        if items:
            for item in items:
                node = LinkedListNodes.DoublyNode(item)
                if not self.head:
                    self.head = self.tail = node
                else:
                    self.tail.next = node
                    node.prev = self.tail
                    self.tail = node

    def to_list(self) -> List[int]:
        result = []
        node = self.head
        while node:
            result.append(node.value)
            node = node.next
        return result

def pigeonhole_sort_doubly(ll: DoublyLinkedList) -> None:
    """
    Pigeonhole sort (O(n + k)), sorts doubly linked list of integers.

    Args:
        ll (DoublyLinkedList): Doubly linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If not integer.
        ValueError: If empty.

    Notes:
        - Time: O(n + k), k is range.
        - Space: O(n + k).
        - Stable: Yes.

    Examples:
        >>> dl = DoublyLinkedList([8, 3, 2, 7, 4, 6, 8])
        >>> pigeonhole_sort_doubly(dl)
        >>> dl.to_list()
        [2, 3, 4, 6, 7, 8, 8]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    for x in arr:
        if not isinstance(x, int):
            raise TypeError("All elements must be integers.")
    mini, maxi = min(arr), max(arr)
    size = maxi - mini + 1
    holes = [0] * size
    for x in arr:
        holes[x - mini] += 1
    out = []
    for i, count in enumerate(holes):
        out.extend([i + mini] * count)
    node = ll.head
    for value in out:
        node.value = value
        node = node.next

class CircularLinkedList(Generic[T]):
    """
    Circular singly linked list of integers.

    Args:
        items (Optional[List[int]]): Initial items.
    """
    def __init__(self, items: Optional[List[int]] = None):
        self.head: Optional[LinkedListNodes.CircularNode[int]] = None
        if items:
            nodes = [LinkedListNodes.CircularNode(item) for item in items]
            n = len(nodes)
            if n > 0:
                for i in range(n):
                    nodes[i].next = nodes[(i + 1) % n]
                self.head = nodes[0]

    def to_list(self) -> List[int]:
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

def pigeonhole_sort_circular(ll: CircularLinkedList) -> None:
    """
    Pigeonhole sort (O(n + k)), sorts circular linked list of integers.

    Args:
        ll (CircularLinkedList): Circular linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If not integer.
        ValueError: If empty.

    Notes:
        - Time: O(n + k), k is range.
        - Space: O(n + k).
        - Stable: Yes.

    Examples:
        >>> cl = CircularLinkedList([8, 3, 2, 7, 4, 6, 8])
        >>> pigeonhole_sort_circular(cl)
        >>> cl.to_list()
        [2, 3, 4, 6, 7, 8, 8]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    for x in arr:
        if not isinstance(x, int):
            raise TypeError("All elements must be integers.")
    mini, maxi = min(arr), max(arr)
    size = maxi - mini + 1
    holes = [0] * size
    for x in arr:
        holes[x - mini] += 1
    out = []
    for i, count in enumerate(holes):
        out.extend([i + mini] * count)
    node = ll.head
    for value in out:
        node.value = value
        node = node.next
        if node == ll.head:
            break