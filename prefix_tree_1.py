"""CSC148 Assignment 2: Autocompleter classes

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===
This file contains the design of a public interface (Autocompleter) and two
implementation of this interface, SimplePrefixTree and CompressedPrefixTree.
You'll complete both of these subclasses over the course of this assignment.

As usual, be sure not to change any parts of the given *public interface* in the
starter code---and this includes the instance attributes, which we will be
testing directly! You may, however, add new private attributes, methods, and
top-level functions to this file.
"""
from __future__ import annotations
from typing import Any, List, Optional, Tuple


################################################################################
# The Autocompleter ADT
################################################################################
class Autocompleter:
    """An abstract class representing the Autocompleter Abstract Data Type.
    """

    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        raise NotImplementedError

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        raise NotImplementedError

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        raise NotImplementedError

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        raise NotImplementedError


################################################################################
# SimplePrefixTree (Tasks 1-3)
################################################################################
class SimplePrefixTree(Autocompleter):
    """A simple prefix tree.

    This class follows the implementation described on the assignment handout.
    Note that we've made the attributes public because we will be accessing them
    directly for testing purposes.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    weight_type:
        The method in which the weight of this subtree will be calculated
        (either 'sum' or 'average').
    subtrees:
        A list of subtrees of this prefix tree.
    _leaf_count:
        The amount of leaves this prefix tree has. If it is a leaf itself,
        its _leaf_count == 1.
    _sum_weight:
        The total weight for this prefix tree. This takes into account all the
        leaves the tree has. It does not store an average but rather the total
        sum of the weights. if the prefix tree is a leaf itself then its
        _sum_weight is the weight of the leaf.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - ("prefixes grow by 1")
      If len(self.subtrees) > 0, and subtree in self.subtrees, and subtree
      is non-empty and not a leaf, then

          subtree.value == self.value + [x], for some element x

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Any
    weight: float
    subtrees: List[SimplePrefixTree]
    weight_type: str
    _leaf_count: int
    _sum_weight: float

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty simple prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        self.value = []
        self.subtrees = []
        self.weight = 0.0
        self.weight_type = weight_type
        self._leaf_count = 0
        self._sum_weight = 0.0

    def __len__(self) -> int:
        """Return the number of values (leaves) stored in this SimplePrefixTree.
        """
        if self.is_empty():
            return 0
        elif self.is_leaf():
            return 1
        else:
            count = 0
            for subtree in self.subtrees:
                count = count + len(subtree)
            return count

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this SimplePrefixTree.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this SimplePrefixTree
                2) was previously inserted with the SAME prefix sequence
        """
        update_leaf = self._insert_helper(value, weight, prefix, 1,
                                          self.weight_type)
        self._update_weight(self.weight_type, update_leaf, weight)
        self._sort_subtrees()

    def _insert_helper(self, value: Any, weight: float, prefix: List,
                       i: int, wtype: str) -> bool:
        """A helper function for insert.
        """
        if i <= len(prefix):
            if prefix[0:i] in [x.value for x in self.subtrees]:
                index = [x.value for x in self.subtrees].index(prefix[0:i])
                update_leaf = self.subtrees[index]._insert_helper(value, weight,
                                                                  prefix, i + 1,
                                                                  wtype)
                self.subtrees[index]._update_weight(wtype, update_leaf, weight)
                self.subtrees[index]._sort_subtrees()
            else:
                newtree = SimplePrefixTree(wtype)
                newtree.value = prefix[0:i]
                self.subtrees.append(newtree)
                update_leaf = newtree._insert_helper(value, weight, prefix,
                                                     i + 1, wtype)
                newtree._update_weight(wtype, update_leaf, weight)
                newtree._sort_subtrees()
            return update_leaf
        else:
            if value in [x.value for x in self.subtrees]:
                index = [x.value for x in self.subtrees].index(value)
                self.subtrees[index].weight += weight
                self.subtrees[index]._sum_weight += weight
                return False
            else:
                endtree = SimplePrefixTree(wtype)
                endtree.value = value
                endtree.weight = float(weight)
                endtree._leaf_count = 1
                endtree._sum_weight = weight
                self.subtrees.append(endtree)
                return True

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        # self._remove_helper(prefix, 1, self)
        pass

    def _remove_helper(self, prefix: List, i: int,
                       prev: SimplePrefixTree) -> None:
        # if i <= len(prefix):
        #     if prefix[0:i] not in [x.value for x in self.subtrees]:
        #         return None
        #     index = [x.value for x in self.subtrees].index(prefix[0:i])
        #     empty = self.subtrees[index]._remove_helper(prefix, i + 1, self)
        #     if empty:
        #         index = prev.subtrees.index(self)
        #         prev.subtrees.pop(index)
        #         return len(prev.subtrees == 0)
        #     return False
        # else:
        #     index = prev.subtrees.index(self)
        #     prev.subtrees.pop(index)
        #     return len(prev.subtrees == 0)
        pass

    def _update_weight(self, wtype: str, update_leaf: bool, weight: float) \
            -> None:
        if update_leaf:
            self._leaf_count += 1
            self._sum_weight += weight
        else:
            self._sum_weight += weight

        if wtype == 'sum':
            self.weight = float(self._sum_weight)
        else:
            self.weight = float(self._sum_weight / self._leaf_count)

    def _sort_subtrees(self) -> None:
        """Helper method that sorts a simple prefix tree's list of subtrees.
        """
        asc = sorted(self.subtrees, key=lambda x: x.weight)
        asc.reverse()
        self.subtrees = asc

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        return self._autocomplete_helper(prefix, 1, limit)

    def _autocomplete_helper(self, prefix: list, i: int,
                             limit: Optional[int]
                             = None) -> List[Tuple[Any, float]]:
        if i <= len(prefix):
            if prefix[0:i] not in [x.value for x in self.subtrees]:
                return []
            index = [x.value for x in self.subtrees].index(prefix[0:i])
            x = self.subtrees[index]._autocomplete_helper(prefix, i + 1, limit)
            return x
        else:
            if limit is None:
                results = self._no_limit_items()
                results = sorted(results, key=lambda x: x[1], reverse=True)
                return results
            else:
                results = self._limited_items(limit)
                results = sorted(results, key=lambda x: x[1], reverse=True)
                return results

    def _no_limit_items(self) -> List[Tuple[Any, float]]:
        """Helper method for autocomplete.

        Returns all items from this prefix tree.

        The return value is a list of tuples (value, weight), this is not
        ordered.
        """
        if self.is_leaf():
            return [(self.value, self.weight)]
        else:
            items = []
            for subtree in self.subtrees:
                items = items + subtree._no_limit_items()
            return items

    def _limited_items(self, limit: int) -> List[Tuple[Any, float]]:
        """Helper method for autocomplete.

        Returns <limit> of the highest-weighted items from this prefix tree.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight.
        """
        if limit == 0:
            return []
        if self.is_leaf():
            return [(self.value, self.weight)]
        else:
            items = []
            lim = limit
            for subtree in self.subtrees:
                items = items + subtree._limited_items(lim - len(items))
            return items

    def is_empty(self) -> bool:
        """Return whether this simple prefix tree is empty."""
        return self.weight == 0.0

    def is_leaf(self) -> bool:
        """Return whether this simple prefix tree is a leaf."""
        return self.weight > 0 and self.subtrees == []

    def __str__(self) -> str:
        """Return a string representation of this tree.

        You may find this method helpful for debugging.
        """
        return self._str_indented()

    def _str_indented(self, depth: int = 0) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.value} ({self.weight})\n'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s


