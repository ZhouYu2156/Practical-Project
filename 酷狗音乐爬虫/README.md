# 酷狗音乐爬取

## 功能说明

> 可以批量爬取酷狗的免费、付费音乐，支持关键字搜索爬取，功能和酷狗的关键字搜索音乐列表是一样的。

## 安装环境

```bash
$ pip install requests urllib3 colorama
```

## 运行程序

```bash
$ python kugou.py
```

## 具体模块介绍

### 1. 获取单首歌曲的签名

- 前提须知: 单首歌曲的签名由时间戳、音乐id(只有这两个参数是变化的)和其他固定的载荷参数一起拼接成字符串后，再将该字符串通过md5加密算法计算出来。

```python
def generate_get_single_song_signature(timestamp, audio_id):
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
        "token=6939c94fb3f6a910bece970ccbd5439dbd5e240383404c3401a1620e305b8275",
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
```

### 2. 获取搜索歌曲列表的签名

- 前提须知: 获取搜索歌曲列表的签名和单首音乐的签名生成类似，将搜索音乐关键字替换歌曲id即可。其他载荷参数需要在发起搜索时执行的JS脚本中打断点获取。

```python
def generate_get_search_signature(timestamp, keyword, page: int, pagesize: int):
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
        "token=6939c94fb3f6a910bece970ccbd5439dbd5e240383404c3401a1620e305b8275",
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
```

### 3. 获取单首歌曲的音乐信息

- 由于载荷和签名都有了，那么就可以确定要获取哪一首音乐的数据了。向获取音乐信息的url发起请求，将载荷传递给服务器即可。服务器会根据是否是会员返回试听的音乐信息(非VIP身份)或者完整的音乐信息(VIP身份)。

```python
def get_single_music_information(audio_id):
    """
    获取音乐信息
    :param audio_id: 音乐id
    :return: `Response`
    """
    # 构建歌曲信息获取的基础 url
    url = 'https://wwwapi.kugou.com/play/songinfo'
    timestamp = int(time.time() * 1000)
    signature = generate_get_single_song_signature(timestamp, audio_id)
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
        "token": "6939c94fb3f6a910bece970ccbd5439dbd5e240383404c3401a1620e305b8275",
        "userid": "2175914904",
        "signature": signature
    }
    # 获取相应结果
    response = requests.get(url=url, params=payload, headers=headers).json()
    return response
```

### 4. 下载并保存音乐

- 获取到单首音乐信息后，就可以根据音乐信息中的`play_url`或```play_backup_url`属性获取到音乐文件的下载地址并进行下载。

```python
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
    if not os.path.exists('./musics'):
        os.mkdir('./musics')
    music_file_name = f'{author_name}-{song_name}'
    with open(f'./musics/{music_file_name}.mp3', 'wb') as fp:
        # 实用 urllib3.request 请求音乐地址, 得到的字节数据在 data 属性中
        fp.write(urllib3.request('GET', play_backup_url, headers=headers).data)
    print(Fore.GREEN + '正在下载音乐: {}'.format(music_file_name))
```

### 5. 榜单音乐获取

- 单首音乐的下载已经知道了，那么获取多首音乐无非来个重复的操作而已。在榜单音乐信息列表中，有每首音乐的id信息，而我们下载音乐的关键就在于需要拿到这个音乐id构造签名，然后向服务器发起请求即可获取到音乐的详细信息，其中就包括了我们需要的音乐的下载地址和其他音乐的基本信息。

```python
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
```

### 6. 获取搜索音乐列表信息

- 因为前面我们已经分析出了搜索音乐加密签名的生成，所以我们只需要根据关键字来生成签名和组装载荷信息发送给服务器即可。另外，搜索音乐还支持传递分页、分页数据量参数给后端进行分页并获取后端分页后的音乐搜索列表。

```python
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
    signature = generate_get_search_signature(timestamp, kw, page, pagesize)
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
        "token": "6939c94fb3f6a910bece970ccbd5439dbd5e240383404c3401a1620e305b8275",
        "appid": "1014",
        "signature": signature,
    }
    response = requests.get(url=search_url, params=payload, headers=headers)
    # print(response.text)
    result = re.findall(r'^callback123\((.*)\)$', response.text)
    # print(len(json.loads(result[0]).get('data').get('lists')))
    return json.loads(result[0]).get('data').get('lists')
```

> 项目代码: [访问我的github仓库](https://github.com/ZhouYu2156/Practical-Project/)



