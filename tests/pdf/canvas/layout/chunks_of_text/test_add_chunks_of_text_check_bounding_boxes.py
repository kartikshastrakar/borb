import copy
import typing
import unittest
from datetime import datetime
from pathlib import Path

from borb.io.read.types import Decimal
from borb.pdf.canvas.color.color import HexColor, Color
from borb.pdf.canvas.geometry.rectangle import Rectangle
from borb.pdf.canvas.layout.annotation.square_annotation import SquareAnnotation
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.table.fixed_column_width_table import (
    FixedColumnWidthTable as Table,
)
from borb.pdf.canvas.layout.text.chunk_of_text import ChunkOfText
from borb.pdf.canvas.layout.text.heterogeneous_paragraph import HeterogeneousParagraph
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.document.document import Document
from borb.pdf.page.page import Page
from borb.pdf.pdf import PDF
from tests.test_util import compare_visually_to_ground_truth, check_pdf_using_validator


class TestAddChunksOfTextCheckBoundingBoxes(unittest.TestCase):
    """
    This test creates a PDF with a Paragraph object in it. The Paragraph is aligned TOP, LEFT.
    """

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        # find output dir
        p: Path = Path(__file__).parent
        while "output" not in [x.stem for x in p.iterdir() if x.is_dir()]:
            p = p.parent
        p = p / "output"
        self.output_dir = Path(p, Path(__file__).stem.replace(".py", ""))
        if not self.output_dir.exists():
            self.output_dir.mkdir()

    def test_write_document(self):

        # create document
        pdf = Document()

        # add page
        page = Page()
        pdf.add_page(page)

        # add test information
        layout = SingleColumnLayout(page)
        layout.add(
            Table(number_of_columns=2, number_of_rows=3)
            .add(Paragraph("Date", font="Helvetica-Bold"))
            .add(
                Paragraph(
                    datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
                    font_color=HexColor("00ff00"),
                )
            )
            .add(Paragraph("Test", font="Helvetica-Bold"))
            .add(Paragraph(Path(__file__).stem))
            .add(Paragraph("Description", font="Helvetica-Bold"))
            .add(
                Paragraph(
                    "This test creates a PDF with a Paragraph object in it. The Paragraph is composed of smaller heterogenous ChunkOfText objects."
                )
            )
            .set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))
        )

        txt: str = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        words: typing.List[str] = txt.split(" ")
        colors: typing.List[Color] = [
            HexColor("f1cd2e") if i % 3 == 0 else HexColor("000000")
            for i in range(0, len(words))
        ]

        # build chunks_of_text
        chunks_of_text: typing.List[ChunkOfText] = [
            ChunkOfText(
                x + " ",
                font_color=colors[i],
            )
            for i, x in enumerate(words)
        ]

        bb = Rectangle(Decimal(59), Decimal(500), Decimal(476), Decimal(124))
        hp: HeterogeneousParagraph = HeterogeneousParagraph(chunks_of_text)
        hp.paint(page, bb)
        chunks_of_text = []
        for l in hp._split_to_lines_of_chunks_of_text(hp.get_previous_paint_box()):
            chunks_of_text.extend(l)

        # add rectangle annotation
        for i, c in enumerate(chunks_of_text):
            r: Rectangle = copy.deepcopy(chunks_of_text[i].get_previous_layout_box())
            r.y -= (i + 1) * Decimal(10)
            page.add_annotation(
                SquareAnnotation(
                    stroke_color=colors[i],
                    fill_color=colors[i],
                    bounding_box=r,
                )
            )

        # determine output location
        out_file = self.output_dir / "output.pdf"

        # attempt to store PDF
        with open(out_file, "wb") as in_file_handle:
            PDF.dumps(in_file_handle, pdf)

        compare_visually_to_ground_truth(out_file)
        check_pdf_using_validator(out_file)
