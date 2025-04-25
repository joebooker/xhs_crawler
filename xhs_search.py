import json
import time
import random
import execjs
import requests
from loguru import logger
import re

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


search_data = {
    "keyword": "考研",
    "page": 1,
    "page_size": 20,
    "search_id": generate_search_id(),
    "sort": "general",#popularity_descending,time_descending
    "note_type": 0
}

headers = {
  'sec-ch-ua': 'Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
  'Content-Type': 'application/json;charset=UTF-8',
  'sec-ch-ua-mobile': '?0',
  'Referer': 'https://www.xiaohongshu.com/',
  'sec-ch-ua-platform': 'macOS',
  'Origin': 'https://www.xiaohongshu.com',
  'Cookie': 'abRequestId=2d1b7cc8-3467-55ef-a9f4-69d820bff81c; a1=1928b966c88qgeirs9l3vbhqbyk0u6mlg7ni7c7t250000186682; webId=c3c8b6ef1e92997d390768ba99d2f553; gid=yjJYDjKWYKkDyjJYDjKKSWSWYYAkd3FMj1qhI9JDxADvT32887K61W888yYKKYJ8W2iJY2KY; web_session=040069b67951dc642cf7eb5e55354ba36200e2; xsecappid=xhs-pc-web; webBuild=4.47.1; acw_tc=0a0b14e217345207714191207e6f5676202ead0753517f37336eed5c9ddd2b; websectiga=cffd9dcea65962b05ab048ac76962acee933d26157113bb213105a116241fa6c; sec_poison_id=fdf716e4-187b-4c9b-9b71-a41d39aa3dd0; unread={%22ub%22:%226753b4ae000000000702a44f%22%2C%22ue%22:%2267594eb3000000000700b62c%22%2C%22uc%22:25}',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
url = 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes'
api_endpoint = '/api/sns/web/v1/search/notes'
a1_value=re.search(r'a1=([^;]+)', headers['Cookie']).group(1)
print(a1_value)


with open('GenXsAndCommon_56.js', 'r', encoding='utf-8') as f:
    js_script = f.read()
    context = execjs.compile(js_script)
    sign = context.call('getXs', api_endpoint, search_data, a1_value)

GREEN = "\033[1;32;40m  %s  \033[0m"

headers['x-s'] = sign['X-s']
headers['x-t'] = str(sign['X-t'])
headers['X-s-common'] = sign['X-s-common']

# print(GREEN % sign)

response = requests.post(url, headers=headers, data=json.dumps(search_data, separators=(",", ":"), ensure_ascii=False).encode('utf-8'))

print(response.status_code)

print(response.headers)

logger.info(f'{response.json()}')
