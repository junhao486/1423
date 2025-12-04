import requests
import zlib
import gzip

# 测试URL和请求头
keyword = '成都'
url = f"https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&rsv_dl=ns_pc&word={keyword}&pn=0"

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    # 禁用压缩
    'accept-encoding': 'identity',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'connection': 'keep-alive',
    'cookie': 'H_WISE_SIDS_BFESS=60948_61006_60941_61027_61024_61036_61055; PSTM=1764750645; BD_UPN=12314753; BIDUPSID=EE83CC6FD339D0BBDE315CEA688E7F9C; delPer=0; BD_CK_SAM=1; PSINO=6; BA_HECTOR=8004212g80852h8584258h2kal24ai1kj1pg325; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; ZFY=aP7D:BM8BB6lh0UD3zSnu:AU2Mv:BWcAD1epinTxuNSYCo:C; channel=bing; baikeVisitId=d48e3324-e0d8-4b9d-ad50-1f1a2f2423a1; BAIDUID=2D541012EC0AD6842A55BAE632418223:FG=1; H_WISE_SIDS=63143_66096_66109_66206_66227_66292_66264_66393_66515_66529_66555_66578_66587_66590_66601_66614_66652_66663_66682_66673_66670_66692_66707_66712_66719_66742_66625_66776_66792_66800; BAIDUID_BFESS=2D541012EC0AD6842A55BAE632418223:FG=1; BDRCVFR[I1GM4qgEDat]=-_EV5wtlMr0mh-8uz4WUvY; H_PS_PSSID=63143_66096_66109_66206_66227_66292_66264_66393_66515_66529_66555_66578_66587_66590_66601_66614_66652_66663_66682_66673_66670_66692_66707_66712_66719_66742_66625_66776_66792_66800; BD_HOME=1; BDRCVFR[C0p6oIjvx-c]=mbxnW11j9Dfmh7GuZR8mvqV; arialoadData=false; BDSVRTM=450',
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

try:
    print(f"测试URL: {url}")
    # 使用会话来保持Cookie
    session = requests.Session()
    response = session.get(url, headers=headers, timeout=10, allow_redirects=True)
    response.raise_for_status()
    
    print(f"\n响应状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"请求头: {dict(response.request.headers)}")
    
    # 尝试不同的解码方式
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
    content = None
    
    for encoding in encodings:
        try:
            content = response.content.decode(encoding)
            print(f"\n使用{encoding}解码成功!")
            break
        except UnicodeDecodeError:
            print(f"使用{encoding}解码失败")
    
    if content:
        print(f"内容长度: {len(content)} 字符")
        
        # 打印部分内容以便查看
        print("\n前1000个字符的内容:")
        print(content[:1000])
        
        # 保存完整内容到文件
        with open('baidu_news_debug.txt', 'w', encoding='utf-8') as f:
            f.write(content)
        print("\n完整内容已保存到 baidu_news_debug.txt 文件")
    else:
        print("所有解码方式都失败了")
        # 保存原始二进制内容
        with open('baidu_news_raw.bin', 'wb') as f:
            f.write(response.content)
        print("原始二进制内容已保存到 baidu_news_raw.bin 文件")
    
except Exception as e:
    print(f"发生错误: {e}")
    import traceback
    traceback.print_exc()
