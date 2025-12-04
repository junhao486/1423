from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import db
from app.models import User, Role, News, Topic, Comment, SystemSetting, CrawlTask, CrawlData
from app.main import bp
from app.utils import crawl_baidu_news, batch_crawl_baidu_news, analyze_sentiment, calculate_heat
import os
from werkzeug.utils import secure_filename
import json

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

# 注册路由
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # 验证表单数据
        if not username or not password or not confirm_password:
            flash('请填写所有必填字段', 'error')
            return redirect(url_for('main.register'))
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return redirect(url_for('main.register'))
        
        if len(password) < 6:
            flash('密码长度不能少于6个字符', 'error')
            return redirect(url_for('main.register'))
        
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('用户名已存在', 'error')
            return redirect(url_for('main.register'))
        
        # 检查邮箱是否已存在
        if email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash('邮箱已被注册', 'error')
                return redirect(url_for('main.register'))
        
        # 获取普通用户角色ID
        user_role = Role.query.filter_by(name='user').first()
        if not user_role:
            flash('系统错误，请联系管理员', 'error')
            return redirect(url_for('main.register'))
        
        # 创建新用户
        new_user = User(
            username=username,
            email=email if email else None,
            role_id=user_role.id
        )
        new_user.password = password
        
        # 保存到数据库
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('注册成功，请登录', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash('注册失败，请稍后重试', 'error')
            return redirect(url_for('main.register'))
    
    return render_template('login.html', register=True)

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

# 管理员管理路由
@bp.route('/admin_management')
@login_required
def admin_management():
    # 检查权限
    if not current_user.has_role('admin'):
        flash('您没有权限访问此页面', 'error')
        return redirect(url_for('main.dashboard'))
    
    # 用户列表数据获取
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 查询用户列表
    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    user_items = pagination.items
    
    # 角色列表数据获取
    roles = Role.query.all()
    
    return render_template('admin_management.html', 
                         pagination=pagination,
                         user_items=user_items,
                         roles=roles)

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
    user.password = password
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
    user.password = new_password
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
    
    latest_news = []
    news_count = 0
    
    latest_news = []
    news_count = 0
    
    if request.method == 'POST':
        keyword = request.form.get('keyword', '')
        num_per_page = int(request.form.get('num_per_page', 20))
        page = int(request.form.get('page', 1))
        sort_by = request.form.get('sort_by', '1')
        
        if not keyword:
            flash('请输入要抓取的关键词', 'warning')
        else:
            try:
                # 调用数据抓取函数
                flash(f'正在抓取"{keyword}"相关新闻...', 'info')
                news_data = crawl_baidu_news(keyword, page=page, num_per_page=num_per_page)
                
                if not news_data:
                    flash('未抓取到新闻数据，可能是由于百度新闻的反爬机制限制。您可以手动添加测试数据。', 'warning')
                else:
                    # 转换数据格式，直接用于模板渲染
                    latest_news = []
                    for item in news_data:
                        # 创建临时新闻对象，模拟数据库模型的结构
                        temp_news = type('TempNews', (object,), {
                            'title': item['title'],
                            'content': item['content'],
                            'source': item['source'],
                            'url': item['url'],
                            'cover': item['cover_image'],
                            'publish_time': item['publish_time']
                        })()
                        latest_news.append(temp_news)
                    
                    news_count = len(latest_news)
                    flash(f'成功抓取 {news_count} 条新闻数据', 'success')
            except Exception as e:
                flash(f'数据抓取失败: {str(e)}。可能是由于百度新闻的反爬机制限制。', 'error')
    
    return render_template('test_crawl.html', news_count=news_count, latest_news=latest_news)


# 数据采集管理路由
@bp.route('/crawl_management')
@login_required
def crawl_management():
    return render_template('crawl_management.html')


# 创建采集任务路由
@bp.route('/create_crawl_task', methods=['POST'])
@login_required
def create_crawl_task():
    try:
        keyword = request.form.get('keyword')
        if not keyword or not keyword.strip():
            return jsonify({'status': 'error', 'message': '关键词不能为空'})
        
        # 创建新的采集任务
        task = CrawlTask(
            user_id=current_user.id,
            keywords=keyword.strip(),
            status='pending',
            progress=0,
            total_items=0,
            success_items=0
        )
        db.session.add(task)
        db.session.commit()
        
        return jsonify({'status': 'success', 'task_id': task.id, 'message': '采集任务已创建'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


# 执行采集任务路由
@bp.route('/execute_crawl_task/<int:task_id>')
@login_required
def execute_crawl_task(task_id):
    try:
        task = CrawlTask.query.get_or_404(task_id)
        
        # 验证任务所有者
        if task.user_id != current_user.id:
            return jsonify({'status': 'error', 'message': '您无权执行此任务'})
        
        # 更新任务状态为运行中
        task.status = 'running'
        task.start_time = datetime.now()
        db.session.commit()
        
        # 执行爬虫
        news_list = crawl_baidu_news(task.keywords, page=1, num_per_page=20)
        
        # 更新任务进度和结果
        task.total_items = len(news_list)
        task.success_items = 0
        
        # 保存采集到的数据
        for news_item in news_list:
            crawl_data = CrawlData(
                task_id=task.id,
                title=news_item['title'],
                content=news_item['content'],
                source=news_item['source'],
                source_type=news_item['source_type'],
                url=news_item['url'],
                publish_time=news_item['publish_time'],
                cover_image=news_item['cover_image'],
                crawl_time=datetime.now()
            )
            db.session.add(crawl_data)
            task.success_items += 1
        
        # 完成任务
        task.status = 'completed'
        task.end_time = datetime.now()
        task.progress = 100
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': '数据采集完成', 'data_count': task.success_items})
    except Exception as e:
        # 更新任务状态为失败
        task.status = 'failed'
        task.error_message = str(e)
        db.session.commit()
        return jsonify({'status': 'error', 'message': str(e)})


# 获取采集任务状态路由
@bp.route('/get_task_status/<int:task_id>')
@login_required
def get_task_status(task_id):
    try:
        task = CrawlTask.query.get_or_404(task_id)
        
        # 验证任务所有者
        if task.user_id != current_user.id:
            return jsonify({'status': 'error', 'message': '您无权查看此任务'})
        
        return jsonify({
            'status': 'success',
            'task': {
                'id': task.id,
                'status': task.status,
                'progress': task.progress,
                'total_items': task.total_items,
                'success_items': task.success_items,
                'error_message': task.error_message
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


# 获取采集数据路由
@bp.route('/get_crawl_data/<int:task_id>')
@login_required
def get_crawl_data(task_id):
    try:
        task = CrawlTask.query.get_or_404(task_id)
        
        # 验证任务所有者
        if task.user_id != current_user.id:
            return jsonify({'status': 'error', 'message': '您无权查看此任务数据'})
        
        # 获取所有采集数据
        crawl_data_list = CrawlData.query.filter_by(task_id=task_id).all()
        
        # 转换为JSON格式
        data_list = []
        for data in crawl_data_list:
            data_list.append({
                'id': data.id,
                'title': data.title,
                'content': data.content,
                'source': data.source,
                'url': data.url,
                'publish_time': data.publish_time.strftime("%Y-%m-%d %H:%M:%S") if data.publish_time else '',
                'cover_image': data.cover_image,
                'is_deep_crawled': data.is_deep_crawled,
                'deep_content': data.deep_content
            })
        
        return jsonify({'status': 'success', 'data': data_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


# 深度采集路由
@bp.route('/deep_crawl/<int:data_id>')
@login_required
def deep_crawl(data_id):
    try:
        crawl_data = CrawlData.query.get_or_404(data_id)
        task = CrawlTask.query.get_or_404(crawl_data.task_id)
        
        # 验证任务所有者
        if task.user_id != current_user.id:
            return jsonify({'status': 'error', 'message': '您无权执行此操作'})
        
        # 模拟深度采集（实际项目中可以实现更复杂的深度采集逻辑）
        import time
        time.sleep(2)  # 模拟网络请求延迟
        
        # 更新深度采集状态
        crawl_data.is_deep_crawled = True
        crawl_data.deep_content = f"深度采集内容：{crawl_data.content}（详细内容已采集...）"
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': '深度采集完成'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


# 保存单个采集数据到数据库路由
@bp.route('/save_single_data/<int:data_id>', methods=['POST'])
@login_required
def save_single_data(data_id):
    try:
        crawl_data = CrawlData.query.get_or_404(data_id)
        
        # 检查是否已存在相同URL的新闻
        existing_news = News.query.filter_by(url=crawl_data.url).first()
        if existing_news:
            return jsonify({'status': 'warning', 'message': '该数据已存在于数据库中'})
        
        # 创建新闻对象
        news = News(
            title=crawl_data.title,
            content=crawl_data.content,
            source=crawl_data.source,
            source_type=crawl_data.source_type,
            url=crawl_data.url,
            publish_time=crawl_data.publish_time,
            cover_image=crawl_data.cover_image,
            crawl_time=crawl_data.crawl_time,
            sentiment_score=0.0,  # 默认情感分数
            heat_score=0.0  # 默认热度分数
        )
        
        # 如果有深度采集内容，使用深度内容
        if crawl_data.is_deep_crawled and crawl_data.deep_content:
            news.content = crawl_data.deep_content
        
        db.session.add(news)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': '数据已成功保存到数据库'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


# 批量保存采集数据到数据库路由
@bp.route('/save_batch_data', methods=['POST'])
@login_required
def save_batch_data():
    try:
        data_ids = request.form.getlist('data_ids[]', type=int)
        if not data_ids:
            return jsonify({'status': 'error', 'message': '请选择要保存的数据'})
        
        success_count = 0
        exists_count = 0
        
        for data_id in data_ids:
            crawl_data = CrawlData.query.get_or_404(data_id)
            
            # 检查是否已存在相同URL的新闻
            existing_news = News.query.filter_by(url=crawl_data.url).first()
            if existing_news:
                exists_count += 1
                continue
            
            # 创建新闻对象
            news = News(
                title=crawl_data.title,
                content=crawl_data.content,
                source=crawl_data.source,
                source_type=crawl_data.source_type,
                url=crawl_data.url,
                publish_time=crawl_data.publish_time,
                cover_image=crawl_data.cover_image,
                crawl_time=crawl_data.crawl_time,
                sentiment_score=0.0,  # 默认情感分数
                heat_score=0.0  # 默认热度分数
            )
            
            # 如果有深度采集内容，使用深度内容
            if crawl_data.is_deep_crawled and crawl_data.deep_content:
                news.content = crawl_data.deep_content
            
            db.session.add(news)
            success_count += 1
        
        db.session.commit()
        
        message = f"成功保存 {success_count} 条数据到数据库"
        if exists_count > 0:
            message += f"，其中 {exists_count} 条数据已存在"
        return jsonify({'status': 'success', 'message': message})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})