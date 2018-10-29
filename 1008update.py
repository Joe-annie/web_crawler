#根据上一个json文件的最新文章作为结束条件
#爬取增量的文章和文章标签，文章html保存在一个文件夹里，标签写在json里


import requests
from requests.exceptions import RequestException
from lxml import etree
from urllib.parse import urljoin 
import re
import os 
import random
import time
import json

def getTime(time):
    #如果是“几小时前”，使用当前时间
    if "小时" in time:
        time = time.strftime("%m%d", time.localtime())
    return time 

def get_html(url, session):
    try:        
        r = session.get(url,headers = headers)
        if r.status_code == 200:
            return r.text
        return None
    except RequestException:
        return None

#上一个文件的json，用来排除重复的文章
with open("update_ch.json","r") as load_f:
    dic_json = json.load(load_f)

number_list = dic_json.keys()
num_list = list(number_list)

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
session = requests.Session()

onetagurl = "https://www.chunyuyisheng.com/pc/health_news/"
pagenumber = 0

end_page = 0
firstFlag = 0
latest_time = ""
end_time = ""

dic_json = {}
cur_dir = os.getcwd()

while onetagurl:
    tagtext = get_html(onetagurl,session)
    if tagtext :
        pagenumber += 1
        html_tag = etree.HTML(tagtext)
        article_onepage = html_tag.xpath('//div[@class="detail"]/a/@href')
        #get all article in the page 
        for index,num in enumerate(article_onepage):
            one_article_url = urljoin('https://www.chunyuyisheng.com', num)
            article_text = get_html(one_article_url,session)
            
            number = re.search('\d+',num)
            number_str = str(number.group())
            #终止循环条件#从上一个文件名获取时间，最后一篇文章编号
            filename = '.json'#填写上一个文件名
            end_time = filename[-4:] 
            with open(filename,"r") as load_f:
                dic = json.load(load_f)
            keylist = list(dic.keys())
            if number_str == keylist[0]:
                print("end")
                end_page = 1
                break
            if number_str in num_list: continue
            
            if article_text :
                #标记第一个文章,获取最新时间
                if not firstFlag:
                    time = article_text.xpath('//p[@class="time"]/text()')
                    latest_time = getTime(time[0])
                    firstFlag = 1
                #获取相对路径
                abspath = os.getcwd()
                rootpath = os.path.abspath('..')
                absdir = abspath.replace(rootpath, '.', 1)
                absdir = absdir + '/' + number_str
                print(absdir)
                #get tag context
                tag_url = "https://www.chunyuyisheng.com/pc/medical_keywords/?id=" + number_str + "&type=n"
                print(tag_url)
                time.sleep(random.randint(1,3))
                text = get_html(tag_url,session)
                if not text: #guard for no content
                    print("find none tag ") 
                    break
                text = text.encode('latin-1').decode('unicode_escape')
                #build dic
                dic_attr = {"path" : absdir, "tag": text}
                dic = {number_str : dic_attr}
                dic_json.update(dic)
                #save article html
                folder_name = 'tag' + latest_time +'update'
                file_path = os.path.join(cur_dir, folder_name)
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                os.chdir(file_path)
                with open(number_str+".html", 'w') as f:
                    f.write(article_text)
    #get next page
    if end_page :break
    nextpage = html_tag.xpath('//div[@class="pagebar"]/a[@class="next"]/@href')        
    onetagurl = urljoin('https://www.chunyuyisheng.com', nextpage[0])
    #延时等待
    time.sleep(random.randint(1,3))
os.chdir(cur_dir)
name = latest_time+'_'+end_time+'.json'
with open(name,'w') as json_f:
    json.dump(dic_json,json_f,ensure_ascii = False)           
    






