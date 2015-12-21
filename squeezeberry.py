#! /usr/bin/python


import sys, getopt
import time, base64, hashlib
import urllib, urllib2, requests
import simplejson
from time import sleep
import threading
import subprocess


# Class qui gere toutes les communications avec le serveur squeezebox
class SqueezeBoxServer():

	def __init__(self, host="127.0.0.1", port=9000):
		self.host = host
		self.port = port
		self.session_id = None
		self.player_id = None
		self.server_url = "http://%s:%s/jsonrpc.js" % (self.host, self.port)
		return

	def getLoginUrl(self, username, password):
		uname = urllib.quote(username)
		t = str(int(time.time()))
		password = urllib.quote(self.sha1_base64(password+t))
		url = "http://www.mysqueezebox.com/api/v1/login?v=sn7.4.1&u="+uname+"&t="+t+"&a="+password
		print url
		return url

	def sha1_base64(self, text):
		return base64.b64encode(hashlib.sha1(text).digest())[0:-1]

	def login(self, email, password):
		print  {"email":email, "password":password}
		r = requests.post("http://mysqueezebox.com/user/login", data = {"email":email, "password":password})
#		print "sdi_squeezenetwork_session", r.text
		# session_id is the auth token for all further calls
		self.session_id = r.cookies['sdi_squeezenetwork_session']
#		print 'sdi_squeezenetwork_session', self.session_id

		# looking for player_id
		cookies = dict(sdi_squeezenetwork_session=self.session_id)
		r = requests.post("http://www.mysqueezebox.com/api/v1/players", cookies=cookies)
		resp = r.text
#		print resp
		pl = simplejson.loads(resp)
		self.player_id = pl['players'][0][u'mac']
#		print self.player_id
		return self.session_id		


	def query(self, *args):
		params = simplejson.dumps({'id':1, 'method':'slim.request', 'params':[self.player_id, list(args)]})
		cookies = dict(sdi_squeezenetwork_session=self.session_id)
		r = requests.post(self.server_url, data=params, cookies=cookies)
		response_text = r.text
		return response_text


	def play(self, *args):
		# https://github.com/Logitech/slimserver/blob/eeeb701d7de3ae2790c359cbd67a4c438c66bf2b/Slim/Control/Request.pm#L527
		print self.query( "mode", "?" )
		print self.query( "sleep", "?" )
		print self.query( "power", "?" )
		print self.query( "time", "?" )
		print self.query( "version", "?" )
#		print self.query( "artist", "?" )
#		print self.query( "title", "?" )
#		print self.query( "album", "?" )

		status = self.query( "status" )
		st = simplejson.loads(status)
		rm = st[u'result'][u'remoteMeta']
		album = rm[u'album']
		artist = rm[u'artist']
		title = rm[u'title']
		print 'playing: ', artist, '-', title, '-', album
		return

		print self.query( "alarms", 0, 9999)
		print self.query( "serverstatus", 0, 9999)
		print self.query( "version", "?") # 7.7.6
		print self.query( "status", "1")
#		print self.query( "mode", "pause")
#		print self.query( "power", "off")
		print self.query( "power", "1")
		print self.query( "mode", "play")
		print self.query( "playlist", "index", 1)
#		print self.query( "mixer", "volume", 20)
		return
		
	def setVolume(self, volume):
		self.query("mixer", "volume", volume)
		
	def getArtists(self):
		return self.artists
		
	def getArtistsCount(self):
		return self.artist_count
	
	def getRadiosCount(self):
		return self.radio_count
	
	def playRadio(self, radio):
		return self.query("favorites", "playlist", "play", "item_id:"+str(radio))
		
	def getArtistAlbum(self, artist_id):
		return self.query("albums", 0, 99, "tags:al", "artist_id:"+str(artist_id))['albums_loop']
		
	def playAlbum(self, id):
		return self.query("playlistcontrol", "cmd:load", "album_id:"+str(id))
		
	def pause(self):
			return self.query("pause")
	
	def previousSong(self):
		return self.query("playlist", "index", "-1")

	def nextSong(self):
		return self.query("playlist", "index", "+1")

	def getCurrentSongTitle(self):
		print self.query("current_title", "?")
		return self.query("current_title", "?")['_current_title']

	def getCurrentRadioTitle(self, radio):
		return self.query("favorites", "items", 0, 99)['loop_loop'][radio]['name']
	

	
		


if __name__ == '__main__':
	try:
		opts, args = getopt.getopt(sys.argv[1:],"hu:p:",["user=","password="])
	except getopt.GetoptError:
		print 'usage: msb.com.py -u email -p password'
		sys.exit(2)

	login = None
	password = None
	for opt, arg in opts:
		if opt == '-h':
			print 'usage: msb.com.py -u email -p password'
			sys.exit()
		elif opt in ("-u", "--user"):
			login = arg
		elif opt in ("-p", "--password"):
			password = arg

	msb = SqueezeBoxServer(host="mysqueezebox.com",port=80)
	msb.login(login, password)
	msb.play()
