import pandas as pd

from models.items import ItemWithPrice
from models.utils import convert_list_to_model


class ExcelReader:
    def __init__(self, filename: str):
        self.filename = filename

        self.excel_file = pd.ExcelFile(self.filename)

    def get_most_recent_date_sheet_name(self) -> str:
        """
        Returns the most recent date sheet
        Note that we are skipping summary sheet here

        :returns: the most recent date sheet
        """
        sheet_names = sorted(self.excel_file.sheet_names)
        return sheet_names[-2]

    def get_items(self) -> list[ItemWithPrice]:
        """
        Get the most recent date sheet items excluding the sum line

        :returns: the most recent date sheet items
        """
        sheet_name = self.get_most_recent_date_sheet_name()
        items_df = self.excel_file.parse(sheet_name)
        items_df = items_df.drop(items_df.index[-1])
        items = items_df.to_dict("records")
        return convert_list_to_model(ItemWithPrice, items)
