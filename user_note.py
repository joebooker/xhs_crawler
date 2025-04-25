import time
import execjs
import urllib.parse
from loguru import logger
import pandas as pd
import os
import requests
import re
import csv
from datetime import datetime
import json
import random

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
def parse_cookies_list(cookies_list):
    result = []
    for cookie_str in cookies_list:
        cookie_dict = {}
        pairs = cookie_str.split(";")
        for pair in pairs:
            if "=" in pair:
                key, value = pair.split("=", 1)
                cookie_dict[key.strip()] = value.strip()
        result.append(cookie_dict)
    return result
def fetch_xiaohongshu_data(source_note_id, xsec_token,cookies):
    url = "https://edith.xiaohongshu.com/api/sns/web/v1/feed"
    api_endpoint = '/api/sns/web/v1/feed'



    data = {
        "source_note_id": source_note_id,
        "image_formats": ["jpg", "webp", "avif"],
        "extra": {"need_body_topic": "1"},
        "xsec_source": "pc_feed",
        "xsec_token": xsec_token
    }
    a1_value =cookies['a1']
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
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "x-b3-traceid": "9cbac8e2b8562aa3"
    }

    # Load the JavaScript file and compile the getXs function
    with open('GenXsAndCommon_56.js', 'r', encoding='utf-8') as f:
        js_script = f.read()
        context = execjs.compile(js_script)
        sign = context.call('getXs', api_endpoint, data, a1_value)

    # logger.info(f'Sign generated: {sign}')
    headers['x-s'] = sign['X-s']
    headers['x-t'] = str(sign['X-t'])

    # Send the request
    data_json = json.dumps(data, separators=(',', ':'))
    time.sleep(0.5)
    response = requests.post(url, headers=headers, cookies=cookies, data=data_json)

    return response.json(),response.status_code,response.headers
def convert_scientific_time(time_str):
    timestamp = float(time_str)
    timestamp_in_seconds = timestamp / 1000
    readable_time = datetime.fromtimestamp(timestamp_in_seconds).strftime('%Y年%m月%d日 %H:%M:%S')
    return readable_time

