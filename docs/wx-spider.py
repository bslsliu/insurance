# -*- coding: UTF-8 -*-
import json
from datetime import datetime
import pandas as pd  
import requests
import time
import pandas as pd
import random

user_agent_list = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Mobile Safari/537.36",
]

# 目标url
url = "https://mp.weixin.qq.com/cgi-bin/appmsgpublish?sub=list&search_field=null&count=40&query=&fakeid=MzI4MDMyNDIxMQ%3D%3D&type=101_1&free_publish_type=1&sub_action=list_ex&token=1584776117&lang=zh_CN&f=json&ajax=1&begin="
cookie = "appmsglist_action_3593980043=card; pgv_pvid=1751427834676244; poc_sid=HMu6nGajyVbOTPiRHJcwvxV7BH8-LhEnCWPDXHEJ; ua_id=i5QBaDdl5SuMoqeNAAAAAG6mkmkGk2bH1SmnL_L0Grs=; wxuin=21549523767367; mm_lang=zh_CN; rand_info=CAESIAMZLoVLT8jUiuR1IC8Sf940owaxd5sUI9jgvbat4ZhC; slave_bizuin=3593980043; data_bizuin=3593980043; bizuin=3593980043; data_ticket=QRlPX6UNjACSKiwSsQK17216hj2fPI2NxJoI++xe9YsuOcQIA688Et9k5fD7WUUx; slave_sid=SExNQUhCT3dIdzRZaWVNNm90X2NhU2x0QnlOaEc3RjNGQTF2dndGbEZhb2pMNXlXZXp5eWZRdXNXOHNUMDFaazN6S04yNjd5RXhPMW5yYVc3N1RDRnROTU5VUkZiZXdYNnRwTG5WNmdDRlVlQW1CdE13aHF5QWpkdm9NTkpTSGFHME1yekNxYzh3ZFF0Rjho; slave_user=gh_b418f6d11509; xid=3178d39ae62ca0e8e20023936974ee5b; _clck=3593980043|1|fnp|0; pac_uid=0_ZFDWHZMN9tQaF; _qimei_uuid42=18717162818100031ea8b97752b561c350223c802c; suid=0_ZFDWHZMN9tQaF; current-city-name=bj; _qimei_fingerprint=0deb14bd418639462eaae1f6779f4820; _qimei_q36=; _qimei_h38=39680b551ea8b97752b561c302000002b18717; _clsk=fn3ix1|1721745682573|3|1|mp.weixin.qq.com/weheat-agent/payload/record"

# 使用Cookie，跳过登陆操作
offset = 1184
content_list = []
content_json={}
try :
  while offset <= 1759:
    user_agent = random.choice(user_agent_list)
    headers = {
        "Cookie": cookie,
        "User-Agent": user_agent,
    }
    real_url = url + str(offset)
    content_json = requests.get(real_url, headers=headers).json()
    print ("进度条: ",offset)
    reso2 = json.loads(content_json["publish_page"])
    seconds = random.randint(1, 5)
    time.sleep(seconds)
    print(reso2["total_count"])
    content_start_len = len(content_list)
    for itm in reso2["publish_list"]:
      if itm['publish_info']!="":
        publish_info = json.loads(itm['publish_info'])
        for line in publish_info['appmsgex']:
          formatted_time = datetime.fromtimestamp(line["update_time"]).strftime('%Y-%m-%d %H:%M:%S')
          items = []
          items.append(formatted_time)
          items.append(line["title"])
          items.append(line["digest"])
          items.append(line["link"])
          content_list.append(items)
      else:
        print(itm['publish_info'])
    print ("数组大小：",len(content_list))
    offset = offset+len(content_list)-content_start_len
    if len(content_list)-content_start_len ==0:
      print("抓取结果为空")
      break
finally :
  name = ['time', 'title', 'digest', 'link']
  test = pd.DataFrame(columns=name, data=content_list)
  test.to_excel("dajiatouzibiji.xlsx")
  print("最后一次保存成功")