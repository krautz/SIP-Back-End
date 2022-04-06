#
# database utils
#
from datetime import date
from db.metadata import sip_sessionmaker
from db.models import List

from sqlalchemy.orm.session import Session as SessionT
from typing import Optional

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
