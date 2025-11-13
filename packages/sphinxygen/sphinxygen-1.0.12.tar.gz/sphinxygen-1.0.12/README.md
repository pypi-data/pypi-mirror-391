Sphinxygen
==========

Sphinxygen is a Python module/script that generates [Sphinx][] markup to
describe a C API, from an XML description extracted by [Doxygen][].

Installation
------------

Sphinxygen can be installed from [PyPI][] with [pip][]:

    pip3 install sphinxygen

Alternatively, it can be installed locally from this source tree:

    pip3 install .

Usage
-----

Sphinxygen is mainly intended for use on the command line or in scripts.  After
installation, `sphinxygen` should be available to be run on an `index.xml`
file, for example:

    sphinxygen xml/index.xml sphinx_input

See the output of `sphinxygen --help` for details.

A `sphinxygen` module is also installed for programmatic use within Python,
typically via `sphinxygen.run()` which is a straightforward reflection of the
command-line options.  The command-line interface is also available as
`sphinxygen.main()`.

A minimal [meson][] build definition is included for using Sphinxygen as a
subproject.  It is not intended for installation, or any use other than
wrapping `sphinxygen.py` to ensure that it's available from meson.

 -- David Robillard <d@drobilla.net>

[Sphinx]: https://www.sphinx-doc.org/
[Doxygen]: https://doxygen.nl/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
[meson]: https://mesonbuild.com/
