import datetime
import os
import time
from functools import partial
from typing import *


class Infix(object):
    def __init__(self, func: Callable) -> None:
        self.func = func

    def __or__(self, other: Self) -> Self:
        return self.func(other)

    def __ror__(self, other: Self) -> Self:
        return Infix(partial(self.func, other))

    def __call__(self, v1, v2):
        return self.func(v1, v2)


# ===Some Infix Operations===
percent_of = Infix(lambda x, y: x / 100 * y)  # x% of y
is_divisible_by = Infix(lambda x, y: x % y == 0)  # checks if x is divisible by y


def clean_list(l: list):
    nl = []
    for i in l:
        if (i is not None) and (i != []) and (i != "") and (i != ()):
            nl.append(i)
    return nl


def clean_list_2d(l: list[list]):
    nl = []
    for i in l:
        r = []
        for j in i:
            if (j is not None) and (j != []) and (j != "") and (j != ()):
                r.append(j)
        nl.append(r)
    return nl


def apply(itr: Iterable, func: Callable) -> list:
    return [func(x) for x in itr]


def apply2D(iter1: Sequence, iter2: Sequence, func: Callable) -> list:
    return [func(item1, item2) for item1, item2 in zip(iter1, iter2)]


def chunks(lst: MutableSequence, n: int):
    result = []
    for i in range(0, len(lst), n):
        result.append(lst[i:i + n])
    return result


def retry(func: Callable, retries: int = 3, args: list[list[Any]] = None):
    if args is None:
        args = []
    i = 0
    if len(args) < retries:
        raise TypeError("Insufficient arguments")
    while True:
        if i >= retries:
            break
        try:
            func(*args[i])
        except:
            print(f"Test {i}: Failed")
            i += 1
        else:
            print(f"Test {i}: Passed")
            i += 1


def find_common_items(*lsts: list) -> list:
    return list(set(lsts[0]).intersection(*lsts[1:]))


def swap(array: list, index1: int, index2: int):
    temp: int = array[index1]
    array[index1] = array[index2]
    array[index2] = temp


def wrap(limit, v):
    return (v + limit) % limit


class Card:
    ACE = 1
    JACK = 11
    QUEEN = 12
    KING = 13

    HEARTS = 40
    DIAMONDS = 41
    SPADE = 42
    CLOVER = 43

    RED = 20
    BLACK = 21

    def __init__(self, number: int, symbol: int):
        self.n = number
        match self.n:
            case 1:
                self.n = "Ace"
            case self.JACK:
                self.n = "Jack"
            case self.QUEEN:
                self.n = "Queen"
            case self.KING:
                self.n = "King"

        self.symbol = symbol
        match self.symbol:
            case self.HEARTS:
                self.symbol = "Hearts"
            case self.DIAMONDS:
                self.symbol = "Diamonds"
            case self.SPADE:
                self.symbol = "Spade"
            case self.CLOVER:
                self.symbol = "Clover"

        self.color = self.RED if self.symbol in [self.HEARTS, self.DIAMONDS] else self.BLACK

    def __repr__(self):
        return f"{self.n} of {self.symbol}"

    @classmethod
    def deck(cls):
        cardDeck = []
        for a in [cls.HEARTS, cls.DIAMONDS, cls.CLOVER, cls.SPADE]:
            for n in range(1, 14):
                cardDeck.append(Card(n, a))
        return cardDeck


class Stopwatch:
    def __init__(self):
        self.t1 = 0
        self.t2 = 0
        self.laps = []

    def start(self):
        self.t1 = time.time()

    def lap(self):
        self.laps.append(self.end())
        self.t1 = 0
        self.t2 = 0
        self.start()

    def elapsed(self):
        return time.time() - self.t1

    def end(self):
        self.t2 = time.time()
        return self.t2 - self.t1


# == Data Structures ==
class Stack:
    def __init__(self):
        self._stack = []

    def __repr__(self):
        return f"Stack{self._stack.__repr__()}"

    def empty(self) -> bool:
        return len(self._stack) == 0

    def size(self) -> int:
        return len(self._stack)

    def top(self):
        return self._stack[-1]

    def push(self, v) -> None:
        self._stack.append(v)

    def pop(self):
        return self._stack.pop()


class Queue:
    def __init__(self, max_size=-1):
        self.max_size = max_size
        self._queue = []

    def __repr__(self):
        return f"Queue{self._queue.__repr__()}"

    def size(self):
        return len(self._queue)

    def empty(self) -> bool:
        return self.size() == 0

    def full(self) -> bool:
        return self.size() == self.max_size

    def enqueue(self, v):
        if self.max_size != -1:
            if self.size() < self.max_size:
                self._queue.append(v)
        else:
            self._queue.append(v)

    def dequeue(self):
        return self._queue.pop(0)

    def front(self):
        return self._queue[0]

    def rear(self):
        return self._queue[-1]


class Node:
    def __init__(self, parent, val=0):
        self.parent = parent
        self.is_root = False if self.parent else True
        self.left_node = None
        self.right_node = None
        self.val = val

    def right(self):
        return self.right_node

    def left(self):
        return self.left_node


class BinaryTree:
    def __init__(self, root_val=0):
        self.root_node = Node(None, root_val)

    def __repr__(self):
        def recurse(node, prefix="", is_left=True):
            if not node:
                return ""

            result = ""
            if node.right_node:
                result += recurse(node.right_node, prefix + ("│   " if is_left else "    "), False)

            result += prefix + ("└── " if is_left else "┌── ") + str(node.val) + "\n"

            if node.left_node:
                result += recurse(node.left_node, prefix + ("    " if is_left else "│   "), True)

            return result

        return recurse(self.root_node)

    def root(self):
        return self.root_node

    def add_node(self, child_of: Node, lr: str, val=0):
        if lr == "l":
            child_of.left_node = Node(child_of, val)
        if lr == "r":
            child_of.right_node = Node(child_of, val)
