# Copyright 2022 David Robillard <d@drobilla.net>
# SPDX-License-Identifier: ISC

import unittest
import subprocess
import sys
import glob
import os

import html5lib

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "src"
    )
)

from sphinxygen import sphinxygen


class TestSphinxygen(unittest.TestCase):
    def _run(self, command):
        try:
            proc = subprocess.run(
                command, capture_output=True, check=True, encoding="utf-8"
            )
        except subprocess.CalledProcessError as error:
            sys.stderr.write(f"sphinxygen test error: {error}\n")
            sys.stderr.write(error.stderr)
            raise

    def test_generate(self):
        self._run(["mkdir", "-p", "build"])
        self._run(["cp", "test/c/conf.py", "build"])
        self._run(["cp", "test/c/index.rst", "build"])
        self._run(["doxygen", "test/c/Doxyfile"])

        sphinxygen.run("build/xml/index.xml", "build/api", "c", True)

        builder = "html"
        build_dir = "build"
        out_dir = os.path.join(build_dir, builder)

        self._run(["sphinx-build", "-EW", "-b", builder, build_dir, out_dir])

        html_files = glob.glob(os.path.join(out_dir, "*.html")) + glob.glob(
            os.path.join(out_dir, "api", "*.html")
        )

        for html_path in html_files:
            html5parser = html5lib.HTMLParser(strict=True)
            with open(html_path, "r") as index:
                try:
                    html5parser.parse(index.read())
                    print("note: validated {}".format(html_path))
                except html5lib.html5parser.ParseError as e:
                    print("error: {}: {}".format(html_path, e))
