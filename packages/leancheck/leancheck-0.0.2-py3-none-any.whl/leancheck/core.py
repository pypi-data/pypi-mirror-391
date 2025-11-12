#!/usr/bin/env python
#
# LeanCheck for Python.  Core module.
#
# (C) 2023-2024  Rudy Matela
# Distributed under the LGPL v2.1 or later (see the file LICENSE)
"""
This is a port of
[Haskell's LeanCheck][] to [Python][].

[Haskell's LeanCheck]: https://hackage.haskell.org/package/leancheck
[Python]: https://python.org

**WIP: This library is currently experimental.**
It works for simple properties,
but the selection of supported types is still limited.

LeanCheck is an enumerative property-based testing library.
It can be used to complement your unit tests.

The usual drill in unit testing involves making assertions
about specific input-output cases of functions, such as:

    assertEqual(sorted([4,2,1,3]), [1,2,3,4])

There are no arguments to the unit test.

In property-based testing (with LeanCheck)
one writes more general properties that should be true
for a given set of arguments.
Properties in this sense are
parameterized unit tests or
parameterized assertions.

For example:
given *any* list, sorting it twice is the same as sorting it once.
We can encode this as a function returning a boolean value:

    >>> def prop_sorted_twice(xs: list[int]) -> bool:
    ...     return sorted(sorted(xs)) == sorted(xs)

For whatever list we provide this function,
it should return `True`.
Now one can use LeanCheck to verify this automatically:

    >>> check(prop_sorted_twice)
    +++ OK, passed 360 tests: prop_sorted_twice
    True

LeanCheck automatically came up with 360 unique lists
to exercise the property.
When the function-under-test is incorrect
LeanCheck may find and report a counterexample:

    *** Failed! Falsifiable after 3 tests:
        prop_sort_len([0, 0])

You then know that an ill input is the list `[0, 0]`.

If you have a bunch of properties (`prop_*`) in a Python file,
just call `leancheck.main()` and all of them will be automatically tested.
In the case of a library, you can put everything under
an if-expression as you would do with `unittest.main()` or `doctest.testmod()`.

    if __name__ == '__main__':
        leancheck.main()
"""


import inspect
import itertools
import sys
import types
import typing


def check(prop, max_tests=360, verbose=True, silent=False, types=[]):
    """
    Checks a property for several enumerated argument values.
    Properties must have type hints
    in order for LeanCheck to be able to know
    which kinds of argument values to generate.

    >>> def prop_commute(x:int, y:int) -> bool:
    ...     return x + y == y + x
    >>> check(prop_commute)
    +++ OK, passed 360 tests: prop_commute
    True

    >>> def prop_increase(x:int, y:int) -> bool:
    ...     return x + y > x
    >>> check(prop_increase)
    *** Failed! Falsifiable after 1 tests:
        prop_increase(0, 0)
    False

    >>> def prop_sorted_twice(xs: list[int]) -> bool:
    ...     return sorted(sorted(xs)) == sorted(xs)
    ...
    >>> check(prop_sorted_twice)
    +++ OK, passed 360 tests: prop_sorted_twice
    True

    >>> def prop_sorted_len(xs: list[int]) -> bool:
    ...     return len(sorted(xs)) == len(xs)
    ...
    >>> check(prop_sorted_len)
    +++ OK, passed 360 tests: prop_sorted_len
    True

    >>> def prop_sorted_wrong(xs: list[int]) -> bool:
    ...     return sorted(xs) == xs
    ...
    >>> check(prop_sorted_wrong)
    *** Failed! Falsifiable after 6 tests:
        prop_sorted_wrong([1, 0])
    False

    >>> check(prop_sorted_twice, silent=True)
    True

    Lambdas do not allow type annotations,
    for them one can use the `types=` option
    to list argument types.

    >>> check(lambda xs: sorted(sorted(xs)) == sorted(xs), types=[list[int]])
    +++ OK, passed 360 tests: <lambda>
    True
    """
    verbose = verbose and not silent
    clear, red, green, blue, yellow = _colour_escapes()
    if not types:
        sig = inspect.signature(prop)
        # print(f"Property's signature: {sig}")
        ret = sig.return_annotation
        if ret != bool and not silent:
            print(f"{yellow}Warning{clear}: property's return value is {ret} and not {bool}")
        types = [par.annotation for par in sig.parameters.values()]
    es = [Enumerator[t] for t in types]
    for i, args in enumerate(itertools.islice(Enumerator.product(*es), max_tests)):
        if not prop(*args):
            if not silent:
                repr_args = ', '.join(map(repr, args))
                print(f"*** Failed! Falsifiable after {i+1} tests:")
                print(f"    {red}{prop.__name__}{clear}({repr_args})")
            return False
    if verbose:
        i = i+1
        exhausted = " (exhausted)" if i < max_tests else ""
        print(f"+++ OK, passed {i} tests{exhausted}: {green}{prop.__name__}{clear}")
    return True


