import argparse
import asyncio

from data_exporters.pandas_excel_exporter import PandasExcelExporter
from data_readers.excel_reader import ExcelReader
from external_apis.steam.api import SteamAPI


async def main(excel_file_name: str):
    # get list of items
    excel_reader = ExcelReader(excel_file_name)
    items = excel_reader.get_items()

    # retrieve price for items
    steam_api = SteamAPI()
    items_with_price = await steam_api.items.add_items_price(items)

    # export data
    excel_exporter = PandasExcelExporter(excel_file_name)
    excel_exporter.export_today_items(items_with_price)


if __name__ == "__main__":
    # creates an argparse object to parse command line option
    parser = argparse.ArgumentParser(
        description="Update today spreadsheet with most up to date prices or add a new spreadsheet if today date does not have it's own spreadsheet yet"
    )
    parser.add_argument(
        "excel_file_name",
        help="Which file name to use. Do not add extension to it, .xlxs will be used. 'prices' is the default value",
        type=str,
    )

    # waits for command line input
    # (proceeds only if it is validated against the options set before)
    args = parser.parse_args()

    # start async loop
    asyncio.run(main(args.excel_file_name + ".xlsx"))
