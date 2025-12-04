from app.utils import crawl_baidu_news

print('开始抓取成都相关新闻...')
try:
    result = crawl_baidu_news('成都')
    print(f'抓取成功，共获取{len(result)}条新闻')
    print('前3条新闻标题：')
    for i, news in enumerate(result[:3], 1):
        print(f'{i}. {news['标题']}')
    print('\n完整的新闻数据结构示例：')
    if result:
        print(result[0])
except Exception as e:
    print(f'抓取过程中发生错误：{str(e)}')
    import traceback
    traceback.print_exc()