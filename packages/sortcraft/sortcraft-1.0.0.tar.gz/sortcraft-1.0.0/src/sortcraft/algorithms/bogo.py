from typing import TypeVar, Generic, Optional, List, Sequence
import random
from .nodes import LinkedListNodes

T = TypeVar("T")

def bogo_sort(items: Sequence[T], max_attempts: int = 50000) -> List[T]:
    """
    Bogo sort (stupid sort, O(∞) expected), randomly shuffles list until sorted.

    Args:
        items (Sequence[T]): Sequence of comparable items.
        max_attempts (int, optional): Safety limit to prevent infinite loops.
            Defaults to 50000.

    Returns:
        List[T]: Sorted list if successful, or the final shuffled list if max_attempts exceeded.

    Raises:
        TypeError: If items is not a sequence or items are not comparable.
        ValueError: If max_attempts is not a positive integer.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n!)
        - Space: O(n)
        - Stable: Yes (if you get lucky).
        - Used only for jokes, demos, or unit tests for misbehavior.

    Examples:
        >>> bogo_sort([2, 3, 1], max_attempts=10000)
        [1, 2, 3]

        >>> bogo_sort([], max_attempts=10)
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.

        >>> bogo_sort(["a", "b", "c"], max_attempts=1)
        ['b', 'c', 'a']  # May vary
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")
    if not isinstance(max_attempts, int) or max_attempts < 1:
        raise ValueError("max_attempts must be a positive integer.")

    arr = list(items)
    attempts = 0
    try:
        _ = sorted(arr)
    except Exception as e:
        raise TypeError("Elements must be comparable for sorting.") from e

    while arr != sorted(arr) and attempts < max_attempts:
        random.shuffle(arr)
        attempts += 1
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
        result = []
        node = self.head
        while node:
            result.append(node.value)
            node = node.next
        return result

def bogo_sort_singly(ll: SinglyLinkedList[T], max_attempts: int = 50000) -> None:
    """
    Bogo sort (O(n!), may never finish), randomly shuffles list until sorted.

    Args:
        ll (SinglyLinkedList[T]): List to sort (modifies in-place, by values).
        max_attempts (int, optional): Safety limit. Defaults to 50000.

    Returns:
        None

    Raises:
        TypeError: If elements are not comparable.
        ValueError: If max_attempts is not a positive integer.
        ValueError: If linked list is empty.

    Notes:
        - Time: O(n!)
        - Space: O(n)
        - Stable: Yes (if you get lucky).

    Examples:
        >>> ll = SinglyLinkedList([2, 3, 1])
        >>> bogo_sort_singly(ll, max_attempts=10000)
        >>> ll.to_list()
        [1, 2, 3]  # if lucky
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Linked list must not be empty.")
    if not isinstance(max_attempts, int) or max_attempts < 1:
        raise ValueError("max_attempts must be a positive integer.")
    try:
        _ = sorted(arr)
    except Exception as e:
        raise TypeError("Elements must be comparable for sorting.") from e

    attempts = 0
    while arr != sorted(arr) and attempts < max_attempts:
        random.shuffle(arr)
        attempts += 1

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

def bogo_sort_doubly(ll: DoublyLinkedList[T], max_attempts: int = 50000) -> None:
    """
    Bogo sort (O(n!), may never finish), randomly shuffles list until sorted.

    Args:
        ll (DoublyLinkedList[T]): List to sort (modifies in-place, by values).
        max_attempts (int, optional): Safety limit. Defaults to 50000.

    Returns:
        None

    Raises:
        TypeError: If elements are not comparable.
        ValueError: If max_attempts is not positive.
        ValueError: If linked list is empty.

    Notes:
        - Time: O(n!)
        - Space: O(n)
        - Stable: Yes (if lucky).

    Examples:
        >>> dl = DoublyLinkedList([2, 3, 1])
        >>> bogo_sort_doubly(dl, max_attempts=10000)
        >>> dl.to_list()
        [1, 2, 3]  # if lucky
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Linked list must not be empty.")
    if not isinstance(max_attempts, int) or max_attempts < 1:
        raise ValueError("max_attempts must be a positive integer.")
    try:
        _ = sorted(arr)
    except Exception as e:
        raise TypeError("Elements must be comparable for sorting.") from e

    attempts = 0
    while arr != sorted(arr) and attempts < max_attempts:
        random.shuffle(arr)
        attempts += 1

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

def bogo_sort_circular(ll: CircularLinkedList[T], max_attempts: int = 50000) -> None:
    """
    Bogo sort (O(n!), may never finish), randomly shuffles list until sorted.

    Args:
        ll (CircularLinkedList[T]): List to sort (modifies in-place, by values).
        max_attempts (int, optional): Safety limit. Defaults to 50000.

    Returns:
        None

    Raises:
        TypeError: If elements are not comparable.
        ValueError: If max_attempts is not positive.
        ValueError: If linked list is empty.

    Notes:
        - Time: O(n!)
        - Space: O(n)
        - Stable: Yes (if lucky).

    Examples:
        >>> cl = CircularLinkedList([1, 3, 2])
        >>> bogo_sort_circular(cl, max_attempts=10000)
        >>> cl.to_list()
        [1, 2, 3]  # if lucky
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Linked list must not be empty.")
    if not isinstance(max_attempts, int) or max_attempts < 1:
        raise ValueError("max_attempts must be a positive integer.")
    try:
        _ = sorted(arr)
    except Exception as e:
        raise TypeError("Elements must be comparable for sorting.") from e

    attempts = 0
    while arr != sorted(arr) and attempts < max_attempts:
        random.shuffle(arr)
        attempts += 1

    node = ll.head
    for value in arr:
        node.value = value
        node = node.next
        if node == ll.head:
            break