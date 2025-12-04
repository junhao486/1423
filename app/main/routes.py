from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import db
from app.models import User, Role, News, Topic, Comment, SystemSetting
from app.main import bp
from app.utils import crawl_baidu_news, batch_crawl_baidu_news, analyze_sentiment, calculate_heat
import os
from werkzeug.utils import secure_filename

# 首页路由
@bp.route('/')
def index():
    return redirect(url_for('main.login'))

# 登录路由
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password) and user.is_active:
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('login.html')

# 登出路由
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# 仪表盘路由
@bp.route('/dashboard')
@login_required
def dashboard():
    # 获取统计信息
    total_news = News.query.count()
    total_topics = Topic.query.count()
    total_comments = Comment.query.count()
    recent_news = News.query.order_by(News.crawl_time.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         total_news=total_news,
                         total_topics=total_topics,
                         total_comments=total_comments,
                         recent_news=recent_news)

# 新闻列表路由
@bp.route('/news')
@login_required
def news_list():
    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 查询新闻列表
    pagination = News.query.order_by(News.crawl_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    news_items = pagination.items
    
    return render_template('news_list.html', 
                         pagination=pagination,
                         news_items=news_items)

# 话题列表路由
@bp.route('/topics')
@login_required
def topic_list():
    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 查询话题列表
    pagination = Topic.query.order_by(Topic.updated_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    topic_items = pagination.items
    
    return render_template('topic_list.html', 
                         pagination=pagination,
                         topic_items=topic_items)

# 用户列表路由（仅管理员可访问）
@bp.route('/users')
@login_required
def user_list():
    # 检查权限
    if not current_user.has_role('admin'):
        flash('您没有权限访问此页面', 'error')
        return redirect(url_for('main.dashboard'))
    
    # 分页参数
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 查询用户列表
    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    user_items = pagination.items
    
    return render_template('user_list.html', 
                         pagination=pagination,
                         user_items=user_items)

# 添加用户路由
@bp.route('/users/add', methods=['POST'])
@login_required
def add_user():
    if not current_user.has_role('admin'):
        return jsonify({'status': 'error', 'msg': '没有权限'})
    
    # 获取表单数据
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role_id = request.form.get('role_id', 2, type=int)  # 默认普通用户
    
    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'status': 'error', 'msg': '用户名已存在'})
    
    # 检查邮箱是否已存在
    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        return jsonify({'status': 'error', 'msg': '邮箱已存在'})
    
    # 创建新用户
    user = User(username=username, email=email)
    user.set_password(password)
    user.role_id = role_id
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'status': 'success', 'msg': '用户添加成功'})

# 获取用户信息路由
@bp.route('/users/<int:user_id>')
@login_required
def get_user(user_id):
    if not current_user.has_role('admin'):
        return jsonify({'status': 'error', 'msg': '没有权限'})
    
    user = User.query.get_or_404(user_id)
    return jsonify({
        'status': 'success',
        'data': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role_id': user.role_id,
            'is_active': user.is_active,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })

# 更新用户路由
@bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    if not current_user.has_role('admin'):
        return jsonify({'status': 'error', 'msg': '没有权限'})
    
    user = User.query.get_or_404(user_id)
    
    # 获取表单数据
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    role_id = data.get('role_id', 2)
    
    # 检查用户名是否已存在（排除当前用户）
    existing_user = User.query.filter_by(username=username).filter(User.id != user_id).first()
    if existing_user:
        return jsonify({'status': 'error', 'msg': '用户名已存在'})
    
    # 检查邮箱是否已存在（排除当前用户）
    existing_email = User.query.filter_by(email=email).filter(User.id != user_id).first()
    if existing_email:
        return jsonify({'status': 'error', 'msg': '邮箱已存在'})
    
    # 更新用户信息
    user.username = username
    user.email = email
    user.role_id = role_id
    db.session.commit()
    
    return jsonify({'status': 'success', 'msg': '用户信息更新成功'})

# 重置密码路由
@bp.route('/users/<int:user_id>/reset_password', methods=['POST'])
@login_required
def reset_password(user_id):
    if not current_user.has_role('admin'):
        return jsonify({'status': 'error', 'msg': '没有权限'})
    
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('password')
    
    # 更新密码
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'status': 'success', 'msg': '密码重置成功'})

