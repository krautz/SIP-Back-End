#
# database utils
#
from datetime import date
from db.metadata import sip_sessionmaker
from db.models import List, Item

from sqlalchemy.orm.session import Session as SessionT
from typing import Optional, List as ListT

def create_list(
    steam_id: int,
    name: str,
    session_external: Optional[SessionT] = None,
) -> List:
    """
    Create a list for the steam_id with the given name

    :param steam_id: steam identifier that holds the list
    :param name: list name
    :param session_external: input session. if provided, session is flushed, and not commited

    :returns: created list ORM object
    """
    # set session based if external sessions has been provided or not
    if session_external:
        session = session_external
    else:
        session = sip_sessionmaker()

    # create list ORM
    list = List(
        name=name, steam_id=steam_id, created_at=date.today(), updated_at=date.today()
    )
    session.add(list)

    # persist changes
    if session_external:
        session.flush()
    else:
        session.commit()
        session.close()

    return list


def create_items(
    items_input: ListT[dict],
    session_external: Optional[SessionT] = None,
) -> ListT[Item]:
    """
    Create all items provided.

    :param items_input: list with dict of items, where each dict must have
        :property market_hash_name: item name, which is its id
        :property app_id: app id of the app (game) that the item belongs to
        :property name_en: item name in english
    :param session_external: input session. if provided, session is flushed, and not commited

    :returns: created items ORM object
    """
    # set session based if external sessions has been provided or not
    if session_external:
        session = session_external
    else:
        session = sip_sessionmaker()

    # search for existent item names
    item_input_names = [item["market_hash_name"] for item in items_input]
    existing_items = session.query(Item.market_hash_name).filter(
        Item.market_hash_name.in_(item_input_names)
    )
    existing_item_names = [item.market_hash_name for item in existing_items]

    # create items ORM only for new items
    # NOTE: we could sort items_input and existing_item_names and traverse with two pointers
    #       to make this O(n log(n)) instead of O(n^2)
    items = []
    for item_input in items_input:
        if item_input["market_hash_name"] not in existing_item_names:
            item = Item(
                market_hash_name=item_input["market_hash_name"],
                app_id=item_input["app_id"],
                name_en=item_input["name_en"],
            )
            items.append(item)
            session.add(item)

    # persist changes
    if session_external:
        session.flush()
    else:
        session.commit()
        session.close()

    return items
