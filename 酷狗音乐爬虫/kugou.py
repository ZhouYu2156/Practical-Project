import hashlib
import json
import os.path
import re
import time
import random

import requests
import urllib3
from colorama import Fore, init

init(autoreset=True)

# 制造请求头, 伪装浏览器身份访问
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
}

# 酷狗认证 token
token = '6939c94fb3f6a910bece970ccbd5439d732747598ac600cb8757652bfaed83b8'

def get_single_song_signature(timestamp, audio_id):
    """
    生成获取单首音乐的加密签名
    :param timestamp: 时间戳
    :param audio_id: `音乐id`
    :return: 单曲音乐的加密签名
    """
    params = [
        "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt",
        "appid=1014",
        f"clienttime={timestamp}",
        "clientver=20000",
        "dfid=4FGxv900QtNq2M7rJX0MjIZI",
        f"encode_album_audio_id={audio_id}",
        "mid=26983d9533541a7156f708491cfeceab",
        "platid=4",
        "srcappid=2919",
        f"token={token}",
        "userid=2175914904",
        "uuid=26983d9533541a7156f708491cfeceab",
        "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"
    ]
    # 实例化md5对象
    md5 = hashlib.md5()
    # 即将要加密的字符串
    s = ''.join(params).encode('utf-8')
    # 更新加密内容
    md5.update(s)
    # 获取加密后的字符串
    _signature = md5.hexdigest()
    return _signature

def get_search_signature(timestamp, keyword, page: int, pagesize: int):
    """
    生成搜索歌曲的加密签名
    :param timestamp 时间戳
    :param keyword: 搜索关键字
    :param page: 搜索结果页码
    :param pagesize: 搜索结果页面数据量
    :return: 搜索歌曲的加密签名
    """
    params = [
        "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt",
        "appid=1014",
        "bitrate=0",
        "callback=callback123",
        f"clienttime={timestamp}",
        "clientver=1000",
        "dfid=4FGxv900QtNq2M7rJX0MjIZI",
        "filter=10",
        "inputtype=0",
        "iscorrection=1",
        "isfuzzy=0",
        f"keyword={keyword}",
        "mid=26983d9533541a7156f708491cfeceab",
        f"page={page}",
        f"pagesize={pagesize}",
        "platform=WebFilter",
        "privilege_filter=0",
        "srcappid=2919",
        f"token={token}",
        "userid=2175914904",
        "uuid=26983d9533541a7156f708491cfeceab",
        "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"
    ]
    # 实例化md5对象
    md5 = hashlib.md5()
    # 即将要加密的字符串
    s = ''.join(params).encode('utf-8')
    # 更新加密内容
    md5.update(s)
    # 获取加密后的字符串
    _signature = md5.hexdigest()
    return _signature

def get_single_music_information(audio_id):
    """
    获取音乐信息
    :param audio_id: 音乐id
    :return: `Response`
    """
    # 构建歌曲信息获取的基础 url
    url = 'https://wwwapi.kugou.com/play/songinfo'
    timestamp = int(time.time() * 1000)
    signature = get_single_song_signature(timestamp, audio_id)
    payload = {
        "srcappid": "2919",
        "clientver": "20000",
        "clienttime": timestamp,
        "mid": "26983d9533541a7156f708491cfeceab",
        "uuid": "26983d9533541a7156f708491cfeceab",
        "dfid": "4FGxv900QtNq2M7rJX0MjIZI",
        "appid": "1014",
        "platid": "4",
        "encode_album_audio_id": audio_id,
        "token": token,
        "userid": "2175914904",
        "signature": signature
    }
    # 获取相应结果
    response = requests.get(url=url, params=payload, headers=headers).json()
    return response

def save_music(audio_id=None):
    """
    保存音乐
    :param audio_id: 音乐id
    :return: None
    """
    if audio_id is None:
        raise ValueError('audio_id is None')
    music_information = get_single_music_information(audio_id)
    # 断言响应是字典类型
    assert type(music_information) is dict, 'response is not a dict'
    data = music_information.get('data', None)
    if data is None:
        return None
    # 断言响应是字典类型
    assert type(data) is dict, 'data is not a dict'
    author_name = data.get('author_name', None)
    song_name = data.get('song_name', None)
    play_backup_url = data.get('play_backup_url', None)
    if not os.path.exists('./static/musics'):
        # 如果不存在则递归创建
        os.makedirs('./static/musics')
    singer = f'./static/musics/{author_name}'
    if not os.path.exists(singer):
        os.mkdir(singer)
    music_file_name = f'{author_name}-{song_name}'
    # print('播放地址: ', play_backup_url)
    if not play_backup_url:
        return None
    print(Fore.GREEN + '正在下载音乐: {}'.format(music_file_name))
    with open(f'./static/musics/{author_name}/{music_file_name}.mp3', 'wb') as fp:
        # 实用 urllib3.request 请求音乐地址, 得到的字节数据在 data 属性中
        fp.write(urllib3.request('GET', play_backup_url, headers=headers).data)
    return data

