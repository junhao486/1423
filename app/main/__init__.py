from flask import Blueprint

# 创建main蓝图
bp = Blueprint('main', __name__, url_prefix='')

# 导入路由
from app.main import routes