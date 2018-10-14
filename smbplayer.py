#coding=utf-8
# -*- coding: utf-8 -*-

#下载歌曲的临时文件
import tempfile,logging,time,os,json,re
from pathlib import Path
from omxplayer.player import OMXPlayer
#python访问samba服务
from smb.SMBConnection import SMBConnection

#引入配置文件
from smbplayerconfig import smbplayerconfig

###############################################日志设置######################################
#日志模块设置--文件日志
# 第一步，创建一个logger
logger = logging.getLogger()
logger.setLevel(smbplayerconfig.gloableloglevel)  # Log等级总开关
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
fh.setLevel(smbplayerconfig.fileloglevel)

# 第三步，定义handler的输出格式
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
# 第四步，将logger添加到handler里面
logger.addHandler(fh)

#日志模块--控制台日志
ch = logging.StreamHandler()
ch.setLevel(smbplayerconfig.consoleloglevel)
ch.setFormatter(formatter)
logger.addHandler(ch)

######################################正式开始代码##################################################
#全局静态变量
#播放模式
ORDERPLAY=0   #顺序播放
RAMDOMPLAY=1  #随机播放
HOTPLAY=3     #根据播放量播放
HOTREVPLAY=4  #根据播放量的反向播放
#循环模式
NOLOOP=0     #不循环
LOOPFOREVER=1#永久循环
LOOPn=2      #循环n次





#全局samba对象
samba=None

#初始化，创建samba对象
def init():
    global samba
    #创建临时工作目录

    tempdir = smbplayerconfig.tempdir
    if not os.path.exists(tempdir):
        os.makedirs(tempdir)
        tempfile.tempdir=tempdir
        logger.info('创建 tempfile.tempdir {}'.format(tempdir))

    # 初始化一个samba访问对象
    samba = SMBConnection('anonymous', '', 'wp-PC', 'wp-32G')
    # 创建一个samba连接
    assert samba.connect('192.168.0.185', 139)  # 返回True/False
    logger.info('成功创建samba连接！')


def close():
    if not samba:
        logger.error('关闭samba时，传入空参数')
        raise Exception('关闭samba时，传入空参数')
    if isinstance(samba,SMBConnection):
        samba.close()
        logger.info('samba连接关闭')
    else:
        logger.error('关闭samba时，传入空参数')
        raise Exception('传入的参数不是SMBConnection对象')


#递归遍历工作目录，找出其中的专辑以及专辑信息
#参数名称：遍历路径、allinfolst存储了遍历的结果，数据结构形式为[(folderpath0,albunname0,albuminfo0,filelist0),(folderpath1,albunname1,albuminfo1,filelist1),……]
def getAllAlbumInfo(folderpath=None, allinfolst=None):
    logger.debug('*************************进入遍历获取专辑信息*************************')
    # logger.debug('folderpath={}, allinfolst={}'.format(folderpath,allinfolst))
    #如果是首次遍历
    if None==folderpath  and None==allinfolst:
        folderpath=smbplayerconfig.rootdir
        allinfolst=[]


    logger.debug('folderpath={}'.format(folderpath))
    smbflst = samba.listPath(smbplayerconfig.servicename, folderpath)
    #获取文件列表:
    filenamelst = [smbf.filename for smbf in smbflst if not smbf.isDirectory]
    # logger.debug('目录{}获取文件列表 {}'.format(folderpath,filenamelst))
    # filenamelst=[smbf.filename for smbf in smbflst if not smbf.isDirectory and '.m4a' in smbf.filename]
    # 获取目录列表,并过滤:
    foldernamelst = [smbf.filename for smbf in smbflst if
                     smbf.isDirectory and smbf.filename not in ['.', '..', 'logs', '__pycache__', 'temp']]

    #如果目录中有'AlbumInfo.json'文件，则认为该目录是一个专辑目录,则读取专辑信息
    # 先将专辑信息下载到临时文件中
    if 'AlbumInfo.json' in filenamelst:
        albuminfo = None
        #获取'AlbumInfo.json'文件路径
        filepath= folderpath + os.path.sep + 'AlbumInfo.json'
        with tempfile.TemporaryFile() as fp:
            file_attributes, filesize = samba.retrieveFile(smbplayerconfig.servicename, filepath, fp)
            fp.seek(0)
            data=fp.read()
            jsonstr=data.decode("utf-8")
            albuminfo = json.loads(jsonstr)
            logger.info('读取AlbumInfo.json成功')
            #添加专辑信息
            albunname=os.path.split(folderpath)[-1]
            # logger.debug('添加专辑信息 albunname={}，albuminfo={}，filenamelst={}'.format(albunname, albuminfo, filenamelst))
            # logger.debug('添加专辑信息 albunname={}，filenamelst={}'.format(albunname,filenamelst))
            #整理文件列表，删除json文件
            filenamelst.remove('AlbumInfo.json')
            allinfolst.append((albunname,folderpath, albuminfo, filenamelst))
        return
    #如果不是专辑目录，则开始遍历子目录
    else:
        for folder in foldernamelst:
            logger.debug('继续遍历目录：{}'.format(folder))
            getAllAlbumInfo(folderpath+os.path.sep+folder, allinfolst)
    return allinfolst


