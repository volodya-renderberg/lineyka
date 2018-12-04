#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import shutil
import platform
import subprocess

#import edit_db

class publish:
	def __init__(self, task, NormPath):
		self.task = task
		self.NormPath = NormPath
	
	
	def publish(self, task_data):
		# get final file path
		result = self.task.get_final_file_path(task_data)
		if not result[0]:
			return(False, result[1])
			
		#self.project = self.task.asset.project
		self.task_data = task_data
		self.final_file_path = result[1]
		self.asset_path = result[2]
		
		if self.task_data['task_type'] == 'sketch':
			result = self.publish_sketch()
			if not result[0]:
				return(False, result[1])
		elif self.task_data['task_type'] in ['model', 'sculpt']:
			result = self.publish_model()
			if not result[0]:
				return(False, result[1])
		elif self.task_data['task_type'] in ['rig']:
			result = self.publish_rig()
			if not result[0]:
				return(False, result[1])
		elif self.task_data['task_type'] in ['animation_shot']:
			result = self.moving_files()
			if not result[0]:
				return(False, result[1])
		elif self.task_data['task_type'] in ['simulation_din', 'render']:
			result = self.publish_simulation_render()
			if not result[0]:
				return(False, result[1])
		else:
			result = self.moving_files()
			if not result[0]:
				return(False, result[1])
		
		return(True, 'Ok')
		
	def publish_simulation_render(self):
		result = self.moving_files()
		if not result[0]:
			return(False, result[1])
		
		if self.task_data['extension'] == '.blend':
			# get src_physics_dir_path
			scr_physics_dir = os.path.dirname(self.final_file_path)
			physics_dir_name = 'blendcache_' + self.task_data['asset']
			src_physics_dir_path = self.NormPath(os.path.join(scr_physics_dir, physics_dir_name))
			
			# get dst_physics_dir_path
			publish_dir = os.path.dirname(self.publish_file_path)
			dst_physics_dir_path = self.NormPath(os.path.join(publish_dir, physics_dir_name))
			
			if os.path.exists(dst_physics_dir_path):
				shutil.rmtree(dst_physics_dir_path)
			
			if os.path.exists(src_physics_dir_path):
				shutil.copytree(src_physics_dir_path, dst_physics_dir_path)
		
		return(True, 'Ok')
		
	def publish_rig(self):
		result = self.moving_files()
		if not result[0]:
			return(False, result[1])
			
		return(True, 'Ok')
		
	def publish_model(self):
		if not self.final_file_path:
			return(False, 'Not Publish - Not Final File!')
		
		res, data  = self.moving_files()
		if not res:
			return(False, data) 
		
		return(True, 'Ok')
		
	def publish_sketch(self):
		if not self.final_file_path:
			return(False, 'Not Publish - Not Final File!')
        
		res, data  = self.moving_files()
		if not res:
			return(False, data)
		new_file_path = data
		'''
		#  ************* moving Files
		# -- get publish folder path
		activity_dir_name = self.task.ACTIVITY_FOLDER[self.task_data['asset_type']][self.task_data['activity']]
		
		publish_dir = self.NormPath(os.path.join(self.asset_path, self.task.publish_folder_name))
		if not os.path.exists(publish_dir):
			os.mkdir(publish_dir)
		
		# -- get activity dir
		publish_activity_dir = self.NormPath(os.path.join(publish_dir, activity_dir_name))
		if not os.path.exists(publish_activity_dir):
			os.mkdir(publish_activity_dir)
		
		# -- new file path
		file_name = os.path.basename(self.final_file_path)
		new_file_path = self.NormPath(os.path.join(publish_activity_dir, file_name))
		
		# -- moving file
		shutil.copyfile(self.final_file_path, new_file_path)
		'''
				
		#  ************* Convert to PNG
		#print(self.task.convert_exe, new_file_path, png_path)
		png_path = new_file_path.replace(self.task_data['extension'], '.png')
		
		cmd = '\"' + self.task.convert_exe + '\" \"' + new_file_path + '\" -flatten \"' + png_path + '\"'
		#print(cmd)
		
		try:
			#os.system(cmd)
			subprocess.Popen(cmd, shell = True)
		except Exception as e:
			print('#'*3)
			print(e)
			return(False, 'in publish_sketch - problems with conversion into .png\n Look the terminal!')
		
		
		return(True, 'Ok')
		
	## UTILITS
	def moving_files(self):
		#  ************* moving Files
		# -- get publish folder path
		activity_dir_name = self.task.asset.ACTIVITY_FOLDER[self.task_data['asset_type']][self.task_data['activity']]
		
		publish_dir = self.NormPath(os.path.join(self.asset_path, self.task.publish_folder_name))
		if not os.path.exists(publish_dir):
			os.mkdir(publish_dir)
		
		# -- get activity dir
		publish_activity_dir = self.NormPath(os.path.join(publish_dir, activity_dir_name))
		if not os.path.exists(publish_activity_dir):
			os.mkdir(publish_activity_dir)
			
		# -- new file path
		if self.final_file_path:
			file_name = os.path.basename(self.final_file_path)
			new_file_path = self.NormPath(os.path.join(publish_activity_dir, file_name))
			
			self.publish_file_path = new_file_path
			
			# -- moving file
			shutil.copyfile(self.final_file_path, new_file_path)
		
		return(True, new_file_path)