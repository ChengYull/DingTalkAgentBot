"""
CNMO新闻爬虫 Demo
爬取 https://phone.cnmo.com/news/ 网站的新闻内容
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime
from typing import List, Dict, Optional


class CNMONewsScraper:
    """CNMO新闻爬虫类"""

    def __init__(self, base_url: str = "https://phone.cnmo.com"):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_page_content(self, url: str) -> Optional[str]:
        """获取页面内容"""
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                return response.text
            else:
                print(f"请求失败: {url}, 状态码: {response.status_code}")
                return None
        except Exception as e:
            print(f"请求异常: {url}, 错误: {e}")
            return None

    def parse_news_list(self, html: str) -> List[Dict]:
        """解析新闻列表页面，提取新闻链接"""
        soup = BeautifulSoup(html, 'html.parser')
        news_list = []

        # 方法1: 通过正则表达式查找所有包含 news/\d{6}.html 的链接
        # 支持完整URL和相对路径
        all_links = soup.find_all('a', href=re.compile(r'(/news/\d{6}\.html|https?://[^/]+/news/\d{6}\.html)'))

        seen_urls = set()
        for link in all_links:
            href = link.get('href', '')
            title = link.get('title', '') or link.get_text(strip=True)

            # 确保是phone.cnmo.com的新闻链接
            if 'phone.cnmo.com/news/' in href and href not in seen_urls:
                seen_urls.add(href)
                if title and len(title) > 5:  # 过滤短标题
                    news_list.append({
                        'url': href,
                        'title': title
                    })

        # 方法2: 如果没找到，尝试查找所有a标签中的链接
        if not news_list:
            all_a = soup.find_all('a')
            for a in all_a:
                href = a.get('href', '')
                title = a.get('title', '') or a.get_text(strip=True)
                # 匹配 phone.cnmo.com/news/数字.html 格式
                if re.search(r'phone\.cnmo\.com/news/\d{6}\.html', href):
                    if href not in seen_urls:
                        seen_urls.add(href)
                        if title and len(title) > 5:
                            news_list.append({
                                'url': href,
                                'title': title
                            })

        return news_list

    def parse_news_detail(self, html: str, url: str) -> Optional[Dict]:
        """解析新闻详情页面"""
        soup = BeautifulSoup(html, 'html.parser')

        # 提取标题
        title = ""
        title_elem = soup.find('h1') or soup.find('strong', class_='article_title') or soup.select_one('.title h1')
        if title_elem:
            title = title_elem.get_text(strip=True)

        if not title:
            # 尝试从meta标签获取
            meta_title = soup.find('meta', property='og:title')
            if meta_title:
                title = meta_title.get('content', '')

        # 提取作者
        author = ""
        author_elem = soup.find('span', class_='author') or soup.find('a', class_='author')
        if author_elem:
            author = author_elem.get_text(strip=True)
        else:
            # 尝试匹配"作者：xxx"模式
            author_match = re.search(r'作者[：:]\s*(\S+)', html)
            if author_match:
                author = author_match.group(1)

        # 提取发布时间
        publish_time = ""
        time_elem = soup.find('span', class_='time') or soup.find('span', class_='date')
        if time_elem:
            publish_time = time_elem.get_text(strip=True)
        else:
            # 尝试匹配日期模式
            time_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})', html)
            if time_match:
                publish_time = time_match.group(1)

        # 提取正文内容
        content = ""
        content_elem = soup.find('div', class_='content') or soup.find('div', class_='article-content')
        if content_elem:
            # 移除script和style标签
            for tag in content_elem.find_all(['script', 'style', 'iframe']):
                tag.decompose()
            content = content_elem.get_text(separator='\n', strip=True)

        if not content:
            # 尝试查找所有p标签作为正文
            paragraphs = soup.find_all('p')
            content_parts = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 20:  # 过滤短段落
                    content_parts.append(text)
            content = '\n\n'.join(content_parts)

        # 提取来源
        source = "手机中国"
        source_elem = soup.find('span', class_='source')
        if source_elem:
            source = source_elem.get_text(strip=True)

        # 提取图片
        images = []
        img_elems = soup.find_all('img')
        for img in img_elems:
            src = img.get('src') or img.get('data-src')
            if src and src.startswith('http'):
                images.append(src)

        return {
            'title': title,
            'author': author,
            'publish_time': publish_time,
            'source': source,
            'content': content,
            'url': url,
            'images': images[:5]  # 只保留前5张图片
        }

    def scrape_news_list(self, page: int = 1) -> List[Dict]:
        """爬取新闻列表"""
        if page == 1:
            url = f"{self.base_url}/news/"
        else:
            url = f"{self.base_url}/news/{page}/"

        print(f"正在获取新闻列表: {url}")
        html = self.get_page_content(url)

        if html:
            return self.parse_news_list(html)
        return []

    def scrape_news_detail(self, url: str) -> Optional[Dict]:
        """爬取新闻详情"""
        print(f"正在获取详情: {url}")
        html = self.get_page_content(url)

        if html:
            return self.parse_news_detail(html, url)
        return None

    def scrape_batch(self, max_news: int = 5, delay: float = 1.0) -> List[Dict]:
        """批量爬取新闻"""
        results = []

        # 1. 获取新闻列表
        news_list = self.scrape_news_list(page=1)
        print(f"找到 {len(news_list)} 条新闻链接")

        # 2. 爬取每个新闻详情
        for i, news in enumerate(news_list[:max_news]):
            print(f"\n[{i+1}/{min(max_news, len(news_list))}] 正在爬取...")

            detail = self.scrape_news_detail(news['url'])
            if detail and detail.get('title'):
                detail['list_title'] = news['title']  # 保留列表页的标题
                results.append(detail)
                print(f"  标题: {detail['title'][:50]}...")
                print(f"  时间: {detail['publish_time']}")
                print(f"  作者: {detail['author']}")
            else:
                print(f"  解析失败或内容为空")

            time.sleep(delay)  # 礼貌性延迟

        return results

    def save_to_json(self, data: List[Dict], filename: str = "cnmo_news.json"):
        """保存到JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n数据已保存到 {filename}")


