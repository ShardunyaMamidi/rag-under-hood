"""Tests for the RST cleaner (Task 1).

One test per cleaning rule documented in `notebooks/chunking_embeddings.ipynb`.
"""
from raghood.clean import clean_rst


def test_headings_become_hashes():
    out = clean_rst("Quickstart\n==========\n\nbody\n\nA Section\n---------\n\nmore\n")
    assert "# Quickstart" in out
    assert "## A Section" in out
    assert "=====" not in out and "-----" not in out


def test_code_block_becomes_fence_with_contents_intact():
    out = clean_rst(".. code-block:: python\n\n    from flask import Flask\n\n    app = Flask(__name__)\n")
    assert "```python" in out
    assert "from flask import Flask" in out
    assert "app = Flask(__name__)" in out
    assert out.count("```") == 2


def test_literal_block_becomes_fence():
    out = clean_rst("Run this::\n\n    $ flask run\n")
    assert "Run this:" in out
    assert "```" in out and "$ flask run" in out
    assert "::" not in out


def test_roles_collapse_to_readable_name():
    assert "Flask" in clean_rst("A :class:`~flask.Flask` instance.\n")
    assert "flask.Flask" not in clean_rst("A :class:`~flask.Flask` instance.\n")
    assert "Blueprint" in clean_rst("A :class:`Blueprint` object.\n")
    assert "the docs" in clean_rst("See :doc:`the docs <patterns/index>`.\n")


def test_inline_literals_and_links():
    assert "`flask run`" in clean_rst("Use ``flask run`` to start.\n")
    assert clean_rst("a `Click`_ interface\n").strip() == "a Click interface"
    assert clean_rst("see `the docs <https://example.com>`_ here\n").strip() == "see the docs here"


def test_admonitions_keep_their_body():
    out = clean_rst(".. warning::\n\n    Do not do this in production.\n")
    assert out.startswith("Warning")
    assert "Do not do this in production." in out


def test_version_directives_become_prose():
    assert "Added in version 0.7." in clean_rst(".. versionadded:: 0.7\n")
    assert "Changed in version 2.0." in clean_rst(".. versionchanged:: 2.0\n")


def test_reference_directive_keeps_name_and_body():
    out = clean_rst(".. py:data:: DEBUG\n\n    Whether debug mode is enabled.\n")
    assert "DEBUG" in out
    assert "Whether debug mode is enabled." in out


def test_autodoc_directives_are_dropped():
    """Docstrings live in the source code, not the .rst, so these carry no content."""
    out = clean_rst("# API\n\n.. autoclass:: Flask\n    :members:\n\ntail\n")
    assert "autoclass" not in out
    assert "tail" in out


def test_layout_directives_and_link_targets_are_dropped():
    out = clean_rst(".. currentmodule:: flask\n\n.. toctree::\n   :maxdepth: 2\n\n   quickstart\n\nreal text\n")
    assert "currentmodule" not in out and "toctree" not in out and "maxdepth" not in out
    assert "real text" in out
    assert clean_rst(".. _my-label:\n\ntext\n").strip() == "text"


def test_transitions_are_dropped():
    assert clean_rst("before\n\n----\n\nafter\n").strip() == "before\n\nafter"


def test_markup_inside_code_fences_is_left_alone():
    """``x`` inside code is real Python, not RST inline literal syntax."""
    out = clean_rst(".. code-block:: python\n\n    s = ``not rst``\n")
    assert "``not rst``" in out


def test_nested_directives_inside_bodies_are_cleaned():
    out = clean_rst(".. note::\n\n    See :class:`Flask` and ``app.run()``.\n")
    assert ":class:" not in out
    assert "Flask" in out and "`app.run()`" in out


def test_output_ends_with_single_newline_and_no_triple_blanks():
    out = clean_rst("a\n\n\n\n\nb\n")
    assert out.endswith("\n") and not out.endswith("\n\n")
    assert "\n\n\n" not in out
