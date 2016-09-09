# data transfer studio <-> outsource.assets.json
from Lineyka_ import edit_db
reload(edit_db)
from Lineyka_ import edit_db as db

import json
import shutil
import os
import zipfile
import random
import mimetypes
import datetime

'''
class controlled_execution:
	def __enter__(self):
		#set things up
		return 'thing'
	def __exit__(self, type, value, traceback):
		#tear things down
		pass
'''

class data_transfer:
	def __init__(self):
		self.json_name = '.data.json'
		self.to_outsource_prefix = 'toOutsource'
		self.to_studio_prefix = 'toStudio'
		self.send_string = 'sendTask'
		self.change_task_string = 'changeTask'
		self.chat_string = 'chat'
		self.textures = 'textures'
		self.chat_img_dir_name = 'chat_images'
	
	# --------------------------- STUDIO ----------------------------------------------------------------------
	
	def send_task(self, user, project, task_data, *args):
		# -------- get user data ----------
		user_data = db.artist().read_artist({'nik_name':user})
		if user_data[0]:
			share_dir = user_data[1][0]['share_dir']
			outsource = user_data[1][0]['outsource']
		else:
			return False, 'Not Found User Data!'
		
		# -------- make tmp dir ---------------
		if os.path.exists(share_dir):
			dir_name = project + '_' + task_data['task_name'].replace(':','_') + '_' + str(random.randint(0, 1000000))
			tmp_dir = os.path.join(db.studio().tmp_folder, dir_name).replace('\\','/')
			if not os.path.exists(tmp_dir):
				os.mkdir(tmp_dir)
			else:
				shutil.rmtree(tmp_dir)
				while(os.path.exists(tmp_dir)):
					shutil.rmtree(tmp_dir,  ignore_errors)
				os.mkdir(tmp_dir)
		else:
			return False, 'Not Share Dir!'
				
		# get asset data
		asset = db.asset()
		#asset_name = task_data['task_name'].split(':')[0]
		asset_name = task_data['asset']
		asset.get_asset(project, asset_name)
		
		# get chat
		chat = db.chat()
		chat_rows = chat.read_the_chat(project, task_data['task_name'])
		chat_data = []
		chat_images = []
		if chat_rows[0]:
			for message in chat_rows[1]:
				message_data = {}
				for key in message.keys():
					if key == 'date_time':
						dt = message[key]
						message_data[key] = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond)
					elif key == 'topic':
						chat_images.append(json.loads(message[key])[0][0])
						message_data[key] = message[key]
					else:
						message_data[key] = message[key]
				chat_data.append(message_data)
		
		if asset.asset_type == 'char' or asset.asset_type == 'obj':
			# get input_task_data
			task = db.task()
			input_task_data = task.read_task(project, task_data['input'], 'all')
			if input_task_data[0]:
				input_task_data = input_task_data[1]
			else:
				input_task_data = {}
			
			# -------- make json --------------
			jdata = {}
			jdata['chat'] = chat_data
			jdata['action'] = 'send_task'
			jdata['project'] = project
			jdata['asset'] = {'name': asset_name, 'group': asset.asset_group, 'type': asset.asset_type}
			jdata['task'] = task_data
			jdata['input_task'] = input_task_data
			
			json_path = os.path.join(tmp_dir, self.json_name)
			
			with open(json_path, 'w') as f:
				jsn = json.dump(jdata, f, sort_keys=True, indent=4)
				f.close()
				
			# -------- current activity folder ------
			# get final_file
			final_file = asset.get_final_file_path(project, asset_name, task_data['activity'])
			if final_file:
				final_file_name = os.path.basename(final_file)
				# -- make folder
				'''
				cur_root = os.path.join(tmp_dir, self.cur_activity_root)
				os.mkdir(cur_root)
				activity_dir = os.path.join(cur_root, task_data['activity'])			
				os.mkdir(activity_dir)
				'''
				activity_dir = os.path.join(tmp_dir, task_data['activity'])			
				os.mkdir(activity_dir)
				new_file_path = os.path.join(activity_dir, final_file_name).replace('\\','/')
				shutil.copyfile(final_file, new_file_path)
				
			# -------- input activity folder ------
			# -- get input task_data
			'''
			task = db.task()
			input_final_file = False
			input_task_data = task.read_task(project, task_data['input'], 'all')
			if input_task_data[0]:
				input_task_data = input_task_data[1]
				#print input_task_data
				#return
			'''
			input_final_file = asset.get_final_file_path(project, asset_name, input_task_data['activity'])
			if input_final_file:
				input_final_file_name = os.path.basename(input_final_file)
				# -- make folder
				'''
				input_root = os.path.join(tmp_dir, self.input_activity_root).replace('\\','/')
				os.mkdir(input_root)
				activity_dir = os.path.join(input_root, input_task_data['activity'])		
				os.mkdir(activity_dir)
				'''
				activity_dir = os.path.join(tmp_dir, input_task_data['activity'])		
				os.mkdir(activity_dir)
				
				input_new_file_path = os.path.join(activity_dir, input_final_file_name).replace('\\','/')
				shutil.copyfile(input_final_file, input_new_file_path)
					
			# -------- Chat Images ----------
			new_chat_images = []
			if len(chat_images) > 0:
				print '+++++++++++', chat_images
				#return
				chat_img_path = asset.chat_img_path
				chat_img_root = os.path.join(tmp_dir, self.chat_img_dir_name).replace('\\','/')
				os.mkdir(chat_img_root)
				for img in chat_images:
					if not os.path.exists(img):
						continue
					img_name = os.path.basename(img)
					new_img_path = os.path.join(chat_img_root, img_name)
					new_chat_images.append(new_img_path)
					shutil.copyfile(img, new_img_path)
				
			# -------- Textures -------------
			
			textures_path = asset.get_activity_path(project, asset_name, 'textures')
			# -- make folder
			textures_root = os.path.join(tmp_dir, self.textures).replace('\\','/')
			os.mkdir(textures_root)
						
			files = os.listdir(textures_path)
			copy_files = []
			for file_ in files:
				type_ext = mimetypes.guess_type(file_)[0]
				if not type_ext:
					continue
				type = type_ext.split('/')[0]
				ext = type_ext.split('/')[1]
				#print type, ext
				if type == 'image' and (ext == 'png' or ext == 'tiff'):
					shutil.copyfile((os.path.join(textures_path, file_).replace('\\','/')), (os.path.join(textures_root, file_).replace('\\','/')))
					copy_files.append(file_)
					
			'''
			with controlled_execution() as thing:
				shutil.copytree(textures_path, textures_root)
			'''
			
			#shutil.copytree(textures_path, textures_root)
			
			# -------- make zip -------------
			#os.chdir(tmp_dir)
			zip_path = os.path.join(tmp_dir, 'tmp.zip')
			myzip = zipfile.ZipFile(zip_path, 'w')
			myzip.write(json_path, arcname=self.json_name)
			if final_file:
				myzip.write(new_file_path, arcname=(os.path.join(task_data['activity'], final_file_name).replace('\\','/')))
			if input_final_file:
				myzip.write(input_new_file_path, arcname=(os.path.join(input_task_data['activity'], input_final_file_name).replace('\\','/')))
			for files in copy_files:
				this_path = os.path.join(textures_root, files).replace('\\','/')
				myzip.write(this_path, arcname= os.path.join(self.textures, files).replace('\\','/'))
			if len(chat_images) > 0:
				for img in new_chat_images:
					img_name = os.path.basename(img)
					myzip.write(img, arcname= os.path.join(self.chat_img_dir_name, img_name).replace('\\','/'))
			myzip.close()
			#os.chdir(os.path.expanduser('~'))
			
			# copy zip to share dir
			share_zip_name = self.to_outsource_prefix + '_' + project + '_' + task_data['task_name'].replace(':','_') + '.zip'
			share_zip_path = os.path.join(share_dir, share_zip_name).replace('\\','/')
			shutil.copyfile(zip_path, share_zip_path)
			
		return True
	
	def send_chat_to_outsource(self, project, task_name, author, color, message, status):
		copy = db.project()
		copy.get_project(project)
		
		# ------ Get Share_Dir --------
		artist = None
		share_dir = None
		
		# get artist
		task_data = db.task().read_task(project, task_name, ('artist',))
		if task_data[0]:
			artist = task_data[1]['artist']
		else:
			return
		
		# get share_dir
		artist_data = db.artist().read_artist({'nik_name':artist})
		if artist_data[0]:
			share_dir = artist_data[1][0]['share_dir']
		else:
			return
		
		# -------- make tmp dir ---------------
		dir_name = project + '_' + task_name.replace(':','_') + '_' + str(random.randint(0, 1000000))
		tmp_dir = os.path.join(copy.tmp_folder, dir_name).replace('\\','/')
		if not os.path.exists(tmp_dir):
			os.mkdir(tmp_dir)
		else:
			shutil.rmtree(tmp_dir)
			while(os.path.exists(tmp_dir)):
				shutil.rmtree(tmp_dir,  ignore_errors)
			os.mkdir(tmp_dir)
			
		# -------- make .json ------------------
		# get date_time
		dt = datetime.datetime.now()
		date_time = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond)
		
		# get chat data 
		chat_data = {}
		chat_data['author'] = author
		chat_data['color'] = color
		chat_data['status'] = status
		chat_data['message'] = message
		chat_data['date_time'] = date_time
		
		jdata = {}
		jdata['chat'] = chat_data
		jdata['action'] = 'send_chat'
		jdata['project'] = project
		jdata['task'] = {'task_name': task_name}
		
		json_path = os.path.join(tmp_dir, self.json_name)
		
		with open(json_path, 'w') as f:
			jsn = json.dump(jdata, f, sort_keys=True, indent=4)
			f.close()
		
		# ---------- copy Img Files ---------------
		# make chat_img_tmp_path
		new_chat_images = []
		chat_img_path = copy.chat_img_path
		chat_img_tmp_path = os.path.join(tmp_dir, self.chat_img_dir_name).replace('\\','/')
		os.mkdir(chat_img_tmp_path)
		
		# copy img files
		mess = json.loads(message)
		for line in mess:
			img_name = os.path.basename(line[0])
			source_img_path = os.path.join(chat_img_path, img_name).replace('\\','/')
			target_img_path = os.path.join(chat_img_tmp_path, img_name).replace('\\','/')
			if os.path.exists(source_img_path):
				new_chat_images.append(target_img_path)
				shutil.copyfile(source_img_path, target_img_path)
				pass
				
		# ------------ make zip -------------------
		# make zip
		zip_path = os.path.join(tmp_dir, 'tmp.zip')
		myzip = zipfile.ZipFile(zip_path, 'w')
		myzip.write(json_path, arcname=self.json_name)
		for img in new_chat_images:
			img_name = os.path.basename(img)
			myzip.write(img, arcname= os.path.join(self.chat_img_dir_name, img_name).replace('\\','/'))
		myzip.close()
		
		# copy zip to share dir
		share_zip_name = self.to_outsource_prefix + '_' + str(random.randint(0, 1000000)) + '_' + project + '_' + task_name.replace(':','_') + '.zip'
		share_zip_path = os.path.join(share_dir, share_zip_name).replace('\\','/')
		shutil.copyfile(zip_path, share_zip_path)
			
	def studio_pic_up(self):
		# get data_artists 
		artist = db.artist()
		project = db.project()
		
		# ----------- Get Share Dir Lists From Artists ------------
		artists_data = artist.read_artist('all')
		if artists_data[0]:
			artists_data = artists_data[1]
					
		# from share_dirs  WORKING zip : get ACTION (from .json)
		for artist in artists_data:
			if artist['outsource'] == '1':
				share_dir = artist['share_dir']
				if not os.path.exists(share_dir):
					continue
				# ------ WORKING zip ------
				for zip in os.listdir(share_dir):
					result = False
					# EXTRACT ZIP
					current_zip_path = os.path.join(share_dir, zip).replace('\\','/')
					myzip = zipfile.ZipFile(current_zip_path, 'r')
					extract_path = os.path.join(project.tmp_folder, (zip.split('.')[0] + str(random.randint(0, 1000000)))).replace('\\','/')
					os.mkdir(extract_path)
					try:
						myzip.extractall(extract_path)
						myzip.close()
					except:
						myzip.close()
						continue

					# GET ACTION
					# read Json
					json_file = os.path.join(extract_path, self.json_name).replace('\\','/')
					if not os.path.exists(json_file):
						continue						
					with open(json_file, 'r') as read:
						input_data = json.load(read)
					
					action = input_data['action']
					print(action)
					
					# WORK FROM ACTION
					if action == 'send_chat':
						result = self.__to_studio_send_chat_action(input_data, extract_path, project)
					else:
						pass
					
					
					# -------- Remove ZIP -----------
					if result:
						print(result)
						os.remove(current_zip_path)
					else:
						print(result)
						continue
						
	def __to_studio_send_chat_action(self, input_data, extract_path, project):
		#Write chat data
		chat_data = {}
		for key in input_data['chat']:
			if key == 'date_time':
				dt = input_data['chat'][key]
				date_time = datetime.datetime(year = dt[0], month = dt[1], day = dt[2], hour = dt[3], minute = dt[4], second = dt[5])
				chat_data[key] = date_time
			else:
				chat_data[key] = input_data['chat'][key]
		
		project_name = input_data['project']
		task_name = input_data['task']['task_name']
		author = chat_data['author']
		color = chat_data['color']
		message = chat_data['message']
		status = chat_data['status']
		date_time = chat_data['date_time']
		
		result = db.chat().record_messages(project_name, task_name, author, color, message, status, date_time = date_time)
		if not result[0]:
			return(False)
		
		# Copy Img Files
		project.get_project(project_name)
		chat_img_path = project.chat_img_path
		
		source_chat_img_dir = os.path.join(extract_path, self.chat_img_dir_name).replace('\\','/')
		if os.path.exists(source_chat_img_dir):
			list_img = os.listdir(source_chat_img_dir)
			if list_img:
				for img_name in list_img:
					source_path = os.path.join(source_chat_img_dir, img_name).replace('\\','/')
					target_path = os.path.join(chat_img_path, img_name).replace('\\','/')
					shutil.copyfile(source_path, target_path)
		
		# return
		return(True)
	
	# -------------------------- OUTSOURCE ------------------------------------------------------------
	
	def send_chat_to_studio(self, project, task_name, author, color, message, status):
		# -------- get share dir ---------- 
		copy = db.project()
		copy.get_project(project)
		share_dir = copy.get_share_dir()
		if share_dir[0]:
			share_dir = share_dir[1]
		else:
			return(False, 'Not Found Share Dir Data!')
			
			
		# -------- make tmp dir ---------------
		dir_name = project + '_' + task_name.replace(':','_') + '_' + str(random.randint(0, 1000000))
		tmp_dir = os.path.join(copy.tmp_folder, dir_name).replace('\\','/')
		if not os.path.exists(tmp_dir):
			os.mkdir(tmp_dir)
		else:
			shutil.rmtree(tmp_dir)
			while(os.path.exists(tmp_dir)):
				shutil.rmtree(tmp_dir,  ignore_errors)
			os.mkdir(tmp_dir)
					
		# -------- make .json ------------------
		# get date_time
		dt = datetime.datetime.now()
		date_time = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond)
		
		# get chat data 
		chat_data = {}
		chat_data['author'] = author
		chat_data['color'] = color
		chat_data['status'] = status
		chat_data['message'] = message
		chat_data['date_time'] = date_time
		
		jdata = {}
		jdata['chat'] = chat_data
		jdata['action'] = 'send_chat'
		jdata['project'] = project
		jdata['task'] = {'task_name': task_name}
		
		json_path = os.path.join(tmp_dir, self.json_name)
		
		with open(json_path, 'w') as f:
			jsn = json.dump(jdata, f, sort_keys=True, indent=4)
			f.close()
		
		# ---------- copy Img Files ---------------
		# make chat_img_tmp_path
		new_chat_images = []
		chat_img_path = copy.chat_img_path
		chat_img_tmp_path = os.path.join(tmp_dir, self.chat_img_dir_name).replace('\\','/')
		os.mkdir(chat_img_tmp_path)
		
		# copy img files
		mess = json.loads(message)
		for line in mess:
			img_name = os.path.basename(line[0])
			source_img_path = os.path.join(chat_img_path, img_name).replace('\\','/')
			target_img_path = os.path.join(chat_img_tmp_path, img_name).replace('\\','/')
			if os.path.exists(source_img_path):
				new_chat_images.append(target_img_path)
				shutil.copyfile(source_img_path, target_img_path)
				pass
				
		# ------------ make zip -------------------
		# make zip
		zip_path = os.path.join(tmp_dir, 'tmp.zip')
		myzip = zipfile.ZipFile(zip_path, 'w')
		myzip.write(json_path, arcname=self.json_name)
		for img in new_chat_images:
			img_name = os.path.basename(img)
			myzip.write(img, arcname= os.path.join(self.chat_img_dir_name, img_name).replace('\\','/'))
		myzip.close()
		
		# copy zip to share dir
		share_zip_name = self.to_studio_prefix + '_' + str(random.randint(0, 1000000)) + '_' + project + '_' + task_name.replace(':','_') + '.zip'
		share_zip_path = os.path.join(share_dir, share_zip_name).replace('\\','/')
		shutil.copyfile(zip_path, share_zip_path)
		
		print('8'*25, 'shar_dir: ', share_dir, message)
				
	def outsource_pick_up(self):
		project = db.project()
		artist = db.artist()
		
		share_dir = project.get_share_dir()
		if not share_dir[0] or (not os.path.exists(share_dir[1])):
			return(share_dir[1])
		else:
			share_dir = share_dir[1]
		
		for zip in os.listdir(share_dir):
			result = False
			# EXTRACT ZIP
			current_zip_path = os.path.join(share_dir, zip).replace('\\','/')
			myzip = zipfile.ZipFile(current_zip_path, 'r')
			extract_path = os.path.join(project.tmp_folder, (zip.split('.')[0] + str(random.randint(0, 1000000)))).replace('\\','/')
			os.mkdir(extract_path)
			myzip.extractall(extract_path)
			myzip.close()
			#os.remove(current_zip_path)
			
			# GET ACTION
			# read Json
			json_file = os.path.join(extract_path, self.json_name).replace('\\','/')
			if not os.path.exists(json_file):
				return ('****** ' + self.json_name + ' Not Found!')
			with open(json_file, 'r') as read:
				input_data = json.load(read)
			
			action = input_data['action']
			
			# WORK FROM ACTION
			if action == 'send_task':
				result = self.__to_outsource_send_task_action(extract_path, input_data)
			elif action == 'send_chat':
				result = self.__to_outsource_send_chat_action(extract_path, input_data, project)
			else:
				pass
				
			# -------- Remove ZIP -----------
			if result:
				print(result)
				os.remove(current_zip_path)
			else:
				print(result)
				continue
			
		return True
		
	def __to_outsource_send_chat_action(self, extract_path, input_data, project):
		#Write chat data
		chat_data = {}
		for key in input_data['chat']:
			if key == 'date_time':
				dt = input_data['chat'][key]
				date_time = datetime.datetime(year = dt[0], month = dt[1], day = dt[2], hour = dt[3], minute = dt[4], second = dt[5])
				chat_data[key] = date_time
			else:
				chat_data[key] = input_data['chat'][key]
		
		project_name = input_data['project']
		task_name = input_data['task']['task_name']
		author = chat_data['author']
		color = chat_data['color']
		message = chat_data['message']
		status = chat_data['status']
		date_time = chat_data['date_time']
		
		result = db.chat().record_messages(project_name, task_name, author, color, message, status, date_time = date_time)
		if not result[0]:
			return(False)
		
		# Copy Img Files
		project.get_project(project_name)
		chat_img_path = project.chat_img_path
		
		source_chat_img_dir = os.path.join(extract_path, self.chat_img_dir_name).replace('\\','/')
		if os.path.exists(source_chat_img_dir):
			list_img = os.listdir(source_chat_img_dir)
			if list_img:
				for img_name in list_img:
					source_path = os.path.join(source_chat_img_dir, img_name).replace('\\','/')
					target_path = os.path.join(chat_img_path, img_name).replace('\\','/')
					shutil.copyfile(source_path, target_path)
		
		# return
		return(True)

	
	def __to_outsource_send_task_action(self, extract_path, input_data):
		# PROJECT
		copy = db.task()
		project_name = input_data['project']
		if not copy.get_project(project_name):
			# create project folder
			project_path = os.path.join(copy.studio_folder, project_name).replace('\\','/')
			if not os.path.exists(project_path):
				os.mkdir(project_path)
			# create project
			copy.add_project(project_name, project_path)
			
		# ASSET
		asset_name = input_data['asset']['name']
		type = input_data['asset']['type']
		group = input_data['asset']['group']
		if not copy.get_asset(project_name, asset_name)[0]:
			# create asset
			#print asset_name, type, group
			copy.add_asset(project_name, type, group, asset_name)
		
		# TASK
		if type == 'char' or type == 'obj':
			# -- -- input_task
			if input_data['input_task']:
				exists_task = False
				if copy.task_list:
					if not input_data['input_task']['task_name'] in copy.task_list:
						# create task
						copy.add_task(project_name, input_data['input_task'])
					else:
						exists_task = True
						copy.edit_task(project_name, input_data['input_task'])
				else:
					# create task
					copy.add_task(project_name, input_data['input_task'])
			# -- -- get new copy.task_list
			copy.get_asset(project_name, asset_name)
			
			# -- -- task
			exists_task = False
			
			########
			# change task status
			if input_data['task']['status'] == 'ready_to_send':
				input_data['task']['status'] = 'ready'
			########
						
			if copy.task_list:
				if not input_data['task']['task_name'] in copy.task_list:
					# create task
					copy.add_task(project_name, input_data['task'])
				else:
					exists_task = True
					copy.edit_task(project_name, input_data['task'])
			else:
				# create task
				copy.add_task(project_name, input_data['task'])
		'''
		# TEXTURES
		in_textures = os.path.join(extract_path, self.textures)
		textures_activity = copy.get_activity_path(project_name, asset_name, 'textures')
		if os.path.exists(in_textures):
			contents = os.listdir(in_textures)
			for content in contents:
				in_path = os.path.join(in_textures, content)
				copy_path = os.path.join(textures_activity, content)
				shutil.copyfile(in_path, copy_path)
		'''
		# CHAT
		chat = db.chat()
		chat.get_project(project_name)
		chat_img_path = chat.chat_img_path
		
		#if not exists_task:
		if not exists_task:
			# -- write CHAT
			for mess in input_data['chat']:
				# -- -- edit message
				for key in mess:
					if key == 'date_time':
						date_time = datetime.datetime(year = mess[key][0], month = mess[key][1], day = mess[key][2], hour = mess[key][3], minute = mess[key][4], second = mess[key][5])
						mess[key] = date_time
					elif key == 'topic':
						new_topic = []
						topic = json.loads(mess[key])
						img_path = topic[0][0]
						file_name = os.path.basename(img_path)
						new_img_path = os.path.join(chat_img_path, file_name).replace('\\','/')
						new_topic.append(new_img_path)
						new_topic.append(topic[0][1])
						mess[key] = json.dumps([new_topic])
				# -- -- write message
				task_name = input_data['task']['task_name']
				author = mess['author']
				color = mess['color']
				topic = mess['topic']
				status = mess['status']
				dateTime = mess['date_time']
				chat.record_messages(project_name, task_name, author, color, topic, status, date_time = dateTime)
			# -- copy chat IMAGES		
			source_chat_img_dir = os.path.join(extract_path, self.chat_img_dir_name).replace('\\','/')
			if os.path.exists(source_chat_img_dir):
				list_img = os.listdir(source_chat_img_dir)
				if list_img:
					for img_name in list_img:
						source_path = os.path.join(source_chat_img_dir, img_name).replace('\\','/')
						target_path = os.path.join(chat_img_path, img_name).replace('\\','/')
						shutil.copyfile(source_path, target_path)
		
		# PUSH ACTIVITY FILES
		contents = os.listdir(extract_path)
		for content in contents:
			if (content in copy.activity_folder.keys()) and (content != self.textures):
				f_names = os.listdir(os.path.join(extract_path, content))
				files = []
				for file_name in f_names:
					files.append(os.path.join(extract_path, content, file_name).replace('\\','/'))
				
				self.__push_activity(input_data, files, content)
				
		return(True)
		
	def __push_activity(self, input_data, files, activity):
		copy = db.task()
		project_name = input_data['project']
		asset_name = input_data['task']['asset']
		task_name = input_data['task']['task_name']
		
		# COPY FILE
		for file in files:
			musor, ext = os.path.splitext(file)
			copy.extension = ext
			new_path = copy.get_new_file_path(project_name, asset_name, activity)
			if not os.path.exists(new_path[0]):
				os.mkdir(new_path[0])
			shutil.copyfile(file, new_path[1])
			
		# LOG
		log = db.log()
		log_keys = {}
		log_keys['task_name'] = task_name
		log_keys['activity'] = activity
		log_keys['action'] = 'push'
		log_keys['comment'] = 'send task'
		log_keys['version'] = os.path.basename(new_path[0])
		
		# -- write log
		print(log.notes_log(project_name, log_keys))
		
		