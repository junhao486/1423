from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

# 角色模型
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return f'<Role {self.name}>'

# 用户模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role_name):
        if self.role:
            return self.role.name == role_name
        return False
    
    def __repr__(self):
        return f'<User {self.username}>'

# 新闻和话题的多对多关联表
news_topics = db.Table('news_topics',
    db.Column('news_id', db.Integer, db.ForeignKey('news.id'), primary_key=True),
    db.Column('topic_id', db.Integer, db.ForeignKey('topic.id'), primary_key=True)
)

# 新闻模型
class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text)
    source = db.Column(db.String(128))
    url = db.Column(db.String(512))
    cover = db.Column(db.String(512))  # 封面图片URL
    publish_time = db.Column(db.DateTime)
    crawl_time = db.Column(db.DateTime, default=datetime.utcnow)
    sentiment_score = db.Column(db.Float, default=0.0)
    heat_score = db.Column(db.Float, default=0.0)
    comments_count = db.Column(db.Integer, default=0)
    views_count = db.Column(db.Integer, default=0)
    is_processed = db.Column(db.Boolean, default=False)
    topics = db.relationship('Topic', secondary=news_topics, lazy='dynamic',
                           backref=db.backref('news_list', lazy='dynamic'))
    comments = db.relationship('Comment', backref='news', lazy='dynamic')
    
    def __repr__(self):
        return f'<News {self.title}>'

# 话题模型
class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False, index=True)
    description = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    monitors = db.relationship('Monitor', backref='topic', lazy='dynamic')
    
    def __repr__(self):
        return f'<Topic {self.name}>'

# 评论模型
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sentiment_score = db.Column(db.Float, default=0.0)
    likes_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Comment {self.id}>'

# 系统设置模型
class SystemSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(256))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_setting(cls, key, default=None):
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    def __repr__(self):
        return f'<SystemSetting {self.key}>'

# 监控模型
class Monitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    monitor_type = db.Column(db.String(64))  # 监控类型：关键词、URL等
    monitor_value = db.Column(db.Text)  # 监控值：关键词内容、URL等
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.Boolean, default=True)  # 监控状态
    
    def __repr__(self):
        return f'<Monitor {self.id}>'