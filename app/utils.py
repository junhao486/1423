import re
import jieba
import jieba.analyse
import requests
from datetime import datetime
from typing import List, Dict, Any

# 文本清理函数
def clean_text(text: str) -> str:
    """清理文本，去除特殊字符和多余空格"""
    if not text:
        return ""
    
    # 去除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 去除特殊字符
    text = re.sub(r'[\r\n\t]+', ' ', text)
    
    # 去除多余空格
    text = re.sub(r'\s+', ' ', text)
    
    # 去除首尾空格
    return text.strip()

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
def crawl_baidu_news(keyword: str, page: int = 1, num_per_page: int = 10) -> List[Dict[str, Any]]:
    """
    从百度新闻搜索中抓取关键词相关的新闻
    
    Args:
        keyword: 搜索关键词
        page: 页码
        num_per_page: 每页条数
        
    Returns:
        新闻列表，每条包含标题、概要、封面、原始URL、来源等信息
    """
    # 构建搜索URL - 使用用户指定的URL格式
    import urllib.parse
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&rsv_dl=ns_pc&word={encoded_keyword}&pn={(page-1)*num_per_page}"
    
    # 设置请求头 - 基于用户提供的信息，但禁用压缩以避免乱码
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-encoding': 'identity',  # 禁用压缩，避免乱码
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'connection': 'keep-alive',
        'cookie': 'H_WISE_SIDS_BFESS=60948_61006_60941_61027_61024_61036_61055; PSTM=1764750645; BD_UPN=12314753; BIDUPSID=EE83CC6FD339D0BBDE315CEA688E99C; delPer=0; BD_CK_SAM=1; PSINO=6; BA_HECTOR=8004212g80852h8584258h2kal24ai1kj1pg325; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; ZFY=aP7D:BM8BB6lh0UD3zSnu:AU2Mv:BWcAD1epinTxuNSYCo:C; channel=bing; baikeVisitId=d48e3324-e0d8-4b9d-ad50-1f1a2f2423a1; BAIDUID=2D541012EC0AD6842A55BAE632418223:FG=1; H_WISE_SIDS=63143_66096_66109_66206_66227_66292_66264_66393_66515_66529_66555_66578_66587_66590_66601_66614_66652_66663_66682_66673_66670_66692_66707_66712_66719_66742_66625_66776_66792_66800; BAIDUID_BFESS=2D541012EC0AD6842A55BAE632418223:FG=1; BDRCVFR[I1GM4qgEDat]=-_EV5wtlMr0mh-8uz4WUvY; H_PS_PSSID=63143_66096_66109_66206_66227_66292_66264_66393_66515_66529_66555_66578_66587_66590_66601_66614_66652_66663_66682_66673_66670_66692_66707_66712_66719_66742_66625_66776_66792_66800; BD_HOME=1; BDRCVFR[C0p6oIjvx-c]=mbxnW11j9Dfmh7GuZR8mvqV; arialoadData=false; BDSVRTM=450',
        'host': 'www.baidu.com',
        'sec-ch-ua': '"Chromium";v="142", "Microsoft Edge";v="142", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0'
    }
    
    # 发送请求
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        # 让requests自动处理编码
        response.encoding = response.apparent_encoding
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return []
    
    # 解析HTML
    html = response.text
    
    # 保存HTML到文件以便调试
    with open('baidu_news_debug.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    # 提取新闻列表
    news_list = []
    
    # 查找所有包含新闻条目的容器
    # 新闻条目通常包含在id="content_left"下的div中
    content_left_match = re.search(r'<div[^>]*id=["\']content_left["\'][^>]*>(.*?)</div>', html, re.DOTALL)
    
    if not content_left_match:
        print("没有找到content_left容器")
        return news_list
    
    content_left = content_left_match.group(1)
    
    # 查找所有包含新闻的div（基于之前看到的页面结构）
    # 每个新闻条目都是一个div，包含h3标签和其他信息
    # 我们使用更通用的匹配方式，找到所有可能的新闻条目
    news_items = []
    
    # 从content_left中找到所有的h3标签，每个h3标签对应一个新闻条目
    h3_tags = re.findall(r'<h3[^>]*>.*?</h3>', content_left, re.DOTALL)
    
    print(f"找到 {len(h3_tags)} 个新闻标题")
    
    # 遍历每个h3标签，提取新闻信息
    for h3_tag in h3_tags:
        # 提取标题和链接
        link_match = re.search(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*class=["\'].*?news-title-font_1xS-F.*?["\'][^>]*>(.*?)</a>', h3_tag, re.DOTALL)
        if not link_match:
            continue
            
        link = link_match.group(1)
        title_content = link_match.group(2)
        
        # 过滤掉不是新闻的链接（如登录链接）
        if 'passport.baidu.com' in link:
            continue
        
        # 提取标题文本（去掉注释标签和HTML标签）
        title_text = re.sub(r'<!--.*?-->|<[^>]*>', '', title_content).strip()
        
        # 清理标题
        cleaned_title = clean_text(title_text)
        
        # 确保标题包含关键词或链接包含关键词
        if keyword not in cleaned_title and keyword not in link:
            continue
        
        # 查找h3标签后面的内容，寻找来源、时间和摘要
        # 首先找到h3标签在content_left中的位置
        h3_index = content_left.find(h3_tag)
        if h3_index == -1:
            continue
            
        # 获取h3标签后面的内容，直到下一个h3标签
        next_h3_index = content_left.find('<h3', h3_index + len(h3_tag))
        if next_h3_index == -1:
            h3_following = content_left[h3_index + len(h3_tag):]
        else:
            h3_following = content_left[h3_index + len(h3_tag):next_h3_index]
        
        # 从后续内容中提取来源和时间
        source = ''
        time = ''
        source_time_match = re.search(r'<span[^>]*class=["\']c-color-gray2["\'][^>]*>(.*?)</span>', h3_following, re.DOTALL)
        if source_time_match:
            source_time_text = source_time_match.group(1).strip()
            # 尝试分割来源和时间
            if ' ' in source_time_text:
                source, time = source_time_text.split(' ', 1)
            else:
                source = source_time_text
        
        # 从后续内容中提取摘要
        summary = ''
        summary_match = re.search(r'<span[^>]*class=["\']content-title["\'][^>]*>(.*?)</span>', h3_following, re.DOTALL)
        if summary_match:
            summary = re.sub(r'<!--.*?-->|<[^>]*>', '', summary_match.group(1)).strip()
        
        # 清理数据
        cleaned_source = clean_text(source)
        cleaned_time = clean_text(time)
        cleaned_summary = clean_text(summary)
        
        # 构建新闻对象
        news = {
            '标题': cleaned_title,
            '概要': cleaned_summary,
            '封面': '',  # 暂不提取封面图片
            '原始URL': link,
            '来源': cleaned_source,
            'publish_time': parse_date(cleaned_time),
            'crawl_time': datetime.now(),
            '关键词': keyword
        }
        news_list.append(news)
        
        # 控制数量
        if len(news_list) >= num_per_page:
            break
    
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