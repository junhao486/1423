import re
import jieba
import jieba.analyse
import requests
from datetime import datetime
from typing import List, Dict, Any
from bs4 import BeautifulSoup

# 文本清理函数
def clean_text(text: str) -> str:
    """清理文本，去除特殊字符和多余空格"""
    if not text:
        return ""
    
    # 去除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 去除特殊字符（保留中文、英文、数字和基本标点）
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9,.!?:;"\'()\[\]{}<>\s]', '', text)
    
    # 去除多余空格
    text = re.sub(r'\s+', ' ', text)
    
    # 去除首尾空格
    return text.strip()

# 确定新闻来源类型的辅助函数
def determine_source_type(source: str) -> str:
    """
    根据新闻来源名称确定来源类型
    
    Args:
        source: 新闻来源名称
        
    Returns:
        来源类型（官方媒体、商业媒体、自媒体等）
    """
    if not source:
        return "未知"
        
    # 官方媒体列表
    official_media = ["央视", "新华社", "人民网", "光明网", "中国日报", "中新网", "环球网", "中国新闻网"]
    
    # 商业媒体列表
    commercial_media = ["澎湃新闻", "界面新闻", "财经网", "科技日报", "成都商报", "华西都市报", "凤凰网", "新浪", "网易", "腾讯"]
    
    # 自媒体列表
    we_media = ["微信", "微博", "知乎", "抖音", "小红书", "头条", "搜狐号", "百家号"]
    
    source_lower = source.lower()
    
    for media in official_media:
        if media in source:
            return "官方媒体"
    
    for media in commercial_media:
        if media in source:
            return "商业媒体"
    
    for media in we_media:
        if media in source_lower:
            return "自媒体"
    
    return "其他媒体"

