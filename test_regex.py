import re

# 读取保存的百度新闻HTML内容
with open('baidu_news_debug.txt', 'r', encoding='utf-8') as f:
    html = f.read()

print("开始分析百度新闻页面结构...")
print(f"HTML内容总长度: {len(html)} 字符")

# 查找新闻相关的CSS类名
print("\n查找可能的新闻标题类名...")
title_classes = re.findall(r'<h3[^>]*class="([^"]*)">[\s\S]*?</h3>', html)
title_classes = list(set(title_classes))[:10]  # 去重并只显示前10个
print(f"找到的h3类名: {title_classes}")

# 查找新闻条目结构
print("\n查找新闻条目结构...")
# 尝试匹配可能的新闻条目容器
try:
    # 查找包含h3标签的div或section
    news_items = re.findall(r'(<div[^>]*class="[^"]*news[^"]*"[^>]*>.*?</div>)', html, re.DOTALL)
    print(f"找到{len(news_items)}个可能的新闻条目容器")
    
    if news_items:
        print("\n第一个新闻条目的内容:")
        print(news_items[0][:500])  # 只显示前500个字符
        
        # 在新闻条目中查找标题、链接、摘要等
        print("\n在新闻条目中查找具体内容:")
        
        # 查找标题和链接
        title_link = re.search(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', news_items[0])
        if title_link:
            print(f"标题链接: {title_link.group(1)}")
            print(f"标题文本: {title_link.group(2)}")
        
        # 查找摘要
        summary = re.search(r'<span[^>]*class="[^"]*text[^"]*"[^>]*>(.*?)</span>', news_items[0])
        if summary:
            print(f"摘要: {summary.group(1)}")
        
        # 查找来源和时间
        source_time = re.search(r'<span[^>]*class="[^"]*gray[^"]*"[^>]*>(.*?)</span>', news_items[0])
        if source_time:
            print(f"来源时间: {source_time.group(1)}")
        
        # 查找图片
        image = re.search(r'<img[^>]*src="([^"]*)"[^>]*>', news_items[0])
        if image:
            print(f"图片链接: {image.group(1)}")
            
except Exception as e:
    print(f"分析失败: {e}")
    import traceback
    traceback.print_exc()

print("\n分析完成!")
