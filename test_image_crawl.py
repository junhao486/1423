from app.utils import crawl_baidu_news

# 测试新闻抓取功能，特别关注封面图片提取
result = crawl_baidu_news('成都', page=1, num_per_page=10)

print(f'共提取到 {len(result)} 条新闻')
print('\n图片提取情况:')
for idx, news in enumerate(result, 1):
    print(f'{idx}. 标题: {news["标题"]}')
    print(f'   封面: {news["封面"]}')
    print('   ' + '-' * 30)
