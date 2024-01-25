from openpyxl import Workbook
from openpyxl.styles import Alignment, Font


class WorkbookStylish:
    def __init__(self, wokrbook: Workbook):
        self.workbook = wokrbook
        self.header_row_font = Font(size=12, name="Arial", bold=True)
        self.column_font = Font(size=12, name="Arial")
        self.column_alignment = Alignment(horizontal="center", vertical="center")

    def _format_items_worksheets(self):
        """
        Format items worksheets

        :returns: nothing
        """
        # set column styles
        # format: ["name", "width", "font", "alignment"]
        columns_style = [
            ["A", 12, self.column_font, self.column_alignment],
            ["B", 55, self.column_font, self.column_alignment],
            ["C", 15, self.column_font, self.column_alignment],
            ["D", 10, self.column_font, self.column_alignment],
            ["E", 15, self.column_font, self.column_alignment],
            ["F", 11, self.column_font, self.column_alignment],
            ["G", 14, self.column_font, self.column_alignment],
            ["H", 24, self.column_font, self.column_alignment],
            ["I", 55, self.column_font, self.column_alignment],
        ]

        # update each date worksheet
        for worksheet in self.workbook.worksheets:
            # skip summary sheet
            if worksheet.title == "Summary":
                continue

            # format date worksheet
            for name, width, font, alignment in columns_style:
                worksheet.column_dimensions[name].font = font
                worksheet.column_dimensions[name].alignment = alignment
                worksheet.column_dimensions[name].width = width

            # overwrite header row style
            worksheet.row_dimensions[1] = self.header_row_font

    def _format_summary_worksheet(self):
        """
        Format summary worksheets

        :returns: nothing
        """
        # format: ["name", "width", "font", "alignment"]
        columns_style = [
            ["A", 14, self.column_font, self.column_alignment],
            ["B", 14, self.column_font, self.column_alignment],
            ["C", 14, self.column_font, self.column_alignment],
        ]
        summary_worksheet = self.workbook.get_sheet_by_name("Summary")
        for name, width, font, alignment in columns_style:
            summary_worksheet.column_dimensions[name].font = font
            summary_worksheet.column_dimensions[name].alignment = alignment
            summary_worksheet.column_dimensions[name].width = width
        summary_worksheet.row_dimensions[1] = self.header_row_font

    def style_workbook(self):
        """
        Style the workbook

        :returns: nothing
        """
        self._format_items_worksheets()
        self._format_summary_worksheet()
