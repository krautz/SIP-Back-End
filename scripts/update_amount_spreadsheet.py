import argparse
import asyncio

import pandas as pd

from scripts.common import format_workbook, set_items_df_column_order, set_summary_df_column_order
from steamapi.inventory import get_user_inventory
from utils.pandas import append_row_to_df


async def main(excel_file_name, steam_id):
    # create empty dataframe for new summary
    summary_df = pd.DataFrame()

    # read provided excel file
    excel_file = pd.ExcelFile(excel_file_name)

    # get any date spreadsheet (to get items to update amount)
    summary_sheet_index = excel_file.sheet_names.index("Summary")
    any_date_sheet = excel_file.sheet_names[summary_sheet_index - 1]
    any_date_items_df = excel_file.parse(any_date_sheet)

    # get app ids on spreadsheet
    app_ids = list(any_date_items_df["app_id"].unique())

    # filter out row that are not numbers (the row '---' on summary line)
    app_ids = list(filter(lambda app_id: isinstance(app_id, int), app_ids))

    # get user's inventory for app ids present on spreadsheet
    user_items = {}
    for app_id in app_ids:
        user_items.update(await get_user_inventory(steam_id, app_id, as_dict=True))

    # remove summary line from items data frame
    number_of_lines = any_date_items_df.shape[0]
    any_date_items_df = any_date_items_df.drop([number_of_lines - 1])

    # set a one column df with the new amount of items
    amount_df = pd.DataFrame({"amount": []})
    removed_items_idx = []
    for idx, item in any_date_items_df.iterrows():
        # item not found on user inventory -> mark the item as removed and skip for the next one
        if not user_items.get(item["market_hash_name"]):
            removed_items_idx.append(idx)
            continue

        # item still in user inventory -> update item amount
        amount_df = append_row_to_df(amount_df, {"amount": user_items[item["market_hash_name"]]["amount"]})

    amount_df["amount"] = amount_df["amount"].astype(int)

    # get object to write into excel
    excel_writer = pd.ExcelWriter(excel_file_name, engine="openpyxl")

    # update amount, total price and summaries
    summaries = []
    excel_file.sheet_names.sort()  # guarantee days are ordered
    for sheet_name in excel_file.sheet_names:
        # summary sheet -> skip
        if sheet_name == "Summary":
            continue

        # not summary sheet -> get summary line and drop it form day df
        day_df = excel_file.parse(sheet_name)
        number_of_lines = day_df.shape[0]
        summary_row_index = number_of_lines - 1
        summary_row = day_df.iloc[[summary_row_index]]
        day_df = day_df.drop([summary_row_index])

        # drop removed items and update amount
        day_df = day_df.drop(removed_items_idx)
        day_df["amount"] = amount_df

        # update total price
        day_df["price_total"] = day_df["price_unitary"] * day_df["amount"]

        # update summary
        summary_row.at[summary_row_index, "amount"] = day_df["amount"].sum()
        summary_row.at[summary_row_index, "price_total"] = day_df["price_total"].sum()
        print(summary_row)
        day_df = append_row_to_df(day_df, summary_row)

        # add day summary to new summary sheet
        summaries.append(
            {
                "api_error": summary_row.at[summary_row_index, "api_error"],
                "price_total": summary_row.at[summary_row_index, "price_total"],
                "price_date": summary_row.at[summary_row_index, "price_date"],
            }
        )

        # write day's prices to excel exclusive sheet
        day_df = set_items_df_column_order(day_df)
        day_df.to_excel(excel_writer, index=False, sheet_name=sheet_name)

    # write new summary sheet
    summary_df = pd.DataFrame(summaries)
    summary_df = set_summary_df_column_order(summary_df)
    summary_df.to_excel(excel_writer, index=False, sheet_name="Summary")

    # persis changes
    format_workbook(excel_writer.book)
    excel_writer.save()


if __name__ == "__main__":
    # creates an argparse object to parse command line option
    parser = argparse.ArgumentParser(description="Update ammount of each user item")
    parser.add_argument(
        "excel_file_name",
        help="Which file name to use. Do not add extension to it, .xlxs will be used. 'prices' is the default value",
        type=str,
    )
    parser.add_argument(
        "steam_id",
        help="Users's Steam id (search for 'ID Steam' on 'https://store.steampowered.com/account')",
        type=int,
    )

    # waits for command line input
    # (proceeds only if it is validated against the options set before)
    args = parser.parse_args()

    # start async loop
    asyncio.run(main(args.excel_file_name + ".xlsx", args.steam_id))
