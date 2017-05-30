[RFC] Recursive Test Discovery

Hello,

This came up as an issue and I believe it deserves some discussion as
there are some different approaches to implement the feature.

Motivation
==========

Currently we can discover test classes that does not inherit directly
from `avocado.Test`. To do so, we rely on the inclusion of a docstring
(`:avocado: enable`) in the mentioned class. Example below.

File `/usr/share/avocado/tests/test_base_class.py`::

    from avocado import Test


    class BaseClass(Test):

        def test_basic(self):
            pass

File `/usr/share/avocado/tests/test_first_child.py`::

    from test_base_class import BaseClass


    class FirstChild(BaseClass):
        """
        :avocado: enable
        """

        def test_first_child(self):
            pass

In the example above, if we ask Avocado to list the tests from
`test_first_child.py`, `FirstChild.test_first_child` will be listed and
the `BaseClass.test_basic` won't::

    $ avocado list test_first_child.py
    INSTRUMENTED test_first_child.py:FirstChild.test_first_child

The request is that, in such cases, we have a way to include the
`BaseClass.test_basic` into the results.


Proposal
========

To include the parent classes into the discovery results, we have three
main aspects to consider:

- How to flag that we want that behaviour?
  The proposal is the creation of a new docstring `recursive`. Example::

    class FirstChild(BaseClass):
        """
        :avocado: recursive
        """
        ...

  Alternative options here are: 1)command line option; 2)make the
  recursive discovery the default behaviour.

- How deep is the recursion?
  The proposal is that the recursion goes all the way up to the class
  inheriting from `avocado.Test`.
  Alternative option here is to discover only the first parent of the
  class flagged with `recursive`. If the parent class also has the same
  docstring, then we go one more level up, and so on.

- Will the recursion respect the parents docstrings?
  The proposal is that we do respect the docstrings in the parents when
  recursively discovering. Example:

  File `/usr/share/avocado/tests/test_base_class.py`::

    from avocado import Test


    class BaseClass(Test):

        def test_basic(self):
            pass

  File `/usr/share/avocado/tests/test_first_child.py`::

    from test_base_class import BaseClass


    class FirstChild(BaseClass):
        """
        :avocado: recursive
        """

        def test_first_child(self):
            pass

  Will result in::

    $ avocado list test_first_child.py
    INSTRUMENTED test_first_child.py:FirstChild.test_first_child
    INSTRUMENTED test_first_child.py:BaseClass.test_basic

  While:

  File `/usr/share/avocado/tests/test_base_class.py`::

    from avocado import Test


    class BaseClass(Test):
        """
        :avocado: disable
        """

        def test_basic(self):
            pass

  File `/usr/share/avocado/tests/test_first_child.py`::

    from test_base_class import BaseClass


    class FirstChild(BaseClass):
        """
        :avocado: recursive
        """

        def test_first_child(self):
            pass

  Will result in::

    $ avocado list test_first_child.py
    INSTRUMENTED test_first_child.py:FirstChild.test_first_child

  The alternative option is that the discovery ignores the parents
  docstrings when discovering recursively, meaning that the
  `:avocado: disable` (or any other current or future available
  docstrings) would have no effect in the recursive discovery.

Expected Results
================

The expected results of this RFC is to have a well defined behaviour for
the recursive discovery feature.

The expected result of the feature itself is to provide users more
flexibility when creating the Avocado tests and consequent Avocado
command lines.

Additional Information
======================

Avocado uses only static analysis to examine the files and this feature
should stick to this principle in its implementation.
