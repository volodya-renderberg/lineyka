#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import platform
import json
import sqlite3
import datetime
import getpass
import random
import shutil

try:
	from .lineyka_publish import publish
except:
	from lineyka_publish import publish
	
def NormPath(input_path):
	if not input_path:
		return(input_path)
	if platform.system() == 'Windows':
			# windows
			path = str(input_path)
			path = os.path.normpath(path.encode('string-escape'))
	else:
		# linux etc...
		path = os.path.normpath(input_path)
	return(path)
	
class studio:
	'''
	@classmethod get_studio()
	@classmethod make_init_file()
	@classmethod get_list_projects()
	'''
	# 
	farme_offset = 100
	# studio
	studio_folder = False
	tmp_folder = False
	convert_exe = False
	studio_database = ['sqlite3', False]
	init_path = False
	set_path = False
	share_dir = False
	projects_path = False  # path to .projects.db
	set_of_tasks_path = False  # path to .set_of_tasks.json
	artists_path = False # path to .artists.db
	workroom_path = False # path to .workroom_db
	statistic_path = False # path to .statistic.db
	list_projects = {} # a list of existing projects
	list_active_projects = []
	
	extensions = ['.blend', '.ma', '.tiff', '.ntp']
	setting_data = {
	'extension': {
		'.tiff':'krita',
		'.blend': 'blender',
		'.ntp': 'natron',
		'.ma': 'maya',
		'.ods':'libreoffice',
		}
	}
	
	publish_folder_name = 'publish'
	
	soft_data = None
	
	priority = ['normal', 'high', 'top', 'ultra']
	
	user_levels = ('user', 'extend_user', 'manager', 'root')
	manager_levels = ('manager', 'root')

	task_status = ('null','ready', 'ready_to_send', 'work', 'work_to_outsorce', 'pause', 'recast', 'checking', 'done', 'close')
	working_statuses = ('ready', 'ready_to_send', 'work', 'work_to_outsorce', 'pause', 'recast')
	end_statuses = ('done', 'close')
	
	color_status = {
	'null':(0.451000005, 0.451000005, 0.451000005),
	#'ready':(0.7627863884, 0, 1),
	'ready':(0.826, 0.249, 1),
	'ready_to_send':(0.9367088675, 0.2608556151, 0.4905878305),
	'work':(0.520749867, 0.7143493295, 0.8227847815),
	'work_to_outsorce':(0.2161512673, 0.5213058591, 0.8987341523),
	#'pause':(0.3417721391, 0.2282493114, 0.1557442695),
	'pause':(0.670, 0.539, 0.827),
	'recast':(0.8481012583, 0.1967110634, 0.1502964497),
	'checking':(1, 0.5872552395, 0.2531645298),
	'done':(0.175, 0.752, 0.113),
	#'close':(0.1645569652, 0.08450711519, 0.02499599569)
	'close':(0.613, 0.373, 0.195)
	}
	
	task_types = [
	# -- film
	'animatic',
	'film',
	#
	'sketch',
	'textures',
	# -- model
	'sculpt',
	'model',
	# -- rig
	'rig',
	# -- location,
	'specification',
	'location',
	#'location_full',
	#'location_for_anim',
	# -- animation
	'animation_shot',
	'tech_anim',
	'simulation_din',
	#'simulation_fluid',
	'render',
	'composition',
	]
	
	service_tasks = [
	'all',
	'pre',
	]
	
	asset_types = [
	#'animatic',
	'obj',
	'char',
	'location',
	'shot_animation',
	#'camera',
	#'shot_render',
	#'shot_composition',
	#'light',
	'film'
	]
	
	asset_types_with_season = [
	'animatic',
	'shot_animation',
	'camera',
	'shot_render',
	'shot_composition',
	'film'
	]
	
	asset_keys = {
	'name': 'text',
	'group': 'text',
	#'path': 'text',
	'type': 'text',
	'season': 'text',
	'priority': 'integer',
	'comment': 'text',
	'content': 'text',
	'id': 'text',
	'status': 'text',
	'parent': 'json' # {'name':asset_name, 'id': asset_id} - возможно не нужно
	}
	
	# constants (0 - 3 required parameters)
	tasks_keys = {
	'asset_name': 'text',
	'activity': 'text',
	'task_name': 'text',
	'task_type': 'text',
	'season': 'text',
	'input': 'json',
	'status': 'text',
	'outsource': 'integer',
	'artist': 'text',
	'planned_time': 'text',
	'time': 'text',
	'start': 'timestamp',
	'end': 'timestamp',
	'supervisor': 'text',
	'approved_date': 'text',
	'price': 'real',
	'tz': 'text',
	'chat_local': 'json',
	'web_chat': 'text',
	#'workroom': 'text',- не актуально, исполнители предлагаются из отделов соответствующего типа.
	'readers': 'json',
	'output': 'json',
	'priority':'integer',
	'asset_id': 'text',
	'asset_type': 'text',
	#'asset_path': 'text', каждый раз определяется при считывании данных.
	'extension': 'text',
	}
	'''
	workroom_keys = [
	('name', 'text'),
	('id', 'text'),
	('type', 'json')
	]
	'''
	workroom_keys = {
	'name': 'text',
	'id': 'text',
	'type': 'json'
	}
	
	# activity, task_name, action, date_time, comment, version, artist
	'''
	logs_keys = [
	('activity', 'text'),
	('task_name', 'text'),
	('action', 'text'),
	('date_time', 'timestamp'),
	('comment', 'text'),
	('version', 'text'),
	('artist', 'text')
	]
	'''
	# user_name, task_name, data_start, data_end, long_time, cost
	statistics_keys = [
	('project_name', 'text'),
	('task_name', 'text'),
	('data_start', 'timestamp'),
	('data_end', 'timestamp'),
	('long_time', 'text'),
	('cost', 'text'),
	('status', 'text')
	]
	# artist_name, user_name, email, phone, specialty, outsource = '' or '0'/'1'
	'''
	artists_keys = [
	('nik_name', 'text'),
	('user_name', 'text'),
	('password', 'text'),
	('date_time', 'timestamp'),
	('email', 'text'),
	('phone', 'text'),
	('specialty', 'text'),
	('outsource', 'text'),
	('workroom', 'text'),
	('level', 'text'),
	('share_dir', 'text'),
	('status', 'text')
	]
	'''
	artists_keys = {
	'nik_name': 'text',
	'user_name': 'text',
	'password': 'text',
	'date_time': 'timestamp',
	'email': 'text',
	'phone': 'text',
	'specialty': 'text',
	'outsource': 'integer',
	'workroom': 'json',
	'level': 'text',
	'share_dir': 'text',
	'status': 'text'
	}
	chats_keys = [
	('date_time', 'timestamp'),
	('author', 'text'),
	('topic', 'text'),
	('color', 'text'),
	('status', 'text'),
	('reading_status', 'text')
	]
	'''
	projects_keys = [
	('name', 'text'),
	('assets_path', 'text'),
	('chat_img_path', 'text'),
	('chat_path', 'text'),
	('list_of_assets_path', 'text'),
	('path', 'text'),
	('preview_img_path', 'text'),
	('status', 'text'),
	('tasks_path', 'text'),
	('project_database', 'json') # формат который конвертируется через json и записывается строкой.
	]
	'''
	projects_keys = {
	'name': 'text',
	'assets_path': 'text',
	'chat_img_path': 'text',
	'chat_path': 'text',
	'list_of_assets_path': 'text',
	'path': 'text',
	'preview_img_path': 'text',
	'status': 'text',
	'tasks_path': 'text',
	'project_database': 'json' # формат который конвертируется через json и записывается строкой.
	}
	
	group_keys = {
	'name': 'text',
	'type': 'text',
	'season': 'text',
	'comment': 'text',
	'id': 'text',
	}
	
	season_keys = {
	'name': 'text',
	'status':'text',
	'id': 'text',
	}

	list_of_assets_keys = [
	'asset_name',
	'asset_type',
	'set_of_tasks',
	]
	
	logs_keys = [
	('version', 'text'),
	('date_time', 'timestamp'),
	('activity', 'text'),
	('task_name', 'text'),
	('action', 'text'),
	('artist', 'text'),
	('comment', 'text'),
	]
	
	init_folder = '.lineyka'
	init_file = 'lineyka_init.json'
	set_file = 'user_setting.json'
	set_of_tasks_file = '.set_of_tasks.json'
	projects_file = '.projects.json'
	location_position_file = 'location_content_position.json'
	user_registr_file_name = 'user_registr.json'
	recycle_bin_name = '-Recycle_Bin-'
	list_of_assets_name = '.list_of_assets.json' # to delete
	
	#database files
	# --- projects
	projects_db = '.projects.db'
	projects_t = 'projects'
	# --- assets
	assets_db = '.assets.db'
	#assets_t = 'assets' # имя таблицы - тип ассета
	# --- artists
	artists_db = '.artists.db'
	artists_t = 'artists'
	# --- workroom
	workroom_db = artists_db
	workroom_t = 'workrooms'
	# --- statistic
	statistic_db = '.statistic.db'
	statistic_t = 'statistic'
	# --- season
	season_db = assets_db
	season_t = 'season'
	# --- group
	group_db = assets_db
	group_t = 'groups'
	# --- tasks
	tasks_db = '.tasks.db'
	tasks_t = 'tasks'
	# --- logs
	logs_db = tasks_db
	logs_t = 'logs'
	# --- chat
	chats_db = '.chats.db'
	
	# shot_animation
	meta_data_file = '.shot_meta_data.json'
	
	# blender
	blend_service_images = {
		'preview_img_name' : 'Lineyka_Preview_Image',
		'bg_image_name' : 'Lineyka_BG_Image',
		}
		
	def __init__(self):
		self.make_init_file()
		self.get_studio()

	@classmethod
	def make_init_file(self):
		home = os.path.expanduser('~')
		
		folder = NormPath(os.path.join(home, self.init_folder))
		self.init_path = NormPath(os.path.join(home, self.init_folder, self.init_file))
		self.set_path = NormPath(os.path.join(folder, self.set_file))
		
		# make folder
		if not os.path.exists(folder):
			os.mkdir(folder)
		
		# make init_file
		if not os.path.exists(self.init_path):
			# make jason
			d = {
				'studio_folder': None,
				'convert_exe': None,
				'use_database': ['sqlite3', False],
				}
			m_json = json.dumps(d, sort_keys=True, indent=4)
			# save
			data_fale = open(self.init_path, 'w')
			data_fale.write(m_json)
			data_fale.close()
			
		# make set_file
		if not os.path.exists(self.set_path):
			# make jason
			d = self.setting_data
			m_json = json.dumps(d, sort_keys=True, indent=4)
			# save
			data_fale = open(self.set_path, 'w')
			data_fale.write(m_json)
			data_fale.close()
	
	@classmethod
	def set_studio(self, path):
		if not os.path.exists(path):
			return(False, "****** to studio path not Found!")
		
		home = os.path.expanduser('~')	
		init_path = os.path.join(home, self.init_folder, self.init_file).replace('\\','/')
		if not os.path.exists(init_path):
			return(False, "****** init_path not Found!")
		
		# write studio path
		try:
			with open(init_path, 'r') as read:
				data = json.load(read)
				data['studio_folder'] = path
				read.close()
		except:
			return(False, "****** in set_studio() -> init file  can not be read")

		try:
			with open(init_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return(False, "****** in set_studio() ->  init file  can not be read")

		self.studio_folder = path
		
		# create projects_db
		projects_path = NormPath(os.path.join(path, self.projects_db))
		if not os.path.exists(projects_path):
			conn = sqlite3.connect(projects_path)
			c = conn.cursor()
			conn.commit()
			conn.close()
		'''
		projects_path = os.path.join(path, self.projects_file)
		if not os.path.exists(projects_path):
			d = {}
			m_json = json.dumps(d, sort_keys=True, indent=4)
			# save
			data_fale = open(projects_path, 'w')
			data_fale.write(m_json)
			data_fale.close()
		'''
		self.projects_path = projects_path
		
		# create .set_of_tasks.json
		set_of_tasks_path = os.path.join(path, self.set_of_tasks_file)
		if not os.path.exists(set_of_tasks_path):
			d = {}
			m_json = json.dumps(d, sort_keys=True, indent=4)
			# save
			data_fale = open(set_of_tasks_path, 'w')
			data_fale.write(m_json)
			data_fale.close()
		self.set_of_tasks_path = set_of_tasks_path

		# create  artists
		artist_path = NormPath(os.path.join(path, self.artists_db))
		if not os.path.exists(artist_path):
			conn = sqlite3.connect(artist_path)
			c = conn.cursor()
			'''
			names = (self.artists_t, )
			c.execute("CREATE TABLE ?(artist_name TEXT, user_name TEXT, email TEXT, phone TEXT, name TEXT, specialty TEXT)", names)
			'''
			'''
			string2 = "CREATE TABLE " + self.artists_t + " ("
			for i,key in enumerate(self.artists_keys):
				if i == 0:
					string2 = string2 + '\"' + key[0] + '\" ' + key[1]
				else:
					string2 = string2 + ', \"' + key[0] + '\" ' + key[1]
			string2 = string2 + ')'
			c.execute(string2)
			'''
			'''
			string = "CREATE TABLE " + self.artists_t + "(artist_name TEXT, user_name TEXT, email TEXT, phone TEXT, name TEXT, specialty TEXT)"
			c.execute(string)
			'''
			
			conn.commit()
			conn.close()
		self.artists_path = artist_path
		
		# create workroom
		self.workroom_path = artist_path

		# create  statistic
		statistic_path = os.path.join(path, self.statistic_db)
		if not os.path.exists(statistic_path):
			conn = sqlite3.connect(statistic_path)
			c = conn.cursor()
			'''
			names = (self.statistic_t, )
			c.execute("CREATE TABLE ?(task TEXT, user_name TEXT, data_start TEXT, data_end TEXT, long_time REAL, price REAL)", names)
			'''
			'''
			string = "CREATE TABLE " + self.statistic_t + "(task TEXT, user_name TEXT, data_start TEXT, data_end TEXT, long_time REAL, price REAL)"
			c.execute(string)
			'''
			
			conn.commit()
			conn.close()
		self.statistic_path = statistic_path
		'''		
		# fill self.extensions
		try:
			with open(self.set_path, 'r') as read:
				data = json.load(read)
				self.extensions = data['extension'].keys()
				read.close()
		except:
			print('in set_studio -> not read user_setting.json!')
			return(False, 'in set_studio -> not read user_setting.json!')
		'''	
		return(True, 'Ok')
	
	@classmethod
	def set_tmp_dir(self, path):
		if not os.path.exists(path):
			return "****** to studio path not Found!"
		
		home = os.path.expanduser('~')	
		init_path = os.path.join(home, self.init_folder, self.init_file).replace('\\','/')
		if not os.path.exists(init_path):
			return "****** init_path not Found!"
		
		# write studio path
		try:
			with open(init_path, 'r') as read:
				data = json.load(read)
				data['tmp_folder'] = path
				read.close()
		except:
			return "****** init file  can not be read"

		try:
			with open(init_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return "****** init file  can not be read"

		self.tmp_folder = path
				
		return(True, 'Ok')
	
	@classmethod
	def set_convert_exe_path(self, path):
		if not os.path.exists(path):
			return(False, "****** to convert.exe path not Found!")
		
		home = os.path.expanduser('~')
		init_path = os.path.join(home, self.init_folder, self.init_file).replace('\\','/')
		if not os.path.exists(init_path):
			return(False, "****** init_path not Found!")
		
		# write studio path
		try:
			with open(init_path, 'r') as read:
				data = json.load(read)
				data['convert_exe'] = NormPath(path)
				read.close()
		except:
			return(False, "****** init file  can not be read")

		try:
			with open(init_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return(False, "****** init file  can not be read")

		self.convert_exe = path
				
		return True, 'Ok'
		
	def set_share_dir(self, path):
		if not os.path.exists(path):
			return "****** to studio path not Found!"
		
		home = os.path.expanduser('~')	
		init_path = os.path.join(home, self.init_folder, self.init_file).replace('\\','/')
		if not os.path.exists(init_path):
			return "****** init_path not Found!"
		
		# write studio path
		try:
			with open(init_path, 'r') as read:
				data = json.load(read)
				data['share_folder'] = path
				read.close()
		except:
			return "****** init file  can not be read"

		try:
			with open(init_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return "****** init file  can not be read"

		#self.out_source_share_folder = path
				
		return True, 'Ok'
		
	def get_share_dir(self):
		# get lineyka_init.json
		home = os.path.expanduser('~')	
		init_path = os.path.join(home, self.init_folder, self.init_file).replace('\\','/')
		if not os.path.exists(init_path):
			return False, "****** init_path not Found!"
			
		# write studio path
		
		try:
			with open(init_path, 'r') as read:
				data = json.load(read)
				try:
					path = data['share_folder']
					self.share_dir = path
					return True, path
				except:
					return False, 'Not key \"share_folder\"'
				read.close()
		except:
			return False, '****** init file not Read!'
	
	@classmethod
	def get_studio(self):
		if self.init_path == False:
			return(False, '****** in get_studio() -> init_path = False!')
		# write studio path
		try:
			with open(self.init_path, 'r') as read:
				data = json.load(read)
				#self.studio_folder = data['studio_folder']
				#self.tmp_folder = data['tmp_folder']
				read.close()
		except:
			return(False, "****** init file  can not be read")
		try:
			self.studio_folder = data['studio_folder']
			self.convert_exe = data['convert_exe']
			self.tmp_folder = data['tmp_folder']
			self.use_database = data['use_database']
		except Exception as e:
			print(e)
			
		# artists_path = False   statistic_path = False
		if self.studio_folder:
			if self.projects_path == False:
				path = NormPath(os.path.join(self.studio_folder, self.projects_db))
				if os.path.exists(path):
					self.projects_path = path
			
			#self.get_set_of_tasks_path()
			if not self.set_of_tasks_path:
				path = NormPath(os.path.join(self.studio_folder, self.set_of_tasks_file))
				if os.path.exists(path):
					self.set_of_tasks_path = path
			
			if not self.artists_path:
				path = NormPath(os.path.join(self.studio_folder, self.artists_db))
				if os.path.exists(path):
					self.artists_path = path
			if self.workroom_path == False:
				path = NormPath(os.path.join(self.studio_folder, self.artists_db))
				if os.path.exists(path):
					self.workroom_path = path
			if self.statistic_path == False:
				path = NormPath(os.path.join(self.studio_folder, self.statistic_db))
				if os.path.exists(path):
					self.statistic_path = path
					
		#print('artist path: ', self.artists_path)
		
		# get self.list_projects
		if self.projects_path:
			self.get_list_projects()
			pass
			
		'''
		# get list_active_projects
		if self.list_projects:
			self.list_active_projects = []
			for key in self.list_projects:
				if self.list_projects[key]['status'] == 'active':
					self.list_active_projects.append(key)
		'''
				
		# fill self.extensions
		try:
			with open(self.set_path, 'r') as read:
				data = json.load(read)
				self.extensions = data['extension'].keys()
				self.soft_data = data['extension']
				read.close()
		except:
			return(False, 'in get_studio -> not read user_setting.json!')
		
		print('studio.get_studio')
		return True, [self.studio_folder, self.tmp_folder, self.projects_path, self.artists_path, self.statistic_path, self.list_projects, self.workroom_path]
		
	@classmethod
	def get_list_projects(self):
		if not self.projects_path:
			return
		if not os.path.exists(self.projects_path):
			return
		
		# get list_projects
		bool_, return_data = database().read('studio', self, self.projects_t, self.projects_keys)
		
		if not bool_:
			print('#'*10, return_data)
			return(False, return_data)
		
		list_projects = {}
		for row in return_data:
			data = {}
			for key in row.keys():
				#print(key)
				if key == 'name':
					continue
				data[key] = row[key]
			list_projects[row['name']] = data
		
		self.list_projects = list_projects

		# get list_active_projects
		if self.list_projects:
			self.list_active_projects = []
			for key in self.list_projects:
				if self.list_projects[key]['status'] == 'active':
					self.list_active_projects.append(key)
		
		print('get_list_projects')
	
	def get_set_of_tasks_path(self):
		if not self.set_of_tasks_path:
			path = NormPath(os.path.join(self.studio_folder, self.set_of_tasks_file))
			if os.path.exists(path):
				self.set_of_tasks_path = path

	# ****** SETTING ******
	# ------- EXTENSION -------------
	def get_extension_dict(self):
		extension_dict = {}
		
		home = os.path.expanduser('~')
		folder = os.path.join(home, self.init_folder)
		set_path = os.path.join(folder, self.set_file)
		
		if not os.path.exists(set_path):
			return(False, ('Not Path ' + set_path))
		
		with open(set_path, 'r') as read:
			extension_dict = json.load(read)['extension']
			
		return(True, extension_dict)
		
	def edit_extension_dict(self, key, path):
		extension_dict = {}
		
		home = os.path.expanduser('~')
		folder = os.path.join(home, self.init_folder)
		set_path = os.path.join(folder, self.set_file)
		
		if not os.path.exists(set_path):
			return(False, ('Not Path ' + set_path))
		
		with open(set_path, 'r') as read:
			data = json.load(read)
		
		data['extension'][key] = path
		
		with open(set_path, 'w') as f:
			jsn = json.dump(data, f, sort_keys=True, indent=4)
			f.close()
		
		return(True, 'Ok')
		
	def edit_extension(self, extension, action, new_extension = False):
		if not extension:
			return(False, 'Not Extension!')
			
		if not action in ['ADD', 'REMOVE', 'EDIT']:
			return(False, 'Incorrect Action!')
			
		# get file path
		home = os.path.expanduser('~')
		folder = os.path.join(home, self.init_folder)
		set_path = os.path.join(folder, self.set_file)
		
		if not os.path.exists(set_path):
			return(False, ('Not Path ' + set_path))
		
		# preparation extension
		if extension[0] != '.':
			extension = '.' + extension
			
		# read extensions
		with open(set_path, 'r') as read:
			data = json.load(read)
			
		if action == 'ADD':
			if not extension in data['extension'].keys():
				data['extension'][extension] = ''
			else:
				return(False, ('This Extension \"' + extension + '\" Already Exists!'))
		elif action == 'REMOVE':
			if extension in data['extension'].keys():
				del data['extension'][extension]
			else:
				return(False, ('This Extension \"' + extension + '\" Not Found!'))
		elif action == 'EDIT':
			if new_extension: 
				if extension in data['extension'].keys():
					value = data['extension'][extension]
					del data['extension'][extension]
					data['extension'][new_extension] = value
			else:
				return(False, 'Not New Extension!')
			
		with open(set_path, 'w') as f:
			jsn = json.dump(data, f, sort_keys=True, indent=4)
			f.close()
		
		return(True, 'Ok')
	
class database():
	def __init__(self):
		self.sqlite3_db_folder_attr = {
			'studio': 'studio_folder',
			'project': 'path',
			}
		
		self.use_db_attr = {
			'studio': 'studio_database',
			'project': 'project_database',
			}
	
	# level - studio or project; or: studio, project, season, group, asset, task, chat, log, statistic ...
	# read_ob - object of studio or project;
	# table_root - assets, chats - те случаи когда имя файла ДБ не соответствует имени таблицы, если есть table_root - имя файла ДБ будет определяться по нему.
	# table_root - может быть как именем таблицы - например: assets, так и именем файла - .assets.db
	def get(self, level, read_ob, table_name, com, table_root=False):
		# get use_db
		attr = self.use_db_attr.get(level)
		if not attr:
			raise Exception('database.get()', 'Unknown Level : %s' % level)
		
		db_name, db_data = eval('read_ob.%s' % attr)
		#return(db_name, db_data)
		
		if db_name == 'sqlite3':
			return_data = self.__sqlite3_get(level, read_ob, table_name, com, table_root)
			return(return_data)
	
	# table_root - может быть как именем таблицы - например: assets, так и именем файла - .assets.db
	def set_db(self, level, read_ob, table_name, com, data_com=False, table_root=False):
		# get use_db
		attr = self.use_db_attr.get(level)
		if not attr:
			raise Exception('database.set_db()', 'Unknown Level : %s' % level)
		
		db_name, db_data = eval('read_ob.%s' % attr)
		#return(db_name, db_data)
		
		if db_name == 'sqlite3':
			return_data = self.__sqlite3_set(level, read_ob, table_name, com, data_com, table_root)
			return(return_data)
	
	# table_root - может быть как именем таблицы - например: assets, так и именем файла - .assets.db
	def create_table(self, level, read_ob, table_name, keys, table_root = False):
		attr = self.use_db_attr.get(level)
		if not attr:
			raise Exception('database.write()', 'Unknown Level : %s' % level)
		
		db_name, db_data = eval('read_ob.%s' % attr)
		#return(db_name, db_data)
		
		if db_name == 'sqlite3':
			return_data = self.__sqlite3_create_table(level, read_ob, table_name, keys, table_root)
			return(return_data)
		
	# write_data - словарь по ключам keys, также может быть списком словарей, для записи нескольких строк.
	# keys - это: tasks_keys, projects_keys итд.
	# table_root - может быть как именем таблицы - например: assets, так и именем файла - .assets.db
	def insert(self, level, read_ob, table_name, keys, write_data, table_root=False):
		attr = self.use_db_attr.get(level)
		if not attr:
			raise Exception('database.insert()', 'Unknown Level : %s' % level)
		
		db_name, db_data = eval('read_ob.%s' % attr)
		#return(db_name, db_data)
		
		if db_name == 'sqlite3':
			return_data = self.__sqlite3_insert(level, read_ob, table_name, keys, write_data, table_root)
			return(return_data)
	
	# where - 1) строка условия, 2) словарь по keys, 3) False - значит выделяется всё.
	# columns - False - означает все столбцы если не False - то список столбцов.
	def read(self, level, read_ob, table_name, keys, columns = False, where=False, table_root=False):
		attr = self.use_db_attr.get(level)
		if not attr:
			raise Exception('database.read()', 'Unknown Level : %s' % level)
		
		db_name, db_data = eval('read_ob.%s' % attr)
		#return(db_name, db_data)
		
		if db_name == 'sqlite3':
			return_data = self.__sqlite3_read(level, read_ob, table_name, keys, columns, where, table_root)
			return(return_data)
	
	# update_data - словарь по ключам из keys
	# where - словарь по ключам, так как значения маскируются под "?" не может быть None или False
	# table_root - может быть как именем таблицы - например: assets, так и именем файла - .assets.db
	def update(self, level, read_ob, table_name, keys, update_data, where, table_root=False):
		attr = self.use_db_attr.get(level)
		if not attr:
			raise Exception('database.update()', 'Unknown Level : %s' % level)
		
		db_name, db_data = eval('read_ob.%s' % attr)
		#return(db_name, db_data)
		
		if db_name == 'sqlite3':
			return_data = self.__sqlite3_update(level, read_ob, table_name, keys, update_data, where, table_root)
			return(return_data)
	
	### SQLITE3
	# table_root - может быть как именем таблицы - например: assets, так и именем файла - .assets.db
	def __get_db_path(self, level, read_ob, table_name, table_root):
		attr = self.sqlite3_db_folder_attr.get(level)
		db_folder = eval('read_ob.%s' % attr)
		if table_root:
			if table_root.endswith('.db'):
				db_path = os.path.join(db_folder, table_root)
			else:
				db_path = os.path.join(db_folder, '.%s.db' % table_root)
		else:
			db_path = os.path.join(db_folder, '.%s.db' % table_name)
		return(db_path)
	
	# update_data - словарь по ключам из keys
	# where - словарь по ключам, так как значения маскируются под "?" не может быть None или False
	def __sqlite3_update(self, level, read_ob, table_name, keys, update_data, where, table_root):
		data_com = []
		# set_data
		set_data = ''
		if update_data.__class__.__name__ != 'dict':
			return(False, 'update_data not dict!')
		else:
			for i, key in enumerate(update_data):
				if i==0:
					set_data = '"%s" = ?' % key
				else:
					set_data = set_data + ', "%s" = ?' % key
				if keys[key]=='json':
					data_com.append(json.dumps(update_data[key]))
				else:
					data_com.append(update_data[key])
		# where
		where_data = ''
		if where.__class__.__name__ != 'dict':
			return(False, 'where not dict!')
		else:
			for i, key in enumerate(where):
				if i==0:
					where_data = '%s = ?' % key
				else:
					where_data = where_data + ', %s = ?' % key
				data_com.append(where[key])
		# com
		com = 'UPDATE %s SET %s WHERE %s' % (table_name, set_data, where_data)
		
		# connect
		# -- db_path
		db_path = self.__get_db_path(level, read_ob, table_name, table_root)
		# -- connect
		conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		# -- com
		try:
			c.execute(com, data_com)
		except Exception as e:
			print('#'*3, 'Exception in database.__sqlite3_update:')
			print('#'*3, 'com:', com)
			print('#'*3, 'data_com:', data_com)
			print('#'*3, e)
			conn.close()
			return(False, 'Exception in database.__sqlite3_update, please look the terminal!')
		conn.commit()
		conn.close()
		return(True, 'Ok!')
	
	# where - 1) строка условия, 2) словарь по keys, 3) False - значит выделяется всё.
	# columns - False - означает все столбцы если не False - то список столбцов.
	def __sqlite3_read(self, level, read_ob, table_name, keys, columns, where, table_root):
		# columns
		col = ''
		if not columns:
			col = '*'
		elif columns.__class__.__name__ == 'list':
			for i, item in enumerate(columns):
				if i == 0:
					col = col + item
				else:
					col = col + ', %s' % item
		# com
		com = 'SELECT %s FROM %s ' % (col, table_name)
		if where:
			if where.__class__.__name__ == 'string':
				com = '%s WHERE %s' % (com, where)
			elif where.__class__.__name__ == 'dict':
				were_string = ''
				for i, key in enumerate(where):
					if i == 0:
						were_string = were_string + '"%s" = "%s"' % (key, where.get(key))
					else:
						were_string = were_string + ', "%s" = "%s"' % (key, where.get(key))
				com = '%s WHERE %s' % (com, were_string)
		# connect
		# -- db_path
		db_path = self.__get_db_path(level, read_ob, table_name, table_root)
		# -- connect
		try:
			conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except Exception as e:
			print('#'*3, 'Exception in database.__sqlite3_read:')
			print('#'*3, 'db_path:', db_path)
			print('#'*3, e)
			return(False, 'Exception in database.__sqlite3_read, please look the terminal!')
		try:
			c.execute(com)
		except Exception as e:
			conn.close()
			print('#'*3, 'Exception in database.__sqlite3_read:')
			print('#'*3, 'com:', com)
			print('#'*3, e)
			return(False, 'Exception in database.__sqlite3_read, please look the terminal!')
		
		data = []
		for row in c.fetchall():
			'''
			dict_row = dict(row)
			'''
			dict_row = {}
			for key in row.keys():
				if keys[key]=='json':
					#print('#'*10, key)
					#print('*'*10, row[key])
					try:
						dict_row[key] = json.loads(row[key])
					except Exception as e:
						print('%s Exception in database.__sqlite3_read:' % '#'*10)
						print('%s table = %s, key = %s, row[key] = %s' % ('#'*10, table_name, key, row[key]))
						print('#'*10, e)
						dict_row[key] = None
				else:
					dict_row[key] = row[key]
			
			data.append(dict_row)
		conn.close()
		return(True, data)
	
	def __sqlite3_create_table(self, level, read_ob, table_name, keys, table_root):
		com = ''
		#data_com = []
		for i, key in enumerate(keys):
			if keys[key] == 'json':
				type_data = 'text'
			else:
				type_data = keys[key]
			if i==0:
				com = com + '"%s" "%s"' % (key, type_data)
			else:
				com = com + ', "%s" "%s"' % (key, type_data)
		com = 'CREATE TABLE IF NOT EXISTS %s (%s)' % (table_name, com)
		return_data = self.__sqlite3_set(level, read_ob, table_name, com, False, table_root)
		return(return_data)
	
	# write_data - словарь по ключам keys, также может быть списком словарей, для записи нескольких строк.
	# keys - это: tasks_keys, projects_keys итд.
	def __sqlite3_insert(self, level, read_ob, table_name, keys, write_data, table_root):
		if write_data.__class__.__name__ == 'dict':
			iterator = [write_data]
		elif write_data.__class__.__name__ == 'list':
			iterator = write_data
		# connect
		# -- db_path
		db_path = self.__get_db_path(level, read_ob, table_name, table_root)
		# -- connect
		conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		# -- com
		for item in iterator:
			com = 'INSERT INTO %s VALUES' % table_name
			com_=''
			data_com = []
			for i, key in enumerate(keys):
				if i==0:
					com_ = com_ + ' ?'
				else:
					com_ = com_ + ', ?'
				if keys[key] == 'json':
					data_ = json.dumps(item.get(key))
				else:
					data_ = item.get(key)
				data_com.append(data_)
			com = '%s (%s)' % (com, com_)
			try:
				c.execute(com, data_com)
			except Exception as e:
				print('#'*3, 'Exception in database.__sqlite3_insert:')
				print('#'*3, 'com:', com)
				print('#'*3, 'data_com:', data_com)
				print('#'*3, e)
				conn.close()
				return(False, 'Exception in database.__sqlite3_insert, please look the terminal!')
		conn.commit()
		conn.close()
		return(True, 'Ok!')
			
	def __sqlite3_get(self, level, read_ob, table_name, com, table_root):
		#db_path
		db_path = self.__get_db_path(level, read_ob, table_name, table_root)
		#print('__sqlite3_get()', db_path, os.path.exists(db_path))
		
		try:
			# -- CONNECT  .db
			conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
			c.execute(com)
			data = []
			for row in c.fetchall():
				data.append(dict(row))
			#print('*'*10, data)
		except Exception as e:
			try:
				conn.close()
			except:
				pass
			print('__sqlite3_get()', e)
			return(False, e)
		
		conn.close()
		return(True, data)
	
	# if com = False - создаётся пустая таблица ,при отсутствии
	def __sqlite3_set(self, level, read_ob, table_name, com, data_com, table_root):
		#db_path
		db_path = self.__get_db_path(level, read_ob, table_name, table_root)
		#print('__sqlite3_get()', db_path, os.path.exists(db_path))
		
		try:
			# -- CONNECT  .db
			conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
			if data_com:
				c.execute(com, data_com)
			elif com:
				c.execute(com)
			else:
				pass
		except Exception as e:
			try:
				conn.close()
			except:
				pass
			print('#'*3, 'Exception in __sqlite3_set()', e)
			print('#'*3, 'com:', com)
			print('#'*3, 'data_com:', data_com)
			return(False, 'Exception in __sqlite3_set(), please read the terminal!')
		
		conn.commit()
		conn.close()
		return(True, 'Ok!')

class project(studio):
	'''
	self.add_project(project_name, project_path, keys) - 

	self.get_project(project_name) - 
	
	'''
	def __init__(self):
		#base fields
		for key in self.projects_keys:
			exec('self.%s = False' % key)
		
		# added fields
		self.assets_list = False # # a list of existing assets
		# constans
		self.folders = {'assets':'assets', 'chat_img_folder':'.chat_images', 'preview_images': '.preview_images'}

	def add_project(self, project_name, project_path):
		project_path = NormPath(project_path)
		# project_name, get project_path
		if not project_path and project_name == '':
			return(False, 'No options!')
			
		elif not project_path:
			project_path = os.path.join(self.studio_folder, project_name)
			try:
				os.mkdir(project_path)
			except:
				return(False, ('Failed to create folder: ' + project_path))
			
		elif project_name == '':
			if not os.path.exists(project_path):
				return(False, ('Project Path: \"%s\" Not Found!' % project_path))
			project_name = os.path.basename(project_path)
			
		# test by name 
		if project_name in self.list_projects.keys():
			return(False, "This project name already exists!")
		self.name = project_name
		
		path = project_path
			
		if not os.path.exists(path):
			text = '****** studio.project.add_project() -> %s not found' % path
			return False, text
		else:
			self.path = path
		
		self.project_database = ['sqlite3', False] # новый проект в начале всегда sqlite3, чтобы сработало всё в database
		self.assets_path = NormPath(os.path.join(self.path, self.assets_db))
		self.chat_path = NormPath(os.path.join(self.path, self.chats_db))
		self.tasks_path = NormPath(os.path.join(self.path, self.tasks_db))
		self.list_of_assets_path = NormPath(os.path.join(self.path, '.list_of_assets_path.json'))
		
		# create folders
		self.make_folders(self.path)
		# -- get chat_img_folder
		img_folder_path = os.path.join(self.path, self.folders['chat_img_folder'])
		if os.path.exists(img_folder_path):
			self.chat_img_path = img_folder_path
		else:
			self.chat_img_path = False
		# -- get preview_images
		preview_img_path = os.path.join(self.path, self.folders['preview_images'])	
		if os.path.exists(preview_img_path):
			self.preview_img_path = preview_img_path
		else:
			self.chat_img_path = False
		
		# status
		self.status = 'active'
		
		# create project
		# -- create table
		bool_, return_data  = database().create_table('studio', self, self.projects_t, self.projects_keys)
		if not bool_:
			return(bool_, return_data)
		
		# -- write data
		write_data = {}
		for key in self.projects_keys:
			write_data[key] = eval('self.%s' % key)
		#print('#'*3, write_data)
		bool_, return_data = database().insert('studio', self, self.projects_t, self.projects_keys, write_data)
		if not bool_:
			return(bool_, return_data)
		
		# create_recycle_bin
		self.get_list_projects()
		#result = group().create_recycle_bin(project_name)
		result = group(self).create_recycle_bin()
		if not result[0]:
			return(False, result[1])
		
		return True, 'ok'
		
	def get_project(self, name):
		pass
		#self.get_list_projects()
		
		if not name in self.list_projects.keys():
			return(False, "This project Not Found!")
		else:
			#self.assets_path = self.list_projects[name]['assets_path']
			#self.tasks_path = self.list_projects[name]['tasks_path']
			#self.chat_path = self.list_projects[name]['chat_path']
			#self.chat_img_path = self.list_projects[name]['chat_img_path']
			#self.preview_img_path = self.list_projects[name]['preview_img_path']
			self.name = name
			#
			self.path = self.list_projects[name]['path']
			#
			assets_path = NormPath(os.path.join(self.path, self.assets_db))
			#if os.path.exists(assets_path):
			self.assets_path = assets_path
			#
			tasks_path = NormPath(os.path.join(self.path, self.tasks_db))
			#if os.path.exists(tasks_path):
			self.tasks_path = tasks_path
			#
			self.list_of_assets_path = NormPath(os.path.join(self.list_projects[name]['path'], '.list_of_assets_path.json'))
			#
			chat_path = NormPath(os.path.join(self.path, self.chats_db))
			#if os.path.exists(chat_path):
			self.chat_path = chat_path
			#
			chat_img_path = NormPath(os.path.join(self.path, self.folders['chat_img_folder']))
			#if os.path.exists(chat_img_path):
			self.chat_img_path = chat_img_path
			#
			preview_img_path = NormPath(os.path.join(self.path, self.folders['preview_images']))
			#if os.path.exists(preview_img_path):
			self.preview_img_path = preview_img_path
			#
			self.status = self.list_projects[name]['status']
			# database
			#self.project_database = json.loads(self.list_projects[name]['project_database'])
			self.project_database = self.list_projects[name]['project_database']
				
		self.get_list_of_assets()
		return(True, (self.list_projects[name], self.assets_list))
		
	def get_list_of_assets(self):
		# self.assets_list - list of dictonary by self.asset_keys
		self.assets_list = []
		return(True, 'Ok')
	
	def rename_project(self, old_name, new_name):
		# test old name
		if not old_name in self.list_projects.keys():
			return(False, ('in rename_project -> No such project: \"%s\"' % old_name))
		# database
		com = 'UPDATE %s SET \"name\" = ? WHERE name = ?' % self.projects_t
		data_com = (new_name, old_name)
		bool_, return_data = database().set_db('studio', self, self.projects_t, com, data_com=data_com)
		if not bool_:
			return(False, return_data)
		# перезапись списка проэктов
		self.get_list_projects()
		# переименованный проект - стал текущим
		result = self.get_project(new_name)
		if not result[0]:
			return(False, ('in rename_project -> ' + result[1]))
		return(True, 'Ok!')
		
	def remove_project(self, name):
		if not name in self.list_projects:
			return(False, ('No such project: \"' + name + '\"'))
			
		result = self.get_project(name)
		if not result[0]:
			return(False, result[1])
		
		# database
		com = 'DELETE FROM %s WHERE name = ?' % self.projects_t
		data_com = (name,)
		bool_, return_data = database().set_db('studio', self, self.projects_t, com, data_com=data_com)
		return(bool_, return_data)
		
	def edit_status(self, name, status):
		if not name in self.list_projects:
			return(False, ('in edit_status -> No such project: \"' + name + '\"'))
			
		result = self.get_project(name)
		if not result[0]:
			return(False, ('in project.edit_status -> ' + result[1]))
		
		# database
		update_data = {'status': status}
		where = {'name': name}
		bool_, return_data = database().update('studio', self, self.projects_t, self.projects_keys, update_data, where)
		return(bool_, return_data)
		
	def make_folders(self, root):
		for f in self.folders:
			path = os.path.join(root, self.folders[f])
			if not os.path.exists(path):
				os.mkdir(path)
				#print '\n****** Created'
			else:
				return False, '\n****** studio.project.make_folders -> No Created'
	
class asset(studio):
	'''
	studio.project.asset()
	
	self.ACTIVITY_FOLDER  - {activity_name : ACTIVITY_FOLDER, ... }
	
	add_asset(asset_name) - create folder: assets/asset_name; create activity folders assets/asset_name/...folders; write {asset_name:folder_full_path} in .assets.json; 
	
	get_asset(asset_name) - return ful path to asset_folder or False, fill self.task_list
	
	get_activity_path(asset_name, activity) - return full path of activity folder, or create activity folder, or return False
	
	get_final_file_path(passet_name, activity) - return full path to file of final version activity, or False
	
	get_new_file_path(asset_name, activity) - return 	new_dir_path, new_file_path, or False
	
	'''
	
	def __init__(self, project):
		pass
		# objects
		self.project = project
		
		self.task_list = False # task lists from this asset
		self.activity_path = False # директория какого либо активити по запросу, заполняется в get_activity_path()
		
		#base fields
		for key in self.asset_keys:
			exec('self.%s = False' % key)
		
		# constants
		#self.extension = '.ma'
		self.ACTIVITY_FOLDER = {
		#'animatic' : {
		'film':{
		'storyboard':'storyboard',
		'specification':'specification',
		'animatic':'animatic',
		'film':'film'
		},
		'obj':{
		'sketch':'sketch',
		'sculpt':'sculpt',
		'model':'03_model',
		'textures':'05_textures'
		},
		'char':{
		'sketch':'sketch',
		'face_blend':'10_face_blend',
		'sculpt':'sculpt',
		'model':'03_model',
		'rig':'08_rig',
		#'rig_face':'09_rig_face',
		#'rig_face_crowd':'09_rig_face_crowd',
		#'rig_hik':'08_rig_hik',
		#'rig_hik_face':'09_ri_hik_face',
		#'rig_low':'08_rig_low',
		'def_rig':'def_rig',
		'din_rig':'din_rig',
		'textures':'05_textures',
		'cache':'cache',
		},
		'location' : {
		'sketch':'sketch',
		'specification':'specification',
		'location_anim':'location_anim',
		'location':'location'
		},
		'shot_animation' : {
			'animatic':'animatic',
			'shot_animation':'shot_animation',
			'camera':'camera',
			'pleyblast_sequence':'pleyblast_sequence',
			'tech_anim': 'tech_anim',
			'simulation_din':'simulation_din',
			'render':'render',
			'composition':'composition',
			'cache':'cache',
			'actions':'actions',
			#'din_simulation':'din_simulation',
			#'fluid_simulation':'fluid_simulation',
		},
		'camera' : {'camera':'camera'},
		'shot_render' : {'shot_render':'shot_render'},
		'shot_composition' : {'shot_composition':'shot_composition'},
		'light' : {'light':'light'},
		#'film' : {'film':'film'},
		}
		
		self.ADDITIONAL_FOLDERS = {
		'meta_data':'00_common',
		}
		
		self.UNCHANGEABLE_KEYS = ['id', 'type', 'path']
		#self.COPIED_ASSET = ['obj', 'char']
		self.COPIED_ASSET = {
			'obj':['obj', 'char'],
			'char':['char', 'obj']
			}
		self.COPIED_WITH_TASK = ['obj', 'char']

		
	# заполнение полей по self.asset_keys - для передачи экземпляра на уровень выше.
	def init(self, keys):
		for key in self.asset_keys:
			exec('self.%s = keys.get("%s")' % (key, key))
		# path
		self.path = NormPath(os.path.join(self.project.path, self.project.folders['assets'],keys['type'], keys['name']))
		
	# **************** ASSET NEW  METODS ******************
	
	# list_keys (list) - список словарей по ключам asset_keys
	# -- обязательные параметры в keys (list_keys): name, group(id).
	# asset_type (str) - тип для всех ассетов
	def create(self, asset_type, list_keys):  # v2
		pass
		# проверка типа ассета
		# проверка типа list_keys
		# список ассетов данного типа для проверки наличия
		# создание таблицы если нет
		# создание ассетов - проверки:
		# -- наличие name, group(id), type
		# -- соответствие type типу группы.
		# -- наличия имени.
		# -- проверка на наличие ассета с таким именем.
		# -- создание id с проверкой на совпадение.
		
		# test valid asset_type
		if not asset_type in self.asset_types:
			return(False, 'Asset_Type (%s) is Not Valid!' % asset_type)
		# test valid type of list_keys
		if list_keys.__class__.__name__!= 'list':
			return(False, 'The type of "list_keys" (%s) is Not Valid! There must be a "list"' % list_keys.__class__.__name__)
		# start data
		make_assets = {}
		# get list assets
		assets = []
		ids = []
		result = self.get_list_by_all_types()
		if result[0]:
			for row in result[1]:
				assets.append(row['name'])
				ids.append(row['id'])
		else:
			print('#'*5)
			print(result[1])
			
		# cteate table
		bool_, return_data = database().create_table('project', self.project, asset_type, self.asset_keys, table_root = self.assets_db)
		if not bool_:
			return(bool_, return_data)
		
		########### create assets
		if not list_keys:
			return(False, 'No data to create an Asset!')
		# test exists name
		for keys in list_keys:
			if keys['name'] in assets:
				return(False, 'The name "%s" already exists!' % keys['name'])
		#
		for keys in list_keys:
			# test name
			if not keys.get('name'):
				return(False,('No name!'))
			# test group(id)
			if not keys.get('group'):
				return(False, 'In the asset "%s" does not specify a group!' % keys['name'])
			# test season
			if asset_type in self.asset_types_with_season and not keys.get('season'):
				return(False, 'In the asset "%s" does not specify a season' % keys['name'])
			elif not asset_type in self.asset_types_with_season and not keys.get('season'):
				keys['season'] = ''
			# edit name
			if asset_type in ['shot_animation']:
				keys['name'] = keys['name'].replace(' ', '_')
			else:
				keys['name'] = keys['name'].replace(' ', '_').replace('.', '_')
			# make keys
			keys['type'] = asset_type
			keys['status'] = 'active'
			# -- get id
			keys['id'] = hex(random.randint(0, 1000000000)).replace('0x','')
			while keys['id'] in ids:
				keys['id'] = hex(random.randint(0, 1000000000)).replace('0x','')
			# -- get priority
			if not keys.get('priority'):
				keys['priority'] = 0
			# create Folders
			group_dir = NormPath(os.path.join(self.project.path, self.project.folders['assets'],asset_type))
			asset_path = NormPath(os.path.join(group_dir, keys['name']))
			# -- create group folder
			if not os.path.exists(group_dir):
				try:
					os.mkdir(group_dir)
				except Exception as e:
					print('#'*5, 'In asset.create() -- create group folder')
					print(e)
					return(False, 'Exception in asset.create() look the terminal!')
			# -- create root folder
			if not os.path.exists(asset_path):
				try:
					os.mkdir(asset_path)
				except Exception as e:
					print('#'*5, 'In asset.create() -- create root folder')
					print(e)
					return(False, 'Exception in asset.create() look the terminal!')
			
			# -- create activity folders
			for activity in self.ACTIVITY_FOLDER[asset_type]:
				folder_path = NormPath(os.path.join(asset_path, self.ACTIVITY_FOLDER[asset_type][activity]))
				if not os.path.exists(folder_path):
					os.mkdir(folder_path)
					
			# -- create additional folders  self.ADDITIONAL_FOLDERS
			for activity in self.ADDITIONAL_FOLDERS:
				folder_path = NormPath(os.path.join(asset_path, self.ADDITIONAL_FOLDERS[activity]))
				if not os.path.exists(folder_path):
					os.mkdir(folder_path)
			
			# create in DB
			bool_, return_data = database().insert('project', self.project, asset_type, self.asset_keys, keys, table_root=self.assets_db)
			if not bool_:
				return(bool_, return_data)
			
			########### make task data
			
			this_asset_tasks = []
			# add service tasks ("final")
			final = {
				'asset_name':keys['name'],
				'asset_id': keys['id'],
				'asset_type': asset_type,
				'task_name': (keys['name'] + ':final'),
				'season': keys['season'],
				'status':'null',
				'task_type':'service',
				'input':[],
				'output': [],
			}
			# create service tasks ("all_input")
			all_input = {
				'asset_name':keys['name'],
				'asset_id': keys['id'],
				'asset_type': asset_type,
				'task_name': (keys['name'] + ':all_input'),
				'season': keys['season'],
				'status':'done',
				'task_type':'service',
				'input':[],
				'output': [],
			}
			this_asset_tasks.append(all_input)
			
			# get list from set_of_tasks
			result = set_of_tasks().get(keys.get('set_of_tasks'))
			if result[0]:
				set_tasks = result[1]['sets']
				
				outputs = {}
				for task_ in set_tasks:
					# name
					name = task_['task_name']
					task_['task_name'] = keys['name'] + ':' + name
					
					# output
					#task_['output'] = json.dumps([final['task_name']])
					task_['output'] = [final['task_name']]
					
					# input
					input_ = task_['input']
					if  input_ == 'all':
						task_['input'] = all_input['task_name']
						# status
						task_['status'] = 'ready'
						# add to output all_input
						#all_outputs = json.loads(all_input['output'])
						all_outputs = all_input['output']
						all_outputs.append(task_['task_name'])
						#all_input['output'] = json.dumps(all_outputs)
						all_input['output'] = all_outputs
						
					elif input_ == 'pre':
						task_['input'] = keys['name'] + ':pre_input:' + name
						# status
						task_['status'] = 'ready'
						# add service tasks ("pre_input" )
						pre_input = {
							'asset_name':keys['name'],
							'asset_id': keys['id'],
							'asset_type': asset_type,
							'task_name': task_['input'],
							'season': keys['season'],
							'status':'done',
							'task_type':'service',
							'input':'',
							#'output': json.dumps([final['task_name'], task_['task_name']])
							#'output': json.dumps([task_['task_name']])
							'output': [task_['task_name']]
						}
						this_asset_tasks.append(pre_input)
					elif input_:
						task_['input'] = keys['name'] + ':' + input_
						# status
						task_['status'] = 'null'
						
						# outputs
						if task_['input'] in outputs.keys():
							outputs[task_['input']].append(task_['task_name'])
						else:
							outputs[task_['input']] = [task_['task_name'],]
						
					else:
						# status
						task_['status'] = 'ready'
						
					# price
					task_['price'] = task_['cost']
						
					# asset
					task_['asset_name'] = keys['name']
					task_['asset_id'] = keys['id']
					task_['asset_type'] = asset_type
					
					# season
					task_['season'] = keys['season']
					
					# readers
					task_['readers'] = {}
					
					# append task
					this_asset_tasks.append(task_)
					
				for task_ in this_asset_tasks:
					if task_['task_name'] in outputs:
						if task_['output']:
							#task_outputs = json.loads(task_['output'])
							task_outputs = task_['output']
							task_outputs = task_outputs + outputs[task_['task_name']]
							#task_['output'] = json.dumps(task_outputs)
							task_['output'] = task_outputs
						else:
							#task_['output'] = json.dumps(outputs['task_name'])
							task_['output'] = outputs['task_name']
			
			# set input of "final"
			final_input = []
			for task_ in this_asset_tasks:
				final_input.append(task_['task_name'])
			#final['input'] = json.dumps(final_input)
			final['input'] = final_input
			
			# append final to task list
			this_asset_tasks.append(final)
			
			########### create tasks (by task data)
			#c = json.dumps(this_asset_tasks, sort_keys=True, indent=4)
			#print(c)
			self.init(keys)
			result = task(self).create_tasks_from_list(this_asset_tasks)
			if not result[0]:
				return(False, result[1])
			
			########### make return data
			# path
			keys['path'] = NormPath(os.path.join(self.project.path, self.project.folders['assets'],keys['type'], keys['name']))
			#
			make_assets[keys['name']] = keys
		
		return(True, make_assets)
		'''
		######################################################################## OLD
		tasks_of_assets = {}
		
		# -- CONNECT  .db
		try:
			# write group to db
			conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return(False, 'Not .db connect!')
			
		# -- EXISTS TABLE
		table = asset_type
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
									
		except:
			string2 = "CREATE TABLE " + table + " ("
			for i,key in enumerate(self.asset_keys):
				if i == 0:
					string2 = string2 + '\"' + key[0] + '\" ' + key[1]
				else:
					string2 = string2 + ', \"' + key[0] + '\" ' + key[1]
			string2 = string2 + ')'
			c.execute(string2)	
			
			
		# -- CREATE ASSETS
		make_assets = {}
		for keys in list_keys:
			# test name
			if (not 'name' in keys) or (keys['name'] == ''):
				conn.close()
				return(False,('not name!'))
				
			elif (not 'group' in keys) or (keys['group'] == ''):
				conn.close()
				return(False, ('\"' + keys['name'] + '\" not group'))
				
			# edit name
			if asset_type in ['shot_animation']:
				keys['name'] = keys['name'].replace(' ', '_')
			else:
				keys['name'] = keys['name'].replace(' ', '_').replace('.', '_')
				
			#while keys['name'] in assets:
			if keys['name'] in assets:
				#keys['name'] = keys['name'] + '01'
				conn.close()
				return(False, ('Name ' + '\"' + keys['name'] + '\" already exists!'))
		
			keys['name'] = keys['name'].replace(' ','_')
			keys['type'] = asset_type
			keys['status'] = 'active'
			
			if asset_type in self.asset_types_with_season and not keys['season']:
				conn.close()
				return(False, ('\"' + keys['name'] + '\" not season'))
		
			# get id
			keys['id'] = hex(random.randint(0, 1000000000)).replace('0x','')
			while keys['id'] in ids:
				keys['id'] = hex(random.randint(0, 1000000000)).replace('0x','')
				
			# get priority
			if (not 'priority' in keys) or (keys['priority'] == ''):
				keys['priority'] = '0'
			
			# -- make folders
			asset_path = ''
			if not 'path' in keys.keys():
				keys['path'] = ''
			if keys['path'] == '':
				asset_path = os.path.join(self.path, self.folders['assets'],asset_type, keys['name'])
				# create group folder
				group_dir = os.path.join(self.path, self.folders['assets'],asset_type)
				if not os.path.exists(group_dir):
					try:
						os.mkdir(group_dir)
					except:
						conn.close()
						return(False, '**** studio/project/asset.create -> you can not create a folder \'assets/asset_type\'')
				# create root folder
				if not os.path.exists(asset_path):
					try:
						os.mkdir(asset_path)
					except:
						conn.close()
						return(False, '**** studio/project/asset.create -> you can not create a folder \'assets/asset_type/asset\'')
				#keys['path'] = asset_path
				
			else:
				if os.path.exists(keys['path']):
					asset_path = keys['path']
				else:
					conn.close()
					return(False, '**** studio/project/asset.create -> asset_path not found!')
			
			keys['path'] = asset_path
			
			# -- create activity folders
			for activity in self.ACTIVITY_FOLDER[asset_type]:
				folder_path = os.path.join(asset_path, self.ACTIVITY_FOLDER[asset_type][activity])
				if not os.path.exists(folder_path):
					os.mkdir(folder_path)
					
			# -- create additional folders  self.ADDITIONAL_FOLDERS
			for activity in self.ADDITIONAL_FOLDERS:
				folder_path = os.path.join(asset_path, self.ADDITIONAL_FOLDERS[activity])
				if not os.path.exists(folder_path):
					os.mkdir(folder_path)
		
			# create string
			string = "insert into " + table + " values"
			values = '('
			data = []
			for i, key in enumerate(self.asset_keys):
				if i< (len(self.asset_keys) - 1):
					values = values + '?, '
				else:
					values = values + '?'
				if key[0] in keys:
					data.append(keys[key[0]])
				else:
					if key[1] == 'real':
						data.append(0.0)
					elif key[1] == 'timestamp':
						data.append(datetime.datetime.now())
					else:
						data.append('')
						
			values = values + ')'
			data = tuple(data)
			string = string + values
			
			# add asset
			#print('\n', string, data)
			c.execute(string, data)
			
			# -------------------------- Make Tasks Data------------------------------ set_of_tasks
			
			# add service tasks ("final")
			final = {
				'asset':keys['name'],
				'asset_id': keys['id'],
				'asset_type': asset_type,
				'task_name': (keys['name'] + ':final'),
				'season': keys['season'],
				'status':'null',
				'task_type':'service',
			}
			
			this_asset_tasks = []
			# create service tasks ("all_input")
			all_input = {
				'asset':keys['name'],
				'asset_id': keys['id'],
				'asset_type': asset_type,
				'task_name': (keys['name'] + ':all_input'),
				'season': keys['season'],
				'status':'done',
				'task_type':'service',
				'input':'',
				#'output': json.dumps([final['task_name']])
				'output': '',
			}
			this_asset_tasks.append(all_input)
		
			# get list from set_of_tasks
			result = set_of_tasks().get(keys['set_of_tasks'])
			if result[0]:
				set_tasks = result[1]['sets']
				
				outputs = {}
				for task_ in set_tasks:
					# name
					name = task_['task_name']
					task_['task_name'] = keys['name'] + ':' + name
					
					# output
					task_['output'] = json.dumps([final['task_name']])
					
					# input
					input_ = task_['input']
					if  input_ == 'all':
						task_['input'] = all_input['task_name']
						# status
						task_['status'] = 'ready'
						# add to output all_input
						all_outputs = json.loads(all_input['output'])
						all_outputs.append(task_['task_name'])
						all_input['output'] = json.dumps(all_outputs)
						
					elif input_ == 'pre':
						task_['input'] = keys['name'] + ':pre_input:' + name
						# status
						task_['status'] = 'ready'
						# add service tasks ("pre_input" )
						pre_input = {
							'asset':keys['name'],
							'asset_id': keys['id'],
							'asset_type': asset_type,
							'task_name': task_['input'],
							'season': keys['season'],
							'status':'done',
							'task_type':'service',
							'input':'',
							#'output': json.dumps([final['task_name'], task_['task_name']])
							'output': json.dumps([task_['task_name']])
						}
						this_asset_tasks.append(pre_input)
					elif input_:
						task_['input'] = keys['name'] + ':' + input_
						# status
						task_['status'] = 'null'
						
						# outputs
						if task_['input'] in outputs.keys():
							outputs[task_['input']].append(task_['task_name'])
						else:
							outputs[task_['input']] = [task_['task_name'],]
						
						
						# outputs
						#try:
						#	outputs[task_['input']].append(task_['task_name'])
						#except:
						#	outputs[task_['input']] = task_['task_name']
						
						
					else:
						# status
						task_['status'] = 'ready'
						
					# price
					task_['price'] = task_['cost']
						
					# asset
					task_['asset'] = keys['name']
					task_['asset_id'] = keys['id']
					task_['asset_type'] = asset_type
					
					# season
					task_['season'] = keys['season']
					
					# readers
					task_['readers'] = "{}"
					
					# append task
					this_asset_tasks.append(task_)
					
				for task_ in this_asset_tasks:
					if task_['task_name'] in outputs:
						if task_['output']:
							task_outputs = json.loads(task_['output'])
							#task_outputs.append(outputs[task_['task_name']])
							task_outputs = task_outputs + outputs[task_['task_name']]
							task_['output'] = json.dumps(task_outputs)
						else:
							task_['output'] = json.dumps(outputs['task_name'])
			
			# set input of "final"
			final_input = []
			for task_ in this_asset_tasks:
				final_input.append(task_['task_name'])
			final['input'] = json.dumps(final_input)
			
			# append final to task list
			this_asset_tasks.append(final)
		
			############################## make tasks to asset
			copy = task()
			#result = copy.create_tasks_from_list(project_name, keys['name'], keys['id'], this_asset_tasks)
			result = copy.create_tasks_from_list(project_name, keys, this_asset_tasks)
			if not result[0]:
				conn.close()
				return(False, result[1])
			
			# append to tasks_of_assets {asset: tasks_list, ... }
			tasks_of_assets[keys['name']] = this_asset_tasks
			
			# make return data
			make_assets[keys['name']] = keys
		
		# CLOSE .db
		conn.commit()
		conn.close()
		'''
		'''
		# send to tasks create  # tasks_of_assets /home/renderberg/create_tasks.json
		with open('/home/renderberg/create_tasks.json', 'w') as f:
		#with open('C:/Users/vladimir/Documents/blender_area/create_tasks.json', 'w') as f:
			jsn = json.dump(tasks_of_assets, f, sort_keys=True, indent=4)
			f.close()
		'''
		
		return(True, make_assets)
	
	# asset_data (dict) - словарь по asset_keys
	def remove_asset(self, asset_data): # v2
		pass
		# 1 - получение id recycle_bin
		# 2 - замена группы ассета на recycle_bin, обнуление priority, status.
		# 3 - список задач ассета
		# 4 - перезапись задачь ассета, обнуление: status, artist, readers, priority.
		# 5 - разрывы исходящих связей в другие ассеты.
		
		# (1)
		# -- get recycle bin  data
		result = group(self.project).get_by_keys({'type': 'all'})
		if not result[0]:
			return(False, ('in asset().remove_asset' + result[1]))
		recycle_bin_data = result[1][0]
		
		# (2)
		update_data = {'group': recycle_bin_data['id'], 'priority': 0, 'status':'none'}
		where = {'id': asset_data['id']}
		bool_, return_data = database().update('project', self.project, asset_data['type'], self.asset_keys, update_data, where, table_root=self.assets_db)
		if not bool_:
			return(bool_, return_data)
		'''
		# -- edit  .db
		try:
			conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return(False, 'in asset()remove_asset - Not .db connect!')
		
		table = asset_data['type']
		string = 'UPDATE ' +  table + ' SET \"group\" = ?, priority = ? WHERE id = ?'
		data = (recycle_bin_data['id'], '0', asset_data['id'])
		c.execute(string, data)
		conn.commit()
		conn.close()
		'''
		
		# (3)
		bool_, task_list = task(self).get_list(asset_id = asset_data['id'])
		if not bool_:
			return(bool_, task_list)
		
		output_tasks = []
		output_tasks_name_list = []
		table = '"%s:%s"' % (asset_data['id'], self.tasks_t)
		# (4)
		for row in task_list:
			if row['task_type'] == 'service':
				continue
			if row.get('output'):
				for task_name in row['output']:
					if task_name.split(':')[0] != row['asset_name']:
						output_tasks.append((row, task_name))
						output_tasks_name_list.append(task_name)
			# -- -- get status
			new_status = 'null'
			if not row['input']:
				new_status = 'ready'
			
			update_data = {'artist':'', 'status': new_status, 'readers': [], 'priority':0}
			where = {'task_name': row['task_name']}
			bool_, r_data = database().update('project', self.project, table, self.tasks_keys, update_data, where, table_root=self.tasks_db)
			if not bool_:
				bool_, r_data
		'''
		# ******** DISCONNECT ARTISTS, READERS
		output_tasks = []
		output_tasks_name_list = []
		# Connect to db
		try:
			conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return(False, 'in asset()remove_asset - Not .db connect!')
		# get tasks rows
		table = '\"' + asset_data['id'] + ':' + self.tasks_t + '\"'
		string = 'select * from ' + table
		c.execute(string)
		for row in c.fetchall():
			if not row['output']:
				print('*'*250, row['task_name'])
				continue
			for task_name in json.loads(row['output']):
				if task_name.split(':')[0] != row['asset']:
					output_tasks.append((row, task_name))
					output_tasks_name_list.append(task_name)
			if row['task_type'] == 'service':
				continue
			# -- -- get status
			new_status = 'null'
			if not row['input']:
				new_status = 'ready'
			# -- -- update .db
			string = 'UPDATE ' +  table + ' SET artist = ?, readers = ?, status = ? WHERE task_name = ?'
			data = ('', json.dumps([]),new_status, row['task_name'])
			c.execute(string, data)
			
		conn.commit()
		conn.close()
		'''
		
		# (5)
		# ******** DISCONNECT OUTPUTS
		# -- get output tasks dict
		result = task(self).get_tasks_data_by_name_list(output_tasks_name_list)
		if not result[0]:
			return(False, ('in asset().remove_asset -' + result[1]))
		output_tasks_data_dict = result[1]
		
		for key in output_tasks:
			if not key[1]:
				continue
			if output_tasks_data_dict[key[1]]['task_type'] == 'service':
				result = task(self).service_remove_task_from_input(output_tasks_data_dict[key[1]], [key[0]])
			else:
				print((output_tasks_data_dict[key[1]]['task_name'] + ' not service!'))
				continue
		
		return(True, 'Ok!')
	
	# self.project должен быть инициализирован
	# new_group_name (str)
	# new_asset_name (str)
	# new_asset_type (str) из studio.asset_types
	# set_of_tasks (str)
	# data_of_source_asset (dict) - дата копируемого ассета, если False - то копируется инициализированный ассет.
	def copy_of_asset(self, new_group_name, new_asset_name, new_asset_type, set_of_tasks, data_of_source_asset=False): # v2
		pass
		# 1 приведение имени нового ассета к стандарту
		# 2 получение id группы по имени
		# 3 заполнение data_of_source_asset - по данным self, в случае если = False
		# 4 составление словаря на создание ассета
		# 5 создание ассета
		# 6 копирование директорий
        
		# (1) edit name
		if new_asset_type in ['shot_animation']:
			new_asset_name = new_asset_name.replace(' ', '_')
		else:
			new_asset_name = new_asset_name.replace(' ', '_').replace('.', '_')
		
		# (2) get group id
		result = group(self.project).get_by_name(new_group_name)
		if not result[0]:
			return(False, result[1])
		new_group_id = result[1]['id']
		
		# (3)
		if not data_of_source_asset:
			for key in self.asset_types:
				if key in dir(self):
					data_of_source_asset[key] = self.key
				else:
					data_of_source_asset[key] = None
		
		# (4) get list_keys
		old_path = data_of_source_asset['path']
		old_name = data_of_source_asset['name']
		old_type = data_of_source_asset['type']
		data_of_source_asset['set_of_tasks'] = set_of_tasks
		data_of_source_asset['type'] = new_asset_type
		data_of_source_asset['group'] = new_group_id
		data_of_source_asset['name'] = new_asset_name
		data_of_source_asset['path'] = ''
		
		list_keys = [data_of_source_asset]
		
		print(json.dumps(list_keys, sort_keys = True, indent = 4))
		
		# (5) make asset
		result = self.create(new_asset_type, list_keys)
		if not result[0]:
			return(False, result[1])
			
		# (6) copy activity files
		# -- copy meta data
		new_asset_data = result[1][new_asset_name]
		for key in self.ADDITIONAL_FOLDERS:
			#print('*'*50)
			#print('old_path', old_path)
			src_activity_path = NormPath(os.path.join(old_path, self.ADDITIONAL_FOLDERS[key]))
			dst_activity_path = NormPath(os.path.join(new_asset_data['path'], self.ADDITIONAL_FOLDERS[key]))
			for obj in os.listdir(src_activity_path):
				src = NormPath(os.path.join(src_activity_path, obj))
				dst = NormPath(os.path.join(dst_activity_path, obj.replace(old_name, new_asset_name))) # + replace name
				#print('*'*50)
				#print('src', src)
				#print('dst', dst)
				if os.path.isfile(src):
					shutil.copyfile(src, dst)
				elif os.path.isdir(src):
					shutil.copytree(src, dst)
		
		# -- copy activity version
		old_activites = self.ACTIVITY_FOLDER[old_type]
		activites = self.ACTIVITY_FOLDER[new_asset_type]
		for key in activites:
			# -- get activity dir
			if not key in old_activites:
				continue
			src_activity_dir = NormPath(os.path.join(old_path, old_activites[key]))
			
			if not os.path.exists(src_activity_dir):
				continue
			
			versions = os.listdir(src_activity_dir)
			if not versions:
				continue
			
			# exceptions ['textures','cache']
			numbers = []
			int_hex = {}
			
			if key == 'textures' or (key == 'cache' and new_asset_type == 'char'):
				src_activity_path = src_activity_dir
				dst_activity_path = NormPath(os.path.join(new_asset_data['path'], activites[key]))
				if not os.path.exists(dst_activity_path):
					os.mkdir(dst_activity_path)
				
			else:
				#numbers = []
				#int_hex = {}
				for version in versions:
					num = int(version, 16)
					numbers.append(num)
					int_hex[str(num)] = version
				
				# -- -- get version contents
				while not os.listdir(os.path.join(src_activity_dir, int_hex[str(max(numbers))])):
					numbers.remove(max(numbers))
				
				src_activity_path = NormPath(os.path.join(old_path, old_activites[key], int_hex[str(max(numbers))]))
				dst_activity_path = NormPath(os.path.join(new_asset_data['path'], activites[key], '0000'))
				
				# -- -- make new dirs
				if not os.path.exists(NormPath(os.path.join(new_asset_data['path'], activites[key]))):
					os.mkdir(NormPath(os.path.join(new_asset_data['path'], activites[key])))
				if not os.path.exists(dst_activity_path):
					os.mkdir(dst_activity_path)
			
			# -- -- copy content
			for obj in os.listdir(src_activity_path):
				src = NormPath(os.path.join(src_activity_path, obj))
				dst = NormPath(os.path.join(dst_activity_path, obj.replace(old_name, new_asset_name)))
				if os.path.isfile(src):
					shutil.copyfile(src, dst)
					#print(int_hex[str(max(numbers))], obj)
				elif os.path.isdir(src):
					shutil.copytree(src, dst)
					#print(int_hex[str(max(numbers))], obj)
		
		# (7) copy preview image
		img_folder_path = NormPath(os.path.join(self.project.path, self.project.folders['preview_images']))
		old_img_path = NormPath(os.path.join(img_folder_path, (old_name + '.png')))
		old_img_icon_path = NormPath(os.path.join(img_folder_path, (old_name + '_icon.png')))
		new_img_path = NormPath(os.path.join(img_folder_path, (new_asset_name + '.png')))
		new_img_icon_path = NormPath(os.path.join(img_folder_path, (new_asset_name + '_icon.png')))
		
		if os.path.exists(old_img_path):
			shutil.copyfile(old_img_path, new_img_path)
		if os.path.exists(old_img_icon_path):
			shutil.copyfile(old_img_icon_path, new_img_icon_path)
		
		return(True, 'Ok!')
	
	# group_id - если не False - то возвращает список ассетов данной группы
	def get_list_by_type(self, asset_type, group_id = False): # v2
		if group_id:
			where = {'group': group_id}
		else:
			where = False
		bool_, return_data = database().read('project', self.project, asset_type, self.asset_keys, where = where, table_root=self.assets_db)
		if not bool_:
			print('#'*5, return_data)
			return(True, [])
		else:
			for asset in return_data:
				asset['path'] = NormPath(os.path.join(self.project.path, self.project.folders['assets'],asset['type'], asset['name']))
			return(True, return_data)
	
	# group_id - если не False - то возвращает список ассетов данной группы
	def get_list_by_all_types(self, group_id = False): # v2
		if group_id:
			where = {'group': group_id}
		else:
			where = False
		assets_list = []
		for asset_type in self.asset_types:
			bool_, return_data = database().read('project', self.project, asset_type, self.asset_keys, where = where, table_root=self.assets_db)
			if not bool_:
				print('#'*5, return_data)
				continue
			else:
				assets_list = assets_list + return_data
		for asset in assets_list:
			asset['path'] = NormPath(os.path.join(self.project.path, self.project.folders['assets'],asset['type'], asset['name']))
		return(True, assets_list)
		
	def get_list_by_group(self, group_id): # v2
		pass
		# get group_type
		group_data = group(self.project).get_by_id(group_id)
		if group_data[0]:
			group_type = group_data[1]['type']
		else:
			return(False, group_data[1])
		
		all_list = []
		if group_type == 'all':
			list_by_type = self.get_list_by_all_types(group_id = group_id)
			if not list_by_type[0]:
				return(False, list_by_type[1])
			all_list = list_by_type[1]
		
		else:
			# get asset list by type
			list_by_type = self.get_list_by_type(group_type, group_id = group_id)
			if not list_by_type[0]:
				return(False, list_by_type[1])
			all_list = list_by_type[1]
		
		for asset in all_list:
			asset['path'] = NormPath(os.path.join(self.project.path, self.project.folders['assets'],asset['type'], asset['name']))
		return(True, all_list)
	'''
	def get_name_list_by_type(self, project_name, asset_type):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# write season to db
		conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		try:
			table = asset_type
			str_ = 'select * from ' + table
			c.execute(str_)
			rows = c.fetchall()
			names = []
			for row in rows:
				names.append(row['name'])
			conn.close()
			return(True, rows)
		except:
			conn.close()
			return(True, [])
	'''
			
	def get_id_name_dict_by_type(self, asset_type): # v2
		bool_, return_data = database().read('project', self.project, asset_type, self.asset_keys, table_root=self.assets_db)
		if not bool_:
			return(bool_, return_data)
		asset_id_name_dict = {}
		for row in return_data:
			#row['path'] = NormPath(os.path.join(self.project.path, self.project.folders['assets'],row['type'], row['name']))
			asset_id_name_dict[row['id']] = row['name']
		return(True, asset_id_name_dict)
		
			
	def get_name_data_dict_by_all_types(self): # v2
		asset_list = []
		for asset_type in self.asset_types:
			bool_, return_data = database().read('project', self.project, asset_type, self.asset_keys, table_root=self.assets_db)
			if not bool_:
				print(return_data)
				continue
			asset_list = asset_list + return_data
		# make dict
		assets_dict = {}
		for asset in asset_list:
			asset['path'] = NormPath(os.path.join(self.project.path, self.project.folders['assets'],asset['type'], asset['name']))
			assets_dict[asset['name']] = asset
		return(True, assets_dict)
			
	def get_by_name(self, asset_type, asset_name): # v2
		where = {'name': asset_name}
		bool_, return_data = database().read('project', self.project, asset_type, self.asset_keys, where=where, table_root=self.assets_db)
		if not bool_:
			return(bool_, return_data)
		if return_data:
			asset = return_data[0]
			asset['path'] = NormPath(os.path.join(self.project.path, self.project.folders['assets'],asset['type'], asset['name']))
			return(True, asset)
		else:
			return(False, 'No Asset With This Name(%s)!' % asset_name)
	
	def get_by_id(self, asset_type, asset_id): # v2
		where = {'id': asset_id}
		bool_, return_data = database().read('project', self.project, asset_type, self.asset_keys, where=where, table_root=self.assets_db)
		if not bool_:
			return(bool_, return_data)
		if return_data:
			asset = return_data[0]
			asset['path'] = NormPath(os.path.join(self.project.path, self.project.folders['assets'],asset['type'], asset['name']))
			return(True, asset)
		else:
			return(False, 'No Asset With This id(%s)!' % asset_id)
	
	# keys - словарь по asset_keys, 
	# -- *name - для идентификации ассета
	# -- *type - для идентификации таблицы
	# -- не меняемые значения 'name', 'type', 'id', 'path'
	def edit_asset_data_by_name(self, keys): # v2
		pass
		# test Name Type
		if not 'name' in keys:
			return(False, 'Name not specified!')
		elif not 'type' in keys:
			return(False, 'Type not specified!')
		
		where = {'name': keys['name']}
		table_name = keys['type']
		# cleaning keys
		del keys['name']
		for key in self.UNCHANGEABLE_KEYS:
			if key in keys:
				del keys[key]
		# update
		bool_, return_data = database().update('project', self.project, table_name, self.asset_keys, keys, where, table_root=self.assets_db)
		if not bool_:
			return(bool_, return_data)
		
		return(True, 'Ok!')
	
	# keys - словарь по asset_keys, 
	# -- *id - для идентификации ассета
	# -- *type - для идентификации таблицы
	# -- не меняемые значения: 'name', 'type', 'id', 'path'
	def edit_asset_data_by_id(self, keys): # v2
		pass
		# test Name Type
		if not 'id' in keys:
			return(False, 'Id not specified!')
		elif not 'type' in keys:
			return(False, 'Type not specified!')
		
		where = {'id': keys['id']}
		table_name = keys['type']
		# cleaning keys
		for key in self.UNCHANGEABLE_KEYS:
			if key in keys:
				del keys[key]
		# update
		bool_, return_data = database().update('project', self.project, table_name, self.asset_keys, keys, where, table_root=self.assets_db)
		if not bool_:
			return(bool_, return_data)
		
		return(True, 'Ok!')
		
	def change_group_of_asset(self, asset_type, asset_name, new_group_id): # v2
		keys = {
		'name': asset_name,
		'type': asset_type,
		'group': new_group_id,
		}
		
		result = self.edit_asset_data_by_name(keys)
		if not result[0]:
			return(False, result[1])
		else:
			return(True, 'Ok!')
			
	def rename_asset(self, asset_type, old_name, new_name): # v2 ???????? ассет нельзя переименовывать!!!!!!!!!!!!!!!!!
		pass
		# get id by name
		result = self.get_by_name(asset_type, old_name)
		if not result[0]:
			return(False, result[1])
		
		# rename
		keys = {
		'name': new_name,
		'type': asset_type,
		'id': result[1]['id'],
		}
		
		result = self.edit_asset_data_by_id(keys)
		if not result[0]:
			return(False, result[1])
		else:
			return(True, 'Ok!')

class task(studio):
	'''
	studio.project.asset.task()
	
	KEYS (season text, task_name text, asset text, activity text, input text, status text, artist text, planned_time text, time text, start text, end text, supervisor text, approved_date text, price real, tz text, chat text)
	
	self.add_task(project_name, asset_name, {key:data, ...}) - add task in .tasks.db;; return: 'ok' - all right; False - ather errors; 'overlap' - the task has not been created, this task name already exists; 'not_project' - not project;  'not_asset' - ... ; 'required' - lacking data (first three values)
	
	self.edit_task(project_name, asset_name, {key:data, ...}) - edit data in .tasks.db;; return: 'ok' - all right, False - ather errors; 'not_project' - not project;  'not_asset' - ...
	
	self.read_task(project_name, task_name, [keys]) - return data (True/False, {key: data, ...}/error) ;; error: (not_project, not_task_name) 
	
	self.edit_status_to_output(project_name, task_name) - (run from edit_task() on status change for 'ready') ;; changes the status of the all outgoing tasks from 'null' to 'ready';; return (True/False, 'ok'/'ather comment')
		
	'''
	
	def __init__(self, asset):
		self.asset = asset
		self.VARIABLE_STATUSES = ('ready', 'ready_to_send', 'work', 'work_to_outsorce')
		
		self.CHANGE_BY_OUTSOURCE_STATUSES = {
		'to_outsource':{'ready':'ready_to_send', 'work':'ready_to_send'},
		'to_studio':{'ready_to_send':'ready', 'work_to_outsorce':'ready'},
		}
		
		#self.db_workroom = workroom() # ??????? как всегда под вопросом
		#self.publish = lineyka_publish.publish()
		
		self.publish = publish(self, NormPath) # ??????? как всегда под вопросом
		
	def init(self, keys):
		for key in self.tasks_keys:
			exec('self.%s = keys.get("%s")' % (key, key))
		
	# ************************ CHANGE STATUS ******************************** start
	
	@staticmethod
	def _input_to_end(task_data): # v2
		if task_data['status'] == 'close':
			return(False)
		
		autsource = bool(task_data['outsource'])
				
		if autsource:
			return('ready_to_send')
		else:
			return('ready')
	
	# изменение статуса сервис задачи, по проверке статусов входящих задачь.
	# task_data (dict) - текущая задача.
	# assets (dict) - словарь всех ассетов по всем типам (ключи - имена, данные - ассеты (словари)) - результат функции asset.get_name_data_dict_by_all_types()
	def service_input_to_end(self, task_data, assets): # v2 *** не тестилось.
		new_status = False
		
		# (1) get input_list
		input_list = task_data['input']
		if not input_list:
			return(True, new_status)
		
		# get status
		bool_statuses = []
		# --------------- fill end_statuses -------------
		'''
		# ****** connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		'''
		for task_name in input_list:
			# (2) asse id
			asset_id = assets[task_name.split(':')[0]].get('id')
			if not asset_id:
				print('in task.service_input_to_end() incorrect key "id" in  "%s"' % task_name.split(':')[0])
				continue
			'''
			table = '\"' + asset_id + ':' + self.tasks_t + '\"'
			
			string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
			try:
				c.execute(string)
				task_data = c.fetchone()
			except:
				conn.close()
				return(False, ('in from_service_remove_input_tasks can not read ', string))
			'''
			# (3) get task data
			table_name = '"%s:%s"' % (asset_id, self.tasks_t)
			read_ob = self.asset.project
			where = {'task_name': task_name}
			bool_, return_data = database().read('project', read_ob, table_name, self.tasks_keys, where=where, table_root=self.tasks_db)
			if not bool_:
				return(bool_, return_data)
			elif return_data:
				task_data = return_data[0]
			else:
				return(False, 'Task Data Not Found! Task_name - "%s"' % task_name)
			# (4) make status
			if task_data['status'] in self.end_statuses:
				bool_statuses.append(True)
			else:
				bool_statuses.append(False)
		
		#conn.close()
		
		if False in bool_statuses:
			new_status = 'null'
		else:
			new_status = 'done'
			#self.this_change_to_end(self, project_name, task_data)
			
		return(True, new_status)
	
	def from_input_status(self, task_data, input_task_data):  # input_task_data = row{self.task_keys} or False
		pass
		# get task_outsource
		task_outsource = bool(task_data['outsource'])
		
		new_status = None
		# change status
		if input_task_data:
			if input_task_data['status'] in self.end_statuses:
				if not task_outsource:
					if task_data['status'] == 'null':
						new_status = 'ready'
				else:
					if task_data['status'] == 'null':
						new_status = 'ready_to_send'
			else:
				if task_data['status'] != 'close':
					new_status = 'null'
		else:
			if not task_data['status'] in self.end_statuses:
				if task_outsource:
					new_status = 'ready_to_send'
				else:
					new_status = 'ready'
		return(new_status)
		
	# замена статусов исходящих задачь при изменении статуса текущей задачи с done или с close.
	# task_data (dict) - текущая задача.
	# assets (dict) - словарь всех ассетов по всем типам (ключи - имена, данные - ассеты (словари)) - результат функции asset.get_name_data_dict_by_all_types()
	def this_change_from_end(self, task_data, assets = False): # v2 *** no test
		pass
		# 1 - список исходящих задачь
		# 2 - получение списка всех ассетов
		# 3 - цикл по списку исходящих задачь (output_list)
		# - 4 - получение id ассета
		# - 5 - чтение таск даты
		# - 6 - определение нового статуса
		# - 7 - изменения в readers
		# - 8 - запись таск
		# 9 - отправка далее в себя же - this_change_from_end() - по списку from_end_list
		
		#
		from_end_list = []
		this_asset_type = task_data['asset_type']
		
		# (1)
		output_list = task_data.get('output')
		if not output_list:
			return(True, 'Ok!')
		# (2)
		if not assets:
			# get assets dict
			result = self.asset.get_name_data_dict_by_all_types()
			if not result[0]:
				return(False, result[1])
			assets = result[1]
		'''
		# ****** connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		'''
		# (3) ****** change status
		for task_name in output_list:
            # (4) asse id
			asset_id = assets[task_name.split(':')[0]].get('id')
			if not asset_id:
				print('in this_change_from_end incorrect key "id" in  "%s"' % task_name.split(':')[0])
				continue
			'''
			#table = '\"' + asset_id + ':' + self.tasks_t + '\"'
			
			string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
			try:
				c.execute(string)
				task_data = c.fetchone()
			except:
				conn.close()
				return(False, ('in this_change_from_end can not read ', string))
				#return(False, string)
			'''
			# (5) get task data
			table_name = '"%s:%s"' % (asset_id, self.tasks_t)
			read_ob = self.asset.project
			where = {'task_name': task_name}
			bool_, return_data = database().read('project', read_ob, table_name, self.tasks_keys, where=where, table_root=self.tasks_db)
			if not bool_:
				return(bool_, return_data)
			elif return_data:
				task_data = return_data[0]
			else:
				return(False, 'Task Data Not Found! Task_name - "%s"' % task_name)
			# (6) make new status char и obj не отключают локацию и аним шот, а локация отключает аним шот.
			if task_data['status'] == 'close':
				continue
			elif task_data['asset_type'] in ['location', 'shot_animation'] and this_asset_type not in ['location', 'shot_animation']:
				continue
			elif task_data['status'] == 'done':
				from_end_list.append(task_data)
				
			new_status = 'null'
			# (7) edit readers
			readers = {}
			try:
				readers = task_data['readers']
			except:
				pass
			if readers:
				for key in readers:
					readers[key] = 0
				#string = 'UPDATE ' +  table + ' SET  readers = ?, status  = ? WHERE task_name = ?'
				#data = (json.dumps(readers), new_status, task_name)
				update_data = {'readers': readers, 'status': new_status}
			else:
				#string = 'UPDATE ' +  table + ' SET  status  = ? WHERE task_name = ?'
				#data = (new_status, task_name)
				update_data = {'status': new_status}
			# (8)
			#c.execute(string, data)
			where = {'task_name': task_name}
			bool_, return_data = database().update('project', read_ob, table_name, self.tasks_keys, update_data, where, table_root=self.tasks_db)
			if not bool_:
				return(bool_, return_data)
		'''
		conn.commit()
		conn.close()
		'''
		
		# (9) ****** edit from_end_list
		if from_end_list:
			for t_d in from_end_list:
				self.this_change_from_end(t_d, assets = assets)
		
		
		return(True, 'Ok!')
		
	# замена статусов исходящих задачь при изменении статуса текущей задачи на done или close.
	# task_data (dict) - текущая задача.
	# assets (dict) - словарь всех ассетов по всем типам (ключи - имена, данные - ассеты (словари)) - результат функции asset.get_name_data_dict_by_all_types()
	def this_change_to_end(self, task_data, assets = False): # v2 *** no test
		pass
		# 1 - список исходящих задачь
		# 2 - получение списка всех ассетов
		# 3 - цикл по списку исходящих задачь (output_list)
		# - 4 - получение id ассета
		# - 5 - чтение таск даты
		# - 6 - определение нового статуса
		# - 7 - запись таск
		# 8 - отправка далее в себя же - this_change_to_end() - по списку service_to_done
        
		# (1)
		output_list = task_data.get('output')
		if not output_list:
			return(True, 'Ok!')
		# (2)
		if not assets:
			# get assets dict
			result = self.asset.get_name_data_dict_by_all_types()
			if not result[0]:
				return(False, result[1])
			assets = result[1]
		'''
		# ****** connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		'''
		service_to_done = []
		# ****** change status
		for task_name in output_list:
			# (4) asse id
			asset_id = assets[task_name.split(':')[0]].get('id')
			if not asset_id:
				print('in this_change_to_end incorrect key "id" in  "%s"' % task_name.split(':')[0])
				continue
			'''
			table = '\"' + asset_id + ':' + self.tasks_t + '\"'
			string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
			try:
				c.execute(string)
				task_data_ = c.fetchone()
			except:
				conn.close()
				return(False, ('in this_change_to_end can not read ', string))
			'''
			# (5) get task data
			table_name = '"%s:%s"' % (asset_id, self.tasks_t)
			read_ob = self.asset.project
			where = {'task_name': task_name}
			bool_, return_data = database().read('project', read_ob, table_name, self.tasks_keys, where=where, table_root=self.tasks_db)
			if not bool_:
				return(bool_, return_data)
			elif return_data:
				task_data_ = return_data[0]
			else:
				return(False, 'Task Data Not Found! Task_name - "%s"' % task_name)
            
			# (6) make new status
			if task_data_['task_type'] == 'service':
				result = self.service_input_to_end(task_data_, assets)
				if not result[0]:
					return(False, result[1])
				new_status = result[1]
				if new_status == 'done':
					service_to_done.append(task_data_)
			else:
				new_status = self._input_to_end(task_data_)
				
			if not new_status:
				continue
			'''
			string = 'UPDATE ' +  table + ' SET  status  = ? WHERE task_name = ?'
			data = (new_status, task_name)
			c.execute(string, data)
			'''
			# (7)
			update_data = {'status': new_status}
			where = {'task_name': task_name}
			bool_, return_data = database().update('project', read_ob, table_name, self.tasks_keys, update_data, where, table_root=self.tasks_db)
			if not bool_:
				return(bool_, return_data)
		#conn.commit()
		#conn.close()
		# (8)
		if service_to_done:
			for task in service_to_done:
				self.this_change_to_end(task, assets = assets)
		
		return(True, 'Ok!')
	'''	
	def from_service_remove_input_tasks(self, project_name, task_data, removed_tasks_list):
		# get input_list
		input_list = json.loads(task_data['input'])
		for task in removed_tasks_list:
			input_list.remove(task['task_name'])
			
		if not input_list:
			return(True, 'done')
			
		# get assets dict
		result = self.get_name_data_dict_by_all_types(project_name)
		if not result[0]:
			return(False, result[1])
		assets = result[1]
		
		bool_statuses = []
		# --------------- fill end_statuses -------------
		
		# ****** connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		for task_name in input_list:
			try:
				asset_id = assets[task_name.split(':')[0]]['id']
			except:
				print(('in from_service_remove_input_tasks incorrect key: ' + task_name.split(':')[0] + ' in ' + task_name))
				continue
			
			table = '\"' + asset_id + ':' + self.tasks_t + '\"'
			
			string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
			try:
				c.execute(string)
				task_data = c.fetchone()
			except:
				conn.close()
				return(False, ('in from_service_remove_input_tasks can not read ', string))
				
			if task_data['status'] in self.end_statuses:
				bool_statuses.append(True)
			else:
				bool_statuses.append(False)
		
		conn.close()
		
		if False in bool_statuses:
			new_status = 'null'
		else:
			new_status = 'done'
			
		return(True, new_status)
	'''
	# **************************** Task() File Path ************************************************
	
	# asset - должен быит инициализирован
	# task_data (dict) - требуется если не инициализирован task
	def get_final_file_path(self, task_data=False): # v2
		asset_path = self.asset.path
		if not task_data:
			asset_type = self.asset_type
			activity = self.activity
			asset = self.asset_name
			extension = self.extension
		else:
			asset_type = task_data['asset_type']
			activity = task_data['activity']
			asset = task_data['asset_name']
			extension = task_data['extension']
            
		folder_name = self.asset.ACTIVITY_FOLDER[asset_type][activity]
		activity_path = NormPath(os.path.join(asset_path, folder_name))
		
		if not os.path.exists(activity_path):
			try:
				os.mkdir(activity_path)
			except:
				print(activity_path)
				return(False, 'in task().get_final_file_path() Can not create activity dir!')
		
		# - get folder list
		folders_16 = os.listdir(activity_path)
		folders = []
		
		if len(folders_16)==0:
			return(True, None, asset_path)
		
		# - 16 to 10
		for obj_ in folders_16:
			folders.append(int(obj_, 16))
		'''
		for obj_ in folders_16:
			if int(obj_, 16) == max(folders):
				final_file = os.path.join(activity_path, obj_, (task_data['asset'] + task_data['extension']))
				break
		if os.path.exists(final_file):
			return(True, final_file, asset_path)
		else:
			return(True, None, asset_path)
		'''
		i = max(folders)
		while i > -1:
			hex_ = hex(i).replace('0x', '')
			num = 4 - len(hex_)
			hex_num = '0'*num + hex_
			
			final_file = os.path.join(activity_path, hex_num, '%s%s' % (asset, extension))
			if os.path.exists(final_file):
				return(True, final_file, asset_path)
			i = i-1
		
		return(True, None, asset_path)
	
	# asset - должен быит инициализирован
	# task_data (dict) - требуется если не инициализирован task
	# version (str) - hex
	def get_version_file_path(self, version, task_data=False): # v2
		asset_path = self.asset.path
		if not task_data:
			asset_type = self.asset_type
			activity = self.activity
			asset = self.asset_name
			extension = self.extension
		else:
			asset_type = task_data['asset_type']
			activity = task_data['activity']
			asset = task_data['asset_name']
			extension = task_data['extension']
				
		folder_name = self.asset.ACTIVITY_FOLDER[asset_type][activity]
		activity_path = NormPath(os.path.join(asset_path, folder_name))
		
		version_file = NormPath(os.path.join(activity_path, version, '%s%s' % (asset, extension)))
		
		if os.path.exists(version_file):
			return(True, version_file)
		else:
			return(False, 'Not Exists File!')
	
	# asset - должен быит инициализирован
	# task_data (dict) - требуется если не инициализирован task
	def get_new_file_path(self, task_data=False): # v2
		pass
		if not task_data:
			asset_type = self.asset_type
			activity = self.activity
			asset = self.asset_name
			extension = self.extension
		else:
			asset_type = task_data['asset_type']
			activity = task_data['activity']
			asset = task_data['asset_name']
			extension = task_data['extension']
		# get final file
		result = self.get_final_file_path(task_data)
		#final_file = None
		if not result[0]:
			return(False, result[1])
			
		final_file = result[1]
		asset_path = result[2]
		
		# get activity path
		folder_name = self.asset.ACTIVITY_FOLDER[asset_type][activity]
		activity_path = NormPath(os.path.join(asset_path, folder_name))
		# make activity folder
		if not os.path.exists(activity_path):
			os.mkdir(activity_path)
		
		if final_file == None:
			new_dir_path = NormPath(os.path.join(activity_path, '0000'))
			new_file_path = NormPath(os.path.join(new_dir_path, '%s%s' % (asset, extension)))
			
		else:
			ff_split = final_file.replace('\\','/').split('/')
			new_num_dec = int(ff_split[len(ff_split) - 2], 16) + 1
			new_num_hex = hex(new_num_dec).replace('0x', '')
			if len(new_num_hex)<4:
				for i in range(0, (4 - len(new_num_hex))):
					new_num_hex = '0' + new_num_hex
			
			new_dir_path = NormPath(os.path.join(activity_path, new_num_hex))
			new_file_path = NormPath(os.path.join(new_dir_path, '%s%s' % (asset, extension)))
		
		return(True, (new_dir_path, new_file_path))
	
	# asset - должен быит инициализирован
	# activity (str)
	def get_publish_file_path(self, activity): # v2
		pass
		# get task_data
		result = self.get_list(asset_id=self.asset.id)
		if not result[0]:
			return(False, result[1])
			
		task_data = None
		for td in result[1]:
			if td['activity'] == activity:
				task_data = td
				break
				
		if not task_data:
			return(False, 'No Found Task with this activity: "%s"!' % activity)
		
		# -- -- get publish dir
		publish_dir = NormPath(os.path.join(self.asset.path, self.publish_folder_name))
		if not os.path.exists(publish_dir):
			return(False, 'in task.get_publish_file_path() - Not Publish Folder! (%s)' % publish_dir)
		# -- -- get activity_dir
		activity_dir = NormPath(os.path.join(publish_dir, self.asset.ACTIVITY_FOLDER[self.asset.type][task_data['activity']]))
		if not os.path.exists(activity_dir):
			return(False, 'in task.get_publish_file_path() - Not Publish/Activity Folder! (%s)' % activity_dir)
		# -- -- get file_path
		file_path = NormPath(os.path.join(activity_dir, '%s%s' % (self.asset.name, task_data['extension'])))
		if not os.path.exists(file_path):
			print('#'*5, file_path)
			return(False, 'Publish/File Not Found!')
			
		return(True, file_path)
		
	
	# **************************** CACHE  ( file path ) ****************************
	def get_versions_list_of_cache_by_object(self, task_data, ob_name, activity = 'cache', extension = '.pc2'):
		asset_path = task_data['asset_path']
		
		folder_name = self.ACTIVITY_FOLDER[task_data['asset_type']][activity]
		activity_path = NormPath(os.path.join(asset_path, folder_name))
		activity_path = NormPath(activity_path)
		cache_dir_path = NormPath(os.path.join(asset_path, folder_name, ob_name))
		
		if not os.path.exists(cache_dir_path):
			return(False, 'No Found Cache Directory!')
			
		# - get folders list
		folders_16 = os.listdir(cache_dir_path)
		dec_nums = []
		tech_anim_cache_versions_list = []
		
		if not folders_16:
			return(False, 'No Found Cache Versions!')
			
		for num in folders_16:
			dec_nums.append(int(num, 16))
			
		dec_nums.sort()
		
		for i in dec_nums:
			number = None
			for num in folders_16:
				if i == int(num, 16):
					number = num
					break
			path = os.path.join(cache_dir_path, number, (ob_name + extension))
			path = NormPath(path)
			if number:
				if os.path.exists(path):
					tech_anim_cache_versions_list.append((str(i), ob_name, path))
				else:
					continue
				
		if tech_anim_cache_versions_list:
			return(True, tech_anim_cache_versions_list)
		else:
			return(False, 'No Found Cache Versions! *')
		
	
	def get_final_cache_file_path(self, task_data, cache_dir_name, activity = 'cache', extension = '.pc2'):
		asset_path = task_data['asset_path']
		
		folder_name = self.ACTIVITY_FOLDER[task_data['asset_type']][activity]
		activity_path = NormPath(os.path.join(asset_path, folder_name))
		activity_path = NormPath(activity_path)
		cache_dir_path = NormPath(os.path.join(asset_path, folder_name, cache_dir_name))
		cache_dir_path = NormPath(cache_dir_path)
		
		#print(cache_dir_path)
		
		if not os.path.exists(activity_path):
			os.mkdir(activity_path)
		if not os.path.exists(cache_dir_path):
			os.mkdir(cache_dir_path)
		
		# - get folder list
		folders_16 = os.listdir(cache_dir_path)
		folders = []
		
		if len(folders_16)==0:
			return(False, 'No Found Chache! *1')
		
		# - 16 to 10
		for obj_ in folders_16:
			folders.append(int(obj_, 16))
		
		i = max(folders)
		while i > -1:
			hex_ = hex(i).replace('0x', '')
			num = 4 - len(hex_)
			hex_num = '0'*num + hex_
			
			final_file = os.path.join(cache_dir_path, hex_num, (cache_dir_name + extension))
			if os.path.exists(final_file):
				return(True, final_file)
			i = i-1
		
		return(False, 'No Found Chache! *2')
		
	def get_new_cache_file_path(self, project_name, task_data, cache_dir_name, activity = 'cache', extension = '.pc2'):
		pass
		# get final file
		result = self.get_final_cache_file_path(task_data, cache_dir_name, activity = activity, extension = extension)
		#final_file = None
		if not result[0]:
			if result[1] == 'No Found Chache! *1' or result[1] == 'No Found Chache! *2':
				final_file = None
			else:
				return(False, result[1])
		else:
			final_file = result[1]
		asset_path = task_data['asset_path']
		
		# get activity path
		folder_name = self.ACTIVITY_FOLDER[task_data['asset_type']][activity]
		activity_path = NormPath(os.path.join(asset_path, folder_name, cache_dir_name))
		
		# make activity folder
		if not os.path.exists(activity_path):
			os.mkdir(activity_path)
		
		if final_file == None:
			new_dir_path = os.path.join(activity_path, '0000')
			new_file_path = os.path.join(new_dir_path, (cache_dir_name + extension))
			
		else:
			ff_split = final_file.replace('\\','/').split('/')
			new_num_dec = int(ff_split[len(ff_split) - 2], 16) + 1
			new_num_hex = hex(new_num_dec).replace('0x', '')
			if len(new_num_hex)<4:
				for i in range(0, (4 - len(new_num_hex))):
					new_num_hex = '0' + new_num_hex
			
			new_dir_path = os.path.join(activity_path, new_num_hex)
			new_file_path = os.path.join(new_dir_path, (cache_dir_name + extension))
		
		
		# make version dir
		if not os.path.exists(new_dir_path):
			os.mkdir(new_dir_path)
		
				 
		return(True, (new_dir_path, new_file_path))
		
	def get_version_cache_file_path(self, project_name, task_data, version, cache_dir_name, activity = 'cache', extension = '.pc2'):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		asset_path = task_data['asset_path']
		
		folder_name = self.ACTIVITY_FOLDER[task_data['asset_type']][activity]
		activity_path = NormPath(os.path.join(asset_path, folder_name, cache_dir_name))
		
		version_file = os.path.join(activity_path, version, (cache_dir_name + extension))
		
		if os.path.exists(version_file):
			return(True, version_file)
		else:
			return(False, 'Not Exists File!')
		
	# ************************ CHANGE STATUS ******************************** end
		
	def add_task(self, project_name, task_key_data): # не обнаружено использование
		pass
		# other errors test
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		# test exists ASSET  self.assets_list
		asset_name = task_key_data['asset']
		if not asset_name in self.assets_list:
			# self.print_log('')
			return False, 'not_asset'
			
		# test required parameters
		for i in range(0, 3):
			try:
				data = task_key_data[self.tasks_keys[i][0]]
			except:
				return False, 'required'
		#########		
		# get Autsource status
		# -- get artist
		outsource = None
		artist_name = task_key_data['artist']
		if artist_name:
			artist_data = artist().read_artist({'nik_name':artist_name})
			if artist_data[0]:
				if artist_data[1][0]['outsource'] == '1':
					outsource = True
		#########
				
		# set STATUS
		try:
			if task_key_data['input'] == '':
				######
				if outsource:
					task_key_data['status'] = "ready_to_send"
				else:
					task_key_data['status'] = "ready"
				######
			else:
				input_task_data = self.read_task(project_name, task_key_data['input'], ('status',))
				if input_task_data[0]:
					if input_task_data[1]['status'] == 'done':
						######
						if outsource:
							task_key_data['status'] = "ready_to_send"
						else:
							task_key_data['status'] = "ready"
						######
					else:
						task_key_data['status'] = "null"
				else:
					#'not_task_name'
					task_key_data['status'] = "null"
		except:
			######
			if outsource:
				task_key_data['status'] = "ready_to_send"
			else:
				task_key_data['status'] = "ready"
			######
				
		#
		table = '\"' + asset_name + ':' + self.tasks_t + '\"'
		string = "insert into " + table + " values"
		values = '('
		data = []
		for i, key in enumerate(self.tasks_keys):
			if i< (len(self.tasks_keys) - 1):
				values = values + '?, '
			else:
				values = values + '?'
			if key[0] in task_key_data:
				data.append(task_key_data[key[0]])
			else:
				if key[1] == 'real':
					data.append(0.0)
				elif key[1] == 'timestamp':
					data.append(None)
				else:
					data.append('')
					
		values = values + ')'
		data = tuple(data)
		string = string + values
		
		# write task to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# exists table
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
			# unicum task_name test
			r = c.fetchall()
			for row in r:
				if row['task_name'] == task_key_data['task_name']:
					conn.close()
					return False, 'overlap'
		except:
			string2 = "CREATE TABLE " + table + " ("
			for i,key in enumerate(self.tasks_keys):
				if i == 0:
					string2 = string2 + key[0] + ' ' + key[1]
				else:
					string2 = string2 + ', ' + key[0] + ' ' + key[1]
			string2 = string2 + ')'
			#print(string2)
			c.execute(string2)
		
		# add task
		c.execute(string, data)
		conn.commit()
		conn.close()
		return True, 'ok'
	
	def edit_task(self, project_name, task_key_data): # не обнаружено использование
		pass
		# other errors test
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		# test exists ASSET  asset
		asset_name = task_key_data['task_name'].split(':')[0]
		if not asset_name in self.assets_list:
			# self.print_log('')
			return False, 'not_asset'
		
		# test task_name
		try:
			task_name = (task_key_data['task_name'],)
		except:
			return False, 'not task_name'
			
		######     ==  COONNECT DATA BASE
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		table = '\"' + asset_name + ':' + self.tasks_t + '\"'
			
		######     == get current data
		command =  'SELECT * FROM ' + table + ' WHERE task_name = ?'
		c.execute(command, task_name)
		current_task_data = c.fetchone()
		#print('***** current name: ', current_task_data['artist'], 'new name:', task_key_data['artist'])
		
		#conn.close()
		#return
		######
			
		#########	 == get Autsource Status	
		# -- get artist
		outsource = None
		artist_name = None
		try:
			artist_name = task_key_data['artist']
		except:
			artist_name = current_task_data['artist']
		if artist_name:
			artist_data = artist().read_artist({'nik_name':artist_name})
			if artist_data[0]:
				if artist_data[1][0]['outsource'] == 1:
					outsource = True
		#########
		
		#########   == get Input Status
		input_status = None
		input_task_name = ''
		try:
			input_task_name = task_key_data['input']
		except:
			input_task_name = current_task_data['input']
		input_task_data = self.read_task(project_name, input_task_name, ['status'])
		if input_task_data[0]:
			input_status = input_task_data[1]['status']
		elif not input_task_data[0] and input_task_data[1] == 'not_task_name':
			input_status = 'done'
			
		
		######### self.working_statuses self.end_statuses
		
		# CHANGE STATUS
		try:
			task_key_data['status']
		except:
			pass
		else:
			if not (input_status in self.end_statuses):
				task_key_data['status'] = "null"
			elif task_key_data['status'] == "ready" and outsource:
				task_key_data['status'] = "ready_to_send"
			elif task_key_data['status'] == "work" and outsource:
				task_key_data['status'] = "work_to_outsorce"
			elif task_key_data['status'] == "work_to_outsorce" and not outsource:
				task_key_data['status'] = "work"
			elif task_key_data['status'] == "null" and (input_status in self.end_statuses) and outsource:
				task_key_data['status'] = "ready_to_send"
			elif task_key_data['status'] == "null" and (input_status in self.end_statuses) and (not outsource):
				task_key_data['status'] = "ready"
			# SET OUTPUT STATUS
			elif task_key_data['status'] in self.end_statuses:
				#print('w'*25, task_key_data['status'])
				self.edit_status_to_output(project_name, task_key_data['task_name'])
			
			if (current_task_data['status'] in self.end_statuses) and (task_key_data['status'] not in self.end_statuses):
				self.edit_status_to_output(project_name, task_key_data['task_name'], new_status = task_key_data['status'])
			
		# write task to db
		'''
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		c = conn.cursor()
		table = '\"' + asset_name + ':' + self.tasks_t + '\"'
		'''
		# edit db
		data_from_input_task = (False,)
		string = 'UPDATE ' +  table + ' SET '
		for key in task_key_data:
			if not key == 'task_name' or key == 'asset' or key == 'sctivity':
				if key == 'price':
					string = string + ' ' + key + ' = ' + str(task_key_data[key]) + ','
				else:
					if task_key_data[key] == None:
						string = string + ' ' + key + ' = null,'
					else:
						string = string + ' ' + key + ' = \"' + task_key_data[key] + '\",'
				'''
				elif key == 'status' and task_key_data['status'] == 'done':
					######
					continue
					self.edit_status_to_output(project_name, task_key_data['task_name'])
					string = string + ' ' + key + ' = \"' + task_key_data[key] + '\",'
				elif key == 'input':
					######
					continue
					data_from_input_task = self.read_task(project_name, task_key_data['input'], ('status',))
					string = string + ' ' + key + ' = \"' + task_key_data[key] + '\",'
				
				else:
					if task_key_data[key] == None:
						string = string + ' ' + key + ' = null,'
					else:
						string = string + ' ' + key + ' = \"' + task_key_data[key] + '\",'
				'''		
		######   == exchange key 'status'	from exchange input task
		'''
		if data_from_input_task[0]:
			if (data_from_input_task[1]['status'] == 'done') and (this_status == 'null'):
				string = string + ' status = \"ready\",'
			elif data_from_input_task[1]['status'] != 'done':
				string = string + ' status = \"null\",'
		'''
		######
		
		# -- >>
		string = string + ' WHERE task_name = \"' + task_key_data['task_name'] + '\"'
		string = string.replace(', WHERE', ' WHERE')
		#print(string)
		
		c.execute(string)
		conn.commit()
		conn.close()
		
		return(True, 'ok')
	
	def edit_status_to_output(self, project_name, task_name, new_status = None): # не обнаружено использование
		asset_name = task_name.split(':')[0]
		table = '\"' + asset_name + ':' + self.tasks_t + '\"'
		data = (task_name,)
		string = 'SELECT * FROM ' + table + ' WHERE input = ?'
		
		try:
			conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		except:
			return(False, 'studio.project.asset.task.edit_status_to_output() -> the database can not be read!')
				
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		c.execute(string, data)
		rows = c.fetchall()
		
		for row in rows:
			#print row['task_name']
			# get artist_status
			'''
			if int(artist().read_artist({'nik_name':row['artist']})[1][0]['outsource']):
				print '###########################################', row['artist']
			'''
			if not new_status:
				if row['status'] == 'null':
					if artist().read_artist({'nik_name':row['artist']})[1][0]['outsource'] == 1:
						string2 = 'UPDATE ' +  table + ' SET status = \"ready_to_send\" WHERE task_name = \"' + row['task_name'] + '\"'
					else:	
						string2 = 'UPDATE ' +  table + ' SET status = \"ready\" WHERE task_name = \"' + row['task_name'] + '\"'
					c.execute(string2)
			elif new_status not in self.end_statuses and row['status'] != 'close':
				string2 = 'UPDATE ' +  table + ' SET status = \"null\" WHERE task_name = \"' + row['task_name'] + '\"'
				c.execute(string2)
			
		conn.commit()
		conn.close()
		
		return True, 'ok'
	'''
	def read_task(self, project_name, task_name, keys):
		if keys == 'all':
			new_keys = []
			for key in self.tasks_keys:
				new_keys.append(key[0])
			keys = new_keys
			
		# other errors test
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# read tasks
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		asset_name = task_name.split(':')[0]
		table = '\"' + asset_name + ':' + self.tasks_t + '\"'
		string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
		
		try:
			c.execute(string)
			row = c.fetchone()
		except:
			conn.close()
			#return(False, ('can_not_read_asset', string))
			return(False, string)
		conn.close()
		
		if not row:
			return(False, 'not_task_name')
				
		data = {}
		for key in keys:
			data[key] = row[key]
			
		return(True, data)
	'''
		
	'''	
	def change_status_by_open_task(self, project_name, task_name, artist):
		self.edit_task(self, project_name, {'task_name': task_name, 'status': 'work'})
	'''
	
	
	# **************** Task NEW  METODS ******************
	
	# объект asset, передаваемый в task должен быть инициализирован.
	# list_of_tasks (str) - список задачь (словари по tasks_keys).
	def create_tasks_from_list(self, list_of_tasks): #v2
		asset_name = self.asset.name #asset_data['name']
		asset_id = self.asset.id #asset_data['id']
		#asset_path = self.asset.path #asset_data['path']
		
		# 1-создаём таблицу если нет
		# 2-читаем список имён существующих задач в exists_tasks
		# 3-пробегаем по списку list_of_tasks - если есть имена из exists_tasks - записываем их в conflicting_names
		# --3.1 если conflicting_names не пустой - то (return False, 'Matching names, look at the terminal!'); print(conflicting_names)
		# --3.2 если task_name или activity вообще остутсвуют - ошибка
		# 4-создаём задачи
		# --4.1 заполняем недостающие поля: asset_name, asset_id, outsource=0
		# --4.2 запись базы данных.
		
		table_name = '"%s:%s"' % ( asset_id, self.tasks_t)
		# 1
		bool_, return_data = database().create_table('project', self.asset.project, table_name, self.tasks_keys, table_root = self.tasks_db)
		if not bool_:
			return(bool_, return_data)
		# 2
		exists_tasks = []
		bool_, return_data = database().read('project', self.asset.project, table_name, self.tasks_keys, table_root=self.tasks_db)
		if not bool_:
			return(bool_, return_data)
		for task_ in return_data:
			exists_tasks.append(task_['task_name'])
		# 3
		conflicting_names = []
		for task_ in list_of_tasks:
			if task_.get('task_name') in exists_tasks:
				conflicting_names.append(task_['task_name'])
			# 3.2
			elif not task_.get('task_name'):
				print('#'*5, task_)
				return(False, 'in create_tasks_from_list() \n The task does not specify the "name"! Look the terminal')
			elif not task_.get('activity') and task_.get('task_type') != 'service':
				print('#'*5, task_)
				return(False, 'in create_tasks_from_list() \n The task does not specify the "activity"! Look the terminal')
		# 3.1
		if conflicting_names:
			print('#'*5, 'in create_tasks_from_list()')
			print('#'*5, 'Matching names: ', conflicting_names)
			return(False, 'in create_tasks_from_list() \n Matching names found! Look the terminal')
		
		# 4
		for task_keys in list_of_tasks:
			# 4.1
			if not task_keys.get('asset_name'):
				task_keys['asset_name'] = asset_name
			if not task_keys.get('asset_id'):
				task_keys['asset_id'] = asset_id
			task_keys['outsource'] = 0
			# 4.2
			bool_, return_data = database().insert('project', self.asset.project, table_name, self.tasks_keys, task_keys, table_root=self.tasks_db)
			if not bool_:
				return(bool_, return_data)
		'''
		# Other errors test
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		# Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + asset_id + ':' + self.tasks_t + '\"'
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
			
		except:
			string2 = "CREATE TABLE " + table + " ("
			for i,key in enumerate(self.tasks_keys):
				if i == 0:
					string2 = string2 + key[0] + ' ' + key[1]
				else:
					string2 = string2 + ', ' + key[0] + ' ' + key[1]
			string2 = string2 + ')'
			#print(string2)
			c.execute(string2)
			
		# Get exists_tasks
		exists_tasks = []
		str_ = 'select * from ' + table
		c.execute(str_)
		for row in c.fetchall():
			exists_tasks.append(row['task_name'])
		
		# Crete Tasks
		for task_keys in list_of_tasks:
			# ***************** tests *************
			try:
				if not task_keys['asset']:
					task_keys['asset'] = asset_name
				if not task_keys['asset_id']:
					task_keys['asset_id'] = asset_id
				if not task_keys['asset_path']:
					task_keys['asset_path'] = asset_path
			except:
				task_keys['asset'] = asset_name
				task_keys['asset_id'] = asset_id
				task_keys['asset_path'] = asset_path
				
			# task autsource
			task_keys['outsource'] = '0'
				
			# test task['Task_Name']
			try:
				if not task_keys['task_name']:
					conn.close()
					return(False, 'Not Task_Name!')
				else:
					if task_keys['task_name'] in exists_tasks:
						conn.close()
						return(False, (task_keys['task_name'] + ' already exists!'))
			except:
				conn.close()
				return(False, 'Not Task_Name!')
				
			# test task['Activity']
			if task_keys['task_type'] != 'service':
				try:
					if not task_keys['activity']:
						conn.close()
						return(False, 'activity!')
				except:
					conn.close()
					return(False, 'activity!')
			
			# ***************** tests end *************
			
			#
			string = "insert into " + table + " values"
			values = '('
			data = []
			for i, key in enumerate(self.tasks_keys):
				if i< (len(self.tasks_keys) - 1):
					values = values + '?, '
				else:
					values = values + '?'
				if key[0] in task_keys:
					data.append(task_keys[key[0]])
				else:
					if key[1] == 'real':
						data.append(0.0)
					elif key[1] == 'timestamp':
						data.append(None)
					else:
						data.append('')
						
			values = values + ')'
			data = tuple(data)
			string = string + values
			
			# add task
			c.execute(string, data)
			
		conn.commit()
		conn.close()
		'''
		return(True, 'ok')
	
	# объект asset, передаваемый в task должен быть инициализирован.
	# обязательные поля в task_data: activity, task_name, task_type, extension
	def add_single_task(self, task_data): # asset_id=False # v2 **
		pass
		# 1 - проверка обязательных полей.
		# 2 - назначение данных из ассета.
		# 3 - проверка статуса, на основе статуса входящей задачи.
		# 4 - внесение данной задачи в список output входящей задачи.
		# 5 - создание задачи. insert
		# 6 - внесение данной задачи в список output исходящей задачи.
		# 7 - смена статусов для output задачь.
		# (1) required fields
		for field in ['activity','task_name','task_type', 'extension']:
			if not task_data.get('%s' % field):
				return(False, 'Not specified the "%s"!' % field)
		# (2)
		# -- priority
		if not task_data.get('priority'):
			task_data['priority'] = self.asset.priority
		# -- outsource
		task_data['outsource'] = 0
		# -- output
		if task_data.get('output'):
			task_data['output'].append('%s:final' % task_data['asset'])
		else:
			task_data['output'] = ['%s:final' % task_data['asset']]
		# -- season
		task_data['season'] = self.asset.season
		# -- asset_id
		task_data['asset_id'] = self.asset.id
		# -- asset_type
		task_data['asset_type'] = self.asset.type
		
		# (3)
		
		# (4)
		
		# get table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
			
		# Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# ***************** get current task_status
		if not task_data['input']:
			task_data['status'] = 'ready'
		else:
			#get_input_string = 'SELECT * FROM ' + table + ' WHERE task_name = ?'
			get_input_string = 'SELECT * FROM ' + table
			#data = (task_data['input'],)
			#c.execute(get_input_string, data)
			c.execute(get_input_string)
			row = None
			#names = []
			for row_ in c.fetchall():
				#names.append(row_['task_name'])
				#print(row_)
				if task_data['task_name'] == row_['task_name']:
					conn.close()
					return(False, 'Thi Task_Name Already Exists!')
				if row_['task_name'] == task_data['input']:
					row = row_
			#print(row['status'])
			if row['status'] in self.end_statuses:
				task_data['status'] = 'ready'
			else:
				task_data['status'] = 'null'
				
			# ***************** add this task to output to input task
			input_task_data = dict(row)
			new_output_list = json.loads(input_task_data['output'])
			new_output_list.append(task_data['task_name'])
			input_task_data['output'] = json.dumps(new_output_list)
			#print(input_task_data['output'])
			
			new_output_string = string = 'UPDATE ' +  table + ' SET  output  = ? WHERE task_name = ?'
			data = (input_task_data['output'],input_task_data['task_name'])
			c.execute(new_output_string, data)
			
		# ***************** insert TASK_
		insert_string = "insert into " + table + " values"
		values = '('
		data = []
		for i, key in enumerate(self.tasks_keys):
			if i< (len(self.tasks_keys) - 1):
				values = values + '?, '
			else:
				values = values + '?'
			if key[0] in task_data:
				data.append(task_data[key[0]])
			else:
				if key[1] == 'real':
					data.append(0.0)
				elif key[1] == 'timestamp':
					data.append(None)
				else:
					data.append('')
			#print '>>> ', key[0], data[len(data) - 1]
					
		values = values + ')'
		data = tuple(data)
		insert_string = insert_string + values
		c.execute(insert_string, data)
		
		# ***************** To OUTPUTS 
		old_status = None
		output_row = None
		old_input = None
		if output_task_name:
			# get output_task_data
			get_output_string = 'SELECT * FROM ' + table + ' WHERE task_name = ?'
			data = (output_task_name,)
			c.execute(get_output_string, data)
			output_row = c.fetchone()
			old_status = output_row['status']
			old_input = output_row['input']
						
			# edit input,status to output_task
			string = 'UPDATE ' +  table + ' SET  input  = ?, status = ? WHERE task_name = ?'
			data = (task_data['task_name'],'null', output_task_name)
			c.execute(string, data)
			
			
			# edit output_list to old_input
			if old_input:
				old_input_row = None
				string = 'SELECT * FROM ' + table + ' WHERE task_name = ?'
				data = (old_input,)
				c.execute(string, data)
				old_input_row = c.fetchone()
				old_input_output = json.loads(old_input_row['output'])
				old_input_output.remove(output_task_name)
				# -- update
				string = 'UPDATE ' +  table + ' SET  output  = ? WHERE task_name = ?'
				data = (json.dumps(old_input_output), old_input)
				c.execute(string, data)
			
		conn.commit()
		conn.close()
			
		if old_input:
			# change status to output
			if (old_status != 'close') and (old_status in self.end_statuses):
				#print('change status')
				self.this_change_from_end(project_name, dict(output_row))
				
		return(True, 'Ok')
	
	# asset_id (str) - требуется если объект asset, передаваемый в task не инициализирован.
	# task_status (str) - фильтр по статусам задач.
	# artist (str) - фильтр по имени.
	def get_list(self, asset_id=False, task_status = False, artist = False): # v2
		if asset_id:
			table_name = '"%s:%s"' % ( asset_id, self.tasks_t)
		else:
			table_name = '"%s:%s"' % ( self.asset.id, self.tasks_t)
		if task_status or artist:
			where = {}
			if task_status and task_status in self.task_status:
				#where = {'status': task_status.lower()}
				where['status'] = task_status.lower()
			elif task_status and not task_status in self.task_status:
				return(False, 'Wrong status "%s"' % task_status)
			if artist:
				where['artist'] = artist
		else:
			where = False
		bool_, return_data = database().read('project', self.asset.project, table_name, self.tasks_keys, where=where, table_root=self.tasks_db)
		
		if not bool_:
			return(bool_, return_data)
		'''
		task_list = []
		
		# Other errors test
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		# Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + asset_id + ':' + self.tasks_t + '\"'
		try:
			if not task_status:
				str_ = 'select * from ' + table
			else:
				str_ = 'select * from  %s where status=\"%s\"' % (table, task_status.lower())
			c.execute(str_)
			task_list = c.fetchall()
		except Exception as e:
			conn.close()
			#return(False, 'Not Table!')
			return(False, e)
		
		conn.close()
		'''
		return(True, return_data)
		
	# self.asset.project - инициализирован
	# assets_data (dict) - dict{asset_name: {asset_data},...}
	# task_name_list (list) - список имён задач.
	def get_tasks_data_by_name_list(self, task_name_list, assets_data = False): # v2
		pass
		# (1) получение assets_data
		if not assets_data:
			result = self.asset.get_name_data_dict_by_all_types()
			if not result[0]:
				return(False, 'in task.get_tasks_data_by_name_list():\n%s' % result[1])
			else:
				assets_data = result[1]
		# (2) чтение БД
		level = 'project'
		read_ob = self.asset.project
		table_root = self.tasks_db
		keys = self.tasks_keys
		task_data_dict = {}
		#
		for task_name in task_name_list:
			#
			asset_id = assets_data[task_name.split(':')[0]]['id']
			table_name = '"%s:%s"' % (asset_id, self.tasks_t)
			where = {'task_name': task_name}
			#
			bool_, return_data = database().read(level, read_ob, table_name, keys, where=where, table_root=table_root)
			if not bool_:
				return(bool_, return_data)
			if return_data:
				task_data_dict[task_name] = return_data[0]
		'''
		try:
			# Connect to db
			conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			conn.close()
			return(False, 'in task().get_tasks_data_by_name_list not connect to db')
		
		task_data_dict = {}
		for task_name in task_name_list:
			# read task
			if not task_name:
				continue
			
			table = '\"' + assets_data[task_name.split(':')[0]]['id'] + ':' + self.tasks_t + '\"'
			
			try:
				string = 'SELECT * FROM ' + table + ' WHERE task_name = ?'
				c.execute(string, (task_name,))
				task_data_dict[task_name] = dict(c.fetchone())
			except:
				conn.close()
				return(False, ('in task().get_tasks_data_by_name_list - Not Table! task - ' + task_name))
				
		conn.close()
		'''
		return(True, task_data_dict)
	
	# self.asset.project - должен быть инициализирован
	# task_data (bool / dict) - необходим если task не инициализирован
	# new_activity (str)
	def change_activity(self, new_activity, task_data=False): # v2
		pass
		# (1) исходные данные
		if task_data:
			asset_id = task_data['asset_id']
			task_name = task_data['task_name']
		else:
			asset_id = self.asset_id
			task_name = self.task_name
		# (2) проверка валидации new_activity
		if not new_activity in self.asset.ACTIVITY_FOLDER[self.asset.type]:
			return(False, 'Incorrect activity: "%s"' % new_activity)
		# (3) запись БД
		table_name = '"%s:%s"' % (asset_id, self.tasks_t)
		read_ob = self.asset.project
		update_data = {'activity':new_activity}
		where = {'task_name':task_name}
		#
		bool_, return_data = database().update('project', read_ob, table_name, self.tasks_keys, update_data, where, table_root=self.tasks_db)
		# запись нового активити в поле объекта, если он инициализирован
		if bool_ and not task_data:
			self.activity = new_activity
		return(bool_, return_data)
		'''
		# Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		try:
			str_ = 'select * from ' + table
		except:
			conn.close()
			return(False, 'Not Table!')
			
		# edit db
		string = 'UPDATE ' +  table + ' SET  \"activity\"  = ? WHERE \"task_name\" = \"' + task_data['task_name'] + '\"'
				
		data = (new_activity,)
		
		c.execute(string, data)
		conn.commit()
		conn.close()
		return(True, 'Ok!')
		'''
		
	def change_workroom(self, project_name, task_data, new_workroom): # не будет вообще - надо менять тип задачи в changes_without_a_change_of_status()
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		# get new_workroom_id
		copy = workroom()
		result = copy.get_id_by_name(new_workroom)
		if not result[0]:
			return(False, result[1])
		new_workroom_id = result[1]
			
		# Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		try:
			str_ = 'select * from ' + table
		except:
			conn.close()
			return(False, 'Not Table!')
			
		# edit db
		string = 'UPDATE ' +  table + ' SET  \"workroom\"  = ? WHERE \"task_name\" = \"' + task_data['task_name'] + '\"'
				
		data = (new_workroom_id,)
		
		c.execute(string, data)
		conn.commit()
		conn.close()
		
		return(True, new_workroom_id)
	
	# self.asset.project - должен быть инициализирован
	# task_data (bool / dict) - необходим если task не инициализирован
	# new_price (float)
	def change_price(self, new_price, task_data=False): # v2
		if task_data:
			asset_id = task_data['asset_id']
			task_name = task_data['task_name']
		else:
			asset_id = self.asset_id
			task_name = self.task_name
		table_name = '"%s:%s"' % (asset_id, self.tasks_t)
		read_ob = self.asset.project
		update_data = {'price': new_price}
		where = {'task_name':task_name}
		#
		bool_, return_data = database().update('project', read_ob, table_name, self.tasks_keys, update_data, where, table_root=self.tasks_db)
		# запись новой цены в поле объекта, если он инициализирован
		if bool_ and not task_data:
			self.price = new_price
		return(bool_, return_data)
		
	# key (str) - ключ для которого идёт замена
	# new_data (по типу ключа) - данные на замену
	# task_data (bool/dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	def changes_without_a_change_of_status(self, key, new_data, task_data=False): # v2
		changes_keys = [
		'activity',
		'task_type',
		'season',
		'price',
		'tz',
		#'workroom',
		'extension'
		]
		if not key in changes_keys:
			return(False, 'This key invalid! You can only edit keys from this list: %s' % json.dumps(changes_keys))
		
		if task_data:
			asset_id = task_data['asset_id']
			task_name = task_data['task_name']
		else:
			asset_id = self.asset_id
			task_name = self.task_name
		read_ob = self.asset.project
		table_name = '"%s:%s"' % (asset_id, self.tasks_t)
		update_data = {key: new_data}
		where = {'task_name': task_name}
		bool_, r_data = database().update('project', read_ob, table_name, self.tasks_keys, update_data, where, table_root=self.tasks_db)
		if not bool_:
			return(bool_, r_data)
		# запись новых данных в поле объекта, если он инициализирован
		if not task_data:
			if isinstance(new_data, str):
				exec('self.%s = "%s"' % (key, new_data))
			else:
				exec('self.%s = %s' % (key, new_data))
		return(True, 'Ok!')
		
	# add_readers_list (list) - список никнеймов проверяющих (читателей)
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	def add_readers(self, add_readers_list, task_data=False): # v2 *** тестилось без смены статуса.
		pass
		# ? - проверять ли актуальность списка читателей.
		# 1 - получение task_data
		# 2 - чтение словаря 'readers' и определение change_status
		# 3 - определение update_data
		# 4 - если задача инициализирована - редактирование данного объекта задачи.
		# 5 - перезапись задачи
		# 6 - смена исходящих статусов если change_status=True
		
		#
		if not isinstance(add_readers_list, list) and not isinstance(add_readers_list, tuple):
			return(False, '###\nin task.add_readers()\nInvalid type of "add_readers_list": "%s"' % add_readers_list.__class__.__name__)
		
		# (1)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.%s' % (key, key))
	
		change_status = False
		readers_dict = {}
		
		# (2)
		read_ob = self.asset.project
		table_name = '"%s:%s"' % (task_data['asset_id'], self.tasks_t)
		keys = self.tasks_keys
		where = {'task_name': task_data['task_name']}
		bool_, r_data = database().read('project', read_ob, table_name, keys, where=where, table_root=self.tasks_db)
		if not bool_:
			return(bool_, r_data)
		elif not r_data:
			return(False, 'This Task (%s) Not Found' % task_data['task_name'])
		else:
			readers_dict = r_data[0].get('readers')
			if r_data[0].get('status') == 'done':
				change_status = True
		
		'''
		try:
			# Connect to db
			conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return(False, ('in task().add_readers Not Connect Table - path = ' + self.tasks_path))
			
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		string = 'select * from ' + table
		try:
			c.execute(string)
			# -- get old readers dict
			for row in c.fetchall():
				if row['task_name'] == task_data['task_name']:
					try:
						if json.loads(row['readers']):
							readers_dict = json.loads(row['readers'])
					except:
						pass
					if row['status'] == 'done':
						change_status = True
					break
		except:
			conn.close()
			return(False, ('in task().add_readers Not Table! - ' + table))
		'''
		for artist_name in add_readers_list:
			readers_dict[artist_name] = 0
			
		# (3)
		new_status = False
		if change_status:
			new_status = 'checking'
			update_data = {'status': new_status, 'readers': readers_dict}
			#string = 'UPDATE ' +  table + ' SET  status  = ?, readers  = ? WHERE task_name = ?'
			#data = ('checking', json.dumps(readers_dict), task_data['task_name'])
		else:
			update_data = {'readers': readers_dict}
			#string = 'UPDATE ' +  table + ' SET  readers  = ? WHERE task_name = ?'
			#data = (json.dumps(readers_dict), task_data['task_name'])
			
		# (4)
		if self.task_name == task_data['task_name']:
			self.readers = readers_dict
			if new_status:
				self.status = new_status
		
		# (5)
		bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
		if not bool_:
			return(bool_, r_data)
		
		# (6) change output statuses
		if change_status:
			bool_, r_data = self.this_change_from_end(task_data)
			if not bool_:
				return(bool_, r_data)
		
		return(True, readers_dict, change_status)
	
	# nik_name (str) - никнейм артиста
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	def make_first_reader(self, nik_name, task_data=False): # v2
		pass
		# ? - проверять ли актуальность читателя.
		# 1 - получение task_data
		# 2 - чтение словаря 'readers' и определение change_status
		# 3 - редактирование задачи в случае если она инициализирована.
		# 4 - перезапись задачи
		
		#
		readers_dict = {}
		# (1)
		if task_data:
			asset_id = task_data['asset_id']
			task_name = task_data['task_name']
		else:
			asset_id = self.asset_id
			task_name = self.task_name
		
		# (2)
		read_ob = self.asset.project
		table_name = '"%s:%s"' % (asset_id, self.tasks_t)
		keys = self.tasks_keys
		where = {'task_name': task_name}
		bool_, r_data = database().read('project', read_ob, table_name, keys, where=where, table_root=self.tasks_db)
		if not bool_:
			return(bool_, r_data)
		elif not r_data:
			return(False, 'This Task (%s) Not Found' % task_name)
		else:
			readers_dict = r_data[0].get('readers')
		'''
		try:
			# Connect to db
			conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return(False, ('in task().add_readers Not Connect Table - path = ' + self.tasks_path))
			
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		string = 'select * from ' + table
		try:
			c.execute(string)
			# -- get old readers dict
			for row in c.fetchall():
				if row['task_name'] == task_data['task_name']:
					try:
						readers_dict = json.loads(row['readers'])
					except:
						pass
					break
		except:
			conn.close()
			return(False, ('in task().add_readers Not Table! - ' + table))
		'''
		readers_dict['first_reader'] = nik_name
		
		# (3)
		if self.task_name == task_name:
			self.readers = readers_dict
			
		# (4)
		update_data = {'readers': readers_dict}
		bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
		if not bool_:
			return(bool_, r_data)
		'''
		# edit .db
		string = 'UPDATE ' +  table + ' SET  readers  = ? WHERE task_name = ?'
		data = (json.dumps(readers_dict), task_data['task_name'])
		
		c.execute(string, data)
		conn.commit()
		conn.close()
		'''		
		return(True, readers_dict)
	
	# надо ли удалять first_reader - если его ник нейм в списке на удаление ???????????????????
	# remove_readers_list (list) - список никнеймов удаляемых из списка читателей
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	def remove_readers(self, remove_readers_list, task_data=False): # v2
		pass
		# 1 - получение task_data
		# 2 - чтение БД - readers_dict
		# 3 - очистка списка читателей
		# 4 - определение изменения статуса
		# 5 - запись изменения readers в БД
		# 6 - в случае если данная задача инициализирована - внесение в неё изменений.
		# 7 - в случае изменения статуса - изменение статуса исходящих задачь.

		change_status = False
		readers_dict = {}
		
		# (1)
		if not task_data:
			task_data = {}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.%s' % (key, key))
		# (2)
		read_ob = self.asset.project
		table_name = '"%s:%s"' % (task_data['asset_id'], self.tasks_t)
		keys = self.tasks_keys
		where = {'task_name': task_data['task_name']}
		bool_, r_data = database().read('project', read_ob, table_name, keys, where=where, table_root=self.tasks_db)
		if not bool_:
			return(bool_, r_data)
		elif not r_data:
			return(False, 'This Task (%s) Not Found' % task_name)
		else:
			readers_dict = r_data[0].get('readers')
		'''
		try:
			# Connect to db
			conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return(False, ('in task().remove_readers Not Connect Table - path = ' + self.tasks_path))
					
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		string = 'select * from ' + table
		try:
			c.execute(string)
			# -- get old readers dict
			for row in c.fetchall():
				if row['task_name'] == task_data['task_name']:
					try:
						readers_dict = json.loads(row['readers'])
					except:
						pass
					break
		except:
			conn.close()
			return(False, ('in task().remove_readers Not Table! - ' + table))
		'''
		
		# (3) remove artists
		for artist_name in remove_readers_list:
			try:
				del readers_dict[artist_name]
			except:
				pass
		
		# (4) get change status
		if task_data['status'] == 'checking':
			change_status = True
		if not readers_dict:
			change_status = False
		else:
			for artist_name in readers_dict:
				if readers_dict[artist_name] == 0:
					change_status = False
					break
		
		# (5) edit db
		new_status = False
		if change_status:
			new_status = 'done'
			update_data = {'status': new_status, 'readers': readers_dict}
			#string = 'UPDATE ' +  table + ' SET  status = ?, readers  = ? WHERE task_name = ?'
			#data = ('done', json.dumps(readers_dict), task_data['task_name'])
		else:
			update_data = {'readers': readers_dict}
			#string = 'UPDATE ' +  table + ' SET  readers  = ? WHERE task_name = ?'
			#data = (json.dumps(readers_dict), task_data['task_name'])
		bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
		if not bool_:
			return(bool_, r_data)
		'''
		c.execute(string, data)
		conn.commit()
		conn.close()
		'''
		
		# (6)
		if self.task_name == task_data['task_name']:
			self.readers = readers_dict
			if new_status:
				self.status = new_status
		
		# (7) change output statuses
		if change_status:
			result = self.this_change_to_end(task_data)
			if not result[0]:
				return(False, result[1])
		
		return(True, readers_dict, change_status)
		
	# new_artist (str) - nik_name
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	def change_artist(self, new_artist, task_data=False): # v2  !!!!! возможно надо рассмотреть варианты когда меняется артист в завершённых статусах задачь.
		pass
		# 1 - получение task_data.
		# 2 - чтение нового артиста и определение аутсорсер он или нет.
		# 3 - чтение outsource - изменяемой задачи.
		# 4 - определение нового статуса задачи
		# 5 - внесение изменений в БД
		# 6 - если task инициализирована - внеси в неё изменения.
		
		# (1)
		if not task_data:
			task_data = {}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.%s' % (key, key))
        
		print('### task_data["outsource"].type = %s, value = %s' % (task_data["outsource"].__class__.__name__, str(task_data["outsource"])))
		
		# --------------- edit Status ------------
		new_status = None
				
		# (2) get artist outsource
		artist_outsource = False
		if new_artist:
			result = artist().read_artist({'nik_name':new_artist})
			if not result[0]:
				return(False, result[1])
			if result[1][0].get('outsource'):
				artist_outsource = bool(result[1][0]['outsource'])
		else:
			new_artist = ''
		print('*** artist_outsource: %s' % str(artist_outsource))
			
		# (3) get task_outsource
		task_outsource = task_data['outsource']
		'''
		task_outsource = False
		if task_data['outsource']:
			task_outsource = bool(task_data['outsource'])
		'''
		print('*** task_outsource: %s' % str(task_outsource))
		
		# (4) get new status
		if task_data['status'] in self.VARIABLE_STATUSES:
			print('****** in variable')
			if not new_artist :
				new_status = 'ready'
			elif (not task_data['artist']) or (not task_outsource):
				#print('****** start not outsource')
				if artist_outsource:
					new_status = self.CHANGE_BY_OUTSOURCE_STATUSES['to_outsource'][task_data['status']]
				else:
					pass
					#print('****** artist not outsource')
			elif task_outsource and (not artist_outsource):
				#print('****** to studio 1')
				new_status = self.CHANGE_BY_OUTSOURCE_STATUSES['to_studio'][task_data['status']]
			else:
				#print('****** start outsource')
				if not artist_outsource:
					new_status = self.CHANGE_BY_OUTSOURCE_STATUSES['to_studio'][task_data['status']]
				else:
					pass
					#print('****** artist outsource')
		else:
			pass
			#print('****** not in variable')
		print('*** new_status: %s' % str(new_status))
			
		# (5)
		read_ob = self.asset.project
		table_name = '"%s:%s"' % (task_data['asset_id'], self.tasks_t)
		keys = self.tasks_keys
		where = {'task_name': task_data['task_name']}
		if new_status:
			update_data = {'artist': new_artist, 'outsource': int(artist_outsource), 'status':new_status}
		else:
			update_data = {'artist': new_artist, 'outsource': int(artist_outsource)}
		bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
		if not bool_:
			return(bool_, r_data)
		
		'''
		# ------------- edit DB -----------------
		# Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		try:
			str_ = 'select * from ' + table
		except:
			conn.close()
			return(False, 'Not Table!')
			
		# edit db
		if new_status:
			string = 'UPDATE ' +  table + ' SET  \"artist\"  = ?, \"outsource\"  = ?, \"status\"  = ?  WHERE \"task_name\" = \"' + task_data['task_name'] + '\"'
			data = (new_artist, str(int(artist_outsource)), new_status)
		else:
			string = 'UPDATE ' +  table + ' SET  \"artist\"  = ?, \"outsource\"  = ?  WHERE \"task_name\" = \"' + task_data['task_name'] + '\"'
			data = (new_artist, str(int(artist_outsource)))
		
		c.execute(string, data)
		conn.commit()
		conn.close()
		'''
		# (6)
		if self.task_name == task_data['task_name']:
			if new_status:
				self.status = new_status
				self.outsource = int(artist_outsource)
				self.artist = new_artist
			else:
				self.outsource = int(artist_outsource)
				self.artist = new_artist
		
		return(True, (new_status, int(artist_outsource)))
		
	# new_input (str) - имя новой входящей задачи
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	def change_input(self, new_input, task_data=False): # v2 *** тестилось без смены статуса.
		pass
		# 1 - получение task_data, task_outsource, old_input_task_data, new_input_task_data, new_status, list_output_old, list_output_new
		# 2 - перезапись БД
		# 3 - если task инициализирована - внеси в неё изменения.
		# 4 - подготовка return_data
		
		# (1)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.%s' % (key, key))
		
		#
		new_status = False
		# get task_outsource
		task_outsource = False
		if task_data['outsource']:
			task_outsource = bool(task_data['outsource'])
		
		# get old inputs tasks data
		old_input_task_data = None
		if task_data['input']:
			result = self.read_task(task_data['input'], task_data['asset_id'])
			if not result[0]:
				return(False, result[1])
			old_input_task_data = result[1]
		
		# get new inputs task data
		new_input_task_data = None
		if new_input:
			result = self.read_task(new_input, task_data['asset_id'])
			if not result[0]:
				return(False, result[1])
			new_input_task_data = result[1]
			new_input_status = new_input_task_data['status']
		
		# ???
		# change status
		new_status = self.from_input_status(task_data, new_input_task_data)
		if task_data['status'] in self.end_statuses and not new_status in self.end_statuses:
			self.this_change_from_end(task_data)
				
		# change outputs
		# -- in old input
		list_output_old = None
		if old_input_task_data:
			list_output_old = old_input_task_data['output']
			if task_data['task_name'] in list_output_old:
				list_output_old.remove(task_data['task_name'])
			
		# -- in new input
		list_output_new = None
		if new_input_task_data:
			if not new_input_task_data['output']:
				list_output_new = []
			else:
				list_output_new = new_input_task_data['output']
			list_output_new.append(task_data['task_name'])
		
		# (2)
		read_ob = self.asset.project
		table_name = '"%s:%s"' % (task_data['asset_id'], self.tasks_t)
		keys = self.tasks_keys
		# edit old_output
		if list_output_old:
			where = {'task_name': old_input_task_data['task_name']}
			update_data = {'output': list_output_old}
			bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
			if not bool_:
				return(bool_, r_data)
		if list_output_new:
			# edit new_output
			where = {'task_name': new_input_task_data['task_name']}
			update_data = {'output': list_output_new}
			bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
			if not bool_:
				return(bool_, r_data)
			# edit new_input
			where = {'task_name': task_data['task_name']}
			update_data = {'input': new_input_task_data['task_name']}
			bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
			if not bool_:
				return(bool_, r_data)
		else:
			where = {'task_name': task_data['task_name']}
			update_data = {'input': ''}
			bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
			if not bool_:
				return(bool_, r_data)
		# edit status
		if new_status:
			where = {'task_name': task_data['task_name']}
			update_data = {'status': new_status}
			bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
			if not bool_:
				return(bool_, r_data)
		
		'''
		# edit db
		# -- Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
		except:
			conn.close()
			return(False, 'Not Table!')
			
		# edit old_output
		string_old, data_old = None,None
		if list_output_old:
			string_old = 'UPDATE ' +  table + ' SET  \"output\"  = ? WHERE \"task_name\" = \"' + old_input_task_data['task_name'] + '\"'
			data_old = (list_output_old,)
			c.execute(string_old, data_old)
		
		# edit new_output
		string_new, data_new = None,None
		if list_output_new:
			# output
			string_new = 'UPDATE ' +  table + ' SET  \"output\"  = ? WHERE \"task_name\" = \"' + new_input_task_data['task_name'] + '\"'
			data_new = (list_output_new,)
			c.execute(string_new, data_new)
			# input
			string = 'UPDATE ' +  table + ' SET  \"input\"  = ? WHERE \"task_name\" = \"' + task_data['task_name'] + '\"'
			data = (new_input_task_data['task_name'],)
			c.execute(string, data)
		else:
			string = 'UPDATE ' +  table + ' SET  \"input\"  = ? WHERE \"task_name\" = \"' + task_data['task_name'] + '\"'
			data = ('',)
			c.execute(string, data)
			
		
		# edit status
		if new_status:
			string = 'UPDATE ' +  table + ' SET  \"status\"  = ? WHERE \"task_name\" = \"' + task_data['task_name'] + '\"'
			data = (new_status,)
			c.execute(string, data)
		
		conn.commit()
		conn.close()
		'''
		
		# (3)
		if self.task_name == task_data['task_name']:
			if list_output_new:
				self.input = new_input_task_data['task_name']
			else:
				self.input = ''
			if new_status:
				self.status = new_status
		
		# (4)
		if list_output_old:
			old_input_task_data['output'] = list_output_old
		if list_output_new:
			new_input_task_data['output'] = list_output_new
		
		return(True, (new_status, old_input_task_data, new_input_task_data))
		
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	def accept_task(self, task_data=False): # v2
		pass
		# 1 - получение task_data,
		# 2 - паблиш Хуки
		# 3 - перезапись БД задачи
		# 4 - изменение статусов исходящих задачь
		# 5 - внесение изменений в объект если он инициализирован
		
		# (1)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.%s' % (key, key))
			
		# (2) publish
		#result = lineyka_publish.publish().publish(project_name, task_data)
		result = self.publish.publish(task_data)
		if not result[0]:
			return(False, result[1])
		
		# (3)
		read_ob = self.asset.project
		table_name = '"%s:%s"' % (task_data['asset_id'], self.tasks_t)
		keys = self.tasks_keys
		update_data = {'readers':{}, 'status':'done'}
		where = {'task_name': task_data['task_name']}
		bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
		if not bool_:
			return(bool_, r_data)
		
		'''	
		# -- Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		#try:
		# remove readers
		readers = json.dumps({})
		
		string = 'UPDATE ' +  table + ' SET  readers = ?, status  = ? WHERE task_name = ?'
		data = (readers, 'done', task_data['task_name'])
		c.execute(string, data)
		conn.commit()
		conn.close()
		'''
		
		# (4) change output statuses
		result = self.this_change_to_end(task_data)
		if not result[0]:
			return(False, result[1])
		
		# (5)
		if self.task_name == task_data['task_name']:
			self.status = 'done'
			
		return(True, 'Ok!')
	
	# приём задачи текущим ридером
	# current_artist (artist) - экземпляр класса артист, должен быть инициализирован - artist.get_user()
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	def readers_accept_task(self, current_artist, task_data=False): # v2
		pass
		# 0 - проверка, чтобы current_artist был экземпляром класса artist
		# 1 - получение task_data,
		# 2 - изменения в readers, определение change_status
		# 3 - паблиш Хуки
		# 4 - запись изменений задачи в БД
		# 5 - изменение статусов исходящих задачь
		# 6 - внесение изменений в объект если он инициализирован
		
		# (0)
		if not isinstance(current_artist, artist):
			return(False, 'in task.readers_accept_task() - "current_artist" must be an instance of "artist" class, and not "%s"' % current_artist.__class__.__name__)
		
		# (1)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.%s' % (key, key))
			
		# (2)
		change_status = True
		readers = task_data['readers']
		if current_artist.nik_name in readers:
			readers[current_artist.nik_name] = 1
		else:
			return(False, 'Current user is not a reader of this task!')
		#
		for key in readers:
			if key == 'first_reader':
				continue
			elif readers[key] == 0:
				change_status = False
				break
			
		# (3) -- publish
		if change_status:
			result = self.publish.publish(task_data)
			if not result[0]:
				return(False, result[1])
			
		# (4)
		read_ob = self.asset.project
		table_name = '"%s:%s"' % (task_data['asset_id'], self.tasks_t)
		keys = self.tasks_keys
		if change_status:
			update_data = {'readers':readers, 'status':'done'}
		else:
			update_data = {'readers':readers}
		where = {'task_name': task_data['task_name']}
		bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
		if not bool_:
			return(bool_, r_data)
		
		'''
		# -- Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		change_status = True
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		
		
		# read .db
		string = 'SELECT * FROM ' +  table + ' WHERE task_name = ?'
		data = (task_data['task_name'],)
		c.execute(string, data)
		task_data = dict(c.fetchone())
		readers = json.loads(task_data['readers'])
		if nik_name in readers:
			readers[nik_name] = 1
		task_data['readers'] = json.dumps(readers)

		# get change_status
		for key in readers:
			if key == 'first_reader':
				continue
			elif readers[key] == 0:
				change_status = False
				break

		# update readers .db
		if change_status:
			string = 'UPDATE ' +  table + ' SET status  = ?, readers  = ? WHERE task_name = ?'
			data = ('done', task_data['readers'], task_data['task_name'])
			c.execute(string, data)
		else:
			string = 'UPDATE ' +  table + ' SET  readers  = ? WHERE task_name = ?'
			data = (task_data['readers'], task_data['task_name'])
			c.execute(string, data)
			
		conn.commit()
		conn.close()
		'''
		
		# (5) change output statuses
		if change_status:
			# -- change output statuses
			result = self.this_change_to_end(task_data)
			if not result[0]:
				return(False, result[1])
		
		# (6)
		if self.task_name == task_data['task_name']:
			if change_status:
				self.status = 'done'
				#self.readers = readers
		
		return(True, 'Ok')
	
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	def close_task(self, task_data=False): # v2
		pass
		# 1 - получение task_data
		# 2 - запись изменений задачи в БД
		# 3 - изменение статусов исходящих задачь
		# 4 - внесение изменений в объект если он инициализирован
		
		# (1)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.%s' % (key, key))
				
		# (2)
		read_ob = self.asset.project
		table_name = '"%s:%s"' % (task_data['asset_id'], self.tasks_t)
		keys = self.tasks_keys
		update_data = {'status':'close'}
		where = {'task_name': task_data['task_name']}
		bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
		if not bool_:
			return(bool_, r_data)
		'''	
		# -- Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		try:
			string = 'UPDATE ' +  table + ' SET  status  = ? WHERE task_name = ?'
			data = ('close', task_data['task_name'])
			c.execute(string, data)
			conn.commit()
			conn.close()
						
		except:
			conn.close()
			return(False, 'in accept_task - Not Edit Table!')
		'''
		
		# (3) change output statuses
		result = self.this_change_to_end(task_data)
		if not result[0]:
			return(False, result[1])
		
		# (4)
		if self.task_name == task_data['task_name']:
			self.status = 'close'
			
		return(True, 'Ok!')
	
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	def rework_task(self, task_data=False, current_user = False): # v2 ** продолжение возможно только после редактирования chat().read_the_chat()
		pass
		# 1 - получение task_data
		
		
		# (1)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.%s' % (key, key))
		
		# get exists chat
		if current_user:
			exists_chat = False
			result = chat().read_the_chat(project_name, task_data['task_name'])
			if not result[0]:
				return(False, 'not chat!')
			
			delta = datetime.timedelta(minutes = 45)
			now_time = datetime.datetime.now()
			for topic in result[1]:
				if topic['author'] == current_user:
					if (now_time - topic['date_time']) <= delta:
						exists_chat = True
						break
						
			if not exists_chat:
				return(False, 'not chat!')
			
		# -- Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		
		#try:
			
		# read .db
		string = 'SELECT * FROM ' +  table + ' WHERE task_name = ?'
		data = (task_data['task_name'],)
		c.execute(string, data)
		task_data = dict(c.fetchone())
		if task_data['readers']:
			readers = json.loads(task_data['readers'])
			for nik_name in readers:
				if nik_name == 'first_reader':
					continue
				readers[nik_name] = 0
			task_data['readers'] = json.dumps(readers)
		
		string = 'UPDATE ' +  table + ' SET  readers = ?, status  = ? WHERE task_name = ?'
		data = (task_data['readers'], 'recast', task_data['task_name'])
		c.execute(string, data)
		
		conn.commit()
		conn.close()
		
		'''				
		except:
			conn.close()
			return(False, 'in rework_task - Not Edit Table!')
		'''
			
		return(True, 'Ok!')
	
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	def return_a_job_task(self, task_data=False): # v2
		pass
		# 1 - получение task_data,
		# 2 - чтение входящей задачи
		# 3 - получение статуса на основе статуса входящей задачи.
		# 4 - внесение изменений в БД
		# 5 - внесение изменений в объект если он инициализирован
		# 6 - изменение статусов исходящих задач
		
		# (1)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.%s' % (key, key))
	
		# (2)
		input_task_name = task_data['input']
		input_task_data = False
		if input_task_name:
			result = self.read_task(input_task_name, task_data['asset_id'])
			if not result[0]:
				return(False, result[1])
			input_task_data = result[1]
		
		# (3)
		task_data['status'] = 'null'
		new_status = self.from_input_status(task_data, input_task_data)
		
		# (4)
		read_ob = self.asset.project
		table_name = '"%s:%s"' % (task_data['asset_id'], self.tasks_t)
		keys = self.tasks_keys
		update_data = {'readers':{}, 'status':new_status}
		where = {'task_name': task_data['task_name']}
		bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
		if not bool_:
			return(bool_, r_data)
		
		'''
		# -- Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		
		try:
			string = 'SELECT * FROM ' + table + 'WHERE task_name = ?'
			data = (task_data['task_name'],)
			c.execute(string, data)
			row = dict(c.fetchone())
			readers = {}
			try:
				readers = json.loads(row['readers'])
			except:
				pass
			for key in readers:
				if key == 'first_reader':
					continue
				readers[key] = 0
			row['readers'] = json.dumps(readers)
			
			string = 'UPDATE ' +  table + ' SET  readers = ?, status  = ? WHERE task_name = ?'
			data = (row['readers'], new_status, task_data['task_name'])
			c.execute(string, data)
			conn.commit()
			conn.close()
						
		except:
			conn.close()
			return(False, 'in return_a_job_task - Not Edit Table!')
		'''
		
		# (5)
		if self.task_name == task_data['task_name']:
			self.status = new_status
		
		# (6) change output statuses
		result = self.this_change_from_end(task_data)
		if not result[0]:
			return(False, result[1])
		else:
			return(True, new_status)
			
	# change_statuses (list) - [(task_data, new_status), ...]
	# тупо смена статусов в пределах рабочих, что не приводит к смене статусов исходящих задач.
	# task инициализирован
	def change_work_statuses(self, change_statuses): # v2
		table_name = '"%s:%s"' % (self.asset.id, self.tasks_t)
		return_data_ = {}
		for data in change_statuses:
			task_data = data[0]
			new_status = data[1]
			update_data = {'status': new_status}
			where = {'task_name': task_data['task_name']}
			bool_, return_data = database().update('project', self.asset.project, table_name, self.tasks_keys, update_data, where, table_root=self.tasks_db)
			if not bool_:
				return(False, return_data)
			return_data_[task_data['task_name']] = new_status
			
		return(True, return_data_)
		'''
		# -- Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		return_data = {}
		
		for data in change_statuses:
			task_data = data[0]
			new_status = data[1]
			# Exists table
			table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
			try:
				string = 'UPDATE ' +  table + ' SET  status  = ? WHERE task_name = ?'
				data = (new_status, task_data['task_name'])
				c.execute(string, data)
				return_data[task_data['task_name']] = new_status
			except:
				conn.close()
				return(False, 'in change_work_statuses - Not Edit Table!')
				
		conn.commit()
		conn.close()
		
		return(True, return_data)
		'''
	
	# если объект asset, передаваемый в task не инициализирован, то надо указать asset_id.
	# возврат словаря задачи по имени задачи.
	def read_task(self, task_name, asset_id=False): # v2
		if not asset_id:
			asset_id = self.asset.id
		table_name = '"%s:%s"' % (asset_id, self.tasks_t)
		where={'task_name': task_name}
		# read
		bool_, return_data = database().read('project', self.asset.project, table_name, self.tasks_keys , where=where, table_root=self.tasks_db)
		return(bool_, return_data[0])
		'''
		if keys == 'all':
			new_keys = []
			for key in self.tasks_keys:
				new_keys.append(key[0])
			keys = new_keys
			
		# other errors test
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# read tasks
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		table = '\"' + asset_id + ':' + self.tasks_t + '\"'
		string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
		
		try:
			c.execute(string)
			row = c.fetchone()
		except:
			conn.close()
			#return(False, ('can_not_read_asset', string))
			return(False, string)
		conn.close()
		
		if not row:
			return(False, 'not_task_name')
				
		data = {}
		for key in keys:
			try:
				data[key] = row[key]
			except:
				pass
				print(('not key: ' + key + ' in ' + row['task_name']))
		return(True, data)
		'''
	
	# self.asset.project - должен быть инициализирован
	# nik_name (str) -
	def get_task_list_of_artist(self, nik_name): # v2
		pass
		# 1 - получаем список ассетов asset_list
		# 2 - для каждого ассета(со статусом "active") получаем список задач данного исполнителя. заполняем список task_list.
		# 3 - бежим по task_list - и достаём входящую задачу.
		#	-- заполняется словарь task_input_task_list = {task_name: {'task':{data}, 'input':{data}}, ... }
		# 4 - возвращаемое значение (True, task_input_task_list, asset_list)
		
		# (1)
		result = self.asset.get_name_data_dict_by_all_types()
		if not result[0]:
			return(False, result[1])
		asset_list = result[1]
		
		# (2)
		task_list = []
		task_input_task_list = {}
		for asset_name in asset_list:
			if asset_list[asset_name]['status']== 'active':
				asset_id = asset_list[asset_name]['id']
				bool_, return_data = self.get_list(asset_id=asset_id, artist = nik_name)
				if not bool_:
					return(bool_, return_data)
				task_list = task_list + return_data
		# (3)
		for task in task_list:
			task_input_task_list[task['task_name']] = {'task' : task}
			if task['input']:
				input_asset_id = asset_list[task['input'].split(':')[0]]['id']
				bool_, return_data = self.read_task(task['input'], asset_id=input_asset_id)
				if not bool_:
					return(bool_, return_data)
				task_input_task_list[task['task_name']]['input'] = return_data
				
		'''
		# read tasks
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		task_list = []
		task_input_task_list = {}
		
		for asset_name in asset_list:
			if asset_list[asset_name]['status']== 'active':
				asset_id = asset_list[asset_name]['id']
				table = '\"' + asset_id + ':' + self.tasks_t + '\"'
				string = 'select * from ' + table + ' WHERE artist = ?'
				data = (nik_name,)
				try:
					c.execute(string, data)
					rows = c.fetchall()
					task_list = task_list + rows
				except:
					conn.close()
					return(False, string)
					
		for task in task_list:
			row = {}
			if task['input']:
				input_asset_id = asset_list[task['input'].split(':')[0]]['id']
				table = '\"' + input_asset_id + ':' + self.tasks_t + '\"'
				string = 'select * from ' + table + ' WHERE task_name = ?'
				data = (task['input'],)
				
				try:
					c.execute(string, data)
					row = c.fetchone()
					#task_input_task_list[task['task_name']] = {'task' : dict(task), 'input':dict(row)}
				except:
					conn.close()
					return(False, string)
			
			try:
				task_input_task_list[task['task_name']] = {'task' : dict(task), 'input':dict(row)}
			except:
				print('*'*250)
				print(task['task_name'], task['input'])
				print(row)
				continue
		conn.close()
		'''
		# (4)
		return(True, task_input_task_list, asset_list)
		
	# возврат списка задачь со статусом checking где данный исполнитель в списке проверяющих.
	# self.asset.project - должен быть инициализирован
	# nik_name (str) -
	def get_chek_list_of_artist(self, nik_name): # v2
		pass
		# 1 - получаем список ассетов asset_list
		# 2 - для каждого ассета(со статусом "active") получаем список задач данного исполнителя (статус - checking). заполняем список task_list.
		# 3 - заполняем chek_list
		
		# (1)
		result = self.asset.get_name_data_dict_by_all_types()
		if not result[0]:
			return(False, result[1])
		asset_list = result[1]
		
		# (2)
		task_list = []
		for asset_name in asset_list:
			if asset_list[asset_name]['status']== 'active':
				asset_id = asset_list[asset_name]['id']
				bool_, return_data = self.get_list(asset_id=asset_id, task_status='checking')
				if not bool_:
					return(bool_, return_data)
				task_list = task_list + return_data
				
		# (3)
		chek_list = []
		for task in task_list:
			readers = task['readers']
			readers2 = {}
			if task['chat_local']:
				readers2 = task['chat_local']
			
			if nik_name in readers and task['status'] == 'checking':
				if readers[nik_name] == 0:
					if 'first_reader' in readers:
						if readers['first_reader'] == nik_name:
							chek_list.append(task)
						elif readers[readers['first_reader']] == 1:
							chek_list.append(task)
					else:
						chek_list.append(task)
			elif nik_name in readers and nik_name in readers2 and readers2[nik_name] == 0:
				chek_list.append(task)
			else:
				pass
		'''
		# read tasks
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		task_list = []
		chek_list = []
		
		for asset_name in asset_list:
			if asset_list[asset_name]['status']== 'active':
				asset_id = asset_list[asset_name]['id']
				table = '\"' + asset_id + ':' + self.tasks_t + '\"'
				#string = 'select * from ' + table + ' WHERE status = ?'
				string = 'select * from ' + table
				data = ('checking',)
				try:
					#c.execute(string, data)
					c.execute(string)
					rows = c.fetchall()
					task_list = task_list + rows
				except:
					conn.close()
					return(False, string)
					
		for task in task_list:
			try:
				readers = json.loads(task['readers'])
			except:
				continue
			readers2 = {}
			try:
				readers2 = json.loads(task['chat_local'])
				#print(readers2)
			except:
				pass
			
			if nik_name in readers and task['status'] == 'checking':
				if readers[nik_name] == 0:
					if 'first_reader' in readers:
						if readers['first_reader'] == nik_name:
							chek_list.append(dict(task))
						elif readers[readers['first_reader']] == 1:
							chek_list.append(dict(task))
					else:
						chek_list.append(dict(task))
			elif nik_name in readers and nik_name in readers2 and readers2[nik_name] == 0:
				chek_list.append(dict(task))
			else:
				pass
				#print('epte!')
		'''
		return(True, chek_list)
	
	# input_task_list (list) - список задач (словари)
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	def service_add_list_to_input(self, input_task_list, task_data=False): # v2
		pass
		# 0 - получение task_data.
		# 1 - проверка на srvice
		# 2 - получение данных для перезаписи инпута данной задачи и аутпутов новых входящих задач.
		# 3 - изменение статуса данной задачи.
		# 4 - внесение изменений в БД по данной задаче.
		# 5 - внесение изменений в БД по входящим задачам.
		# 6 - внесение изменений в объект, если он инициализирован
		
		# (0)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.%s' % (key, key))
				
		# (1)
		if task_data['task_type'] != 'service':
			comment = 'In task.service_add_list_to_input() - incorrect type!\nThe type of task to be changed must be "service".\nThis type: "%s"' % task_data['task_type']
			return(False, comment)
		
		# (2)
		# add input list
		# -- get_input_list
		overlap_list = []
		inputs = []
		done_statuses = []
		rebild_input_task_list = []
		for task in input_task_list:
			# -- get inputs list
			if task_data['input']:
				ex_inputs = []
				try:
					ex_inputs = task_data['input']
				except:
					pass
				if task['task_name'] in ex_inputs:
					overlap_list.append(task['task_name'])
					continue
			inputs.append(task['task_name'])
			# -- get done statuses
			done_statuses.append(task['status'] in self.end_statuses)
			
			# edit outputs
			if task['output']:
				ex_outputs = []
				try:
					ex_outputs = task['output']
				except:
					pass
				ex_outputs.append(task_data['task_name'])
				task['output'] = ex_outputs
			else:
				this_outputs = []
				this_outputs.append(task_data['task_name'])
				task['output'] = this_outputs
				
			rebild_input_task_list.append(task)
			
		if not task_data['input']:
			task_data['input'] = inputs
		else:
			ex_inputs = []
			try:
				ex_inputs = task_data['input']
			except:
				pass
			task_data['input'] = ex_inputs + inputs
		
		# (3) change status
		if task_data['status'] in self.end_statuses:
			if False in done_statuses:
				task_data['status'] = 'null'
				self.this_change_from_end(task_data)
				
		# (4)
		read_ob = self.asset.project
		table_name = '"%s:%s"' % (task_data['asset_id'], self.tasks_t)
		keys = self.tasks_keys
		update_data = {'input':task_data['input'], 'status':task_data['status']}
		where = {'task_name': task_data['task_name']}
		bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
		if not bool_:
			return(bool_, r_data)
		
		# (5)
		append_task_name_list = []
		for task in rebild_input_task_list:
			if not task['task_name'] in overlap_list:
				table_name = '"%s:%s"' % (task['asset_id'], self.tasks_t)
				update_data = {'output':task['output']}
				where = {'task_name': task['task_name']}
				append_task_name_list.append(task['task_name'])
				bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
				if not bool_:
					return(bool_, r_data)
				
		# (6)
		if self.task_name == task_data['task_name']:
			self.status = task_data['status']
			self.input = task_data['input']
		
		'''
		# edit db
		# -- Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# -- -- edit Current Task
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		
		string = 'UPDATE ' +  table + ' SET  \"input\"  = ?, \"status\"  = ?  WHERE \"task_name\" = \"' + task_data['task_name'] + '\"'
		data = (task_data['input'], task_data['status'])
		c.execute(string, data)
		# debug
		#print('input: ', string, data)
		
		# -- -- edit Outputs Task
		append_task_name_list = []
		#for task in input_task_list:
		for task in rebild_input_task_list:
			#print(task['task_name'], task['output'])
			if not task['task_name'] in overlap_list:
				table = '\"' + task['asset_id'] + ':' + self.tasks_t + '\"'
				string = 'UPDATE ' +  table + ' SET  \"output\"  = ?  WHERE \"task_name\" = \"' + task['task_name'] + '\"'
				data = (task['output'],)
				c.execute(string, data)
				append_task_name_list.append(task['task_name'])
				# debug
				print('output: ', string, data)
		
		conn.commit()
		conn.close()
		'''
		
		return(True, (task_data['status'], append_task_name_list))
		
	# asset_list (list) - подсоединяемые ассеты (словари)
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	def service_add_list_to_input_from_asset_list(self, asset_list, task_data=False): # v2 ** start
		pass
		# 1 - получение task_data.
		# 2 - проверка на srvice
		# 3 - получение списка задачь для добавления в инпут
		
		# (1)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.%s' % (key, key))
				
		# (2)
		if task_data['task_type'] != 'service':
			comment = 'In task.service_add_list_to_input_from_asset_list() - incorrect type!\nThe type of task to be changed must be "service".\nThis type: "%s"' % task_data['task_type']
			return(False, comment)
		
		# (3)
		final_tasks_list = []
		types = {'obj':'model', 'char':'rig'}
		for ast in asset_list:
			ast_ob = asset(self.project)
			ast_ob.init(ast)
			tsk_ob = task(ast_ob)
			if task_data['asset_type'] in ['location', 'shot_animation'] and ast['type'] in types:
				activity = types[ast['type']]
				
		
		'''
		# edit db
		# -- Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# get task list
		final_tasks_list = []
		for asset in asset_list:
			if task_data['asset_type'] in ['location', 'shot_animation'] and asset['type'] in ['obj', 'char']:
				activity = None
				if asset['type'] == 'obj':
					activity = 'model'
				elif asset['type'] == 'char':
					activity = 'rig'
				
				# get all task data
				table = '\"' + asset['id'] + ':' + self.tasks_t + '\"'
				string = 'select * from ' + table
				try:
					c.execute(string)
				except:
					print(('Not exicute in service_add_list_to_input_from_asset_list -> ' + asset['name']))
					continue
				else:
					td_dict = {}
					rows = c.fetchall()
					for td in rows:
						td_dict[td['task_name']] = td
						
					for td in rows:
						if td['activity'] == activity:
							if not dict(td).get('input') or td_dict[td['input']]['activity'] != activity:
								final_tasks_list.append(td)
			
			else:
				task_name = (asset['name'] + ':final')
				
				table = '\"' + asset['id'] + ':' + self.tasks_t + '\"'
				string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
				try:
					c.execute(string)
					final_task = dict(c.fetchone())
					final_tasks_list.append(final_task)
				except:
					print(('not found task: ' + task_name))
		
		conn.close()
		'''
		
		result = self.service_add_list_to_input(final_tasks_list, task_data)
		if not result[0]:
			return(False, result[1])
		
		return(True, result[1])
		
	# self.asset.project - должен быть инициализирован
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	# removed_tasks_list (list) - содержит словари удаляемых из инпута задач.
	def service_remove_task_from_input(self, removed_tasks_list, task_data=False, change_status = True): # v2
		pass
		# 0 - получение task_data.
		# 1 - тест на статус сервис-не сервис.
		# 2 - очистка списка входящих.
		# 3 - замена статуса очищаемой задачи.
		# 4 - удаление данной задачи из output - входящей задачи.
		# 5 - перезепись status, input - изменяемой задачи.
		# 6 - изменение статуса далее по цепи.
		# 7 - внесение изменений в объект, если он инициализирован
		
		# (0)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.%s' % (key, key))
		
		# (1)
		if task_data['task_type'] != 'service':
			comment = 'In task.service_remove_task_from_input() - incorrect type!\nThe type of task being cleared, must be "service".\nThis type: "%s"' % task_data['task_type']
			return(False, comment)
		
		# (2)
		# get input_list
		input_list = task_data['input']
		# removed input list
		for tsk in removed_tasks_list:
			if tsk['task_name'] in input_list:
				input_list.remove(tsk['task_name'])
			else:
				print('warning! *** ', tsk['task_name'], ' not in ', input_list)
		
		# (3)
		# GET STATUS
		new_status = None
		old_status = task_data['status']
		assets = False
		if old_status == 'done' or not input_list:
			new_status = 'done'
		else:
			# get assets dict
			result = self.asset.get_name_data_dict_by_all_types()
			if not result[0]:
				return(False, result[1])
			assets = result[1]
			#
			bool_statuses = []
			
			for task_name in input_list:
				bool_, r_data = self.get_tasks_data_by_name_list([task_name], assets_data = assets.get(task_name.split(':')[0]))
				if not bool_:
					print('#'*5)
					print('in task.get_tasks_data_by_name_list()')
					print('task_name - %s' % task_name)
					print('asset_data - ', assets_data)
					continue
				else:
					if r_data:
						inp_task_data = r_data[task_name]
					else:
						continue
				
				if inp_task_data['status'] in self.end_statuses:
					bool_statuses.append(True)
				else:
					bool_statuses.append(False)
					
			if False in bool_statuses:
				new_status = 'null'
			else:
				new_status = 'done'
		'''
		# ****** connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		assets = False
		if old_status == 'done' or not input_list:
			new_status = 'done'
		else:
			# get assets dict
			result = self.get_name_data_dict_by_all_types(project_name)
			if not result[0]:
				return(False, result[1])
			assets = result[1]
			
			bool_statuses = []
			
			for task_name in input_list:
				try:
					asset_id = assets[task_name.split(':')[0]]['id']
				except:
					print(('in from_service_remove_input_tasks incorrect key: ' + task_name.split(':')[0] + ' in ' + task_name))
					continue
				
				table = '\"' + asset_id + ':' + self.tasks_t + '\"'
				
				string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
				try:
					c.execute(string)
					inp_task_data = c.fetchone()
				except:
					conn.close()
					return(False, ('in from_service_remove_input_tasks can not read ' + string))
					
				if inp_task_data['status'] in self.end_statuses:
					bool_statuses.append(True)
				else:
					bool_statuses.append(False)
					
			if False in bool_statuses:
				new_status = 'null'
			else:
				new_status = 'done'
		'''	
		# (4)
		for tsk in removed_tasks_list:
			output_list = tsk['output']
			if not output_list:
				continue
			
			if task_data['task_name'] in output_list:
				output_list.remove(task_data['task_name'])
				print('#'*5, tsk['task_name'], output_list)
			else:
				print('#'*5)
				continue
			
			table = '"%s:%s"' % (tsk['asset_id'], self.tasks_t)
			update_data = {'output': output_list}
			where = {'task_name': tsk['task_name']}
			bool_, r_data = database().update('project', self.asset.project, table, self.tasks_keys, update_data, where, table_root=self.tasks_db)
			if not bool_:
				return(bool_, r_data)
			'''
			string = 'UPDATE ' + table + ' SET output = ? WHERE task_name = ?'
			data = (json.dumps(output_list), tsk['task_name'])
			c.execute(string, data)
			'''
		# (5)
		table = '"%s:%s"' % (task_data['asset_id'], self.tasks_t)
		if change_status:
			update_data = {'input': input_list, 'status':new_status}
		else:
			update_data = {'input': input_list}
		where = {'task_name': task_data['task_name']}
		bool_, r_data = database().update('project', self.asset.project, table, self.tasks_keys, update_data, where, table_root=self.tasks_db)
		if not bool_:
			return(bool_, r_data)
		
		'''
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		string = 'UPDATE ' + table + ' SET status = ?, input = ?  WHERE task_name = ?'
		data = (new_status, json.dumps(input_list), task_data['task_name'])
		c.execute(string, data)
		conn.commit()
		conn.close()
		'''
		
		# (6)
		if change_status:
			if old_status == 'done' and new_status == 'null':
				self.this_change_from_end(task_data, assets = assets)
			elif old_status == 'null' and new_status == 'done':
				self.this_change_to_end(task_data, assets = assets)
				
		# (7)
		if self.task_name == task_data['task_name']:
			if change_status:
				self.status = new_status
			self.input = input_list
		
		# return
		if change_status:
			return(True, (new_status, input_list))
		else:
			return(True, (old_status, input_list))
		
	def service_change_task_in_input(self, project_name, task_data, removed_task_data, added_task_data):
		pass
		# other errors test
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		# debug	
		print(task_data['task_name'])
		print(removed_task_data['task_name'])
		print(added_task_data['task_name'])
		
		# remove task
		result = self.service_remove_task_from_input(project_name, task_data, [removed_task_data])
		if not result[0]:
			return(False, result[1])
		
		new_status, input_list = result[1]
		
		# edit task_data.input
		task_data = dict(task_data)
		#input_tasks = json.loads(task_data['input'])
		#input_tasks.remove(removed_task_data['task_name'])
		#task_data['input'] = json.dumps(input_tasks)
		task_data['input'] = json.dumps(input_list)
		task_data['status'] = new_status
		
		#print(json.dumps(task_data, sort_keys = True, indent = 4))
		#return(False, 'Epteeeee!')
		
		# add task
		result = self.service_add_list_to_input(project_name, task_data, [added_task_data])
		if not result[0]:
			return(False, result[1])
			
		return(True, result[1])
			
class log(task):
	'''
	notes_log(project_name, task_name, {key: data, ...}) 
	
	read_log(project_name, asset_name, {key: key_name, ...});; example: self.read_log(project, asset, {'activity':'rig_face', 'action':'push'});; return: (True, ({key: data, ...}, {key: data, ...}, ...))  or (False, comment)
	
	'''
	
	def __init__(self):
		self.camera_log_file_name = 'camera_logs.json'
		self.playblast_log_file_name = 'playblast_logs.json'
		
		self.log_actions = ['push', 'open', 'report','recast' , 'change_artist', 'close', 'done', 'return_a_job', 'send_to_outsource', 'load_from_outsource']
		
		task.__init__(self)
	
	def notes_log(self, project_name, logs_keys, asset_id):
		
		# other errors test
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# test task_name
		try:
			task_name = (logs_keys['task_name'],)
		except:
			return False, 'not task_name'
		
		# date time
		try:
			time = logs_keys['date_time']
		except:
			logs_keys['date_time'] = datetime.datetime.now()
		
		# open db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		table = '\"' + asset_id + ':' + logs_keys['activity'] + ':logs\"'
		
		# exists and create table
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
			
		except:
			string2 = "CREATE TABLE " + table + " ("
			for i,key in enumerate(self.logs_keys):
				if i == 0:
					string2 = string2 + key[0] + ' ' + key[1]
				else:
					string2 = string2 + ', ' + key[0] + ' ' + key[1]
			string2 = string2 + ')'
			c.execute(string2)
			
		# create string to add log
		string = "insert into " + table + " values"
		values = '('
		data = []
		for i, key in enumerate(self.logs_keys):
			if i< (len(self.logs_keys) - 1):
				values = values + '?, '
			else:
				values = values + '?'
			if key[0] in logs_keys:
				data.append(logs_keys[key[0]])
			else:
				if key[1] == 'real':
					data.append(0.0)
				elif key[1] == 'timestamp':
					data.append(None)
				else:
					data.append('')
					
		values = values + ')'
		data = tuple(data)
		string = string + values
		
		# add log
		c.execute(string, data)
		conn.commit()
		conn.close()
		
		return(True, 'ok')
		
	def read_log(self, project_name, asset_id, activity):
		# other errors test
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# read tasks
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# create string
		table = '\"' + asset_id + ':' + activity + ':logs\"'
		string = 'select * from ' + table
		
		rows = None
		
		try:
			c.execute(string)
			rows = c.fetchall()
		except:
			conn.close()
			return(False, 'can_not_read_logs!')
		'''
		c.execute(string)
		rows = c.fetchall()
		'''
		conn.close()
		return(True, rows)
		
	def get_push_logs(self, project_name, task_data):
		# get all logs
		result = self.read_log(project_name, task_data['asset_id'], task_data['activity'])
		if not result[0]:
			return(False, result[1])
		
		push_logs = []
		for row in result[1]:
			if row['action'] == 'push':
				row = dict(row)
				dt = row['date_time']
				data = str(dt.year) + '/' + str(dt.month) + '/' + str(dt.day) + '/' + str(dt.hour) + ':' + str(dt.minute)
				row['date_time'] = data
				push_logs.append(row)
				
		return(True, push_logs)
	
	# *** CAMERA LOGS ***
	def camera_notes_log(self, project_name, task_data, comment, version):
		logs_keys = {}
		tasks_keys = []
		for key in self.tasks_keys:
			tasks_keys.append(key[0])
		
		for key in self.logs_keys:
			if key[0] in tasks_keys:
				logs_keys[key[0]] = task_data[key[0]]
				
		logs_keys['comment'] = comment
		logs_keys['action'] = 'push_camera'
		dt = datetime.datetime.now()
		date = str(dt.year) + '/' + str(dt.month) + '/' + str(dt.day) + '/' + str(dt.hour) + ':' + str(dt.minute)
		logs_keys['date_time'] = date
		logs_keys['version'] = version
		
		path = os.path.join(task_data['asset_path'], self.ADDITIONAL_FOLDERS['meta_data'], self.camera_log_file_name)
		path = NormPath(path)
		
		data = {}
		
		if os.path.exists(path):
			with open(path, 'r') as f:
				try:
					data = json.load(f)
				except:
					pass
		
		data[version] = logs_keys
		
		with open(path, 'w') as f:
			jsn = json.dump(data, f, sort_keys=True, indent=4)
		
		return(True, 'Ok!')
	
	def camera_read_log(self, project_name, task_data):
		path = os.path.join(task_data['asset_path'], self.ADDITIONAL_FOLDERS['meta_data'], self.camera_log_file_name)
		if not os.path.exists(path):
			return(False, 'No saved versions!')
			
		with open(path, 'r') as f:
			data = None
			try:
				data = json.load(f)
			except:
				return(False, ('problems with file versions: ' + path))
		
		nums = []
		sort_data = []
		for key in data:
			nums.append(int(key))
		nums.sort()
		
		for num in nums:
			key = '0'*(4 - len(str(num))) + str(num)
			sort_data.append(data[str(key)])
			
		return(True, sort_data)
		
	# *** PLAYBLAST LOGS ***
	def playblast_notes_log(self, project_name, task_data, comment, version):
		logs_keys = {}
		tasks_keys = []
		for key in self.tasks_keys:
			tasks_keys.append(key[0])
		
		for key in self.logs_keys:
			if key[0] in tasks_keys:
				logs_keys[key[0]] = task_data[key[0]]
				
		logs_keys['comment'] = comment
		logs_keys['action'] = 'playblast'
		dt = datetime.datetime.now()
		date = str(dt.year) + '/' + str(dt.month) + '/' + str(dt.day) + '/' + str(dt.hour) + ':' + str(dt.minute)
		logs_keys['date_time'] = date
		logs_keys['version'] = version
		
		path = os.path.join(task_data['asset_path'], self.ADDITIONAL_FOLDERS['meta_data'], self.playblast_log_file_name)
		path = NormPath(path)
		
		data = {}
		
		if os.path.exists(path):
			with open(path, 'r') as f:
				try:
					data = json.load(f)
				except:
					pass
		
		data[version] = logs_keys
		
		with open(path, 'w') as f:
			jsn = json.dump(data, f, sort_keys=True, indent=4)
		
		return(True, 'Ok!')
	
	def playblast_read_log(self, project_name, task_data):
		path = os.path.join(task_data['asset_path'], self.ADDITIONAL_FOLDERS['meta_data'], self.playblast_log_file_name)
		if not os.path.exists(path):
			return(False, 'No saved versions!')
			
		with open(path, 'r') as f:
			data = None
			try:
				data = json.load(f)
			except:
				return(False, ('problems with file versions: ' + path))
		
		nums = []
		sort_data = []
		for key in data:
			nums.append(int(key))
		nums.sort()
		
		for num in nums:
			key = '0'*(4 - len(str(num))) + str(num)
			sort_data.append(data[str(key)])
			
		return(True, sort_data)
		
	
	def camera_get_push_logs(self, project_name, task_data):
		pass
		
class artist(studio):
	'''
	self.add_artist({key:data, ...}) - "nik_name", "user_name" - Required, add new artist in 'artists.db';; return - (True, 'ok') or (Fasle, comment) comments: 'overlap', 'not nik_name', 
	
	self.login_user(nik_name, password) - 
	
	self.read_artist({key:data, ...}) - "nik_name", - Required, returns full information, relevant over the keys ;; example: self.read_artist({'specialty':'rigger'});; return: (True, [{Data}, ...])  or (False, comment)
	
	self.edit_artist({key:data, ...}) - "nik_name", - Required, does not change the setting ;;
	
	self.get_user() - ;; return: (True, (nik_name, user_name)), (False, 'more than one user'), (False, 'not user') ;;
	
	self.add_stat(user_name, {key:data, ...}) - "project_name, task_name, data_start" - Required ;;
	
	self.read_stat(user_name, {key:data, ...}) - returns full information, relevant over the keys: (True, [{Data}, ...]) or (False, comment);; 
	
	self.edit_stat(user_name, project_name, task_name, {key:data, ...}) - 
	'''
	def __init__(self):
		#base fields
		for key in self.artists_keys:
			exec('self.%s = False' % key)
		#studio.__init__(self)
		pass
	
	# если registration=True - произойдёт заполнение полей artists_keys, поле user_name будет заполнено.
	# если registration=False - поля artists_keys заполняться не будут, поле user_name - останется пустым.
	def add_artist(self, keys, registration = True):
		# test nik_name
		if not keys.get('nik_name'):
			return(False, '\"Nik Name\" not specified!')
		if not keys.get('password'):
			return(False, '\"Password\" not specified!')

		# создание таблицы, если отсутствует.
		# определение level - если первый юзер то рут.
		# проверка на совпадение имени.
		# проверка на совпадение user_name и перезапись существующих в пустую строку.
		# запиь нового юзера
		
		# create table
		bool_, return_data = database().create_table('studio', self, self.artists_t, self.artists_keys)
		if not bool_:
			return(bool_, return_data)
		
		# read table
		bool_, return_data = database().read('studio', self, self.artists_t, self.artists_keys)
		if not bool_:
			return(bool_, return_data)
		# -- set level
		if not return_data:
			keys['level'] = 'root'
		else:
			if not keys.get('level'):
				keys['level'] = 'user'
		# -- date_time
		keys['date_time'] = datetime.datetime.now()
		# -- test exist name, user_name
		if registration:
			keys['user_name'] = getpass.getuser()
		else:
			keys['user_name'] = ''
		for item in return_data:
			# test nik_name
			if item.get('nik_name') == keys['nik_name']:
				return(False, 'User "%s" Already Exists!' % keys['nik_name'])
			# test user_name
			if registration:
				if item.get('user_name') == keys['user_name']:
					bool_, return_data = database().update('studio', self, self.artists_t, self.artists_keys, {'user_name': ''}, {'user_name': keys['user_name']})
					if not bool_:
						return(bool_, return_data)
				
		# create user
		bool_, return_data = database().insert('studio', self, self.artists_t, self.artists_keys, keys)
		if not bool_:
			return(bool_, return_data)
		else:
			# fill fields
			if registration:
				for key in self.artists_keys:
					com = 'self.%s = keys.get("%s")' % (key, key)
					exec(com)
			return(True, 'ok')
		
	def read_artist(self, keys):
		if keys == 'all':
			keys = False
		bool_, return_data = database().read('studio', self, self.artists_t, self.artists_keys, where=keys)
		return(bool_, return_data)
		
	def read_artist_of_workroom(self, workroom_id):
		bool_, return_data = database().read('studio', self, self.artists_t, self.artists_keys)
		if not bool_:
			return(bool_, return_data)
		#
		artists_dict = {}
		for row in return_data:
			try:
				workrooms = json.loads(row['workroom'])
			except:
				continue
			if workroom_id in workrooms:
				artists_dict[row['nik_name']] = row
		return(True, artists_dict)
		
	def login_user(self, nik_name, password):
		# проверка наличия юзера
		# проверка пароля
		# очистка данного юзернейма
		# присвоение данного юзернейма пользователю
		user_name = getpass.getuser()
		bool_, user_data = database().read('studio', self, self.artists_t, self.artists_keys, where = {'nik_name': nik_name})
		if not bool_:
			return(bool_, user_data)
		# test exists user
		if not user_data:
			return(False, 'User is not found!')
		# test password
		else:
			if user_data[0].get('password') != password:
				return(False, 'Incorrect password!')
		# clean
		bool_, return_data = database().update('studio', self, self.artists_t, self.artists_keys, {'user_name': ''}, {'user_name': user_name})
		if not bool_:
			return(bool_, return_data)
		# set user_name
		bool_, return_data = database().update('studio', self, self.artists_t, self.artists_keys, {'user_name': user_name}, {'nik_name': nik_name})
		if not bool_:
			return(bool_, return_data)
		
		# fill fields
		for key in self.artists_keys:
			com = 'self.%s = user_data[0].get("%s")' % (key, key)
			#print('#'*3, item[0], com)
			exec(com)
		return(True, (nik_name, user_name))

	def get_user(self, outsource = False):
		user_name = getpass.getuser()
		bool_, return_data = database().read('studio', self, self.artists_t, self.artists_keys, where = {'user_name': user_name})
		if not bool_:
			return(bool_, return_data)
		rows = return_data
		# conditions # return
		if not rows:
			return False, 'not user'
		elif len(rows)>1:
			return False, 'more than one user'
		else:
			# fill fields
			for key in self.artists_keys:
				com = 'self.%s = rows[0].get("%s")' % (key, key)
				exec(com)
			if not outsource:
				return True, (rows[0]['nik_name'], rows[0]['user_name'], None, rows[0])
			else:
				if rows[0]['outsource']:
					out_source = bool(rows[0]['outsource'])
				else:
					out_source = False
				return True, (rows[0]['nik_name'], rows[0]['user_name'], out_source, rows[0])
	
	# key_data = обязательное поле nik_name
	# artist_current_data - текущие данные пользователя на момент редактирования.
	def edit_artist(self, key_data, artist_current_data = False):
		# test nik_name
		nik_name = key_data.get('nik_name')
		if not nik_name:
			return False, 'not nik_name!'
		# test level
		level = key_data.get('level')
		if level and not level in self.user_levels:
			return False, 'wrong level: "%s"!' % level
		# get artist_current_data
		if not artist_current_data:
			bool_, return_data = database().read('studio', self, self.artists_t, self.artists_keys, where = {'nik_name': nik_name})
			if not bool_:
				return(bool_, return_data)
			else:
				if return_data:
					artist_current_data = return_data[0]
				else:
					return(False, return_data)
		# test Access Rights
		# -- user не менеджер
		if not self.level in self.manager_levels:
			return(False, 'Not Access! (your level does not allow you to make similar changes)')
		# -- попытка возвести в ранг выше себя
		elif key_data.get("level") and self.user_levels.index(self.level) < self.user_levels.index(key_data.get("level")):
			return(False, 'Not Access! (attempt to assign a level higher than yourself)')
		# -- попытка сделать изменения пользователя с более высоким уровнем.
		elif artist_current_data.get("level") and self.user_levels.index(self.level) < self.user_levels.index(artist_current_data.get("level")):
			return(False, 'Not Access! (attempt to change a user with a higher level)')
		# update
		del key_data['nik_name']
		bool_, return_data = database().update('studio', self, self.artists_t, self.artists_keys, key_data, {'nik_name': nik_name})
		if not bool_:
			return(bool_, return_data)
		return True, 'ok'
		
	def add_stat(self, user_name, keys):
		# test project_name
		try:
			project_name = keys['project_name']
		except:
			return False, 'not project_name'
		
		# test task_name
		try:
			task_name = keys['task_name']
		except:
			return False, 'not task_name'
		
		# test data_start
		try:
			data_start = keys['data_start']
		except:
			return False, 'not data_start'
		
		# create string
		table = '\"' + user_name + ':' + self.statistic_t + '\"'
		string = "insert into " + table + " values"
		values = '('
		data = []
		for i, key in enumerate(self.statistics_keys):
			if i< (len(self.statistics_keys) - 1):
				values = values + '?, '
			else:
				values = values + '?'
			if key[0] in keys:
				data.append(keys[key[0]])
			else:
				if key[1] == 'real':
					data.append(0.0)
				else:
					data.append('')
					
		values = values + ')'
		data = tuple(data)
		string = string + values
		
		# write task to db
		conn = sqlite3.connect(self.statistic_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# exists table
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
			# unicum task_name test
			r = c.fetchall()
			for row in r:
				if row['task_name'] == keys['task_name']:
					conn.close()
					return False, 'overlap'
		except:
			string2 = "CREATE TABLE " + table + " ("
			for i,key_ in enumerate(self.statistics_keys):
				if i == 0:
					string2 = string2 + key_[0] + ' ' + key_[1]
				else:
					string2 = string2 + ', ' + key_[0] + ' ' + key_[1]
			string2 = string2 + ')'
			#return string2
			c.execute(string2)
		
		# add task
		c.execute(string, data)
		conn.commit()
		conn.close()
		return True, 'ok'
	
	def read_stat(self, nik_name, keys):
		# create string
		table = '\"' + nik_name + ':' + self.statistic_t + '\"'
		
		if keys == 'all':
			string = 'select * from ' + table
		else:
			string = 'select * from ' + table + ' WHERE '
			for i,key in enumerate(keys):
				if key != 'nik_name':
					if i == 0:
						string = string + ' ' + key + ' = ' + '\"' + keys[key] + '\"'
					else:
						string = string + 'and ' + key + ' = ' + '\"' + keys[key] + '\"'
				
		#return string
				
		# read tasks
		conn = sqlite3.connect(self.statistic_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		'''	
		c.execute(string)
		rows = c.fetchall()
		'''
		try:
			c.execute(string)
			rows = c.fetchall()
		except:
			conn.close()
			return False, 'can_not_read_stat'
			
		conn.close()
		'''
		if not rows:
			return False, 'not_task_name'
		'''
						
		return True, rows
		
	def edit_stat(self, user_name, project_name, task_name, keys):
		# create string	
		table = '\"' + user_name + ':' + self.statistic_t + '\"'
		# edit db
		string = 'UPDATE ' +  table + ' SET '
		for key in keys:
			if (key != 'project_name') and (key != 'task_name'):
				string = string + ' ' + key + ' = \"' + keys[key] + '\",'
			
		# -- >>
		string = string + ' WHERE project_name = \"' + project_name + '\" and task_name = \"' + task_name + '\"'
		string = string.replace(', WHERE', ' WHERE')
		#return string
		
		# write task to db
		conn = sqlite3.connect(self.statistic_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		c = conn.cursor()
		'''
		c.execute(string)
		'''
		try:
			c.execute(string)
		except:
			conn.close()
			return False, 'can_not_execute_stat'
		
		conn.commit()
		conn.close()
		
		return True, 'ok'
		
class workroom(studio):
	def __init__(self):
		pass
		#artist.__init__(self)
	
	# keys['type'] - must be a list, False or None
	def add(self, keys):
		# test name
		try:
			name = keys['name']
		except:
			return(False, 'not Name!')
			
		keys['id'] = str(random.randint(0, 1000000000))
		
		# создание таблицы, если отсутствует.
		# проверка на совпадение имени
		# проверка чтобы типы задач были из task_types
		# запись строки в таблицу
		
		# create table
		bool_, return_data = database().create_table('studio', self, self.workroom_t, self.workroom_keys, table_root = self.artists_db)
		if not bool_:
			return(bool_, return_data)
		
		# test exists name
		bool_, return_data = database().read('studio', self, self.workroom_t, self.workroom_keys, where={'name': name}, table_root=self.artists_db)
		if not bool_:
			return(bool_, return_data)
		elif return_data:
			return(False, 'This workroom name: "%s" already exists!' % name)
		
		# test type
		type_ = keys.get('type')
		if type_:
			if type_.__class__.__name__ == 'list':
				for item in type_:
					if not item in self.task_types:
						return(False, 'This type of task: "%s" is not correct!' % item)
			else:
				return(False, 'This type of keys[type]: "%s" is not correct (must be a list, False or None)' % str(type_))
			
		# insert string
		bool_, return_data = database().insert('studio', self, self.workroom_t, self.workroom_keys, keys, table_root=self.artists_db)
		if not bool_:
			return(bool_, return_data)
		
		return(True, 'ok')
		
	def get_list_workrooms(self, DICTONARY = False):
		bool_, return_data = database().read('studio', self, self.workroom_t, self.workroom_keys, table_root=self.artists_db)
		if not bool_:
			return(bool_, return_data)

		return_data_0 = {}
		return_data_1 = []
		return_data_2 = {}
		for row in return_data:
			#return_data['name'] = row['name']
			work_room_data = {}
			work_room_data_1 = {}
			work_room_data_2 = {}
			for key in row.keys():
				work_room_data_1[key] = row[key]
				#print(key)
				#continue
				if key != 'name':
					work_room_data[key] = row[key]
				if key != 'id':
					work_room_data_2[key] = row[key]
			return_data_0[row['name']] = work_room_data
			return_data_1.append(work_room_data_1)
			return_data_2[row['id']] = work_room_data_2
		
		if not DICTONARY:
			return(True, return_data_1)
		elif DICTONARY == 'by_name':
			return(True, return_data_0)
		elif DICTONARY == 'by_id':
			return(True, return_data_2)
		elif DICTONARY == 'by_id_by_name':
			return(True, return_data_2, return_data_0)
		else:
			return(False, ('Incorrect DICTONARY: ' + DICTONARY))
	
	
	def get_name_by_id(self, id_):
		where = {'id': id_}
		bool_, return_data = database().read('studio', self, self.workroom_t, self.workroom_keys, columns = ['name'], where = where, table_root=self.artists_db)
		if not bool_:
			return(bool_, return_data)
		else:
			if return_data:
				return(True, return_data[0]['name'])
			else:
				print('#'*3, 'workroom.get_name_by_id() - id is incorrect!')
				print('#'*3, 'id:', id_)
				return(False, 'Look the terminal!')
	
	def get_id_by_name(self, name):
		where = {'name': name}
		bool_, return_data = database().read('studio', self, self.workroom_t, self.workroom_keys, columns = ['id'], where = where, table_root=self.artists_db)
		if not bool_:
			return(bool_, return_data)
		else:
			if return_data:
				return(True, return_data[0]['id'])
			else:
				print('#'*3, 'workroom.get_id_by_name() - name is incorrect!')
				print('#'*3, 'name:', name)
				return(False, 'Look the terminal!')
	
	# возможно лучше не использовать
	def name_list_to_id_list(self, name_list):
		bool_, data = self.get_list_workrooms('by_name')
		if not bool_:
			return(bool_, data)
		if data:
			return_data = []
			for key in data:
				if key in name_list:
					return_data.append(data[key]['id'])
			return(True, return_data)
		else:
			print('#'*3, 'workroom.name_list_to_id_list() - list of names is incorrect!')
			print('#'*3, 'name list:', name_list)
			return(False, 'Look the terminal!')
	
	# возможно лучше не использовать
	def id_list_to_name_list(self, id_list):
		bool_, data = self.get_list_workrooms('by_id')
		if not bool_:
			return(bool_, data)
		if data:
			return_data = []
			for key in data:
				if key in id_list:
					return_data.append(data[key]['name'])
			return(True, return_data)
		else:
			print('#'*3, 'workroom.id_list_to_name_list() - list of id is incorrect!')
			print('#'*3, 'id list:', id_list)
			return(False, 'Look the terminal!')
			
	def rename_workroom(self, old_name, new_name):
		new_name = new_name.replace(' ', '_')
		
		# проверка имени на совпадение, со старым и с имеющимися
		# получить id
		# экшен
		
		# test name
		if old_name == new_name:
			return(False, 'Match names!')
		bool_, return_data = self.get_list_workrooms('by_name')
		if not bool_:
			return(bool_, return_data)
		if new_name in return_data:
			return(False, 'This name of workroom already exists! "%s"' % new_name)
		
		# get id
		result = self.get_id_by_name(old_name)
		if not result[0]:
			return(False, result[1])
		wr_id = result[1]
		# action
		update_data = {'name':new_name}
		where = {'id': wr_id}
		bool_, return_data = database().update('studio', self, self.workroom_t, self.workroom_keys, update_data, where, table_root=self.artists_db)
		if not bool_:
			return(bool_, return_data)
		return(True, 'Ok!')
	
	# new_type_list - список типов
	def edit_type(self, wr_id, new_type_list):
		update_data = {'type': new_type_list}
		where = {'id': wr_id}
		bool_, return_data = database().update('studio', self, self.workroom_t, self.workroom_keys, update_data, where, table_root=self.artists_db)
		if not bool_:
			return(bool_, return_data)
		return(True, 'Ok!')
		
	
class chat(task):
	'''
	self.record_messages(project_name, task_name, topic) - records topic to '.chats.db';; topic = dumps({line1:(img, img_icon, text), ...})
	
	self.read_the_chat(self, project_name, task_name, reverse = 0) - It returns a list of all messages for a given task;;
	'''
	def __init__(self):
		task.__init__(self)
	
	#def record_messages(self, project_name, task_name, author, color, topic, status, date_time = ''):
	def record_messages(self, project_name, task_name, input_keys):
		# test project
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		'''	
		# get date time
		if date_time == '' or type(date_time) != datetime.datetime:
			date_time = datetime.datetime.now()
		'''
		
		# create string  timestamp
		table = '\"' + task_name + '\"'
		string = "insert into " + table + " values("
		data = []
		for i, key in enumerate(self.chats_keys):
			# -- string
			if i == 0:
				string = string + '?'
			else:
				string = string + ',?'
			
			# -- data
			if key[0] in input_keys.keys():
				data.append(input_keys[key[0]])
			else:
				if key[1] == 'text':
					data.append('')
				elif key[1] == 'real':
					data.append(0.0)
				elif key[1] == 'timestamp':
					data.append(datetime.datetime.now())
				
			
		string = string + ')'
		data = tuple(data)
		
		# connect to self.chat_path
		conn = sqlite3.connect(self.chat_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		#conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# exists or create table
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
			
		except:
			string2 = "CREATE TABLE " + table + " ("
			for i,key in enumerate(self.chats_keys):
				if i == 0:
					string2 = string2 + key[0] + ' ' + key[1]
				else:
					string2 = string2 + ', ' + key[0] + ' ' + key[1]
			string2 = string2 + ')'
			#return string2
			c.execute(string2)
	
		# add topic
		#print(string, data)
		#return
		c.execute(string, data)
		conn.commit()
		conn.close()
		return(True, 'ok')
	
	def read_the_chat(self, project_name, task_name, reverse = 0):
		# test project
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		table = '\"' + task_name + '\"'
		
		# connect to self.chat_path
		'''
		conn = sqlite3.connect(self.chat_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		'''
		try:
			conn = sqlite3.connect(self.chat_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return False, '".chats.db" not Connect!'
		
		# read the topic
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
			rows = c.fetchall()
			
		except:
			conn.close()
			return False, ('topic with name ' + table + ' not Found!')
		
		conn.close()
		
		return True, rows
		
	def task_edit_rid_status_unread(self, project_name, task_data):
		# test project
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		string = 'SELECT * FROM ' + table + ' WHERE task_name = ?'
		data = (task_data['task_name'],)
		
		# connect db
		try:
			conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return(False, 'in task_edit_rid_status_unread - not connect db!')
		
		# read-edit data
		c.execute(string, data)
		task_data = dict(c.fetchone())
		try:
			readers = json.loads(task_data['readers'])
			for nik_name in readers:
				readers[nik_name] = 0
			task_data['chat_local'] = json.dumps(readers)
		except:
			task_data['chat_local'] = json.dumps({})
			
		# write data
		string = 'UPDATE ' + table + 'SET chat_local = ? WHERE task_name = ?'
		data = (task_data['chat_local'], task_data['task_name'])
		c.execute(string, data)
		
		conn.commit()
		conn.close()
		
		return(True, 'Ok!')
	
	def task_edit_rid_status_read(self, project_name, task_data, nik_name):
		# test project
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		string = 'SELECT * FROM ' + table + ' WHERE task_name = ?'
		data = (task_data['task_name'],)
		
		# connect db
		try:
			conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return(False, 'in task_edit_rid_status_unread - not connect db!')
		
		# read-edit data
		c.execute(string, data)
		task_data = dict(c.fetchone())
		
		readers2 = {}
		try:
			readers2 = json.loads(task_data['chat_local'])
			readers2[nik_name] = 1
		except:
			readers2[nik_name] = 1
		task_data['chat_local'] = json.dumps(readers2)
		
		# write data
		string = 'UPDATE ' + table + 'SET chat_local = ? WHERE task_name = ?'
		data = (task_data['chat_local'], task_data['task_name'])
		c.execute(string, data)
		
		conn.commit()
		conn.close()
		
		return(True, 'Ok!')
	
	def edit_message(self, project_name, task_name, keys):
		pass
	
class set_of_tasks(studio):
	def __init__(self):
		self.set_of_tasks_keys = [
		'task_name',
		'input',
		'activity',
		'tz',
		'cost',
		'standart_time',
		'task_type',
		'extension',
		]
	
	def create(self, name, asset_type, keys = False):
		# test data
		if name == '':
			return(False, 'Not Name!')
		
		if not asset_type in self.asset_types:
			return(False, 'Wrong type of asset: "%s"' % asset_type)
		
		# test exists path
		if not os.path.exists(self.set_of_tasks_path):
			return(False, (self.set_of_tasks_path + ' Not Found!'))
		
		# read data
		try:
			with open(self.set_of_tasks_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, (self.set_of_tasks_path + " can not be read!"))
			
		# test exists of set
		if name in data.keys():
			return(False, 'This Set Already Exists!')
			
		# edit data
		data[name] = {}
		data[name]['asset_type'] = asset_type
		if keys and keys.__class__.__name__ != 'list':
			return(False, 'Not the correct data type from the "keys": "%s"' % keys.__class__.__name__)
		elif keys and keys.__class__.__name__ == 'list':
			data[name]['sets'] = keys
		else:
			data[name]['sets'] = {}

		# write data
		try:
			with open(self.set_of_tasks_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				#print('data:', data)
				f.close()
		except:
			return(False, (self.set_of_tasks_path + "  can not be write"))
		
		return(True, 'ok')
	
	def get_list(self, path = False):
		if not path:
			# test exists path
			if not self.set_of_tasks_path:
				#self.get_set_of_tasks_path()
				self.get_studio()
				
			if not os.path.exists(self.set_of_tasks_path):
				return(False, ('%s Not Found!' % self.set_of_tasks_path))
				
			# read data
			try:
				with open(self.set_of_tasks_path, 'r') as read:
					data = json.load(read)
					read.close()
			except Exception as e:
				print('#'*5, e)
				return(False, ("%s can not be read! Look The terminal!" % self.set_of_tasks_path))
				
		else:
			if not os.path.exists(path):
				return(False, ('No Exists path: %s' % path))
			# read data
			try:
				with open(path, 'r') as read:
					data = json.load(read)
					read.close()
			except Exception as e:
				print('#'*5, e)
				return(False, ("%s can not be read! Look The terminal!" % self.set_of_tasks_path))
			
		return(True, data)
		
	def get_list_by_type(self, asset_type):
		result = self.get_list()
		if not result[0]:
			return(False, result[1])
		
		return_list = {}
		for key in result[1]:
			if result[1][key]['asset_type'] == asset_type:
				return_list[key] = result[1][key]
				
		return(True, return_list)
		
	def get_dict_by_all_types(self):
		result = self.get_list()
		if not result[0]:
			return(False, result[1])
		
		return_list = {}
		for key in result[1]:
			asset_type = result[1][key]['asset_type']
			if not asset_type in return_list:
				return_list[asset_type] = {}
			
			return_list[asset_type][key] = result[1][key]
				
		return(True, return_list)
	
	def get(self, name):
		# test data
		if not name:
			return(False, 'Not Name!')
			
		# test exists path
		if not os.path.exists(self.set_of_tasks_path):
			return(False, (self.set_of_tasks_path + ' Not Found!'))
			
		# read data
		try:
			with open(self.set_of_tasks_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, (self.set_of_tasks_path + " can not be read!"))
			
		if not name in data:
			return(False, ('Set with name \"' + name + '\" Not Found!'))
		
		return(True, data[name]) # list of dictionaries
			
	
	def remove(self, name):
		# test data
		if name == '':
			return(False, 'Not Name!')
			
		# test exists path
		if not os.path.exists(self.set_of_tasks_path):
			return(False, (self.set_of_tasks_path + ' Not Found!'))
			
		# read data
		try:
			with open(self.set_of_tasks_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, (self.set_of_tasks_path + " can not be read!"))
			
		if not name in data:
			return(False, ('Set with name \"' + name + '\" Not Found!'))
		
		# del data
		del data[name]
		
		# write data
		try:
			with open(self.set_of_tasks_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				#print('data:', data)
				f.close()
		except:
			return(False, (self.set_of_tasks_path + "  can not be write"))
			
		return(True, 'ok')
	
	def rename(self, name, new_name):
		# test data
		if name == '' or new_name == '':
			return(False, 'Not Name!')
			
		# test exists path
		if not os.path.exists(self.set_of_tasks_path):
			return(False, (self.set_of_tasks_path + ' Not Found!'))
			
		# read data
		try:
			with open(self.set_of_tasks_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, (self.set_of_tasks_path + " can not be read!"))
			
		# test exists of set
		if not name in data.keys():
			return(False, ('Set With Name \"' + name + '\" Not Found!'))
			read.close()
		
		# del data
		keys = data[name]
		del data[name]
		data[new_name] = keys
		
		# write data
		try:
			with open(self.set_of_tasks_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				#print('data:', data)
				f.close()
		except:
			return(False, (self.set_of_tasks_path + "  can not be write"))
			
		return(True, 'ok')
		
	def edit_asset_type(self, name, asset_type):
		# test data
		if name == '':
			return(False, 'Not Name!')
		
		# test type
		if not asset_type in self.asset_types:
			return(False, 'Wrong type of asset: "%s"' % asset_type)
			
		# test exists path
		if not os.path.exists(self.set_of_tasks_path):
			return(False, (self.set_of_tasks_path + ' Not Found!'))
			
		# read data
		try:
			with open(self.set_of_tasks_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, (self.set_of_tasks_path + " can not be read!"))
		# test name
		if not data.get(name):
			return(False, 'A set with this name: "%s" does not exist!' % name)
		# edit data
		data[name]['asset_type'] = asset_type
		
		# write data
		try:
			with open(self.set_of_tasks_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return(False, (self.set_of_tasks_path + "  can not be write"))
		
		return(True, 'ok')
	
	def edit(self, name, keys):
		# test data
		if name == '':
			return(False, 'Not Name!')
		
		if keys.__class__.__name__ != 'list':
			return(False, 'Not the correct data type from the "keys": "%s"' % keys.__class__.__name__)
		
		# test exists path
		if not os.path.exists(self.set_of_tasks_path):
			return(False, (self.set_of_tasks_path + ' Not Found!'))
		
		# read data
		try:
			with open(self.set_of_tasks_path, 'r') as read:
				data = json.load(read)
				read.close()
								
		except:
			return(False, (self.set_of_tasks_path + " can not be read!"))
		
		# test exists of set
		if not name in data.keys():
			return(False, ('Set With Name \"' + name + '\" Not Found!'))
			read.close()
		
		# edit data
		data[name]['sets'] = keys

		# write data
		try:
			with open(self.set_of_tasks_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return(False, (self.set_of_tasks_path + "  can not be write"))
		
		return(True, 'ok')
		
	### ****************** Library
	
	def save_set_of_tasks_to_library(self, path):
		# Read Data
		## -- test exists path
		if not os.path.exists(self.set_of_tasks_path):
			return(False, (self.set_of_tasks_path + ' Not Found!'))
		## -- read data
		try:
			with open(self.set_of_tasks_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, (self.set_of_tasks_path + " can not be read!"))
			
		# Write Data
		try:
			with open(path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return(False, (path + "  can not be write"))
		
		return(True, 'ok')
		
	def load_set_of_tasks_from_library(self, load_data):
		# Read Data
		## -- test exists path
		if not os.path.exists(self.set_of_tasks_path):
			return(False, (self.set_of_tasks_path + ' Not Found!'))
		## -- read data
		try:
			with open(self.set_of_tasks_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, (self.set_of_tasks_path + " can not be read!"))
		
		# Edit Data
		for key in load_data:
			data[key] = load_data[key]
		
		
		# Write Data
		try:
			with open(self.set_of_tasks_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return(False, (self.set_of_tasks_path + "  can not be write"))
		
		return(True, 'ok')
		
	def copy_set_of_tasks(self, old_name, new_name):
		# Read Data
		## -- test exists path
		if not os.path.exists(self.set_of_tasks_path):
			return(False, (self.set_of_tasks_path + ' Not Found!'))
		## -- read data
		try:
			with open(self.set_of_tasks_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, (self.set_of_tasks_path + " can not be read!"))
		
		# test name
		if not data.get(name):
			return(False, 'A set with this name: "%s" does not exist!' % name)
		
		# Edit Data
		data[new_name] = data[old_name]
		
		# Write Data
		try:
			with open(self.set_of_tasks_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return(False, (self.set_of_tasks_path + "  can not be write"))
		
		return(True, 'Ok!')
		
class season(studio):
	def __init__(self, project):
		self.project = project
		# fill fields
		for key in self.season_keys:
			exec('self.%s = False' % key)
	
	# заполнение полей по self.season_keys - для передачи экземпляра в уровень ниже.
	def init(self, keys):
		for key in self.season_keys:
			exec('self.%s = keys.get("%s")' % (key, key))

	def create(self, name):
		keys = {}
		keys['name'] = name
		keys['status'] = 'active'
		keys['id'] = str(random.randint(0, 1000000000))
		
		# создание таблицы, если не существует.
		# проверка на существование с даныи именем.
		# добавление сезона.
		
		# -- create table
		bool_, return_data  = database().create_table('project', self.project, self.season_t, self.season_keys, table_root = self.season_db)
		if not bool_:
			return(bool_, return_data)
		
		# проверка на совпадение имени
		bool_, return_data = self.get_by_name(keys['name'])
		if bool_ and return_data:
			return(False, 'Season with this name(%s) already exists!' % keys['name'])
		
		# -- write data
		bool_, return_data = database().insert('project', self.project, self.season_t, self.season_keys, keys, table_root = self.season_db)
		if not bool_:
			return(bool_, return_data)
		return(True, 'ok')
	
	def get_list(self, active = False):
		if active:
			where = {'status': u'active'}
		else:
			where = False
		# write season to db
		bool_, return_data = database().read('project', self.project, self.season_t, self.season_keys, where=where, table_root=self.season_db)
		return(bool_, return_data)

	def get_by_name(self, name):
		keys = {'name': name}
		bool_, return_data = database().read('project', self.project, self.season_t, self.season_keys, where = keys, table_root=self.season_db)
		if not bool_:
			return(bool_, return_data)
		if return_data:
			return(True, return_data[0])
		else:
			return(True, return_data)
	
	def get_by_id(self, id_):
		keys = {'id': id_}
		bool_, return_data = database().read('project', self.project, self.season_t, self.season_keys, where = keys, table_root=self.season_db)
		if not bool_:
			return(bool_, return_data)
		if return_data:
			return(True, return_data[0])
		else:
			return(True, return_data)
	
	def rename(self, name, new_name):
		update_data = {'name': new_name}
		where = {'name': name}
		bool_, return_data = database().update('project', self.project, self.season_t, self.season_keys, update_data, where, table_root=self.season_db)
		if not bool_:
			return(bool_, return_data)
		return(True, 'ok')
	
	def stop(self, name):
		where = {'name': name}
		update_data = {'status': u'none'}
		bool_, return_data = database().update('project', self.project, self.season_t, self.season_keys, update_data, where, table_root=self.season_db)
		return(bool_, return_data)
	
	def start(self, name):
		where = {'name': name}
		update_data = {'status': u'active'}
		bool_, return_data = database().update('project', self.project, self.season_t, self.season_keys, update_data, where, table_root=self.season_db)
		return(bool_, return_data)
	
class group(studio):
	def __init__(self, project):
		self.project = project
		#base fields
		for key in self.group_keys:
			exec('self.%s = False' % key)
	
	# заполнение полей по self.group_keys - для передачи экземпляра в уровень ниже.
	def init(self, keys):
		for key in self.group_keys:
			exec('self.%s = keys.get("%s")' % (key, key))
	
	# keys - словарь по group_keys (name и type - обязательные ключи)
	def create(self, keys):
		# test name
		if not keys.get('name'):
			return(False, 'Not Name!')
			
		# test type
		if not keys.get('type') or (not keys.get('type') in self.asset_types):
			return(False, 'Not Type!')
		
		# get id
		keys['id'] = hex(random.randint(0, 1000000000)).replace('0x','')
		
		# test season key
		if keys['type'] in self.asset_types_with_season:
			if 'season' in keys and keys['season'] == '':
				return(False, 'For This Type Must Specify a Season!')
			elif not 'season' in keys:
				return(False, 'Required For This Type of Key Season!')
		else:
			keys['season'] = ''
		#return(keys)
		# create group
		# -- create table
		bool_, return_data  = database().create_table('project', self.project, self.group_t, self.group_keys, table_root = self.group_db)
		if not bool_:
			return(bool_, return_data)
		
		# проверка на совпадение имени
		if self.get_by_name(keys['name'])[0]:
			return(False, 'Group with this name(%s) already exists!' % keys['name'])
		
		# -- write data
		bool_, return_data = database().insert('project', self.project, self.group_t, self.group_keys, keys, table_root = self.group_db)
		if not bool_:
			return(bool_, return_data)
		
		return(True, 'ok')
		
	def create_recycle_bin(self):
		# -- create table
		bool_, return_data  = database().create_table('project', self.project, self.group_t, self.group_keys, table_root = self.group_db)
		if not bool_:
			return(bool_, return_data)
		
		# get group list
		result = self.get_list()
		if not result[0]:
			return(False, (result[1] + ' in get group list'))
		groups = result[1]
		
		all_group = False
		recycle_bin = False
		names = []
		id_s = []
		if groups:
			for group in groups:
				names.append(group['name'])
				id_s.append(group['id'])
				if group['name'] == self.recycle_bin_name:
					recycle_bin = group
				if group['type'] == 'all':
					all_group = group
				
		if not all_group:
			#print('Not ALL type')
			# rename
			if recycle_bin:
				#print('Exist RB name')
				# -- new name
				new_name = self.recycle_bin_name + hex(random.randint(0, 1000000000)).replace('0x','')
				while new_name in names:
					new_name = self.recycle_bin_name + hex(random.randint(0, 1000000000)).replace('0x','')
				# -- rename
				result = self.rename(self.recycle_bin_name, new_name)
				if not result[0]:
					return(False, result[1])
				
			# create group
			# -- keys
			keys = {
			'name':self.recycle_bin_name,
			'type': 'all',
			'comment':'removed assets'
			}
			# -- get id
			keys['id'] = hex(random.randint(0, 1000000000)).replace('0x','')
			while keys['id'] in id_s:
				keys['id'] = hex(random.randint(0, 1000000000)).replace('0x','')
			#print(keys)
			# -- write data
			bool_, return_data = database().insert('project', self.project, self.group_t, self.group_keys, keys, table_root = self.group_db)
			if not bool_:
				return(bool_, return_data)
		else:
			#print('Exist RB!')
			if not recycle_bin:
				# -- rename
				result = self.rename(all_group['name'], self.recycle_bin_name)
				if not result[0]:
					return(False, (result[1] + 'in rename rcycle bin'))
			
		return(True, 'ok')
			
		
	def get_list(self, f = False): # f = [...] - filter of types список типов
		# write season to db
		bool_, return_data = database().read('project', self.project, self.group_t, self.group_keys, table_root=self.group_db)
		if not bool_:
			return(bool_, return_data)
		# f
		if not f:
			return(True, return_data)
		else:
			f_rows = []
			for grp_data in return_data:
				if grp_data['type'] in f:
					f_rows.append(grp_data)
			return(True, f_rows)
	
	def get_groups_dict_by_id(self):
		result = self.get_list()
		if not result[0]:
			return(False, result[1])
		
		group_dict = {}
		for row in result[1]:
			group_dict[row['id']] = row
			
		return(True, group_dict)
	
	def get_by_keys(self, keys):
		if not keys:
			return(False, 'Not Keys!')
		elif keys.__class__.__name__ != 'dict':
			return(False, 'Wrong type of keys: %s' % keys.__class__.__name__)
		
		bool_, return_data = database().read('project', self.project, self.group_t, self.group_keys, where = keys, table_root=self.group_db)
		return(bool_, return_data)
	
	def get_by_name(self, name):
		rows = self.get_by_keys({'name': name})
		if rows[0] and rows[1]:
			return(True, rows[1][0])
		elif rows[0] and not rows[1]:
			return(False, 'This name(%s) not Found' % name)
		else:
			return(False, rows[1])
	
	def get_by_id(self, id_):
		rows = self.get_by_keys({'id': id_})
		if rows[0] and rows[1]:
			return(True, rows[1][0])
		elif rows[0] and not rows[1]:
			return(False, 'This id(%s) not Found' % id_)
		else:
			return(False, rows[1])
	
	def get_by_season(self, season):
		rows = self.get_by_keys({'season': season})
		if rows[0]:
			return(True, rows[1])
		else:
			return(False, rows[1])
	
	def get_by_type_list(self, type_list):
		data = []
		for type_ in type_list:
			rows = self.get_by_keys({'type':type_})
			if rows[0]:
				data = data + rows[1]
				
		return(True, data)
		
	def get_dict_by_all_types(self):
		# get all group data
		result = self.get_list()
		if not result[0]:
			return(False, result[1])
		
		# make data
		data = {}
		for group in result[1]:
			if not group['type'] in data.keys():
				c_data = []
			else:
				c_data = data[group['type']]
			c_data.append(group)
			data[group['type']] = c_data
			
		return(True, data)
	
	def rename(self, group_id, new_name):
		update_data = {'name': new_name}
		where = {'id': group_id}
		bool_, return_data = database().update('project', self.project, self.group_t, self.group_keys, update_data, where, table_root=self.group_db)
		if not bool_:
			return(bool_, return_data)
		
		return(True, 'ok')
		
	def edit_comment_by_name(self, name, comment):
		update_data = {'comment': comment}
		where = {'name': name}
		bool_, return_data = database().update('project', self.project, self.group_t, self.group_keys, update_data, where, table_root=self.group_db)
		if not bool_:
			return(bool_, return_data)
		return(True, 'ok')
		
class list_of_assets(studio):
	def __init__(self, group):
		self.group = group

	# rows (list) = [{keys}, {keys}, ...]
	def save_list(self, rows, group_name = False):
		list_of_assets_path = self.group.project.list_of_assets_path
		# test data keys
		if not group_name:
			if not self.group.name:
				return(False, 'No init of Group!')
			group_name = self.group.name
		
		if not self.group.project.name:
			return(False, 'No init of Project!')
		
		# test exists path
		if not os.path.exists(list_of_assets_path):
			try:
				with open(list_of_assets_path, 'w') as f:
					jsn = json.dump({}, f, sort_keys=True, indent=4)
					f.close()
			except:
				return(False, '"%s"  can not be write' % list_of_assets_path)
		
		# read data
		try:
			with open(list_of_assets_path, 'r') as read:
				data = json.load(read)
				read.close()
		
		except:
			return(False, '"%s"  can not be read' % list_of_assets_path)
		
		# edit data
		data[group_name] = rows
		
		# write data
		try:
			with open(list_of_assets_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				#print('data:', data)
				f.close()
		except:
			return(False, '"%s"  can not be write' % list_of_assets_path)
		
		return(True, 'ok')
		
	def get_list(self):
		list_of_assets_path = self.group.project.list_of_assets_path
		# test exists path
		if not os.path.exists(list_of_assets_path):
			return(True, [])
		
		# read data
		try:
			with open(list_of_assets_path, 'r') as read:
				data = json.load(read)
				read.close()
								
		except:
			return(False, '"%s" can not be read!' % list_of_assets_path)
			
		return(True, data)
		
	def get(self, group_name = False):
		list_of_assets_path = self.group.project.list_of_assets_path
		if not group_name:
			if not self.group.name:
				return(False, 'No init of group!')
			group_name = self.group.name
			
		# test exists path
		if not os.path.exists(list_of_assets_path):
			return(False, '"%s" Not Found!' % list_of_assets_path)
		
		# read data
		try:
			with open(list_of_assets_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, '"%s" can not be read!' % list_of_assets_path)
		
		if group_name in data:
			return(True, data[group_name])
		else:
			return(False, 'list of assets for "%s" not found!' % group_name)
		
		
	def remove(self, group_name = False):
		list_of_assets_path = self.group.project.list_of_assets_path
		if not group_name:
			if not self.group.name:
				return(False, 'No init of group!')
			group_name = self.group.name
		
		# test exists path
		if not os.path.exists(list_of_assets_path):
			return(False, '"%s" Not Found!' % list_of_assets_path)
			
		# read data
		try:
			with open(list_of_assets_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, '"%s" can not be read!' % list_of_assets_path)
			
		if group_name in data:
			del data[group_name]
		else:
			return(False, 'list of assets for "%s" not found!' % group_name)
			
		# write data
		try:
			with open(list_of_assets_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				#print('data:', data)
				f.close()
		except:
			return(False, '"%s"  can not be write' % list_of_assets_path)
			
		return(True, 'Ok')
		
		
	def create_assets(self, project, group):
		pass
	
