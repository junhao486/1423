import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import custom_create_app

# 创建应用实例
app = custom_create_app()

if __name__ == '__main__':
    # 获取端口号，默认为5000
    port = int(os.environ.get('PORT', 5000))
    
    # 启动应用
    app.run(host='0.0.0.0', port=port, debug=True)