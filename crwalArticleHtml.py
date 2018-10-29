#爬取除了热点tag以外其他tag下的文章html
#保存在每个tag的文件夹里

import requests
from requests.exceptions import RequestException
from lxml import etree
from urllib.parse import urljoin 
import re
import os 
import random
import time
import json


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

text = get_html("https://www.chunyuyisheng.com/pc/health_news/",session)

html = etree.HTML(text)
tags = html.xpath('//li[@class="tab-item" or @class="tab-item cur"]/a/@href')

cur_dir = os.getcwd()
dic = {}
for n in range(len(tags)):
    onetagurl = urljoin('https://www.chunyuyisheng.com/pc/health_news/', tags[n])
    #change article dir
    os.chdir(cur_dir)
    folder_name = 'tag' + str(n)
    file_path = os.path.join(cur_dir, folder_name)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    os.chdir(file_path)
        
    pagenumber = 0
    
    while onetagurl :
        tagtext = get_html(onetagurl,session)
        if tagtext :
            pagenumber += 1
            html_tag = etree.HTML(tagtext)
            article_onepage = html_tag.xpath('//div[@class="detail"]/a/@href')
            #get all article in the page 
            for num in range(len(article_onepage)):
                one_article_url = urljoin('https://www.chunyuyisheng.com', article_onepage[num])
                article_text = get_html(one_article_url,session)
                #正则获取链接里的编号
                number = re.search('\d+',article_onepage[num])
                if article_text :
                    #save article html
                    with open(str(number.group())+'.html', 'w') as f:
                        f.write(article_text)
                    #获取相对路径
                    abspath = os.getcwd()
                    rootpath = os.path.abspath('..')
                    absdir = abspath.replace(rootpath, '.', 1)
                    absdir = absdir + '/' + str(number.group())
                    #build dic
                    print(absdir)
                    dic.append({one_article_url:absdir})
            #get next page 
            nextpage = html_tag.xpath('//div[@class="pagebar"]/a[@class="next"]/@href')
            if len(nextpage)== 0 or pagenumber > 30:
                break
            onetagurl = urljoin('https://www.chunyuyisheng.com', nextpage[0])
            #延时等待
            time.sleep(random.randint(1,3))
os.chdir(cur_dir)
with open('index_json.json','w') as json_f:
    json.dump(dic,json_f,ensure_ascii = False)           
    






