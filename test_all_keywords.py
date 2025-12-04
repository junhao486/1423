from app.utils import crawl_baidu_news

# 测试所有关键词的抓取
keywords = ["成都", "重庆", "西安", "武汉", "杭州"]

for keyword in keywords:
    print(f"\n\n开始抓取{keyword}相关新闻...")
    try:
        news_list = crawl_baidu_news(keyword, page=1, num_per_page=5)
        print(f"{keyword}相关新闻抓取成功，共获取{len(news_list)}条新闻")
        
        if news_list:
            print(f"\n{keyword}相关新闻前2条标题：")
            for i, news in enumerate(news_list[:2]):
                print(f"{i+1}. {news['标题']}")
                print(f"   时间: {news['publish_time']}")
                print(f"   链接: {news['原始URL']}")
                print(f"   摘要: {news['概要'][:100]}...")
    except Exception as e:
        print(f"{keyword}相关新闻抓取失败：{str(e)}")

print("\n\n所有关键词测试完成！")
