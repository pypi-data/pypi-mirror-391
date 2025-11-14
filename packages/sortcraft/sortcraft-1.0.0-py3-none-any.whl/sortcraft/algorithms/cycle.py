from typing import TypeVar, Generic, Optional, List, Sequence
from .nodes import LinkedListNodes

T = TypeVar("T")

def cycle_sort(items: Sequence[T]) -> List[T]:
    """
    Cycle sort (in-place, O(n^2)), minimizes memory writes.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If the input sequence is empty.

    Notes:
        - Time: O(n^2)
        - Space: O(n)
        - Stable: No
        - Used where write operations are expensive.

    Examples:
        >>> cycle_sort([3, 2, 4, 1])
        [1, 2, 3, 4]
        >>> cycle_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> cycle_sort(['c', 'a', 'b'])
        ['a', 'b', 'c']
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")

    arr = list(items)
    n = len(arr)
    try:
        _ = arr[0] < arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    for cycle_start in range(n - 1):
        item = arr[cycle_start]
        pos = cycle_start
        for i in range(cycle_start + 1, n):
            try:
                if arr[i] < item:
                    pos += 1
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        if pos == cycle_start:
            continue
        while item == arr[pos]:
            pos += 1
        arr[pos], item = item, arr[pos]
        while pos != cycle_start:
            pos = cycle_start
            for i in range(cycle_start + 1, n):
                try:
                    if arr[i] < item:
                        pos += 1
                except Exception as e:
                    raise TypeError("Elements must be comparable for sorting.") from e
            while item == arr[pos]:
                pos += 1
            arr[pos], item = item, arr[pos]
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

def cycle_sort_singly(ll: SinglyLinkedList[T]) -> None:
    """
    Cycle sort (in-place, O(n^2)), minimizes writes; sorts singly linked list.

    Args:
        ll (SinglyLinkedList[T]): Linked list to sort (modifies in-place, by values).

    Returns:
        None

    Raises:
        TypeError: If elements are not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n^2)
        - Space: O(1) (node values rewritten in place)
        - Stable: No
        - Used when writes are expensive.

    Examples:
        >>> ll = SinglyLinkedList([3, 2, 4, 1])
        >>> cycle_sort_singly(ll)
        >>> ll.to_list()
        [1, 2, 3, 4]
    """
    arr = ll.to_list()
    n = len(arr)
    if n == 0:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] < arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e
    for cycle_start in range(n - 1):
        item = arr[cycle_start]
        pos = cycle_start
        for i in range(cycle_start + 1, n):
            try:
                if arr[i] < item:
                    pos += 1
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        if pos == cycle_start:
            continue
        while item == arr[pos]:
            pos += 1
        arr[pos], item = item, arr[pos]
        while pos != cycle_start:
            pos = cycle_start
            for i in range(cycle_start + 1, n):
                try:
                    if arr[i] < item:
                        pos += 1
                except Exception as e:
                    raise TypeError("Elements must be comparable for sorting.") from e
            while item == arr[pos]:
                pos += 1
            arr[pos], item = item, arr[pos]
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

def cycle_sort_doubly(ll: DoublyLinkedList[T]) -> None:
    """
    Cycle sort (in-place, O(n^2)), minimizes writes; sorts doubly linked list.

    Args:
        ll (DoublyLinkedList[T]): Doubly linked list to sort in-place.

    Returns:
        None

    Raises:
        TypeError: If not comparable.
        ValueError: If empty.

    Notes:
        - Time: O(n^2)
        - Space: O(1)
        - Stable: No

    Examples:
        >>> dl = DoublyLinkedList([3, 2, 4, 1])
        >>> cycle_sort_doubly(dl)
        >>> dl.to_list()
        [1, 2, 3, 4]
    """
    arr = ll.to_list()
    n = len(arr)
    if n == 0:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] < arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e
    for cycle_start in range(n - 1):
        item = arr[cycle_start]
        pos = cycle_start
        for i in range(cycle_start + 1, n):
            try:
                if arr[i] < item:
                    pos += 1
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        if pos == cycle_start:
            continue
        while item == arr[pos]:
            pos += 1
        arr[pos], item = item, arr[pos]
        while pos != cycle_start:
            pos = cycle_start
            for i in range(cycle_start + 1, n):
                try:
                    if arr[i] < item:
                        pos += 1
                except Exception as e:
                    raise TypeError("Elements must be comparable for sorting.") from e
            while item == arr[pos]:
                pos += 1
            arr[pos], item = item, arr[pos]
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

def cycle_sort_circular(ll: CircularLinkedList[T]) -> None:
    """
    Cycle sort (in-place, O(n^2)), minimizes writes; sorts circular linked list.

    Args:
        ll (CircularLinkedList[T]): List to sort (modifies in-place, by values).

    Returns:
        None

    Raises:
        TypeError: If elements are not comparable.
        ValueError: If input is empty.

    Notes:
        - Time: O(n^2)
        - Space: O(1)
        - Stable: No

    Examples:
        >>> cl = CircularLinkedList([3, 2, 4, 1])
        >>> cycle_sort_circular(cl)
        >>> cl.to_list()
        [1, 2, 3, 4]
    """
    arr = ll.to_list()
    n = len(arr)
    if n == 0:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] < arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e
    for cycle_start in range(n - 1):
        item = arr[cycle_start]
        pos = cycle_start
        for i in range(cycle_start + 1, n):
            try:
                if arr[i] < item:
                    pos += 1
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        if pos == cycle_start:
            continue
        while item == arr[pos]:
            pos += 1
        arr[pos], item = item, arr[pos]
        while pos != cycle_start:
            pos = cycle_start
            for i in range(cycle_start + 1, n):
                try:
                    if arr[i] < item:
                        pos += 1
                except Exception as e:
                    raise TypeError("Elements must be comparable for sorting.") from e
            while item == arr[pos]:
                pos += 1
            arr[pos], item = item, arr[pos]
    node = ll.head
    for value in arr:
        node.value = value
        node = node.next
        if node == ll.head:
            break