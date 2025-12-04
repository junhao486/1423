from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env', '.env'))

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

def create_app(config_name=None):
    """创建Flask应用实例"""
    app = Flask(__name__, instance_relative_config=True)
    
    # 配置应用
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key_change_in_production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['APP_NAME'] = os.getenv('APP_NAME', '舆情系统')
    app.config['APP_VERSION'] = os.getenv('APP_VERSION', '1.0.0')
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # 注册蓝图
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    # 模型导入（避免循环导入）
    from app.models import User, Role, News, Topic, Comment, SystemSetting, Monitor
    
    @login_manager.user_loader
    def load_user(user_id):
        """加载用户"""
        return User.query.get(int(user_id))
    
    return app

def custom_create_app():
    """创建自定义配置的Flask应用实例"""
    app = create_app()
    
    # 设置模板和静态文件目录
    app.template_folder = os.path.join(os.path.dirname(__file__), '..', 'templates')
    app.static_folder = os.path.join(os.path.dirname(__file__), '..', 'static')
    
    return app