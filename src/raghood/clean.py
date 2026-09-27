"""Turn reStructuredText docs into plain Markdown-ish prose for embedding (Task 1).

The Flask docs are `.rst`, full of Sphinx markup (`:class:`~flask.Flask``, `.. code-block::`)
that an embedding model has never seen and that only adds noise to a chunk. `clean_rst`
strips the markup while keeping the content: headings become `#` lines, code blocks become
fenced blocks with their contents untouched, roles collapse to the readable name.

Derived and verified in `notebooks/chunking_embeddings.ipynb`, which shows before/after on
real pages and scans the whole corpus for markup that survived.
"""
import re

DROP_DIRECTIVES = {"currentmodule", "module", "toctree", "image", "rst-class",
                   "highlight", "include", "literalinclude", "only", "contents", "index"}
KEEP_BODY_DIRECTIVES = {"tabs", "group-tab", "tab"}  # marker is layout only; the content matters
AUTODOC_DIRECTIVES = {"autofunction", "autoclass", "autodata", "automodule"}  # docstrings are not in the .rst
REFERENCE_DIRECTIVES = {"py:data", "data", "attribute", "function", "class", "method", "py:function", "py:class"}
CODE_DIRECTIVES = {"code-block", "sourcecode", "code"}
ADMONITIONS = {"note": "Note", "warning": "Warning", "tip": "Tip", "important": "Important",
               "danger": "Danger", "attention": "Attention", "caution": "Caution", "seealso": "See also"}
VERSION_DIRECTIVES = {"versionadded": "Added in version", "versionchanged": "Changed in version",
                      "deprecated": "Deprecated since version"}

DIRECTIVE = re.compile(r"^(\s*)\.\. ([\w:-]+)::\s*(.*)$")
UNDERLINE = re.compile(r"^([=\-~^\"`#*+])\1{2,}\s*$")
ROLE = re.compile(r":([\w:-]+):`([^`]+)`")


def _role(m: re.Match) -> str:
    """:class:`~flask.Flask` -> Flask ; :doc:`text <page>` -> text"""
    role, target = m.group(1), m.group(2)
    if role == "gh":
        return f"issue {target}"
    titled = re.match(r"^(.*?)\s*<([^>]+)>$", target, re.S)
    if titled:
        return titled.group(1) or titled.group(2)
    if target.startswith("~"):
        return target.lstrip("~").split(".")[-1]
    return target.lstrip(".!/")


def _inline(t: str) -> str:
    t = ROLE.sub(_role, t)
    t = re.sub(r"`([^`<]+?)\s*<(https?://[^>]+)>`_{1,2}", r"\1", t)  # `text <url>`_ -> text
    t = re.sub(r"(?<!`)`([^`\n]+)`_{1,2}(?!\w)", r"\1", t)            # `Click`_ -> Click
    t = re.sub(r"``([^`]+)``", r"`\1`", t)                             # ``code`` -> `code`
    t = re.sub(r"\|\w+\|", "", t)                                      # |substitution| refs
    return t


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _block(lines: list[str], start: int, parent_indent: int):
    """Collect the indented body after a directive / '::' marker.

    Returns (body lines dedented, index of first line after the block).
    """
    i = start
    while i < len(lines) and re.match(r"^\s+:[\w-]+:", lines[i]) and _indent(lines[i]) > parent_indent:
        i += 1  # skip option lines such as ":maxdepth: 2" or ":caption: ..."
    body = []
    while i < len(lines) and (not lines[i].strip() or _indent(lines[i]) > parent_indent):
        body.append(lines[i])
        i += 1
    while body and not body[-1].strip():  # trailing blank lines belong to what follows
        body.pop()
        i -= 1
    nonblank = [l for l in body if l.strip()]
    if nonblank:
        cut = min(_indent(l) for l in nonblank)
        body = [l[cut:] if l.strip() else "" for l in body]
    while body and not body[0].strip():
        body.pop(0)
    return body, i


def clean_rst(text: str) -> str:
    """Strip Sphinx/RST markup, keeping headings, code blocks and prose."""
    lines = text.splitlines()
    out: list[str] = []
    level_of: dict[str, int] = {}  # underline char -> heading level, in order of first appearance
    i = 0
    while i < len(lines):
        line = lines[i]

        # headings: a text line followed by an underline at least as long
        if (i + 1 < len(lines) and line.strip() and not line.startswith(" ")
                and UNDERLINE.match(lines[i + 1]) and len(lines[i + 1].strip()) >= len(line.strip())):
            ch = lines[i + 1].strip()[0]
            level = level_of.setdefault(ch, len(level_of) + 1)
            out += ["", "#" * min(level, 4) + " " + line.strip(), ""]
            i += 2
            continue

        # transitions ("----" with no heading text above it)
        if UNDERLINE.match(line):
            i += 1
            continue

        # link targets (".. _x:"), substitutions, comments: drop with their body
        if line.startswith(".. ") and not DIRECTIVE.match(line):
            _, i = _block(lines, i + 1, 0)
            continue

        m = DIRECTIVE.match(line)
        if m:
            name, arg = m.group(2), m.group(3)
            body, i = _block(lines, i + 1, len(m.group(1)))
            if name not in CODE_DIRECTIVES and body:  # bodies may hold nested directives / roles
                body = clean_rst("\n".join(body)).splitlines()
            if name in CODE_DIRECTIVES:
                out += ["", "```" + arg, *body, "```", ""]
            elif name in ADMONITIONS:
                out += ["", f"{ADMONITIONS[name]}: {arg}".rstrip(), *body, ""]
            elif name == "admonition":
                out += ["", f"{arg}:", *body, ""]
            elif name in VERSION_DIRECTIVES:
                out += ["", f"{VERSION_DIRECTIVES[name]} {arg}." + (" " + " ".join(body) if body else ""), ""]
            elif name in REFERENCE_DIRECTIVES:
                out += ["", arg.strip(), *body, ""]
            elif name in KEEP_BODY_DIRECTIVES:
                out += ["", *([arg] if arg else []), *body, ""]
            elif name in AUTODOC_DIRECTIVES or name in DROP_DIRECTIVES:
                pass
            else:  # unknown directive: keep its text, drop the marker
                out += ["", *body, ""]
            continue

        # literal blocks: "text::" followed by an indented block
        if line.rstrip().endswith("::"):
            head = line.rstrip()[:-2].rstrip()
            body, j = _block(lines, i + 1, _indent(line))
            out += ([head + ":"] if head else [])
            if body:
                out += ["", "```", *body, "```", ""]
                i = j
            else:
                i += 1
            continue

        out.append(line)
        i += 1

    # inline markup, but never inside code fences
    parts = re.split(r"(```.*?```)", "\n".join(out), flags=re.S)
    for k in range(0, len(parts), 2):
        parts[k] = _inline(parts[k])
    return re.sub(r"\n{3,}", "\n\n", "".join(parts)).strip() + "\n"