# 标准化时间格式的辅助函数
def normalize_time(time_str: str) -> str:
    """
    标准化时间格式，将各种时间表示转换为统一格式
    
    Args:
        time_str: 原始时间字符串
        
    Returns:
        标准化后的时间字符串
    """
    from datetime import timedelta
    if not time_str:
        return ""
        
    # 处理相对时间（如 "1小时前"、"2天前"）
    relative_time_patterns = {
        r'(\d+)小时前': lambda m: (datetime.now() - timedelta(hours=int(m.group(1)))).strftime("%Y-%m-%d %H:%M"),
        r'(\d+)天前': lambda m: (datetime.now() - timedelta(days=int(m.group(1)))).strftime("%Y-%m-%d %H:%M"),
        r'(\d+)分钟前': lambda m: (datetime.now() - timedelta(minutes=int(m.group(1)))).strftime("%Y-%m-%d %H:%M"),
        r'刚刚': lambda m: datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    
    for pattern, formatter in relative_time_patterns.items():
        match = re.search(pattern, time_str)
        if match:
            return formatter(match)
    
    # 处理完整日期格式
    full_date_patterns = [
        (r'^(\d{4})[-/年](0?[1-9]|1[0-2])[-/月](0?[1-9]|[12]\d|3[01])日?$', "%Y-%m-%d"),
        (r'^(0?[1-9]|1[0-2])[-/月](0?[1-9]|[12]\d|3[01])日?$', f"{datetime.now().year}-%m-%d"),
        (r'^(\d{2}):(\d{2})$', f"{datetime.now().strftime('%Y-%m-%d')} %H:%M"),
    ]
    
    for pattern, format_str in full_date_patterns:
        match = re.match(pattern, time_str)
        if match:
            try:
                # 特殊处理不含年份的情况
                if "%Y" not in format_str:
                    # 如果是未来日期（如12月31日，但当前是1月1日），则减一年
                    formatted_date = datetime.strptime(time_str, "%m-%d")
                    formatted_date = formatted_date.replace(year=datetime.now().year)
                    if formatted_date > datetime.now():
                        formatted_date = formatted_date.replace(year=datetime.now().year - 1)
                    return formatted_date.strftime("%Y-%m-%d %H:%M")
                else:
                    return datetime.strptime(time_str, "%Y-%m-%d").strftime("%Y-%m-%d %H:%M")
            except ValueError:
                continue
    
    return time_str

# 关键词提取函数
def extract_keywords(text: str, topK: int = 10) -> List[str]:
    """使用jieba提取关键词"""
    if not text:
        return []
    
    # 确保中文分词正常工作
    try:
        # 使用TF-IDF提取关键词
        keywords = jieba.analyse.extract_tags(text, topK=topK)
        return keywords
    except Exception as e:
        print(f"关键词提取错误: {e}")
        return []

# 情感分析关键词库
POSITIVE_WORDS = {
    '好', '优秀', '棒', '赞', '精彩', '完美', '满意', '喜欢', '推荐',
    '成功', '进步', '创新', '高效', '专业', '可靠', '安全', '优质', '舒适'
}

NEGATIVE_WORDS = {
    '差', '糟糕', '坏', '烂', '失望', '失败', '问题', '错误', '缺点',
    '风险', '危险', '不安全', '低效', '麻烦', '困扰', '讨厌', '反对', '拒绝'
}

# 简单的情感分析函数
def analyze_sentiment(text: str) -> float:
    """基于关键词匹配的简单情感分析，返回-1.0到1.0之间的分数"""
    if not text:
        return 0.0
    
    # 分词
    words = jieba.lcut(text)
    
    # 统计情感词
    positive_count = 0
    negative_count = 0
    
    for word in words:
        if word in POSITIVE_WORDS:
            positive_count += 1
        elif word in NEGATIVE_WORDS:
            negative_count += 1
    
    # 计算情感得分
    total_emotional_words = positive_count + negative_count
    if total_emotional_words == 0:
        return 0.0
    
    # 归一化到-1.0到1.0
    sentiment_score = (positive_count - negative_count) / total_emotional_words
    
    return sentiment_score

# 网页内容获取函数
def fetch_web_content(url: str, timeout: int = 10) -> str:
    """获取网页内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response.text
    except Exception as e:
        print(f"获取网页内容错误: {e}")
        return ""

# 日期解析函数
def parse_date(date_str: str) -> datetime:
    """解析日期字符串为datetime对象"""
    if not date_str:
        return datetime.now()
    
    # 尝试多种常见的日期格式
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%Y/%m/%d %H:%M:%S',
        '%Y/%m/%d',
        '%d/%m/%Y',
        '%d-%m-%Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # 如果都解析失败，返回当前时间
    return datetime.now()

# 热度计算函数
def calculate_heat(news: Any) -> float:
    """计算新闻热度分数"""
    # 基于评论数、浏览量和发布时间计算热度
    base_score = news.comments_count * 2 + news.views_count * 0.1
    
    # 时间衰减因子
    if news.publish_time:
        hours_passed = (datetime.now() - news.publish_time).total_seconds() / 3600
        time_factor = 1 / (1 + hours_passed / 24)  # 每天衰减一半
    else:
        time_factor = 1.0
    
    # 情感因子（极端情感增加热度）
    sentiment_factor = 1 + abs(news.sentiment_score) * 0.5
    
    # 综合热度分数
    heat_score = base_score * time_factor * sentiment_factor
    
    return round(heat_score, 2)

# 数字格式化函数
def format_number(num: int) -> str:
    """格式化数字，超过10000显示为x.xx万"""
    if num >= 10000:
        return f"{num / 10000:.2f}万"
    return str(num)

# 分页参数验证函数
def validate_pagination_params(page: int, per_page: int) -> tuple:
    """验证分页参数"""
    if page < 1:
        page = 1
    
    if per_page < 1:
        per_page = 10
    elif per_page > 100:
        per_page = 100
    
    return page, per_page

# 获取分页URL函数
def get_pagination_urls(pagination: Any) -> Dict[str, str]:
    """获取分页的URL"""
    from flask import request
    
    urls = {
        'first': None,
        'prev': None,
        'next': None,
        'last': None
    }
    
    args = request.args.copy()
    
    if pagination.has_next:
        args['page'] = pagination.next_num
        urls['next'] = f"{request.base_url}?{args.to_dict(flat=True)}"
    
    if pagination.has_prev:
        args['page'] = pagination.prev_num
        urls['prev'] = f"{request.base_url}?{args.to_dict(flat=True)}"
    
    args['page'] = 1
    urls['first'] = f"{request.base_url}?{args.to_dict(flat=True)}"
    
    args['page'] = pagination.pages
    urls['last'] = f"{request.base_url}?{args.to_dict(flat=True)}"
    
    return urls

# 百度新闻搜索抓取函数
def crawl_baidu_news(keyword: str, page: int = 1, num_per_page: int = 20) -> List[Dict[str, Any]]:
    """
    从百度新闻搜索中抓取关键词相关的新闻
    
    Args:
        keyword: 搜索关键词
        page: 页码 (1-based)
        num_per_page: 每页条数
        
    Returns:
        新闻列表，每条包含标题、概要、封面、原始URL、来源等信息
    """
    # 输入参数验证
    if not keyword or not keyword.strip():
        print("错误: 关键词不能为空")
        return []
    
    page = max(1, page)  # 确保页码至少为1
    num_per_page = max(1, min(100, num_per_page))  # 限制每页条数在1-100之间
    
    keyword = keyword.strip()
    # 构建搜索URL - 使用用户指定的百度新闻搜索URL格式
    import urllib.parse
    import random
    import time
    
    encoded_keyword = urllib.parse.quote(keyword)
    # 计算pn参数：pn = (page-1) * num_per_page
    # 默认第一页：pn=0，第二页：pn=20，第三页：pn=40...
    pn_value = (page - 1) * num_per_page
    
    # 使用用户指定的URL格式，添加翻页参数pn
    url = f"https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&rsv_dl=ns_pc&word={encoded_keyword}&pn={pn_value}"
    
    # 添加num参数控制每页条数
    if num_per_page != 10:  # 如果不是默认的10条，显式指定rn参数
        url += f"&rn={num_per_page}"
    
    # 设置User-Agent池，包含桌面和移动设备
    user_agents = [
        # 桌面设备
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        
        # 移动设备
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Android 13; Mobile; rv:119.0) Gecko/109.0 Firefox/119.0',
        'Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
    ]
    
    # 设置请求头 - 模拟真实浏览器请求
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'connection': 'keep-alive',
        'host': 'www.baidu.com',
        'referer': 'https://www.baidu.com/',
        'upgrade-insecure-requests': '1',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'user-agent': random.choice(user_agents)
    }
    
    # 发送请求，实现重试机制
    max_retries = 3
    retry_delay = 5
    html_content = ""
    
    for retry in range(max_retries):
        try:
            # 添加随机延迟，避免请求过快触发反爬虫
            delay = random.uniform(2, 5) + retry * 2  # 重试时增加延迟
            time.sleep(delay)
            print(f"正在抓取关键词 '{keyword}' 第 {page} 页 (延迟 {delay:.2f}秒)...")
            
            # 使用会话对象，模拟浏览器会话
            session = requests.Session()
            
            # 先访问百度首页，获取cookie
            session.get('https://www.baidu.com/', headers=headers, timeout=10)
            
            # 再访问新闻搜索页面
            response = session.get(url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            # 验证响应是否正常（检查是否包含搜索结果）
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容长度: {len(response.text)}")
            print(f"响应前100个字符: {response.text[:100]}...")
            
            # 放宽验证条件，只要响应内容不为空且长度大于1000就认为是正常的
            if response.text and len(response.text) > 1000:
                html_content = response.text
                print(f"成功获取关键词 '{keyword}' 第 {page} 页的内容")
                break
            else:
                print(f"警告: 响应内容可能异常，重试 {retry + 1}/{max_retries}")
                
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}，重试 {retry + 1}/{max_retries}")
            if retry == max_retries - 1:  # 最后一次重试失败
                return []
            
            # 调整请求头，尝试使用不同的User-Agent
            headers['user-agent'] = random.choice(user_agents)
            continue
    
    if not html_content:
        print("无法获取有效内容，返回空列表")
        return []
    
    # 保存HTML内容用于调试（可选，产品环境可关闭）
    if page == 1 and num_per_page == 10:  # 仅在默认情况下保存调试文件
        with open('baidu_news.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("HTML内容已保存到 baidu_news.html")
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 提取新闻列表
    news_list = []
    news_set = set()  # 用于去重，存储(标题, URL)元组
    
    # 记录处理开始时间
    processing_start = time.time()
    
    # 查找可能的新闻条目容器
    # 移动版百度新闻的页面结构可能不同，尝试多种方式查找
    candidate_divs = []
    
    # 1. 尝试查找所有包含h3标签的div
    all_divs = soup.find_all('div')
    for div in all_divs:
        h3_tag = div.find('h3')
        if h3_tag:
            a_tag = h3_tag.find('a')
            if a_tag and a_tag.get('href'):
                candidate_divs.append(div)
    
    # 2. 如果没有找到，尝试直接查找所有h3标签
    if not candidate_divs:
        h3_tags = soup.find_all('h3')
        for h3 in h3_tags:
            a_tag = h3.find('a')
            if a_tag and a_tag.get('href'):
                # 使用h3的父元素作为容器
                if h3.parent.name == 'div':
                    candidate_divs.append(h3.parent)
                else:
                    # 创建一个临时div作为容器
                    candidate_divs.append(h3)
    
    # 3. 如果还是没有找到，尝试查找所有包含链接的元素
    if not candidate_divs:
        a_tags = soup.find_all('a')
        for a in a_tags:
            if a.get('href') and a.get_text().strip():
                candidate_divs.append(a.parent)
    
    print(f"找到 {len(candidate_divs)} 个候选新闻容器")
    
    # 遍历每个候选容器，尝试提取新闻信息
    for container in candidate_divs:
        try:
            # 提取标题和链接
            h3_tag = container.find('h3')
            if h3_tag:
                a_tag = h3_tag.find('a')
            else:
                # 如果没有h3标签，尝试直接在容器中查找a标签
                a_tag = container.find('a')
            
            if not a_tag:
                continue
            
            link = a_tag.get('href')
            if not link:
                continue
            
            # 获取标题文本
            if h3_tag:
                title_text = h3_tag.get_text(strip=True)
            else:
                title_text = a_tag.get_text(strip=True)
            
            if not title_text:
                continue
            
            # 清理标题
            cleaned_title = clean_text(title_text)
            
            # 放宽关键词匹配条件，只要新闻内容相关即可
            # 不再严格要求标题或链接包含关键词，避免过滤掉相关新闻
            # 我们会在后续步骤中通过内容分析进一步筛选
            
            # 数据验证
            if not cleaned_title or len(cleaned_title) < 5:
                print(f"新闻标题过短或为空，跳过")
                continue
                
            if not link or not link.startswith(('http://', 'https://')):
                print(f"新闻链接无效或为空，跳过")
                continue
                
            # 检查是否已经存在相同的新闻（去重）
            news_key = (cleaned_title, link)
            if news_key in news_set:
                print(f"发现重复新闻: {cleaned_title[:30]}...")
                continue
            
            # 提取来源和时间信息
            source = ''
            publish_time_str = ''
            
            # 查找所有可能包含来源和时间的文本节点
            all_text = container.get_text()
            
            # 尝试匹配常见来源模式，优先匹配主要新闻网站
            source_patterns = [
                r'(央视网|新华网|人民网|光明网|中国日报网|中新网|环球网|凤凰网|中国新闻网|澎湃新闻|界面新闻|财经网|科技日报|成都商报|华西都市报)',
                r'来源[:：]\s*(\w+)',
                r'\s*(\w+)(?:[网报台])\s*',
                r'^(\w+)(?:\s*[:：])?',  # 开头的来源
                r'\s*(\w+)\s*·\s*',    # 中间的来源，如 "成都商报 · "
            ]
            
            for pattern in source_patterns:
                match = re.search(pattern, all_text, re.MULTILINE)
                if match:
                    source = match.group(1)
                    break
            
            # 尝试匹配时间模式
            time_patterns = [
                r'((?:20\d{2}|19\d{2})[-/年](?:0?[1-9]|1[0-2])[-/月](?:0?[1-9]|[12]\d|3[01])日?)',
                r'((?:0?[1-9]|1[0-2])[-/月](?:0?[1-9]|[12]\d|3[01])日?)',
                r'(\d{2}:\d{2})',
                r'(\d+[小时天前])',
                r'发布于\s*([^\s]+)',
                r'时间[:：]\s*([^\s]+)',
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, all_text)
                if match:
                    publish_time_str = match.group(1)
                    break
            
            # 提取摘要信息
            summary = ''
            
            # 查找所有文本节点，提取最相关的内容作为摘要
            all_text = container.get_text()
            
            # 移除标题、来源和时间
            if cleaned_title in all_text:
                all_text = all_text.replace(cleaned_title, '')
            if source in all_text:
                all_text = all_text.replace(source, '')
            if publish_time_str in all_text:
                all_text = all_text.replace(publish_time_str, '')
            
            # 清理文本
            all_text = clean_text(all_text)
            
            # 跳过热搜榜等无关内容
            irrelevant_keywords = ['热搜榜', '民生榜', '财经榜', '换一换', '新闻全文', '新闻标题', '全部资讯', '', '', '', '', '分享', '收藏', '评论', '点赞']
            for keyword in irrelevant_keywords:
                all_text = all_text.replace(keyword, '')
            
            # 移除多余的空格和换行
            all_text = re.sub(r'\s+', ' ', all_text).strip()
            
            # 提取摘要
            if all_text:
                if len(all_text) <= 200:
                    summary = all_text
                else:
                    # 截取前200个字符作为摘要
                    summary = all_text[:200] + '...'
            
            # 如果还是没有摘要，尝试从容器的兄弟节点或子节点中提取
            if not summary:
                # 尝试查找容器内的p标签
                p_tags = container.find_all('p')
                for p in p_tags:
                    p_text = clean_text(p.get_text(strip=True))
                    if p_text and len(p_text) > 10:
                        summary = p_text[:200] + ('...' if len(p_text) > 200 else '')
                        break
                
            # 再次验证摘要长度
            if not summary or len(summary) < 10:
                print(f"新闻摘要过短或为空，跳过")
                continue
            
            # 提取封面图片
            cover_image = ''
            
            # 1. 尝试查找容器内的图片，支持现代百度新闻的多种结构
            # 查找容器内的所有img标签
            all_imgs = container.find_all('img')
            for img in all_imgs:
                # 获取图片源
                img_src = img.get('src', '')
                # 也检查data-src等懒加载属性
                if not img_src:
                    img_src = img.get('data-src', '')
                if not img_src:
                    img_src = img.get('data-original', '')
                
                if img_src:
                    # 排除base64图片和图标
                    if not img_src.startswith('data:') and not img_src.startswith('//www.baidu.com/img/'):
                        # 处理相对URL和协议相对URL
                        if img_src.startswith('//'):
                            img_src = 'https:' + img_src
                        elif img_src.startswith('/'):
                            img_src = 'https://www.baidu.com' + img_src
                        elif img_src.startswith('https:') and not img_src.startswith('https://'):
                            # 修复缺少//的情况，如https:t9.baidu.com/...
                            img_src = 'https://' + img_src[6:]
                        elif img_src.startswith('http:') and not img_src.startswith('http://'):
                            # 修复缺少//的情况，如http:t9.baidu.com/...
                            img_src = 'http://' + img_src[5:]
                        elif not img_src.startswith(('http://', 'https://')):
                            img_src = 'https://www.baidu.com/' + img_src
                        cover_image = img_src
                        break
            
            # 2. 尝试从容器的子元素或兄弟元素中查找图片
            if not cover_image:
                # 查找可能包含图片的子容器
                image_containers = container.find_all(['div', 'span', 'a'], class_=re.compile(r'.*img.*|.*pic.*|.*image.*', re.I))
                for img_container in image_containers:
                    img_tag = img_container.find('img')
                    if img_tag:
                        img_src = img_tag.get('src', '') or img_tag.get('data-src', '') or img_tag.get('data-original', '')
                        if img_src and not img_src.startswith('data:') and not img_src.startswith('//www.baidu.com/img/'):
                            if img_src.startswith('//'):
                                img_src = 'https:' + img_src
                            elif img_src.startswith('/'):
                                img_src = 'https://www.baidu.com' + img_src
                            elif img_src.startswith('https:') and not img_src.startswith('https://'):
                                # 修复缺少//的情况，如https:t9.baidu.com/...
                                img_src = 'https://' + img_src[6:]
                            elif img_src.startswith('http:') and not img_src.startswith('http://'):
                                # 修复缺少//的情况，如http:t9.baidu.com/...
                                img_src = 'http://' + img_src[5:]
                            elif not img_src.startswith(('http://', 'https://')):
                                img_src = 'https://www.baidu.com/' + img_src
                            cover_image = img_src
                            break
            
            # 3. 尝试从链接中提取
            if not cover_image and 'img' in link:
                cover_image = link
                # 同样需要处理URL格式问题
                if cover_image and not cover_image.startswith('data:'):
                    if cover_image.startswith('//'):
                        cover_image = 'https:' + cover_image
                    elif cover_image.startswith('/'):
                        cover_image = 'https://www.baidu.com' + cover_image
                    elif cover_image.startswith('https:') and not cover_image.startswith('https://'):
                        # 修复缺少//的情况，如https:t9.baidu.com/...
                        cover_image = 'https://' + cover_image[6:]
                    elif cover_image.startswith('http:') and not cover_image.startswith('http://'):
                        # 修复缺少//的情况，如http:t9.baidu.com/...
                        cover_image = 'http://' + cover_image[5:]
                    elif not cover_image.startswith(('http://', 'https://')):
                        cover_image = 'https://www.baidu.com/' + cover_image
            
            # 清理数据
            cleaned_source = clean_text(source)
            cleaned_time = clean_text(publish_time_str)
            cleaned_summary = clean_text(summary)
            # 封面图片URL不使用clean_text处理，避免破坏URL结构
            cleaned_cover = cover_image.strip() if cover_image else ''
            
            # 构建新闻对象
            news = {
                "title": cleaned_title,
                "content": cleaned_summary,
                "source": cleaned_source,
                "source_type": determine_source_type(cleaned_source),
                "url": link,
                "publish_time": normalize_time(cleaned_time),
                "cover_image": cleaned_cover,
                "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "keyword": keyword,
                "page": page
            }
            
            # 脏数据过滤：检查五个关键字段的有效性，至少三个无效则视为脏数据
            invalid_count = 0
            
            # 检查标题
            if not news["title"]:
                invalid_count += 1
            
            # 检查摘要
            if not news["content"]:
                invalid_count += 1
            
            # 检查来源
            if not news["source"]:
                invalid_count += 1
            
            # 检查URL
            if not news["url"] or not (news["url"].startswith("http://") or news["url"].startswith("https://")):
                invalid_count += 1
            
            # 检查封面图片
            if not news["cover_image"]:
                invalid_count += 1
            
            # 如果无效字段数量大于等于3，则跳过这条新闻
            if invalid_count >= 3:
                print(f"过滤脏数据（{invalid_count}个无效字段）: {cleaned_title[:30]}...")
                continue
            
            # 添加到新闻列表并记录到集合中用于去重
            news_list.append(news)
            news_set.add(news_key)
            print(f"成功提取新闻: {cleaned_title[:30]}...")
            
            # 打印新闻信息
            print(f"\n发现新闻:")
            print(f"标题: {cleaned_title}")
            print(f"链接: {link}")
            print(f"来源: {cleaned_source}")
            print(f"时间: {cleaned_time}")
            print(f"摘要: {cleaned_summary}")
            print(f"封面图片: {cleaned_cover}")
            print("-" * 50)
            
            # 控制数量
            if len(news_list) >= num_per_page:
                break
            
        except Exception as e:
            print(f"处理新闻时发生错误: {e}")
            import traceback
            traceback.print_exc()
            continue
    
        # 记录处理结束时间
    processing_end = time.time()
    processing_time = processing_end - processing_start
    
    print(f"关键词 '{keyword}' 第 {page} 页处理完成")
    print(f"提取到 {len(news_list)} 条有效新闻")
    print(f"处理时间: {processing_time:.2f}秒")
    print("=" * 50)
    
    return news_list

# 批量抓取百度新闻函数
def batch_crawl_baidu_news(keywords: List[str], pages: int = 3, num_per_page: int = 10) -> List[Dict[str, Any]]:
    """
    批量抓取百度新闻
    
    Args:
        keywords: 关键词列表
        pages: 每个关键词抓取的页数
        num_per_page: 每页条数
        
    Returns:
        所有抓取的新闻列表
    """
    all_news = []
    
    for keyword in keywords:
        for page in range(1, pages + 1):
            try:
                news_list = crawl_baidu_news(keyword, page, num_per_page)
                all_news.extend(news_list)
                print(f"已抓取关键词 '{keyword}' 第 {page} 页，共 {len(news_list)} 条新闻")
            except Exception as e:
                print(f"抓取关键词 '{keyword}' 第 {page} 页失败: {e}")
                continue
    
    return all_news