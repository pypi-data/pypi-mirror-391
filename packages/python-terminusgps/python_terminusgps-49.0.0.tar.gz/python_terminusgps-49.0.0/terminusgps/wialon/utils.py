import secrets
import string
import typing
from collections.abc import Collection

from terminusgps.wialon import flags
from terminusgps.wialon.items import WialonObjectFactory
from terminusgps.wialon.items.unit import WialonUnit
from terminusgps.wialon.items.user import WialonUser
from terminusgps.wialon.session import WialonSession


def get_notifications(
    resource_id: str | int,
    session: WialonSession,
    notification_ids: Collection[int] | None = None,
) -> list[dict[str, typing.Any]]:
    """
    Returns a list of notification dictionaries from the Wialon API.

    Wialon notification dictionary format:

    +----------------+----------------+-----------------------------------------------+
    | key            | type           | desc                                          |
    +================+================+===============================================+
    | ``"id"``       | :py:obj:`int`  | Notification ID                               |
    +----------------+----------------+-----------------------------------------------+
    | ``"n"``        | :py:obj:`str`  | Notification name                             |
    +----------------+----------------+-----------------------------------------------+
    | ``"txt"``      | :py:obj:`int`  | Notification text                             |
    +----------------+----------------+-----------------------------------------------+
    | ``"ta"``       | :py:obj:`int`  | Activation time (UNIX timestamp)              |
    +----------------+----------------+-----------------------------------------------+
    | ``"td"``       | :py:obj:`int`  | Deactivation time (UNIX timestamp)            |
    +----------------+----------------+-----------------------------------------------+
    | ``"ma"``       | :py:obj:`int`  | Maximum number of alarms (0 = unlimited)      |
    +----------------+----------------+-----------------------------------------------+
    | ``"mmtd"``     | :py:obj:`int`  | Maximum time interval between messages (sec)  |
    +----------------+----------------+-----------------------------------------------+
    | ``"cdt"``      | :py:obj:`int`  | Alarm timeout (sec)                           |
    +----------------+----------------+-----------------------------------------------+
    | ``"mast"``     | :py:obj:`int`  | Minimum duration of the alarm state (sec)     |
    +----------------+----------------+-----------------------------------------------+
    | ``"mpst"``     | :py:obj:`int`  | Minimum duration of previous state (sec)      |
    +----------------+----------------+-----------------------------------------------+
    | ``"cp"``       | :py:obj:`int`  | Control period relative to current time (sec) |
    +----------------+----------------+-----------------------------------------------+
    | ``"fl"``       | :py:obj:`int`  | Notification flags                            |
    +----------------+----------------+-----------------------------------------------+
    | ``"tz"``       | :py:obj:`int`  | Notification timezone                         |
    +----------------+----------------+-----------------------------------------------+
    | ``"la"``       | :py:obj:`str`  | Notification language code                    |
    +----------------+----------------+-----------------------------------------------+
    | ``"ac"``       | :py:obj:`int`  | Alarms count                                  |
    +----------------+----------------+-----------------------------------------------+
    | ``"d"``        | :py:obj:`str`  | Notification description                      |
    +----------------+----------------+-----------------------------------------------+
    | ``"sch"``      | :py:obj:`dict` | Notification schedule (see below)             |
    +----------------+----------------+-----------------------------------------------+
    | ``"ctrl_sch"`` | :py:obj:`dict` | Notification control schedule (see below)     |
    +----------------+----------------+-----------------------------------------------+
    | ``"un"``       | :py:obj:`list` | List of unit/unit group IDs                   |
    +----------------+----------------+-----------------------------------------------+
    | ``"act"``      | :py:obj:`list` | List of notification actions (see below)      |
    +----------------+----------------+-----------------------------------------------+
    | ``"trg"``      | :py:obj:`dict` | Notification trigger (see below)              |
    +----------------+----------------+-----------------------------------------------+
    | ``"ct"``       | :py:obj:`int`  | Creation time (UNIX timestamp)                |
    +----------------+----------------+-----------------------------------------------+
    | ``"mt"``       | :py:obj:`int`  | Last modification time (UNIX timestamp)       |
    +----------------+----------------+-----------------------------------------------+

    Notification schedule/control schedule format:

    +----------+----------------+------------------------------------------------------------------+
    | key      | type           | desc                                                             |
    +==========+================+==================================================================+
    | ``"f1"`` | :py:obj:`int`  | Beginning of interval 1 (minutes from midnight)                  |
    +----------+----------------+------------------------------------------------------------------+
    | ``"f2"`` | :py:obj:`int`  | Beginning of interval 2 (minutes from midnight)                  |
    +----------+----------------+------------------------------------------------------------------+
    | ``"t1"`` | :py:obj:`int`  | End of interval 1 (minutes from midnight)                        |
    +----------+----------------+------------------------------------------------------------------+
    | ``"t2"`` | :py:obj:`int`  | End of interval 2 (minutes from midnight)                        |
    +----------+----------------+------------------------------------------------------------------+
    | ``"m"``  | :py:obj:`int`  | Mask of the days of the month (1: 2\ :sup:`0`, 31: 2\ :sup:`30`) |
    +----------+----------------+------------------------------------------------------------------+
    | ``"y"``  | :py:obj:`int`  | Mask of months (Jan: 2\ :sup:`0`, Dec: 2\ :sup:`11`)             |
    +----------+----------------+------------------------------------------------------------------+
    | ``"w"``  | :py:obj:`int`  | Mask of days of the week (Mon: 2\ :sup:`0`, Sun: 2\ :sup:`6`)    |
    +----------+----------------+------------------------------------------------------------------+
    | ``"f"``  | :py:obj:`int`  | Schedule flags                                                   |
    +----------+----------------+------------------------------------------------------------------+

    Notification `action <https://wialon-help.link/bb04a9a5>`_ format (each item in the ``act`` list):

    +----------+-----------------+-------------------+
    | key      | type            | desc              |
    +==========+=================+===================+
    | ``"t"``  | :py:obj:`str`   | Action type       |
    +----------+-----------------+-------------------+
    | ``"p"``  | :py:obj:`dict`  | Action parameters |
    +----------+-----------------+-------------------+

    Notification `trigger <https://wialon-help.link/9d54585d>`_ format:

    +----------+-----------------+--------------------+
    | key      | type            | desc               |
    +==========+=================+====================+
    | ``"t"``  | :py:obj:`str`   | Trigger type       |
    +----------+-----------------+--------------------+
    | ``"p"``  | :py:obj:`dict`  | Trigger parameters |
    +----------+-----------------+--------------------+

    :param resource_id: A Wialon resource id.
    :type resource_id: str | int
    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.session.WialonSession
    :param notification_ids: Optional. A list of notification ids.
    :type notification_ids: ~collections.abc.Collection[int] | None
    :raises ValueError: If ``resource_id`` was a string containing non-digit characters.
    :returns: A list of Wialon notification dictionaries.
    :rtype: list[dict[str, ~typing.Any]]

    """
    if isinstance(resource_id, str) and not resource_id.isdigit():
        raise ValueError(
            f"resource_id can only contain digits, got '{resource_id}'."
        )
    params = {"itemId": resource_id}
    if notification_ids is not None:
        params["col"] = notification_ids
    return session.wialon_api.resource_get_notification_data(**params)


