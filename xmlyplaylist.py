#coding=utf-8
# -*- coding: utf-8 -*-


import platform
import logging
import os
import time
import math
import json
import re
import requests
from http import cookiejar
from bs4 import BeautifulSoup
from xmlyplaylist import config as xmlyplaylistcfg

###############################################日志设置######################################
#日志模块设置--文件日志
# 第一步，创建一个logger
logger = logging.getLogger()
logger.setLevel(xmlyplaylistcfg.gloableloglevel)  # Log等级总开关
# 第二步，创建一个handler，用于写入日志文件
rq = time.strftime('%Y-%m-%d', time.localtime(time.time()))
script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
log_path = script_dir + '/logs/'
#如果不存在定义的日志目录就创建一个
if not os.path.isdir(log_path):
    os.mkdir(log_path)
#获取脚本名称，并以脚本名称作为日志名
log_name = log_path +os.path.basename(os.path.realpath(__file__)).split('.')[0]+ rq + '.log'
logfile = log_name
fh = logging.FileHandler(logfile, mode='w',encoding='utf-8')
#文件日志级别
fh.setLevel(xmlyplaylistcfg.fileloglevel)

# 第三步，定义handler的输出格式
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
# 第四步，将logger添加到handler里面
logger.addHandler(fh)

#日志模块--控制台日志
ch = logging.StreamHandler()
ch.setLevel(xmlyplaylistcfg.consoleloglevel)
ch.setFormatter(formatter)
logger.addHandler(ch)


######################################正式开始代码##################################################

# cookie初始化
httpsession = requests.session()
newcj = cookiejar.LWPCookieJar()
httpsession.cookies = newcj

#基础函数，获取网页
def gethtml(url):
    logger.info("******************************开始获取网页************************************")
    logger.info('url={}'.format(url))
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host':'www.ximalaya.com',
        'Upgrade-Insecure-Requests':'1',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.17 Safari/537.36'
    }

    try:
        res=None
        res = httpsession.get(url, headers=headers)
    except Exception as e:
        logger.error('Error code:', str(e))
    if res==None:
        logger.error('未获取数据')
        raise Exception('未获取数据')
    page = res.text
    logger.info("******************************获取网页完成************************************")
    return page


#url文件扫描器，扫描文件，并解析出需要的url
def parseUrls():
    #先检测url配置文件在不在
    if not os.path.exists(xmlyplaylistcfg.urlsconfig):
        logger.error('url配置文件不存在')
        raise Exception('url配置文件不存在')
    #按行读取配置文件
    lines=[]
    with open(xmlyplaylistcfg.urlsconfig, 'r', encoding='utf-8') as file:
        for line in file:
            linstr=line.strip()
            if len(linstr)>0:
                lines.append(line.strip())
    logging.debug('读取到的配置文件为：\r\n{}'.format(str(lines)))

    addr_regex = re.compile(r"""http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+""")  # 匹配网址，
    urllst=[]
    for line in lines:
        for groups in addr_regex.findall(line):
            urllst.append(groups)
    logger.debug('匹配到的url是:{}'.format(str(urllst)))
    #开始解析网页，并生成基础信息
    metainfolst=[]
    for url in urllst:
        #获取id
        strlst = url.split('/')
        if url.endswith('/'):
            id = strlst[-2]
        else:
            id=strlst[-1]
        htmldata = gethtml(url=url)
        soup = BeautifulSoup(htmldata, 'html.parser')
        titlelst = soup.select('.o77S .title')
        logger.info('titlelst={}'.format(str(titlelst)))
        if len(titlelst)==0:
            logger.error('输入的url {}  无效！'.format(url))
            raise Exception('输入的url {}  无效！'.format(url))
        title = titlelst[0].text
        #过滤输出文件夹中的冒号，括号
        album = re.sub(':|：|\(|（|\)|）','_',str(title))
        #去掉其中的空格
        album = re.sub(' ', '', str(album))

        logger.info('make album {}'.format(album))
        lst = soup.select('div .dOi2 .head > h2')
        cntstrlst = re.findall(r'\d+',str(lst[0].text))
        cnt=int(cntstrlst[0])
        logger.info('cnt={}'.format(cnt))
        metainfolst.append((id,album,cnt))
    return metainfolst

#根据基础信息获取json数据，并生成要生成播放列表的文件和url清单
#解析json字符串
def parsejson(jsonstr):
    if jsonstr==None:
        return None
    jsonobj=json.loads(jsonstr)
    datalst=jsonobj['data']['tracksAudioPlay']
    print(len(datalst))
    infodict=dict()
    for datadict in datalst:
        trackName=datadict['trackName']
        src=datadict['src']
        #截取文件名
        if '：' in trackName:
            fname = trackName[trackName.index('：') + 1:].strip()
        else:
            fname=trackName
        #去掉括号等的异常字符
        fname=re.sub(':|：|\(|（|\)|）','_',str(fname))
        infodict[fname+'.m4a']=src
    return infodict

