#!/usr/bin/python

# Author : Shirish Saxena
# Version : 0.43v
# Copyright to Shirish [ me@shirish.me ] @ 2015


import time
import socket
import re
class Player:
	def __init__(self, name, frags, ping, address=None, bot=-1):
		self.name = name
		self.frags = frags
		self.ping = ping
		self.address = address
		self.bot = bot
	def __str__(self):
		return self.name
	def __repr__(self):
		return str(self)

class Main:
	packet_prefix = '\xff' * 4
	player_reo = re.compile(r'^(\d+) (\d+) "(.*)"')
	def __init__(self, server, rcon_password=''):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.set_server(server)
		self.set_rcon_password(rcon_password)
	def set_server(self, server):
		try:
			self.address, self.port = server.split(':')
		except:
			raise Exception('Server address must be in the format of \
					"address:port"')
		self.port = int(self.port)
		self.s.connect((self.address, self.port))
	def get_address(self):
		return '%s:%s' % (self.address, self.port)
	def set_rcon_password(self, rcon_password):
		self.rcon_password = rcon_password
	def send_packet(self, data):
		self.s.send('%s%s\n' % (self.packet_prefix, data))
	def recv(self, timeout=20):
		self.s.settimeout(timeout)
		try:
			return self.s.recv(4096)
		except socket.error, e:
			raise Exception('Error receiving the packet: %s' % \
					e[1])
	def command(self, cmd, timeout=20, retries=3):
		while retries:
			self.send_packet(cmd)
			try:
				data = self.recv(timeout)
			except:
				data = None
			if data:
				return self.parse_packet(data)
			retries -= 1
		raise Exception('Server response timed out')
	def rcon(self, cmd):
		r = self.command('rcon "%s" %s' % (self.rcon_password, cmd))
		if r[1] == 'No rconpassword set on the server.\n' or r[1] == \
				'Bad rconpassword.\n':
			raise Exception(r[1][:-1])
		return r
	def parse_packet(self, data):
		if data.find(self.packet_prefix) != 0:
			raise Exception('Malformed packet')
		first_line_length = data.find('\n')
		if first_line_length == -1:
			raise Exception('Malformed packet')
		response_type = data[len(self.packet_prefix):first_line_length]
		response_data = data[first_line_length+1:]
		return response_type, response_data
	def parse_status(self, data):
		split = data[1:].split('\\')
		values = dict(zip(split[::2], split[1::2]))
		
		for var, val in values.items():
			pos = val.find('\n')
			if pos == -1:
				continue
			split = val.split('\n', 1)
			values[var] = split[0]
			self.parse_players(split[1])
		return values
	def parse_players(self, data):
		self.players = []
		for player in data.split('\n'):
			if not player:
				continue
			match = self.player_reo.match(player)
			if not match:
				print 'couldnt match', player
				continue
			frags, ping, name = match.groups()
			self.players.append(Player(name, frags, ping))
	def update(self):
		cmd, data = self.command('getstatus')
		self.vars = self.parse_status(data)
	def rcon_update(self):
		cmd, data = self.rcon('status')
		lines = data.split('\n')
		players = lines[3:]
		self.players = []
		for p in players:
			while p.find('  ') != -1:
				p = p.replace('  ', ' ')
			while p.find(' ') == 0:
				p = p[1:]
			if p == '':
				continue
			p = p.split(' ')
			self.players.append(Player(p[3][:-2], p[0], p[1], p[5], p[6]))

def Clean_Name(Hostname):
        global Server_Name
        Hostname = Hostname.replace('^1','')
        Hostname = Hostname.replace('^2','')
        Hostname = Hostname.replace('^3','')
        Hostname = Hostname.replace('^4','')
        Hostname = Hostname.replace('^5','')
        Hostname = Hostname.replace('^6','')
        Hostname = Hostname.replace('^7','')
        Hostname = Hostname.replace('^8','')
        Hostname = Hostname.replace('^9','')
        Hostname = Hostname.replace('^0','')
        Server_Name = Hostname
def ServerSelect(IP):
        ad = Main(IP,'')
        ad.update()
        Clean_Name(ad.vars['sv_hostname'])
        print """


###############################################################################
#                                                                             #
# Server Name : %s           
#                                                                             #
###############################################################################
#                                                                             #
# Online Players : %s/%s
# Current map    : %s
# Gametype       : %s
# Punkbuster     : %s
# Password       : %s
###############################################################################



""" %( Server_Name,len(ad.players),ad.vars['sv_maxclients'],ad.vars['mapname'],ad.vars['g_gametype'],ad.vars['sv_punkbuster'],ad.vars['pswrd'])

def Start():
        Servers = raw_input("Enter IP:Port : ")
        while True:
                print ''
                
                if ':' in Servers :
                        ServerSelect(Servers)
                        raw_input('Press Any Key to exit')
                        break
                elif ':' not in Servers :
                        print ''
                        print 'Error : Format Should be IP:Port or Hostname:Port'
                        print 'Example : 1.2.3.4:28960'
                elif Servers == 'exit':
                        print '''Bye Bye'''
                        exit()

                else :
                        print '-----------------------------------------------------------'
                        print '-                    Error : Try Again                    -'
                        print '-----------------------------------------------------------'

Start()