def get_music_top500_list():
    """
    获取酷狗Top500音乐列表: https://www.kugou.com/yy/rank/home/{n}-8888.html
    n表示页码, 综合其他分类的网址来分析, 我猜测`-`后面的8888这样的数字表示的是分类的代码或者是其他什么东西, 总之跟页码和数据量没有关系
    :return: None
    """
    url = 'https://www.kugou.com/yy/rank/home/{}-8888.html'
    for page in range(1, 24):
        response = requests.get(url=url.format(page), headers=headers)
        audio_id_list = re.findall(r'data-eid="(.*?)">', response.text)
        for audio_id in audio_id_list:
            save_music(audio_id)
            time.sleep(random.randint(1, 5) / 10)
        time.sleep(random.randint(1, 3))

def get_search_music_list(kw="刀郎", page=1, pagesize=30):
    """
    获取搜索音乐信息列表
    :param kw: 关键字搜索
    :param page: 获取搜索结果数据列表的哪一页
    :param pagesize: 获取搜索结果数据列表的多少数据量
    :return: 搜索音乐信息列表
    """
    search_url = 'https://complexsearch.kugou.com/v2/search/song'
    timestamp = int(time.time() * 1000)
    signature = get_search_signature(timestamp, kw, page, pagesize)
    # print(signature)
    payload = {
        "callback": "callback123",
        "srcappid": "2919",
        "clientver": "1000",
        "clienttime": timestamp,
        "mid": "26983d9533541a7156f708491cfeceab",
        "uuid": "26983d9533541a7156f708491cfeceab",
        "dfid": "4FGxv900QtNq2M7rJX0MjIZI",
        "keyword": kw,
        "page": page,
        "pagesize": pagesize,
        "bitrate": "0",
        "isfuzzy": "0",
        "inputtype": "0",
        "platform": "WebFilter",
        "userid": "2175914904",
        "iscorrection": "1",
        "privilege_filter": "0",
        "filter": "10",
        "token": token,
        "appid": "1014",
        "signature": signature,
    }
    response = requests.get(url=search_url, params=payload, headers=headers)
    # print(response.text)
    result = re.findall(r'^callback123\((.*)\)$', response.text)
    # print(len(json.loads(result[0]).get('data').get('lists')))
    return json.loads(result[0]).get('data').get('lists')

def get_multiple_music(pagesize=30):
    with open(file='./musics.json', mode='r+', encoding='utf-8') as fp:
        # 读取原来的数据 => 转换为字典
        store = json.loads(fp.read())
    assert type(store) is dict, 'store is not a dict'
    keyword = input('请输入音乐搜索关键字: ')
    search_music_list = get_search_music_list(kw=keyword, pagesize=pagesize)
    persisted_music_info(search_music_list, store)


def persisted_music_info(search_music_list, store):
    # 持久化保存操作
    for song in search_music_list:
        music_info = save_music(song.get('EMixSongID', None))
        if music_info is None:
                print(Fore.RED + '该音乐不能播放，需要下载客户端, 略过...')
                continue
        assert type(music_info) is dict, 'music_info is not a dict'
        singer = music_info.get('author_name', None)
        songName = music_info.get('song_name', None)
        remote_url = music_info.get('play_backup_url', None)
        cover = music_info.get('img', None)
        lyrics = music_info.get('lyrics', None)
        # print(singer, songName, remote_url, cover, lyrics)
        if not all([singer, songName, remote_url, cover, lyrics]):
            print(Fore.RED + '数据不完整, 略过...')
            continue
        if not store.get(singer, None):
            store[singer] = []
        store[singer].append({
            "songName": songName,
            "cover": cover,
            "playUrl": f'/static/musics/{singer}/{singer}-{songName}.mp3',
            'remote_url': remote_url,
            "lyrics": lyrics
        })
    with open(file='./musics.json', mode='w', encoding='utf-8') as fp:
        json.dump(store, fp, ensure_ascii=False, indent=4)

def get_single_music():
    # 小书子 - 不要慌太阳下山有月光 (弹唱版)
    with open(file='./musics.json', mode='r+', encoding='utf-8') as fp:
    # 读取原来的数据 => 转换为字典
        store = json.loads(fp.read())
    keyword=input('请输入音乐搜索关键字: ')
    search_music_list = get_search_music_list(kw=keyword, pagesize=1)
    persisted_music_info(search_music_list, store)

if __name__ == '__main__':
    # os.startfile(music_path)  # 模拟双击该文件, 让它使用默认的打开软件来启动该文件
    # get_music_top500_list()
    flag = input('1.单曲下载\n2.批量下载音乐(默认一次下载30条)\n3.自定义下载数量\n请输入选项数字: ')
    while flag != '4':
        if flag == '1':
            get_multiple_music(pagesize=1)
        elif flag == '2':
            get_multiple_music()
        elif flag == '3':
            count = int(input('请输入自定义下载数量: '))
            get_multiple_music(pagesize=count)
        else:
            print(Fore.RED + '输入错误, 请重新输入...')
        flag = input('1.单曲下载\n2.批量下载音乐(默认一次下载30条)\n3.自定义下载数量\n4.退出\n请输入选项数字: ')

# ['刀郎', '林俊杰', '邓紫棋', '戚薇', '虎二', '周杰伦', '薛之谦', '鞠婧祎', '于文文', '韩红', '陈楚生', '张杰', '张碧晨', '张靓颖', '张韶涵', '于果', '印子月', '古巨基', '王绎龙', '王力宏', '王心凌', '王靖雯', '王菲', '章子怡', '刘德华', '刘若英', '刘增瞳', '季彦霖']

# 酷狗爬虫教程: https://blog.csdn.net/weixin_63657273/article/details/135637966