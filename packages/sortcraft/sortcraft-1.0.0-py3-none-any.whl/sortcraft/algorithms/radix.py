from typing import Generic, Optional, List, TypeVar, Sequence
from .nodes import LinkedListNodes

T = TypeVar("T")

def radix_sort(items: Sequence[int]) -> List[int]:
    """
    Radix sort (stable, O(nk)), returns a new sorted list.

    Args:
        items (Sequence[int]): Sequence of non-negative integers.

    Returns:
        List[int]: Sorted list.

    Raises:
        TypeError: If items is not a sequence or elements are not integers.
        ValueError: If any element is negative.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(nk), k is number of digits.
        - Space: O(n + k).
        - Stable: Yes.
        - Works for non-negative integers only.

    Examples:
        >>> radix_sort([170, 45, 75, 90, 802, 24, 2, 66])
        [2, 24, 45, 66, 75, 90, 170, 802]
        >>> radix_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> radix_sort([7, -2, 6])
        Traceback (most recent call last):
            ...
        ValueError: All elements must be non-negative integers.
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")
    for x in items:
        if not isinstance(x, int):
            raise TypeError("All elements must be integers.")
        if x < 0:
            raise ValueError("All elements must be non-negative integers.")

    arr = list(items)
    if not arr:
        return arr
    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        arr = _counting_sort_exp(arr, exp)
        exp *= 10
    return arr

def _counting_sort_exp(items: List[int], exp: int) -> List[int]:
    n = len(items)
    output = [0] * n
    count = [0] * 10
    for num in items:
        index = (num // exp) % 10
        count[index] += 1
    for i in range(1, 10):
        count[i] += count[i - 1]
    for num in reversed(items):
        index = (num // exp) % 10
        output[count[index] - 1] = num
        count[index] -= 1
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

def radix_sort_singly(ll: SinglyLinkedList) -> None:
    """
    Radix sort (stable, O(nk)), sorts singly linked list of non-negative integers.

    Args:
        ll (SinglyLinkedList): Linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements are not integers.
        ValueError: If input is empty or value is negative.

    Notes:
        - Time: O(nk), k = number of digits.
        - Space: O(n + k).
        - Stable: Yes.
        - Works for non-negative integers only.

    Examples:
        >>> ll = SinglyLinkedList([170, 45, 75, 90, 802, 24, 2, 66])
        >>> radix_sort_singly(ll)
        >>> ll.to_list()
        [2, 24, 45, 66, 75, 90, 170, 802]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    for x in arr:
        if not isinstance(x, int):
            raise TypeError("All elements must be integers.")
        if x < 0:
            raise ValueError("All elements must be non-negative integers.")
    if not arr:
        return
    max_val = max(arr)
    exp = 1
    def _counting_sort_exp(items: List[int], exp: int) -> List[int]:
        n = len(items)
        output = [0] * n
        count = [0] * 10
        for num in items:
            index = (num // exp) % 10
            count[index] += 1
        for i in range(1, 10):
            count[i] += count[i - 1]
        for num in reversed(items):
            index = (num // exp) % 10
            output[count[index] - 1] = num
            count[index] -= 1
        return output
    while max_val // exp > 0:
        arr = _counting_sort_exp(arr, exp)
        exp *= 10
    node = ll.head
    for value in arr:
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

def radix_sort_doubly(ll: DoublyLinkedList) -> None:
    """
    Radix sort (stable, O(nk)), sorts doubly linked list of non-negative integers.

    Args:
        ll (DoublyLinkedList): Doubly linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements are not integers.
        ValueError: If input is empty or value is negative.

    Notes:
        - Time: O(nk), k = number of digits.
        - Space: O(n + k).
        - Stable: Yes.
        - Works for non-negative integers only.

    Examples:
        >>> dl = DoublyLinkedList([170, 45, 75, 90, 802, 24, 2, 66])
        >>> radix_sort_doubly(dl)
        >>> dl.to_list()
        [2, 24, 45, 66, 75, 90, 170, 802]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    for x in arr:
        if not isinstance(x, int):
            raise TypeError("All elements must be integers.")
        if x < 0:
            raise ValueError("All elements must be non-negative integers.")
    if not arr:
        return
    max_val = max(arr)
    exp = 1
    def _counting_sort_exp(items: List[int], exp: int) -> List[int]:
        n = len(items)
        output = [0] * n
        count = [0] * 10
        for num in items:
            index = (num // exp) % 10
            count[index] += 1
        for i in range(1, 10):
            count[i] += count[i - 1]
        for num in reversed(items):
            index = (num // exp) % 10
            output[count[index] - 1] = num
            count[index] -= 1
        return output
    while max_val // exp > 0:
        arr = _counting_sort_exp(arr, exp)
        exp *= 10
    node = ll.head
    for value in arr:
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

def radix_sort_circular(ll: CircularLinkedList) -> None:
    """
    Radix sort (stable, O(nk)), sorts circular linked list of non-negative integers.

    Args:
        ll (CircularLinkedList): List to sort.

    Returns:
        None

    Raises:
        TypeError: If elements are not integers.
        ValueError: If input is empty or value is negative.

    Notes:
        - Time: O(nk), k = number of digits.
        - Space: O(n + k).
        - Stable: Yes.
        - Works for non-negative integers only.

    Examples:
        >>> cl = CircularLinkedList([170, 45, 75, 90, 802, 24, 2, 66])
        >>> radix_sort_circular(cl)
        >>> cl.to_list()
        [2, 24, 45, 66, 75, 90, 170, 802]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    for x in arr:
        if not isinstance(x, int):
            raise TypeError("All elements must be integers.")
        if x < 0:
            raise ValueError("All elements must be non-negative integers.")
    if not arr:
        return
    max_val = max(arr)
    exp = 1
    def _counting_sort_exp(items: List[int], exp: int) -> List[int]:
        n = len(items)
        output = [0] * n
        count = [0] * 10
        for num in items:
            index = (num // exp) % 10
            count[index] += 1
        for i in range(1, 10):
            count[i] += count[i - 1]
        for num in reversed(items):
            index = (num // exp) % 10
            output[count[index] - 1] = num
            count[index] -= 1
        return output
    while max_val // exp > 0:
        arr = _counting_sort_exp(arr, exp)
        exp *= 10
    node = ll.head
    for value in arr:
        node.value = value
        node = node.next
        if node == ll.head:
            break