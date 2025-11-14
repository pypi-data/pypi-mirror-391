from typing import TypeVar, Generic, Optional, List, Sequence
from .nodes import LinkedListNodes

T = TypeVar("T")

def cocktail_sort(items: Sequence[T]) -> List[T]:
    """
    Cocktail Shaker sort (stable, bidirectional bubble, O(n^2)), returns sorted list.

    Args:
        items (Sequence[T]): Sequence of comparable items.

    Returns:
        List[T]: Sorted list.

    Raises:
        TypeError: If items is not a sequence or elements are not comparable.
        ValueError: If input sequence is empty.

    Notes:
        - Time: O(n^2).
        - Space: O(n).
        - Stable: Yes.

    Examples:
        >>> cocktail_sort([4, 2, 3, 1])
        [1, 2, 3, 4]
        >>> cocktail_sort([])
        Traceback (most recent call last):
            ...
        ValueError: Input sequence must not be empty.
        >>> cocktail_sort(['c', 'a', 'b'])
        ['a', 'b', 'c']
    """
    if not isinstance(items, Sequence):
        raise TypeError("Input must be a sequence (list, tuple, etc.).")
    if not items:
        raise ValueError("Input sequence must not be empty.")

    arr = list(items)
    n = len(arr)
    try:
        _ = arr[0] > arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    swapped = True
    start, end = 0, n - 1
    while swapped:
        swapped = False
        for i in range(start, end):
            try:
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    swapped = True
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        if not swapped:
            break
        swapped = False
        end -= 1
        for i in range(end - 1, start - 1, -1):
            try:
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    swapped = True
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        start += 1
    return arr

class SinglyLinkedList(Generic[T]):
    """
    Singly linked list.

    Args:
        items (Optional[List[T]]): Initial items.

    Attributes:
        head (Optional[LinkedListNodes.SinglyNode[T]]): Head node.

    Examples:
        >>> ll = SinglyLinkedList([4, 2, 3, 1])
        >>> ll.to_list()
        [4, 2, 3, 1]
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

def cocktail_sort_singly(ll: SinglyLinkedList[T]) -> None:
    """
    Cocktail shaker sort (stable, bidirectional bubble, O(n^2)), sorts linked list in place.

    Args:
        ll (SinglyLinkedList[T]): Linked list to sort (modifies in-place, by values).

    Returns:
        None

    Raises:
        TypeError: If elements are not comparable.
        ValueError: If input linked list is empty.

    Notes:
        - Time: O(n^2).
        - Space: O(1).
        - Stable: Yes.

    Examples:
        >>> ll = SinglyLinkedList([4, 2, 3, 1])
        >>> cocktail_sort_singly(ll)
        >>> ll.to_list()
        [1, 2, 3, 4]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] > arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    n = len(arr)
    swapped = True
    start, end = 0, n - 1
    while swapped:
        swapped = False
        for i in range(start, end):
            try:
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    swapped = True
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        if not swapped:
            break
        swapped = False
        end -= 1
        for i in range(end - 1, start - 1, -1):
            try:
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    swapped = True
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        start += 1
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

def cocktail_sort_doubly(ll: DoublyLinkedList[T]) -> None:
    """
    Cocktail shaker sort for doubly linked list (in-place, stable, O(n^2)).

    Args:
        ll (DoublyLinkedList[T]): Doubly linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.
        ValueError: If linked list is empty.

    Notes:
        - Time: O(n^2).
        - Space: O(1).
        - Stable: Yes.

    Examples:
        >>> dl = DoublyLinkedList([6, 2, 1, 4, 3])
        >>> cocktail_sort_doubly(dl)
        >>> dl.to_list()
        [1, 2, 3, 4, 6]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] > arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    n = len(arr)
    swapped = True
    start, end = 0, n - 1
    while swapped:
        swapped = False
        for i in range(start, end):
            try:
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    swapped = True
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        if not swapped:
            break
        swapped = False
        end -= 1
        for i in range(end - 1, start - 1, -1):
            try:
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    swapped = True
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        start += 1
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

def cocktail_sort_circular(ll: CircularLinkedList[T]) -> None:
    """
    Cocktail shaker sort (stable, O(n^2)), sorts circular linked list in-place.

    Args:
        ll (CircularLinkedList[T]): Circular linked list to sort.

    Returns:
        None

    Raises:
        TypeError: If elements not comparable.
        ValueError: If input linked list is empty.

    Notes:
        - Time: O(n^2).
        - Space: O(1).
        - Stable: Yes.

    Examples:
        >>> cl = CircularLinkedList([3, 1, 2])
        >>> cocktail_sort_circular(cl)
        >>> cl.to_list()
        [1, 2, 3]
    """
    arr = ll.to_list()
    if not arr:
        raise ValueError("Input linked list must not be empty.")
    try:
        _ = arr[0] > arr[0]
    except Exception as e:
        raise TypeError("Elements must be comparable.") from e

    n = len(arr)
    swapped = True
    start, end = 0, n - 1
    while swapped:
        swapped = False
        for i in range(start, end):
            try:
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    swapped = True
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        if not swapped:
            break
        swapped = False
        end -= 1
        for i in range(end - 1, start - 1, -1):
            try:
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    swapped = True
            except Exception as e:
                raise TypeError("Elements must be comparable for sorting.") from e
        start += 1
    node = ll.head
    for value in arr:
        node.value = value
        node = node.next
        if node == ll.head:
            break