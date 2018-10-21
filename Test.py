#coding=utf-8
# -*- coding: utf-8 -*-

from omxplayer.player import OMXPlayer
from omxplayer.bus_finder import  BusFinder
from pathlib import Path
from time import sleep
import logging
logging.basicConfig(level=logging.INFO)


VIDEO_1_PATH = "lvguang.mp3"
player_log = logging.getLogger("Player 1")

player = OMXPlayer(VIDEO_1_PATH, dbus_name='org.mpris.MediaPlayer2.omxplayer1')
player.playEvent += lambda _: player_log.info("Play")
player.pauseEvent += lambda _: player_log.info("Pause")
player.stopEvent += lambda _: player_log.info("Stop")

# it takes about this long for omxplayer to warm up and start displaying a picture on a rpi3
sleep(3)

bf = BusFinder()
print(bf.get_address())


sleep(5)

player.quit()