################################################################################
# CompressedPrefixTree (Task 6)
################################################################################
class CompressedPrefixTree(Autocompleter):
    """A compressed prefix tree implementation.

    While this class has the same public interface as SimplePrefixTree,
    (including the initializer!) this version follows the implementation
    described on Task 6 of the assignment handout, which reduces the number of
    tree objects used to store values in the tree.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - **NEW**
      This tree does not contain any compressible internal values.
      (See the assignment handout for a definition of "compressible".)

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Optional[Any]
    weight: float
    subtrees: List[CompressedPrefixTree]

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty simple prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        self.value = []
        self.subtrees = []
        self.weight = 0.0
        self.weight_type = weight_type
        self._leaf_count = 0
        self._sum_weight = 0.0

    def __len__(self) -> int:
        """Return the number of values (leaves) stored in this SimplePrefixTree.
        """
        if self.is_empty():
            return 0
        elif self.is_leaf():
            return 1
        else:
            count = 0
            for subtree in self.subtrees:
                count = count + len(subtree)
            return count

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this SimplePrefixTree.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this SimplePrefixTree
                2) was previously inserted with the SAME prefix sequence
        """
        update_leaf = self._insert_helper(value, weight, prefix, 1)
        self._update_weight(self.weight_type, update_leaf, weight)
        self._sort_subtrees()

    def _insert_helper(self, value: Any, weight: float,
                       prefix: List, i: int) -> bool:
        if i < len(prefix):
            if not self.subtrees:
                temp = CompressedPrefixTree(self.weight_type)
                temp.value = prefix
                new_leaf = CompressedPrefixTree(self.weight_type)
                new_leaf.weight = weight
                new_leaf._leaf_count = 1
                new_leaf._sum_weight = weight
                temp.subtrees.append(new_leaf)

    def _insert_find_prefix(self, prefix: List):
        j = 0
        while j <= len(prefix):
            if prefix[:j] in [x.value for x in self.subtrees]:
                return j
            j += 1
        return False

    def _update_weight(self, update_leaf: bool, weight: float) \
            -> None:
        if update_leaf:
            self._leaf_count += 1
            self._sum_weight += weight
        else:
            self._sum_weight += weight

        if self.weight_type == 'sum':
            self.weight = float(self._sum_weight)
        else:
            self.weight = float(self._sum_weight / self._leaf_count)

    def _sort_subtrees(self) -> None:
        """Helper method that sorts a simple prefix tree's list of subtrees.
        """
        asc = sorted(self.subtrees, key=lambda x: x.weight)
        asc.reverse()
        self.subtrees = asc

    def is_empty(self) -> bool:
        """Return whether this simple prefix tree is empty."""
        return self.weight == 0.0

    def is_leaf(self) -> bool:
        """Return whether this simple prefix tree is a leaf."""
        return self.weight > 0 and self.subtrees == []

    def __str__(self) -> str:
        """Return a string representation of this tree.

        You may find this method helpful for debugging.
        """
        return self._str_indented()

    def _str_indented(self, depth: int = 0) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.value} ({self.weight})\n'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s


if __name__ == '__main__':
    tree = SimplePrefixTree("sum")
    # tree.insert('no', 3, ['n', 'o'])
    # tree.insert('ab', 1, ['a', 'b'])
    # tree.insert('try', 1, ['t', 'r', 'y'])
    # tree.insert('trees', 3, ['t', 'r', 'e', 'e', 's'])
    # tree.insert('trie', 5, ['t', 'r', 'i', 'e'])
    # tree.insert({'a': 2}, 1, [True, False, 2, 'abc'])
    # tree.insert('abra', 3, ['a', 'b', 'r', 'a'])
    # tree.insert(123, 2, [5, 2, 3])
    # tree.insert('tree', 2, ['t', 'r', 'e', 'e'])
    # tree.insert('a', 4, ['a'])
    # tree.insert(True, 4, [True])
    # tree.insert('abs', 1, ['a', 'b', 's'])
    # print(tree.autocomplete(['t', 'r', 'e'], limit=4))
    # tree = CompressedPrefixTree("sum")
    # tree.insert("cat", 20, ['c', 'a', 't'])
    # tree.insert("can", 20, ['c', 'a', 'n'])
    print(str(tree))

    # import python_ta
    # python_ta.check_all(config={
    #     'max-nested-blocks': 4
    # })
