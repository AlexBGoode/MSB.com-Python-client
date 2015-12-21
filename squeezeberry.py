#! /usr/bin/python


import time, base64, hashlib
import urllib, urllib2, requests
import simplejson
from time import sleep
import threading
import subprocess


# Class qui gere toutes les communications avec le serveur squeezebox
class SqueezeBoxServer():

	def __init__(self, host="127.0.0.1", port=9000, player_id=""):
		self.host = host
		self.port = port
		self.player_id = player_id
		self.session_id = 1
		self.server_url = "http://%s:%s/jsonrpc.js" % (self.host, self.port)

		self.session_id = self.login("me@gmail.com", "pass")

#		self.artists = self.query( "players", 0, 9999)
#		self.artists = self.query( "artists", 0, 9999)['artists_loop']

		# https://github.com/Logitech/slimserver/blob/eeeb701d7de3ae2790c359cbd67a4c438c66bf2b/Slim/Control/Request.pm#L527
		print self.query( "mode", "?" )

		print self.query( "sleep", "?" )
		print self.query( "power", "?" )
		print self.query( "time", "?" )
		print self.query( "version", "?" )
		print self.query( "artist", "?" )
		print self.query( "title", "?" )
		print self.query( "album", "?" )

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
		r = requests.post("http://mysqueezebox.com/user/login", data = {"email":email, "password":password})
#		print "sdi_squeezenetwork_session", r.text
		self.session_id = r.cookies['sdi_squeezenetwork_session']
		print 'sdi_squeezenetwork_session', self.session_id
#		user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"
		return self.session_id		


	def query(self, *args):
		params = simplejson.dumps({'id':1, 'method':'slim.request', 'params':[self.player_id, list(args)]})
		cookies = dict(sdi_squeezenetwork_session=self.session_id)
		r = requests.post(self.server_url, data=params, cookies=cookies)
#		req = urllib2.Request(self.server_url, params)
#		response = urllib2.urlopen(req)
#		response_txt = response.read()
#		print(response_txt)
#		return simplejson.loads(response_txt)['result']
		response_text = r.text
#		print response_text
		return response_text
		
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
	


class App(threading.Thread):
	
	def __init__(self):    
		self.current_artist=0
		self.current_artist_album_count=0
		self.current_radio=0
		self.current_album=0
		self.left=False
		self.right=False
		self.push=False
		self.back=False
		self.level="root"
		self.cursor=0
		self.sbs = SqueezeBoxServer(host="mysqueezebox.com",port=80, player_id="00:04:20:28:bd:1e")
#		self.sbs.setVolume(30)
#		print self.sbs.getCurrentSongTitle()
		self.paused = False
		threading.Thread.__init__(self)
		
		


if __name__ == '__main__':
	ui = App()
	ui.start() 
	q = str(raw_input('Press ENTER to quit program\n'))
	ui.Stop()