#生成播放列表工具
def cmd_download(fname,url,albumdir=None):
    try:
        if not albumdir:
            if 'Windows' == platform.system():
                cmdstr = r'you-get --debug -o {} -O "{}" {}'.format(albumdir, fname, url)
            else:
                cmdstr = r'/home/wp/you-get/you-get --debug -O "{}" {}'.format(fname, url)
        else:
            if 'Windows' == platform.system():
                cmdstr = r'you-get --debug -o {} -O "{}" {}'.format(albumdir, fname, url)
            else:
                cmdstr = r'/home/wp/you-get/you-get --debug -o {} -O "{}" {}'.format(albumdir,fname, url)
        logger.info(cmdstr)
        info = os.system(cmdstr)
        logger.debug(info)
    except Exception as e:
        logger.error(str(e))

#创建专辑目录
def mkAlbumdir(album):
    albumdir = xmlyplaylistcfg.workdir + album
    if  not os.path.exists(albumdir):
        os.makedirs(albumdir)
        logger.info('make albumdir {}'.format(albumdir))
    return albumdir

#获取专辑信息
def getAlbumInfo(id,album,cnt):
    #先创建专辑目录
    albumdir=mkAlbumdir(album)
    #获取专辑信息
    urltemplet='https://www.ximalaya.com/revision/album/getTracksList?albumId={}&pageNum='.format(id)
    #计算有多少页
    numtop=math.ceil(cnt/30)
    urllst=[urltemplet+str(i) for i in range(1,numtop+1)]
    albuminfodict=dict()
    for urldata in urllst:
        jsonstr = gethtml(url=urldata)
        jsonobj = json.loads(jsonstr)
        datalst=jsonobj['data']['tracks']
        for data in datalst:
            index=data['index']
            title=data['title']
            fname = re.sub(':|：|\(|（|\)|）', '_', str(title))+'.m4a'#文件名过滤特殊字符
            playCount=data['playCount']
            trackId=data['trackId']
            url=data['url']
            createDateFormat=data['createDateFormat']
            albuminfodict[fname]={'fname':fname,'index':index,'playCount':playCount,'trackId':trackId,'url':url,'createDateFormat':createDateFormat}
    #生成json字符串，并直接写入json文件中
    jsonfilepath=albumdir+os.path.sep+'AlbumInfo.json'
    json.dump(albuminfodict,open(jsonfilepath,'w'))
    logger.info('write albuminfo to {}'.format(jsonfilepath))


#生成播放列表专辑
def downloadAlbum(id,album,cnt):
    if cnt>500:
        logger.info('生成播放列表文件数量大于500，分页生成播放列表！')
        downloadinfodict = dict()
        pagecnt=math.ceil(cnt/500)
        logger.info('分页数{}'.format(pagecnt))
        for pagenum in range(1,pagecnt+1):
            jsonstr = gethtml(url='https://www.ximalaya.com/revision/play/album?albumId={}&pageNum={}&sort=-1&pageSize={}'.format(id,pagenum,500))
            tmpdownloadinfodict=parsejson(jsonstr)
            downloadinfodict.update(tmpdownloadinfodict)
    else:
        jsonstr = gethtml(url='https://www.ximalaya.com/revision/play/album?albumId={}&pageNum=1&sort=-1&pageSize={}'.format(id, cnt))
        downloadinfodict=parsejson(jsonstr)
    #创建专辑目录
    albumdir= mkAlbumdir(album)
    #写入专辑信息json
    getAlbumInfo(id, album, cnt)
    # 列出目录下的文件列表,路径是绝对路径
    filelst = os.listdir(albumdir)
    # 找出已生成播放列表的文件，并存储到tnplst中，然后删除
    tmplst = []
    for fname in downloadinfodict.keys():
        if fname in filelst:
            tmplst.append(fname)
    # 删除不需要生成播放列表的文件
    for fname in tmplst:
        downloadinfodict.pop(fname)
    logger.info('专辑"{}"的 {} 文件已存在，不再生成播放列表'.format(album, ','.join(tmplst)))

    #开始生成播放列表
    for fname,url in downloadinfodict.items():
        logger.info('start download {}'.format(fname))
        cmd_download(fname=fname, url=url, albumdir=albumdir)
        logger.info('finish download {}'.format(fname))
    pass

#批量生成播放列表
def batdownloadAlbum(metainfolst):
    if not metainfolst:
        logger.error('未传入有效的专辑信息！')
        raise Exception('未传入有效的专辑信息')
    logger.info('********************开始批量生成播放列表*******************')
    for id,album,cnt in metainfolst:
        downloadAlbum(id,album,cnt)
        logger.info('********************批量生成播放列表完成*******************')

#加锁
def lock():
    filepath= xmlyplaylistcfg.workdir + "lock.lck"
    lockfile = open(filepath, 'w')
    lockfile.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    lockfile.flush()
    lockfile.close()

def unlock():
    filepath = xmlyplaylistcfg.workdir + "lock.lck"
    if os.path.exists(filepath):
        os.remove(filepath)

def islocked():
    filepath = xmlyplaylistcfg.crtdir + "lock.lck"
    return os.path.exists(filepath)

def main():
    if islocked():
        print('{} 有其他进程在生成播放列表，退出！'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
        exit(0)
    else:
        lock()
    try:
        metainfolst=parseUrls()
        batdownloadAlbum(metainfolst)
    except Exception as e:
        logger.error(str(e))
    finally:
        unlock()

def test():
    metainfolst = parseUrls()
    for id,album,cnt in metainfolst:
        getAlbumInfo(id,album,cnt)

if __name__=='__main__':
    main()