# !/usr/bin/env python
# -*- coding: utf-8 -*-


import requests                 # 进行网络请求
import xlwt                     # 与excel相关的操作
from lxml import etree          # 引入xpath库，方便定位元素
import time                     # 进行访问频率控制
import random                   # 随机数生成
import re                       # 正则表达式
# 主程序
def main():
    base_url = "https://movie.douban.com/top250?start="     # 最基本的网址，后续会根据这个进行翻页操作
    Savepath = "豆瓣电影.xlsx"                           # 存储路径
    datalist = getdata(base_url)
    savedata(datalist, Savepath)#保存的数据和路径参数

# 获取html源码
def ask_url(url):
    html=""
    # 进行伪装头信息，防止416错误，模拟浏览器头部信息，向豆瓣服务器发送消息(最好加上cookie)
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
    }
    try:
        response = requests.get(url,headers=headers,timeout=10)  # 用户代理，表示告诉豆瓣服务器，我们是什么类型的机器、浏览器（本质上是告诉浏览器，我们可以接收什么水平的文件内容）
        # time.sleep(random.randint(3, 6))           # 每隔3-6s执行一次请求
        html = response.content            # 获取网页的html源代码
        # print("请求访问成功")
    except requests.exceptions.RequestException as e:
        print("超时")
        print(e)
    return html

# 从html源码中获取信息
def getdata(baseurl):
    Datalist = []                                 # 用来存储已经经过处理的信息
    for i in range(0, 10):                     # 在1-10页内爬取豆瓣电影的信息
        url = baseurl+str(i*25)   #这个根据网页的翻页特点 豆瓣电影top250翻页后参数变化是每页的参数乘以25
        data = ask_url(url)                     # 获取到源代码
        data=data.decode('utf-8')
        # 从源代码中提取信息
        if data != "":
            html_data = etree.HTML(data)
            #使用xpath定位到全部要获取的内容   然后在这个里面循环提取
            div_list = html_data.xpath('//div[@class="item"]')
            for item in div_list:
                data_item = []#在循环里面建立一个空的列表存储一个电影的全部数据
                # 电影排名
                movie_rank = item.xpath('div[1]//em//text()')[0]
                data_item.append(movie_rank)
                # 电影名称
                movie_name=item.xpath('div[2]//div[1]//span[@class="title"][1]//text()')[0]
                data_item.append(movie_name)
                #电影评分
                movie_score = item.xpath( 'div[2]//div[2]//div//span[2]//text()')[0]
                data_item.append(movie_score)
                # 电影海报地址
                movie_poster = item.xpath('div//a//@src')[0]
                data_item.append(movie_poster)
                #导演,使用正则，
                movie_director = item.xpath('div[2]//div[2]//p[1]//text()')
                # 这里面是将xpath提取的内容转换为字符串 并且使用strip('\n')函数剔除两边的空格
                movie_director = ''.join(movie_director).strip('\n')
                #使用正则表达式进行抽取匹配的信息 re.S模式是在字符串中可以换行提取
                movie_director = re.findall(r'导演:*? (.*?)\xa0\xa0\xa0主', movie_director, re.S)
                data_item.append(movie_director)
                #评价人数
                movie_estate=item.xpath('div[2]//div[2]//div//span[4]//text()')
                movie_estate=''.join(movie_estate)
                # 这里面是将xpath提取的内容转换为字符串，用正则将 人评价 用 ;这个符号代替 这样提取的就都是数字
                movie_estate=re.sub(r'人评价',';',movie_estate)
                movie_estate=movie_estate.split(';')[0]
                data_item.append(movie_estate)
                #上映时间
                movie_time= item.xpath('div[2]//div[2]//p[1]//text()')
                #同理 这里面是将xpath提取的内容转换为字符串，使用正则提取数字
                movie_time = ''.join(movie_time).strip('\n')
                movie_time = re.findall(r'\d{4}', movie_time)[0]
                data_item.append(movie_time)
                #电影类型
                movie_type = item.xpath('div[2]//div[2]//p[1]//text()')
                # 同理 这里面是将xpath提取的内容转换为字符串，使用正则提取
                movie_type = ''.join(movie_type).strip('\n')
                movie_type = re.findall(r'\d{4}\xa0/\xa0.*\xa0(.*)', movie_type, re.S)
                movie_type = ''.join(movie_type)
                if len(movie_type)==0:
                    movie_type=['无信息']
                else:
                    movie_type=movie_type
                data_item.append(movie_type)
                #主演
                movie_main_actor = item.xpath('div[2]//div[2]//p[1]//text()')
                # 同理 这里面是将xpath提取的内容转换为字符串，使用正则提取
                movie_main_actor = ''.join(movie_main_actor).strip('\n')
                movie_main_actor = re.findall(r'主演:.(.*)\d{4}', movie_main_actor, re.S)
                if len(movie_main_actor) == 0:
                    movie_main_actor = ['无主演信息']
                else:
                    movie_main_actor = movie_main_actor
                movie_main_actor = ''.join(movie_main_actor)
                data_item.append(movie_main_actor)
                # 电影国家
                movie_country = item.xpath('div[2]//div[2]//p[1]//text()')
                # 同理 这里面是将xpath提取的内容转换为字符串，使用正则提取
                movie_country = ''.join(movie_country).strip('\n')
                movie_country = re.findall(r'\d{4}./\xa0(.*?)\xa0/', movie_country, re.S)
                data_item.append(movie_country)
                #电影摘要
                movie_abstract = item.xpath('div[2]//div[2]//p[@class="quote"]//span//text()')
                if len(movie_abstract) == 0:
                    movie_abstract = ['无摘要信息']
                else:
                    movie_abstract = movie_abstract
                data_item.append(movie_abstract)
                Datalist.append(data_item)

    # print(Datalist)
    return Datalist

# 将html获取的信息存入Excel表格中
def savedata(Datalist,Savapath):
    col = ("影片排名","影片名称", "评分","海报地址",'导演',"评价人数",'上映时间','电影类型','主演','影片区域','影片摘要')# Excel的表头 也就是列数
    house_list = xlwt.Workbook(encoding="utf-8", style_compression=0)       # 创建workbook对象
    worksheet = house_list.add_sheet("douban", cell_overwrite_ok=True)   # 新建工作区，设为可覆盖
    for i in range(0, 11):        # 写入表头 一共11列
        worksheet.write(0, i, col[i])   # 写入表头 一共11列
    for i in range(0, 250):        # 写入数据  也就是行数
        print("正在写入第%d条数据" % (i + 1))
        item = Datalist[i]   #获取的数据的索引
        for j in range(0, 11):   #列数
            worksheet.write(i + 1, j, item[j])   #i + 1是从第1行开始写 第0行被表头占用了  item[j]将数据按照数据的索引进行写入
    house_list.save(Savapath)        # 存储

# 程序从这里开始执行
if __name__ == "__main__":
    star_time=time.time()
    main()
    end_time=time.time()
    print("爬取完毕! 一共耗时: %.2f秒"%(end_time-star_time))






