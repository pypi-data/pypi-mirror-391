import re
from pathlib import Path

import pytest

from codesentinel.cli import (
    set_header_for_file,
    set_footer_for_file,
)
from codesentinel.cli.doc_utils import _normalize_markdown_whitespace


def test_normalize_markdown_whitespace_collapses_excess_blanks():
    md = """
# Title



Some paragraph with trailing spaces.   


- list item 1



Another paragraph

"""

    normalized = _normalize_markdown_whitespace(md)
    # No runs of more than 1 blank line
    assert "\n\n\n" not in normalized
    # Trailing spaces removed
    assert not any(line.endswith(" ") for line in normalized.splitlines())
    # Ends with single newline
    assert normalized.endswith("\n")


def test_set_header_and_footer_roundtrip(tmp_path: Path):
    # Create a sample doc with an old header/footer and content
    doc = tmp_path / "README.md"
    doc.write_text("""# Old Title

Old subtitle

Content section

---

Old Footer
""")

    # Apply header (function will use template based on filename)
    ok, msg = set_header_for_file(doc)
    assert ok, msg

    # After header set, apply footer
    ok2, msg2 = set_footer_for_file(doc, template_name="standard")
    assert ok2, msg2

    text = doc.read_text(encoding="utf-8")
    # Header should start with a H1 title
    assert text.startswith("# ")
    # Footer should contain SEAM Protected™
    assert "SEAM Protected™" in text
