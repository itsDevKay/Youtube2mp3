#! /usr/bin/env python3
import os
import sys
import time
import argparse
import youtube_dl
import threading #using to open threads to read status while downloading
import requests # using to find the name of the video title
import progressbar

from bs4 import BeautifulSoup as soup
from tqdm import tqdm # progress bar


totalBytes = 40000
ascii_chars = ''
page_title = ''


class Color:
	CYAN = '\033[96m'
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	END = '\033[0m'


class MyLogger(object):
	def debug(self, msg):
		pass

	def warning(self, msg):
		pass

	def error(self, msg):
		print(msg)


def my_hook(d):
	global downloaded_bytes
	global totalBytes
	global pBar
	
	totalBytes = d['total_bytes']
	pBar.start(init=True)

	if d['status'] == 'finished':
		pBar.finish()
		print(Color.BOLD + '\nDone downloading, now converting ...' + Color.END)
	elif d['status'] == 'downloading':
		downloaded_bytes = d['downloaded_bytes']

		# creating a progress bar to skip out on unnecessary lines
		if downloaded_bytes <= d['total_bytes']:
			time.sleep(0.1)
			progressbar.streams.flush()
			downloaded_bytes += d['downloaded_bytes'] # updating value
			pBar.update(downloaded_bytes)
		pBar.finish()


ydl_opts = {
	'format': 'bestaudio/best',
	'postprocessors':[{
		'key': 'FFmpegExtractAudio',
		'preferredcodec': 'mp3',
		'preferredquality': '320',
	}],
	'logger': MyLogger(),
	'progress_hooks': [ my_hook ],
}

def video2mp3( video_link ):
	global pBar 
	pBar = progressbar.ProgressBar(max_error=False)
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		#pBar.start(max_value=progressbar.UnknownLength)
		pBar.start(max_value=totalBytes)
		ydl.download([ video_link ])


def grab_title_name( video_link ):
	global page_title
	r = requests.get(video_link).content
	page = soup(r, 'html.parser')
	page_title, trash = page.title.text.split(' - Y')
	print(Color.BOLD + Color.UNDERLINE + Color.CYAN + '[-] Downloading: ' + page_title + Color.END)


def bash_rename():
	global page_title
	global ascii_chars

	new_title = page_title +'.mp3'
	page_title = page_title +'-'+ ascii_chars +'.mp3'

	os.system('mv "%s" "/home/dextop/Desktop/LoD_Share/Internal Storage/%s"' % (page_title, new_title))
	print(Color.BOLD + Color.YELLOW + '[+] File saved under ~/Destkop/LoD_Share/Internal Storage/%s' % (new_title) + Color.END)


def main(video_link):
	global ascii_chars
	
	print(Color.GREEN + '[-] Starting download process, please wait ...' + Color.END)
	trash, ascii_chars = video_link.split('=')
	grab_title_name( video_link )
	time.sleep(0.5)
	
	video2mp3( video_link )
	time.sleep(0.5)
	
	bash_rename()


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-v', '--video', help=("enter youtube link here to download to mp3"), type=str, required=True)
	args = parser.parse_args()
	main(args.video)
