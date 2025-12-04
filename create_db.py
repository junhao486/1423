import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import custom_create_app, db
from app.models import Role, User, SystemSetting, News, Topic, Comment, Monitor

def init_database():
    """初始化数据库"""
    # 删除旧的数据库文件（如果存在）
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.db')
    if os.path.exists(db_path):
        print(f"删除旧数据库文件: {db_path}")
        os.remove(db_path)
    
    # 创建应用实例
    app = custom_create_app()
    
    with app.app_context():
        # 创建所有表
        print("创建数据库表...")
        db.create_all()
        print("数据库表创建完成")
        
        # 创建角色
        print("创建角色...")
        admin_role = Role(name='admin', description='系统管理员')
        user_role = Role(name='user', description='普通用户')
        
        db.session.add_all([admin_role, user_role])
        db.session.commit()
        
        # 创建用户
        print("创建用户...")
        # 创建管理员用户
        admin_user = User(
            username='admin',
            email='admin@example.com',
            role_id=admin_role.id
        )
        admin_user.password = 'admin123'
        
        # 创建普通用户
        normal_user = User(
            username='user',
            email='user@example.com',
            role_id=user_role.id
        )
        normal_user.password = 'user123'
        
        db.session.add_all([admin_user, normal_user])
        db.session.commit()
        
        # 创建系统设置
        print("创建系统设置...")
        settings = [
            SystemSetting(key='system_name', value='舆情系统', description='系统名称'),
            SystemSetting(key='system_version', value='1.0.0', description='系统版本'),
            SystemSetting(key='page_size', value='10', description='分页大小'),
            SystemSetting(key='max_keywords', value='20', description='最大关键词数量'),
            SystemSetting(key='crawl_interval', value='3600', description='爬取间隔（秒）'),
        ]
        
        db.session.add_all(settings)
        db.session.commit()
        
        # 创建测试话题
        print("创建测试话题...")
        topics = [
            Topic(name='科技', description='科技相关新闻'),
            Topic(name='财经', description='财经相关新闻'),
            Topic(name='娱乐', description='娱乐相关新闻'),
            Topic(name='体育', description='体育相关新闻'),
            Topic(name='政治', description='政治相关新闻'),
        ]
        
        db.session.add_all(topics)
        db.session.commit()
        
        # 创建测试新闻
        print("创建测试新闻...")
        # 获取话题ID
        tech_topic = Topic.query.filter_by(name='科技').first()
        finance_topic = Topic.query.filter_by(name='财经').first()
        
        # 创建测试新闻数据
        news_list = [
            News(
                title='人工智能技术取得重大突破',
                content='最新的人工智能技术在自然语言处理领域取得了重大突破，为智能助手的发展提供了新的可能。',
                source='科技日报',
                url='https://example.com/news/1',
                publish_time=datetime.now(),
                sentiment_score=0.8,
                heat_score=95.5,
                comments_count=123,
                views_count=10000
            ),
            News(
                title='股市行情分析：本周市场走势预测',
                content='分析师认为，本周股市可能会出现波动，但长期趋势仍然向好。投资者应保持理性，关注政策变化。',
                source='财经网',
                url='https://example.com/news/2',
                publish_time=datetime.now(),
                sentiment_score=0.2,
                heat_score=88.3,
                comments_count=89,
                views_count=8500
            )
        ]
        
        # 添加话题关联
        news_list[0].topics.append(tech_topic)
        news_list[1].topics.append(finance_topic)
        
        db.session.add_all(news_list)
        db.session.commit()
        
        # 创建测试评论
        print("创建测试评论...")
        comments = [
            Comment(
                news_id=news_list[0].id,
                user_id=normal_user.id,
                content='这个技术确实很厉害，期待应用到实际产品中！',
                sentiment_score=0.9
            ),
            Comment(
                news_id=news_list[1].id,
                user_id=admin_user.id,
                content='分析得很到位，确实需要关注政策面的变化。',
                sentiment_score=0.5
            )
        ]
        
        db.session.add_all(comments)
        db.session.commit()
        
        # 创建测试监控
        print("创建测试监控...")
        monitors = [
            Monitor(
                topic_id=tech_topic.id,
                monitor_type='keyword',
                monitor_value='人工智能',
                status=True
            ),
            Monitor(
                topic_id=finance_topic.id,
                monitor_type='keyword',
                monitor_value='股市',
                status=True
            )
        ]
        
        db.session.add_all(monitors)
        db.session.commit()
        
        print("数据库初始化完成！")
        print("\n用户信息：")
        print(f"管理员账户: admin / admin123")
        print(f"普通用户账户: user / user123")

if __name__ == '__main__':
    init_database()