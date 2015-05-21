import pickle
import xml.etree.ElementTree as ET
import json

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
    result = []
    text = nsb_steam.decodeResponse(response)
    data = ET.fromstring(text)

    if responseType == 'leaderboard':
        index = entryIndex(data)
        entries = data[index]
    elif responseType == 'index':
        entries = data[3:]
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



def jsonToList(response):

    data = json.loads(response.read().decode())

    for entry in data['data']:
        for key in entry:
            entry[key] = convertIfPossible(entry[key])

    return data['data']



def pickle_file(data, path):
    with open(path, 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)


def unpickle(path):
    with open(path, 'rb') as f:
        # The protocol version used is detected automatically, so we do not
        # have to specify it.
        return pickle.load(f)






