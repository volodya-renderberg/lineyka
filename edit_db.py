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
import uuid
import tempfile

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

def print_args(fn):
	def inner_fn(*args):
		print(args)
		return fn(*args)
	return(inner_fn)
	
class studio:
	'''
	@classmethod get_studio()
	@classmethod make_init_file()
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
		},
	'task__visible_fields':[
		'activity',
		'task_type',
		'artist',
		'priority',
		'extension',
		]
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
	'description': 'text',
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
	#'asset_path': 'text', # каждый раз определяется при считывании данных. ## больше не нужен это task.asset.path
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
	
	# activity, task_name, action, date_time, description, version, artist
	'''
	logs_keys = [
	('activity', 'text'),
	('task_name', 'text'),
	('action', 'text'),
	('date_time', 'timestamp'),
	('description', 'text'),
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
	chats_keys = {
	'message_id':'text',
	'date_time': 'timestamp',
	'date_time_of_edit': 'timestamp',
	'author': 'text',
	'topic': 'text',
	'color': 'text',
	'status': 'text',
	'reading_status': 'text',
	}
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
	'path': 'text',
	'status': 'text',
	'project_database': 'json',
	'chat_img_path': 'text',
	'list_of_assets_path': 'text',
	'preview_img_path': 'text',
	}
	
	group_keys = {
	'name': 'text',
	'type': 'text',
	'season': 'text',
	'description': 'text',
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
	
	logs_keys = {
	'version': 'text',
	'date_time': 'timestamp',
	'activity': 'text',
	'task_name': 'text',
	'action': 'text',
	'artist': 'text',
	'description': 'text',
	}
	
	init_folder = '.lineyka'
	init_file = 'lineyka_init.json'
	set_file = 'user_setting.json'
	#projects_file = '.projects.json'
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
	# --- set_of_tasks
	set_of_tasks_db = '.set_of_tasks.db'
	set_of_tasks_t = 'set_of_tasks'
	
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
				'tmp_folder': tempfile.gettempdir(),
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
			
		#print('artist path: ', self.artists_path)
			
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
		return True, [self.studio_folder, self.tmp_folder]
	
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
			# create table
			bool_, r_data = self.__sqlite3_create_table(level, read_ob, table_name, keys, table_root)
			if not bool_:
				return(bool_, r_data)
			# write
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
			b, r = self.__sqlite3_read(level, read_ob, table_name, keys, columns, where, table_root)
			return(b, r)
	
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
		
	# удаление строки из таблицы БД
	# where - словарь по ключам, так как значения маскируются под "?" не может быть None или False
	# table_root - может быть как именем таблицы - например: assets, так и именем файла - .assets.db
	def delete(self, level, read_ob, table_name, where, table_root=False):
		attr = self.use_db_attr.get(level)
		if not attr:
			raise Exception('database.update()', 'Unknown Level : %s' % level)
		
		db_name, db_data = eval('read_ob.%s' % attr)
		#return(db_name, db_data)
		
		if db_name == 'sqlite3':
			return_data = self.__sqlite3_delete(level, read_ob, table_name, where, table_root)
			return(return_data)
	
	### SQLITE3
	# table_root - может быть как именем таблицы - например: assets, так и именем файла - .assets.db
	#@print_args
	def __get_db_path(self, level, read_ob, table_name, table_root):
		attr = self.sqlite3_db_folder_attr.get(level)
		db_folder = getattr(read_ob, attr)
		if not db_folder:
			return(None)
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
		if not db_path:
			return(False, 'No path to database!')
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
	
	# where - словарь по ключам, так как значения маскируются под "?" не может быть None или False
	def __sqlite3_delete(self, level, read_ob, table_name, where, table_root):
		data_com = []
		
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
		com = 'DELETE FROM %s WHERE %s' % (table_name, where_data)
		
		# connect
		# -- db_path
		db_path = self.__get_db_path(level, read_ob, table_name, table_root)
		if not db_path:
			return(False, 'No path to database!')
		# -- connect
		conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		# -- com
		try:
			c.execute(com, data_com)
		except Exception as e:
			print('#'*3, 'Exception in database.__sqlite3_delete:')
			print('#'*3, 'com:', com)
			print('#'*3, 'data_com:', data_com)
			print('#'*3, e)
			conn.close()
			return(False, 'Exception in database.__sqlite3_delete, please look the terminal!')
		conn.commit()
		conn.close()
		return(True, 'Ok!')
	
	# where - 1) строка условия, 2) словарь по keys, 3) False - значит выделяется всё.
	# columns - False - означает все столбцы если не False - то список столбцов.
	#@print_args
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
		if not db_path:
			return(False, 'No path to database!')
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
			'''
			#test_com = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % table_name
			#c.execute(test_com)
			c.execute("SELECT rowid FROM components WHERE name = '?'", (table_name,))
			if c.fetchone():
				c.execute(com)
			'''
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
		if not db_path:
			return(False, 'No path to database!')
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
		if not db_path:
			return(False, 'No path to database!')
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
		if not db_path:
			return(False, 'No path to database!')
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
	list_active_projects = []
	list_projects = []
	dict_projects = {}
	
	def __init__(self):
		pass
		#base fields
		for key in self.projects_keys:
			exec('self.%s = False' % key)
			
		# constans
		self.folders = {'assets':'assets', 'chat_img_folder':'.chat_images', 'preview_images': '.preview_images'}
		
	# if new=True - возвращает новый инициализированный объект, если False то инициализирует текущий объект и возвращает (True, 'Ok')
	def init(self, name, new=True): # v2
		pass
		b, r = database().read('studio', self, self.projects_t, self.projects_keys, table_root=self.projects_db)
		if not b:
			return(b, r)
		
		for data in r:
			if data['name'] == name:
				return(self.init_by_keys(data, new=new))
		if new:
			return(None)
		else:
			return(False, 'Project with the same name "%s" does not exist!' % name)
        
	def init_by_keys(self, keys, new=True): # v2
		if new:
			r_ob = project()
		else:
			r_ob = self
		
		for key in self.projects_keys:
			setattr(r_ob, key, keys[key])
			
		if new:
			return r_ob
		else:
			return(True, 'Ok!')
        

	def add_project(self, name, path): # v2
		project_path = NormPath(path)
		# test by name
		self.get_list()
		if name in self.dict_projects.keys():
			return(False, "This project name already exists!")
		
		# project_name, get project_path
		if not project_path and name == '':
			return(False, 'No options!')
			
		elif not project_path:
			project_path = os.path.join(self.studio_folder, name)
			try:
				os.mkdir(project_path)
			except:
				return(False, ('Failed to create folder: ' + project_path))
			
		elif name == '':
			if not os.path.exists(project_path):
				return(False, ('Project Path: \"%s\" Not Found!' % project_path))
			name = os.path.basename(project_path)
			
		self.name = name
		path = project_path
			
		if not os.path.exists(path):
			text = '****** studio.project.add_project() -> %s not found' % path
			return False, text
		else:
			self.path = path
		
		self.project_database = ['sqlite3', False] # новый проект в начале всегда sqlite3, чтобы сработало всё в database
		self.list_of_assets_path = NormPath(os.path.join(self.path, '.list_of_assets_path.json'))
		
		# create folders
		self.__make_folders(self.path)
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
		# -- write data
		write_data = {}
		for key in self.projects_keys:
			write_data[key] = eval('self.%s' % key)
		#print('#'*3, write_data)
		bool_, return_data = database().insert('studio', self, self.projects_t, self.projects_keys, write_data)
		if not bool_:
			return(bool_, return_data)
		
		# create_recycle_bin
		
		result = group(self).create_recycle_bin()
		if not result[0]:
			return(False, result[1])
		#
		return True, 'ok'
		
	# заполняет поля класса list_active_projects, list_projects, dict_projects.
	def get_list(self): # v2
		pass
		b, r = database().read('studio', self, self.projects_t, self.projects_keys)
		if not b:
			return(b,r)
		
		list_active_projects = [] # имена активных проектов
		list_projects = [] # все проекты (объекты)
		dict_projects = {} # все проекты (объекты) по именам.
		
		for item in r:
			ob = self.init_by_keys(item)
			list_projects.append(ob)
			dict_projects[ob.name] = ob
			if ob.status == 'active':
				list_active_projects.append(ob.name)
		
		self.__fill_class_fields(list_active_projects, list_projects, dict_projects)
		return(True, list_projects)
	
	@classmethod
	def __fill_class_fields(self, list_active_projects, list_projects, dict_projects):
		self.list_active_projects = list_active_projects
		self.list_projects = list_projects
		self.dict_projects = dict_projects
	
	# переименование проекта, перезагружает studio.list_projects
	# объект должен быть инициализирован
	def rename_project(self, new_name): # v2
		pass
		if not new_name:
			return(False, 'Not Name!')
		ud = {'name': new_name}
		wh = {'name': self.name}
		bool_, rdata = database().update('studio', self, self.projects_t, self.projects_keys, update_data=ud, where=wh, table_root=self.projects_db)
		if not bool_:
			return(bool_, rdata)
		
		self.name = new_name
		#		
		return(True, 'Ok!')
		
	# удаляет проект из БД, перезагружает studio.list_projects, приводит объектк empty.
	# объект должен быть инициализирован
	def remove_project(self): # v2
		pass
		# edit DB
		wh = {'name': self.name}
		bool_, return_data = database().delete('studio', self, self.projects_t, where=wh, table_root=self.projects_db)
		
		# to empty
		for key in self.projects_keys:
			setattr(self, key, False)
		#
		return(True, 'Ok!')
		
	# меняет статус проекта
	# объект должен быть инициализирован
	def edit_status(self, status): # v2
		pass
		# database
		ud = {'status': status}
		wh = {'name': self.name}
		bool_, return_data = database().update('studio', self, self.projects_t, self.projects_keys, update_data=ud, where=wh, table_root=self.projects_db)
		if not bool_:
			return(bool_, return_data)
		
		self.status = status
		#
		return(True, 'Ok')
		
	def __make_folders(self, root): # v2
		for f in self.folders:
			path = os.path.join(root, self.folders[f])
			if not os.path.exists(path):
				os.mkdir(path)
				#print '\n****** Created'
			else:
				return False, '\n****** studio.project.make_folders -> No Created'
	
class asset(studio):
	'''
	https://sites.google.com/site/lineykadoc/home/doc/edit-database/class-studio-project-asset
	'''
	
	def __init__(self, project_ob):
		if not isinstance(project_ob, project):
			raise Exception('in asset.__init__() - Object is not the right type "%s", must be "project"' % project_ob.__class__.__name__)
		# objects
		self.project = project_ob
		
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

	# инициализация по имени
	# заполнение полей по self.asset_keys
	# asset_name (str) - имя ассета. данные ассета будут считаны из базы данных.
	# new (bool) - если True - то возвращается новый инициализированный объект класса asset, если False - то инициализируется текущий объект
	def init(self, asset_name, new = True):
		pass
		# 1 - чтение БД
		where = {'name': asset_name}
		asset_data = False
		for asset_type in self.asset_types:
			b, r = database().read('project', self.project, asset_type, self.asset_keys, where=where, table_root=self.assets_db)
			if not b:
				print(r)
				continue
			if r:
				asset_data = r[0]
		if not asset_data:
			return(False, 'An asset with that name(%s) was not found!' % asset_name)
				
		if new:
			new_asset = asset(self.project)
			for key in self.asset_keys:
				#exec('new_asset.%s = keys.get("%s")' % (key, key))
				setattr(new_asset, key, asset_data.get(key))
			# path
			new_asset.path = NormPath(os.path.join(self.project.path, self.project.folders['assets'],asset_data['type'], asset_data['name']))
			return new_asset
		else:
			for key in self.asset_keys:
				#exec('self.%s = keys.get("%s")' % (key, key))
				setattr(self, key, asset_data.get(key))
			# path
			self.path = NormPath(os.path.join(self.project.path, self.project.folders['assets'],asset_data['type'], asset_data['name']))
			return(True, 'Ok!')
		
	# инициализация по словарю ассета
	# заполнение полей по self.asset_keys
	# new (bool) - если True - то возвращается новый инициализированный объект класса asset, если False - то инициализируется текущий объект
	def init_by_keys(self, keys, new = True):
		if new:
			new_asset = asset(self.project)
			for key in self.asset_keys:
				exec('new_asset.%s = keys.get("%s")' % (key, key))
			# path
			new_asset.path = NormPath(os.path.join(self.project.path, self.project.folders['assets'],keys['type'], keys['name']))
			return new_asset
		else:
			for key in self.asset_keys:
				exec('self.%s = keys.get("%s")' % (key, key))
			# path
			self.path = NormPath(os.path.join(self.project.path, self.project.folders['assets'],keys['type'], keys['name']))
			return(True, 'Ok!')
		
	# list_keys (list) - список словарей по ключам asset_keys
	# -- обязательные параметры в keys (list_keys): name, group(id).
	# asset_type (str) - тип для всех ассетов
	def create(self, asset_type, list_keys):  # v2
		pass
		# 1 - проверка типа ассета
		# 2 - проверка типа list_keys
		# 3 - список ассетов данного типа для проверки наличия
		# 4 - создание таблицы если нет
		# 5 - проверка на совпадение имени ассета
		# 6 - создание ассетов - проверки:
		# --6.1 - наличие name, group(id), season
		# --6.2 - изменение имени
		# --6.3 - добавление значений (type, status, priority) в словарь ассета
		# --6.4 - создание id с проверкой на совпадение.
		# --6.5 - создание директорий
		# --6.6 - создание ассета в БД
		
		# (1) test valid asset_type
		if not asset_type in self.asset_types:
			return(False, 'Asset_Type (%s) is Not Valid!' % asset_type)
		# (2) test valid type of list_keys
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
				assets.append(row.name)
				ids.append(row.id)
		else:
			print('#'*5)
			print(result[1])
			
		# (4) cteate table
		bool_, return_data = database().create_table('project', self.project, asset_type, self.asset_keys, table_root = self.assets_db)
		if not bool_:
			return(bool_, return_data)
		
		#
		if not list_keys:
			return(False, 'No data to create an Asset!')
		# (5) test exists name
		for keys in list_keys:
			if keys['name'] in assets:
				return(False, 'The name "%s" already exists!' % keys['name'])
		# (6) create assets
		for keys in list_keys:
			# (6.1)
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
			# (6.2) edit name
			if asset_type in ['shot_animation']:
				keys['name'] = keys['name'].replace(' ', '_')
			else:
				keys['name'] = keys['name'].replace(' ', '_').replace('.', '_')
			# (6.3) make keys
			keys['type'] = asset_type
			keys['status'] = 'active'
			if not keys.get('priority'):
				keys['priority'] = 0
			
			# (6.4) get id
			keys['id'] = hex(random.randint(0, 1000000000)).replace('0x','')
			while keys['id'] in ids:
				keys['id'] = hex(random.randint(0, 1000000000)).replace('0x','')

			# (6.5) create Folders
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
			
			# (6.6) create in DB init
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
				print('**** by set of tasks: %s' % keys.get('set_of_tasks'))
				set_tasks = result[1].sets
				
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
			else:
				print('**** without sets')
			
			# set input of "final"
			final_input = []
			for task_ in this_asset_tasks:
				final_input.append(task_['task_name'])
			#final['input'] = json.dumps(final_input)
			final['input'] = final_input
			
			# append final to task list
			this_asset_tasks.append(final)
			
			#print(this_asset_tasks)
			
			########### create tasks (by task data)
			#c = json.dumps(this_asset_tasks, sort_keys=True, indent=4)
			#print(c)
			new_asset = self.init_by_keys(keys)
			result = task(new_asset).create_tasks_from_list(this_asset_tasks)
			if not result[0]:
				return(False, result[1])
			
			########### make return data
			# path
			keys['path'] = NormPath(os.path.join(self.project.path, self.project.folders['assets'],keys['type'], keys['name']))
			#
			make_assets[keys['name']] = keys
		
		return(True, make_assets)
	
	# удаление текущего ассета
	# asset_data (dict) - словарь по asset_keys
	def remove(self): # v2
		pass
		# 1 - получение id recycle_bin
		# 2 - замена группы ассета на recycle_bin, обнуление priority, status.
		# 3 - список задач ассета
		# 4 - перезапись задачь ассета, обнуление: status, artist, readers, priority.
		# 5 - разрывы исходящих связей в другие ассеты.
		
		# (1)
		# -- get recycle bin  data
		result = group(self.project).get_by_keys({'type': 'recycle_bin'})
		if not result[0]:
			return(False, ('in asset().remove' + result[1]))
		recycle_bin = result[1][0]
		
		# (2)
		update_data = {'group': recycle_bin.id, 'priority': 0, 'status':'none'}
		where = {'id': self.id}
		bool_, return_data = database().update('project', self.project, self.type, self.asset_keys, update_data, where, table_root=self.assets_db)
		if not bool_:
			return(bool_, return_data)
				
		# (3)
		bool_, task_list = task(self).get_list()
		if not bool_:
			return(bool_, task_list)
		
		output_tasks = []
		output_tasks_name_list = []
		table = '"%s:%s"' % (self.id, self.tasks_t)
		# (4)
		for row in task_list:
			if row.task_type == 'service':
				continue
			if row.output:
				for task_name in row.output:
					if task_name.split(':')[0] != row.asset_name:
						output_tasks.append((row, task_name))
						output_tasks_name_list.append(task_name)
			# -- -- get status
			new_status = 'null'
			if not row.input:
				new_status = 'ready'
			
			update_data = {'artist':'', 'status': new_status, 'readers': [], 'priority':0}
			where = {'task_name': row.task_name}
			bool_, r_data = database().update('project', self.project, table, self.tasks_keys, update_data, where, table_root=self.tasks_db)
			if not bool_:
				bool_, r_data
		
		# (5)
		# ******** DISCONNECT OUTPUTS
		# -- get output tasks dict
		result = task(self).get_tasks_by_name_list(output_tasks_name_list)
		if not result[0]:
			return(False, ('in asset().remove - %s' % result[1]))
		output_tasks_data_dict = result[1]
		
		for key in output_tasks:
			if not key[1]:
				continue
			if output_tasks_data_dict[key[1]].task_type == 'service':
				b,r = output_tasks_data_dict[key[1]].service_remove_task_from_input([key[0]])
				if not b:
					return(b,r)
			else:
				print((output_tasks_data_dict[key[1]].task_name + ' not service!'))
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
		if not new_asset_name:
			return(False, 'New asset name is not specified!')
		elif not new_group_name:
			return(False, 'New group name is not specified!')
		elif not new_asset_type:
			return(False, 'New type of asset is not specified!')
		elif not set_of_tasks:
			return(False, '"Set of tasks" is not specified!')
		
		#
		if new_asset_type in ['shot_animation']:
			new_asset_name = new_asset_name.replace(' ', '_')
		else:
			new_asset_name = new_asset_name.replace(' ', '_').replace('.', '_')
		
		# (2) get group id
		result = group(self.project).get_by_name(new_group_name)
		if not result[0]:
			return(False, result[1])
		new_group_id = result[1].id
		
		# (3)
		if not data_of_source_asset:
			data_of_source_asset={}
			asset_list_keys = list(self.asset_keys.keys()) + ['path']
			for key in asset_list_keys:
				if key in dir(self):
					data_of_source_asset[key] = getattr(self, key)
				else:
					data_of_source_asset[key] = None
					
		print(data_of_source_asset)
		#return
		
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
	
	# возвращает список ассетов по типам
	# asset_type (str) - тип ассета, если False, то возвращает список ассетов по всем типам.
	# return - (True, [objects]) или (False, comment)
	def get_list_by_type(self, asset_type=False): # v2
		pass
		#
		
		where = False
		assets_list = []
		r_data = []
		if not asset_type:
			for asset_type in self.asset_types:
				b, r = database().read('project', self.project, asset_type, self.asset_keys, where = where, table_root=self.assets_db)
				if not b:
					print('#'*5, r)
					continue
				else:
					assets_list = assets_list + r
		else:
			b, r = database().read('project', self.project, asset_type, self.asset_keys, where = where, table_root=self.assets_db)
			if not b:
				print('#'*5, r)
				return(True, [])
			else:
				assets_list = r
				
		for asset in assets_list:
			r_data.append(self.init_by_keys(asset))
		return(True, r_data)
	
	# обёртка на get_list_by_type()
	# return - (True, [objects]) или (False, comment)
	def get_list_by_all_types(self): # v2
		b, r = self.get_list_by_type()
		return(b, r)
	
	# group (group) - объект группы
	# return - (True, [objects]) или (False, comment)
	def get_list_by_group(self, group_ob): # v2
		pass
		# 1 - тест типа переменной group
		# 2 - чтение БД
		
		# (1)
		if not isinstance(group_ob, group):
			return(False, 'asset.get_list_by_group(): the data type of the variable passed to this procedure must be a "group", passed type: "%s"' % group_ob.__class__.__name__)
		
		# (2)
		assets = []
		where = {'group': group_ob.id}
		if group_ob.type == 'recycle_bin':
			for asset_type in self.asset_types:
				b, r = database().read('project', group_ob.project, asset_type, self.asset_keys, where = where, table_root=self.assets_db)
				if not b:
					print('#'*5, r)
					continue
				else:
					assets = assets + r
		else:
			bool_, assets = database().read('project', group_ob.project, group_ob.type, self.asset_keys, where = where, table_root=self.assets_db)
			if not bool_:
				print('#'*5, assets)
				return(True, [])
		
		r_data = []
		for asset in assets:
			#asset['path'] = NormPath(os.path.join(self.project.path, self.project.folders['assets'],asset['type'], asset['name']))
			r_data.append(self.init_by_keys(asset))
		return(True, r_data)

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
		
			
	def get_dict_by_name_by_all_types(self): # v2
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
			assets_dict[asset['name']] = self.init_by_keys(asset)
		return(True, assets_dict)
			
	def get_by_id(self, asset_id): # v2
		where = {'id': asset_id}
		asset_data = False
		for asset_type in self.asset_types:
			bool_, return_data = database().read('project', self.project, asset_type, self.asset_keys, where=where, table_root=self.assets_db)
			if not bool_:
				print(return_data)
				continue
			if return_data:
				asset_data = return_data[0]
				asset_data['path'] = NormPath(os.path.join(self.project.path, self.project.folders['assets'],asset_data['type'], asset_data['name']))
				return(True, asset_data)
		if not asset_data:
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
		
	# ассет должен быть инициализирован
	# group_id (str) - id группы
	def change_group(self, group_id): # v2
		where = {'name': self.name}
		keys={'group': group_id}
		
		# update
		table_name = self.type
		b, r = database().update('project', self.project, table_name, self.asset_keys, keys, where, table_root=self.assets_db)
		if not b:
			return(b, r)
		
		self.group = group_id
		return(True, 'Ok!')

	# ассет должен быть инициализирован
	# priority (int) - новый приоритет
	def change_priority(self, priority):
		pass
		where = {'name': self.name}
		keys={'priority': priority}
		
		# update
		table_name = self.type
		b, r = database().update('project', self.project, table_name, self.asset_keys, keys, where, table_root=self.assets_db)
		if not b:
			return(b, r)
		
		self.priority = priority
		return(True, 'Ok!')
	
	# ассет должен быть инициализирован
	# description (str) - новое описание
	def change_description(self, description):
		pass
		where = {'name': self.name}
		keys={'description': description}
		
		# update
		table_name = self.type
		b, r = database().update('project', self.project, table_name, self.asset_keys, keys, where, table_root=self.assets_db)
		if not b:
			return(b, r)
		
		self.description = description
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
	'''
	
	def __init__(self, asset_ob):
		if not isinstance(asset_ob, asset):
			raise Exception('in task.__init__() - Object is not the right type "%s", must be "asset"' % asset_ob.__class__.__name__)
		self.asset = asset_ob
		
		for key in self.tasks_keys:
			setattr(self, key, False)
		
		self.VARIABLE_STATUSES = ('ready', 'ready_to_send', 'work', 'work_to_outsorce')
		
		self.CHANGE_BY_OUTSOURCE_STATUSES = {
		'to_outsource':{'ready':'ready_to_send', 'work':'ready_to_send'},
		'to_studio':{'ready_to_send':'ready', 'work_to_outsorce':'ready'},
		}
		
		#self.db_workroom = workroom() # ??????? как всегда под вопросом
		#self.publish = lineyka_publish.publish()
		
		self.publish = publish(self, NormPath) # ??????? как всегда под вопросом
		
	# инициализация по имени
	# new (bool) - если True - то возвращается новый инициализированный объект класса task, если False - то инициализируется текущий объект
	def init(self, task_name, new = True):
		pass
		# get keys
		bool_, task_ob = self.__read_task(task_name)
		if not bool_:
			return(bool_, task_ob)
				
		# fill fields
		if new:
			return task_ob
		else:
			for key in self.tasks_keys:
				setattr(self, key, getattr(task_ob, key))
			self.asset=task_ob.asset
			return(True, 'Ok')
		
	# инициализация по словарю
	# new (bool) - если True - то возвращается новый инициализированный объект класса task, если False - то инициализируется текущий объект
	def init_by_keys(self, keys, new = True):
		if new:
			new_task = task(self.asset)
			for key in self.tasks_keys:
				setattr(new_task, key, keys.get(key))
			return new_task
		else:
			for key in self.tasks_keys:
				setattr(self, key, keys.get(key))
			return(True, 'Ok')
		
	# ************************ CHANGE STATUS ******************************** start
	
	@staticmethod
	def _input_to_end(task_ob): # v2
		if task_ob.status == 'close':
			return(False)
		
		autsource = bool(task_ob.outsource)
				
		if autsource:
			return('ready_to_send')
		else:
			return('ready')
	
	# изменение статуса сервис задачи, по проверке статусов входящих задачь.
	# задача должна быть инициализирована
	# assets (dict) - словарь всех ассетов по всем типам (ключи - имена, данные - ассеты (объекты)) - результат функции asset.get_dict_by_name_by_all_types()
	def service_input_to_end(self, assets): # v2 *** не тестилось.
		new_status = False
		
		# (1) get input_list
		input_list = self.input
		if not input_list:
			return(True, new_status)
		
		# get status
		bool_statuses = []
		# --------------- fill end_statuses -------------
		for task_name in input_list:
			# (2) asse id
			asset_name = task_name.split(':')[0]
			asset_ob = assets.get(asset_name)
			if not asset_ob:
				print('in task.service_input_to_end() incorrect asset_name  "%s"' % asset_name)
				continue
			# (3) get task data
			task_ob = task(asset_ob).init(task_name)
			
			# (4) make status
			if task_ob.status in self.end_statuses:
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
	
	# возвращает новый статус текущей задачи (если this_task=False), на основе входящей задачи.
	# input_task (task / False) входящая задача.
	# this_task (task / False) - если False - то предполагается текущая задача.
	def from_input_status(self, input_task, this_task=False):  # v2 no test
		pass
		if not this_task:
			this_task=self
		# get task_outsource
		task_outsource = bool(this_task.outsource)
		
		new_status = None
		# change status
		if input_task:
			if input_task.status in self.end_statuses:
				if not task_outsource:
					if this_task.status == 'null':
						new_status = 'ready'
				else:
					if this_task.status == 'null':
						new_status = 'ready_to_send'
			else:
				if this_task.status != 'close':
					new_status = 'null'
		else:
			if not this_task.status in self.end_statuses:
				if task_outsource:
					new_status = 'ready_to_send'
				else:
					new_status = 'ready'
		return(new_status)
		
	# замена статусов исходящих задачь при изменении статуса текущей задачи с done или с close.
	# this_task (task / False) - если False то текущая задача.
	# assets (dict) - словарь всех ассетов по всем типам (ключи - имена, данные - ассеты (объекты)) - результат функции asset.get_dict_by_name_by_all_types()
	def this_change_from_end(self, this_task=False, assets = False): # v2 *** no test
		pass
		# 0 - задаём объект текущей задачи
		# 1 - список исходящих задачь
		# 2 - получение списка всех ассетов
		# 3 - цикл по списку исходящих задачь (output_list)
		# - 4 - получение ассета
		# - 5 - чтение таска
		# - 6 - определение нового статуса
		# - 7 - изменения в readers
		# - 8 - запись таск
		# 9 - отправка далее в себя же - this_change_from_end() - по списку from_end_list
		
		# (0)
		if not this_task:
			this_task=self
		
		#
		from_end_list = []
		this_asset_type = this_task.asset_type
		
		# (1)
		output_list = this_task.output
		if not output_list:
			return(True, 'Ok!')
		# (2)
		if not assets:
			# get assets dict
			result = self.asset.get_dict_by_name_by_all_types()
			if not result[0]:
				return(False, result[1])
			assets = result[1]
		
		# (3) ****** change status
		for task_name in output_list:
			# (4)
			asset_name = task_name.split(':')[0]
			asset_ob = assets.get(asset_name)
			if not asset_ob:
				print('in task.this_change_from_end() incorrect asset_name  "%s"' % asset_name)
				continue
			# (5) get task data
			task_ob = task(asset_ob).init(task_name)
			
			# (6) make new status char и obj не отключают локацию и аним шот, а локация отключает аним шот. ??????
			if task_ob.status == 'close':
				continue
			elif task_ob.asset_type in ['location', 'shot_animation'] and this_asset_type not in ['location', 'shot_animation']:
				continue
			elif task_ob.status == 'done':
				from_end_list.append(task_ob)
				
			new_status = 'null'
			# (7) edit readers
			readers = {}
			try:
				readers = task_ob.readers
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
			table_name = '"%s:%s"' % (task_ob.asset.id, self.tasks_t)
			where = {'task_name': task_name}
			bool_, return_data = database().update('project', task_ob.asset.project, table_name, self.tasks_keys, update_data, where, table_root=self.tasks_db)
			if not bool_:
				return(bool_, return_data)
		'''
		conn.commit()
		conn.close()
		'''
		
		# (9) ****** edit from_end_list
		if from_end_list:
			for t_ob in from_end_list:
				t_ob.this_change_from_end(assets = assets)
		
		
		return(True, 'Ok!')
		
	# замена статусов исходящих задачь при изменении статуса текущей задачи на done или close.
	# task_data (dict/task) - текущая задача.
	# assets (dict) - словарь всех ассетов по всем типам (ключи - имена, данные - ассеты (словари)) - результат функции asset.get_dict_by_name_by_all_types()
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
		if isinstance(task_data, dict):
			output_list = task_data.get('output')
		elif isinstance(task_data, task):
			output_list = task_data.output
		if not output_list:
			return(True, 'Ok!')
		# (2)
		if not assets:
			# get assets dict
			result = self.asset.get_dict_by_name_by_all_types()
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
			asset_id = assets[task_name.split(':')[0]].id
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
				task_data_ = self.init_by_keys(return_data[0])
			else:
				return(False, 'Task Data Not Found! Task_name - "%s"' % task_name)
            
			# (6) make new status
			if task_data_.task_type == 'service':
				#result = self.service_input_to_end(task_data_, assets)
				result = task_data_.service_input_to_end(assets)
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
		result = self.get_dict_by_name_by_all_types(project_name)
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
			
			final_file = NormPath(os.path.join(activity_path, hex_num, '%s%s' % (asset, extension)))
			if os.path.exists(final_file):
				return(True, final_file, asset_path)
			i = i-1
		
		return(True, None, asset_path)
	
	# asset - должен быит инициализирован
	# task_data (dict) - требуется если не инициализирован task
	# version (str) - hex 4 символа
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
	# ob_name (str) - имя 3d объекта
	# activity (str) - по умолчанию cache (для blender) - для других программ может быть другим, например "maya_cache"
	# extension (str) - расширение файла кеша.
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	def get_versions_list_of_cache_by_object(self, ob_name, activity = 'cache', extension = '.pc2', task_data=False): # v2 *** без тестов
		pass
		# 1 - получение task_data
		# (1)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.%s' % (key, key))
		
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
		
	# cache_dir_name (str) - "asset_name + '_' + ob_name"
	# activity (str) - по умолчанию cache (для blender) - для других программ может быть другим, например "maya_cache"
	# extension (str) - расширение файла кеша.
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	def get_final_cache_file_path(self, cache_dir_name, activity = 'cache', extension = '.pc2', task_data=False): # v2 *** без тестов
		pass
		# 1 - получение task_data
		# (1)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.%s' % (key, key))
		
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
			
			final_file = NormPath(os.path.join(cache_dir_path, hex_num, (cache_dir_name + extension)))
			if os.path.exists(final_file):
				return(True, final_file)
			i = i-1
		
		return(False, 'No Found Chache! *2')
		
	# cache_dir_name (str) - "asset_name + '_' + ob_name"
	# activity (str) - по умолчанию cache (для blender) - для других программ может быть другим, например "maya_cache"
	# extension (str) - расширение файла кеша.
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	def get_new_cache_file_path(self, cache_dir_name, activity = 'cache', extension = '.pc2', task_data=False): # v2 *** без тестов
		pass
		# 1 - получение task_data
		# (1)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.%s' % (key, key))
		
		# get final file
		result = self.get_final_cache_file_path(cache_dir_name, activity = activity, extension = extension, task_data=task_data)
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
			new_dir_path = NormPath(os.path.join(activity_path, '0000'))
			new_file_path = NormPath(os.path.join(new_dir_path, (cache_dir_name + extension)))
			
		else:
			ff_split = final_file.replace('\\','/').split('/')
			new_num_dec = int(ff_split[len(ff_split) - 2], 16) + 1
			new_num_hex = hex(new_num_dec).replace('0x', '')
			if len(new_num_hex)<4:
				for i in range(0, (4 - len(new_num_hex))):
					new_num_hex = '0' + new_num_hex
			
			new_dir_path = NormPath(os.path.join(activity_path, new_num_hex))
			new_file_path = NormPath(os.path.join(new_dir_path, (cache_dir_name + extension)))
		
		
		# make version dir
		if not os.path.exists(new_dir_path):
			os.mkdir(new_dir_path)
		
				 
		return(True, (new_dir_path, new_file_path))
		
	# version (str) - hex 4 символа
	# cache_dir_name (str) - "asset_name + '_' + ob_name"
	# activity (str) - по умолчанию cache (для blender) - для других программ может быть другим, например "maya_cache"
	# extension (str) - расширение файла кеша.
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	def get_version_cache_file_path(self, version, cache_dir_name, activity = 'cache', extension = '.pc2', task_data=False): # v2 *** без тестов
		pass
		# 1 - получение task_data
		# (1)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.%s' % (key, key))
		
		asset_path = task_data['asset_path']
		
		folder_name = self.ACTIVITY_FOLDER[task_data['asset_type']][activity]
		activity_path = NormPath(os.path.join(asset_path, folder_name, cache_dir_name))
		
		version_file = NormPath(os.path.join(activity_path, version, (cache_dir_name + extension)))
		
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
				input_task_data = self.__read_task(project_name, task_key_data['input'], ('status',))
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
		input_task_data = self.__read_task(project_name, input_task_name, ['status'])
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
					data_from_input_task = self.__read_task(project_name, task_key_data['input'], ('status',))
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
	def __read_task(self, project_name, task_name, keys):
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
	# list_of_tasks (list) - список задачь (словари по tasks_keys).
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
			task_keys['asset_path'] = ''
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
	def add_single_task(self, task_data): # asset_id=False # v2
		pass
		# 0 - проверка обязательных полей.
		# 1 - проверка уникальности имени.
		# 2 - назначение данных из ассета.
		# 3 - создание задачи. insert
		# 4 - внесение данной задачи в список output входящей задачи. change_input()
		# 5 - внесение данной задачи в список input исходящей задачи. change_input()
		
		# (0) required fields
		for field in ['activity','task_name','task_type', 'extension']:
			if not task_data.get('%s' % field):
				return(False, 'Not specified the "%s"!' % field)
			
		# (1)
		for td in self.get_list()[1]:
			if td['task_name'] == task_data['task_name']:
				return(False, 'Task with this name: "%s" already exists!' % task_data['task_name'])
			
		# (2)
		# -- priority
		if not task_data.get('priority'):
			task_data['priority'] = self.asset.priority
		# -- output
		output_task_name = False
		if task_data.get('output'):
			output_task_name = task_data.get('output')
			task_data['output'] = ['%s:final' % self.asset.name]
		# -- input
		input_task_name = False
		if task_data.get('input'):
			input_task_name = task_data.get('input')
			task_data['input']= ''
		else:
			task_data['input'] = ''
		#
		#other_fields = [
			#'artist',
			#'planned_time',
			#'time',
			#'supervisor',
			#'price',
			#'tz',
			#]
		#
		task_data['status'] = 'ready'
		task_data['outsource'] = 0
		task_data['season'] = self.asset.season
		task_data['asset_name'] = self.asset.name
		task_data['asset_id'] = self.asset.id
		task_data['asset_type'] = self.asset.type
		
		# (3)
		table_name = '"%s:%s"' % ( self.asset.id, self.tasks_t)
		bool_, return_data = database().insert('project', self.asset.project, table_name, self.tasks_keys, task_data, table_root=self.tasks_db)
		if not bool_:
			return(bool_, return_data)
		
		# (4)
		if input_task_name:
			bool_, return_data = self.change_input(input_task_name, task_data)
			if not bool_:
				return(bool_, return_data)
		
		# (5)
		if output_task_name:
			bool_, output_task_data = self.__read_task(output_task_name)
			if not bool_:
				return(bool_, return_data)
			# --
			bool_, return_data = self.change_input(task_data['task_name'], output_task_data)
			if not bool_:
				return(bool_, return_data)
		
		'''
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
		'''
				
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
		
		tasks_ob = []
		for td in return_data:
			td['asset_path'] = self.asset.path
			tasks_ob.append(self.init_by_keys(td))
		
		return(True, tasks_ob)
		
	# возвращает задачи (словари) по списку имён задачь, из различных ассетов.
	# self.asset.project - инициализирован
	# assets_data (dict) - dict{asset_name: {asset_data},...} словарь всех ассетов (всех типов) по именам
	# task_name_list (list) - список имён задач.
	def get_tasks_by_name_list(self, task_name_list, assets_data = False): # v2
		pass
		# (1) получение assets_data
		if not assets_data:
			result = self.asset.get_dict_by_name_by_all_types()
			if not result[0]:
				return(False, 'in task.get_tasks_by_name_list():\n%s' % result[1])
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
			asset_id = assets_data[task_name.split(':')[0]].id
			table_name = '"%s:%s"' % (asset_id, self.tasks_t)
			where = {'task_name': task_name}
			#
			bool_, return_data = database().read(level, read_ob, table_name, keys, where=where, table_root=table_root)
			if not bool_:
				return(bool_, return_data)
			if return_data:
				return_data[0]['asset_path'] = assets_data[task_name.split(':')[0]].path
				r_task = task(assets_data[task_name.split(':')[0]])
				task_data_dict[task_name] = r_task.init_by_keys(return_data[0])
		
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
			setattr(self, key, new_data)
			'''
			if isinstance(new_data, str):
				exec('self.%s = "%s"' % (key, new_data))
			else:
				exec('self.%s = %s' % (key, new_data))
			'''
		return(True, 'Ok!')
	
	# принудительная перезапись какого либо поля в таблице базы данных текущей задачи, без каких либо изменений во взаимосвязях.
	# key (str) - изменяемое поле в таблице из studio.tasks_keys (имя колонки)
	# new_data (в зависимости от типа данных данной колонки) - новое значение.
	def __change_data(self, key, new_data): # v2
		pass
		#
		read_ob = self.asset.project
		table_name = '"%s:%s"' % (self.asset_id, self.tasks_t)
		update_data = {key: new_data}
		where = {'task_name': self.task_name}
		bool_, r_data = database().update('project', read_ob, table_name, self.tasks_keys, update_data, where, table_root=self.tasks_db)
		if not bool_:
			return(bool_, r_data)
		
		# запись новых данных в поле объекта.
		setattr(self, key, new_data)
		
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
			if artist_name == readers_dict.get('first_reader'):
				del readers_dict['first_reader']
		
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
		
	# new_artist (str/artist) - nik_name или artist - объект
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	def change_artist(self, new_artist, task_data=False): # v2  !!!!! возможно надо рассмотреть варианты когда меняется артист в завершённых статусах задачь.
		pass
		# 1 - получение task_data.
		# 2 - чтение нового артиста и определение аутсорсер он или нет.
		# 3 - чтение outsource - изменяемой задачи.
		# 4 - определение нового статуса задачи
		# 5 - внесение изменений в БД
		# 6 - если task инициализирована - внеси в неё изменения.
		
		#print('*** new artist: ', new_artist)
		
		# (1)
		if not task_data:
			task_data = {}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.%s' % (key, key))
        
		#print('### task_data["outsource"].type = %s, value = %s' % (task_data["outsource"].__class__.__name__, str(task_data["outsource"])))
		
		# --------------- edit Status ------------
		new_status = None
				
		# (2) get artist outsource
		artist_outsource = False
		if new_artist and (isinstance(new_artist, str) or isinstance(new_artist, unicode)):
			result = artist().read_artist({'nik_name':new_artist})
			if not result[0]:
				return(False, result[1])
			if result[1][0].outsource:
				artist_outsource = bool(result[1][0].outsource)
		elif new_artist and isinstance(new_artist, artist):
			artist_outsource = new_artist.outsource
			new_artist = new_artist.nik_name
		else:
			new_artist = ''
		# затыка
		if artist_outsource is None:
			artist_outsource = '0'
		#print('*** artist_outsource: %s' % str(artist_outsource))
			
		# (3) get task_outsource
		task_outsource = task_data['outsource']
		'''
		task_outsource = False
		if task_data['outsource']:
			task_outsource = bool(task_data['outsource'])
		'''
		#print('*** task_outsource: %s' % str(task_outsource))
		
		# (4) get new status
		if task_data['status'] in self.VARIABLE_STATUSES:
			#print('****** in variable')
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
		#print('*** new_status: %s' % str(new_status))
			
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
		
		#print('*'*25, update_data, bool_)
		
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
		
	# new_input (bool/str) - имя новой входящей задачи или False
	# предполагается, что task инициализирован и меняем инпут данной задачи.
	def change_input(self, new_input): # v2 *** тестилось без смены статуса.
		pass
		# 1 - получение task_data, task_outsource, old_input_task, new_input_task, new_status, list_output_old, list_output_new
		# 2 - перезапись БД
		# 3 - подготовка return_data
		
		# (1)
		if new_input:
			if self.output and new_input in self.output:
				return(False, 'Outgoing task cannot be added to input!')
		
		# get old inputs tasks data (task instance)
		old_input_task = None
		if self.input:
			result = self.__read_task(self.input)
			if not result[0]:
				return(False, result[1])
			old_input_task = result[1]
		
		# get new inputs task data (task instance)
		new_input_task = None
		if new_input:
			result = self.__read_task(new_input)
			if not result[0]:
				return(False, result[1])
			new_input_task = result[1]
		
		# ???
		# change status
		new_status = self.from_input_status(new_input_task)
		if self.status in self.end_statuses and not new_status in self.end_statuses:
			self.this_change_from_end()
				
		# change outputs
		# -- in old input
		list_output_old = None # output бывшей входящей задачи
		if old_input_task:
			list_output_old = old_input_task.output
			if self.task_name in list_output_old:
				list_output_old.remove(self.task_name)
			
		# -- in new input
		list_output_new = None
		if new_input_task:
			if not new_input_task.output:
				list_output_new = []
			else:
				list_output_new = new_input_task.output
			list_output_new.append(self.task_name)
			
		# prints
		#if new_input_task:
			#print('new input: %s' % new_input_task.task_name)
		#else:
			#print('new input: %s' % new_input_task)
		#if old_input_task:
			#print('old input: %s' % old_input_task.task_name)
		#print('new status: %s' % new_status)
		#print('list_output_old:' , list_output_old)
		#print('list_output_new:' , list_output_new)
		#return(True, 'Be!')
		
		# (2)
		# change data
		if new_input_task:
			if list_output_new:
				new_input_task.__change_data('output', list_output_new)
			self.__change_data('input', new_input_task.task_name)
		else:
			self.__change_data('input', '')
		#
		if old_input_task and list_output_old:
			old_input_task.__change_data('output', list_output_old)
		#
		if new_status:
			self.__change_data('status', new_status)
		
		# (3)
		return(True, (new_status, old_input_task, new_input_task))
		
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
	# current_user (artist) - экземпляр класса артист, должен быть инициализирован - artist.get_user() - если False - то чат проверятся не будет (для тех нужд)
	def rework_task(self, current_user = False, task_data=False): # v2 ** продолжение возможно только после редактирования chat().read_the_chat()
		pass
		# 1 - получение task_data
		
		
		# (1)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.%s' % (key, key))
		
		# get exists chat
		if current_user:
			if not isinstance(current_user, artist):
				return(False, 'in task.rework_task() - "current_user" must be an instance of "artist" class, and not "%s"' % current_user.__class__.__name__)
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
			result = self.__read_task(input_task_name)
			if not result[0]:
				return(False, result[1])
			input_task_data = result[1]
		
		# (3)
		task_data['status'] = 'null'
		new_status = self.from_input_status(input_task_data)
		
		# (4)
		read_ob = self.asset.project
		table_name = '"%s:%s"' % (task_data['asset_id'], self.tasks_t)
		keys = self.tasks_keys
		update_data = {'readers':{}, 'status':new_status}
		where = {'task_name': task_data['task_name']}
		bool_, r_data = database().update('project', read_ob, table_name, keys, update_data, where, table_root=self.tasks_db)
		if not bool_:
			return(bool_, r_data)
		
		# (5)
		if self.task_name == task_data['task_name']:
			self.status = new_status
		
		# (6) change output statuses
		result = self.this_change_from_end(self.init_by_keys(task_data))
		if not result[0]:
			return(False, result[1])
		else:
			return(True, new_status)
			
	# change_statuses (list) - [(task_data, new_status), ...]
	# тупо смена статусов в пределах рабочих, что не приводит к смене статусов исходящих задач.
	# task.asset инициализирован
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
	
	# task_name (str) - имя задачи
	# возврат словаря задачи по имени задачи. если нужен объект используем task.init(name)
	def __read_task(self, task_name): # v2
		pass
		
		# (1)
		other_asset=False
		asset_path = False
		if self.asset.name == task_name.split(':')[0]: # задача из данного ассета
			asset_path = self.asset.path
			asset_id = self.asset.id
		# asset_path
		else: # задача из другого ассета
			other_asset=True
			read_asset = self.asset.init(task_name.split(':')[0])
			asset_path = read_asset.path
			asset_id = read_asset.id
		# read task
		table_name = '"%s:%s"' % (asset_id, self.tasks_t)
		where={'task_name': task_name}
		# -- read
		bool_, return_data = database().read('project', self.asset.project, table_name, self.tasks_keys , where=where, table_root=self.tasks_db)
		if not bool_:
			return(bool_, return_data)
		if not return_data:
			return(False, 'Not Found task whith name "%s"!' % task_name)
		
		task_data = return_data[0]
		task_data['asset_path'] = asset_path
		
		if not other_asset:	
			return(True, self.init_by_keys(task_data))
		else:
			task_ob = task(read_asset)
			task_ob.init_by_keys(task_data, new=False)
			return(True, task_ob)
	
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
		result = self.asset.get_dict_by_name_by_all_types()
		if not result[0]:
			return(False, result[1])
		asset_list = result[1]
		
		# (2)
		task_list = []
		task_input_task_list = {}
		for asset_name in asset_list:
			if asset_list[asset_name]['status']== 'active':
				asset_id = asset_list[asset_name].id
				bool_, return_data = self.get_list(asset_id=asset_id, artist = nik_name)
				if not bool_:
					return(bool_, return_data)
				task_list = task_list + return_data
		# (3)
		for task in task_list:
			task_input_task_list[task['task_name']] = {'task' : task}
			if task['input']:
				input_asset_id = asset_list[task['input'].split(':')[0]].id
				bool_, return_data = self.__read_task(task['input'])
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
		result = self.asset.get_dict_by_name_by_all_types()
		if not result[0]:
			return(False, result[1])
		asset_list = result[1]
		
		# (2)
		task_list = []
		for asset_name in asset_list:
			if asset_list[asset_name].status== 'active':
				asset_id = asset_list[asset_name].id
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
			description = 'In task.service_add_list_to_input() - incorrect type!\nThe type of task to be changed must be "service".\nThis type: "%s"' % task_data['task_type']
			return(False, description)
		
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
		
	# asset_list (list) - подсоединяемые ассеты (словари, или объекты)
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован
	def service_add_list_to_input_from_asset_list(self, asset_list, task_data=False): # v2
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
			description = 'In task.service_add_list_to_input_from_asset_list() - incorrect type!\nThe type of task to be changed must be "service".\nThis type: "%s"' % task_data['task_type']
			return(False, description)
		
		# (3)
		final_tasks_list = []
		types = {'obj':'model', 'char':'rig'}
		for ast in asset_list:
			if isinstance(ast, dict):
				ast_ob = asset(self.asset.project)
				ast_ob.init_by_keys(ast, new=False)
			elif isinstance(ast, asset):
				ast_ob = ast
			else:
				continue
			tsk_ob = task(ast_ob)
			if task_data['asset_type'] in ['location', 'shot_animation'] and ast_ob.type in types:
				activity = types[ast_ob.type]
				bool_, task_list = tsk_ob.get_list()
				if not bool_:
					return(bool_, task_list)
				#
				td_dict = {}
				for td in task_list:
					td_dict[td['task_name']] = td
				#
				for td in task_list:
					if td.get('activity') == activity:
						if not td.get('input') or td_dict[td['input']]['activity'] != activity:
								final_tasks_list.append(td)
			else:
				task_name = (ast_ob.name + ':final')
				bool_, td = tsk_ob.__read_task(task_name)
				if not bool_:
					return(bool_, td)
				final_tasks_list.append(td)
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
		
		#
		if self.task_name == task_data['task_name']:
			self.status = result[1][0]
			for task_name in result[1][1]:
				if not task_name in self.input:
					self.input.append(task_name)
		
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
			description = 'In task.service_remove_task_from_input() - incorrect type!\nThe type of task being cleared, must be "service".\nThis type: "%s"' % task_data['task_type']
			return(False, description)
		
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
			result = self.asset.get_dict_by_name_by_all_types()
			if not result[0]:
				return(False, result[1])
			assets = result[1]
			#
			bool_statuses = []
			
			for task_name in input_list:
				bool_, r_data = self.get_tasks_by_name_list([task_name], assets_data = assets.get(task_name.split(':')[0]))
				if not bool_:
					print('#'*5)
					print('in task.get_tasks_by_name_list()')
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
			result = self.get_dict_by_name_by_all_types(project_name)
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
		
	# 
	# removed_task_data (dict) - удаляемая задача
	# added_task_data (dict) - добавляемая задача
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	def service_change_task_in_input(self, removed_task_data, added_task_data, task_data=False): # v2
		pass
		# 0 - получение task_data.
		
		# (0)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.%s' % (key, key))
		
		# debug	
		#print(task_data['task_name'])
		#print(removed_task_data['task_name'])
		#print(added_task_data['task_name'])
		
		# remove task
		result = self.service_remove_task_from_input([removed_task_data], task_data=task_data)
		if not result[0]:
			return(False, result[1])
		
		new_status, input_list = result[1]
		
		# edit task_data
		print(task_data['input'], task_data['status'])
		#
		task_data['input'] = input_list
		task_data['status'] = new_status
		#
		print(task_data['input'], task_data['status'])
		
		#print(json.dumps(task_data, sort_keys = True, indent = 4))
		#return(False, 'Epteeeee!')
		
		# add task
		result = self.service_add_list_to_input([added_task_data], task_data=task_data)
		if not result[0]:
			return(False, result[1])
		
		#
		if self.task_name == task_data['task_name']:
			self.status = result[1][0]
			self.input = input_list + result[1][1]
			
		return(True, result[1])
	
	# заменяет все рид статусы задачи на 0
	# task_data (dict) - изменяемая задача, если False - значит предполагается, что task инициализирован.
	def task_edit_read_status_unread(self, task_data=False): # v2 ** start - не обнаружено использование
		pass
		# 0 - получение task_data.
		# 1 - принудительное прочтение задачи из БД - ???????????? зачееемм!!!!!!
		
		# (0)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.%s' % (key, key))
				
		# (1)
		read_ob = self.asset.project
		table_name = '"%s:%s"' % (task_data['asset_id'], self.tasks_t)
		keys = self.tasks_keys
		where = {'task_name': task_data['task_name']}
		
		
		'''
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		string = 'SELECT * FROM ' + table + ' WHERE task_name = ?'
		data = (task_data['task_name'],)
		
		# connect db
		try:
			conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return(False, 'in task_edit_read_status_unread - not connect db!')
		
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
		'''
		return(True, 'Ok!')
	
	# заменяет все рид статусы задачи на 1
	# self.task - должен быть инициализирован
	def task_edit_read_status_read(self, project_name, task_data, nik_name): # v2 ** - не обнаружено использование
		pass
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
			return(False, 'in task_edit_read_status_read - not connect db!')
		
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
			
class log(studio):
	'''
	write_log(project_name, task_name, {key: data, ...}) 
	
	read_log(project_name, asset_name, {key: key_name, ...});; example: self.read_log(project, asset, {'activity':'rig_face', 'action':'push'});; return: (True, ({key: data, ...}, {key: data, ...}, ...))  or (False, description)
	
	'''
	
	def __init__(self, task_ob): # v2
		if not isinstance(task_ob, task):
			raise Exception('in log.__init__() - Object is not the right type "%s", must be "task"' % task_ob.__class__.__name__)
		self.task = task_ob
		#
		for key in self.logs_keys:
			exec('self.%s = False' % key)
		
		self.camera_log_file_name = 'camera_logs.json'
		self.playblast_log_file_name = 'playblast_logs.json'
		
		self.log_actions = ['push', 'publish', 'open', 'report','recast' , 'change_artist', 'close', 'done', 'return_a_job', 'send_to_outsource', 'load_from_outsource']
	
	# запись лога для задачи
	# self.task - должен быть инициализирован
	# logs_keys (dict) - словарь по studio.logs_keys - обязательные ключи: description, version, action
	# artist (bool/artist) - если False - значит создаётся новый объект artist и определяется текущий пользователь.
	def write_log(self, logs_keys, artist_ob=False): # v2 - процедура бывшая notes_log 
		pass
		# 1 - тест обязательных полей: description, version, action
		# 2 - чтение artist
		# 3 - заполнение полей task_name, date_time, artist
		# 4 - запись БД
		
		# (1)
		for item in ["description", "version", "action"]:
			if not logs_keys.get(item):
				return(False, 'in log.write_log() - no "%s" submitted!' % item)
		
		if not logs_keys['action'] in self.log_actions:
			return(False, 'in log.write_log() - wrong action - "%s"!' % logs_keys['action'])
		
		# (2)
		if not artist_ob:
			artist_ob = artist()
			bool_, r_data = artist_ob.get_user()
			if not bool_:
				return(bool_, r_data)

		# (3)		
		# task_name
		if not self.task.task_name:
			return(False, 'in log.write_log() - value "self.task.task_name" not defined!')
		else:
			logs_keys['task_name'] = self.task.task_name
		#
		if not logs_keys.get('date_time'):
			logs_keys['date_time'] = datetime.datetime.now()
		#
		logs_keys['artist'] = artist_ob.nik_name
		#
		logs_keys['activity'] = self.task.activity
		
		# (4)
		table_name = '"%s:%s:logs"' % (self.task.asset_id, logs_keys['activity'])
		read_ob = self.task.asset.project
		#
		bool_, r_data = database().insert('project', read_ob, table_name, self.logs_keys, logs_keys, table_root=self.logs_db)
		if not bool_:
			return(bool_, r_data)
		'''
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
		'''
		
		return(True, 'ok')
	
	# запись лога задачи
	# self.task - должен быть инициализирован
	# action (bool / str) если False - то возврат для всех action
	def read_log(self, action=False): # v2
		pass
		# 1 - проверка инициализации ассета.
		# 2 - проверка action
		# 3 - чтение БД.
	
		# (1)
		if not self.task.task_name:
			return(False, 'in log.write_log() - value "self.task.task_name" not defined!')
		
		# (2)
		if action and not action in self.log_actions:
			return(False, 'in log.read_log() - wrong "action" - "%s"!' % action)
		
		# (3)
		table_name = '"%s:%s:logs"' % (self.task.asset_id, self.task.activity)
		read_ob = self.task.asset.project
		if action:
			where = {'action': action}
		else:
			where = False
		bool_, r_data = database().read('project', read_ob, table_name, self.logs_keys, where=where, table_root=self.logs_db)
		return(bool_, r_data)
		
		'''
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
		conn.close()
		'''
		
	# читает только push логи
	# преобразует datetime в строку
	# task_data (bool/dict) - если False - значит читается self.task
	# time_to_str (bool) - если True - то преобразует дату в строку.
	def get_push_logs(self, task_data=False, time_to_str = False): # v2 возможно устаревшая
		pass
		# get all logs
		if not task_data:
			bool_, logs_list = self.read_log(action='push')
			if not bool_:
				return(False, logs_list)
		else:
			# get asset/task
			if task_data['asset_name'] != self.task.asset.name:
				asset_ob = self.task.asset.init(task_data['asset_name'])
				task_ob = task(asset_ob)
			else:
				task_ob = task(self.task.asset)
			#
			task_ob.init_by_keys(task_data, new=False)
			# get log
			log_new = log(task_ob)
			# read log
			bool_, logs_list = log_new.read_log(action='push')
			if not bool_:
				return(False, logs_list)
			
		
		if time_to_str:
			for row in logs_list:
				dt = row['date_time']
				data = dt.strftime("%d-%m-%Y %H:%M:%S")
				row['date_time'] = data
				
		return(True, logs_list)
	
	# *** CAMERA LOGS ***
	# artist_ob - (artist) - объект artist, его никнейм записывается в лог.
	# description (str) - комментарий
	# version (str/int) - номер версии <= 9999
	# task_data (bool/dict) - если False - значит читается self.task, если передаётся, то только задача данного ассета.
	def camera_write_log(self, artist_ob, description, version, task_data=False): # v2 - возможно нужна поверка существования версии ?
		pass
		# 0 - проверка user
		# 1 - заполнение task_data
		# 2 - тест обязательных полей: description, version
		# 3 - заполнение logs_keys
		# 4 - запись json
		
		# (0)
		if not isinstance(artist_ob, artist):
			return(False, 'in log.camera_write_log() - "artist_ob" parameter is not an instance of "artist" class')
		if not artist_ob.nik_name:
			return(False, 'in log.camera_write_log() - required login!')
		
		# (1)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.task.%s' % (key, key))
		else:
			if not taks_data['asset_name'] == self.task.asset.name:
				return(False, 'in log.camera_write_log() - transferred "task_data" is not from the correct asset: transferred: "%s", required: "%s"' % (taks_data['asset_name'], self.task.asset.name))
				
		# (2)
		for item in [description, version]:
			if not item:
				return(False, '"%s" parameter not passed!' % item)
		
		# (3)
		logs_keys = {}
		for key in self.logs_keys:
			if key in self.tasks_keys:
				logs_keys[key] = task_data[key]
		
		str_version = '%04d' % int(version)
		logs_keys['description'] = description
		logs_keys['action'] = 'push_camera'
		logs_keys['date_time'] = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
		logs_keys['version'] = str_version
		logs_keys['artist'] = artist_ob.nik_name
		
		# (4)
		path = os.path.join(task_data['asset_path'], self.task.asset.ADDITIONAL_FOLDERS['meta_data'], self.camera_log_file_name)
		path = NormPath(path)
		
		data = {}
		
		if os.path.exists(path):
			with open(path, 'r') as f:
				try:
					data = json.load(f)
				except:
					pass
		
		data[str_version] = logs_keys
		
		with open(path, 'w') as f:
			jsn = json.dump(data, f, sort_keys=True, indent=4)
		
		return(True, 'Ok!')
	
	# task_data (bool/dict) - если False - значит читается self.task, если передаётся, то только задача данного ассета.
	def camera_read_log(self, task_data=False): # v2
		pass
		# 1 - заполнение task_data
		# 2 - определение пути к файлу
		# 3 - чтение json
		# 4 - сортировка
		
		# (1)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.task.%s' % (key, key))
		else:
			if not taks_data['asset_name'] == self.task.asset.name:
				return(False, 'in log.camera_read_log() - transferred "task_data" is not from the correct asset: transferred: "%s", required: "%s"' % (taks_data['asset_name'], self.task.asset.name))		
		
		# (2)
		path = os.path.join(task_data['asset_path'], self.task.asset.ADDITIONAL_FOLDERS['meta_data'], self.camera_log_file_name)
		if not os.path.exists(path):
			return(False, 'No saved versions!')
			
		# (3)
		with open(path, 'r') as f:
			data = None
			try:
				data = json.load(f)
			except:
				return(False, ('problems with file versions: ' + path))
		# (4)
		nums = []
		sort_data = []
		for key in data:
			nums.append(int(key))
		nums.sort()
		
		for num in nums:
			#key = '0'*(4 - len(str(num))) + str(num)
			key = '%04d' % int(num)
			if data.get(key):
				sort_data.append(data[str(key)])
			else:
				print('*** not key')
			
		return(True, sort_data)
		
	# *** PLAYBLAST LOGS ***
	# artist_ob - (artist) - объект artist, его никнейм записывается в лог.
	# description (str) - комментарий
	# version (str/int) - номер версии <= 9999
	# task_data (bool/dict) - если False - значит читается self.task, если передаётся, то только задача данного ассета.
	def playblast_write_log(self, artist_ob, description, version, task_data=False): # v2
		pass
		# 0 - проверка user
		# 1 - заполнение task_data
		# 2 - тест обязательных полей: description, version
		# 3 - заполнение logs_keys
		# 4 - запись json
		
		# (0)
		if not isinstance(artist_ob, artist):
			return(False, 'in log.playblast_write_log() - "artist_ob" parameter is not an instance of "artist" class')
		if not artist_ob.nik_name:
			return(False, 'in log.playblast_write_log() - required login!')
		
		# (1)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.task.%s' % (key, key))
		else:
			if not taks_data['asset_name'] == self.task.asset.name:
				return(False, 'in log.playblast_write_log() - transferred "task_data" is not from the correct asset: transferred: "%s", required: "%s"' % (taks_data['asset_name'], self.task.asset.name))
				
		# (2)
		for item in [description, version]:
			if not item:
				return(False, '"%s" parameter not passed!' % item)
		
		# (3)
		logs_keys = {}
		for key in self.logs_keys:
			if key in self.tasks_keys:
				logs_keys[key] = task_data[key]
		
		str_version = '%04d' % int(version)
		logs_keys['description'] = description
		logs_keys['action'] = 'playblast'
		logs_keys['date_time'] = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
		logs_keys['version'] = str_version
		logs_keys['artist'] = artist_ob.nik_name
		
		path = os.path.join(task_data['asset_path'], self.task.asset.ADDITIONAL_FOLDERS['meta_data'], self.playblast_log_file_name)
		path = NormPath(path)
		
		data = {}
		
		if os.path.exists(path):
			with open(path, 'r') as f:
				try:
					data = json.load(f)
				except:
					pass
		
		data[str_version] = logs_keys
		
		with open(path, 'w') as f:
			jsn = json.dump(data, f, sort_keys=True, indent=4)
		
		return(True, 'Ok!')
	
	# task_data (bool/dict) - если False - значит читается self.task, если передаётся, то только задача данного ассета.
	def playblast_read_log(self, task_data=False): # v2
		pass
		# 1 - заполнение task_data
		# 2 - определение пути к файлу
		# 3 - чтение json
		# 4 - сортировка
		
		# (1)
		if not task_data:
			task_data={}
			for key in self.tasks_keys:
				exec('task_data["%s"] = self.task.%s' % (key, key))
		else:
			if not taks_data['asset_name'] == self.task.asset.name:
				return(False, 'in log.camera_read_log() - transferred "task_data" is not from the correct asset: transferred: "%s", required: "%s"' % (taks_data['asset_name'], self.task.asset.name))	
			
		# (2)
		path = os.path.join(task_data['asset_path'], self.task.asset.ADDITIONAL_FOLDERS['meta_data'], self.playblast_log_file_name)
		if not os.path.exists(path):
			return(False, 'No saved versions!')
		
		# (3)
		with open(path, 'r') as f:
			data = None
			try:
				data = json.load(f)
			except:
				return(False, ('problems with file versions: ' + path))
		
		# (4)
		nums = []
		sort_data = []
		for key in data:
			nums.append(int(key))
		nums.sort()
		
		for num in nums:
			#key = '0'*(4 - len(str(num))) + str(num)
			key = '%04d' % int(num)
			sort_data.append(data[key])
			
		return(True, sort_data)
		
	
	def camera_get_push_logs(self, project_name, task_data): # возможно никогда не понадобится
		pass
		
class artist(studio):
	'''
	self.add_artist({key:data, ...}) - "nik_name", "user_name" - Required, add new artist in 'artists.db';; return - (True, 'ok') or (Fasle, description) descriptions: 'overlap', 'not nik_name', 
	
	self.login_user(nik_name, password) - 
	
	self.read_artist({key:data, ...}) - "nik_name", - Required, returns full information, relevant over the keys ;; example: self.read_artist({'specialty':'rigger'});; return: (True, [{Data}, ...])  or (False, description)
	
	self.edit_artist({key:data, ...}) - "nik_name", - Required, does not change the setting ;;
	
	self.get_user() - ;; return: (True, (nik_name, user_name)), (False, 'more than one user'), (False, 'not user') ;;
	
	self.add_stat(user_name, {key:data, ...}) - "project_name, task_name, data_start" - Required ;;
	
	self.read_stat(user_name, {key:data, ...}) - returns full information, relevant over the keys: (True, [{Data}, ...]) or (False, description);; 
	
	self.edit_stat(user_name, project_name, task_name, {key:data, ...}) - 
	'''
	def __init__(self):
		pass
		#base fields
		for key in self.artists_keys:
			exec('self.%s = False' % key)
		#studio.__init__(self)
		pass
	
	# инициализация по имени
	# new (bool) - если True - то возвращается новый инициализированный объект класса artist, если False - то инициализируется текущий объект
	def init(self, nik_name, new = True):
		pass
		# get keys
		bool_, artists = self.read_artist({'nik_name': nik_name})
		if not bool_:
			return(bool_, artists)
				
		# fill fields
		if new:
			return artists[0]
		else:
			for key in self.artists_keys:
				#exec('self.%s = keys[0].get("%s")' % (key, key))
				setattr(self, key, getattr(artists[0], key))
			#self.asset_path = keys.get('asset_path')
			return(True, 'Ok')
		
	# инициализация по словарю
	# new (bool) - если True - то возвращается новый инициализированный объект класса artist, если False - то инициализируется текущий объект
	def init_by_keys(self, keys, new = True):
		pass
		# fill fields
		if new:
			new_artist = artist()
			for key in self.artists_keys:
				exec('new_artist.%s = keys.get("%s")' % (key, key))
			return new_artist
		else:
			for key in self.artists_keys:
				exec('self.%s = keys.get("%s")' % (key, key))
			#self.asset_path = keys.get('asset_path')
			return(True, 'Ok')
	
	# если registration=True - произойдёт заполнение полей artists_keys, поле user_name будет заполнено.
	# если registration=False - поля artists_keys заполняться не будут, поле user_name - останется пустым.
	def add_artist(self, keys, registration = True):
		pass
		# test nik_name
		if not keys.get('nik_name'):
			return(False, '\"Nik Name\" not specified!')
		if not keys.get('password'):
			return(False, '\"Password\" not specified!')
		if not keys.get('outsource'):
			keys['outsource'] = '0'
		else:
			keys['outsource'] = '1'

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
		
	# keys (dict) - фильтр по ключам artists_keys
	# objects (bool) - если True - то возвращаются объекты, если False - то словари.
	def read_artist(self, keys, objects=True):
		if keys == 'all':
			keys = False
		bool_, r_data = database().read('studio', self, self.artists_t, self.artists_keys, where=keys)
		if not bool_:
			return(bool_, r_data)
		if not objects:
			return(bool_, r_data)
		else:
			objects = []
			for data in r_data:
				objects.append(self.init_by_keys(data))
			return(True, objects)
			
		
	def read_artist_of_workroom(self, workroom_id, objects=True):
		bool_, return_data = database().read('studio', self, self.artists_t, self.artists_keys)
		if not bool_:
			return(bool_, return_data)
		#
		artists_dict = {}
		for row in return_data:
			try:
				workrooms = row['workroom']
			except:
				continue
			if workroom_id in workrooms:
				if objects:
					artists_dict[row['nik_name']] = self.init_by_keys(row)
				else:
					artists_dict[row['nik_name']] = row
		return(True, artists_dict)
	
	# список активных артистов подходящих для данного типа задачи.
	# task_type (str) - тип задачи
	# workroom_ob (workroom)предполагается что выполнена процедура workroom.get_list() и заполнено поле list_workroom (список всех отделов)
	# rturn - (True, сортированный список имён артистов, словарь артистов по именам.) или (False, comment)
	def get_artists_for_task_type(self, task_type, workroom_ob):
		pass
		artists_dict = {}
		active_artists_list = []
		for wr in workroom_ob.list_workroom:
			if task_type in wr.type:
				b, r_data = self.read_artist_of_workroom(wr.id)
				if not b:
					print('*** problem in workroom.read_artist_of_workroom() by "%s"' % wr.name)
					print(r_data)
					continue
				else:
					for artist_name in r_data:
						if r_data[artist_name].status=='active':
							active_artists_list.append(artist_name)
					artists_dict.update(r_data)
		
		active_artists_list = list(set(active_artists_list))
		active_artists_list.sort()
	
		return(True, active_artists_list, artists_dict)
		
	def login_user(self, nik_name, password):
		pass
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
				setattr(self, key, rows[0].get(key))
				#com = 'self.%s = rows[0].get("%s")' % (key, key)
				#exec(com)
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
	def edit_artist_old(self, key_data, artist_current_data = False):
		pass
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
		bool_, return_data = database().update('studio', self, self.artists_t, self.artists_keys, key_data, where = {'nik_name': nik_name})
		if not bool_:
			return(bool_, return_data)
		return True, 'ok'
	
	# редактирование объекта артиста. текущий объект artist должен быть инициализирован. редактирует параметры текущего-редактируемого объекта.
	# keys (dict) - данные на замену - nik_name - не редактируется, поэтому удаляется из данных перед записью.
	# current_user (artist) - редактор - залогиненный пользователь.
	def edit_artist(self, keys, current_user=False):
		pass
		# 1 - проверка заполненности keys
		# 2 - тест current_user
		# 3 - уровни доступа
		# 4 - запись данных в БД
		# 5 - изменение данных текущего объекта
		
		# (1)
		if not keys:
			return(False, 'No data to write!')
		# (2)
		if current_user and not isinstance(current_user, artist):
			return(False, 'In artist.edit_artist() - wrong type of "current_user" - %s' % current_user.__class__.__name__)
		elif not current_user:
			current_user = artist()
			bool_, return_data = current_user.get_user()
			if not bool_:
				return(bool_, return_data)
		
		# (3)
		# -- user не менеджер
		if not current_user.level in self.manager_levels:
			return(False, 'Not Access! (your level does not allow you to make similar changes)')
		# -- попытка возвести в ранг выше себя
		elif keys.get("level") and self.user_levels.index(current_user.level) < self.user_levels.index(keys.get("level")):
			return(False, 'Not Access! (attempt to assign a level higher than yourself)')
		# -- попытка сделать изменения пользователя с более высоким уровнем.
		elif self.user_levels.index(current_user.level) < self.user_levels.index(self.level):
			return(False, 'Not Access! (attempt to change a user with a higher level)')
		
		# (4)
		# update
		if 'nik_name' in keys:
			del keys['nik_name']
		bool_, return_data = database().update('studio', self, self.artists_t, self.artists_keys, keys, where = {'nik_name': self.nik_name}, table_root=self.artists_db)
		if not bool_:
			return(bool_, return_data)
		
		# (5)
		for key in self.artists_keys:
			if key in keys:
				exec('self.%s = keys.get("%s")' % (key, key))
		
		return True, 'ok'
		
	def add_stat(self, user_name, keys):
		pass
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
		pass
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
		pass
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
	list_workroom = None
	dict_by_name = None
	dict_by_id = None
	
	def __init__(self):
		pass
		for key in self.workroom_keys:
			exec('self.%s = False' % key)
		
	# инициализация по словарю
	# new (bool) - если True - то возвращается новый инициализированный объект класса workroom, если False - то инициализируется текущий объект
	def init_by_keys(self, keys, new = True):
		if new:
			new_ob = workroom()
			for key in self.workroom_keys:
				exec('new_ob.%s = keys.get("%s")' % (key, key))
			return new_ob
		else:
			for key in self.workroom_keys:
				exec('self.%s = keys.get("%s")' % (key, key))
			return(True, 'Ok')
	
	# keys['type'] - must be a list, False or None
	def add(self, keys, new=False):
		pass
		# test name
		try:
			name = keys['name']
		except:
			return(False, 'not Name!')
			
		keys['id'] = uuid.uuid4().hex
		
		# 1 - создание таблицы, если отсутствует. чтобы без вылетов сработала проверка на совпадение имени.
		# 2 - проверка на совпадение имени
		# 3 - проверка чтобы типы задач были из task_types
		# 4 - запись строки в таблицу
		
		# (1) create table 
		bool_, return_data = database().create_table('studio', self, self.workroom_t, self.workroom_keys, table_root = self.workroom_db)
		if not bool_:
			return(bool_, return_data)
		
		# (2) test exists name
		bool_, return_data = database().read('studio', self, self.workroom_t, self.workroom_keys, where={'name': name}, table_root=self.workroom_db)
		if not bool_:
			return(bool_, return_data)
		elif return_data:
			return(False, 'This workroom name: "%s" already exists!' % name)
		
		# (3) test type
		type_ = keys.get('type')
		if type_:
			if type_.__class__.__name__ == 'list':
				for item in type_:
					if not item in self.task_types:
						return(False, 'This type of task: "%s" is not correct!' % item)
			else:
				return(False, 'This type of keys[type]: "%s" is not correct (must be a list, False or None)' % str(type_))
			
		# (4) insert string
		bool_, return_data = database().insert('studio', self, self.workroom_t, self.workroom_keys, keys, table_root=self.workroom_db)
		if not bool_:
			return(bool_, return_data)
		
		if not new:
			return(True, 'ok')
		else:
			return(self.init_by_keys(keys, True))
		
	def get_list(self, return_type = False, objects=True):
		pass
		bool_, return_data = database().read('studio', self, self.workroom_t, self.workroom_keys, table_root=self.workroom_db)
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
			if objects:
				wr_data = self.init_by_keys(row)
			else:
				wr_data = row
			return_data_0[row['name']] = wr_data
			return_data_1.append(wr_data)
			return_data_2[row['id']] = wr_data
		
		# fill fields
		self._fill_fields_of_workroom_class(return_data_1, return_data_0, return_data_2)
		
		# return
		if not return_type:
			return(True, return_data_1)
		elif return_type == 'by_name':
			return(True, return_data_0)
		elif return_type == 'by_id':
			return(True, return_data_2)
		elif return_type == 'by_id_by_name':
			return(True, return_data_2, return_data_0)
		else:
			return(False, ('Incorrect "return_type": %s' % return_type))
		
	@classmethod
	def _fill_fields_of_workroom_class(self, list_workroom, dict_by_name, dict_by_id):
		pass
		self.list_workroom = list_workroom
		self.dict_by_name = dict_by_name
		self.dict_by_id = dict_by_id
	
	
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
		bool_, data = self.get_list('by_name', False)
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
		bool_, data = self.get_list('by_id', False)
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
			
	# объект должен быть инициализирован
	# new_name (str) - новое имя для отдела
	def rename_workroom(self, new_name):
		new_name = new_name.replace(' ', '_')
		
		# 1 - проверка имени на совпадение, со старым и с имеющимися
		# 2 - запись данных в БД
		# 3 - перезапись name текущего объекта.
		
		# (1)
		if self.name == new_name:
			return(False, 'Match names!')
		bool_, return_data = self.get_list('by_name', False)
		if not bool_:
			return(bool_, return_data)
		if new_name in return_data:
			return(False, 'This name of workroom already exists! "%s"' % new_name)
		
		# (2)
		update_data = {'name':new_name}
		where = {'id': self.id}
		bool_, return_data = database().update('studio', self, self.workroom_t, self.workroom_keys, update_data, where, table_root=self.workroom_db)
		if not bool_:
			return(bool_, return_data)
		
		# (3)
		self.name = new_name
		
		return(True, 'Ok!')
	
	# объект должен быть инициализирован
	# new_type_list (list) - список типов
	def edit_type(self, new_type_list):
		pass
		# (1) test type
		if new_type_list:
			if new_type_list.__class__.__name__ == 'list':
				for item in new_type_list:
					if not item in self.task_types:
						return(False, 'This type of task: "%s" is not correct!' % item)
			else:
				return(False, 'This type of keys[type]: "%s" is not correct (must be a list, False or None)' % str(new_type_list))
		# (2)
		update_data = {'type': new_type_list}
		where = {'id': self.id}
		bool_, return_data = database().update('studio', self, self.workroom_t, self.workroom_keys, update_data, where, table_root=self.workroom_db)
		if not bool_:
			return(bool_, return_data)
		self.type = new_type_list
		return(True, 'Ok!')
		
class chat(studio):
	'''
	self.record_messages(project_name, task_name, topic) - records topic to '.chats.db';; topic = dumps({line1:(img, img_icon, text), ...})
	
	self.read_the_chat(self, project_name, task_name, reverse = 0) - It returns a list of all messages for a given task;;
	'''
	def __init__(self, task_ob):
		if not isinstance(task_ob, task):
			raise Exception('in chat.__init__() - Object is not the right type "%s", must be "task"' % task_ob.__class__.__name__)
		self.task = task_ob
		# 
		for key in self.chats_keys:
			exec('self.%s = False' % key)
	
	#def record_messages(self, project_name, task_name, author, color, topic, status, date_time = ''):
	# запись сообщения в чат для задачи
	# self.task - должен быть инициализирован
	# input_keys (dict) - словарь по studio.chats_keys - обязательные ключи: 'topic','color','status', 'reading_status'  ??????? список обязательных полей будет пересмотрен
	# artist_ob (bool/artist) - если False - значит создаётся новый объект artist и определяется текущий пользователь.
	def record_messages(self, input_keys, artist_ob=False): # v2
		pass
		# 1 - artist_ob test
		# 2 - тест обязательных полей
		# 3 - datetime, message_id
		# 4 - запись БД
		
		# (1)
		if artist_ob and not isinstance(artist_ob, artist):
			return(False, 'in chat.record_messages() - Wrong type of "artist_ob"! - "%s"' % artist_ob.__class__.__name__)
		elif artist_ob:
			if not artist_ob.nik_name:
				return(False, 'in chat.record_messages() - User is not logged in!')
			input_keys['author'] = artist_ob.nik_name
		elif not artist_ob:
			artist_ob = artist()
			bool_, r_data = artist_ob.get_user()
			if not bool_:
				return(bool_, r_data)
			input_keys['author'] = artist_ob.nik_name
			
		# (2)
		for item in ['topic','color','status', 'reading_status']:
			if not input_keys[item]:
				return(False, 'in chat.record_messages() - missing "%s"!' % item)
			
		# (3)
		input_keys['date_time_of_edit'] = input_keys['date_time'] = datetime.datetime.now()
		input_keys['message_id'] = uuid.uuid4().hex
		
		# (4)
		table_name = '"%s"' % self.task.task_name
		read_ob = self.task.asset.project
		#
		bool_, r_data = database().insert('project', read_ob, table_name, self.chats_keys, input_keys, table_root=self.chats_db)
		if not bool_:
			return(bool_, r_data)
		
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
		'''
		return(True, 'ok')
	
	# чтение сообщений чата задачи
	# self.task - должен быть инициализирован
	# message_id (hex/bool) - id читаемого сообщения, если False - то читаются все сообщения чата.
	# reverse (bool) - пока никак не используется
	def read_the_chat(self, message_id=False, reverse = False): # v2
		pass
		# 1 - чтение БД
		
		# (1)
		table_name = '"%s"' % self.task.task_name
		if message_id:
			where = {'message_id': message_id}
			return(database().read('project', self.task.asset.project, table_name, self.chats_keys, where = where, table_root = self.chats_db))
		return(database().read('project', self.task.asset.project, table_name, self.chats_keys, table_root = self.chats_db))

		'''
		table = '\"' + task_name + '\"'
		
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
				
		return(True, rows)
		'''
	
	# изменение записи автором сообщения.
	# self.task - должен быть инициализирован.
	# artist_ob (bool/artist) - если False - значит создаётся новый объект artist и определяется текущий пользователь.
	# message_id (hex) - id изменяемого сообщения
	# new_data (dict) - словарь данных на замену - topic, color
	def edit_message(self, message_id, new_data, artist_ob=False):
		VALID_DATA = ['topic', 'color']
		# 0 - тест new_data
		# 1 - artist_ob test
		# 2 - проверка автора
		# 3 - запись изменений
		
		# (0)
		for key in new_data:
			if not key in ['topic', 'color']:
				del(new_data[key])
		
		# (1)
		if artist_ob and not isinstance(artist_ob, artist):
			return(False, 'in chat.record_messages() - Wrong type of "artist_ob"! - "%s"' % artist_ob.__class__.__name__)
		elif artist_ob and not artist_ob.nik_name:
			return(False, 'in chat.record_messages() - User is not logged in!')
		elif not artist_ob:
			artist_ob = artist()
			bool_, r_data = artist_ob.get_user()
			if not bool_:
				return(bool_, r_data)
			
		# (2)
		bool_, r_data = self.read_the_chat(message_id=message_id)
		if not bool_:
			return(bool_, r_data)
		message = r_data[0]
		if message['author'] != artist_ob.nik_name:
			return(False, 'Only author can edit messages!')
			
		# (3)
		new_data['date_time_of_edit'] = datetime.datetime.now()
		read_ob = self.task.asset.project
		table_name = '"%s"' % self.task.task_name
		where = {'message_id': message_id}
		
		bool_, r_data = database().update('project', read_ob, table_name, self.chats_keys, new_data, where=where, table_root=self.chats_db)
		if not bool_:
			return(bool_, r_data)
		
		return(True, 'Ok!')
	
class set_of_tasks(studio):
	def __init__(self):
		self.set_of_tasks_keys = {
		'name':'text',
		'asset_type': 'text',
		'sets':'json',
		'edit_time': 'timestamp',
		}
		self.sets_keys = [
		'task_name',
		'input',
		'activity',
		'tz',
		'cost',
		'standart_time',
		'task_type',
		'extension',
		]
		
		for key in self.set_of_tasks_keys:
			setattr(self, key, False)
	
	def init_by_keys(self, keys, new=True): # v2
		if new:
			r_ob = set_of_tasks()
		else:
			r_ob = self
			
		for key in self.set_of_tasks_keys:
			setattr(r_ob, key, keys.get(key))
			
		if new:
			return r_ob
		else:
			return(True, 'Ok!')
	
	# asset_type (str) - тип ассета
	# keys (list) список словарей по каждой задаче сета (по sets_keys)
	# force (bool) - если False - то будет давать ошибку при совпадении имени, если True - то будет принудительно перименовывать подбирая номер
	def create(self, name, asset_type, keys = False, force=False): # v2
		pass
		# 1 - тесты передаваемых имени и типа ассета
		# 2 - чтение наборов на определение совпадения имени + создание нового имени при force=True
		# 3 - запись
		
		# (1)
		# test data
		if not name:
			return(False, 'Not Name!')
		
		# (2)
		b, r = self.get_list(f = {'name': name})
		if not b:
			print(r)
		elif r and not force:
			return(False, 'A set with that name "%s" already exists' % name)
		elif r and force:
			num = 0
			while r:
				num+=1
				new_name = '%s.%i' % (name, num)
				b, r = self.get_list(f = {'name': new_name})
				if not b:
					return(b, r)
				print(new_name)
			name = new_name
		
		if not asset_type in self.asset_types:
			return(False, 'Wrong type of asset: "%s"' % asset_type)
		
		# (3)
		# edit data
		data = {}
		data['name'] = name
		data['asset_type'] = asset_type
		data['edit_time'] = datetime.datetime.now()
		if keys:
			data['sets'] = keys

		# write data
		bool_, r_data = database().insert('studio', self, self.set_of_tasks_t, self.set_of_tasks_keys, data, table_root=self.set_of_tasks_db)
		if not bool_:
			return(bool_, r_data)
		
		return(True, self.init_by_keys(data))
	
	# возврат списка объектов
	# f (dict) - фильтр ро ключам set_of_tasks_keys / используется только для чтения из базы данных при path=False
	# path (bool / str) - если указан - то чтение из файла json, если - False - то чтение из базы данных.
	def get_list(self, f = False, path = False): # v2
		pass
		# 1 - чтение из базы данных
		# 2 - чтение из json
		data = []
		
		# (1)
		if not path:
			if f:
				wh = f
			else:
				wh = False
			bool_, r_data = database().read('studio', self, self.set_of_tasks_t, self.set_of_tasks_keys, where=wh, table_root=self.set_of_tasks_db)
			if not bool_:
				return(False, r_data)
			
			## преобразование в словарь
			#for set_ in r_data:
				#data[set_['name']] = set_
				
			for item in r_data:
				data.append(self.init_by_keys(item))
		
		# (2)
		else:
			if not os.path.exists(path):
				return(False, ('No Exists path: %s' % path))
			# read data
			try:
				with open(path, 'r') as read:
					r_data = json.load(read)
					read.close()
			except Exception as e:
				print('#'*5, e)
				return(False, ("%s can not be read! Look The terminal!" % path))
			
			for key in r_data:
				item = r_data[key]
				item['name'] = key
				data.append(self.init_by_keys(item))
			
		return(True, data)
		
	# обёртка на get_list(f)
	def get_list_by_type(self, asset_type): # v2
		if not asset_type in self.asset_types:
			return(False, 'Wrong type of asset: "%s"' % asset_type)
		return_list = []
		return(self.get_list(f = {'asset_type': asset_type}))
		
	# объекты
	def get_dict_by_all_types(self): # v2
		result = self.get_list()
		if not result[0]:
			return(False, result[1])
		
		return_list = {}
		for item in result[1]:
			asset_type = item.asset_type
			if not asset_type in return_list:
				return_list[asset_type] = {}
			
			return_list[asset_type][item.name] = item
				
		return(True, return_list)
	
	# возвращает новый объект по имени, обёртка на get_list(f)
	# name (str) имя сета
	def get(self, name): # v2
		pass
		# test data
		if not name:
			return(False, 'Not Name!')
		bool_, r_data = self.get_list(f = {'name': name})
		if not bool_:
			return(False, r_data)
		
		if not r_data:
			return(False, 'A set with that name "%s" was not found' % name)
		else:
			return(True, r_data[0])
	
	# удаление из базы данных
	# name (str) - если False - то удаляется текущий инициализированный объект: удаляется строка из БД - поля объекта переписываются на False.
	def remove(self, name=False): # v2
		pass
		# 1 - удаление записи из БД
		# 2 - перезапись полей в False - если name=False
	
		# (1)
		if name:
			where = {'name': name}
		else:
			where = {'name': self.name}
		bool_, r_data = database().delete('studio', self, self.set_of_tasks_t, where, table_root=self.set_of_tasks_db)
		if not bool_:
			return(False, r_data)
		
		# (2)
		if not name:
			for key in self.set_of_tasks_keys:
				setattr(self, key, False)
		
		return(True, 'ok')
	
	# new_name (str) - новое имя сета
	# name (str) - имя переименоваваемого сета, если False - переименовывается текущий объект.
	def rename(self, new_name, name=False): # v2
		pass
		# 1 - тест на наличие и совпадение имени
		# 2 - перезапись БД
		# 3 - перезапись полей текущего объекта
	
		# (1)
		if not new_name:
			return(False, 'No new name is specified!')
		
		if name:
			old_name = name
		else:
			old_name = self.name
			if not old_name:
				return(False, 'This object is not initialized!')
			
		if old_name == new_name:
			return(False, 'New name matches existing one!')
		
		# (2)
		table_name = self.set_of_tasks_t
		keys = self.set_of_tasks_keys
		update_data = {'name': new_name, 'edit_time':datetime.datetime.now()}
		where = {'name': old_name}
		bool_, r_data = database().update('studio', self, table_name, keys, update_data, where, table_root=self.set_of_tasks_db)
		if not bool_:
			return(False, r_data)
		
		# (3)
		if not name:
			self.name = new_name
			self.edit_time = update_data['edit_time']
			
		return(True, 'ok')
		
	# asset_type (str) - новый тип сета
	# name (str/bool) - имя изменяемого сета, если False - то редактируется текущий объект
	def edit_asset_type(self, asset_type, name=False): # v2
		pass
		# 1 - тест имени и типа
		# 2 - перезапись БД
		# 3 - перезапись полей текущего объекта
	
		# (1)
		if name:
			old_name = name
		else:
			old_name = self.name
			if not old_name:
				return(False, 'This object is not initialized!')
		
		if not asset_type in self.asset_types:
			return(False, 'Wrong type of asset: "%s"' % asset_type)	
				
		# (2)
		table_name = self.set_of_tasks_t
		keys = self.set_of_tasks_keys
		update_data = {'asset_type': asset_type, 'edit_time':datetime.datetime.now()}
		where = {'name': old_name}
		bool_, r_data = database().update('studio', self, table_name, keys, update_data, where, table_root=self.set_of_tasks_db)
		if not bool_:
			return(False, r_data)
		
		# (3)
		if not name:
			self.asset_type = asset_type
			self.edit_time = update_data['edit_time']
			
		return(True, 'ok')
	
	# редактирование именно значения sets
	# data (list) - список словарей по sets_keys
	# name (bool/str) - если False - то редактируется текущий инициализированный объект
	def edit_sets(self, data, name=False): # v2
		pass
		# 1 - тест типа данных data
		# 2 - перезапись БД
		# 3 - редактирование инициализированного объекта, если name=False
		
		# (1)
		if not isinstance(data, list):
			return(False, 'the "data" must be of type "list" but not "%s"' % data.__class__.__name__)
		
		# (2)
		table_name = self.set_of_tasks_t
		keys = self.set_of_tasks_keys
		update_data = {'sets': data, 'edit_time':datetime.datetime.now()}
		if name:
			where = {'name': name}
		else:
			where = {'name': self.name}
		bool_, r_data = database().update('studio', self, table_name, keys, update_data, where, table_root=self.set_of_tasks_db)
		if not bool_:
			return(False, r_data)
		
		# (3)
		if not name:
			self.sets = data
			self.edit_time = update_data['edit_time']
				
		return(True, 'ok')
	
	# создание копии сета
	# new_name (str) - имя создаваемого сета
	# old_name (bool / str) - имя копируемого сета, если False - то копируется текущий.
	def copy(self, new_name, old_name=False): # v2
		pass
		# 1 - тесты имён
		# 2 - создание нового сета
		
		# (1)
		if old_name == new_name:
			return(False, 'Matching names!')
		if not new_name:
			return(False, 'Name not specified!')
		
		# (2)
		if old_name:
			b, source_ob = self.get(old_name)
			if not b:
				return(b, source_ob)
		else:
			source_ob = self
			
		b, r_data = self.create(new_name, source_ob.asset_type, keys = source_ob.sets)
		return(b, r_data) # если  b=True, то r_data - новый объект.
		
	### ****************** Library
	
	# запись в файл json библиотеки наборов задач.
	# path (str) - путь сохранения
	# save_objects (list) - список объектов (set_of_tasks) - если False - то сохраняет всю библиотеку.
	def save_to_library(self, path, save_objects=False): # v2
		pass
		# 1 - получение save_objects
		# 2 - создание словаря save_data по типу json файла
		# 3 - запись данных
		
		# (1)
		if not save_objects:
			b, r = self.get_list()
			if not b:
				return(b, r)
			save_objects = r
			
		# (2)
		save_data = {}
		for ob in save_objects:
			save_data[ob.name] = {}
			for key in self.set_of_tasks_keys:
				if key=='edit_time':
					continue
				save_data[ob.name][key] = getattr(ob, key)
		
		# (3)
		try:
			with open(path, 'w') as f:
				jsn = json.dump(save_data, f, sort_keys=True, indent=4)
				f.close()
		except Exception as e:
			print('***', e)
			return(False, (path + "  can not be write"))
		
		return(True, 'ok')
		
class season(studio):
	def __init__(self, project_ob):
		seasons_list = []
		dict_by_name = {}
		dict_by_id = {}
		
		if not isinstance(project_ob, project):
			raise Exception('in season.__init__() - Object is not the right type "%s", must be "project"' % project_ob.__class__.__name__)
		self.project = project_ob
		# fill fields
		for key in self.season_keys:
			#exec('self.%s = False' % key)
			setattr(self, key, False)
	
	def init(self, name, new=True):
		pass
		# 1 - чтение БД
		# 2 - инициализация по keys
		
		bool_, r_data = database().read('project', self.project, self.season_t, self.season_keys, where={'name': name}, table_root=self.season_db)
		if not bool_:
			return(bool_, r_data)
		if r_data:
			return self.init_by_keys(r_data[0], new=new)
		else:
			if new:
				return None
			else:
				return(False, 'a season with this name "%s" no found!')
		
	
	# заполнение полей по self.season_keys - для передачи экземпляра в уровень ниже.
	# keys (dict) словарь по self.season_keys
	# new (bool) - если True - вернёт новый объект, если False - инициализирует текущий.
	def init_by_keys(self, keys, new=True):
		if new:
			r_ob = season(self.project)
		else:
			r_ob = self
		for key in self.season_keys:
			#exec('self.%s = keys.get("%s")' % (key, key))
			setattr(r_ob, key, keys.get(key))
			
		if new:
			return r_ob
		else:
			return(True, 'Ok!')
		
	
	def create(self, name):
		keys = {}
		keys['name'] = name
		keys['status'] = 'active'
		keys['id'] = uuid.uuid4().hex
		
		# создание таблицы, если не существует. - (не нужно)
		# проверка на существование с даныи именем.
		# добавление сезона.
		
		# проверка на совпадение имени
		ob = self.init(name)
		if isinstance(ob, season):
			return(False, 'Season with this name(%s) already exists!' % keys['name'])
		
		# -- write data
		bool_, return_data = database().insert('project', self.project, self.season_t, self.season_keys, keys, table_root = self.season_db)
		if not bool_:
			return(bool_, return_data)
		return(True, self.init_by_keys(keys))
	
	# status (str) - значения из ['all', 'active', 'none']
	def get_list(self, status='all'):
		pass
	
		#
		if not status in ['all', 'active', 'none']:
			return(False, 'This status (%s) is not correct.' % status)
		
		#
		seasons_list = []
		dict_by_name = {}
		dict_by_id = {}
		
		where = False
		# write season to db
		b, r = database().read('project', self.project, self.season_t, self.season_keys, where=where, table_root=self.season_db)
		if not b:
			return(b, r)
		
		#
		for item in r:
			ob = self.init_by_keys(item)
			seasons_list.append(ob)
			dict_by_name[ob.name] = ob
			dict_by_id[ob.id] = ob
		
		#
		self.__fill_season_class_fields(seasons_list, dict_by_name, dict_by_id)
		
		seasons = []
		for ob in seasons_list:
			if status =='active' and ob.status == 'active':
				seasons.append(ob)
			elif status=='none' and ob.status == 'none':
				seasons.append(ob)
			elif status=='all':
				seasons.append(ob)
			else:
				continue
		return(True, seasons)
	
	@classmethod
	def __fill_season_class_fields(self, seasons_list, dict_by_name, dict_by_id):
		self.seasons_list = seasons_list
		self.dict_by_name = dict_by_name
		self.dict_by_id = dict_by_id

	'''
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
	'''
	
	def rename(self, new_name):
		update_data = {'name': new_name}
		where = {'id': self.id}
		bool_, return_data = database().update('project', self.project, self.season_t, self.season_keys, update_data, where, table_root=self.season_db)
		if not bool_:
			return(bool_, return_data)
		self.name=new_name
		return(True, 'ok')
	
	def stop(self):
		where = {'id': self.id}
		update_data = {'status': u'none'}
		bool_, return_data = database().update('project', self.project, self.season_t, self.season_keys, update_data, where, table_root=self.season_db)
		if not bool_:
			return(bool_, return_data)
		self.status=u'none'
		return(True, 'ok')
	
	def start(self):
		where = {'id': self.id}
		update_data = {'status': u'active'}
		bool_, return_data = database().update('project', self.project, self.season_t, self.season_keys, update_data, where, table_root=self.season_db)
		if not bool_:
			return(bool_, return_data)
		self.status=u'active'
		return(True, 'ok')
	
class group(studio):
	list_group = None
	dict_by_name = None
	dict_by_id = None
	dict_by_type = None
	
	def __init__(self, project_ob):
		if not isinstance(project_ob, project):
			raise Exception('in group.__init__() - Object is not the right type "%s", must be "project"' % project_ob.__class__.__name__)
		self.project = project_ob
		#base fields
		for key in self.group_keys:
			exec('self.%s = False' % key)
	
	# инициализация по имени группы
	# new (bool) - если True - то возвращается новый инициализированный объект класса group, если False - то инициализируется текущий объект
	def init(self, group_name, new = True):
		pass
		# get keys
		bool_, ob = self.get_by_name(group_name)
		if not bool_:
			return(bool_, ob)
		
		if new:
			return(ob)
		else:
			self = ob
			return(True, 'Ok!')
		
	# инициализация по словарю
	# new (bool) - если True - то возвращается новый инициализированный объект класса group, если False - то инициализируется текущий объект
	# keys (dict) - словарь данных группы
	def init_by_keys(self, keys, new = True):
		if new:
			new_group = group(self.project)
			for key in self.group_keys:
				exec('new_group.%s = keys.get("%s")' % (key, key))
			return new_group
		else:
			for key in self.group_keys:
				exec('self.%s = keys.get("%s")' % (key, key))
			return(True, 'Ok!')
	
	# keys - словарь по group_keys (name и type - обязательные ключи)
	def create(self, keys):
		pass
		# test name
		if not keys.get('name'):
			return(False, 'Not Name!')
			
		# test type
		if not keys.get('type') or (not keys.get('type') in self.asset_types):
			return(False, 'Not Type!')
		
		# get id
		keys['id'] = uuid.uuid4().hex
		
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
		pass
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
				names.append(group.name)
				id_s.append(group.id)
				if group.name == self.recycle_bin_name:
					recycle_bin = group
				if group.type == 'recycle_bin':
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
				result = self.dict_by_name[self.recycle_bin_name].rename(new_name)
				if not result[0]:
					return(False, result[1])
				
			# create group
			# -- keys
			keys = {
			'name':self.recycle_bin_name,
			'type': 'recycle_bin',
			'description':'removed assets'
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
			
	# возвращает список групп (объекты) согласно фильтру - заполняет поля класса: list_group, dict_by_name, dict_by_id, dict_by_type
	# f (list) - filter of types список типов
	def get_list(self, f = False): # f = [...] - filter of types список типов
		pass
		# 1 - пустые поля
		# 2 - чтение БД
		# 3 - output list
		# 4 - заполнение полей
		
		# (1)
		list_group = []
		dict_by_name = {}
		dict_by_id = {}
		dict_by_type = {}
		
		# (2)
		bool_, return_data = database().read('project', self.project, self.group_t, self.group_keys, table_root=self.group_db)
		if not bool_:
			return(bool_, return_data)
		
		# (3)
		output_list = []
		if not f:
			for grp_d in return_data:
				output_list.append(self.init_by_keys(grp_d))
		else:
			for grp_d in return_data:
				if grp_d['type'] in f:
					output_list.append(self.init_by_keys(grp_d))
					
		# (4)
		for t in self.asset_types + ['recycle_bin']:
			dict_by_type[t] = []
			
		for d in return_data:
			ob = self.init_by_keys(d)
			list_group.append(ob)
			dict_by_name[ob.name] = ob
			dict_by_id[ob.id] = ob
			dict_by_type[ob.type].append(ob)
			
		self._fill_fields_of_group_class(list_group, dict_by_name, dict_by_id, dict_by_type)
		return(True, output_list)
		
	@classmethod
	def _fill_fields_of_group_class(self, list_group, dict_by_name, dict_by_id, dict_by_type):
		pass
		self.list_group = list_group
		self.dict_by_name = dict_by_name
		self.dict_by_id = dict_by_id
		self.dict_by_type = dict_by_type

	
	''' не нужен так как class.dict_by_id - заполняется в self.get_list()
	def get_groups_dict_by_id(self):
		result = self.get_list()
		if not result[0]:
			return(False, result[1])
		
		group_dict = {}
		for row in result[1]:
			group_dict[row['id']] = row
			
		return(True, group_dict)
	'''
	
	# keys (dict) - словарь по self.group_keys
	# возвращает список объектов
	def get_by_keys(self, keys):
		if not keys:
			return(False, 'Not Keys!')
		elif keys.__class__.__name__ != 'dict':
			return(False, 'Wrong type of keys: %s' % keys.__class__.__name__)
		
		bool_, return_data = database().read('project', self.project, self.group_t, self.group_keys, where = keys, table_root=self.group_db)
		if not bool_:
			return(bool_, return_data)
		
		r_list = []
		for keys in return_data:
			r_list.append(self.init_by_keys(keys))
		
		return(True, r_list)
	
	# обёртка на self.get_by_keys()
	# name (str)
	def get_by_name(self, name):
		rows = self.get_by_keys({'name': name})
		if rows[0] and rows[1]:
			return(True, rows[1][0])
		elif rows[0] and not rows[1]:
			return(False, 'This name(%s) not Found' % name)
		else:
			return(False, rows[1])
	
	# обёртка на self.get_by_keys()
	# id_ (str)
	def get_by_id(self, id_):
		rows = self.get_by_keys({'id': id_})
		if rows[0] and rows[1]:
			return(True, rows[1][0])
		elif rows[0] and not rows[1]:
			return(False, 'This id(%s) not Found' % id_)
		else:
			return(False, rows[1])
	
	# обёртка на self.get_by_keys()
	# season (str)
	def get_by_season(self, season):
		rows = self.get_by_keys({'season': season})
		if rows[0] and rows[1]:
			return(True, rows[1][0])
		elif rows[0] and not rows[1]:
			return(False, 'This season(%s) not Found' % season)
		else:
			return(False, rows[1])
	
	# обёртка на self.get_list()
	# type_list (list) - список типов по self.
	def get_by_type_list(self, type_list):
		data = []
		b, r = self.get_list(f = type_list)
		if not b:
			return(b, r)
				
		return(True, r)
		
	''' не нужен так как class.dict_by_type - заполняется в self.get_list()
	def get_dict_by_all_types(self):
		pass
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
	'''
	
	# переименование текущего объекта
	# new_name (str)
	def rename(self, new_name):
		pass
		update_data = {'name': new_name}
		where = {'id': self.id}
		bool_, return_data = database().update('project', self.project, self.group_t, self.group_keys, update_data, where, table_root=self.group_db)
		if not bool_:
			return(bool_, return_data)
		
		# изменение текущего объекта
		self.name = new_name
		
		return(True, 'ok')
		
	# изменение комента текущего объекта
	# description (str)
	def edit_description(self, description):
		update_data = {'description': description}
		where = {'id': self.id}
		bool_, return_data = database().update('project', self.project, self.group_t, self.group_keys, update_data, where, table_root=self.group_db)
		if not bool_:
			return(bool_, return_data)
		
		self.description = description
		return(True, 'ok')
		
class list_of_assets(studio):
	def __init__(self, group_ob):
		if not isinstance(group_ob, group):
			raise Exception('in list_of_assets.__init__() - Object is not the right type "%s", must be "group"' % group_ob.__class__.__name__)
		self.group = group_ob

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
	
