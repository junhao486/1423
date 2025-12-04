import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath('.'))

from app.utils import crawl_baidu_news
import time

def test_crawl_functionality():
    """
    测试抓取功能和翻页参数是否正常工作
    """
    print("开始测试百度新闻抓取功能")
    print("=" * 60)
    
    # 测试1：基本抓取功能
    print("\n测试1：基本抓取功能（第1页）")
    print("-" * 40)
    try:
        news_list = crawl_baidu_news("人工智能", page=1, num_per_page=5)
        print(f"抓取成功！共获取 {len(news_list)} 条新闻")
        
        if news_list:
            print("\n新闻详情：")
            for i, news in enumerate(news_list[:3], 1):
                print(f"\n{str(i).zfill(2)}. 标题: {news['title'][:50]}...")
                print(f"   来源: {news['source']} ({news['source_type']})")
                print(f"   发布时间: {news['publish_time']}")
                print(f"   链接: {news['url']}")
    except Exception as e:
        print(f"测试1失败: {e}")
        return False
    
    # 测试2：翻页功能
    print("\n\n测试2：翻页功能（第2页）")
    print("-" * 40)
    try:
        news_list_page2 = crawl_baidu_news("人工智能", page=2, num_per_page=5)
        print(f"抓取成功！第2页共获取 {len(news_list_page2)} 条新闻")
        
        if news_list_page2:
            print("\n第2页新闻详情：")
            for i, news in enumerate(news_list_page2[:2], 1):
                print(f"\n{str(i).zfill(2)}. 标题: {news['title'][:50]}...")
                print(f"   来源: {news['source']} ({news['source_type']})")
                print(f"   发布时间: {news['publish_time']}")
                print(f"   链接: {news['url']}")
    except Exception as e:
        print(f"测试2失败: {e}")
        return False
    
    # 测试3：自定义每页数量
    print("\n\n测试3：自定义每页数量（10条/页）")
    print("-" * 40)
    try:
        news_list_10 = crawl_baidu_news("人工智能", page=1, num_per_page=10)
        print(f"抓取成功！共获取 {len(news_list_10)} 条新闻")
    except Exception as e:
        print(f"测试3失败: {e}")
        return False
    
    # 测试4：不同关键词
    print("\n\n测试4：不同关键词")
    print("-" * 40)
    try:
        news_list_diff = crawl_baidu_news("新能源汽车", page=1, num_per_page=3)
        print(f"抓取成功！共获取 {len(news_list_diff)} 条新闻")
        
        if news_list_diff:
            print("\n新能源汽车相关新闻：")
            for i, news in enumerate(news_list_diff, 1):
                print(f"\n{str(i).zfill(2)}. 标题: {news['title'][:50]}...")
                print(f"   来源: {news['source']} ({news['source_type']})")
    except Exception as e:
        print(f"测试4失败: {e}")
        return False
    
    print("\n\n" + "=" * 60)
    print("所有测试完成！百度新闻抓取功能正常工作")
    return True

if __name__ == "__main__":
    start_time = time.time()
    success = test_crawl_functionality()
    end_time = time.time()
    
    print(f"\n测试总耗时: {end_time - start_time:.2f}秒")
    
    if success:
        print("\n✓ 所有测试通过！")
        sys.exit(0)
    else:
        print("\n✗ 部分测试失败！")
        sys.exit(1)
