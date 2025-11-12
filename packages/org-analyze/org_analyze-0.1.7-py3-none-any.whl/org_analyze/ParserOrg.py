"""
Very small Org-mode table/header parser.

Improvements over the original:
- Class is now `ParserOrg` and supports passing either a filename or a file-like object.
- Context manager support (use `with ParserOrg(...) as p:`).
- Safer parsing of headers, tables and variables.
- Returns parsed items from `parse()` and stores vars on `vars`.
"""

import logging
import re
from typing import IO, List, Sequence, Tuple, Union, Optional
import os


class OrgHeader:
    """Represents an org-mode header (a line starting with one or more '*')."""
    header_re = re.compile(r"^(\*+)\s+(?:TODO\s+|DONE\s+)?(.*)")

    def __init__(self, line: str) -> None:
        m = self.header_re.match(line)
        if m:
            self.level = len(m.group(1))
            self.name = m.group(2) or ""
        else: # fallback: treat whole line as name with level 0
            self.level = 0
            self.name = line.strip()

    def __repr__(self) -> str:
        return f"<H{self.level} {self.name!r}>"

class OrgClock:
    """Represents a CLOCK entry."""
    clock_re = re.compile(r"CLOCK: \[(\d{4}-\d{2}-\d{2}) [^\]]+\]--\[.*?\] =>\s+([\d:]+)")
    clk_re = re.compile(
        r"^\#\+CLK:\s*\[(\d{4}-\d{2}-\d{2})\s+[A-Za-z]{3}\s+(\d{1,2}:\d{2})\]"
    )
    def __init__(self, line: str) -> None:
        m = self.clock_re.match(line)
        if not m:
            m = self.clk_re.match(line)
            if not m:
                raise ValueError(f"Invalid CLOCK line: {line}")
        self.start = m.groups(1)[0]  # YYYY-MM-DD
        self.duration = m.groups(1)[1]  # HH:MM

    def __repr__(self) -> str:
        return f"<Clock {self.start} {self.duration}>"

class OrgTable:
    """Simple container for table rows. Rows are lists of cell strings."""
    def __init__(self) -> None:
        self.rows: List[List[str]] = []

    def add_row(self, row: Sequence[str]) -> None:
        self.rows.append(list(row))

    def getDictRows(self) -> List[dict]:
        """Return table rows as list of dicts, using the first row as keys."""
        if not self.rows:
            return []
        keys = self.rows[0]
        dict_rows = []
        for row in self.rows[1:]:
            row_dict = {keys[i]: row[i] if i < len(row) else "" for i in range(len(keys))}
            dict_rows.append(row_dict)
        return dict_rows
    
    def __repr__(self) -> str:
        return f"<Table rows={len(self.rows)}>"

class OrgSourceBlock:
    """Represents a source code block."""
    def __init__(self, lines: List[str]) -> None:
        self.lines = lines[1:-1]  # exclude the begin/end lines
        self.language = lines[0].strip(" ").split()[1] if lines else "unknown"

    def __repr__(self) -> str:
        return f"<SourceBlock lang={self.language} lines={len(self.lines)}>"

class OrgText:
    """Represents a plain text paragraph."""
    def __init__(self, line: str) -> None:
        self.line = line

    def __repr__(self) -> str:
        return f"<Text '{self.line}'>"

class OrgMath:
    """Represents a math block."""
    def __init__(self, lines: List[str]) -> None:
        self.lines = lines[1:-1]  # exclude the begin/end lines

    def __repr__(self) -> str:
        return f"<Math lines={len(self.lines)}>"

class OrgProperties:
    """Represents a PROPERTIES block."""
    property_re = re.compile(r"^:([a-zA-Z0-9_\-]+):\s*(.*)")
    def __init__(self, lines: List[str]) -> None:
        self.values = {}
        for line in lines[:-1]:
            m = self.property_re.match(line)
            if m:
                key = m.group(1).strip().lower()
                value = m.group(2).strip()
                self.values[key] = value
                # setattr(self, key, value)

    def __repr__(self) -> str:
        return f"<Properties lines={len(self.lines)}>"

