#单独爬取文章标签，添加到json中

import os 
import requests
from requests.exceptions import RequestException
import random
import time
import json 
import re


headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
session = requests.Session()
def get_html(url, session):
    try:        
        r = session.get(url,headers = headers)
        if r.status_code == 200:
            return r.text
        return None
    except RequestException:
        return None

dic_json = {}
with  open("index_json.txt","r") as load_f:#未保存标签的json
    load_list = json.load(load_f)
for value in load_list:
    url_type = value.keys()
    for url in url_type:
        article_number = re.search('\d+',url)
        path = value[url]
        #get tag context
        tag_url = "https://www.chunyuyisheng.com/pc/medical_keywords/?id=" + str(article_number.group()) + "&type=n"
        print(tag_url)
        time.sleep(random.randint(1,3))
        text = get_html(tag_url,session)
        if not text: 
            print("find none tag ") 
            break
        dic_attr = {"path" : path, "tag": text}
        dic = {str(article_number.group()) : dic_attr}
        dic_json.update(dic)
with open('update.json','w') as json_f:
    json.dump(dic_json,json_f,ensure_ascii = False) 