from app.utils import crawl_baidu_news

# 测试1: 正常抓取新闻
print("=== 测试1: 正常抓取新闻 ===")
news_list = crawl_baidu_news('test', page=1, num_per_page=3)
print(f"成功抓取到 {len(news_list)} 条新闻")

# 测试2: 模拟脏数据过滤功能
print("\n=== 测试2: 模拟脏数据过滤 ===")

# 模拟脏数据1: 只有标题有效，其他字段无效（4个无效字段）
dirty_news_1 = {
    "title": "有效的标题",
    "content": "",
    "source": "",
    "url": "",
    "cover_image": ""
}

# 模拟脏数据2: 标题和URL有效，其他字段无效（3个无效字段）
dirty_news_2 = {
    "title": "有效的标题",
    "content": "",
    "source": "",
    "url": "https://example.com",
    "cover_image": ""
}

# 模拟正常数据: 所有字段都有效
valid_news = {
    "title": "有效的标题",
    "content": "有效的摘要",
    "source": "有效的来源",
    "url": "https://example.com",
    "cover_image": "https://example.com/image.jpg"
}

# 测试脏数据过滤逻辑
print("\n测试脏数据过滤逻辑:")

# 测试1的过滤结果
invalid_count_1 = 0
if not dirty_news_1["title"]: invalid_count_1 += 1
if not dirty_news_1["content"]: invalid_count_1 += 1
if not dirty_news_1["source"]: invalid_count_1 += 1
if not dirty_news_1["url"] or not (dirty_news_1["url"].startswith("http://") or dirty_news_1["url"].startswith("https://")): invalid_count_1 += 1
if not dirty_news_1["cover_image"]: invalid_count_1 += 1
print(f"脏数据1无效字段数: {invalid_count_1}, 是否过滤: {invalid_count_1 >= 3}")

# 测试2的过滤结果
invalid_count_2 = 0
if not dirty_news_2["title"]: invalid_count_2 += 1
if not dirty_news_2["content"]: invalid_count_2 += 1
if not dirty_news_2["source"]: invalid_count_2 += 1
if not dirty_news_2["url"] or not (dirty_news_2["url"].startswith("http://") or dirty_news_2["url"].startswith("https://")): invalid_count_2 += 1
if not dirty_news_2["cover_image"]: invalid_count_2 += 1
print(f"脏数据2无效字段数: {invalid_count_2}, 是否过滤: {invalid_count_2 >= 3}")

# 测试正常数据的过滤结果
invalid_count_valid = 0
if not valid_news["title"]: invalid_count_valid += 1
if not valid_news["content"]: invalid_count_valid += 1
if not valid_news["source"]: invalid_count_valid += 1
if not valid_news["url"] or not (valid_news["url"].startswith("http://") or valid_news["url"].startswith("https://")): invalid_count_valid += 1
if not valid_news["cover_image"]: invalid_count_valid += 1
print(f"正常数据无效字段数: {invalid_count_valid}, 是否过滤: {invalid_count_valid >= 3}")

print("\n脏数据过滤功能测试完成！")
