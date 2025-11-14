from typing import TypeVar, Generic, Optional, List, Sequence
from .nodes import LinkedListNodes

T = TypeVar("T")

def counting_sort(items: Sequence[int]) -> List[int]:
    """
    Counting sort for integers (stable, O(n + k)), returns a new sorted list.

    Args:
        items (Sequence[int]): Sequence of non-negative integers.

    Returns:
        List[int]: Sorted list.

    Raises:
        TypeError: If items is not a sequence.
        ValueError: If elements are not non-negative integers.
        ValueError: If items is empty.

    Notes:
        - Time: O(n + k), where k is range of input.
        - Space: O(n + k).
        - Stable: Yes.
        - Only works for integers >= 0.

    Examples:
        >>> counting_sort([2, 5, 3, 0, 2, 3, 0, 3])
        [0, 0, 2, 2, 3, 3, 3, 5]
        >>> counting_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> counting_sort([2, -1, 3])
        Traceback (most recent call last):
            ...
        ValueError: All elements must be non-negative integers.
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")
    for num in items:
        if not isinstance(num, int) or num < 0:
            raise ValueError("All elements must be non-negative integers.")

    max_val = max(items)
    counts = [0] * (max_val + 1)
    for num in items:
        counts[num] += 1
    out = []
    for num, count in enumerate(counts):
        out.extend([num] * count)
    return out

class SinglyLinkedList(Generic[T]):
    """
    Singly linked list for non-negative integers.

    Args:
        items (Optional[List[int]]): Initial items (must be non-negative ints).
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

def counting_sort_singly(ll: SinglyLinkedList) -> None:
    """
    Counting sort for singly linked list of non-negative integers (stable, O(n + k)).

    Args:
        ll (SinglyLinkedList): Linked list to sort (modifies in-place).

    Returns:
        None

    Raises:
        TypeError: If values not int.
        ValueError: If empty or negative values.

    Notes:
        - Time: O(n + k), k = range of input.
        - Space: O(n + k).
        - Stable: Yes.
        - Only for integers >= 0.

    Examples:
        >>> ll = SinglyLinkedList([2, 5, 3, 0, 2, 3, 0, 3])
        >>> counting_sort_singly(ll)
        >>> ll.to_list()
        [0, 0, 2, 2, 3, 3, 3, 5]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Linked list must not be empty.")
    for num in arr:
        if not isinstance(num, int) or num < 0:
            raise ValueError("All elements must be non-negative integers.")
    max_val = max(arr)
    counts = [0] * (max_val + 1)
    for num in arr:
        counts[num] += 1
    out = []
    for num, count in enumerate(counts):
        out.extend([num] * count)
    node = ll.head
    for value in out:
        node.value = value
        node = node.next

class DoublyLinkedList(Generic[T]):
    """
    Doubly linked list for non-negative integers.

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

def counting_sort_doubly(ll: DoublyLinkedList) -> None:
    """
    Counting sort for doubly linked list of non-negative integers (stable, O(n + k)).

    Args:
        ll (DoublyLinkedList): List to sort (modifies in-place).

    Returns:
        None

    Raises:
        TypeError: If values not int.
        ValueError: If empty or negative values.

    Notes:
        - Time: O(n + k), k = range of input.
        - Space: O(n + k).
        - Stable: Yes.

    Examples:
        >>> dl = DoublyLinkedList([2, 5, 3, 0, 2, 3, 0, 3])
        >>> counting_sort_doubly(dl)
        >>> dl.to_list()
        [0, 0, 2, 2, 3, 3, 3, 5]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Linked list must not be empty.")
    for num in arr:
        if not isinstance(num, int) or num < 0:
            raise ValueError("All elements must be non-negative integers.")
    max_val = max(arr)
    counts = [0] * (max_val + 1)
    for num in arr:
        counts[num] += 1
    out = []
    for num, count in enumerate(counts):
        out.extend([num] * count)
    node = ll.head
    for value in out:
        node.value = value
        node = node.next

class CircularLinkedList(Generic[T]):
    """
    Circular singly linked list for non-negative integers.

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

def counting_sort_circular(ll: CircularLinkedList) -> None:
    """
    Counting sort for circular linked list of non-negative integers (stable, O(n + k)).

    Args:
        ll (CircularLinkedList): List to sort (modifies in-place).

    Returns:
        None

    Raises:
        TypeError: If values not int.
        ValueError: If empty or negative.

    Notes:
        - Time: O(n + k).
        - Space: O(n + k).
        - Stable: Yes.

    Examples:
        >>> cl = CircularLinkedList([2, 5, 3, 0, 2, 3, 0, 3])
        >>> counting_sort_circular(cl)
        >>> cl.to_list()
        [0, 0, 2, 2, 3, 3, 3, 5]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Linked list must not be empty.")
    for num in arr:
        if not isinstance(num, int) or num < 0:
            raise ValueError("All elements must be non-negative integers.")
    max_val = max(arr)
    counts = [0] * (max_val + 1)
    for num in arr:
        counts[num] += 1
    out = []
    for num, count in enumerate(counts):
        out.extend([num] * count)
    node = ll.head
    for value in out:
        node.value = value
        node = node.next
        if node == ll.head:
            break