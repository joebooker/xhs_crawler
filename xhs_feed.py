import json
import time
import random
import execjs
import requests
from loguru import logger

def base36encode(number, digits='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    base36 = ""
    while number:
        number, i = divmod(number, 36)
        base36 = digits[i] + base36
    return base36.lower()

def generate_search_id():
    timestamp = int(time.time() * 1000) << 64
    random_value = int(random.uniform(0, 2147483646))
    return base36encode(timestamp + random_value)

url = "https://edith.xiaohongshu.com/api/sns/web/v1/feed"
api_endpoint = '/api/sns/web/v1/feed'



data = {"source_note_id":"6653c1b4000000001303eb04","image_formats":["jpg","webp","avif"],"extra":{"need_body_topic":"1"},"xsec_source":"pc_feed","xsec_token":"ABA568O3eIjf3uDTBtydz1daPZLEFIO6h6Gtaq0UMbCak="}

cookies ={
            "a1":'xxxxxx',
            #………………………………
        }
a1_value=cookies['a1']
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://www.xiaohongshu.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://www.xiaohongshu.com/",
    "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "rsec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "x-b3-traceid": "9cbac8e2b8562aa3"
}

with open('GenXsAndCommon_56.js', 'r', encoding='utf-8') as f:
    js_script = f.read()
    context = execjs.compile(js_script)
    sign = context.call('getXs', api_endpoint, data, a1_value)

logger.info(f'{sign}')
headers['x-s'] = sign['X-s']
headers['x-t'] = str(sign['X-t'])
# headers['X-s-common'] = sign['X-s-common']

data = json.dumps(data, separators=(',', ':'))
response = requests.post(url, headers=headers, cookies=cookies, data=data)

print(response.status_code)
print(response.json())