def holds(prop, max_tests=360):
    """
    Alias to `check(prop, silent=True)`.
    Returns a boolean indicating whether the given argument property holds
    for a (given) number of maximum tests.

    >>> def prop_commute(x:int, y:int) -> bool:
    ...     return x + y == y + x
    >>> holds(prop_commute)
    True

    >>> def prop_increase(x:int, y:int) -> bool:
    ...     return x + y > x
    >>> holds(prop_increase)
    False
    """
    return check(prop, max_tests=max_tests, silent=True)


def main(max_tests=360, silent=False, verbose=False, exit_on_failure=True):
    """
    Tests all properties present in the current file,
    report results and
    exit with an error in case one of the properties fails.

    This is analogous to `unittest.main()`
    and is generally used at the end of a Python file as:

        if __name__ == '__main__':
            leancheck.main()
    """
    n_failures, n_properties = testmod(max_tests=max_tests, silent=silent, verbose=verbose)
    clear, red, green, blue, yellow = _colour_escapes()
    if not silent:
        if not n_properties:
            print(f"{yellow}Warning{clear}: no properties found")
        if n_failures:
            print(f"\n{red}*** {n_failures} of {n_properties} properties failed{clear}")
        elif verbose:
            print(f"{green}+++ {n_properties} properties passed{clear}")
    if n_failures and exit_on_failure:
        sys.exit(1)


def testmod(max_tests=360, silent=False, verbose=False):
    """
    Tests all properties present in the current file
    and report the results.

    This is analogous to `doctest.testmod()`
    and is generally used at the end of a Python file as:

        if __name__ == '__main__':
            n_failures, n_properties = leancheck.testmod()
            if n_failures:
                sys.exit(1)

    Depending on your use-case
    you may be better off calling `leancheck.main()` instead.
    """
    n_failures = 0
    n_properties = 0
    def lineno(m):
        try:
            return m[1].__code__.co_firstlineno
        except AttributeError:
            return -1
    for name, member in sorted(inspect.getmembers(sys.modules["__main__"]), key=lineno):
        if name.startswith("prop_") and callable(member):
            n_properties += 1
            passed = check(member, max_tests=max_tests, silent=silent, verbose=verbose)
            if not passed:
                n_failures += 1
    return (n_failures, n_properties) # just like doctest.testmod()