def parse_data(data, filename='博主信息', xsec_token=0):
    fieldnames = [
        "笔记id", "xsec_token","笔记链接","笔记类型", "笔记标题", "笔记正文", "笔记标签",
        "发布时间", "笔记最后更新时间", "图片链接", "点赞数", "收藏数",
        "评论数", "分享数", "用户名", "用户id", "用户ip", "用户头像"
    ]
    file_name = f"{filename}.csv"
    file_exists = os.path.isfile(file_name)

    with open(file_name, mode='a', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        item = data['data']['items'][0]
        note_card = item['note_card']
        note_id = item["id"]
        note_url = 'https://www.xiaohongshu.com/explore/' + note_id + '?xsec_token=' + xsec_token + '&xsec_source=pc_feed'
        note_type = item["model_type"]
        desc = note_card.get("desc", "")
        tags = re.findall(r"#([^#]+?)(?=\[话题\])", desc)
        tags = ", ".join(tags)
        interact_info = note_card.get("interact_info", {})
        publish_time = note_card.get("time")
        title = note_card.get("title", "")
        user_info = note_card.get("user", {})
        user_avatar = user_info.get("avatar", "")
        user_name = user_info.get('nickname', '')
        user_id = user_info.get('user_id', '')
        last_updated_time = note_card.get("last_update_time", "")
        like_count = interact_info.get("liked_count", 0)
        collect_count = interact_info.get("collected_count", 0)
        comment_count = interact_info.get("comment_count", 0)
        share_count = interact_info.get("share_count", 0)
        ip = note_card.get("ip_location", "")
        image_url = ""
        if note_card.get("image_list"):
            image_url = note_card["image_list"][0]["info_list"][0]["url"]

        writer.writerow({
            "笔记id": note_id,
            "笔记链接":note_url,
            "xsec_token":xsec_token,
            "笔记类型": note_type,
            "笔记标题": title,
            "笔记正文": desc,
            "笔记标签": tags,
            "发布时间": convert_scientific_time(publish_time),
            "笔记最后更新时间": convert_scientific_time(last_updated_time),
            "图片链接": image_url,
            "点赞数": convert_to_int(like_count),
            "收藏数": convert_to_int(collect_count),
            "评论数": convert_to_int(comment_count),
            "分享数": convert_to_int(share_count),
            "用户名": user_name,
            "用户id": user_id,
            "用户ip": ip,
            "用户头像": user_avatar
        })
    return note_id,user_id
def convert_to_int(value):
    if '万' in value:
        value = value.replace('万', '')
        return float(value) * 10000  # 转换为万单位的整数
    else:
        return value

def download_img(data, user_id, note_id):
    image_list = data["data"]["items"][0]["note_card"]["image_list"]
    image_urls = [img["url_default"] for img in image_list]
    output_dir = os.path.join("images", user_id, note_id)
    os.makedirs(output_dir, exist_ok=True)
    for idx, url in enumerate(image_urls):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(os.path.join(output_dir, f"image_{idx + 1}.jpg"), "wb") as f:
                    f.write(response.content)
                    logger.info(f"图片下载成功: {os.path.join(output_dir, f'image_{idx + 1}.jpg')}")
        except Exception as e:
            logger.error(f"图片下载出错: {e}")
def update_headers(api, data, current_cookies):
        with open('GenXsAndCommon_56.js', 'r', encoding='utf-8') as f:
            js_script = f.read()
            context = execjs.compile(js_script)
            sign = context.call('getXs', api, data, current_cookies['a1'])
        return sign
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.xiaohongshu.com/',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'x-b3-traceid': '703a524e5c541b60',
    'x-xray-traceid': 'ca3cd4476912fa7a1e48bcdb111afd67',
}
def main(file_path, file_name, cookies_list, is_download=False):
    data = pd.read_excel(file_path)
    user_ids=['6349f363000000001901c850']
    url = "https://edith.xiaohongshu.com/api/sns/web/v1/user_posted"
    person_index=0

    for user_id in user_ids:
        has_more = True
        print(f'正在爬取第{person_index}个人 {user_id} 的帖子信息')
        params = {
            "num": "30",
            "cursor": "",
            "user_id": user_id,
            "image_formats": "jpg,webp,avif",
            "xsec_token": "",
            "xsec_source": "pc_note"
        }
        k = 0
        current_cookie_index = 0
        
        while has_more:
            try:
                current_cookies = cookies_list[current_cookie_index]
                params_encoded = urllib.parse.urlencode(params)
                sign_headers = update_headers(f'/api/sns/web/v1/user_posted?{params_encoded}', None, current_cookies)
                headers['x-s'] = sign_headers['X-s']
                headers['x-t'] = str(sign_headers['X-t'])
                response1 = requests.get(url, headers=headers, cookies=current_cookies, params=params)
                
                if response1.status_code == 200 and response1.json().get('success') == True:
                    data = response1.json()
                    notes = data.get('data', {}).get('notes', [])
                    has_more = data.get('data', {}).get('has_more', False)
                    cursor = data.get('data', {}).get('cursor', None)
                    
                    if cursor:
                        params['cursor'] = cursor
                        logger.info(f"成功更新 cursor 为: {cursor}")
                    else:
                        has_more = False
                        logger.info("未返回 cursor，结束分页")
                    
                    note_index = 0
                    while note_index < len(notes):
                        note = notes[note_index]
                        logger.info(f'正在爬取第{person_index}个人的第{k}个帖子')
                        
                        xsec_token = note.get('xsec_token')
                        note_id = note.get('note_id')
                        
                        while True:  # 循环尝试直到成功获取笔记数据
                            current_cookies = cookies_list[current_cookie_index]
                            note_data, status_code_result, headers_result = fetch_xiaohongshu_data(note_id, xsec_token, current_cookies)
                            
                            if status_code_result == 200:
                                if note_data.get('success') == True:
                                    # 成功获取数据，处理并继续下一个笔记
                                    note_id, user_id_1 = parse_data(note_data, file_name, xsec_token)
                                    if is_download:
                                        download_img(note_data, user_id_1, note_id)
                                    k += 1
                                    note_index += 1
                                    break  # 跳出重试循环
                                else:
                                    # Cookie失效，切换到下一个
                                    logger.warning('Cookie失效，切换到下一个')
                                    current_cookie_index = (current_cookie_index + 1) % len(cookies_list)
                                    if current_cookie_index == 0:
                                        time.sleep(1)  # 所有cookie都试过一遍，暂停一下
                            else:
                                logger.error(f'请求失败，状态码: {status_code_result}')
                                current_cookie_index = (current_cookie_index + 1) % len(cookies_list)
                                if current_cookie_index == 0:
                                    time.sleep(1)
                            
                            time.sleep(0.5)  # 请求间隔
                            
                else:
                    # 分页请求失败，切换cookie重试
                    print(response1.json())
                    logger.warning('分页请求失败，切换cookie重试')
                    current_cookie_index = (current_cookie_index + 1) % len(cookies_list)
                    if current_cookie_index == 0:
                        time.sleep(1)
                    continue
                    
            except Exception as e:
                logger.error(f"发生错误: {str(e)}")
                current_cookie_index = (current_cookie_index + 1) % len(cookies_list)
                if current_cookie_index == 0:
                    time.sleep(1)
                continue
        
        person_index += 1
        logger.info(f'用户{user_id}的笔记已经爬完')
    
    logger.info("所有用户数据处理完毕")

if __name__ == '__main__':
    file_path='博主id.xlsx'
    cookies_list_original = [
        'web复制下来的cookie'
    ]
    cookies_list = parse_cookies_list(cookies_list_original)
    is_download=True
    file_name = 'filename'
    main(file_path,file_name,cookies_list,is_download)