# 禁用/启用用户路由
@bp.route('/users/<int:user_id>/toggle_active', methods=['POST'])
@login_required
def toggle_user_active(user_id):
    if not current_user.has_role('admin'):
        return jsonify({'status': 'error', 'msg': '没有权限'})
    
    user = User.query.get_or_404(user_id)
    
    # 不允许禁用自己
    if user.id == current_user.id:
        return jsonify({'status': 'error', 'msg': '不能禁用当前登录用户'})
    
    # 不允许禁用系统管理员
    if user.has_role('admin') and User.query.filter_by(role_id=1).count() <= 1:
        return jsonify({'status': 'error', 'msg': '系统至少需要一个管理员账号'})
    
    # 切换用户状态
    user.is_active = not user.is_active
    db.session.commit()
    
    return jsonify({
        'status': 'success', 
        'msg': '用户已' + ('启用' if user.is_active else '禁用'),
        'is_active': user.is_active
    })

# 删除用户路由
@bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if not current_user.has_role('admin'):
        return jsonify({'status': 'error', 'msg': '没有权限'})
    
    user = User.query.get_or_404(user_id)
    
    # 不允许删除自己
    if user.id == current_user.id:
        return jsonify({'status': 'error', 'msg': '不能删除当前登录用户'})
    
    # 不允许删除系统管理员
    if user.has_role('admin') and User.query.filter_by(role_id=1).count() <= 1:
        return jsonify({'status': 'error', 'msg': '系统至少需要一个管理员账号'})
    
    # 删除用户
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'status': 'success', 'msg': '用户删除成功'})

# 角色列表路由（仅管理员可访问）
@bp.route('/roles')
@login_required
def role_list():
    # 检查权限
    if not current_user.has_role('admin'):
        flash('您没有权限访问此页面', 'error')
        return redirect(url_for('main.dashboard'))
    
    # 获取所有角色
    roles = Role.query.order_by(Role.id.desc()).all()
    
    return render_template('role_list.html', roles=roles)

# 添加角色路由
@bp.route('/roles/add', methods=['POST'])
@login_required
def add_role():
    if not current_user.has_role('admin'):
        return jsonify({'status': 'error', 'msg': '没有权限'})
    
    name = request.form.get('name')
    description = request.form.get('description')
    
    # 检查角色名是否已存在
    existing_role = Role.query.filter_by(name=name).first()
    if existing_role:
        return jsonify({'status': 'error', 'msg': '角色名已存在'})
    
    # 创建新角色
    role = Role(name=name, description=description)
    db.session.add(role)
    db.session.commit()
    
    return jsonify({'status': 'success', 'msg': '角色添加成功'})

# 获取角色信息路由
@bp.route('/roles/<int:role_id>')
@login_required
def get_role(role_id):
    if not current_user.has_role('admin'):
        return jsonify({'status': 'error', 'msg': '没有权限'})
    
    role = Role.query.get_or_404(role_id)
    return jsonify({
        'status': 'success',
        'data': {
            'id': role.id,
            'name': role.name,
            'description': role.description
        }
    })

# 更新角色路由
@bp.route('/roles/<int:role_id>', methods=['PUT'])
@login_required
def update_role(role_id):
    if not current_user.has_role('admin'):
        return jsonify({'status': 'error', 'msg': '没有权限'})
    
    role = Role.query.get_or_404(role_id)
    
    # 不允许修改默认角色
    if role_id <= 2:
        return jsonify({'status': 'error', 'msg': '不能修改默认角色'})
    
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    
    # 检查角色名是否已存在
    existing_role = Role.query.filter_by(name=name).first()
    if existing_role and existing_role.id != role_id:
        return jsonify({'status': 'error', 'msg': '角色名已存在'})
    
    # 更新角色信息
    role.name = name
    role.description = description
    db.session.commit()
    
    return jsonify({'status': 'success', 'msg': '角色更新成功'})

# 删除角色路由
@bp.route('/roles/<int:role_id>', methods=['DELETE'])
@login_required
def delete_role(role_id):
    if not current_user.has_role('admin'):
        return jsonify({'status': 'error', 'msg': '没有权限'})
    
    # 不允许删除默认角色
    if role_id <= 2:
        return jsonify({'status': 'error', 'msg': '不能删除默认角色'})
    
    role = Role.query.get_or_404(role_id)
    
    # 检查是否有用户使用此角色
    if role.users.count() > 0:
        return jsonify({'status': 'error', 'msg': '该角色已被用户使用，无法删除'})
    
    # 删除角色
    db.session.delete(role)
    db.session.commit()
    
    return jsonify({'status': 'success', 'msg': '角色删除成功'})

