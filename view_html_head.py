# 查看HTML文件的前100行内容
with open('baidu_news_analysis.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        print(f"{i:3d}: {line.rstrip()}")
        if i >= 100:
            break
