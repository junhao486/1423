import requests
import re
import json

# 设置请求头
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'connection': 'keep-alive',
    'cookie': 'H_WISE_SIDS_BFESS=60948_61006_60941_61027_61024_61036_61055; PSTM=1764750645; BD_UPN=12314753; BIDUPSID=EE83CC6FD339D0BBDE315CEA688E7F9C; delPer=0; BD_CK_SAM=1; PSINO=6; BA_HECTOR=8004212g80852h8584258h2kal24ai1kj1pg325; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; ZFY=aP7D:BM8BB6lh0UD3zSnu:AU2Mv:BWcAD1epinTxuNSYCo:C; channel=bing; baikeVisitId=d48e3324-e0d8-4b9d-ad50-1f1a2f2423a1; BAIDUID=2D541012EC0AD6842A55BAE632418223:FG=1; H_WISE_SIDS=63143_66096_66109_66206_66227_66292_66264_66393_66515_66529_66555_66578_66587_66590_66601_66614_66652_66663_66682_66673_66670_66692_66707_66712_66719_66742_66625_66776_66792_66800; BAIDUID_BFESS=2D541012EC0AD6842A55BAE632418223:FG=1; BDRCVFR[I1GM4qgEDat]=-_EV5wtlMr0mh-8uz4WUvY; H_PS_PSSID=63143_66096_66109_66206_66227_66292_66264_66393_66515_66529_66555_66578_66587_66590_66601_66614_66652_66663_66682_66673_66670_66692_66707_66712_66719_66742_66625_66776_66792_66800; BD_HOME=1; BDRCVFR[C0p6oIjvx-c]=mbxnW11j9Dfmh7GuZR8mvqV; arialoadData=false; BDSVRTM=450',
    'host': 'www.baidu.com',
    'sec-ch-ua': '"Chromium";v="142", "Microsoft Edge";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0'
}

# 测试URL
keyword = '成都'
url = f"https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&rsv_dl=ns_pc&word={keyword}&pn=0"

print(f"正在请求URL: {url}")

# 发送请求
try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    response.encoding = 'utf-8'
    html = response.text
    
    print(f"响应状态码: {response.status_code}")
    print(f"HTML内容长度: {len(html)} 字符")
    
    # 保存HTML到文件以便分析
    with open('baidu_news_analysis.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("HTML内容已保存到 baidu_news_analysis.html")
    
    # 分析页面结构
    print("\n=== 页面结构分析 ===")
    
    # 查找所有h3标签
    h3_tags = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.DOTALL)
    print(f"找到 {len(h3_tags)} 个h3标签")
    
    if h3_tags:
        print("\n前3个h3标签内容:")
        for i, tag in enumerate(h3_tags[:3], 1):
            print(f"{i}. {tag.strip()[:100]}...")
    
    # 查找所有带有href属性的a标签
    a_tags = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', html)
    print(f"\n找到 {len(a_tags)} 个带有href的a标签")
    
    if a_tags:
        print("\n前5个包含'news'或'成都'的链接:")
        news_links = []
        for href, text in a_tags:
            if 'news' in href or '成都' in href or '成都' in text:
                news_links.append((href, text))
                if len(news_links) >= 5:
                    break
        
        for i, (href, text) in enumerate(news_links, 1):
            print(f"{i}. 文本: {text.strip()[:50]} | 链接: {href[:100]}...")
    
    # 查找所有可能的新闻容器
    news_containers = re.findall(r'<div[^>]*class="[^"]*news[^>]*"[^>]*>(.*?)</div>', html, re.DOTALL)
    print(f"\n找到 {len(news_containers)} 个包含'news'的div容器")
    
    if news_containers:
        print("\n第一个新闻容器内容:")
        print(news_containers[0][:200] + "...")
    
    # 查找所有可能的时间元素
    time_elements = re.findall(r'<span[^>]*class="[^"]*gray[^>]*"[^>]*>(.*?)</span>', html)
    print(f"\n找到 {len(time_elements)} 个包含'gray'的span元素")
    
    if time_elements:
        print("\n前5个时间元素:")
        for i, time in enumerate(time_elements[:5], 1):
            print(f"{i}. {time.strip()}")
    
    # 查找所有可能的来源元素
    source_elements = re.findall(r'<span[^>]*class="[^"]*c-color-gray[^>]*"[^>]*>(.*?)</span>', html)
    print(f"\n找到 {len(source_elements)} 个包含'c-color-gray'的span元素")
    
    if source_elements:
        print("\n前5个来源元素:")
        for i, source in enumerate(source_elements[:5], 1):
            print(f"{i}. {source.strip()}")
    
    # 尝试直接提取新闻条目
    print("\n=== 尝试提取新闻条目 ===")
    
    # 新的提取策略：查找所有包含标题链接的完整新闻块
    news_blocks = re.findall(r'(<div[^>]*class="[^"]*result[^>]*"[^>]*>.*?</div>)', html, re.DOTALL)
    print(f"找到 {len(news_blocks)} 个可能的新闻块")
    
    extracted_news = []
    
    for i, block in enumerate(news_blocks):
        # 从块中提取标题和链接
        title_link = re.search(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', block)
        if not title_link:
            continue
            
        href = title_link.group(1)
        title = title_link.group(2)
        
        # 从块中提取来源和时间
        source_time = re.search(r'<span[^>]*class="[^"]*c-color-gray[^>]*"[^>]*>(.*?)</span>', block)
        source = source_time.group(1) if source_time else ''
        
        # 清理数据
        cleaned_title = re.sub(r'<[^>]*>', '', title).strip()
        cleaned_source = re.sub(r'<[^>]*>', '', source).strip()
        
        if cleaned_title and '成都' in cleaned_title:
            extracted_news.append({
                '标题': cleaned_title,
                '链接': href,
                '来源': cleaned_source
            })
    
    print(f"成功提取 {len(extracted_news)} 条包含'成都'的新闻")
    
    if extracted_news:
        print("\n提取的新闻列表:")
        for i, news in enumerate(extracted_news[:5], 1):
            print(f"{i}. 标题: {news['标题']}")
            print(f"   链接: {news['链接']}")
            print(f"   来源: {news['来源']}")
            print()
            
except Exception as e:
    print(f"请求或分析出错: {e}")
    import traceback
    traceback.print_exc()