class Enumerator:
    """
    This class enumerates test values.

    Enumerations are represented internally as
    [a (potentially infinite) generator of finite lists](https://matela.com.br/thesis-rudy.pdf):
    tiers of values of increasing size.
    This is needed in order for the enumeration to be fair.

    As a user, you can query available enumerations with
    enumerations with "indexing":

    >>> Enumerator[int]
    Enumerator(lambda: (xs for xs in [[0], [1], [2], [3], [4], [5], ...]))

    >>> Enumerator[bool]
    Enumerator(lambda: (xs for xs in [[False, True]]))

    >>> print(Enumerator[list[int]])
    [[], [0], [0, 0], [1], [0, 0, 0], [1, 0], ...]

    >>> print(Enumerator[tuple[bool, int]])
    [(False, 0), (True, 0), (False, 1), (True, 1), (False, 2), (True, 2), ...]

    >>> print(Enumerator[tuple[int,int,int]])
    [(0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0), (0, 0, 2), (0, 1, 1), ...]

    You can use this class to build new enumerations
    which can be registered using the `Enumerator.register()` method.

    This class supports computing sums and products of enumerations:

    >>> print(Enumerator[int] + Enumerator[bool])
    [0, False, True, 1, 2, 3, ...]

    Use `*` to take the product of two enumerations:

    >>> print(Enumerator[int] * Enumerator[bool])
    [(0, False), (0, True), (1, False), (1, True), (2, False), (2, True), ...]
    """

    tiers: typing.Callable[[], typing.Generator]
    """
    Generate tiers of values.

    >>> list(Enumerator[bool].tiers())
    [[False, True]]
    """

    def __init__(self, tiers):
        """
        Raw initialization of an enumerator
        with a (potentially infinite) generator of finite lists.

        >>> Enumerator(lambda: ([x] for x in itertools.count()))
        Enumerator(lambda: (xs for xs in [[0], [1], [2], [3], [4], [5], ...]))

        >>> Enumerator(lambda: (ps for ps in [[False, True]]))
        Enumerator(lambda: (xs for xs in [[False, True]]))
        """

        self.tiers = tiers

    def __iter__(self):
        return _to_list(self.tiers())

    @classmethod
    def from_gen(cls, gen):
        """
        Initializes an enumerator directly from a plain generator.

        >>> Enumerator.from_gen(itertools.count)
        Enumerator(lambda: (xs for xs in [[0], [1], [2], [3], [4], [5], ...]))
        """
        return cls(lambda: _to_tiers(gen()))

    @classmethod
    def from_list(cls, lst):
        """
        Initializes an enumerator from a list of options.
        Earlier values are considered of smaller size than later values.

        >>> Enumerator.from_list([0,2,4,6])
        Enumerator(lambda: (xs for xs in [[0], [2], [4], [6]]))
        """
        return cls(lambda: _to_tiers(x for x in lst))

    @classmethod
    def from_choices(cls, choices):
        """
        Initializes an enumerator from a list of choices.
        All given values are considered to be of the same size.

        >>> Enumerator.from_choices([0,2,4,6])
        Enumerator(lambda: (xs for xs in [[0, 2, 4, 6]]))
        """
        return cls(lambda: (cs for cs in [choices]))

    @classmethod
    def lists(cls, enumerator):
        """
        Constructs an enumerator of lists of values from another enumeration.

        >>> print(Enumerator.lists(Enumerator[int]))
        [[], [0], [0, 0], [1], [0, 0, 0], [1, 0], ...]

        You are perhaps better off using:

        >>> print(Enumerator[list[int]])
        [[], [0], [0, 0], [1], [0, 0, 0], [1, 0], ...]
        """
        return cls(lambda: _llist(enumerator.tiers))

    def __add__(self, other):
        """
        Use `+` to compute the sum of two enumerations:

        >>> print(Enumerator[int] + Enumerator[bool])
        [0, False, True, 1, 2, 3, ...]

        >>> Enumerator[int] + Enumerator[bool]
        Enumerator(lambda: (xs for xs in [[0, False, True], [1], [2], [3], [4], [5], ...]))
        """
        return Enumerator(lambda: _zippend(self.tiers(), other.tiers()))

    def __mul__(self, other):
        """
        Use `*` to take the product of two enumerations:

        >>> print(Enumerator[int] * Enumerator[bool])
        [(0, False), (0, True), (1, False), (1, True), (2, False), (2, True), ...]

        >>> Enumerator[int] * Enumerator[bool]
        Enumerator(lambda: (xs for xs in [[(0, False), (0, True)], [(1, False), (1, True)], [(2, False), (2, True)], [(3, False), (3, True)], [(4, False), (4, True)], [(5, False), (5, True)], ...]))
        """
        return Enumerator(lambda: _pproduct(self.tiers(), other.tiers()))

    def __repr__(self):
        # TODO: remove magic numbers: make them configurable?
        xss = [str(xs) for xs in itertools.islice(self.tiers(), 7)]
        if (len(xss) > 6):
            xss[6] = "..."
        return "Enumerator(lambda: (xs for xs in [" + ', '.join(xss) + "]))"

    def __str__(self):
        # TODO: remove magic numbers: make them configurable?
        xs = [str(x) for x in itertools.islice(self, 7)]
        if (len(xs) > 6):
            xs[6] = "..."
        return "[" + ', '.join(xs) + "]"

    def map(self, f):
        """
        Applies a function to all values in the enumeration.

        >>> Enumerator[int].map(lambda x: x*2)
        Enumerator(lambda: (xs for xs in [[0], [2], [4], [6], [8], [10], ...]))
        """
        return Enumerator(lambda: _mmap(f, self.tiers()))

    @classmethod
    def product(cls, *enumerators):
        """
        Computes the product of several enumerators
        returning an enumeration of tuples.

        >>> print(Enumerator.product(Enumerator[int], Enumerator[bool], Enumerator[list[int]]))
        [(0, False, []), (0, True, []), (0, False, [0]), (0, True, [0]), (1, False, []), (1, True, []), ...]

        If you have just two enumerations, you can simply use `*`:

        >>> print(Enumerator[int] * Enumerator[bool])
        [(0, False), (0, True), (1, False), (1, True), (2, False), (2, True), ...]
        """
        if len(enumerators) == 0:
            return Enumerator(lambda: (xs for xs in [[()]]))
        else:
            e, *es = enumerators
            return (e * cls.product(*es)).map(lambda t: (t[0],) + t[1])

    _enumerators = None

    # A hack!  Functions that use _enumerators, should first call this.
    @classmethod
    def _initialize(cls):
        "Initializes the internal _enumerators dictionary"
        if cls._enumerators is None:
            cls._enumerators = {
                int: cls.from_gen(itertools.count), # TODO: include negatives
                bool: cls.from_choices([False,True]),
                list: lambda e: cls.lists(e),
                tuple: lambda *e: cls.product(*e),
            }

    @classmethod
    def register(cls, c, enumerator):
        """
        Registers an enumerator for the given type.

        >>> Enumerator.register(bool, Enumerator(lambda: (xs for xs in [[False, True]])))
        """
        cls._initialize()
        cls._enumerators[c] = enumerator

    # @classmethod # automatic
    def __class_getitem__(cls, c):
        """
        Finds an enumerator for the given type.

        >>> Enumerator[int]
        Enumerator(lambda: (xs for xs in [[0], [1], [2], [3], [4], [5], ...]))

        >>> Enumerator[bool]
        Enumerator(lambda: (xs for xs in [[False, True]]))

        >>> print(Enumerator[list[int]])
        [[], [0], [0, 0], [1], [0, 0, 0], [1, 0], ...]

        >>> print(Enumerator[tuple[bool, int]])
        [(False, 0), (True, 0), (False, 1), (True, 1), (False, 2), (True, 2), ...]

        >>> print(Enumerator[tuple[int,int,int]])
        [(0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0), (0, 0, 2), (0, 1, 1), ...]

        >>> print(Enumerator[type])
        Traceback (most recent call last):
        ...
        TypeError: could not find Enumerator for <class 'type'>
        """
        cls._initialize()
        try:
            if type(c) is types.GenericAlias:
                origin = typing.get_origin(c)
                args = typing.get_args(c)
                enums = [Enumerator[a] for a in args]
                return cls._enumerators[origin](*enums)
            else:
                return cls._enumerators[c]
        except KeyError as err:
            raise TypeError(f"could not find Enumerator for {c}") from err


