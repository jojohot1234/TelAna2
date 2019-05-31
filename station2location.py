import json
import requests
from bs4 import BeautifulSoup


def station2location(stations):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36'
        }
    if stations[0] == 'NULL' or stations[1] == 'NULL':
        stations[0] = '0x0'
        stations[1] = '0x0'
        url = ' http://api.cellocation.com:81/cell/' \
              '?mcc=460&mnc=0&lac={}&ci={}&output=json'.format(int(stations[0], 16), int(stations[1], 16))
    else:
        url = ' http://api.cellocation.com:81/cell/' \
      '?mcc=460&mnc=0&lac={}&ci={}&output=json'.format(int(stations[0], 16), int(stations[1], 16))

    data = requests.get(url, headers=headers)
# 返回值 data.text --> <class 'str'>
# {"errcode":0, "lat":"39.96135712", "lon":"116.37831879", "radius":"420", "address":"北京市西城区德胜街道黄寺大街24号院22号楼;什坊街与黄寺大街路口东58米"}
    location = json.loads(data.text)
# 坐标类型(wgs84/gcj02/bd09)，默认wgs84
    if location['lat']== '' or location['lon'] == '':
        print('基站数据有误')
    else:
        print(location['lat'], location['lon'], location['address'])
