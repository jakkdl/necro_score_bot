import json
import nsb_steam
from pprint import pprint

url1 = 'http://www.necrolab.com/api/power_rankings/latest_rankings'
url2 = 'http://www.necrolab.com/api/daily_rankings/latest_rankings'




#response = nsb_steam.fetchUrl(url2)
#data = json.loads(response.read().decode())
#pprint(data)



nsb_steam.fetchUrl(url1, 'data.json')

with open('data.json') as data_file:
    data = json.load(data_file)
#
pprint(data)

class necrolab_info:

    def __init(self, mode):


        self.mode = mode


    def url(self):
        result = 'http://www.necrolab.com/api/'
        result += self.mode
        result += '/latest_rankings'
        return result

