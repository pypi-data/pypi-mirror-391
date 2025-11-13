Contributing to Sphinxygen
==========================

Sphinxygen was written to address the needs of specific projects as quickly and
pragmatically as possible, not to be comprehensive or support arbitrary code.
Accordingly, feature requests related to "missing" support aren't welcome.

Feel free, however, to use Sphinxygen for your project and adapt it to your
needs.  Patches for general improvements would be appreciated, and I will do my
best to merge them and make new releases when appropriate.

Some guidelines about the structure and requirements of the code follow.

Testing
-------

A simple test suite is included that runs Doxygen, Sphinxygen, then Sphinx on a
test header, and ensures that valid HTML documentation is successfully
produced.  This can be run with the ``unittest`` module:

    python3 -m unittest discover

This test doubles as a quick feedback loop for working on Sphinxygen itself.
After running the suite, the output at ``build/html/index.html`` will be
preserved.  The test API deliberately includes a broad range of language
constructs to ensure that various situations are covered well.

If you are adding support for new features, please ensure that they are covered
by the test suite (for example, by adding a definition to
`test/c/include/testlib.h`).  A coverage report can be generated with the
``coverage`` module, for example:

    python3 -m coverage run --source src/sphinxygen,test -m unittest discover
    python3 -m coverage html
    firefox htmlcov/index.html

Style
-----

The code is formatted with `black -l 79` and is clean with both `flake8` and
`pylint`.  Please try not to add any suppressions for these tools if at all
possible.
