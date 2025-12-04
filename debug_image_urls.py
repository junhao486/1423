import requests
from bs4 import BeautifulSoup
import re

# 爬取百度新闻搜索页面
def crawl_baidu_news_page(keyword, page=1):
    # 构建搜索URL
    url = f"https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&word={keyword}&pn={(page-1)*10}"
    print(f"\n正在爬取: {url}")
    
    # 设置请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = "utf-8"
        return response.text
    except Exception as e:
        print(f"爬取失败: {e}")
        return None

# 解析页面并查看整体结构
def parse_page_structure(html_content):
    if not html_content:
        return
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 查看所有div标签及其类名
    all_divs = soup.find_all('div')
    print(f"\n找到 {len(all_divs)} 个div标签")
    
    # 统计最常见的类名
    class_counts = {}
    for div in all_divs:
        classes = div.get('class', [])
        for cls in classes:
            if cls in class_counts:
                class_counts[cls] += 1
            else:
                class_counts[cls] = 1
    
    # 显示前20个最常见的类名
    sorted_classes = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    print("\n最常见的div类名:")
    for cls, count in sorted_classes:
        print(f"  {cls}: {count} 次")
    
    # 尝试查找包含新闻的容器
    print("\n尝试查找新闻容器...")
    
    # 方法1: 查找包含"新闻"或"article"的类名
    news_containers = []
    for div in all_divs:
        classes = div.get('class', [])
        text = div.get_text(strip=True)
        if any('news' in cls.lower() or 'article' in cls.lower() or 'result' in cls.lower() for cls in classes):
            news_containers.append(div)
    
    print(f"找到 {len(news_containers)} 个可能的新闻容器")
    
    # 查看前3个容器的结构
    for i, container in enumerate(news_containers[:3]):
        print(f"\n=== 容器 {i+1} ===")
        print(f"类名: {container.get('class', [])}")
        print(f"内容预览: {container.get_text(strip=True)[:100]}...")
        
        # 查看其中的img标签
        imgs = container.find_all('img')
        print(f"包含 {len(imgs)} 个图片标签")
        for img in imgs[:2]:  # 只显示前2个图片
            print(f"图片: {img}")
            print(f"  src: {img.get('src', '')}")
            print(f"  data-src: {img.get('data-src', '')}")

if __name__ == "__main__":
    # 爬取测试页面
    html = crawl_baidu_news_page('test', page=1)
    
    if html:
        # 保存HTML到文件，方便查看
        with open('baidu_news.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("\nHTML已保存到 baidu_news.html")
    
    # 解析页面结构
    parse_page_structure(html)