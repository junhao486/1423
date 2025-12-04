import requests
import re
from bs4 import BeautifulSoup

# 设置代理
proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890',
}

# 测试URL，使用用户提供的接口
keyword = "成都"
url = f"https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&rsv_dl=ns_pc&word={keyword}"

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0'
}

# 获取页面内容
try:
    response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
    response.raise_for_status()
    html = response.text
    print("成功获取页面内容")
    
    # 保存完整HTML到文件
    with open('full_page.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("页面内容已保存到full_page.html")
    
    # 1. 检查content_left容器
    print("\n1. 检查content_left容器：")
    content_left_match = re.search(r'<div[^>]*id=["\']content_left["\'][^>]*>(.*?)</div>', html, re.DOTALL)
    if content_left_match:
        content_left = content_left_match.group(1)
        print(f"content_left容器内容长度: {len(content_left)}")
        
        # 保存content_left内容到文件
        with open('content_left.html', 'w', encoding='utf-8') as f:
            f.write(content_left)
        print("content_left内容已保存到content_left.html")
        
        # 查找h3标签
        h3_tags = re.findall(r'<h3[^>]*>.*?</h3>', content_left, re.DOTALL)
        print(f"content_left中的h3标签数量: {len(h3_tags)}")
        
        # 查找所有的a标签
        a_tags = re.findall(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*class=["\'].*?news-title-font_1xS-F.*?["\'][^>]*>(.*?)</a>', content_left, re.DOTALL)
        print(f"content_left中包含news-title-font_1xS-F的a标签数量: {len(a_tags)}")
    else:
        print("未找到content_left容器")
    
    # 2. 直接在整个HTML中查找
    print("\n2. 直接在整个HTML中查找：")
    all_h3_tags = re.findall(r'<h3[^>]*>.*?</h3>', html, re.DOTALL)
    print(f"整个HTML中的h3标签数量: {len(all_h3_tags)}")
    
    all_a_tags = re.findall(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*class=["\'].*?news-title-font_1xS-F.*?["\'][^>]*>(.*?)</a>', html, re.DOTALL)
    print(f"整个HTML中包含news-title-font_1xS-F的a标签数量: {len(all_a_tags)}")
    
    # 3. 使用BeautifulSoup分析
    print("\n3. 使用BeautifulSoup分析：")
    soup = BeautifulSoup(html, 'lxml')
    
    # 查找所有包含news-title-font_1xS-F的a标签
    news_links = soup.find_all('a', class_='news-title-font_1xS-F')
    print(f"BeautifulSoup找到的新闻链接数量: {len(news_links)}")
    
    if news_links:
        print("\n前3个新闻链接的信息：")
        for i, link in enumerate(news_links[:3]):
            print(f"\n链接{i+1}:")
            print(f"  标题: {link.get_text(strip=True)}")
            print(f"  URL: {link.get('href')}")
            
            # 查看链接的父元素
            parent = link.parent
            print(f"  父元素: {parent.name}")
            print(f"  父元素class: {parent.get('class')}")
            
            # 查看父元素的父元素
            grandparent = parent.parent
            print(f"  祖父元素: {grandparent.name}")
            print(f"  祖父元素class: {grandparent.get('class')}")
            print(f"  祖父元素id: {grandparent.get('id')}")
            
            # 尝试找到来源和时间信息
            source_time = grandparent.find_next('span', class_='c-color-gray2')
            if source_time:
                print(f"  来源和时间: {source_time.get_text(strip=True)}")
            
            # 尝试找到摘要信息
            summary = grandparent.find_next('span', class_='content-title')
            if summary:
                print(f"  摘要: {summary.get_text(strip=True)}")
                
except Exception as e:
    print(f"获取页面内容失败: {e}")
    import traceback
    traceback.print_exc()