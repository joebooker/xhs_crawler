import time
import urllib.parse
import random
import execjs
import requests
from loguru import logger
import hashlib
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

def get_b3_trace_id():
    re = "abcdef0123456789"
    je = 16
    e = ""
    for t in range(16):
        e += re[random.randint(0, je - 1)]
    return e


import datetime
from typing import List, Dict, Any
import pandas as pd


def parse_sub_comments(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    解析子评论数据，提取指定字段。

    :param data: 包含子评论数据的字典
    :return: 包含解析后子评论信息的列表
    """
    parsed_sub_comments = []

    # 确保数据中有 'data' 和 'comments'
    if 'data' not in data or 'comments' not in data['data']:
        print("无效的数据结构")
        return parsed_sub_comments

    comments = data['data']['comments']

    for comment in comments:
        # 提取基础字段，使用dict.get以避免KeyError
        note_id = comment.get('note_id', '')
        comment_id = comment.get('id', '')
        create_time_ms = comment.get('create_time', 0)
        # 转换时间戳（假设是毫秒级）
        comment_time = datetime.datetime.fromtimestamp(create_time_ms / 1000).strftime(
            '%Y-%m-%d %H:%M:%S') if create_time_ms else ''
        comment_content = comment.get('content', '')

        # 提取图片地址
        pictures = comment.get('pictures', [])
        comment_pictures = []
        for pic in pictures:
            # 根据需要选择合适的URL，这里选择 'url_default' 如果存在
            url = pic.get('url_default') or pic.get('url_pre') or pic.get('url')
            if url:
                comment_pictures.append(url)

        # 提取评论人信息
        user_info = comment.get('user_info', {})
        commenter_nickname = user_info.get('nickname', '')
        commenter_avatar = user_info.get('image', '')
        commenter_id = user_info.get('user_id', '')
        commenter_ip = comment.get('ip_location', '')  # 可能不存在

        # 提取父评论ID
        target_comment = comment.get('target_comment', {})
        parent_comment_id = target_comment.get('id', '')

        # 构建子评论字典
        parsed_sub_comment = {
            'note_id': note_id,
            'comment_id': comment_id,
            'comment_time': comment_time,
            'comment_content': comment_content,
            'comment_pictures': ';'.join(comment_pictures),  # 多张图片用分号分隔
            'commenter_nickname': commenter_nickname,
            'commenter_avatar': commenter_avatar,
            'commenter_ip': commenter_ip,
            'commenter_id': commenter_id,
            'parent_comment_id': parent_comment_id,
            'sub_comment_count': '',
            'sub_comment_cursor': '',
            'sub_comment_has_more': ''
        }
        parsed_sub_comments.append(parsed_sub_comment)

    return parsed_sub_comments


def save_comments_to_table(comments: List[Dict[str, Any]], filename: str = 'sub_comments.csv',
                           file_format: str = 'csv'):
    """
    将解析后的子评论保存到表格文件中。

    :param comments: 解析后的子评论列表
    :param filename: 输出文件名
    :param file_format: 文件格式，支持 'csv' 和 'excel'
    """
    if not comments:
        print("没有子评论数据可保存。")
        return

    # 将列表转换为 pandas DataFrame
    df = pd.DataFrame(comments)

    try:
        if file_format.lower() == 'csv':
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"子评论数据已成功保存到 CSV 文件：{filename}")
        elif file_format.lower() in ['excel', 'xlsx']:
            df.to_excel(filename, index=False, engine='openpyxl')
            print(f"子评论数据已成功保存到 Excel 文件：{filename}")
        else:
            print("不支持的文件格式。请使用 'csv' 或 'excel'。")
    except Exception as e:
        print(f"保存文件时出错：{e}")







url = "https://edith.xiaohongshu.com/api/sns/web/v2/comment/sub/page"
api_endpoint = '/api/sns/web/v2/comment/sub/page'

b3_trace_id=get_b3_trace_id()
params = {
    "note_id": '678a94450000000016019b5d',
    "root_comment_id": '678af44f000000002200ba20',
    "num": 100,
    "cursor": '',
}
params_encoded = api_endpoint + '?' + urllib.parse.urlencode(params)

cookies ={
            "a1":'xxxxxx',
            #………………………………
        }

a1_value=cookies['a1']
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'origin': 'https://www.xiaohongshu.com',
    'priority': 'u=1, i',
    'referer': 'https://www.xiaohongshu.com/',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    "x-b3-traceid": b3_trace_id,
    "x_xray_traceid" :hashlib.md5(b3_trace_id.encode('utf-8')).hexdigest()
}
with open('GenXsAndCommon_56.js', 'r', encoding='utf-8') as f:
    js_script = f.read()
    context = execjs.compile(js_script)
    sign = context.call('getXs', params_encoded, '', a1_value)

headers['x-s'] = sign['X-s']
headers['x-t'] = str(sign['X-t'])
headers['X-s-common'] = sign['X-s-common']

response = requests.get(url, headers=headers, cookies=cookies, params=params)
logger.info(f'{response.json()}')
data=response.json()
cursor = data['data'].get('cursor')
params['cursor']=cursor
logger.info(f'{cursor}')






