# 查看HTML文件的开头部分
with open('baidu_news_debug.html', 'r', encoding='utf-8') as f:
    content = f.read()
    print("HTML文件开头内容：")
    print(content[:5000])  # 查看前5000个字符
    print("\n\nHTML文件结束内容：")
    print(content[-2000:])  # 查看最后2000个字符