# Declaration of some internal functions.
# These could eventually reside in a separate file,
# but for simplicity I am keeping them in a single one.


def _to_tiers(xs):
    for x in xs:
        yield [x]


def _to_list(xss):
    for xs in xss:
        yield from xs


def _intercalate(generator1, generator2):
    """
    This function intercalates the two given iterables.

    >>> list(_intercalate([1,2,3], [-1, -2, -3]))
    [1, -1, 2, -2, 3, -3]

    If the arguments are generators, they will be consumed.

    >>> list(_intercalate((x for x in [1,2,3]), (y for y in [4,5,6])))
    [1, 4, 2, 5, 3, 6]
    """
    g1 = (x for x in generator1) # makes this work on lists
    g2 = (y for y in generator2) # makes this work on lists
    while True:
        try:
            yield next(g1)
        except StopIteration:
            yield from g2
            break
        try:
            yield next(g2)
        except StopIteration:
            yield from g1
            break


def _zippend(*iiterables):
    return map(list,itertools.starmap(itertools.chain,itertools.zip_longest(*iiterables, fillvalue=[])))


def _pproduct(xss, yss, with_f=None):
    if with_f is None:
        with_f = lambda x, y: (x,y)
    xss_ = []
    yss_ = []
    l = 0
    while True:
        xss_.append(list(next(xss, [])))
        yss_.append(list(next(yss, [])))
        l += 1
        zs = []
        for i in range(0,l):
            zs += [with_f(x,y) for x in xss_[i] for y in yss_[l-i-1]]
        if zs == []:
            # This is "sound-but-incomplete".
            # TODO: in the final version, use None as a default value
            # in the appends above
            # and break only in the case where we
            # end up with empty zs because of None values
            # there's an opportunity for memory optimization here
            # such as in the example of product between integers and booleans
            break
        yield zs


def _delay(xss):
    yield []
    yield from xss


def _mmap(f,xss):
    for xs in xss:
        yield [f(x) for x in xs]


def _llist(mkTiers):
    yield [[]]
    yield from _pproduct(mkTiers(), _llist(mkTiers), with_f=lambda x, xs: xs + [x])


def _colour_escapes():
    """
    Returns colour escape sequences for clear, red, green, blue and yellow

    >>> clear, red, green, blue, yellow = _colour_escapes()
    >>> print(f"{red}This is red{clear} and {blue}this is blue{clear}.")
    This is red and this is blue.
    """
    plats = ['linux'] # TODO: add other supported platforms
    supported = sys.stdout.isatty() and sys.platform in plats
    if supported:
        return '\x1b[m', '\x1b[1;31m', '\x1b[32m', '\x1b[34m', '\x1b[33m'
    else:
        return '', '', '', '', ''


# Runs tests if this is not being imported as a module.
if __name__ == "__main__":
    import doctest
    import sys
    (failures, _) = doctest.testmod()
    if failures:
        sys.exit(1)
