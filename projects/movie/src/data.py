"""
Author: Li Rui
Project: Douban Top250 Movie Crawler (Learning Version)
------------------------------------------------------------
本脚本仅用于学习、数据分析与公开网页解析示例。
请遵守目标网站（豆瓣电影）的 robots 协议与服务条款，
避免高频请求或用于商业目的。
------------------------------------------------------------
"""

import requests
from lxml import etree
import csv
import time


# ---------------------- 基本配置 ----------------------
BASE_URL = "https://movie.douban.com/top250"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0"
    )
}
URLS = [f"{BASE_URL}?start={i * 25}&filter=" for i in range(10)]


# ---------------------- 工具函数 ----------------------
def get_first_text(lst):
    """安全地获取列表中第一个非空文本"""
    return lst[0].strip() if lst else ""


def clean_comment(text):
    """清理评论中的换行和空白"""
    return text.replace("\n", "").replace("\r", "").replace("\t", "").strip()


# ---------------------- 主函数 ----------------------
def crawl_douban_top250(output_file="douban_top250.csv"):
    """
    爬取豆瓣 Top250 电影信息（学习版）
    输出字段：
    rank, movie, link, director, year, country, genre,
    score, comment_count, summary, hot_comments
    """
    count = 1

    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "rank",
            "movie",
            "link",
            "director",
            "year",
            "country",
            "genre",
            "score",
            "comment_count",
            "summary",
            "hot_comments",
        ])

        for url in URLS:
            print(f"\n 正在爬取页面: {url}")
            try:
                res = requests.get(url, headers=HEADERS, timeout=10)
                res.raise_for_status()
                html = etree.HTML(res.text)
                movies = html.xpath('//*[@id="content"]/div/div[1]/ol/li')
            except Exception as e:
                print(f"❌ 页面请求失败: {e}")
                continue

            for li in movies:
                # 基础字段
                title = get_first_text(li.xpath("./div/div[2]/div[1]/a/span[1]/text()"))
                src = get_first_text(li.xpath("./div/div[2]/div[1]/a/@href"))
                director = get_first_text(li.xpath("./div/div[2]/div[2]/p[1]/text()"))

                # 第二行信息（年份 / 地区 / 类型）
                year, country, genre = "", "", ""
                p_texts = li.xpath("./div/div[2]/div[2]/p[1]/text()")
                if len(p_texts) > 1:
                    parts = [p.strip() for p in p_texts[1].split("/")]
                    if len(parts) >= 3:
                        year, country, genre = parts[:3]

                # 评分与简介
                score = get_first_text(li.xpath("./div/div[2]/div[2]/div/span[2]/text()"))
                comment_count = get_first_text(li.xpath("./div/div[2]/div[2]/div/span[4]/text()"))
                summary = get_first_text(li.xpath("./div/div[2]/div[2]/p[2]/span/text()"))

                # 详情页热评
                hot_comments = ""
                try:
                    detail_res = requests.get(src, headers=HEADERS, timeout=10)
                    detail_html = etree.HTML(detail_res.text)
                    hot_comments_list = detail_html.xpath(
                        '//*[@id="hot-comments"]//span[@class="short"]/text()'
                    )
                    cleaned = [clean_comment(c) for c in hot_comments_list if clean_comment(c)]
                    hot_comments = " | ".join(cleaned[:5])  # 仅保留前5条热评
                except Exception:
                    hot_comments = ""

                # 写入数据
                writer.writerow([
                    count,
                    title,
                    src,
                    director,
                    year,
                    country,
                    genre,
                    score,
                    comment_count,
                    summary,
                    hot_comments,
                ])

                print(f"已抓取: {count:03d} | {title}")
                count += 1
                time.sleep(0.5)  # 合理访问间隔

    print(f"\n 爬取完成，数据已保存至: {output_file}")


# ---------------------- 程序入口 ----------------------
if __name__ == "__main__":
    crawl_douban_top250()
