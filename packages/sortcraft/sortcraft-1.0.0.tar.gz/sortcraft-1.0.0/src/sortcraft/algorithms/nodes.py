from typing import TypeVar, Generic, Optional

T = TypeVar("T")

class LinkedListNodes:
    """
    Container for various node types used in linked lists.

    Includes:
      - SinglyNode: Node for singly linked list.
      - DoublyNode: Node for doubly linked list.
      - CircularNode: Node for circular singly linked list.
    """

    class SinglyNode(Generic[T]):
        """
        Node for singly linked list.

        Args:
            value (T): Value to store in the node.

        Attributes:
            value (T): Node value.
            next (SinglyNode[T]): Next node or None.
        """
        def __init__(self, value: T):
            self.value: T = value
            self.next: Optional["LinkedListNodes.SinglyNode[T]"] = None

    class DoublyNode(Generic[T]):
        """
        Node for doubly linked list.

        Args:
            value (T): Value to store.

        Attributes:
            value (T): Node value.
            prev (DoublyNode[T]): Previous node or None.
            next (DoublyNode[T]): Next node or None.
        """
        def __init__(self, value: T):
            self.value: T = value
            self.prev: Optional["LinkedListNodes.DoublyNode[T]"] = None
            self.next: Optional["LinkedListNodes.DoublyNode[T]"] = None

    class CircularNode(Generic[T]):
        """
        Node for circular singly linked list.

        Args:
            value (T): Node value.

        Attributes:
            value (T): Node value.
            next (CircularNode[T]): Next node in circle or self if single.
        """
        def __init__(self, value: T):
            self.value: T = value
            self.next: Optional["LinkedListNodes.CircularNode[T]"] = None