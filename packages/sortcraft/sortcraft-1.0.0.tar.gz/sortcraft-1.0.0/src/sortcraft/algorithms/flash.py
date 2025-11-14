from typing import Generic, Optional, List, TypeVar, Sequence
from .nodes import LinkedListNodes

T = TypeVar("T")

def flash_sort(items: Sequence[int]) -> List[int]:
    """
    Flash sort (O(n) to O(n^2)), distribution-based, very fast for certain data.

    Args:
        items (Sequence[int]): Sequence of non-negative integers.

    Returns:
        List[int]: Sorted list.

    Raises:
        TypeError: If items is not a sequence.
        ValueError: If any element is not a non-negative integer.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n) best, O(n^2) worst
        - Space: O(n)
        - Stable: No
        - Used for large, uniformly distributed integer arrays.

    Examples:
        >>> flash_sort([6, 4, 1, 7, 9, 1, 3])
        [1, 1, 3, 4, 6, 7, 9]
        >>> flash_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> flash_sort([7, -2, 6])
        Traceback (most recent call last):
            ...
        ValueError: All elements must be non-negative integers.
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")
    for x in items:
        if not isinstance(x, int) or x < 0:
            raise ValueError("All elements must be non-negative integers.")

    arr = list(items)
    n = len(arr)
    if n == 0:
        return []
    min_val, max_val = min(arr), max(arr)
    if min_val == max_val:
        return arr
    m = int(0.45 * n) + 1
    counts = [0] * m
    for x in arr:
        idx = int((m - 1) * (x - min_val) / (max_val - min_val))
        counts[idx] += 1
    for i in range(1, m):
        counts[i] += counts[i - 1]
    output = [0] * n
    for x in reversed(arr):
        idx = int((m - 1) * (x - min_val) / (max_val - min_val))
        counts[idx] -= 1
        output[counts[idx]] = x
    return output

class SinglyLinkedList(Generic[T]):
    """
    Singly linked list for non-negative integers.

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

def flash_sort_singly(ll: SinglyLinkedList) -> None:
    """
    Flash sort (O(n) best, O(n^2) worst), sorts singly linked list of non-negative ints.

    Args:
        ll (SinglyLinkedList): Linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If values not int.
        ValueError: If empty or negative.

    Notes:
        - Time: O(n) best, O(n^2) worst.
        - Space: O(n).
        - Stable: No.

    Examples:
        >>> ll = SinglyLinkedList([6, 4, 1, 7, 9, 1, 3])
        >>> flash_sort_singly(ll)
        >>> ll.to_list()
        [1, 1, 3, 4, 6, 7, 9]
    """
    arr = ll.to_list()
    n = len(arr)
    if n == 0:
        raise ValueError("Linked list must not be empty.")
    for x in arr:
        if not isinstance(x, int) or x < 0:
            raise ValueError("All elements must be non-negative integers.")
    min_val, max_val = min(arr), max(arr)
    if min_val == max_val:
        out = arr.copy()
    else:
        m = int(0.45 * n) + 1
        counts = [0] * m
        for x in arr:
            idx = int((m - 1) * (x - min_val) / (max_val - min_val))
            counts[idx] += 1
        for i in range(1, m):
            counts[i] += counts[i - 1]
        out = [0] * n
        for x in reversed(arr):
            idx = int((m - 1) * (x - min_val) / (max_val - min_val))
            counts[idx] -= 1
            out[counts[idx]] = x
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

def flash_sort_doubly(ll: DoublyLinkedList) -> None:
    """
    Flash sort (O(n) best, O(n^2) worst), sorts doubly linked list of non-negative ints.

    Args:
        ll (DoublyLinkedList): Doubly linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If values not int.
        ValueError: If empty or negative.

    Notes:
        - Time: O(n) best, O(n^2) worst.
        - Space: O(n).
        - Stable: No.

    Examples:
        >>> dl = DoublyLinkedList([6, 4, 1, 7, 9, 1, 3])
        >>> flash_sort_doubly(dl)
        >>> dl.to_list()
        [1, 1, 3, 4, 6, 7, 9]
    """
    arr = ll.to_list()
    n = len(arr)
    if n == 0:
        raise ValueError("Linked list must not be empty.")
    for x in arr:
        if not isinstance(x, int) or x < 0:
            raise ValueError("All elements must be non-negative integers.")
    min_val, max_val = min(arr), max(arr)
    if min_val == max_val:
        out = arr.copy()
    else:
        m = int(0.45 * n) + 1
        counts = [0] * m
        for x in arr:
            idx = int((m - 1) * (x - min_val) / (max_val - min_val))
            counts[idx] += 1
        for i in range(1, m):
            counts[i] += counts[i - 1]
        out = [0] * n
        for x in reversed(arr):
            idx = int((m - 1) * (x - min_val) / (max_val - min_val))
            counts[idx] -= 1
            out[counts[idx]] = x
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

def flash_sort_circular(ll: CircularLinkedList) -> None:
    """
    Flash sort (O(n) best, O(n^2) worst), sorts circular linked list of non-negative ints.

    Args:
        ll (CircularLinkedList): List to sort.

    Returns:
        None

    Raises:
        TypeError: If values not int.
        ValueError: If empty or negative.

    Notes:
        - Time: O(n) best, O(n^2) worst.
        - Space: O(n).
        - Stable: No.

    Examples:
        >>> cl = CircularLinkedList([6, 4, 1, 7, 9, 1, 3])
        >>> flash_sort_circular(cl)
        >>> cl.to_list()
        [1, 1, 3, 4, 6, 7, 9]
    """
    arr = ll.to_list()
    n = len(arr)
    if n == 0:
        raise ValueError("Linked list must not be empty.")
    for x in arr:
        if not isinstance(x, int) or x < 0:
            raise ValueError("All elements must be non-negative integers.")
    min_val, max_val = min(arr), max(arr)
    if min_val == max_val:
        out = arr.copy()
    else:
        m = int(0.45 * n) + 1
        counts = [0] * m
        for x in arr:
            idx = int((m - 1) * (x - min_val) / (max_val - min_val))
            counts[idx] += 1
        for i in range(1, m):
            counts[i] += counts[i - 1]
        out = [0] * n
        for x in reversed(arr):
            idx = int((m - 1) * (x - min_val) / (max_val - min_val))
            counts[idx] -= 1
            out[counts[idx]] = x
    node = ll.head
    for value in out:
        node.value = value
        node = node.next
        if node == ll.head:
            break