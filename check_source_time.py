import re

# 读取完整页面内容
with open('full_page.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 提取所有来源和时间信息
source_time_list = re.findall(r'<span[^>]*class=["\']c-color-gray2["\'][^>]*>(.*?)</span>', html, re.DOTALL)

print(f'提取到的来源时间数量: {len(source_time_list)}')
print('\n前10个来源时间:')
for i, item in enumerate(source_time_list[:10]):
    print(f'{i+1}. {repr(item)}')

# 尝试其他可能的class名
print('\n\n尝试其他可能的class名:')

# 查找所有包含来源或时间的span标签
all_span = re.findall(r'<span[^>]*class=["\'](.*?)["\'][^>]*>(.*?)</span>', html, re.DOTALL)

# 筛选出可能是来源或时间的span
potential_source_time = []
for class_name, content in all_span:
    # 如果内容包含时间相关词汇或网站名称
    if any(word in content for word in ['前', '小时', '分钟', '天', '月', '年']):
        potential_source_time.append((class_name, content))

print(f'找到 {len(potential_source_time)} 个可能的来源时间:')
for class_name, content in potential_source_time[:10]:
    print(f'Class: {repr(class_name)}, 内容: {repr(content)}')
