#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PySide import QtCore, QtGui, QtUiTools, QtSql
import os
import shutil
import webbrowser
import getpass
from functools import partial
import json
import random
import subprocess
import datetime

import ui
import edit_db as db

# /home/vofka/Yandex.Disk/Lineyka_/lineyka_user.py

class G(object):
	current_project = ''
	current_user = ''
	current_task = {}
	current_file = ''
	action = 'work_list'
	
	task_list = []
	working_task_list = []
	all_task_list = {}
	versions_list = []
	
	task_look_statuses = [
	'ready',
	'work',
	'pause',
	'recast',
	'checking',
	]
	
	not_used_extensions = [
	'.blend','.tiff', '.ods', '.xcf', '.svg'
	]

class MainWindow(QtGui.QMainWindow):
	def __init__(self, parent = None):
		# moduls
		self.db_studio = db.studio()
		self.db_artist = db.artist()
		self.db_task = db.task()
		self.db_log = db.log()
		self.db_chat = db.chat()
		
		# get Path
		path = os.path.dirname(ui.__file__)
		self.ui_folder = path
		self.main_window_path = os.path.join(path, "lineyka_user.ui")
		
		# other path
		# -- chat
		self.chat_main_path = os.path.join(path, "chat_dialog.ui")
		self.chat_add_topic_path = os.path.join(path, "chat_add_topic.ui")
		self.chat_img_viewer_path = os.path.join(path, "chat_img_viewer.ui")
		# -- other
		self.set_window_path = os.path.join(path, "qt_settings.ui")
		self.login_window_path = os.path.join(path, "qt_login.ui")
		self.user_registr_window_path = os.path.join(path, "qt_registration.ui")
		self.qt_set_project_path = os.path.join(path, "qt_set_project.ui")
		self.new_dialog_path = os.path.join(path, "new_dialog.ui")
		self.combo_dialog_path = os.path.join(path, "combo_dialog.ui")
		self.new_dialog_2_path = os.path.join(path, 'new_dialog_two_field.ui')
		self.new_dialog_3_path = os.path.join(path, 'new_dialog_three_field.ui')
		self.new_dialog_4_path = os.path.join(path, 'new_dialog_four_field.ui')
		self.artist_dialog_path = os.path.join(path, "artist_dialog.ui")
		self.select_from_list_dialog_path = os.path.join(path, "select_from_list_dialog.ui")
		self.select_from_list_dialog_combobox_path = os.path.join(path, "select_from_list_dialog_combobox.ui")
		self.select_from_list_dialog_3button_path = os.path.join(path, "select_from_list_dialog_3_button.ui")
		self.select_from_check_button_dialog_path = os.path.join(path, "select_from_check_button_dialog.ui")
		
		# create widget
		QtGui.QMainWindow.__init__(self, parent)
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.main_window_path)
		file.open(QtCore.QFile.ReadOnly)
		self.myWidget = loader.load(file, self)
		file.close()
		
		# edit widgets
		# -- radio buttons
		self.myWidget.work_list_radio_button.setText('Work List')
		self.myWidget.work_list_radio_button.setChecked(True)
		self.myWidget.chek_list_radio_button.setText('Check List')
		
		
		# radio_button connect
		self.myWidget.chek_list_radio_button.clicked.connect(partial(self.load_task_list_table, '', get_project_name = True, action = 'check_list'))
		self.myWidget.work_list_radio_button.clicked.connect(partial(self.load_task_list_table, '', get_project_name = True, action = 'work_list'))
		# menu connect
		self.myWidget.actionSet_studio.triggered.connect(self.set_studio_ui)
		self.myWidget.actionLogin.triggered.connect(self.user_login_ui)
		self.myWidget.actionRegistration.triggered.connect(self.user_registration_ui)
		self.myWidget.actionUser_manual.triggered.connect(self.help_user_manual)
		
		# button connect
		self.myWidget.look_button.clicked.connect(self.look_file_action)
		self.myWidget.look_version_button.clicked.connect(self.look_version_ui)
		self.myWidget.chat_button.clicked.connect(self.chat_ui)
		self.myWidget.chat_button_2.clicked.connect(self.chat_ui)
		self.myWidget.tz_button.clicked.connect(self.tz)
		self.myWidget.tz_button_2.clicked.connect(self.tz)
		
		self.myWidget.open_button.clicked.connect(self.open_action)
		self.myWidget.open_version_button.clicked.connect(partial(self.look_version_ui, look = False))
		self.myWidget.open_version_button_2.clicked.connect(partial(self.look_version_ui, look = False))
		self.myWidget.open_from_input_button.clicked.connect(self.open_input_action)
		self.myWidget.open_from_input_button_2.clicked.connect(self.open_input_action)
		self.myWidget.open_from_file_button.clicked.connect(self.open_from_file_action)
		
		self.myWidget.push_button.clicked.connect(self.push_comment_ui)
		self.myWidget.report_button.clicked.connect(self.report_action)
		self.myWidget.show_task_list_button.clicked.connect(self.show_task_list)
		
		# comobox connect
		try:
			self.myWidget.project_box.activated[str].disconnect()
		except:
			pass
		self.myWidget.project_box.activated[str].connect(self.determinant_of_that_load)
		
		# hide widget
		self.myWidget.outsource_loader_button.setVisible(False)
		self.myWidget.task_info.setVisible(False)
		self.myWidget.distrib_frame.setVisible(False)
		self.myWidget.work_frame.setVisible(False)
		
		self.load_project_list()
		self.load_nik_name()
						
	# *********************** Task List **************************************************
	def show_task_list(self):
		self.myWidget.task_list_table.setVisible(True)
		self.load_task_list_table(self, G.current_project)
		
	def determinant_of_that_load(self, project_name):
		if self.myWidget.work_list_radio_button.isChecked():
			self.load_task_list_table(project_name)
		elif self.myWidget.chek_list_radio_button.isChecked():
			self.load_task_list_table(project_name, action = 'check_list')
	
	def load_task_list_table(self, project_name, get_project_name = False, action = 'work_list'):
		G.action = action
		
		self.myWidget.task_list_table.setVisible(True)
		if get_project_name:
			project_name = self.myWidget.project_box.currentText()
			
		if project_name == '--select project--':
			G.current_project = ''
			self.clear_table()
			
			# hide widgets
			self.myWidget.task_info.setVisible(False)
			self.myWidget.distrib_frame.setVisible(False)
			self.myWidget.work_frame.setVisible(False)
			return
			
		G.current_project = project_name
		
		G.working_task_list = []
		result = (False, 'fack!')
		if action == 'work_list':
			result = self.db_task.get_task_list_of_artist(G.current_project, G.current_user)
		elif action == 'check_list':
			result = self.db_task.get_chek_list_of_artist(G.current_project, G.current_user)
		if not result[0]:
			G.task_list = []
			self.message(result[1], 2)
			
			# hide widgets
			self.myWidget.task_info.setVisible(False)
			self.myWidget.distrib_frame.setVisible(False)
			self.myWidget.work_frame.setVisible(False)
			return
		
		# get G.working_task_list
		if action == 'work_list':
			G.all_task_list = result[1]
			for key in G.all_task_list:
				if G.all_task_list[key]['task']['status'] in G.task_look_statuses:
					G.working_task_list.append(G.all_task_list[key]['task'])
		elif action == 'check_list':
			G.working_task_list = result[1]
				#print(G.all_task_list[key]['task']['task_name'])
		
		
		# make table
		headers = ['icon', 'task_name','activity', 'extension', 'status']
		
		self.myWidget.task_list_table.setColumnCount(len(headers))
		self.myWidget.task_list_table.setRowCount(len(G.working_task_list))
		self.myWidget.task_list_table.setHorizontalHeaderLabels(headers)
		
		# selection mode   
		self.myWidget.task_list_table.setSortingEnabled(True)
		self.myWidget.task_list_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.myWidget.task_list_table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		
		# fill table
		for i, task in enumerate(G.working_task_list):
			for j,key in enumerate(headers):
				if key != 'icon':
					newItem = QtGui.QTableWidgetItem()
					newItem.setText(task[key])
					newItem.task = False
					newItem.task = task
				
				if key == 'task_name':
					color = QtGui.QColor(255, 241, 150)
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
					#newItem.task = task
					
				elif key == 'status':
					rgb = self.db_task.color_status[task['status']]
					r = (rgb[0]*255)
					g = (rgb[1]*255)
					b = (rgb[2]*255)
					color = QtGui.QColor(r, g, b)
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
					
				elif key == 'icon':
					path = os.path.join(self.db_task.preview_img_path, (task['asset'] + '_icon.png'))
					label = QtGui.QLabel()
					if os.path.exists(path):
						image = QtGui.QImage(path)
						pix = QtGui.QPixmap(image)
						label.setPixmap(pix)
					else:
						label.setText('no Images')
						
					label.show()
					self.myWidget.task_list_table.setCellWidget(i, j, label)
						
				
				if key != 'icon':
					self.myWidget.task_list_table.setItem(i, j, newItem)
		
		self.myWidget.task_list_table.resizeRowsToContents()
		self.myWidget.task_list_table.resizeColumnsToContents()
		
		# table connect
		try:
			self.myWidget.task_list_table.itemClicked.disconnect()
		except:
			pass
		if action == 'work_list':
			self.myWidget.task_list_table.itemClicked.connect(self.fill_distrib_panel)
		elif action == 'check_list':
			self.myWidget.task_list_table.itemClicked.connect(self.fill_chek_panel)
		
		# hide widgets
		self.myWidget.task_info.setVisible(False)
		self.myWidget.distrib_frame.setVisible(False)
		self.myWidget.work_frame.setVisible(False)
		self.myWidget.current_file.setVisible(False)
										
		return(True, 'Ok')
	
	# *********************** Task DISTRIB ***********************************************
	def fill_distrib_panel(self, *args):
		G.current_task = self.myWidget.task_list_table.currentItem().task
		
		self.myWidget.distrib_frame.setVisible(True)
		self.myWidget.work_frame.setVisible(False)
		self.fill_info_panel()
		self.get_versions_list()
		
		# edit buttons
		# -- chat button
		self.myWidget.chat_button.clicked.disconnect()
		self.myWidget.chat_button.clicked.connect(self.chat_ui)
		# -- open button
		self.myWidget.open_button.clicked.disconnect()
		self.myWidget.open_button.setText('Open')
		self.myWidget.open_button.clicked.connect(self.open_action)
		# -- open version
		self.myWidget.open_version_button.clicked.disconnect()
		self.myWidget.open_version_button.setText('Open Version')
		self.myWidget.open_version_button.clicked.connect(partial(self.look_version_ui, look = False))
		# -- open from input
		self.myWidget.open_from_input_button.setVisible(True)
		self.myWidget.open_from_input_button.clicked.disconnect()
		self.myWidget.open_from_input_button.clicked.connect(self.open_input_action)
		# -- open from file
		self.myWidget.open_from_file_button.setVisible(True)
		self.myWidget.open_from_file_button.clicked.disconnect()
		self.myWidget.open_from_file_button.clicked.connect(self.open_from_file_action)
		
		
	def fill_chek_panel(self, *args):
		G.current_task = self.myWidget.task_list_table.currentItem().task
		self.myWidget.distrib_frame.setVisible(True)
		self.myWidget.work_frame.setVisible(False)
		self.fill_info_panel()
		
		# edit buttons
		self.myWidget.chat_button.clicked.disconnect()
		self.myWidget.chat_button.clicked.connect(partial(self.chat_ui, chat_status = 'manager'))
		# -- open button
		self.myWidget.open_button.clicked.disconnect()
		self.myWidget.open_button.setText('Accept')
		self.myWidget.open_button.clicked.connect(self.accept_action)
		# -- open version
		self.myWidget.open_version_button.clicked.disconnect()
		self.myWidget.open_version_button.setText('To Rework')
		self.myWidget.open_version_button.clicked.connect(self.to_rework_action)
		# -- open from input
		self.myWidget.open_from_input_button.setVisible(False)
		self.myWidget.open_from_file_button.setVisible(False)
	
	def fill_info_panel(self):
		if G.action == 'work_list':
			string = 'name:' + ' '*10 + G.current_task['task_name'].replace(':',' : ')  + '\n'
			string = string + 'activity:' + ' '*16 + G.current_task['activity']  + '\n'
			if G.all_task_list[G.current_task['task_name']]['input']:
				string = string + 'input activity:' + ' '*10 + G.all_task_list[G.current_task['task_name']]['input']['activity']  + '\n'
			else:
				string = string + 'input activity:' + ' '*10 + 'None\n'
			string = string + 'status:' + ' '*18 + G.current_task['status']  + '\n'
			string = string + 'extension:' + ' '*15 + G.current_task['extension']  + '\n'
			string = string + 'priority:' + ' '*16 + G.current_task['priority']  + '\n'
			string = string + 'price:' + ' '*19 + str(G.current_task['price'])  + '\n'
		elif G.action == 'check_list':
			string = 'name:' + ' '*10 + G.current_task['task_name'].replace(':',' : ')  + '\n'
			string = string + 'activity:' + ' '*16 + G.current_task['activity']  + '\n'
			string = string + 'extension:' + ' '*15 + G.current_task['extension']  + '\n'
			string = string + 'priority:' + ' '*16 + G.current_task['priority']  + '\n'
			string = string + 'artist:' + ' '*19 + G.current_task['artist']  + '\n'
		
		self.myWidget.task_info.clear()
		self.myWidget.task_info.append(string)
		
		self.myWidget.task_info.setVisible(True)
	
	# ***************** Functional ********************************
	def tz(self):
		if G.current_task['tz']:
			webbrowser.open_new_tab(G.current_task['tz'])
		else:
			self.message('Not Link!', 2)
			
	def report_action(self):
		if not G.versions_list:
			self.message('Not Versions of Activity', 2)
			return
		
		# ask
		ask = self.message(('Submit?'), 0)
		if not ask:
			return
		
		# change status in db
		result = self.db_task.change_work_statuses(G.current_project, [(G.current_task, 'checking')])
		if not result[0]:
			self.message(result[1], 2)
			return
		
		# change current status
		G.current_task['status'] = 'checking'
		self.show_task_list()
		
			
	def look_file_action(self):
		task_data = G.current_task
		
		result = self.db_task.get_final_file_path(G.current_project, task_data)
		if not result[0]:
			return(False, result[1])
		
		open_path = result[1]
		
		if not open_path:
			#return(False, 'Not Saved Version!')
			self.message('Not Saved Version!', 2)
		
		# get tmp_file_path
		tmp_path = self.db_task.tmp_folder
		tmp_file_name = task_data['task_name'].replace(':','_', 2) + '_' + hex(random.randint(0, 1000000000)).replace('0x', '') + task_data['extension']
		tmp_file_path = os.path.join(tmp_path, tmp_file_name)
				
		# copy to tmp
		shutil.copyfile(open_path, tmp_file_path)
		
		# vising current file
		G.current_file = tmp_file_path
		self.myWidget.current_file.setText(G.current_file)
		self.myWidget.current_file.setVisible(True)
				
		# open file
		soft = self.db_studio.soft_data[task_data['extension']]
		#cmd = soft + " \"" + tmp_file_path + "\""
		cmd = "\"" + soft + "\"  \"" + tmp_file_path + "\""
		subprocess.Popen(cmd, shell = True)
		
		print(cmd)
	
	def look_version_action(self, window, look = True):
		# get version
		list_items = []
		select_items = window.select_from_list_data_list_table.selectedItems()
		for item in select_items:
			if item.log:
				list_items.append(item.log)
				
		if not list_items:
			self.message('Not Selected Versions!', 2)
			return
			
		version = list_items[0]['version']
		
		# get file_path
		result = self.db_task.get_version_file_path(G.current_project, G.current_task, version)
		if not result[0]:
			return(False, result[1])
			
		open_path = result[1]
		
		if not open_path:
			return(False, 'Not Saved Version!')
			
		# get tmp_file_path
		task_data = G.current_task
		tmp_path = self.db_task.tmp_folder
		tmp_file_name = task_data['task_name'].replace(':','_', 2) + '_' + hex(random.randint(0, 1000000000)).replace('0x', '') + task_data['extension']
		tmp_file_path = os.path.join(tmp_path, tmp_file_name)
		
		# vising current file
		G.current_file = tmp_file_path
		self.myWidget.current_file.setText(G.current_file)
		
		# copy to tmp
		shutil.copyfile(open_path, tmp_file_path)
				
		# open file
		soft = self.db_studio.soft_data[task_data['extension']]
		#cmd = soft + " \"" + tmp_file_path + "\""
		cmd = "\"" + soft + "\"  \"" + tmp_file_path + "\""
		subprocess.Popen(cmd, shell = True)
		
		if not look:
			# ***** CHANGE STATUS
			if G.current_task['status'] != 'work':
				#result = G.func.open_change_status(G.current_project, G.current_task, G.all_task_list)
				change_statuses = [(G.current_task, 'work'),]
				for task_name in G.all_task_list:
					if G.all_task_list[task_name]['task']['status'] == 'work':
						change_statuses.append((G.all_task_list[task_name]['task'], 'pause',))
			
				result = self.db_task.change_work_statuses(G.current_project, change_statuses)
				if not result[0]:
					self.message(result[1], 2)
					#return
				
				else:
					G.current_task['status'] = 'work'
					# result[1] = dict {task_name : new_status, ...}
					for task_name in result[1]:
						G.all_task_list[task_name]['task']['status'] = result[1][task_name]
				G.current_task['status'] = 'work'
				
			# ****** edit widget visible
			self.myWidget.task_list_table.setVisible(False)
			self.myWidget.distrib_frame.setVisible(False)
			self.myWidget.work_frame.setVisible(True)
			self.myWidget.current_file.setVisible(True)
			
			self.close_window(window)
		
	def push_action(self, window):
		# ****** Get Comment
		comment = window.new_dialog_name.text()
		if not comment:
			self.message('Not Comment!', 2)
			return
		
		# ****** COPY to ACtTIVITY
		result = self.db_task.get_new_file_path(G.current_project, G.current_task)
		if not result[0]:
			self.message(result[1], 3)
			return
		
		new_dir_path, new_file_path = result[1]
		
		# make version folder
		if not os.path.exists(new_dir_path):
			os.mkdir(new_dir_path)
		
		# copy file
		if os.path.exists(G.current_file):
			shutil.copyfile(G.current_file, new_file_path)
		else:
			current_file_path = self.myWidget.current_file.text()
			if os.path.exists(current_file_path):
				ask = self.message(('This is your File? ' + current_file_path), 0)
				if ask:
					G.current_file = current_file_path
					shutil.copyfile(G.current_file, new_file_path)
				else:
					return
			
			else:
				self.message('you can not copy a file!', 3)
				print(os.path.normpath(G.current_file), os.path.exists(G.current_file))
				print(new_file_path, os.path.exists(new_dir_path))
				return
				
		# ****** LOG
		logs_keys = {
		'activity': G.current_task['activity'],
		'task_name': G.current_task['task_name'],
		'action': 'push',
		'comment': comment,
		'version': os.path.basename(new_dir_path),
		'artist': G.current_task['artist']
		}
		
		result = self.db_log.notes_log(G.current_project, logs_keys, G.current_task['asset_id'])
		if not result[0]:
			return(False, result[1])
		
		'''
		# converce Tiff to Png
		if G.current_task['extension'] == '.tiff':
			png_path = new_file_path.replace(G.current_task['extension'], '.png')
			cmd = 'ffmpeg -i \"' + new_file_path + '\"  \"' + png_path + '\"'
			print(cmd)
			os.system(cmd)
		'''
		
		# message
		self.message(('push to ' + new_file_path), 1)
		
		# get versions list
		self.get_versions_list()
		
		# close window
		self.close_window(window)
		
		
	def open_action(self, input_task = False, open_path = None):
		print('{OPEN}')
		# ***** CHANGE STATUS
		if G.current_task['status'] != 'work':
			#result = G.func.open_change_status(G.current_project, G.current_task, G.all_task_list)
			change_statuses = [(G.current_task, 'work'),]
			for task_name in G.all_task_list:
				if G.all_task_list[task_name]['task']['status'] == 'work':
					change_statuses.append((G.all_task_list[task_name]['task'], 'pause',))
		
			result = self.db_task.change_work_statuses(G.current_project, change_statuses)
			if not result[0]:
				self.message(result[1], 2)
				#return
			
			else:
				G.current_task['status'] = 'work'
				# result[1] = dict {task_name : new_status, ...}
				for task_name in result[1]:
					G.all_task_list[task_name]['task']['status'] = result[1][task_name]
			G.current_task['status'] = 'work'
		
		# ******* OPEN FILE
		task_data = None
		if input_task:
			task_data = input_task
		else:
			task_data = G.current_task
		
		if not open_path:
			result = self.db_task.get_final_file_path(G.current_project, task_data)
			if result[0]:
				open_path = result[1]
			else:
				print('*'*25, result[1])
		
			# get tmp_file_path
			tmp_path = self.db_task.tmp_folder
			tmp_file_name = task_data['task_name'].replace(':','_', 2) + '_' + hex(random.randint(0, 1000000000)).replace('0x', '') + task_data['extension']
			tmp_file_path = os.path.join(tmp_path, tmp_file_name)
			
			if open_path:
				# copy to tmp
				shutil.copyfile(open_path, tmp_file_path)
			else:
				if task_data['extension'] in G.not_used_extensions:
					empty_folder = os.path.split(self.ui_folder)[0]
					empty_path = os.path.join(empty_folder, 'empty_files', ('empty' + task_data['extension']))
					shutil.copyfile(empty_path, tmp_file_path)
		
			G.current_file = tmp_file_path
		
		else:
			G.current_file = open_path
		
		
		self.myWidget.current_file.setText(G.current_file)
				
		# open file
		soft = self.db_studio.soft_data[task_data['extension']]
		#cmd = soft + " \"" + tmp_file_path + "\""
		cmd = "\"" + soft + "\"  \"" + G.current_file + "\""
		subprocess.Popen(cmd, shell = True)
		
		# ****** edit widget visible
		self.myWidget.task_list_table.setVisible(False)
		self.myWidget.distrib_frame.setVisible(False)
		self.myWidget.work_frame.setVisible(True)
		self.myWidget.current_file.setVisible(True)
		
	def open_input_action(self):
		input_task = G.all_task_list[G.current_task['task_name']]['input']
		
		if not input_task:
			self.message('Not Input task!', 2)
			return
			
		elif input_task['task_type'] == 'service':
			self.message('Type of incoming service tasks!', 2)
			return
		
		if G.current_task['extension'] != input_task['extension']:
			report_text = 'extession of input_task are not ' + G.current_task['extension']
			self.message(report_text, 2)
			
		else:
			self.open_action(input_task = input_task)
		
		#self.close_window(window)
		
	def open_from_file_action(self):
		home = os.path.expanduser('~')
		f = u'Files ' + G.current_task['extension'] + '  (*' + G.current_task['extension'] + ')'
		file_ = QtGui.QFileDialog.getOpenFileName(self, caption = 'Open From File',  dir = home, filter = f)
		
		if file_[0]:
			self.open_action(open_path = file_[0])
		
	def to_rework_action(self):
		ask = self.message('Are you sure?', 0)
		if not ask:
			return
		
		# accept in .db
		result = self.db_chat.rework_task(G.current_project, G.current_task, current_user = G.current_user)
		if not result[0]:
			if result[1] == 'not chat!':
				self.message('no posts in the chat!', 2)
				self.chat_ui()
				return
			self.message(result[1], 2)
			return
		
		# reload check_list
		self.load_task_list_table('', get_project_name = True, action = 'check_list')
		
	def accept_action(self):
		ask = self.message('Are you sure?', 0)
		if not ask:
			return
		
		# accept in .db
		result = self.db_chat.readers_accept_task(G.current_project, G.current_task, G.current_user)
		if not result[0]:
			self.message(result[1], 2)
			return
		
		#self.message(str(result[1]), 1)
		
		# reload check_list
		self.load_task_list_table('', get_project_name = True, action = 'check_list')
	
	# *********************** Panels *****************************************************
	
	def push_comment_ui(self):
		# ask
		ask = self.message(('You save the file?'), 0)
		if not ask:
			return
		
		task_data = G.current_task
		
		# make widjet
		ui_path = self.new_dialog_path
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(ui_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.lookVersionDialog = loader.load(file, self)
		file.close()
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		# edit Widget
		window.setWindowTitle('Push Comment')
		window.new_dialog_label.setText('comment:')
		window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.new_dialog_ok.clicked.connect(partial(self.push_action, window))
		
		window.show()
		pass
	
	def look_version_ui(self, look = True):
		task_data = G.current_task
		
		# get logs
		#result = self.db_log.get_push_logs(G.current_project, G.current_task)
		#if not result[0]:
		if not G.versions_list:
			#self.message(result[1], 2)
			self.message('Not Versions of Activity!', 2)
			return
		
		# make widjet
		ui_path = self.select_from_list_dialog_path
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(ui_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.lookVersionDialog = loader.load(file, self)
		file.close()
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		# edit Widget
		window.select_from_list_cansel_button.clicked.connect(partial(self.close_window, window))
		if look:
			window.setWindowTitle('Look Version')
			window.select_from_list_apply_button.clicked.connect(partial(self.look_version_action, window))
		else:
			window.setWindowTitle('Open Version')
			window.select_from_list_apply_button.setText('Open')
			window.select_from_list_apply_button.clicked.connect(partial(self.look_version_action, window, look = False))
		
		# make table
		headers = []
		for key in self.db_log.logs_keys:
			headers.append(key[0])
		
		window.select_from_list_data_list_table.setColumnCount(len(headers))
		window.select_from_list_data_list_table.setRowCount(len(G.versions_list))
		window.select_from_list_data_list_table.setHorizontalHeaderLabels(headers)
		
		# selection mode   
		window.select_from_list_data_list_table.setSortingEnabled(True)
		window.select_from_list_data_list_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		window.select_from_list_data_list_table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		
		# make tabel
		for i,log in enumerate(G.versions_list):
			#print(log)
			for j,key in enumerate(headers):
				newItem = QtGui.QTableWidgetItem()
				newItem.setText(log[key])
				newItem.log = False
								
				if key == 'version':
					newItem.log = log
					
				window.select_from_list_data_list_table.setItem(i, j, newItem)
				
		window.show()
		
		
	# *********************** CHAT *******************************************************
	def chat_ui(self, chat_status = 'user'):
		self.chat_status = chat_status
		self.current_task = G.current_task
		self.current_user = G.current_user
		self.current_project = G.current_project
		
		import lineyka_chat
		chat_window = lineyka_chat.lineyka_chat(self)
		#chat_class.__init__(self)
		
	'''
	def chat_main_ui_(self):
		task_data = G.current_task
		nik_name = G.current_user
		project = G.current_project
		
		# status
		self.chat_status = 'user'
		
		# make widjet
		ui_path = self.chat_main_path
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(ui_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.chatMain = loader.load(file, self)
		file.close()
		
		# fill meta data
		window.setWindowTitle('Lineyka Chat')
		window.chat_nik_name_label.setText(nik_name)
		window.chat_asset_name_label.setText(task_data['asset'])
		window.chat_task_name_label.setText(task_data['task_name'].split(':')[1])
		
		# button connect
		window.close_button.clicked.connect(partial(self.close_window, window))
		window.reload_button.clicked.connect(partial(self.chat_load_topics, window))
		window.chat_add_topic_button.clicked.connect(partial(self.chat_new_topic_ui, window))
		
		window.show()
		
		self.chat_load_topics(window)
		
	def chat_load_topics(self, window):
		#topics = ['aaaa']*3
		task_data = G.current_task
		project_name = G.current_project
		
		# read chat data
		topics = None
		result = self.db_chat.read_the_chat(project_name, task_data['task_name'])
		if not result[0]:
			self.message(result[1], 2)
		else:
			topics = result[1]
		
		tool_box = window.chat_tool_box
		# clear tool box
		i = tool_box.count()
		while i > -1:
			try:
				tool_box.removeItem(i)
			except:
				pass
			i = i-1
		
		# size item
		tool_box.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
		
		if topics:
			for topic in topics:
				dt = topic['date_time']
				date = str(dt.year) + '/' + str(dt.month) + '/' + str(dt.day) + '/' + str(dt.hour) + ':' + str(dt.minute)
				header = topic['author'] + ' '*5 + date
				
				lines = json.loads(topic['topic'])
				
				topic_widget = QtGui.QFrame()
				v_layout = QtGui.QVBoxLayout()
				for key in lines:
					widget = QtGui.QFrame(parent = topic_widget)
					layout = QtGui.QHBoxLayout()
					# button
					if lines[key][1]:
						button = QtGui.QPushButton(QtGui.QIcon(lines[key][1]), '', parent = widget)
					else:
						button = QtGui.QPushButton('not Image', parent = widget)
					button.setIconSize(QtCore.QSize(100, 100))
					button.setFixedSize(100, 100)
					button.img_path = lines[key][0]
					button.clicked.connect(partial(self.chat_image_view_ui, button))
					layout.addWidget(button)
					
					# text field
					text_field = QtGui.QTextEdit(lines[key][2], parent = widget)
					text_field.setMaximumHeight(100)
					layout.addWidget(text_field)
					
					widget.setLayout(layout)
					#print(widget.sizeHint())
					
					v_layout.addWidget(widget)
				topic_widget.setLayout(v_layout)
							
				tool_box.addItem(topic_widget, header)
				
	
	def chat_new_topic_ui(self, window):
		# make widjet
		ui_path = self.chat_add_topic_path
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(ui_path)
		#file.open(QtCore.QFile.ReadOnly)
		add_window = self.chatAddTopic = loader.load(file, self)
		file.close()
		
		# set modal window
		add_window.setWindowModality(QtCore.Qt.WindowModal)
		add_window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		# ****** add first line
		# H
		h_layout = QtGui.QHBoxLayout()
		line_frame = QtGui.QFrame(parent = add_window.new_topics_frame)
		# button
		button = QtGui.QPushButton('img', parent = line_frame)
		button.setFixedSize(100, 100)
		button.img_path = False
		h_layout.addWidget(button)
		# -- button connect
		button.clicked.connect(partial(self.chat_image_view_ui, button))
		button.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
		addgrup_action = QtGui.QAction( 'Inser Image From Clipboard', add_window)
		addgrup_action.triggered.connect(partial(self.chat_add_img_to_line, button))
		button.addAction( addgrup_action )
		
		# text field
		text_field = QtGui.QTextEdit(parent = line_frame)
		#text_field = QtGui.QTextBrowser(parent = line_frame)
		text_field.setMaximumHeight(100)
		h_layout.addWidget(text_field)
		line_frame.setLayout(h_layout)
		# V
		v_layout = QtGui.QVBoxLayout()
		v_layout.addWidget(line_frame)
		add_window.new_topics_frame.setLayout(v_layout)
		
		# ****** append line data
		add_window.line_data = {}
		add_window.line_data['1'] = (button, text_field)
		
		# connect button
		add_window.cansel_button.clicked.connect(partial(self.close_window, add_window))
		add_window.add_line_button.clicked.connect(partial(self.chat_add_line_to_message, add_window, v_layout))
		add_window.send_message_button.clicked.connect(partial(self.chat_new_topic_action, add_window, self.chat_status))
		
		add_window.show()
		
	def chat_add_img_to_line(self, button):
		rand  = hex(random.randint(0, 1000000000)).replace('0x', '')
		img_path = os.path.join(self.db_chat.tmp_folder, ('tmp_image_' + rand + '.png')).replace('\\','/')
		
		clipboard = QtGui.QApplication.clipboard()
		img = clipboard.image()
		if img:
			img.save(img_path)
		else:
			self.message('Cannot Image!', 2)
			return(False, 'Cannot Image!')
			
		button.setIcon(QtGui.QIcon(img_path))
		button.setIconSize(QtCore.QSize(100, 100))
		button.setText('')
		button.img_path = img_path
		
		return(True, 'Ok!')
		
	def chat_image_view_ui(self, button):
		if not button.img_path:
			return
		# make widjet
		ui_path = self.chat_img_viewer_path
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(ui_path)
		#file.open(QtCore.QFile.ReadOnly)
		img_window = self.chatImgViewer = loader.load(file, self)
		file.close()
		
		
		# SHOW IMAGE
		image = QtGui.QImage(button.img_path)
		img_window.setWindowTitle(button.img_path)
			
		img_window.image_label.setBackgroundRole(QtGui.QPalette.Base)
		img_window.image_label.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
		img_window.image_label.setScaledContents(True)
		
		img_window.image_label.setPixmap(QtGui.QPixmap.fromImage(image))
		
		# connect button
		img_window.cansel_button.clicked.connect(partial(self.close_window, img_window))
		
		img_window.show()
    
				
	def chat_add_line_to_message(self, add_window, v_layout):
		# H
		h_layout = QtGui.QHBoxLayout()
		line_frame = QtGui.QFrame(parent = add_window.new_topics_frame)
		# button
		button = QtGui.QPushButton('img', parent = line_frame)
		button.setFixedSize(100, 100)
		button.img_path = False
		h_layout.addWidget(button)
		# -- button connect
		button.clicked.connect(partial(self.chat_image_view_ui, button))
		button.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
		addgrup_action = QtGui.QAction( 'Inser Image From Clipboard', add_window)
		addgrup_action.triggered.connect(partial(self.chat_add_img_to_line, button))
		button.addAction( addgrup_action )
		
		# text field
		text_field = QtGui.QTextEdit(parent = line_frame)
		text_field.setMaximumHeight(100)
		h_layout.addWidget(text_field)
		line_frame.setLayout(h_layout)
		
		v_layout.addWidget(line_frame)
		
		# ****** append line data
		# -- get num
		numbers = []
		for key in add_window.line_data.keys():
			numbers.append(int(key))
		num = max(numbers) + 1
		add_window.line_data[str(num)] = (button, text_field)
		
	def chat_new_topic_action(self, add_window, status):
		task_data = G.current_task
		nik_name = G.current_user
		project = G.current_project
		
		# get project
		result = self.db_chat.get_project(project)
		if not result[0]:
			return(False, result[1])
		
		# get color
		if status == 'manager' or status == 'manager_to_outsource':
			color = json.dumps(self.db_chat.color_status['checking'])
		elif status == 'user' or status == 'user_outsource':
			color = json.dumps(self.db_chat.color_status['work'])
		else:
			color = json.dumps(self.db_chat.color_status['done'])
			
		message = {}
		line_data = add_window.line_data
		for key in line_data:
			# GET Img
			tmp_img_path = line_data[key][0].img_path
			if tmp_img_path and os.path.exists(tmp_img_path):
				# -- copy to img_path
				rand  = hex(random.randint(0, 1000000000)).replace('0x', '')
				img_path = os.path.normpath(os.path.join(self.db_chat.chat_img_path, (task_data['task_name'].replace(':','_') + rand + '.png')))
				shutil.copyfile(tmp_img_path, img_path)
				# -- make icon
				icon_path = img_path.replace('.png', '_icon.png')
				cmd = self.db_chat.convert_exe + ' \"' + img_path + '\" -resize 100 \"' + icon_path + '\"'
				try:
					os.system(cmd)
				except:
					return(False, 'in chat_new_topic_action - problems with conversion icon.png')
			else:
				img_path = False
				icon_path = False
				
			# GET Text
			text = line_data[key][1].toPlainText()
			
			# append message
			message[key] = (img_path, icon_path, text)
		
		topic = json.dumps(message, sort_keys=True, indent=4)
		
		# save message 
		chat_keys = {
		'author':nik_name,
		'color':color,
		'topic':topic,
		'status':status
		}
		result = self.db_chat.record_messages(project, task_data['task_name'], chat_keys)
		if not result[0]:
			self.message(result[1], 2)
			return
		else:
			print(result[1])
			self.close_window(add_window)
			self.chat_load_topics(self.chatMain)
	'''	
	# *********************** SETTING ****************************************************
    
	def help_user_manual(self):
		webbrowser.open_new_tab('http://www.lineyka.org.ru/')
		print("go to user manual!")

	def set_studio_ui(self):
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.set_window_path)
		#file.open(QtCore.QFile.ReadOnly)
		self.setWindow = loader.load(file, self)
		file.close()
		
		# add line
		# -- get extension_dict
		ext_dict = {}
		result = self.db_studio.get_extension_dict()
		if result[0]:
			ext_dict = result[1]
		
		# -- add widgets
		layout = QtGui.QVBoxLayout()
		for key in ext_dict:
			print(key)
			frame = QtGui.QFrame(parent = self.setWindow.additional_frame)
			# frame content
			h_layout = QtGui.QHBoxLayout()
			# -- label
			label = QtGui.QLabel(('exe for extension:  \"' + key + '\"'), parent = frame)
			h_layout.addWidget(label)
			# -- line edit
			line = QtGui.QLineEdit(parent = frame)
			line.setText(ext_dict[key])
			line.returnPressed.connect(partial(self.set_exe_string, line, key))
			h_layout.addWidget(line)
			# -- button
			button = QtGui.QPushButton(key, parent = frame)
			button.clicked.connect(partial(self.set_exe_path, line, key))
			h_layout.addWidget(button)
			
			frame.setLayout(h_layout)
			# frame content end
			
			layout.addWidget(frame)
			
		# EDIT EXTENSION
		frame = QtGui.QFrame(parent = self.setWindow.additional_frame)
		# frame content
		h_layout = QtGui.QHBoxLayout()
		# -- line edit
		line = QtGui.QLineEdit(parent = frame)
		h_layout.addWidget(line)
		# -- add button
		button = QtGui.QPushButton('Add Extension', parent = frame)
		button.clicked.connect(partial(self.edit_extension, line, 'ADD', self.setWindow))
		h_layout.addWidget(button)
		# -- remove button
		button = QtGui.QPushButton('Remove Extension', parent = frame)
		button.clicked.connect(partial(self.edit_extension, line, 'REMOVE', self.setWindow))
		h_layout.addWidget(button)
		# -- final
		frame.setLayout(h_layout)
		layout.addWidget(frame)
		
		# pass button
		button = QtGui.QPushButton(key, parent = self.setWindow.additional_frame)
		button.setDefault(True)
		button.setVisible(False)
		layout.addWidget(button)
			
			
		self.setWindow.additional_frame.setLayout(layout)


		# fill field
		copy = self.db_studio
		data = copy.get_studio()
		if data[0]:
			self.setWindow.set_studio_field.setText(str(copy.studio_folder))
			self.setWindow.set_tmp_field.setText(str(copy.tmp_folder))
			self.setWindow.set_convert_exe_field.setText(str(copy.convert_exe))
			'''
			for row in data[1]:
			print row
			'''
	
		else:
			self.setWindow.set_studio_field.setText('set studio_folder')
			self.setWindow.set_tmp_field.setText('set tmp_folder')
			print(data[0])
			
		# set modal window
		self.setWindow.setWindowModality(QtCore.Qt.WindowModal)
		self.setWindow.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
    
		self.setWindow.show()

		# edit button
		self.setWindow.set_studio_button.clicked.connect(self.set_studio_action)
		self.setWindow.set_tmp_button.clicked.connect(self.set_tmp_path_action)
		self.setWindow.set_convert_button.clicked.connect(self.set_convert_path_action)

		print('set studio ui')
    
	def set_studio_action(self):
		# get path
		home = os.path.expanduser('~')
		folder = QtGui.QFileDialog.getExistingDirectory(self, home)
		
		if folder:
			self.setWindow.set_studio_field.setText(str(folder))

			#return
			# set studio path
			result = self.db_studio.set_studio(folder)
			if not result[0]:
				self.message(result[1], 2)
		
			# finish
			self.clear_table()
		print('set studio folder')
    
	def set_tmp_path_action(self):
		# get path
		home = os.path.expanduser('~')
		folder = QtGui.QFileDialog.getExistingDirectory(self, home)
		
		if folder:
			self.setWindow.set_tmp_field.setText(str(folder))

			# set studio path
			copy = self.db_studio
			result = copy.set_tmp_dir(folder)
			if not result[0]:
				self.message(result[1], 2)
      
		# finish
		print('set tmp folder')
		
	def set_convert_path_action(self):
		# get path
		home = os.path.expanduser('~')
		file_ = QtGui.QFileDialog.getOpenFileName(self, dir = home)[0]
		
		if file_:
			self.setWindow.set_convert_exe_field.setText(str(file_))
			
			# set studio path
			copy = self.db_studio
			result = copy.set_convert_exe_path(file_)
			if not result[0]:
				self.message(result[1], 2)
      
		# finish
		print('set convert.exe path')
		
	def set_exe_path(self, line, key):
		# get path
		home = os.path.expanduser('~')
		file_path = QtGui.QFileDialog.getOpenFileName(self, dir = home)[0]
		
		if file_path:
			line.setText(str(file_path))
			
			# edit data
			result = self.db_studio.edit_extension_dict(key, file_path)
			if not result[0]:
				self.message(result[1], 2)
				
	def edit_extension(self, line, action, window):
		result = self.db_studio.edit_extension(line.text(), action)
		if not result[0]:
			self.message(result[1], 2)
			return
				
		window.close()
		self.set_studio_ui()
			
	def set_exe_string(self, line, key):
		text = line.text()
		
		# edit data
		result = self.db_studio.edit_extension_dict(key, text)
		if not result[0]:
			self.message(result[1], 2)
		else:
			self.message((key + ' changed!'), 1)
    
	def user_login_ui(self):
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.login_window_path)
		#file.open(QtCore.QFile.ReadOnly)
		self.loginWindow = loader.load(file, self)
		file.close()
		
		# set modal window
		self.loginWindow.setWindowModality(QtCore.Qt.WindowModal)
		self.loginWindow.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		self.loginWindow.show()

		# edit button
		self.loginWindow.login_button.clicked.connect(self.user_login_action)

		# finish
		print('login ui')
    
	def user_login_action(self):
		copy = self.db_artist

		nik_name = self.loginWindow.login_nik_name_field.text()
		password = self.loginWindow.login_password_field.text()

		login = copy.login_user(nik_name, password)
    
		if login[0]:
			self.loginWindow.close()
		elif login[1] == 'not user':
			self.message('user name is not correct!', 2)
			return
		elif login[1] == 'not password':
			self.message('password is not correct!!', 2)
			return
    
		# finish
		self.load_nik_name()
		self.clear_table()
		print('login action')
    
	def user_registration_ui(self):
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.user_registr_window_path)
		#file.open(QtCore.QFile.ReadOnly)
		self.myWidget.registrWindow = loader.load(file, self)
		file.close()
		
		# set modal window
		self.myWidget.registrWindow.setWindowModality(QtCore.Qt.WindowModal)
		self.myWidget.registrWindow.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		self.myWidget.registrWindow.show()

		# edit Button
		self.myWidget.registrWindow.user_registration_button.clicked.connect(self.user_registration_action)

		# finish
		print('registration ui')
    
	def user_registration_action(self):
		copy = self.db_artist

		# get Data
		data = {
		'nik_name' : self.myWidget.registrWindow.nik_name_field.text(),
		'password' : self.myWidget.registrWindow.password_field.text(),
		'email' : self.myWidget.registrWindow.email_field.text(),
		'phone' : self.myWidget.registrWindow.phone_field.text(),
		'speciality' : self.myWidget.registrWindow.specialty_field.text(),
		'workroom': '[]',
		'status' : 'active'
		}
    
		# exists Nik - Password
		if data['nik_name'] == '':
			self.message('\"Nik Name\" not specified!', 3)
			return
		if data['password'] == '':
			self.message('\"Password\" not specified!', 3)
			return
    
		# get User_Name
		user_name = getpass.getuser()
		data['user_name'] = user_name

		# get user_level
		artists = copy.read_artist('all')
		if not artists[0]:
			data['level'] = 'root'
		else:
			data['level'] = 'user'
      
		# add artist
		result = copy.add_artist(data)
		if result[0]:
			self.myWidget.registrWindow.close()
		else:
			if result[1] == 'overlap':
				self.message('User With That Username Already Exists!', 2)
				return
			else:
				self.message(result[1], 2)
				return
	
		# finish
		self.load_nik_name()
		self.clear_table()
		print('user registration action')
    
	#*********************** UTILITS *******************************************
	def get_versions_list(self):
		result = self.db_log.get_push_logs(G.current_project, G.current_task)
		
		if not result[0]:
			G.versions_list = []
		else:
			G.versions_list = result[1]
		
		return(True, 'Ok!')
	
	def load_project_list(self): 
		enum_list = ['--select project--']
		if self.db_studio.list_projects:
			project_list = self.db_studio.list_projects.keys()
			for key in project_list:
				if self.db_studio.list_projects[key]['status'] == 'active':
					enum_list.append(key)
		else:
			pass
		self.myWidget.project_box.addItems(enum_list)
	
	def load_nik_name(self):
		nik_name = 'Not User'
		result = self.db_artist.get_user()
		if result[0]:
			nik_name = result[1][0]
		
		self.myWidget.nik_name.setText(nik_name)
		G.current_user = nik_name
	
	def close_window(self, window):
		window.close()
	
	def clear_table(self, table = False):
		if not table:
			table = self.myWidget.task_list_table
		
		# -- clear table
		num_row = table.rowCount()
		num_column = table.columnCount()
		
		# old
		'''
		for i in range(0, num_row):
			for j in range(0, num_column):
				item = table.item(i, j)
				table.takeItem(i, j)

				table.removeCellWidget(i, j)
		'''
		
		# new
		table.clear()
		table.setColumnCount(0)
		table.setRowCount(0)
				
	
	def message(self, m, i):
		mBox = QtGui.QMessageBox()
		mBox.setText(m)
		#mBox.setStandardButtons( QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok )
		ok_button = mBox.addButton(QtGui.QMessageBox.Ok)
		cancel_button = mBox.addButton(QtGui.QMessageBox.Cancel)
    
		if i==1:
			mBox.setIcon(QtGui.QMessageBox.Information)
			mBox.setWindowTitle('information')
		elif i == 2:
			mBox.setIcon(QtGui.QMessageBox.Warning)
			mBox.setWindowTitle('Oh my God!')
		elif i == 3:
			mBox.setIcon(QtGui.QMessageBox.Critical)
			mBox.setWindowTitle('Saint Mary!')
		elif i == 0:
			mBox.setIcon(QtGui.QMessageBox.Question)
			mBox.setWindowTitle('tel me!')
    
		com = mBox.exec_()
    
		if mBox.clickedButton() == ok_button:
			return(True)
		elif mBox.clickedButton() == cancel_button:
			return(False)
      
	
			
app = QtGui.QApplication(sys.argv)
mw = MainWindow()
mw.show()
app.exec_()
