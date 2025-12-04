#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查和初始化数据库
"""

from app import create_app, db
from app.models import User, Role
from sqlalchemy import inspect

# 创建应用和上下文
app = create_app()
with app.app_context():
    print("=== 检查数据库状态 ===")
    
    # 检查表是否存在
    inspector = inspect(db.engine)
    user_table_exists = 'user' in inspector.get_table_names()
    role_table_exists = 'role' in inspector.get_table_names()
    
    print(f"User表存在: {user_table_exists}")
    print(f"Role表存在: {role_table_exists}")
    
    # 如果表不存在，创建表
    if not user_table_exists or not role_table_exists:
        print("\n=== 创建数据库表 ===")
        db.create_all()
        print("数据库表创建完成！")
        
        # 创建默认角色
        print("\n=== 创建默认角色 ===")
        admin_role = Role(name='admin', description='管理员角色')
        user_role = Role(name='user', description='普通用户角色')
        
        db.session.add(admin_role)
        db.session.add(user_role)
        db.session.commit()
        print("默认角色创建完成！")
        
        # 创建默认用户
        print("\n=== 创建默认用户 ===")
        admin = User(username='admin', email='admin@example.com', role_id=admin_role.id)
        admin.set_password('admin123')
        
        user = User(username='user', email='user@example.com', role_id=user_role.id)
        user.set_password('user123')
        
        db.session.add(admin)
        db.session.add(user)
        db.session.commit()
        print("默认用户创建完成！")
    else:
        print("\n数据库表已存在")
        
        # 检查是否有默认角色和用户
        admin_role = Role.query.filter_by(name='admin').first()
        user_role = Role.query.filter_by(name='user').first()
        
        admin_user = User.query.filter_by(username='admin').first()
        regular_user = User.query.filter_by(username='user').first()
        
        print(f"管理员角色存在: {admin_role is not None}")
        print(f"普通用户角色存在: {user_role is not None}")
        print(f"管理员用户存在: {admin_user is not None}")
        print(f"普通用户存在: {regular_user is not None}")

print("\n=== 操作完成 ===")