# 系统设置路由
@bp.route('/settings')
@login_required
def settings():
    if not current_user.has_role('admin'):
        flash('您没有权限访问此页面', 'error')
        return redirect(url_for('main.dashboard'))
    
    # 获取系统设置
    settings = SystemSetting.query.first()
    if not settings:
        # 如果没有设置，创建默认设置
        settings = SystemSetting(
            app_name='政企智能舆情分析报告生成智能体应用系统',
            logo_url='',
            description='舆情分析系统'
        )
        db.session.add(settings)
        db.session.commit()
    
    return render_template('settings.html', settings=settings)

# 更新系统设置路由
@bp.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    if not current_user.has_role('admin'):
        return jsonify({'status': 'error', 'msg': '没有权限'})
    
    # 获取表单数据
    app_name = request.form.get('app_name')
    description = request.form.get('description')
    
    # 处理LOGO上传
    logo_url = request.form.get('logo_url')
    if 'logo_file' in request.files:
        file = request.files['logo_file']
        if file.filename != '':
            # 保存文件到静态目录
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.root_path, 'static', 'uploads', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)
            # 更新LOGO URL
            logo_url = url_for('static', filename=f'uploads/{filename}', _external=True)
    
    # 更新系统设置
    settings = SystemSetting.query.first()
    if not settings:
        settings = SystemSetting()
        db.session.add(settings)
    
    settings.app_name = app_name
    settings.description = description
    settings.logo_url = logo_url
    db.session.commit()
    
    # 更新配置
    current_app.config['APP_NAME'] = app_name
    
    return jsonify({'status': 'success', 'msg': '系统设置更新成功'})

# API路由 - 获取新闻列表
@bp.route('/api/news')
@login_required
def api_news():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = News.query.order_by(News.crawl_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    news_list = []
    for news in pagination.items:
        news_list.append({
            'id': news.id,
            'title': news.title,
            'source': news.source,
            'publish_time': news.publish_time.isoformat() if news.publish_time else None,
            'sentiment_score': news.sentiment_score,
            'heat_score': news.heat_score,
            'comments_count': news.comments_count
        })
    
    return jsonify({
        'items': news_list,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })

# API路由 - 获取话题列表
@bp.route('/api/topics')
@login_required
def api_topics():
    topics = Topic.query.all()
    topic_list = [{'id': topic.id, 'name': topic.name} for topic in topics]
    return jsonify(topic_list)

# 测试数据抓取功能路由
@bp.route('/test_crawl', methods=['GET', 'POST'])
@login_required
def test_crawl():
    if not current_user.has_role('admin'):
        flash('权限不足，只有管理员可以执行数据抓取操作', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        keyword = request.form.get('keyword', '宜宾')
        try:
            # 调用数据抓取函数
            news_data = crawl_baidu_news(keyword)
            
            # 将抓取的新闻数据存储到数据库
            count = 0
            for item in news_data:
                # 检查是否已存在相同URL的新闻
                existing_news = News.query.filter_by(url=item['原始URL']).first()
                if not existing_news:
                    # 计算情感分数和热度分数
                    sentiment_score = analyze_sentiment(item['概要'])
                    heat_score = calculate_heat(item['概要'])
                    
                    # 创建新闻对象
                    news = News(
                        title=item['标题'],
                        content=item['概要'],
                        source=item['来源'],
                        url=item['原始URL'],
                        cover=item['封面'],
                        publish_time=item['publish_time'],
                        crawl_time=item['crawl_time'],
                        sentiment_score=sentiment_score,
                        heat_score=heat_score
                    )
                    
                    db.session.add(news)
                    count += 1
            
            db.session.commit()
            flash(f'成功抓取并存储 {count} 条新闻数据', 'success')
            return redirect(url_for('main.test_crawl'))
        except Exception as e:
            flash(f'数据抓取失败: {str(e)}', 'error')
            return redirect(url_for('main.test_crawl'))
    
    return render_template('test_crawl.html')