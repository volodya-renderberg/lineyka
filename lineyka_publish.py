#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import shutil
import platform
import subprocess

#import edit_db

class publish:
	def __init__(self, NormPath):
		self.NormPath = NormPath
	
	def publish(self, task_ob):
		# get final file path
		result = task_ob.get_final_file_path()
		if not result[0]:
			return(False, result[1])
			
		self.final_file_path = result[1]
		self.asset_path = result[2]
		
		if task_ob.task_type == 'sketch':
			result = self.publish_sketch(task_ob)
			if not result[0]:
				return(False, result[1])
		elif task_ob.task_type in ['model', 'sculpt']:
			result = self.publish_model(task_ob)
			if not result[0]:
				return(False, result[1])
		elif task_ob.task_type in ['rig']:
			result = self.publish_rig(task_ob)
			if not result[0]:
				return(False, result[1])
		elif task_ob.task_type in ['animation_shot']:
			result = self.moving_files(task_ob)
			if not result[0]:
				return(False, result[1])
		elif task_ob.task_type in ['simulation_din', 'render']:
			result = self.publish_simulation_render(task_ob)
			if not result[0]:
				return(False, result[1])
		else:
			result = self.moving_files(task_ob)
			if not result[0]:
				return(False, result[1])
		
		return(True, 'Ok')
		
	def publish_simulation_render(self, task_ob):
		result = self.moving_files(task_ob)
		if not result[0]:
			return(False, result[1])
		
		if task_ob.extension == '.blend':
			# get src_physics_dir_path
			scr_physics_dir = os.path.dirname(self.final_file_path)
			physics_dir_name = 'blendcache_%s' % task_ob.asset
			src_physics_dir_path = self.NormPath(os.path.join(scr_physics_dir, physics_dir_name))
			
			# get dst_physics_dir_path
			publish_dir = os.path.dirname(self.publish_file_path)
			dst_physics_dir_path = self.NormPath(os.path.join(publish_dir, physics_dir_name))
			
			if os.path.exists(dst_physics_dir_path):
				shutil.rmtree(dst_physics_dir_path)
			
			if os.path.exists(src_physics_dir_path):
				shutil.copytree(src_physics_dir_path, dst_physics_dir_path)
		
		return(True, 'Ok')
		
	def publish_rig(self, task_ob):
		result = self.moving_files(task_ob)
		if not result[0]:
			return(False, result[1])
			
		return(True, 'Ok')
		
	def publish_model(self, task_ob):
		if not self.final_file_path:
			return(False, 'Not Publish - Not Final File!')
		
		res, data  = self.moving_files(task_ob)
		if not res:
			return(False, data) 
		
		return(True, 'Ok')
		
	def publish_sketch(self, task_ob):
		if not self.final_file_path:
			return(False, 'Not Publish - Not Final File!')
        
		res, data  = self.moving_files(task_ob)
		if not res:
			return(False, data)
		new_file_path = data
		'''
		#  ************* moving Files
		# -- get publish folder path
		activity_dir_name = self.task.ACTIVITY_FOLDER[self.task_data['asset.type']][self.task_data['activity']]
		
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
		png_path = new_file_path.replace(task_ob.extension, '.png')
		
		if not task_ob.convert_exe:
			return(False, 'The path to the "convert.exe" is not defined!')
		cmd = '\"' + task_ob.convert_exe + '\" \"' + new_file_path + '\" -flatten \"' + png_path + '\"'
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
	def moving_files(self, task_ob):
		#  ************* moving Files
		# -- get publish folder path
		activity_dir_name = task_ob.asset.ACTIVITY_FOLDER[task_ob.asset.type][task_ob.activity]
		
		publish_dir = self.NormPath(os.path.join(self.asset_path, task_ob.publish_folder_name))
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