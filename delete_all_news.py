import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import custom_create_app
from app import db
from app.models import News

def delete_all_news():
    """删除数据库中所有新闻记录"""
    # 创建应用实例
    app = custom_create_app()
    
    with app.app_context():
        try:
            # 获取当前新闻数量
            current_count = News.query.count()
            print(f"当前数据库中有 {current_count} 条新闻记录")
            
            # 删除所有新闻
            News.query.delete()
            
            # 提交事务
            db.session.commit()
            
            # 验证删除结果
            new_count = News.query.count()
            print(f"成功删除所有新闻记录，现在数据库中有 {new_count} 条新闻记录")
            print("所有抓取到的新闻已被删除")
            
        except Exception as e:
            # 回滚事务
            db.session.rollback()
            print(f"删除新闻记录时发生错误：{e}")
        finally:
            # 关闭会话
            db.session.close()

if __name__ == "__main__":
    delete_all_news()
