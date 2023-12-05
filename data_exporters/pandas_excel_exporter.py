from datetime import datetime
from time import time

import pandas as pd
from openpyxl import Workbook

from data_exporters.workbook_stylish import WorkbookStylish


class PandasExcelExporter:
    def __init__(self, filename: str):
        self.filename = filename

        self.today_date = datetime.utcnow().strftime("%Y-%m-%d")
        self.excel_writer: pd.ExcelWriter = self._create_writter()
        self.workbook: Workbook = self._get_workbook()
        self.workbook_stylish = WorkbookStylish(self.workbook)

    def _create_writter(self) -> pd.ExcelWriter:
        """
        Create and return a pandas excel writter.
        If the file exists, it will open it in append mode, otherwise it creates a new file in write mode.

        :returns: Nothing
        """
        try:
            return pd.ExcelWriter(self.filename, engine="openpyxl", mode="a")
        except FileNotFoundError:
            return pd.ExcelWriter(self.filename, engine="openpyxl", mode="w")

    def _get_workbook(self) -> Workbook:
        """
        Create and return a pandas excel writter.
        If the file exists, it will open it in append mode, otherwise it creates a new file in write mode.

        :returns: Nothing
        """
        return self.excel_writer.book

    def _get_sheet_data(self, sheet_name: str) -> pd.DataFrame:
        """
        Returns a sheet data given its name
        If the sheet doesn't exist, return DataFrame

        :param sheet_name: sheet to get data from

        :returns: sheet data as list of dicts, or DataFrame on sheet not existing
        """
        if sheet_name in self.workbook.sheetnames:
            worksheet = self.workbook.get_sheet_by_name(sheet_name)
            worksheet_values = list(worksheet.values)
            return pd.DataFrame(columns=worksheet_values[0], data=worksheet_values[1:])
        return pd.DataFrame(columns=["price_date", "price_total", "api_error"])

    def _delete_sheet(self, sheet_name: str):
        """
        Deletes a sheet data given its name
        If the sheet doesn't exist, do nothing

        :param sheet_name: sheet to get data from

        :returns: nothing
        """
        if sheet_name in self.workbook.sheetnames:
            worksheet = self.workbook.get_sheet_by_name(sheet_name)
            self.workbook.remove(worksheet)

    def _format_items_today_df_column_order(self, items_today_df: pd.DataFrame) -> pd.DataFrame:
        """
        Set the desired order of columns to write to an excel spreadsheet on items dataframes

        :param items_today_df: today items dataframe to have its column order set

        :returns: new df with the desired column order
        """
        return items_today_df[
            [
                "app_id",
                "name",
                "price_unitary",
                "amount",
                "price_total",
                "api_error",
                "price_date",
                "price_date_timestamp",
                "market_hash_name",
            ]
        ]

    def _format_summary_df_column_order(self, summary_df: pd.DataFrame) -> pd.DataFrame:
        """
        Set the desired order of columns to write to an excel spreadsheet on summary dataframes

        :param summary_df: summary dataframe to have its column order set

        :returns: new df with the desired column order
        """
        return summary_df[["price_date", "price_total", "api_error"]]

    def _get_items_today_sum(self, items_today_df: pd.DataFrame) -> dict:
        """
        Get a report of all items in today's items

        :param items_df: today's item dataframe

        :returns: dict with sum of today's items data
        """
        today_price_total = items_today_df["price_total"].sum()
        api_error_amount = items_today_df[items_today_df["api_error"] == "yes"].shape[0]
        today_sum = {
            "amount": items_today_df["amount"].sum(),
            "app_id": "---",
            "market_hash_name": "---",
            "name": "Sum of all items",
            "price_unitary": "---",
            "price_total": today_price_total,
            "price_date": self.today_date,
            "price_date_timestamp": int(time()),
            "api_error": "yes" if api_error_amount > 0 else "no",
        }
        return today_sum

    def _get_today_summary(self, today_sum: dict) -> dict:
        """
        Get summary report for today's items

        :param today_sum: today's item summed data

        :returns: dict with summary data
        """
        today_summary = {
            "api_error": today_sum["api_error"],
            "price_total": today_sum["price_total"],
            "price_date": today_sum["price_date"],
        }
        return today_summary

    def _append_data_to_df(self, df: pd.DataFrame, data: dict) -> pd.DataFrame:
        """
        Add a dict to a dataframe and return new dataframe

        :param df: dataframe to have data appended to it
        :param data: new data to be added to the dataframe

        :returns: new dataframe with data row included to df
        """
        new_row = pd.DataFrame([data])
        return pd.concat([df, new_row], ignore_index=True)

    def export_today_items(self, items_today: list[dict]):
        """
        Add provided items to today's sheet
        Also, add today to summary sheet

        :param items_today: list of items to be added to today's sheet

        :returns: nothing
        """
        # set items as a dataframe and compute total price of each iten
        items_today_df = pd.DataFrame(items_today)
        items_today_df["price_total"] = items_today_df["price_unitary"] * items_today_df["amount"]

        # add today's prices sum to dataframe
        today_sum = self._get_items_today_sum(items_today_df)
        items_today_df = self._append_data_to_df(items_today_df, today_sum)
        items_today_df = self._format_items_today_df_column_order(items_today_df)

        # get summary sheet and add today's summary (or overwrite, if it exists)
        # NOTE: for some reason, the price_date column values are starting with a '
        summary_df = self._get_sheet_data("Summary")
        if self.today_date in summary_df["price_date"].values:
            summary_df = summary_df.drop(summary_df.index[-1])
        today_summary = self._get_today_summary(today_sum)
        summary_df = self._append_data_to_df(summary_df, today_summary)
        summary_df = self._format_summary_df_column_order(summary_df)

        # remove summary and today's prices sheets
        self._delete_sheet("Summary")
        self._delete_sheet(self.today_date)

        # add new sheets
        items_today_df.to_excel(self.excel_writer, index=False, sheet_name=self.today_date)
        summary_df.to_excel(self.excel_writer, index=False, sheet_name="Summary")
        self.workbook_stylish.style_workbook()
        self.excel_writer.close()
