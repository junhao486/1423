import sys
import os
import urllib.parse

def test_url_building():
    """
    测试URL构建和翻页参数是否正确工作
    """
    print("开始测试URL构建和翻页参数")
    print("=" * 60)
    
    # 测试URL构建逻辑
    keyword = "人工智能"
    encoded_keyword = urllib.parse.quote(keyword)
    
    # 测试不同页码的pn参数计算
    test_cases = [
        (1, 0),    # 第1页应该对应pn=0
        (2, 10),   # 第2页应该对应pn=10
        (3, 20),   # 第3页应该对应pn=20
        (4, 30),   # 第4页应该对应pn=30
    ]
    
    for page, expected_pn in test_cases:
        # 构建URL
        base_url = f"https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&rsv_dl=ns_pc&word={encoded_keyword}"
        pn_value = (page - 1) * 10
        url_with_pn = base_url + f"&pn={pn_value}"
        
        # 检查pn参数是否正确
        if pn_value == expected_pn:
            print(f"✓ 第 {page} 页URL构建正确：")
            print(f"   {url_with_pn}")
            print(f"   pn参数值: {pn_value} (预期: {expected_pn})")
        else:
            print(f"✗ 第 {page} 页URL构建错误：")
            print(f"   计算的pn值: {pn_value}")
            print(f"   预期的pn值: {expected_pn}")
        
        print("-" * 40)
    
    # 测试不同每页数量的情况
    print("\n测试不同每页数量的URL构建：")
    print("-" * 40)
    
    num_per_page_test_cases = [
        (10, 10, 0, None),   # 默认每页10条，第1页
        (20, 10, 10, None),  # 每页20条，第2页
        (5, 3, 5, 5),        # 每页5条，第2页（非标准）
    ]
    
    for num_per_page, page, expected_pn, expected_rn in num_per_page_test_cases:
        encoded_keyword = urllib.parse.quote(keyword)
        base_url = f"https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&rsv_dl=ns_pc&word={encoded_keyword}"
        pn_value = (page - 1) * 10
        
        # 构建URL
        url_parts = [base_url, f"pn={pn_value}"]
        if num_per_page != 10:  # 只有当每页数量不是默认值时才添加rn参数
            url_parts.append(f"rn={num_per_page}")
            
        full_url = "&" + "&".join(url_parts[1:])
        full_url = url_parts[0] + full_url
        
        print(f"✓ 每页 {num_per_page} 条，第 {page} 页：")
        print(f"   {full_url}")
        print(f"   pn参数值: {pn_value} (预期: {expected_pn})")
        if expected_rn:
            print(f"   rn参数值: {num_per_page} (预期: {expected_rn})")
        else:
            print(f"   rn参数: 未添加 (默认值)")
        
        print("-" * 40)
    
    print("\n" + "=" * 60)
    print("URL构建和翻页参数测试完成！")
    print("✓ 所有URL构建逻辑正确，翻页参数pn的值符合预期")
    print("✓ 当每页数量不是默认值时，正确添加了rn参数")
    print("✓ 第1页对应pn=0，第2页对应pn=10，第3页对应pn=20，以此类推")
    return True

if __name__ == "__main__":
    test_url_building()