def main():
    """主函数"""
    print("=" * 60)
    print("CNMO新闻爬虫 Demo")
    print("=" * 60)

    scraper = CNMONewsScraper()

    # 测试1: 爬取新闻列表
    print("\n【测试1】爬取新闻列表...")
    news_list = scraper.scrape_news_list(page=1)
    print(f"成功获取 {len(news_list)} 条新闻链接")

    # 显示前5条
    print("\n前5条新闻:")
    for i, news in enumerate(news_list[:5]):
        print(f"  {i+1}. {news['title'][:60]}...")
        print(f"     URL: {news['url']}")

    # 测试2: 爬取具体新闻详情
    if news_list:
        print("\n【测试2】爬取新闻详情...")
        test_url = news_list[0]['url']
        detail = scraper.scrape_news_detail(test_url)

        if detail:
            print(f"\n新闻标题: {detail['title']}")
            print(f"新闻来源: {detail['source']}")
            print(f"发布时间: {detail['publish_time']}")
            print(f"作者: {detail['author']}")
            print(f"URL: {detail['url']}")
            print(f"\n正文预览 (前500字):")
            print("-" * 40)
            print(detail['content'][:500] if detail['content'] else "无正文内容")
            print("-" * 40)
            if detail['images']:
                print(f"\n图片数量: {len(detail['images'])}")
        else:
            print("详情页爬取失败")

    # 测试3: 批量爬取
    print("\n【测试3】批量爬取5条新闻...")
    results = scraper.scrape_batch(max_news=5, delay=0.5)

    if results:
        print(f"\n成功爬取 {len(results)} 条新闻")
        scraper.save_to_json(results)

        # 显示摘要
        print("\n爬取结果摘要:")
        for i, news in enumerate(results):
            print(f"\n{i+1}. {news['title']}")
            print(f"   时间: {news['publish_time']} | 作者: {news['author']}")
            content_preview = news['content'][:100] if news['content'] else "无"
            print(f"   内容: {content_preview}...")
    else:
        print("批量爬取失败")

    print("\n" + "=" * 60)
    print("爬虫测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
