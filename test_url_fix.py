# 测试图片URL修复逻辑

def fix_image_url(img_src):
    """
    模拟修复图片URL的函数，与utils.py中的逻辑一致
    """
    if not img_src:
        return ""
    
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
    
    return img_src

if __name__ == "__main__":
    # 测试各种URL情况
    test_urls = [
        'https:t9.baidu.com/it/u=123456789,123456789&fm=193&f=GIF',
        'http:t9.baidu.com/it/u=123456789,123456789&fm=193&f=GIF',
        '//t9.baidu.com/it/u=123456789,123456789&fm=193&f=GIF',
        '/t9.baidu.com/it/u=123456789,123456789&fm=193&f=GIF',
        't9.baidu.com/it/u=123456789,123456789&fm=193&f=GIF',
        'https://t9.baidu.com/it/u=123456789,123456789&fm=193&f=GIF',
        'http://t9.baidu.com/it/u=123456789,123456789&fm=193&f=GIF',
        'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/...',
        '//www.baidu.com/img/baidu_jgylogo3.gif'
    ]
    
    print("测试图片URL修复逻辑：")
    print("=" * 60)
    
    for url in test_urls:
        fixed_url = fix_image_url(url)
        print(f"原始URL: {url}")
        print(f"修复后:  {fixed_url}")
        print("-" * 60)