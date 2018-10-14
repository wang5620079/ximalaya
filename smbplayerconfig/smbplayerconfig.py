#coding=utf-8
# -*- coding: utf-8 -*-

import logging
import os



"""
配置文件
"""

#日志配置
gloableloglevel = logging.DEBUG
fileloglevel = logging.INFO
consoleloglevel = logging.DEBUG

#samba服务名称
servicename='public'
#目录配置
rootdir='/usbdisk/taijiao'

#临时文件目录
tempdir= os.path.dirname(os.path.abspath(os.path.join(os.path.realpath(__file__), ".."))) + os.path.sep+'temp'



if __name__ == '__main__':
    import tempfile

    file=tempfile.TemporaryFile()

    file.write(b'test')
    print(file.name)
    file.seek(0)
    data = file.read()
    print(str(data,encoding='utf-8'))
    file.close()

    print(os.path.sep)
    foldername=rootdir.split('/')[-1]
    print(foldername)




