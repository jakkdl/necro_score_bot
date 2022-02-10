import xml.etree.ElementTree as ET

import nsb_steam


def entryIndex(xml):
    for index, value in enumerate(xml):
        if value.tag == 'entries':
            return index
    raise Exception('no index tag in xml')


def convertIfPossible(data):
    try:
        return int(data)
    except (ValueError, TypeError):
        pass

    try:
        return float(data)
    except (ValueError, TypeError):
        pass

    return data


def xmlToList(response, responseType):
    text = nsb_steam.decodeResponse(response)
    data = ET.fromstring(text)
    return xmlToList_internal(data, responseType)


def xmlToList_file(path, responseType):
    tree = ET.parse(path)
    root = tree.getroot()
    return xmlToList_internal(root, responseType)


def xmlToList_internal(xml_data, responseType):
    result = []
    if responseType == 'leaderboard':
        index = entryIndex(xml_data)
        entries = xml_data[index]
    elif responseType == 'index':
        entries = xml_data[3:]
    else:
        raise Exception('Unknown responseType')

    for entry in entries:
        dictEntry = {}

        for data in entry:
            tag = data.tag
            if tag == 'score':
                tag = 'points'
            elif tag == 'steamid':
                tag = 'steam_id'
            dictEntry[tag] = convertIfPossible(data.text)

        result.append(dictEntry)

    return result
