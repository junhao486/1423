#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试认证功能：登录和注册
"""

from app import custom_create_app, db
from app.models import User, Role

def test_auth():
    """测试认证功能"""
    print("=== 测试认证功能 ===")
    
    # 创建测试应用，使用custom_create_app来确保模板路径正确
    app = custom_create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # 测试时禁用CSRF保护
    
    with app.app_context():
        # 确保数据库表存在
        db.create_all()
        
        # 确保角色存在
        if not Role.query.first():
            admin_role = Role(name='admin', description='管理员')
            user_role = Role(name='user', description='普通用户')
            db.session.add_all([admin_role, user_role])
            db.session.commit()
        
        print("数据库准备完成")
    
    # 使用测试客户端
    with app.test_client() as client:
        print("\n1. 测试注册功能")
        
        # 注册一个新用户
        test_username = "testuser"
        test_password = "test123456"
        test_email = "test@example.com"
        
        # 发送注册请求
        response = client.post('/register', data={
            'username': test_username,
            'email': test_email,
            'password': test_password,
            'confirm_password': test_password
        }, follow_redirects=True)
        
        # 检查注册结果
        if response.status_code == 200:
            print(f"  ✅ 注册请求成功")
            
            # 检查数据库中是否存在该用户
            with app.app_context():
                user = User.query.filter_by(username=test_username).first()
                if user:
                    print(f"  ✅ 新用户 '{test_username}' 已添加到数据库")
                    print(f"  ✅ 用户邮箱: {user.email}")
                    print(f"  ✅ 用户角色: {user.role.name}")
                else:
                    print(f"  ❌ 用户 '{test_username}' 未添加到数据库")
        else:
            print(f"  ❌ 注册请求失败，状态码: {response.status_code}")
        
        print("\n2. 测试登录功能")
        
        # 使用新注册的用户登录
        response = client.post('/login', data={
            'username': test_username,
            'password': test_password,
            'remember': False
        }, follow_redirects=True)
        
        # 检查登录结果
        if response.status_code == 200:
            print(f"  ✅ 登录请求成功")
            # 检查是否成功跳转到仪表盘
            if '仪表盘'.encode('utf-8') in response.data or '舆情分析'.encode('utf-8') in response.data:
                print(f"  ✅ 成功登录并跳转到仪表盘")
            else:
                print(f"  ⚠️ 登录成功，但未跳转到预期页面")
        else:
            print(f"  ❌ 登录请求失败，状态码: {response.status_code}")
        
        print("\n3. 测试登出功能")
        
        # 登出
        response = client.get('/logout', follow_redirects=True)
        
        if response.status_code == 200:
            print(f"  ✅ 登出请求成功")
            # 检查是否跳转到登录页面
            if '登录'.encode('utf-8') in response.data and '密码'.encode('utf-8') in response.data:
                print(f"  ✅ 成功登出并跳转到登录页面")
        else:
            print(f"  ❌ 登出请求失败，状态码: {response.status_code}")
        
        print("\n4. 测试使用错误密码登录")
        
        # 使用错误密码登录
        response = client.post('/login', data={
            'username': test_username,
            'password': 'wrongpassword',
            'remember': False
        }, follow_redirects=True)
        
        if response.status_code == 200:
            # 应该显示错误消息
            if '用户名或密码错误'.encode('utf-8') in response.data:
                print(f"  ✅ 成功拦截错误密码登录")
            else:
                print(f"  ⚠️ 错误密码登录被接受")
        else:
            print(f"  ❌ 错误密码登录请求失败，状态码: {response.status_code}")
        
        print("\n=== 清理测试数据 ===")
        
        # 清理测试用户
        with app.app_context():
            user = User.query.filter_by(username=test_username).first()
            if user:
                db.session.delete(user)
                db.session.commit()
                print(f"  ✅ 测试用户 '{test_username}' 已从数据库中删除")
        
    print("\n=== 认证功能测试完成 ===")

if __name__ == '__main__':
    test_auth()