def get_hw_types(session: WialonSession) -> list[dict[str, str | int]]:
    """
    Returns a list of hardware type objects for Wialon.

    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.session.WialonSession
    :returns: A list of hardware types.
    :rtype: list[dict[str, str | int]]

    Hardware type format:

    +----------+--------------------+
    | key      | value              |
    +==========+====================+
    | ``id``   | Hardware type id   |
    +----------+--------------------+
    | ``name`` | Hardware type name |
    +----------+--------------------+

    """
    return session.wialon_api.core_get_hw_types()


def get_user_by_name(name: str, session: WialonSession) -> WialonUser:
    """
    Returns a Wialon user by name.

    :param name: A Wialon user name.
    :type name: str
    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.session.WialonSession
    :returns: A Wialon user.
    :rtype: ~terminusgps.wialon.items.user.WialonUser | None

    """
    response = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "user",
                "propName": "sys_name",
                "propValueMask": name,
                "sortType": "sys_name",
                "propType": "property",
            },
            "force": 0,
            "flags": flags.DataFlag.USER_BASE,
            "from": 0,
            "to": 0,
        }
    )
    num_items: int = int(response.get("totalItemsCount"))
    if num_items > 1:
        raise ValueError(f"Multiple users returned for '{name}'.")
    elif num_items <= 0:
        raise ValueError(f"Couldn't find a Wialon user named '{name}'.")
    factory = WialonObjectFactory(session)
    user_id = response.get("items")[0].get("id")
    return factory.get("user", id=int(user_id))