class ParserOrg:
    """Parser for a tiny subset of Emacs org-mode used by this project.

    Usage:
      p = ParserOrg(path_or_file)
      p.parse()
      items = p.items

    or as a context manager:
      with ParserOrg(path) as p:
          items = p.parse()

    The parser focuses on headers (lines starting with '*'), tables (lines
    beginning with '|') and file-local variables (lines starting with '#+').
    """

    org_link_re = re.compile(r"\[\[([^\[\]]+)\](?:\[([^\[\]]+)\])?\]")

    def __init__(self, source: Union[str, os.PathLike, IO[str]], link_converter=None) -> None:
        if isinstance(source, (str, os.PathLike)):
            # open file ourselves
            self._f = open(str(source), "rt", encoding="utf-8", errors="replace")
            self._own_file = True
        else:
            # assume file-like object
            self._f = source
            self._own_file = False

        self.items: List[object] = []
        self.vars: dict = {}
        self.link_converter = link_converter

    def __enter__(self) -> "ParserOrg":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        if getattr(self, "_own_file", False):
            try:
                self._f.close()
            except Exception:
                logging.exception("Failed to close org file")

    def parse_links(self, line: str) -> str:
        """Parse org-mode links in the given line using the link_converter."""
        if self.link_converter is None:
            return line

        def repl(m: re.Match) -> str:
            link = m.group(1)
            name = m.group(2) if m.group(2) is not None else link
            return self.link_converter(link, name)

        return self.org_link_re.sub(repl, line)

    def parse_table(self, line: str) -> OrgTable:
        """Parse consecutive table lines starting from `line` (which should
        start with '|'). Returns an OrgTable object. The file pointer will be
        left at the first non-table line.
        """
        tbl = OrgTable()
        # line may have trailing newline
        while line is not None and line.lstrip().startswith("|"):
            text = line.strip()
            if not text.startswith("|-") and len(text) > 1:
                # remove leading and trailing pipe if present
                if text.endswith("|"):
                    core = text[1:-1]
                else:
                    core = text[1:]
                cells = [c.strip() for c in core.split("|")]
                tbl.add_row(cells)
            # read next line
            line = self._f.readline()

            if line == "":
                # EOF - break and return
                break

        # If we stopped on a non-empty non-table line, move the file cursor
        # back so the outer loop can process it. We can approximate by using
        # tell/seek only for real files; for other file-likes we keep the
        # leftover line in a small attribute.
        if line and not line.lstrip().startswith("|"):
            # store leftover line for next parse step
            self._last_line = line
        else:
            self._last_line = None

        return tbl

    def _is_property_line(self, line: str) -> bool:
        """Check if the line is a property line (starts with ':PROPERTY:')."""
        if not line.startswith(":"):
            return False
        match = re.search(r":[A-Z]+:", line)
        return match and match.start() == 0

    def parse(self) -> List[object]:
        """Parse the opened file and return a list of top-level items.

        Items are instances of OrgHeader (which has .items) or OrgTable.
        File-local variables are stored in `self.vars`.
        """
        # Reset state
        self.items = []
        self.vars = {}
        self._last_line = None

        while True:
            if self._last_line is not None:
                raw = self._last_line
                self._last_line = None
            else:
                raw = self._f.readline()

            if raw == "":
                break

            # keep the original for pattern checks
            line = raw.rstrip("\n")
            if line.strip() == "":
                # empty line
                continue

            if line.lstrip().startswith("|"):
                # table
                table = self.parse_table(line)
                self.items.append(table)

            elif line.startswith("*"):  # header
                self.items.append(OrgHeader(line))

            elif line.startswith("CLOCK:") or line.startswith("#+CLK:"):
                self.items.append(OrgClock(line))

            elif line.lower().startswith("#+begin_src"):
                lines = [line]
                while line and not line.lower().startswith("#+end_src"):
                    line = self._f.readline()
                    if len(line) == 0:
                        break
                    lines.append(line.rstrip("\n"))
                self.items.append(OrgSourceBlock(lines))
            elif line.strip() == "\[":
                lines = [line]
                while line and not line.strip()== "\]":
                    line = self._f.readline()
                    if len(line) == 0:
                        break
                    lines.append(line.rstrip("\n"))
                self.items.append(OrgMath(lines))
            elif line.strip() == ":PROPERTIES:":
                properties = []
                while line and not line.strip() == ":END:":
                    line = self._f.readline()
                    properties.append(line.strip())
                self.items.append(OrgProperties(properties))
            elif self._is_property_line(line):
                pass # skip property lines
            elif line.startswith("#+"):
                # file variable - split at first ':' for safety
                tail = line[2:]
                if ":" in tail:
                    name, value = tail.split(":", 1)
                    self.vars[name.strip().lower()] = value.strip()
                else:
                    logging.debug("Unrecognized variable line: %r", line)

            else:
                self.items.append(OrgText(self.parse_links(line)))

        self.close()
        return self.items
