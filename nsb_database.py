import xml.etree.ElementTree as ET
from typing import Any, cast

import requests


def entry_index(xml: ET.Element) -> int:
    """returns at which index the entries are"""
    for index, value in enumerate(xml):
        if value.tag == "entries":
            return index
    raise Exception("no index tag in xml")


def convert_if_possible(data: str) -> Any:
    """Converts data to int or float, if possible. Otherwise returns data"""
    try:
        return int(data)
    except (ValueError, TypeError):
        pass

    try:
        return float(data)
    except (ValueError, TypeError):
        pass

    return data


def xml_to_list(
    response: requests.Response, response_type: str
) -> list[dict[str, str]]:
    text = response.text
    data = ET.fromstring(text)
    return xml_to_list_internal(data, response_type)


def xml_to_list_internal(
    xml_data: ET.Element, response_type: str
) -> list[dict[str, str]]:
    result = []
    if response_type == "leaderboard":
        index = entry_index(xml_data)
        entries: ET.Element = xml_data[index]
    elif response_type == "index":
        entries = cast(ET.Element, xml_data[3:])
    else:
        raise Exception("Unknown response_type")

    for entry in entries:
        dict_entry = {}

        for data in entry:
            tag = data.tag
            if tag == "score":
                tag = "points"
            elif tag == "steamid":
                tag = "steam_id"
            assert isinstance(data.text, str)
            dict_entry[tag] = convert_if_possible(data.text)

        result.append(dict_entry)

    return result
