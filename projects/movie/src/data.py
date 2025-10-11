#导入模块
import requests#网络请求
from lxml import etree #请求数据解析
import csv
#请求头信息，反爬虫
headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0'}
#功能函数
def get_first_text(list):
    try:
        return list[0].strip()
    except:
        return ""

urls=['https://movie.douban.com/top250?start={}&filter='.format(str(i*25)) for i in range(10)]
count=1
with open("douban_top250.csv",'w',encoding='utf-8',newline='') as f:
    writer=csv.writer(f)
    # 更新列结构，添加年份、地区、类型信息
    writer.writerow(['rank','movie','link','director','year','country','genre','score','comment','summary','hot_comments'])
    for url in urls:
        #print(url)
        print('正在爬取……')
        res = requests.get(url=url, headers=headers)#发起请求
        html = etree.HTML(res.text)
        lis = html.xpath('//*[@id="content"]/div/div[1]/ol/li')
        for li in lis:
            title=get_first_text(li.xpath('./div/div[2]/div[1]/a/span[1]/text()'))
            src=get_first_text(li.xpath('./div/div[2]/div[1]/a/@href'))
            
            # 获取导演+主演信息（第一行）
            director=get_first_text(li.xpath('./div/div[2]/div[2]/p[1]/text()'))
            
            # 获取年份、地区、类型信息（第二行）- 修复br标签问题
            # 获取p[1]中所有文本节点（包括br分隔的）
            p1_texts = li.xpath('./div/div[2]/div[2]/p[1]/text()')
            year,country,genre="","",""
            if len(p1_texts) > 1:#第二行存在,说明有年份、地区、类型信息
                second_line=p1_texts[1]
                parts=[p.strip() for p in second_line.split('/')]
                year=parts[0]
                country=parts[1]
                genre=parts[2]
            else:
                print("年份、地区、类型信息获取失败")
            
            score=get_first_text(li.xpath('./div/div[2]/div[2]/div/span[2]/text()'))
            comment=get_first_text(li.xpath('./div/div[2]/div[2]/div/span[4]/text()'))
            summary=get_first_text(li.xpath('./div/div[2]/div[2]/p[2]/span/text()'))
            
            try:
                detail_res = requests.get(src, headers=headers, timeout=10)
                detail_html = etree.HTML(detail_res.text)
                hot_comments_list = detail_html.xpath('//*[@id="hot-comments"]//span[@class="short"]/text()')
                # 去除每条热评中的换行和多余空格
                def clean_comment(c):
                    return c.replace('\n', '').replace('\r', '').replace('\t', '').strip()
                hot_comments = " | ".join([clean_comment(c) for c in hot_comments_list if clean_comment(c)])
            except Exception as e:
                print(f"爬取热评失败: {e}")

            # 调试输出
            print(f"电影: {title}")
            print(f"  导演行: {director}")
            print(f"  信息行: {second_line}")
            print(f"  解析结果: 年份={year}, 地区={country}, 类型={genre}")
            print(f"热评：{hot_comments}")
            print("-" * 50)
            writer.writerow([count,title,src,director,year,country,genre,score,comment,summary,hot_comments])
            count+=1
print('数据保存在douban_top250.csv')