#播放单独一个歌曲
def play(filename,fppath):
    try:
        filepath = Path(fppath)
        player = OMXPlayer(filepath)
        logger.info('开始播放文件{},文件时长{}'.format(filename, player.duration()))
        time.sleep(player.duration())
    except Exception as e:
        logger.exception(e)
    finally:
        #最后一定要退出
        if player:
            player.quit()

#带缓冲播放专辑,默认顺序播放
def playalbun(albunname,folderpath, albuminfo, filenamelst,playmode=ORDERPLAY,loopmode=NOLOOP,**kwargs):
    logger.debug('*************************开始播放专辑*************************')
    cnt=0
    loopn=1
    if kwargs and 'loopn' in kwargs.keys():
        loopdata=kwargs.get('loopn')
        if loopdata and isinstance(loopdata,(int,str)):
            if isinstance(loopdata,str) and re.match(r'\d+',loopdata):
                loopn=int(loopdata)
            else:
                loopn=loopdata
        else:
            logger.critical('输入的循环次数参数{}不合法！默认不循环.'.format(loopdata))
    else:
        logger.critical('未输入循环参数！默认不循环.')

    # 已经播放过的文件
    playedlst=[]
    #如果播放模式是按照播放热度播放
    if playmode==HOTPLAY or HOTREVPLAY:
        tmplist = []
        #根据播放热度生成顺序列表
        for filename in albuminfo:
            tmplist.append((albuminfo[filename]['fname'],int(albuminfo[filename]['playCount'])))
        tmplist.sort(key=lambda tmp:tmp[1],reverse=playmode==HOTREVPLAY)
        #过滤无效的文件名
        playlist=[item[0] for item in tmplist if item[0] in filenamelst]
    else:
        # 默认播放列表是文件列表
        playlist = filenamelst
    logger.info('生成播放列表完成，播放列表为：{}'.format(playlist))
    logger.info('#############开始缓冲播放###########')
    crtfile = None
    bakfile=None
    headptr=None
    bakptr=None
    try:
        while cnt<loopn:
            if headptr==None:
                headptr=0
                bakptr=headptr+1
            elif headptr==len(playlist)-1:
                bakfile=0
                cnt = cnt + 1
            elif headptr==len(playlist):
                headptr=0
                bakptr=headptr+1
            else:
                bakptr=headptr+1
            #如果是刚开始播放，则开始就缓冲文件
            if crtfile == None:
                logger.debug('i==0，开始缓冲文件{}'.format(playlist[headptr]))
                crtfile=open(smbplayerconfig.tempdir+os.path.sep+'crtfile.m4a',mode='wb+')
                # 缓冲文件远程路径
                filepath = folderpath + os.path.sep + playlist[headptr]
                #缓冲文件
                samba.retrieveFile(smbplayerconfig.servicename, filepath, crtfile)
                logger.debug('缓冲文件 {} 完成！'.format(playlist[headptr]))
                logger.debug('设置当前播放文件指针到文件{}'.format(playlist[headptr]))
            #开始播放当前文件
            logger.debug('开始播放')
            try:
                logger.debug(crtfile.name)
                filepath = Path(crtfile.name)
                playstarttime=time.time()
                player = OMXPlayer(filepath)
                durtime=player.duration()
                logger.info('开始播放文件{},文件时长{}'.format(playlist[headptr], player.duration()))
                #休眠3秒钟，等待文件开始播放
                time.sleep(3)
                #缓冲下个文件
                logger.debug('开始缓冲bak文件{}'.format(playlist[bakptr]))
                bakfile = open(smbplayerconfig.tempdir+os.path.sep+'bakfile.m4a',mode='wb+')
                # 缓冲文件远程路径
                filepath = folderpath + os.path.sep + playlist[bakptr]
                samba.retrieveFile(smbplayerconfig.servicename, filepath, bakfile)
                downloadtime=time.time()
                logger.debug('缓冲bak文件 {} 完成！'.format(playlist[bakptr]))
                #等待播放完成
                logger.debug('继续等待 {} 秒以完成播放'.format(durtime+3.0-(downloadtime-playstarttime)))
                time.sleep(durtime+3.0-(downloadtime-playstarttime))
                # # 退出
                # try:
                #     if player:
                #         player.quit()
                # except Exception as e:
                #     logger.error('{} 播放进程已不存在，无需杀掉进程'.format(str(e)))
                logger.debug('文件 {} 播放完成！退出播放。'.format(playlist[headptr]))
            except Exception as e:
                logger.exception(e)
            # finally:
            #     try:
            #         if player:
            #             player.quit()
            #     except Exception as e:
            #         logger.error('{} 播放进程已不存在，无需杀掉进程'.format(str(e)))
            #关闭当前文件
            # crtfile.close()
            crtfile,bakfile=bakfile,crtfile
            headptr=headptr+1
    except Exception as e:
        logger.exception(e)
    finally:
        if player:
            player.quit()
        if crtfile and not crtfile.closed:
            crtfile.close()
        if bakfile and not bakfile.closed:
            bakfile.close()
        os.remove(smbplayerconfig.tempdir+os.path.sep+'crtfile.m4a')
        os.remove(smbplayerconfig.tempdir+os.path.sep+'bakfile.m4a')






if __name__ == '__main__':
    init()
    allinfolst=getAllAlbumInfo()
    albunname, folderpath, albuminfo, filenamelst = allinfolst[0]
    playalbun(albunname, folderpath, albuminfo, filenamelst,playmode=HOTPLAY)

    close()

