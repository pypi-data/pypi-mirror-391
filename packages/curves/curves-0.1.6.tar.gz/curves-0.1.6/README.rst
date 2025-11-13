
.. image:: logo.png


Python Project *curves*
-----------------------


.. image:: https://github.com/sonntagsgesicht/curves/actions/workflows/python-package.yml/badge.svg
    :target: https://github.com/sonntagsgesicht/curves/actions/workflows/python-package.yml
    :alt: GitHubWorkflow

.. image:: https://img.shields.io/readthedocs/curves
   :target: http://curves.readthedocs.io
   :alt: Read the Docs

.. image:: https://img.shields.io/github/license/sonntagsgesicht/curves
   :target: https://github.com/sonntagsgesicht/curves/raw/master/LICENSE
   :alt: GitHub

.. image:: https://img.shields.io/github/release/sonntagsgesicht/curves?label=github
   :target: https://github.com/sonntagsgesicht/curves/releases
   :alt: GitHub release

.. image:: https://img.shields.io/pypi/v/curves
   :target: https://pypi.org/project/curves/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/curves
   :target: https://pypi.org/project/curves/
   :alt: PyPI - Python Version

.. image:: https://pepy.tech/badge/curves
   :target: https://pypi.org/project/curves/
   :alt: PyPI Downloads


Introduction
------------

To import the project simply type

.. code-block:: python

    >>> import curves

after installation.

The **Curve** class turns a function into an algebraic object
which can handle operations like +, -, /, * as well es @.

.. code-block:: python

    >>> from curves import Curve

    >>> eye = Curve()  # identity function
    >>> eye(123.456)
    123.456

    >>> zero = Curve(0.0)
    >>> zero(123.456)
    0.0

    >>> one = Curve(1.0)
    >>> one(123.456)
    1.0

    >>> X = Curve('X')
    >>> X
    X

    >>> p = 2 * X **2 + 3 * X + 1
    >>> p
    2 * X **2 + 3 * X + 1

    >>> p(123.456)
    30854.135872

    >>> q = p(X - 1)
    >>> q
    (2 * X ** 2 + 3 * X + 1)(X - 1)

    >>> q1 = p @ (X - 1)
    >>> q1
    (2 * X ** 2 + 3 * X + 1)(X - 1)

    >>> q2 = 2 * (X - 1) ** 2 + 3 * (X - 1) + 1
    >>> q2
    2 * (X - 1) ** 2 + 3 * (X - 1) + 1

    >>> q(123.456)
    30359.311872

    >>> q1(123.456)
    30359.311872

    >>> q2(123.456)
    30359.311872


Documentation
-------------

More documentation available at
`https://curves.readthedocs.io <https://curves.readthedocs.io>`_


Install
-------

The latest stable version can always be installed or updated via pip:

.. code-block:: bash

    $ pip install curves


License
-------

Code and documentation are available according to the license
(see LICENSE file in repository).
