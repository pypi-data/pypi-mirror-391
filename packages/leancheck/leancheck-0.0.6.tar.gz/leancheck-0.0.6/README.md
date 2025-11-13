LeanCheck for Python
====================

[![LeanCheck's Build Status][build-status]][build-log]
[![LeanCheck on PyPI][pypi-version]][leancheck-on-pypi]

This is a port of [Haskell's LeanCheck] to [Python].

LeanCheck is an enumerative property-based testing library.
It can be used to complement your unit tests.

This is a work in progress:
__this library is currently experimental.__.

The usual drill in unit testing involves making assertions
about specific input-output cases of functions, such as:

```py
assertEqual(sorted([4,2,1,3]), [1,2,3,4])
```

There are no arguments to the unit test.

In property-based testing (with LeanCheck)
one writes more general properties that should be true
for any assignment of arguments.

For example:
given __any__ list, sorting it twice is the same as sorting it once.
We can encode this as a function returning a boolean value:

```py
def prop_sorted_twice(xs: list[int]) -> bool:
    return sorted(sorted(xs)) == sorted(xs)
```

For whatever list we provide this function,
it should return `True`.
Now one can use LeanCheck to verify this automatically:

```py
>>> from leancheck import *

>>> check(prop_sorted_twice)
+++ OK, passed 360 tests: prop_sorted_twice
```

When the property or function-under-test is incorrect
LeanCheck may find and report a counterexample like so:

```py
*** Failed! Falsifiable after 6 tests:
    prop_sorted_wrong([1, 0])
```

This would indicate that the list `[1, 0]` is an ill input.

Besides using `check()` to test individual properties,
one can use `leancheck.main()` to test all properties
defined in the current file.


Example, testing a sorting function
-----------------------------------

Consider the following (not-quite) `qsort` function:

```py
def qsort(lst):
    if lst == []:
        return []
    x, *etc = lst  # split into head and tail
    lesser  = [y for y in etc if y < x]
    greater = [y for y in etc if y > x]
    return qsort(lesser) + [x] + qsort(greater)
```

It returns the sorted version of the given argument list:

```py
>>> qsort([4,2,1,3])
[1,2,3,4]
```

We can define the following three properties about it:

1. Sorting a list returns the elements in order;
2. Sorting preserves membership in the list;
3. Sorting does not change the list length.

We can define and test these properties with LeanCheck as follows:

```py
import leancheck

def prop_sort_ordered(xs: list[int]) -> bool:
	def ordered(xs):
		for x, y in zip(xs, xs[1:]):
			if x > y:
				return False
		return True
	return ordered(qsort(xs))

def prop_sort_elem(x: int, xs: list[int]) -> bool:
	return (x in qsort(xs)) == (x in xs)

def prop_sort_len(xs: list[int]) -> bool:
	return len(qsort(xs)) == len(xs)

if __name__ == '__main__':
	leancheck.main()
```

We import LeanCheck, define the properties and call `leancheck.main()`
which will test all properties defined in the file:
anything named `prop_*`.
The properties may be placed together with the function(s) under test
or in a separate test file depending on your needs.

Note the type annotations, these are necessary for LeanCheck to know
how to test each property.

Running the above file/program/script yields the following report:

```py
+++ OK, passed 360 tests: prop_sort_ordered

+++ OK, passed 360 tests: prop_sort_elem

*** Failed! Falsifiable after 3 tests:
    prop_sort_len([0, 0])
```

We actually have a failure in the third property
and we can investigate:

```py
>>> leancheck.check(prop_sort_len)
*** Failed! Falsifiable after 3 tests:
    prop_sort_len([0, 0])

>>> prop_sort_len([0, 0])
False

>>> len(qsort([0, 0]))
1

>>> qsort([0, 0])
[0]
```

Our function discards repeated elements!
Fixing the bug in `qsort` is left as an exercise to the reader.

An extended version of this example can be found
under the `examples/` folder in the source repository.


Further reading
---------------

[LeanCheck for Haskell] is subject to a chapter in a [PhD Thesis (2017)].

As of 2024, [Python] already has a relatively popular property-based testing
library called [Hypothesis].  While writing this port of LeanCheck, I
intentionally did not take a closer look at Hypothesis.  I want to see if I
would take an entirely different approach here by not getting biased of how
things were implemented there.  ... and indeed I did.  Python's LeanCheck stays
as close as possible to its Haskell counterpart, here are key differences
between LeanCheck and Hypothesis:

|                                | LeanCheck        | Hypothesis            |
| ------------------------------ | ---------------- | --------------------- |
| test generation                | enumerative      | random                |
| generator selection            | type annotation  | strategy decorators   |
| testing individual properties  | check() function | properties themselves |
| testing all properties in file | leancheck.main() | not supported?        |
| development status             | experimental     | production/stable     |

LeanCheck is enumerative.  The test generators are selected based on type
annotations in the properties.  One can test an individual property with the
`check()` function.  To test all properties in a single test file one can use
`leancheck.main()`.  Any function named `prop_*` with a return type of `bool`
is considered a property by convention.  LeanCheck is simpler to use IMHO.


[Haskell's LeanCheck]:   https://hackage.haskell.org/package/leancheck
[LeanCheck for Haskell]: https://hackage.haskell.org/package/leancheck
[Python]: https://www.python.org/
[Hypothesis]: https://pypi.org/project/hypothesis/
[TODO]: TODO.md
[PhD Thesis (2017)]: https://matela.com.br/thesis-rudy.pdf

[build-log]:    https://github.com/rudymatela/python-leancheck/actions/workflows/test.yml
[build-status]: https://github.com/rudymatela/python-leancheck/actions/workflows/test.yml/badge.svg
[pypi-version]: https://img.shields.io/pypi/v/leancheck.svg
[leancheck-on-pypi]: https://pypi.org/project/leancheck
