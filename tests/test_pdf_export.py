import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["DB_ENGINE"] = "sqlite"

from app import build_simple_pdf  # noqa: E402

PAGE_WIDTH, PAGE_HEIGHT = 612, 792


def text_positions(pdf_bytes):
    """Replay the Td/Tj operators and return (x, y, text) for each line."""
    stream = pdf_bytes.split(b"stream\n", 1)[1].split(b"\nendstream", 1)[0].decode("latin-1")
    x = y = 0.0
    positions = []
    for line in stream.splitlines():
        move = re.fullmatch(r"(-?[\d.]+) (-?[\d.]+) Td", line)
        if move:
            # Td is relative to the start of the previous line.
            x += float(move.group(1))
            y += float(move.group(2))
            continue
        shown = re.fullmatch(r"\((.*)\) Tj", line)
        if shown:
            positions.append((x, y, shown.group(1)))
    return positions


def test_every_row_is_drawn_on_the_page():
    rows = [[f"T{i}", f"Train {i}"] for i in range(5)]
    positions = text_positions(build_simple_pdf("Train Report", ["Number", "Name"], rows).getvalue())

    assert [text for _x, _y, text in positions] == [
        "Train Report",
        "Number | Name",
        *[f"T{i} | Train {i}" for i in range(5)],
    ]
    for x, y, text in positions:
        assert 0 <= x <= PAGE_WIDTH and 0 <= y <= PAGE_HEIGHT, text


def test_lines_run_top_to_bottom():
    positions = text_positions(build_simple_pdf("Report", ["A"], [["1"], ["2"], ["3"]]).getvalue())
    ys = [y for _x, y, _text in positions]
    assert ys == sorted(ys, reverse=True)


def test_overflow_rows_are_summarised_on_the_page():
    rows = [[str(i)] for i in range(100)]
    positions = text_positions(build_simple_pdf("Report", ["N"], rows).getvalue())

    last_x, last_y, last_text = positions[-1]
    assert re.fullmatch(r"\.\.\. \d+ more rows not shown", last_text)
    drawn_rows = len(positions) - 2 - 1  # minus title, header and the note
    assert int(last_text.split()[1]) == 100 - drawn_rows
    for x, y, text in positions:
        assert 0 <= x <= PAGE_WIDTH and 50 <= y <= PAGE_HEIGHT, text
