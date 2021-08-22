"""
Common functionalities between scripts.
"""

import pandas as pd

from datetime import datetime
from time import time

def write_items_to_excel(items, spreadsheet_name):
    """
    Write an array of items dict into a dataframe.
    Also, compute the sum value of all items.

    :param items: list of dict containing items
    :param spreadsheet_name: file name to write to

    :returns: nothing
    """
    # set the result as a dataframe and write to xlsx file
    items_data_frame = pd.DataFrame(items)
    items_data_frame["price_total"] = items_data_frame["price_unitary"] * items_data_frame["amount"]
    items_data_frame = items_data_frame.append(
        {
            "amount": items_data_frame["amount"].sum(),
            "app_id": "---",
            "market_hash_name": "---",
            "name": "Sum of all items",
            "price_unitary": "---",
            "price_total": items_data_frame["price_total"].sum(),
            "price_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "price_date_timestamp": int(time())
        },
        ignore_index = True
    )
    items_data_frame.to_excel(spreadsheet_name, index=False)