def get_carrier_names(session: WialonSession) -> list[str]:
    """
    Returns a list of all telecommunication carrier company names present in Wialon.

    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.session.WialonSession
    :returns: A list of telecommunication carrier company names.
    :rtype: list[str]

    """
    response = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "avl_unit",
                "propName": "admin_fields,rel_adminfield_value",
                "propValueMask": "carrier,*",
                "sortType": "admin_fields,admin_fields",
                "propType": "propitemname",
            },
            "force": 0,
            "flags": flags.DataFlag.UNIT_BASE
            | flags.DataFlag.UNIT_ADMIN_FIELDS,
            "from": 0,
            "to": 0,
        }
    )
    carrier_names: list[str] = [
        str(field["v"]).lower()
        for item in response.get("items", [{}])
        for field in item.get("aflds", {}).values()
        if field["n"] == "carrier" and field["v"]
    ]
    return sorted(list(frozenset(carrier_names)))


def get_units_by_carrier(
    carrier_name: str, session: WialonSession
) -> list[WialonUnit]:
    """
    Returns a list of all units by telecommunications carrier company name.

    :param carrier_name: Case-insensitive telecommunications carrier company name, e.g. ``"UScell"`` or ``"Conetixx"``.
    :type carrier_name: str
    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.session.WialonSession
    :returns: A list of units.
    :rtype: list[~terminusgps.wialon.items.unit.WialonUnit]

    """
    response = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "avl_unit",
                "propName": "admin_fields,rel_adminfield_value",
                "propValueMask": f"carrier,{carrier_name.lower()}",
                "sortType": "admin_fields,admin_fields",
                "propType": "propitemname",
            },
            "force": 0,
            "flags": flags.DataFlag.UNIT_BASE
            | flags.DataFlag.UNIT_ADMIN_FIELDS,
            "from": 0,
            "to": 0,
        }
    )
    num_items: int = int(response.get("totalItemsCount"))
    if num_items <= 0:
        raise ValueError(
            f"Couldn't find any units by carrier '{carrier_name.lower()}'."
        )

    factory = WialonObjectFactory(session)
    unit_ids = [int(unit.get("id")) for unit in response.get("items")]
    return [factory.get("avl_unit", id) for id in unit_ids]


