#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加测试数据到数据库
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import db
from app import custom_create_app
from app.models import News

# 创建应用实例和上下文
app = custom_create_app()
app_context = app.app_context()
app_context.push()

def add_test_news():
    """添加测试新闻数据"""
    print("开始添加测试新闻数据...")
    
    # 定义测试新闻数据
    test_news = [
        {
            'title': '成都城市发展规划获批',
            'content': '近日，成都市城市发展规划正式获批，将推动城市建设迈上新台阶。',
            'source': '成都日报',
            'url': 'https://example.com/news1',
            'publish_time': datetime.now() - timedelta(days=1)
        },
        {
            'title': '成都大熊猫基地新馆开放',
            'content': '成都大熊猫基地新馆正式开放，吸引大量游客前来参观。',
            'source': '四川电视台',
            'url': 'https://example.com/news2',
            'publish_time': datetime.now() - timedelta(days=2)
        },
        {
            'title': '成都高新区企业创新成果展',
            'content': '成都高新区举办企业创新成果展，展示了众多高科技产品。',
            'source': '科技日报',
            'url': 'https://example.com/news3',
            'publish_time': datetime.now() - timedelta(days=3)
        },
        {
            'title': '成都美食文化节开幕',
            'content': '第20届成都美食文化节盛大开幕，来自世界各地的美食汇聚一堂。',
            'source': '成都商报',
            'url': 'https://example.com/news4',
            'publish_time': datetime.now() - timedelta(days=4)
        },
        {
            'title': '成都地铁新线开通',
            'content': '成都地铁10号线新段正式开通运营，方便市民出行。',
            'source': '交通广播',
            'url': 'https://example.com/news5',
            'publish_time': datetime.now() - timedelta(days=5)
        }
    ]
    
    # 添加到数据库
    count = 0
    for news_data in test_news:
        # 检查是否已存在
        existing = News.query.filter_by(url=news_data['url']).first()
        if not existing:
            news = News(
                title=news_data['title'],
                content=news_data['content'],
                source=news_data['source'],
                url=news_data['url'],
                publish_time=news_data['publish_time'],
                crawl_time=datetime.now()
            )
            db.session.add(news)
            count += 1
    
    # 提交事务
    db.session.commit()
    
    print(f"成功添加{count}条测试新闻数据")
    
    # 验证数据
    total = News.query.count()
    print(f"数据库中共有{total}条新闻数据")
    
    return count

# 主函数
if __name__ == "__main__":
    add_test_news()
