import unittest
from datetime import datetime
from pathlib import Path

from borb.io.read.types import Decimal
from borb.pdf.canvas.color.color import HexColor
from borb.pdf.canvas.geometry.rectangle import Rectangle
from borb.pdf.canvas.layout.annotation.square_annotation import SquareAnnotation
from borb.pdf.canvas.layout.layout_element import Alignment
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.table.fixed_column_width_table import (
    FixedColumnWidthTable as Table,
)
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.document.document import Document
from borb.pdf.page.page import Page
from borb.pdf.pdf import PDF
from tests.test_util import compare_visually_to_ground_truth, check_pdf_using_validator


class TestAddParagraphJustifiedCenterWithPaddingAndBorderAndBackground(
    unittest.TestCase
):
    """
    This test creates a PDF with a Paragraph object in it. The Paragraph is aligned BOTTOM, CENTERED.
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
                    "This test creates a PDF with a Paragraph object in it. The Paragraph is aligned BOTTOM, CENTERED."
                )
            )
            .set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))
        )
        p = Paragraph(
            """
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
            Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. 
            Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. 
            Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
            """,
            font_size=Decimal(12),
            text_alignment=Alignment.CENTERED,
            vertical_alignment=Alignment.BOTTOM,
            padding_top=Decimal(5),
            padding_right=Decimal(5),
            padding_bottom=Decimal(5),
            padding_left=Decimal(5),
            border_top=True,
            border_right=True,
            border_bottom=True,
            border_left=True,
            border_color=HexColor("56cbf9"),
            background_color=HexColor("0b3954"),
            font_color=HexColor("ffffff"),
            border_width=Decimal(1),
        )

        # the next line of code uses absolute positioning
        # fmt: off
        r: Rectangle = Rectangle(
            Decimal(59),  # x: 0 + page_margin
            Decimal(848 - 84 - 200 - 100),  # y: page_height - page_margin - y - height_of_textbox
            Decimal(595 - 59 * 2),  # width: page_width - 2 * page_margin
            Decimal(100),  # height
        )
        # fmt: on

        # this is a quick and dirty way to draw a rectangle on the page
        page.add_annotation(SquareAnnotation(r, stroke_color=HexColor("f1cd2e")))

        # add the paragraph to the page
        p.paint(page, r)

        # determine output location
        out_file = self.output_dir / "output.pdf"

        # attempt to store PDF
        with open(out_file, "wb") as in_file_handle:
            PDF.dumps(in_file_handle, pdf)

        # compare visually
        compare_visually_to_ground_truth(out_file)
        check_pdf_using_validator(out_file)