def get_unit_by_iccid(iccid: str, session: WialonSession) -> WialonUnit:
    """
    Returns a unit by iccid (SIM card #).

    :param iccid: A SIM card #.
    :type iccid: str
    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.session.WialonSession
    :returns: The Wialon unit.
    :rtype: ~terminusgps.wialon.items.WialonUnit

    """
    response = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "avl_unit",
                "propName": "admin_fields,rel_adminfield_value",
                "propValueMask": f"iccid,{iccid}",
                "sortType": "admin_fields,admin_fields",
                "propType": "propitemname",
            },
            "force": 0,
            "flags": flags.DataFlag.UNIT_BASE
            | flags.DataFlag.UNIT_ADMIN_FIELDS,
            "from": 0,
            "to": 0,
        }
    )

    num_items: int = int(response.get("totalItemsCount"))
    if num_items > 1:
        raise ValueError(f"Multiple units returned for '{iccid}'.")
    elif num_items <= 0:
        raise ValueError(f"Couldn't find a Wialon unit with iccid '{iccid}'.")

    factory = WialonObjectFactory(session)
    return factory.get("avl_unit", id=int(response.get("items")[0].get("id")))


def get_unit_by_imei(
    imei: int | str, session: WialonSession
) -> WialonUnit | None:
    """
    Takes a Wialon unit's IMEI # and returns its unit id.

    :param imei: A Wialon unit's IMEI #.
    :type imei: str
    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.session.WialonSession
    :raises ValueError: If ``imei`` wasn't a digit.
    :raises WialonAPIError: If something went wrong calling the Wialon API.
    :returns: A Wialon unit, if it was found.
    :rtype: ~terminusgps.wialon.items.unit.WialonUnit | None

    """
    if isinstance(imei, str) and not imei.isdigit():
        raise ValueError(f"'imei' must be a digit, got '{imei}'.")
    response = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "avl_unit",
                "propName": "sys_unique_id",
                "propValueMask": imei,
                "sortType": "sys_unique_id",
                "propType": "property",
            },
            "force": 0,
            "flags": flags.DataFlag.UNIT_BASE,
            "from": 0,
            "to": 0,
        }
    )
    num_items: int = int(response.get("totalItemsCount"))
    if num_items > 1:
        raise ValueError(f"Multiple units returned for IMEI #: '{imei}'.")
    elif num_items <= 0:
        raise ValueError(f"Couldn't find a Wialon unit with IMEI #: '{imei}'.")

    factory = WialonObjectFactory(session)
    return factory.get("avl_unit", id=int(response.get("items")[0].get("id")))


def get_vin_info(vin: str, session: WialonSession) -> dict[str, typing.Any]:
    """
    Retrieves vehicle data from a VIN number.

    :param vin: A vehicle VIN #.
    :type vin: str
    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.session.WialonSession
    :returns: A dictionary of vehicle information, if any was found.
    :rtype: dict[str, ~typing.Any]

    """
    response = session.wialon_api.unit_get_vin_info(**{"vin": vin})
    results = response.get("vin_lookup_result", {})
    if "error" in results.keys():
        return {}
    return {field.get("n"): field.get("v") for field in results.get("pflds")}


def generate_wialon_password(length: int = 32) -> str:
    """
    Generates a Wialon compliant password between ``8`` and ``64`` characters.

    The generated password will contain:

        - At least one uppercase letter.
        - At least one lowercase letter.
        - At least one special symbol.
        - At least three digits.

    :param length: Length of the generated password. Default is ``32``.
    :type length: int
    :raises ValueError: If ``length`` was less than ``8`` or greater than ``64``.
    :returns: A Wialon compliant password.
    :rtype: str

    """
    min_length, max_length = 8, 64
    if length > max_length:
        raise ValueError(
            f"Password cannot be greater than {max_length} characters in length, got {length}."
        )
    elif length < min_length:
        raise ValueError(
            f"Password cannot be less than {min_length} characters in length, got {length}."
        )

    s0 = list(string.ascii_uppercase)
    s1 = list(string.ascii_lowercase)
    s2 = list(string.digits)
    s3 = list("!@#$%^*()[]-_+")

    while True:
        password = "".join(
            [secrets.choice(s0 + s1 + s2 + s3) for _ in range(length)]
        )
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and sum(c.isdigit() for c in password) >= 3
            and any(c in s3 for c in password)
        ):
            break
    return password
