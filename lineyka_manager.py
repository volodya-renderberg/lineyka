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

# from lineyka 
import ui
import edit_db as db
#import lineyka_publish

# sudo chmod +x "/home/vofka/Yandex.Disk/Lineyka/lineyka_manager.py"

class G(object):
	pass

class MainWindow(QtGui.QMainWindow):
	def __init__(self, parent = None):
		# get Path
		#path = '/home/renderberg/Yandex.Disk/Lineyka_'
		path = os.path.dirname(ui.__file__)
		self.lineyka_path = os.path.dirname(path)
		self.main_window_path = os.path.join(path, "lineyka_manager.ui")
		self.set_window_path = os.path.join(path, "qt_settings.ui")
		self.login_window_path = os.path.join(path, "qt_login.ui")
		self.user_registr_window_path = os.path.join(path, "qt_registration.ui")
		self.qt_set_project_path = os.path.join(path, "qt_set_project.ui")
		self.new_dialog_path = os.path.join(path, "new_dialog.ui")
		self.combo_dialog_path = os.path.join(path, "combo_dialog.ui")
		self.new_dialog_2_path = os.path.join(path, 'new_dialog_two_field.ui')
		self.new_dialog_3_path = os.path.join(path, 'new_dialog_three_field.ui')
		self.new_dialog_4_path = os.path.join(path, 'new_dialog_four_field.ui')
		self.new_dialog_4_2_path = os.path.join(path, 'new_dialog_four_field_2.ui')
		self.artist_dialog_path = os.path.join(path, "artist_dialog.ui")
		self.select_from_list_dialog_path = os.path.join(path, "select_from_list_dialog.ui")
		self.select_from_list_dialog_combobox_path = os.path.join(path, "select_from_list_dialog_combobox.ui")
		self.select_from_list_dialog_3button_path = os.path.join(path, "select_from_list_dialog_3_button.ui")
		self.select_from_check_button_dialog_path = os.path.join(path, "select_from_check_button_dialog.ui")
		
		# -- chat path
		self.chat_main_path = os.path.join(path, "chat_dialog.ui")
		self.chat_add_topic_path = os.path.join(path, "chat_add_topic.ui")
		self.chat_img_viewer_path = os.path.join(path, "chat_img_viewer.ui")
		
		# colors
		self.project_color = QtGui.QColor(106, 229, 255)
		self.workroom_color = QtGui.QColor(145, 185, 246)
		self.artist_color = QtGui.QColor(200, 250, 100)
		self.grey_color = QtGui.QColor(150, 150, 150)
		self.set_of_tasks_color = QtGui.QColor(183, 231, 178)
		self.tasks_color = QtGui.QColor(255, 241, 150)
		self.series_color = QtGui.QColor(255, 205, 227)
		self.group_color = QtGui.QColor(255, 201, 190)
		self.asset_color = QtGui.QColor(255, 218, 160)
		self.stop_color = QtGui.QColor(142, 160, 193)
		
		# load db.
		self.db_studio = db.studio()
		self.artist = db.artist()
		self.db_workroom = db.workroom()
		self.db_series = db.series()
		self.db_group = db.group()
		self.db_list_of_assets = db.list_of_assets()
		self.db_asset = db.asset()
		#self.db_task = db.task()
		self.db_set_of_tasks = db.set_of_tasks()
		self.db_chat = db.chat()
		self.db_log = db.log()
		
		# other moduls
		#self.publish = lineyka_publish.publish()
		
		#
		self.look_keys = ['nik_name','specialty','outsource','level']
		self.current_project = False
		self.current_group = False
		self.type_editor = False
		
		QtGui.QMainWindow.__init__(self, parent)
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.main_window_path)
		file.open(QtCore.QFile.ReadOnly)
		self.myWidget = loader.load(file, self)
		file.close()
		
		# ---- get artist data
		self.get_artist_data()
		
		# menu
		self.myWidget.actionSet_studio.triggered.connect(self.set_studio_ui)
		self.myWidget.actionLogin.triggered.connect(self.user_login_ui)
		self.myWidget.actionRegistration.triggered.connect(self.user_registration_ui)
		self.myWidget.actionUser_manual.triggered.connect(self.help_user_manual)

				
		# at studio 
		self.myWidget.artist_editor_button.clicked.connect(self.edit_ui_to_artist_editor)
		self.myWidget.workroom_editor_button.clicked.connect(self.edit_ui_to_workroom_editor)
		self.myWidget.project_editor_button.clicked.connect(self.edit_ui_to_project_editor)
		self.myWidget.set_of_tasks_editor_button.clicked.connect(self.edit_ui_to_set_of_tasks_editor)
		
		# at project
		self.myWidget.series_editor_button.clicked.connect(self.edit_ui_to_series_editor)
		self.myWidget.groups_editor_button.clicked.connect(self.edit_ui_to_group_editor)
		self.myWidget.location_content_editor_button.clicked.connect(partial(self.edit_ui_to_location_editor, 'location'))
		self.myWidget.anim_shot_content_editor_button.clicked.connect(partial(self.edit_ui_to_location_editor, 'animation'))
		#self.myWidget.render_shot_content_editor_button.clicked.connect(partial(self.edit_ui_to_location_editor, 'render'))
		self.myWidget.render_shot_content_editor_button.setVisible(False)
		
		# tools button
		self.myWidget.studio_butt_1.setVisible(False)
		self.myWidget.studio_butt_2.setVisible(False)
		self.myWidget.studio_butt_3.setVisible(False)
		self.myWidget.studio_butt_4.setVisible(False)
		self.myWidget.studio_butt_5.setVisible(False)
		self.myWidget.studio_butt_6.setVisible(False)
		self.myWidget.studio_butt_7.setVisible(False)
		self.myWidget.studio_butt_8.setVisible(False)
		self.myWidget.studio_butt_9.setVisible(False)
		self.myWidget.studio_butt_10.setVisible(False)
		self.myWidget.group_search_qline.setVisible(False)
		self.myWidget.group_search_qline.returnPressed.connect(self.reload_group_content_list)
		
		# edit combobox 
		self.myWidget.set_comboBox_01.setVisible(False)
		self.myWidget.set_comboBox_02.setVisible(False)
		self.myWidget.set_comboBox_03.setVisible(False)
		
		# edit table
		#self.myWidget.studio_editor_table_2.setVisible(False)
		self.myWidget.title_label.setVisible(False)
		self.myWidget.right_table_frame.setVisible(False)
		
		# table_2 context menu
		# change input task
		self.myWidget.studio_editor_table_2.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
		addgrup_action = QtGui.QAction( 'change Task', self.myWidget)
		addgrup_action.triggered.connect(partial(self.loc_change_input_task_ui))
		self.myWidget.studio_editor_table_2.addAction( addgrup_action )
		
		# ---- List Active Projects
		self.get_list_active_projects()
		
		# ---- self.WORKROOM ----------------------------
		self.set_self_workrooms()
		
		# ---- TASKS MANAGER ----------------------------
		self.preparation_to_task_manager()
		
								
	# ******************* STUDIO EDITOR ************************************************
	
	# ******************* STUDIO EDITOR /// ARTIST EDITOR ****************************
	def edit_ui_to_artist_editor(self):
		# edit label
		self.myWidget.studio_editor_label.setText('Artist Editor')
				
		# edit button
		# 1
		self.myWidget.studio_butt_1.setVisible(True)
		self.myWidget.studio_butt_1.setText('Reload')
		try:
			self.myWidget.studio_butt_1.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_1.clicked.connect(self.reload_artist_list)
		# 2
		self.myWidget.studio_butt_2.setVisible(True)
		self.myWidget.studio_butt_2.setText('New Artist')
		try:
			self.myWidget.studio_butt_2.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_2.clicked.connect(self.add_artist_ui)
		# 3
		self.myWidget.studio_butt_3.setVisible(True)
		self.myWidget.studio_butt_3.setText('Edit Artist Data')
		try:
			self.myWidget.studio_butt_3.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_3.clicked.connect(self.edit_artist_ui)
		# 4
		self.myWidget.studio_butt_4.setVisible(False)
		self.myWidget.studio_butt_5.setVisible(False)
		self.myWidget.studio_butt_6.setVisible(False)
		self.myWidget.studio_butt_7.setVisible(False)
		self.myWidget.studio_butt_8.setVisible(False)
		self.myWidget.studio_butt_9.setVisible(False)
		self.myWidget.studio_butt_10.setVisible(False)
		
		# edit combobox 
		self.myWidget.set_comboBox_01.setVisible(False)
		self.myWidget.set_comboBox_02.setVisible(False)
		self.myWidget.set_comboBox_03.setVisible(False)
		self.myWidget.group_search_qline.setVisible(False)
		
		# edit table
		#self.myWidget.studio_editor_table_2.setVisible(False)
		self.myWidget.right_table_frame.setVisible(False)
		# -- selection mode
		self.myWidget.studio_editor_table.setSortingEnabled(True)
		self.myWidget.studio_editor_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.myWidget.studio_editor_table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		
		self.clear_table()
		self.fill_artist_table()
				
	def fill_artist_table(self):
		#copy = self.db_artist
		artists = self.artist.read_artist('all')
		
		if not artists[0]:
			return
		
		# get workroom data
		wr_id_dict = {}
		wr_name_dict = {}
		
		result = self.db_workroom.get_list_workrooms(DICTONARY = 'by_id_by_name')
		if not result[0]:
			self.message(result[1], 3)
			#return
		else:
			wr_id_dict = result[1]
			wr_name_dict = result[2]
		   
		# get table data
		num_row = len(artists[1])
		num_column = len(self.artist.artists_keys)
		headers = []
		
		for item in self.artist.artists_keys:
			#headers.append(item[0])
			headers.append(item)
    
		# make table
		self.myWidget.studio_editor_table.setColumnCount(num_column)
		self.myWidget.studio_editor_table.setRowCount(num_row)
		self.myWidget.studio_editor_table.setHorizontalHeaderLabels(headers)
    
		# fill table
		for i, artist in enumerate(artists[1]):
			for j,key in enumerate(headers):
				if key == 'date_time':
					continue
				newItem = QtGui.QTableWidgetItem()
				if key == 'workroom':
					if artist[key]:
						wr_list = []
						for wr_id in artist[key]:
							wr_list.append(wr_id_dict[wr_id]['name'])
						newItem.setText(','.join(wr_list))
				else:
					newItem.setText(artist[key])
				if key == 'nik_name':
					color = self.artist_color
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
				newItem.artist = artist
				self.myWidget.studio_editor_table.setItem(i, j, newItem)
				
		self.myWidget.studio_editor_table.wr_id_dict = wr_id_dict
		self.myWidget.studio_editor_table.wr_name_dict = wr_name_dict
        
		print('fill artist table')
		
			
	def reload_artist_list(self):
		# clear table
		num_row = self.myWidget.studio_editor_table.rowCount()
		num_column = self.myWidget.studio_editor_table.columnCount()
    
		for i in range(0, num_row):
			for j in range(0, num_column):
				item = self.myWidget.studio_editor_table.item(i, j)
				self.myWidget.studio_editor_table.takeItem(i, j)

				#self.myWidget.studio_editor_table.removeCellWidget(i, j)
    
		# fill table
		self.fill_artist_table()

		# finish
		print('reload artist list')
	
	# ------------------- Add Artist ---------------------------------------------------------
	def add_artist_ui(self):
		if not self.artist.level:
			self.message('No Access! (you must register or login)', 3)
			return
		elif self.artist.level not in self.artist.manager_levels:
			self.message('No Access! (level "%s" is not enough to perform this operation)' % self.artist.level, 3)
			return
			
		# get levels
		levels = []
		for level in self.artist.user_levels:
			levels.append(level)
			if level == self.artist.level:
				break
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.artist_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		self.newArtistDialog = loader.load(file, self)
		file.close()
		
		# edit widget
		self.newArtistDialog.setWindowTitle('add New Artist')
		self.newArtistDialog.workroom_field.setEnabled(False)
		self.newArtistDialog.share_dir_field.setEnabled(False)
		self.newArtistDialog.level_combobox.addItems(levels)
		
		# workroom dialog
		self.newArtistDialog.artist_edit_workroom_button.clicked.connect(partial(self.artist_edit_workroom_ui, self.newArtistDialog))
		
		# edit button
		self.newArtistDialog.get_share_dir_button.clicked.connect(partial(self.get_share_dir, self.newArtistDialog.share_dir_field))
		self.newArtistDialog.artist_dialog_cancel.clicked.connect(partial(self.add_artist_action, False))
		self.newArtistDialog.artist_dialog_ok.clicked.connect(partial(self.add_artist_action, True))
		
		# set modal window
		self.newArtistDialog.setWindowModality(QtCore.Qt.WindowModal)
		self.newArtistDialog.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		self.newArtistDialog.show()
			
				
	def add_artist_action(self, action):
		if not action:
			self.newArtistDialog.close()
			return
			
		# get Data
		data = {
		'nik_name' : self.newArtistDialog.nik_name_field.text(),
		'password' : self.newArtistDialog.password_field.text(),
		'email' : self.newArtistDialog.email_field.text(),
		'phone' : self.newArtistDialog.phone_field.text(),
		'specialty' : self.newArtistDialog.specialty_field.text(),
		'outsource' : self.newArtistDialog.autsource_check_box.checkState(),
		'workroom' : self.newArtistDialog.workroom_field.text(),
		'level' : self.newArtistDialog.level_combobox.itemText(self.newArtistDialog.level_combobox.currentIndex()),
		'share_dir' : self.newArtistDialog.share_dir_field.text(),
		'user_name' : '',
		'status' : 'active'
		}
		
		# get workroom list
		wr_id_list = []
		if data['workroom']:
			for wr_name in json.loads(data['workroom']):
				wr_id_list.append(self.myWidget.studio_editor_table.wr_name_dict[wr_name]['id'])
		data['workroom'] = json.dumps(wr_id_list)
		
		# get Outsource
		if data['outsource'] == QtCore.Qt.CheckState.Checked:
			data['outsource'] = True
		else:
			data['outsource'] = False
			
		# get NikName Password
		if data['nik_name'] == '' or data['password'] == '':
			self.message('Not Nik_Name or Password', 2)
			return
		'''
		print(data)
		return
		'''
		
		# add artist
		result = self.artist.add_artist(data, registration = False)
		
		if not result[0]:
			self.message(result[1], 2)
			return
	
		# finish
		self.reload_artist_list()
		print('add artist action')
		
		self.newArtistDialog.close()
		
	# ----------------- Edit Artist --------------------------------------
	def edit_artist_ui(self):
		current_item = self.myWidget.studio_editor_table.currentItem()
		if not current_item:
			self.message('Not Selected Artists!', 2)
			return
		
		selected_data = current_item.artist
		level = selected_data['level']
		
		if self.artist.level not in self.artist.manager_levels:
			self.message('No Access! your level: "%s"' % self.artist.level, 3)
			return
		
		# get levels
		levels = []
		for level in self.artist.user_levels:
			levels.append(level)
			if level == self.artist.level:
				break
			
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.artist_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.editArtistDialog = loader.load(file, self)
		file.close()
		
		# get workrooms list
		if selected_data['workroom']:
			wr_id_list = selected_data['workroom']
		else:
			wr_id_list = []
		
		wr_name_list = []
		for wr_id in wr_id_list:
			wr_name_list.append(self.myWidget.studio_editor_table.wr_id_dict[wr_id]['name'])
		
		# edit widget
		window.setWindowTitle('Edit Artist Data')
		window.nik_name_field.setEnabled(False)
		window.nik_name_field.setText(selected_data['nik_name'])
		window.workroom_field.setEnabled(False)
		window.workroom_field.setText(json.dumps(wr_name_list))
		window.share_dir_field.setEnabled(False)
		window.share_dir_field.setText(selected_data['share_dir'])
		window.password_field.setText(selected_data['password'])
		window.email_field.setText(selected_data['email'])
		window.phone_field.setText(selected_data['phone'])
		window.specialty_field.setText(selected_data['specialty'])
		
		window.level_combobox.addItems(levels)
		window.level_combobox.setCurrentIndex(window.level_combobox.findText(selected_data['level']))
		
		if selected_data['outsource'] == '1':
			window.autsource_check_box.setCheckState(QtCore.Qt.CheckState.Checked)
			
		# button connect
		window.get_share_dir_button.clicked.connect(partial(self.get_share_dir, window.share_dir_field))
		window.artist_edit_workroom_button.clicked.connect(partial(self.artist_edit_workroom2_ui, window))
		window.artist_dialog_ok.clicked.connect(partial(self.edit_artist_action, selected_data))
		window.artist_dialog_cancel.clicked.connect(partial(self.close_window, window))
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()
		
		# finish
		print('edit artist ui')
		
	
	def edit_artist_action(self, selected_data):
		window = self.editArtistDialog
		# get data
		# -- get workroom id list
		wr_name_list = json.loads(window.workroom_field.text())
		wr_id_list = []
		
		for name in wr_name_list:
			wr_id_list.append(self.myWidget.studio_editor_table.wr_name_dict[name]['id'])
		
		# -- fill table
		nik_name = window.nik_name_field.text()
		data = {
		'nik_name' : nik_name,
		'password' : window.password_field.text(),
		'email' : window.email_field.text(),
		'phone' : window.phone_field.text(),
		'outsource' : window.autsource_check_box.checkState(),
		'specialty' : window.specialty_field.text(),
		'workroom' : wr_id_list,
		'share_dir' : window.share_dir_field.text(),
		'level' : window.level_combobox.itemText(window.level_combobox.currentIndex()),
		}
		
		# get Outsource
		if data['outsource'] == QtCore.Qt.CheckState.Checked:
			data['outsource'] = True
		else:
			data['outsource'] = False
		
		# save artist data
		result = self.artist.edit_artist(data, artist_current_data = selected_data)
		
		if not result[0]:
			self.message(result[1], 2)
			return
		
		# get artist data
		#print('*'*5, self.current_user, nik_name)
		if self.artist.nik_name == nik_name:
			self.get_artist_data()
			
		# finish
		self.reload_artist_list()
		window.close()
			
		print('edit artist action', data)
	
	# ----------------- Artist Edit Workroom ----------------------------
	def artist_edit_workroom2_ui(self, current_widget):
		# get all workrooms
		bool_, workrooms = self.db_workroom.get_list_workrooms()
		
		if not bool_:
			self.message(workrooms, 3)
			return
				
		# get exists workrooms
		workroom_list = []
		if current_widget.workroom_field.text():
			workroom_list = json.loads(current_widget.workroom_field.text())
		
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.select_from_check_button_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.selectWorkroomDialog2 = loader.load(file, self)
		file.close()
		
		# edit widget
		window.setWindowTitle('Select WorkRoom')
		
		# -- add checkbox
		checkbox_list = []
		layout = QtGui.QVBoxLayout()
		for wr in workrooms:
			wr_name = wr['name']
			box = QtGui.QCheckBox(wr_name, window.check_buttons_frame)
			checkbox_list.append(box)
			if wr_name in workroom_list:
				box.setCheckState(QtCore.Qt.CheckState.Checked)
				
			layout.addWidget(box)
		window.check_buttons_frame.setLayout(layout)
		
		# -- edit button
		window.select_from_chbut_cansel_button.clicked.connect(partial(self.close_window, window))
		window.select_from_chbut_apply_button.clicked.connect(partial(self.artist_edit_workroom2_action, current_widget, window, checkbox_list))
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()
		
	def artist_edit_workroom2_action(self, current_widget, window, checkbox_list):
		# get data
		data = []
		for obj in checkbox_list:
			if obj.checkState() == QtCore.Qt.CheckState.Checked:
				data.append(obj.text())
		# set data
		current_widget.workroom_field.setText(json.dumps(data))
		self.close_window(window)
		
		# get artist data
		#self.get_artist_data()
		
	
	def artist_edit_workroom_ui(self, current_widget):
		# select_from_list_dialog.ui
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.select_from_list_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		self.selectWorkroomDialog = loader.load(file, self)
		file.close()
		
		# get exists workrooms
		workroom_list = []
		if current_widget.workroom_field.text():
			workroom_list = json.loads(current_widget.workroom_field.text())
				
		# edit widget
		self.selectWorkroomDialog.setWindowTitle('Select WorkRoom')
		
		# edit table
		# -- fill table
		table = self.selectWorkroomDialog.select_from_list_data_list_table
		self.fill_workroom_table(table)
		
		# -- selection mode
		table.setSortingEnabled(True)
		table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		table.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		
		
		# edit button
		self.selectWorkroomDialog.select_from_list_cansel_button.clicked.connect(partial(self.close_window, self.selectWorkroomDialog))
		self.selectWorkroomDialog.select_from_list_apply_button.clicked.connect(partial(self.artist_edit_workroom_action, current_widget))
		
		# set modal window
		self.selectWorkroomDialog.setWindowModality(QtCore.Qt.WindowModal)
		self.selectWorkroomDialog.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		self.selectWorkroomDialog.show()
		
	def artist_edit_workroom_action(self, current_widget):
		items = self.selectWorkroomDialog.select_from_list_data_list_table.selectedItems()
				
		data = []
		for item in items:
			data.append(item.text())
		'''	
		copy = db.workroom()
		result = copy.name_list_to_id_list(data)
		if result[0]:
			data = result[1]
		else:
			self.message(result[1], 2)
			return
		
		print(data, result)
		return
		'''
		current_widget.workroom_field.setText(json.dumps(data))
		self.close_window(self.selectWorkroomDialog)
		
		# get artist data
		#self.get_artist_data()
		
	
	# ------------------ Artist Get Share Dir ---------------------------
	def get_share_dir(self, field):
		# get path
		home = os.path.expanduser('~')
		folder = QtGui.QFileDialog.getExistingDirectory(self, home)
		field.setText(str(folder))
	
	
	
	# ******************* STUDIO EDITOR /// WORKROOM EDITOR ****************************
	
	def edit_ui_to_workroom_editor(self):
		# edit label
		self.myWidget.studio_editor_label.setText('WorkRoom Editor')
				
		# edit button
		self.myWidget.studio_butt_1.setVisible(True)
		self.myWidget.studio_butt_1.setText('Reload')
		try:
			self.myWidget.studio_butt_1.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_1.clicked.connect(self.reload_workroom_list)
		self.myWidget.studio_butt_2.setVisible(True)
		self.myWidget.studio_butt_2.setText('New')
		try:
			self.myWidget.studio_butt_2.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_2.clicked.connect(self.new_workroom_ui)
		self.myWidget.studio_butt_3.setVisible(False)
		self.myWidget.studio_butt_4.setVisible(False)
		self.myWidget.studio_butt_5.setVisible(True)
		self.myWidget.studio_butt_5.setText('Rename')
		try:
			self.myWidget.studio_butt_5.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_5.clicked.connect(self.rename_workroom_ui)
		self.myWidget.studio_butt_6.setVisible(True)
		self.myWidget.studio_butt_6.setText('Edit Artist List')
		try:
			self.myWidget.studio_butt_6.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_6.clicked.connect(self.edit_ui_to_edit_artist_list)
		self.myWidget.studio_butt_7.setVisible(False)
		self.myWidget.studio_butt_8.setVisible(False)
		self.myWidget.studio_butt_9.setVisible(False)
		self.myWidget.studio_butt_10.setVisible(False)
		
		# edit combobox 
		self.myWidget.set_comboBox_01.setVisible(False)
		self.myWidget.set_comboBox_02.setVisible(False)
		self.myWidget.set_comboBox_03.setVisible(False)
		self.myWidget.group_search_qline.setVisible(False)
		
		# edit table
		#self.myWidget.studio_editor_table_2.setVisible(False)
		self.myWidget.right_table_frame.setVisible(False)
		# -- selection mode   
		self.myWidget.studio_editor_table.setSortingEnabled(True)
		#self.myWidget.studio_editor_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.myWidget.studio_editor_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
		self.myWidget.studio_editor_table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		
		self.clear_table()
		self.fill_workroom_table(self.myWidget.studio_editor_table)
				
	def fill_workroom_table(self, table):
		copy = self.db_workroom
		workrooms = copy.get_list_workrooms()
    
		if not workrooms[0]:
			return
			
		self.set_self_workrooms(workrooms = workrooms)
		
		# look_keys
		look_keys = ['name', 'type']
		
		# get table data
		num_row = len(workrooms[1])
		num_column = len(look_keys)
		headers = []
		
		for item in look_keys:
			headers.append(item)
			
		# make table
		table.setColumnCount(num_column)
		table.setRowCount(num_row)
		table.setHorizontalHeaderLabels(headers)
    
		
		# fill table
		for i, workroom in enumerate(workrooms[1]):
			for j,key in enumerate(headers):
				if key == 'date_time':
					continue
				newItem = QtGui.QTableWidgetItem()
				if workroom[key] and key == 'type':
					type_string = ','.join(workroom[key])
					newItem.setText(type_string)
				else:
					newItem.setText(workroom[key])
				newItem.workroom = workroom
				if key == 'name':
					color = self.workroom_color
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
	
				table.setItem(i, j, newItem)
		
		table.resizeRowsToContents()
		table.resizeColumnsToContents()
		
		print('fill workroom table')
				
	def reload_workroom_list(self):
		self.clear_table()
		self.fill_workroom_table(self.myWidget.studio_editor_table)
		print('reload workroom list')
		
	# -------------------- New Workroom ---------------------------------------
		
	def new_workroom_ui(self):
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.new_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		self.newWorkroomDialog = loader.load(file, self)
		file.close()
		
		# edit widget
		self.newWorkroomDialog.setWindowTitle('add New WorkRoom')
		self.newWorkroomDialog.new_dialog_label.setText('Name:')
		
		# edit button
		self.newWorkroomDialog.new_dialog_cancel.clicked.connect(partial(self.new_workroom_action, False))
		self.newWorkroomDialog.new_dialog_ok.clicked.connect(partial(self.new_workroom_action, True))
		
		# set modal window
		self.newWorkroomDialog.setWindowModality(QtCore.Qt.WindowModal)
		self.newWorkroomDialog.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		self.newWorkroomDialog.show()
		print('new workroom ui')
		
	def new_workroom_action(self, action):
		if not action:
			self.newWorkroomDialog.close()
			return
		else:
			name = self.newWorkroomDialog.new_dialog_name.text().replace(' ','_')
			if name == '':
				self.message('Not Name!', 2)
				return
			copy = self.db_workroom
			result = copy.add({'name': name})
			if not result[0]:
				self.message(result[1], 3)
			self.newWorkroomDialog.close()
			self.fill_workroom_table(self.myWidget.studio_editor_table)
			
	# -------------------- Rename Workroom ---------------------------------------
	
	def rename_workroom_ui(self):
		table = self.myWidget.studio_editor_table
		current_item = table.currentItem()
		if not current_item:
			self.message('Not Selected Workroom!', 2)
			return
		else:
			wr_data = current_item.workroom
			name = wr_data['name']
		
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.new_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		self.newWorkroomDialog = loader.load(file, self)
		file.close()
		
		# edit widget
		self.newWorkroomDialog.setWindowTitle('Rename WorkRoom')
		self.newWorkroomDialog.new_dialog_label.setText('New Name:')
		self.newWorkroomDialog.new_dialog_name.setText(name)
		
		# edit button
		self.newWorkroomDialog.new_dialog_cancel.clicked.connect(partial(self.rename_workroom_action, False))
		self.newWorkroomDialog.new_dialog_ok.clicked.connect(partial(self.rename_workroom_action, True))
		
		# set modal window
		self.newWorkroomDialog.setWindowModality(QtCore.Qt.WindowModal)
		self.newWorkroomDialog.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		self.newWorkroomDialog.show()
		
	def rename_workroom_action(self, action):
		if not action:
			self.newWorkroomDialog.close()
			return
		else:
			# get old_name
			old_name = None
			table = self.myWidget.studio_editor_table
			current_item = table.currentItem()
			if not current_item:
				self.message('Not Selected Workroom!', 2)
				return
			else:
				wr_data = current_item.workroom
				old_name = wr_data['name']
			
			new_name = self.newWorkroomDialog.new_dialog_name.text().replace(' ','_')
			
			result = self.db_workroom.rename_workroom(old_name, new_name)
			if not result[0]:
				self.message(result[1], 3)
				return
			else:
				print(result[1])
				
			self.newWorkroomDialog.close()
			self.fill_workroom_table(self.myWidget.studio_editor_table)
			
	# -------------------- Workroom ADD  Artists Editor ---------------------------------------
	
	def edit_ui_to_edit_artist_list(self):
		# get workroom data
		wr_data = {}
		current_item = self.myWidget.studio_editor_table.currentItem()
		if not current_item:
			self.message('Not Selected Workroom!', 2)
			return
		else:
			self.workroom = current_item.workroom
		name = self.workroom['name']
				
		# edit label
		self.myWidget.studio_editor_label.setText(('WorkRoom Editor / \"' + name + '\" - edit Artist List'))
		
		# edit button
		self.myWidget.studio_butt_1.setVisible(True)
		self.myWidget.studio_butt_1.setText('Reload')
		try:
			self.myWidget.studio_butt_1.clicked.disconnect()
		except:
			pass
		#self.myWidget.studio_butt_1.clicked.connect(self.reload_workroom_list)
		self.myWidget.studio_butt_2.setVisible(True)
		self.myWidget.studio_butt_2.setText('Add Artists')
		try:
			self.myWidget.studio_butt_2.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_2.clicked.connect(self.add_artists_to_workroom_dialog)
		self.myWidget.studio_butt_3.setVisible(True)
		self.myWidget.studio_butt_3.setText('Remove Selected Artists')
		try:
			self.myWidget.studio_butt_3.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_3.clicked.connect(partial(self.remove_artists_from_workroom_action, self.myWidget.studio_editor_table))
		self.myWidget.studio_butt_4.setVisible(True)
		self.myWidget.studio_butt_4.setText('Back')
		try:
			self.myWidget.studio_butt_4.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_4.clicked.connect(self.edit_ui_to_workroom_editor)
		self.myWidget.studio_butt_5.setVisible(False)
		self.myWidget.studio_butt_6.setVisible(False)
		self.myWidget.studio_butt_7.setVisible(False)
		self.myWidget.studio_butt_8.setVisible(False)
		self.myWidget.studio_butt_9.setVisible(False)
		self.myWidget.studio_butt_10.setVisible(False)
		
		# edit combobox 
		self.myWidget.set_comboBox_01.setVisible(False)
		self.myWidget.set_comboBox_02.setVisible(False)
		self.myWidget.set_comboBox_03.setVisible(False)
		self.myWidget.group_search_qline.setVisible(False)
		
		# edit table
		#self.myWidget.studio_editor_table_2.setVisible(False)
		self.myWidget.right_table_frame.setVisible(False)
		# -- selection mode   
		self.myWidget.studio_editor_table.setSortingEnabled(True)
		self.myWidget.studio_editor_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.myWidget.studio_editor_table.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		
		# fill table
		self.clear_table()
		self.fill_active_artist_table_at_workroom()
				
		
		print('edit ui to edit artist list')
		
	def add_artists_to_workroom_dialog(self):
		workroom = self.workroom['name']
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.select_from_list_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.addArtistToWorkroomDialog = loader.load(file, self)
		file.close()
		
		# edit widget
		window.setWindowTitle(('Add Artist To \"' + self.workroom['name'] + '\"'))
		window.select_from_list_apply_button.setText('Add Select Artists')
		window.select_from_list_apply_button.clicked.connect(partial(self.add_select_artists_to_workroom, window))
		window.select_from_list_cansel_button.clicked.connect(partial(self.close_window, window))
		
		# edit table
		#self.myWidget.studio_editor_table_2.setVisible(False)
		self.myWidget.right_table_frame.setVisible(False)
		# -- selection mode   
		window.select_from_list_data_list_table.setSortingEnabled(True)
		window.select_from_list_data_list_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		window.select_from_list_data_list_table.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()
		
		self.fill_active_artist_table_for_workroom(window)
		print('add artist to workroom dialog')
		
	def fill_active_artist_table_at_workroom(self):
		bool_, artists = self.artist.read_artist('all')
    
		if not bool_:
			self.message(artists, 2)
			return
		
		wr_id = self.workroom.get('id')
			
		# get artist list
		active_artists = []
		for artist in artists:
			# get workroom
			wr_list = []
			if wr_id in artist['workroom'] and artist['status'] == 'active':
				active_artists.append(artist)
    
		# get table data
		num_row = len(active_artists)
		num_column = len(self.look_keys)
		headers = self.look_keys
		    
		# make table
		self.myWidget.studio_editor_table.setColumnCount(num_column)
		self.myWidget.studio_editor_table.setRowCount(num_row)
		self.myWidget.studio_editor_table.setHorizontalHeaderLabels(headers)
    
		# fill table
		for i, artist in enumerate(active_artists):
			for j,key in enumerate(headers):
				if not (key in self.look_keys):
					continue
				newItem = QtGui.QTableWidgetItem()
				newItem.setText(artist[key])
				newItem.artist = artist
				if key == 'nik_name':
					color = self.artist_color
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)				
				self.myWidget.studio_editor_table.setItem(i, j, newItem)
        
		print('fill active artist table')
		
	def fill_active_artist_table_for_workroom(self, window):
		artists = self.artist.read_artist('all')
    
		if not artists[0]:
			return
			
		# get active list
		active_artists = []
		for artist in artists[1]:
			if artist['status'] == 'active':
				active_artists.append(artist)
				
		wr_id = self.workroom.get('id')
    
		# get table data
		num_row = len(active_artists)
		num_column = len(self.look_keys)
		headers = self.look_keys
		    
		# make table
		window.select_from_list_data_list_table.setColumnCount(num_column)
		window.select_from_list_data_list_table.setRowCount(num_row)
		window.select_from_list_data_list_table.setHorizontalHeaderLabels(headers)
    
		# fill table
		for i, artist in enumerate(active_artists):
			wr_list = []
			if artist['workroom']:
				wr_list = artist['workroom']
			for j,key in enumerate(headers):
				if not (key in self.look_keys):
					continue
				newItem = QtGui.QTableWidgetItem()
				newItem.setText(artist[key])
				newItem.artist = artist
				if key == 'nik_name' and not wr_id in wr_list:
					color = self.artist_color
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
				elif wr_id in wr_list:
					color = self.grey_color
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
				
				window.select_from_list_data_list_table.setItem(i, j, newItem)
        
		print('fill active artist table')
		
	def add_select_artists_to_workroom(self, window):
		table = window.select_from_list_data_list_table
		column = table.columnCount()
		name_column = None
		for i in range(0, column):
			head_item = table.horizontalHeaderItem(i)
			if head_item.text() == 'nik_name':
				name_column = i
				break
		
		# get selected rows
		selected = table.selectedItems()
		artists = []
		for item in selected:
			if item.column() == name_column:
				artists.append(item.artist)
		
		wr_id = self.workroom.get('id')
		
		for artist in artists:
			workrooms = []
			if artist['workroom']:
				workrooms = artist['workroom']
			
			if not wr_id in workrooms:
				workrooms.append(wr_id)
				#keys = {'nik_name': artist_, 'workroom' : json.dumps(workrooms)}
				keys = {'nik_name': artist['nik_name'], 'workroom' : workrooms}
				bool_, return_data = self.artist.edit_artist(keys)
				if not bool_:
					self.message(return_data, 2)
				
			print(wr_id, workrooms)
				
		self.fill_active_artist_table_for_workroom(window)
		self.fill_active_artist_table_at_workroom()
		
		# get artist data
		self.get_artist_data()
		
		
	def remove_artists_from_workroom_action(self, table):
		column = table.columnCount()
		name_column = None
		for i in range(0, column):
			head_item = table.horizontalHeaderItem(i)
			if head_item.text() == 'nik_name':
				name_column = i
				break
		
		# get selected rows
		selected = table.selectedItems()
		artists = []
		for item in selected:
			if item.column() == name_column:
				artists.append(item.artist)
				
		wr_id = self.workroom.get('id')
		
		# remove artist from workroom
		for artist in artists:
			workrooms = []
			if artist.get('workroom'):
				workrooms = artist.get('workroom')
			
			if wr_id in workrooms:
				workrooms.remove(wr_id)
				keys = {'nik_name': artist['nik_name'], 'workroom' : workrooms}
				bool_, return_data = self.artist.edit_artist(keys)
				if not bool_:
					self.message('look terminal', 2)
					print(return_data)
					return
				
		
		# get artist data
		self.get_artist_data()
				
		self.fill_active_artist_table_at_workroom()
		print('remove select artists from workroom', artists)
		
	# ******************* STUDIO EDITOR /// PROJECT EDITOR ****************************
	def edit_ui_to_project_editor(self):
		# edit label
		self.myWidget.studio_editor_label.setText('Project Editor')
				
		# edit button
		self.myWidget.studio_butt_1.setVisible(True)
		self.myWidget.studio_butt_1.setText('Reload')
		try:
			self.myWidget.studio_butt_1.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_1.clicked.connect(self.reload_project_list)
		self.myWidget.studio_butt_2.setVisible(True)
		self.myWidget.studio_butt_2.setText('Create / Attache')
		try:
			self.myWidget.studio_butt_2.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_2.clicked.connect(self.new_project_ui)
		self.myWidget.studio_butt_3.setVisible(True)
		self.myWidget.studio_butt_3.setText('Rename')
		try:
			self.myWidget.studio_butt_3.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_3.clicked.connect(partial(self.rename_project_ui, self.myWidget.studio_editor_table))
		self.myWidget.studio_butt_4.setVisible(True)
		self.myWidget.studio_butt_4.setText('Remove')
		try:
			self.myWidget.studio_butt_4.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_4.clicked.connect(partial(self.remove_project_action, self.myWidget.studio_editor_table))
		self.myWidget.studio_butt_5.setVisible(True)
		self.myWidget.studio_butt_5.setText('Deactivate')
		try:
			self.myWidget.studio_butt_5.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_5.clicked.connect(partial(self.edit_status_project_action, self.myWidget.studio_editor_table, 'none'))
		self.myWidget.studio_butt_6.setVisible(True)
		self.myWidget.studio_butt_6.setText('Set Active')
		try:
			self.myWidget.studio_butt_6.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_6.clicked.connect(partial(self.edit_status_project_action, self.myWidget.studio_editor_table, 'active'))
		self.myWidget.studio_butt_7.setVisible(False)
		self.myWidget.studio_butt_8.setVisible(False)
		self.myWidget.studio_butt_9.setVisible(False)
		self.myWidget.studio_butt_10.setVisible(False)
		
		# edit combobox 
		self.myWidget.set_comboBox_01.setVisible(False)
		self.myWidget.set_comboBox_02.setVisible(False)
		self.myWidget.set_comboBox_03.setVisible(False)
		self.myWidget.group_search_qline.setVisible(False)
		
		# edit table
		#self.myWidget.studio_editor_table_2.setVisible(False)
		self.myWidget.right_table_frame.setVisible(False)
		# -- selection mode   
		self.myWidget.studio_editor_table.setSortingEnabled(True)
		self.myWidget.studio_editor_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.myWidget.studio_editor_table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		
		self.clear_table()
		self.fill_project_table(self.myWidget.studio_editor_table)
		
	def reload_project_list(self):
		self.clear_table()
		self.fill_project_table(self.myWidget.studio_editor_table)
		
	def fill_project_table(self, table):
		#copy = db.studio() # self.db_studio
		self.db_group.get_list_projects()
		
		if not self.db_group.list_projects:
			return
			
		projects = []
		for key in self.db_group.list_projects.keys():
			projects.append({'name' : key,'status' : self.db_group.list_projects[key]['status'], 'path': self.db_group.list_projects[key]['path']})
		
		# get table data
		columns = ('name', 'status', 'path')
		num_row = len(projects)
		num_column = len(columns)
		headers = columns
		
		# make table
		table.setColumnCount(num_column)
		table.setRowCount(num_row)
		table.setHorizontalHeaderLabels(headers)
    
		
		# fill table
		for i, project in enumerate(projects):
			for j,key in enumerate(headers):
				newItem = QtGui.QTableWidgetItem()
				newItem.setText(project[key])
				if key == 'name':
					color = self.project_color
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
	
				table.setItem(i, j, newItem)
		
		table.resizeRowsToContents()
		table.resizeColumnsToContents()
		
		print('fill project table')
	
	def new_project_ui(self):
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.qt_set_project_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.setProjectDialog = loader.load(file, self)
		file.close()
		
		# edit widget
		window.setWindowTitle('Create Project')
		window.set_project_cansel_button.clicked.connect(partial(self.close_window, window))
		window.set_project_ok_button.clicked.connect(partial(self.new_project_action, window))
		window.set_project_path_button.clicked.connect(partial(self.get_share_dir, window.set_project_folder))
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()
		print('new project ui')
		
	def new_project_action(self, window):
		# get data
		name = window.priject_name_field.text()
		path = window.set_project_folder.text()
		
		copy = self.db_group
		result = copy.add_project(name, path)
		if not result[0]:
			self.message(result[1], 3)
			return
		
		self.clear_table()
		self.fill_project_table(self.myWidget.studio_editor_table)
		'''
		# recycle bin
		result = copy.create_recycle_bin(name)
		if not result[0]:
			self.message(result[1], 3)
			#return(False, result[1])
		else:
			print('RB created!')
		'''
		self.close_window(window)
		
		self.current_project = name
		self.get_list_active_projects()
		self.tm_fill_project_list()
		
	def rename_project_ui(self, table):
		column = table.columnCount()
		name_column = None
		for i in range(0, column):
			head_item = table.horizontalHeaderItem(i)
			if head_item.text() == 'name':
				name_column = i
				break
		
		# get selected rows
		selected = table.selectedItems()
		projects = []
		for item in selected:
			if item.column() == name_column:
				projects.append(item.text())
				
		if projects == []:
			self.message('Not Selected Project', 2)
			return
		
		project = projects[0]
		
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.new_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.setProjectDialog = loader.load(file, self)
		file.close()
		
		# edit widget
		window.setWindowTitle(('Rename Project: ' + project))
		window.new_dialog_label.setText('New Name:')
		window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.new_dialog_ok.clicked.connect(partial(self.rename_project_action, window, project))
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()
		print('new project ui', project)
		
	def rename_project_action(self, window, project):
		# get data
		new_name = window.new_dialog_name.text()
		if new_name == '':
			self.message('Not Name!', 3)
			return
			
		copy = self.db_group
		result = copy.rename_project(project, new_name)
		if not result[0]:
			self.message(result[1], 2)
			return
		
		self.clear_table()
		self.fill_project_table(self.myWidget.studio_editor_table)
		self.close_window(window)
		
		self.current_project = new_name
		self.get_list_active_projects()
		self.tm_fill_project_list()
		
	def remove_project_action(self, table):
		ask = self.message('You Are Soure?', 0)
		if not ask:
			return
		
		column = table.columnCount()
		name_column = None
		for i in range(0, column):
			head_item = table.horizontalHeaderItem(i)
			if head_item.text() == 'name':
				name_column = i
				break
		
		# get selected rows
		selected = table.selectedItems()
		projects = []
		for item in selected:
			if item.column() == name_column:
				projects.append(item.text())
				
		if projects == []:
			self.message('Not Selected Project', 2)
			return
		
		project = projects[0]
		
		copy = self.db_group
		result = copy.remove_project(project)
		if not result[0]:
			self.message(result[1], 2)
			return
		
		self.clear_table()
		self.fill_project_table(self.myWidget.studio_editor_table)
		
		self.get_list_active_projects()
		self.tm_fill_project_list()
		
	def edit_status_project_action(self, table, status):
		ask = self.message('You Are Soure?', 0)
		if not ask:
			return
		
		column = table.columnCount()
		name_column = None
		for i in range(0, column):
			head_item = table.horizontalHeaderItem(i)
			if head_item.text() == 'name':
				name_column = i
				break
		
		# get selected rows
		selected = table.selectedItems()
		projects = []
		for item in selected:
			if item.column() == name_column:
				projects.append(item.text())
				
		if projects == []:
			self.message('Not Selected Project', 2)
			return
		
		project = projects[0]
		
		copy = self.db_group
		result = copy.edit_status(project, status)
		if not result[0]:
			self.message(result[1], 2)
			return
		
		self.clear_table()
		self.fill_project_table(self.myWidget.studio_editor_table)
		self.get_list_active_projects()
		self.tm_fill_project_list()
		print('deactivate project action')
		
	# ******************* STUDIO EDITOR /// SET OF TASKS EDITOR ****************************
	
	def edit_ui_to_set_of_tasks_editor(self):
		# edit label
		self.myWidget.studio_editor_label.setText('Set Of Tasks Editor')
				
		# edit button
		self.myWidget.studio_butt_1.setVisible(True)
		self.myWidget.studio_butt_1.setText('Reload')
		try:
			self.myWidget.studio_butt_1.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_1.clicked.connect(self.reload_set_of_tasks_list)
		self.myWidget.studio_butt_2.setVisible(True)
		self.myWidget.studio_butt_2.setText('Create')
		try:
			self.myWidget.studio_butt_2.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_2.clicked.connect(self.new_set_of_tasks_ui)
		self.myWidget.studio_butt_3.setVisible(True)
		self.myWidget.studio_butt_3.setText('Make Copy')
		try:
			self.myWidget.studio_butt_3.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_3.clicked.connect(partial(self.copy_set_of_tasks_ui))
		self.myWidget.studio_butt_4.setVisible(True)
		self.myWidget.studio_butt_4.setText('Rename')
		try:
			self.myWidget.studio_butt_4.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_4.clicked.connect(partial(self.rename_set_of_tasks_ui, self.myWidget.studio_editor_table))
		self.myWidget.studio_butt_5.setVisible(True)
		self.myWidget.studio_butt_5.setText('Edit Asset Type')
		try:
			self.myWidget.studio_butt_5.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_5.clicked.connect(partial(self.edit_asset_type_ui, self.myWidget.studio_editor_table))
		self.myWidget.studio_butt_6.setVisible(True)
		self.myWidget.studio_butt_6.setText('Remove')
		try:
			self.myWidget.studio_butt_6.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_6.clicked.connect(partial(self.remove_set_of_tasks_action, self.myWidget.studio_editor_table))
		self.myWidget.studio_butt_7.setVisible(True)
		self.myWidget.studio_butt_7.setText('Edit')
		try:
			self.myWidget.studio_butt_7.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_7.clicked.connect(partial(self.edit_set_of_tasks_ui, self.myWidget.studio_editor_table))
		self.myWidget.studio_butt_8.setVisible(True)
		self.myWidget.studio_butt_8.setText('Save Library')
		try:
			self.myWidget.studio_butt_8.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_8.clicked.connect(partial(self.save_set_of_task_to_library_ui))
		self.myWidget.studio_butt_9.setVisible(True)
		self.myWidget.studio_butt_9.setText('Load Library')
		try:
			self.myWidget.studio_butt_9.clicked.disconnect()
		except:
			pass
		self.myWidget.studio_butt_9.clicked.connect(partial(self.load_set_of_task_from_library_ui))
		self.myWidget.studio_butt_10.setVisible(False)
		
		# edit combobox 
		self.myWidget.set_comboBox_01.setVisible(False)
		self.myWidget.set_comboBox_02.setVisible(False)
		self.myWidget.set_comboBox_03.setVisible(False)
		self.myWidget.group_search_qline.setVisible(False)
		
		# edit table
		#self.myWidget.studio_editor_table_2.setVisible(False)
		self.myWidget.right_table_frame.setVisible(False)
		# -- selection mode   
		self.myWidget.studio_editor_table.setSortingEnabled(True)
		self.myWidget.studio_editor_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.myWidget.studio_editor_table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		
		self.clear_table()
		self.fill_set_of_tasks_table(self.myWidget.studio_editor_table)
		
	def fill_set_of_tasks_table(self, table):
		copy = self.db_set_of_tasks
		
		# get data list
		list_sets = copy.get_list()
		if not list_sets[0]:
			return
		
		data_to_fill = []
		for key in list_sets[1].keys():
			data_to_fill.append({'name' : key, 'asset_type': list_sets[1][key]['asset_type']})
		
		# get table data
		columns = ('name', 'asset_type')
		num_row = len(data_to_fill)
		num_column = len(columns)
		headers = columns
		
		# make table
		table.setColumnCount(num_column)
		table.setRowCount(num_row)
		table.setHorizontalHeaderLabels(headers)
    
		
		# fill table
		for i, project in enumerate(data_to_fill):
			for j,key in enumerate(headers):
				newItem = QtGui.QTableWidgetItem()
				newItem.setText(project[key])
				newItem.name = project['name']
				if key == 'name':
					color = self.set_of_tasks_color
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
	
				table.setItem(i, j, newItem)
					
		print('fill set of tasks table')
		
	def reload_set_of_tasks_list(self):
		self.clear_table()
		self.fill_set_of_tasks_table(self.myWidget.studio_editor_table)
		
	def new_set_of_tasks_ui(self):
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.new_dialog_2_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.setProjectDialog = loader.load(file, self)
		file.close()
		
		# edit widget
		copy = self.db_studio
		window.setWindowTitle('Create Set Of Tasks')
		window.new_dialog_label.setText('Name of New Set:')
		window.new_dialog_label_2.setText('Type of Asset')
		window.new_dialog_combo_box.addItems(copy.asset_types)
		window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.new_dialog_ok.clicked.connect(partial(self.new_set_of_tasks_action, window))
				
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()
		
		print('create set of tasks')
		
	def new_set_of_tasks_action(self, window):
		# get data
		name = window.new_dialog_name.text()
		asset_type = window.new_dialog_combo_box.currentText()
		
		# create
		#copy = db.set_of_tasks()
		result = self.db_set_of_tasks.create(name, asset_type)
		
		if not result[0]:
			self.message(result[1], 2)
			return
		
		self.close_window(window)
		self.reload_set_of_tasks_list()
		print('create set of tasks action')
		
	def copy_set_of_tasks_ui(self):
		old_name = self.myWidget.studio_editor_table.currentItem().name
		
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.new_dialog_path)
		file.open(QtCore.QFile.ReadOnly)
		window = self.setProjectDialog = loader.load(file, self)
		file.close()
		
		# edit widget
		window.setWindowTitle(('Make Copy: ' + old_name))
		window.new_dialog_label.setText('New Name of Set:')
		window.new_dialog_name.setText(old_name)
		window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.new_dialog_ok.clicked.connect(partial(self.copy_set_of_tasks_action, window, old_name))
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()
	
	def copy_set_of_tasks_action(self, window, old_name):
		
		# get new_name
		new_name = window.new_dialog_name.text()
		if new_name == old_name:
			self.message('match names!', 2)
			return
			
		result, data = self.db_set_of_tasks.copy_set_of_tasks(old_name, new_name)
		if not result:
			self.message(data, 3)
			return
		
		self.reload_set_of_tasks_list()
		window.close()
		
	def rename_set_of_tasks_ui(self, table):
		column = table.columnCount()
		name_column = None
		for i in range(0, column):
			head_item = table.horizontalHeaderItem(i)
			if head_item.text() == 'name':
				name_column = i
				break
		
		# get selected rows
		selected = table.selectedItems()
		lists = []
		for item in selected:
			if item.column() == name_column:
				lists.append(item.text())
				
		if lists == []:
			self.message('Not Selected Set', 2)
			return
		
		name = lists[0]
		
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.new_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.setProjectDialog = loader.load(file, self)
		file.close()
		
		# edit widget
		window.setWindowTitle(('Rename: ' + name))
		window.new_dialog_label.setText('New Name of Set:')
		window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.new_dialog_ok.clicked.connect(partial(self.rename_set_of_tasks_action, name, window))
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()
		
		print('rename set of tasks ui')
		
	def rename_set_of_tasks_action(self, old_name, window):
		# get data
		new_name = window.new_dialog_name.text()
		
		# rename
		#copy = db.set_of_tasks()
		result = self.db_set_of_tasks.rename(old_name, new_name)
		
		if not result[0]:
			self.message(result[1], 2)
			return
		
		self.close_window(window)
		self.reload_set_of_tasks_list()
		print('rename set action')
		
	def remove_set_of_tasks_action(self, table):
		# ask
		ask = self.message('You Are Soure?', 0)
		if not ask:
			return
		
		# get name
		column = table.columnCount()
		name_column = None
		for i in range(0, column):
			head_item = table.horizontalHeaderItem(i)
			if head_item.text() == 'name':
				name_column = i
				break
		
		# get selected rows
		selected = table.selectedItems()
		lists = []
		for item in selected:
			if item.column() == name_column:
				lists.append(item.text())
				
		if lists == []:
			self.message('Not Selected Set', 2)
			return
		
		name = lists[0]
		
		# remove
		#copy = db.set_of_tasks()
		result = self.db_set_of_tasks.remove(name)
		
		if not result[0]:
			self.message(result[1], 2)
			return
				
		self.reload_set_of_tasks_list()
		print('remove set of tasks ui')
		
	def edit_set_of_tasks_ui(self, table, geometry = False):
		# get name
		column = table.columnCount()
		name_column = None
		for i in range(0, column):
			head_item = table.horizontalHeaderItem(i)
			if head_item.text() == 'name':
				name_column = i
				break
		
		# get selected rows
		selected = table.selectedItems()
		lists = []
		for item in selected:
			if item.column() == name_column:
				lists.append(item.text())
				
		if lists == []:
			self.message('Not Selected Set', 2)
			return
		
		name = lists[0]
		
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.select_from_list_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.selectWorkroomDialog = loader.load(file, self)
		file.close()
		
		# fill table
		copy = self.db_set_of_tasks
		data = copy.get(name)
		
		if not data[0]:
			self.message(data[1], 2)
			return
		else:
			right_data = data[1]['sets']
			asset_type = data[1]['asset_type']
			
		'''
		right_data = []
		
		if data[1]:
			for key in data:
				data[key]['task_name'] = key
				right_data.append(data[key])
		'''
		
		# -- get table data
		num_row = 100
		num_column = len(copy.set_of_tasks_keys)
		headers = copy.set_of_tasks_keys
		    
		# -- make table
		window.select_from_list_data_list_table.setColumnCount(num_column)
		window.select_from_list_data_list_table.setRowCount(num_row)
		window.select_from_list_data_list_table.setHorizontalHeaderLabels(headers)
		
		# -- edit table
		window.select_from_list_data_list_table.setDragEnabled(True)
		window.select_from_list_data_list_table.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
		
		# context menu
		# -- get workroom list
		wr = self.db_workroom
		wr_list = wr.get_list_workrooms()
		
		# -- get wr_list by id
		result = wr.get_list_workrooms(DICTONARY = 'by_id')
		if not result[0]:
			self.message(result[1], 3)
			#return
		wr_by_id_list = result[1]
		
		if wr_list[0]:
			# -- add menu  
			window.select_from_list_data_list_table.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
			# workroom menu
			addgrup_action = QtGui.QAction( '== workrooms == ', window)
			window.select_from_list_data_list_table.addAction( addgrup_action )
			for w_room in wr_list[1]:
				wr_name = w_room['name']
				addgrup_action = QtGui.QAction( wr_name, window)
				#addgrup_action.setToolTip( 'to WorkRoom column' )
				addgrup_action.triggered.connect(partial(self.insert_data_in_table, wr_name, window.select_from_list_data_list_table, 'workroom'))
				window.select_from_list_data_list_table.addAction( addgrup_action )
			
			# activity
			addgrup_action = QtGui.QAction( '== activity == ', window)
			window.select_from_list_data_list_table.addAction( addgrup_action )
			#asset = db.asset() # folders.sort
			list_activity = self.db_asset.activity_folder[asset_type].keys()
			list_activity.sort()
			for activity in list_activity:
				addgrup_action = QtGui.QAction( activity, window)
				addgrup_action.triggered.connect(partial(self.insert_data_in_table, activity, window.select_from_list_data_list_table, 'activity'))
				window.select_from_list_data_list_table.addAction( addgrup_action )
				
			# task type menu
			addgrup_action = QtGui.QAction( '== task types == ', window)
			window.select_from_list_data_list_table.addAction( addgrup_action )
			for type_ in copy.task_types:
				addgrup_action = QtGui.QAction( type_, window)
				addgrup_action.triggered.connect(partial(self.insert_data_in_table, type_, window.select_from_list_data_list_table, 'task_type'))
				window.select_from_list_data_list_table.addAction( addgrup_action )
			
			# extensions menu
			addgrup_action = QtGui.QAction( '== extensions == ', window)
			window.select_from_list_data_list_table.addAction( addgrup_action )
			for ext in copy.extensions:
				addgrup_action = QtGui.QAction( ext, window)
				addgrup_action.triggered.connect(partial(self.insert_data_in_table, ext, window.select_from_list_data_list_table, 'extension'))
				window.select_from_list_data_list_table.addAction( addgrup_action )
			
			# extensions menu
			addgrup_action = QtGui.QAction( '== input service task == ', window)
			window.select_from_list_data_list_table.addAction( addgrup_action )
			for text in copy.service_tasks:
				addgrup_action = QtGui.QAction( text, window)
				addgrup_action.triggered.connect(partial(self.insert_data_in_table, text, window.select_from_list_data_list_table, 'input'))
				window.select_from_list_data_list_table.addAction( addgrup_action )
    
		# fill table
		for i, set_of_tasks in enumerate(right_data):
			for j,key in enumerate(headers):
				if not (key in copy.set_of_tasks_keys):
					continue
				newItem = QtGui.QTableWidgetItem()
				try:
					newItem.setText(set_of_tasks[key])
				except:
					pass
				if key == 'task_name':
					color = self.tasks_color
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
				elif key == 'workroom':
					try:
						if set_of_tasks[key] in wr_by_id_list.keys():
							wr_name = wr_by_id_list[set_of_tasks[key]]['name']
							newItem.setText(wr_name)
						else:
							newItem.setText('')
						
					except:
						pass
								
				window.select_from_list_data_list_table.setItem(i, j, newItem)
		
		# fill empty items
		for i in range(len(right_data), num_row):
			for j in range(0, num_column):
				newItem = QtGui.QTableWidgetItem()
				window.select_from_list_data_list_table.setItem(i, j, newItem)
				
		# edit widjet
		window.setWindowTitle(('Edit Set Of Tasks: ' + name))
		window.select_from_list_cansel_button.clicked.connect(partial(self.close_window, window))
		window.select_from_list_apply_button.setText('Save Data')
		window.select_from_list_apply_button.clicked.connect(partial(self.edit_set_of_tasks_action, window, window.select_from_list_data_list_table, name))
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		if geometry:
			window.setGeometry(geometry)
		else:
			window.resize(1000, 412)
			
		window.show()
		

	def edit_set_of_tasks_action(self, window, table, Name):
		# wr 
		wr = self.db_workroom
		result = wr.get_list_workrooms(DICTONARY = 'by_name')
		if not result[0]:
			self.message(result[1], 3)
			return
		wr_list = result[1]
		'''
		# debug
		print(wr_list)
		return
		'''
		# get data
		num_column = table.columnCount()
		num_row = table.rowCount()
		
		data = []
		names = []
		inputs = []
				
		for i in range(0, num_row):
			task_data = {}
			for j in range(0, num_column):
				head_item = table.horizontalHeaderItem(j)
				key = head_item.text()
				item = table.item(i,j)
				if item:
					task_data[key] = item.text()
				else:
					task_data[key] = u''
			
			if task_data['task_name']:
				# get wroom id
				wr_id = ''
				if task_data['workroom']:
					task_data['workroom'] = wr_list[task_data['workroom']]['id']
				data.append(task_data)
				#print(task_data)
				names.append(task_data['task_name'])
				inputs.append(task_data['input'])
				
		# check the correctness of the name on inputs
		for name in inputs:
			if not name:
				continue
			elif name in ['all', 'pre']:
				continue
			if not name in names:
				self.message(('incorrect input name: \"' + name + '\"'), 2)
				return
		
		#return	
		#copy = db.set_of_tasks()
		#copy.edit(name, data)
		result, reply = self.db_set_of_tasks.edit(Name, data)
		if not result:
			self.message(reply, 3)
		
		geometry = window.frameGeometry()
		
		self.close_window(window)
		#self.reload_set_of_tasks_list()
		self.edit_set_of_tasks_ui(self.myWidget.studio_editor_table, geometry = geometry)
		print('edit set of tasks action')
		
	def save_set_of_task_to_library_ui(self, action = 'all'):
		home = os.path.expanduser('~')
		path, f = QtGui.QFileDialog.getSaveFileName(self, caption = 'Save Set_Of_Tasks To Library',  dir = home, filter = u'Json files (*.json)')
		
		split = os.path.splitext(path)
		
		if not split[1]:
			path = os.path.normpath(path + '.json')
		else:
			if split[1] != '.json':
				path = os.path.normpath(split[0] + '.json')
		
		self.save_set_of_task_to_library_action(path, action)
		
	def save_set_of_task_to_library_action(self, path, action):
		if action == 'all':
			result = self.db_set_of_tasks.save_set_of_tasks_to_library(path)
			if not result[0]:
				self.message(result[1], 3)
				
	def load_set_of_task_from_library_ui(self):
		home = os.path.expanduser('~')
		path, f = QtGui.QFileDialog.getOpenFileNames(self, caption = 'Load Set_Of_Tasks Library',  dir = home, filter = u'Json files (*.json)')
		
		
		result, data = self.db_set_of_tasks.get_list(path = path[0])
		
		if not result:
			self.message(data, 3)
			return
		
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.select_from_list_dialog_3button_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.addAssetsDialog = loader.load(file, self)
		file.close()
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		# set select mode
		window.select_from_list_data_list_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		window.select_from_list_data_list_table.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		
		columns = ['name','asset_type']
		
		# -- get table data
		num_row = len(data.keys())
		num_column = len(columns)
		headers = columns
		    
		# -- make table
		table = window.select_from_list_data_list_table
		table.setColumnCount(num_column)
		table.setRowCount(num_row)
		table.setHorizontalHeaderLabels(headers)
		
		# fill table
		for i, set_name in enumerate(data):
			for j,key in enumerate(headers):
				newItem = QtGui.QTableWidgetItem()
				
				if key == 'name':
					color = self.set_of_tasks_color
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
					newItem.setText(set_name)
				elif key == 'asset_type':
					newItem.setText(data[set_name][key])
					
				newItem.name = set_name
	
				table.setItem(i, j, newItem)
				
		# connect buttons
		window.pushButton_01.setText('Load Selected')
		window.pushButton_02.setText('Load All')
		window.select_from_list_cansel_button.clicked.connect(partial(self.close_window, window))
		window.pushButton_01.clicked.connect(partial(self.load_set_of_task_from_library_action, window, data, 'selected'))
		window.pushButton_02.clicked.connect(partial(self.load_set_of_task_from_library_action, window, data, 'all'))
		
		# context menu
		table.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
		addgrup_action = QtGui.QAction( 'Look Set_of_Tasks', self.myWidget)
		addgrup_action.triggered.connect(partial(self.look_set_of_task_from_library, table, data))
		table.addAction( addgrup_action )
		
		window.show()
		
	def load_set_of_task_from_library_action(self, window, data, action):
		if action == 'selected':
			selected_data = {}
			
			for item in window.select_from_list_data_list_table.selectedItems():
				selected_data[item.name] = data[item.name]
				
			data = selected_data
			
		elif action == 'all':
			pass
		
		result, data = self.db_set_of_tasks.load_set_of_tasks_from_library(data)
		if not result:
			self.message(data, 3)
		
		self.reload_set_of_tasks_list()
		window.close()
		
	def look_set_of_task_from_library(self, table, data):
		name = table.currentItem().name
		
		right_data = data[name]['sets']
		
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.select_from_list_dialog_path)
		file.open(QtCore.QFile.ReadOnly)
		window = self.selectWorkroomDialog = loader.load(file, self)
		file.close()
		
		# -- get table data
		num_row = len(right_data)
		num_column = len(self.db_set_of_tasks.set_of_tasks_keys)
		headers = self.db_set_of_tasks.set_of_tasks_keys
		    
		# -- make table
		window.select_from_list_data_list_table.setColumnCount(num_column)
		window.select_from_list_data_list_table.setRowCount(num_row)
		window.select_from_list_data_list_table.setHorizontalHeaderLabels(headers)
		
		# fill table
		for i, set_of_tasks in enumerate(right_data):
			for j,key in enumerate(headers):
				if not (key in self.db_set_of_tasks.set_of_tasks_keys):
					continue
				newItem = QtGui.QTableWidgetItem()
				try:
					newItem.setText(set_of_tasks[key])
				except:
					pass
				if key == 'task_name':
					color = self.tasks_color
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
				elif key == 'workroom':
					try:
						newItem.setText('')
					except:
						pass
								
				window.select_from_list_data_list_table.setItem(i, j, newItem)
		
		# edit widjet
		window.setWindowTitle(('Set Of Tasks: ' + name))
		window.select_from_list_cansel_button.clicked.connect(partial(self.close_window, window))
		window.select_from_list_apply_button.setVisible(False)
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()
		
	
	def insert_workroom_in_table(self, workroom, table):
		# get selected rows
		selected = table.selectedItems()
		if not selected:
			self.message('Not Selected!', 2)
			return
		
		rows = []
		for item in selected:
			if not item.row() in rows:
				rows.append(item.row())
				
		# get num column "workroom"
		num_column = table.columnCount()
		column = False
		for j in range(0, num_column):
			head_item = table.horizontalHeaderItem(j)
			if head_item.text() == 'workroom':
				column = j
				break
				
		if not column:
			self.message('Column \"workroom\' Not Found!', 2)
			return
			
		# insert workroom
		for row in rows:
			item = table.item(row, column)
			item.setText(workroom)
				
		print('insert workroom in table')
		
	def insert_task_type_in_table(self, type_, table):
		# get selected rows
		selected = table.selectedItems()
		if not selected:
			self.message('Not Selected!', 2)
			return
		
		rows = []
		for item in selected:
			if not item.row() in rows:
				rows.append(item.row())
				
		# get num column "task_type"
		num_column = table.columnCount()
		column = False
		for j in range(0, num_column):
			head_item = table.horizontalHeaderItem(j)
			if head_item.text() == 'task_type':
				column = j
				break
				
		if not column:
			self.message('Column \"task_type\' Not Found!', 2)
			return
			
		# insert task_type
		for row in rows:
			item = table.item(row, column)
			item.setText(type_)
				
		print('insert task type in table')
			
	def insert_data_in_table(self, insert_text, table, column_head):
		# get selected rows
		selected = table.selectedItems()
		if not selected:
			self.message('Not Selected!', 2)
			return
		
		rows = []
		for item in selected:
			if not item.row() in rows:
				rows.append(item.row())
				
		# get num column "task_type"
		num_column = table.columnCount()
		column = False
		for j in range(0, num_column):
			head_item = table.horizontalHeaderItem(j)
			if head_item.text() == column_head:
				column = j
				break
				
		if not column:
			self.message(('Column \"' + column_head + '\" Not Found!'), 2)
			return
			
		# insert task_type
		for row in rows:
			item = table.item(row, column)
			item.setText(insert_text)
				
		print('insert data in table')
		
	def edit_asset_type_ui(self, table):
		column = table.columnCount()
		name_column = None
		for i in range(0, column):
			head_item = table.horizontalHeaderItem(i)
			if head_item.text() == 'name':
				name_column = i
				break
		
		# get selected rows
		selected = table.selectedItems()
		lists = []
		for item in selected:
			if item.column() == name_column:
				lists.append(item.text())
				
		if lists == []:
			self.message('Not Selected Set', 2)
			return
		
		name = lists[0]
		
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.combo_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.setProjectDialog = loader.load(file, self)
		file.close()
		
		# edit widget
		#copy = db.studio()
		copy = self.db_studio
		window.setWindowTitle(('Edit Asset Type: ' + name))
		window.combo_dialog_label.setText('New Name of Set:')
		window.combo_dialog_combo_box.addItems(copy.asset_types)
		window.combo_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.combo_dialog_ok.clicked.connect(partial(self.edit_asset_type_action, name, window))
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()
		print('edit asset type')
		
	def edit_asset_type_action(self, name, window):
		#copy = db.set_of_tasks()
		self.db_set_of_tasks.edit_asset_type(name, window.combo_dialog_combo_box.currentText())
		
		self.close_window(window)
		self.reload_set_of_tasks_list()
		print('edit asset type action')
		
	
	# ******************* STUDIO EDITOR /// SERIES EDITOR ****************************
	
	def edit_ui_to_series_editor(self):
		window = self.myWidget
		table = window.studio_editor_table
		
		self.series_columns = ('name', 'status')
		
		button01 = window.studio_butt_1
		button02 = window.studio_butt_2
		button03 = window.studio_butt_3
		button04 = window.studio_butt_4
		button05 = window.studio_butt_5
		button06 = window.studio_butt_6
		button07 = window.studio_butt_7
		button08 = window.studio_butt_8
		button09 = window.studio_butt_9
		button10 = window.studio_butt_10
		
		# edit label
		window.studio_editor_label.setText('Series Editor')
				
		# edit button
		button01.setVisible(True)
		button01.setText('Reload')
		try:
			button01.clicked.disconnect()
		except:
			pass
		button01.clicked.connect(partial(self.reload_series_list, table))
		button02.setVisible(True)
		button02.setText('Create')
		try:
			button02.clicked.disconnect()
		except:
			pass
		button02.clicked.connect(self.new_series_ui)
		button03.setVisible(True)
		button03.setText('Rename')
		try:
			button03.clicked.disconnect()
		except:
			pass
		button03.clicked.connect(partial(self.rename_series_ui, table))
		button04.setVisible(False)
		button05.setVisible(False)
		button06.setVisible(False)
		button07.setVisible(False)
		button08.setVisible(False)
		button09.setVisible(False)
		button10.setVisible(False)
		
		# edit combobox
		projects = ['-- select project --'] + self.list_active_projects
		window.set_comboBox_01.setVisible(True)
		window.set_comboBox_01.clear()
		window.set_comboBox_01.addItems(projects)
		if self.current_project:
			window.set_comboBox_01.setCurrentIndex(projects.index(self.current_project))
		try:
			window.set_comboBox_01.activated[str].disconnect()
		except:
			pass
		window.set_comboBox_01.activated[str].connect(partial(self.fill_series_table, table))
		window.set_comboBox_02.setVisible(False)
		window.set_comboBox_03.setVisible(False)
		
		# edit table
		#self.myWidget.studio_editor_table_2.setVisible(False)
		self.myWidget.right_table_frame.setVisible(False)
		# -- selection mode   
		table.setSortingEnabled(True)
		table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		
		self.clear_table()
		self.reload_series_list(table)
		
	def default_state_series_table(self, table):
		# get table data
		columns = self.series_columns
		num_row = 0
		num_column = len(columns)
		headers = columns
		
		# make table
		table.setColumnCount(num_column)
		table.setRowCount(num_row)
		table.setHorizontalHeaderLabels(headers)
		
		#  edit label
		self.myWidget.studio_editor_label.setText('Series Editor')
		
		print('series table to default state')
		
	def reload_series_list(self, table):
		# get project
		if not self.current_project:
			project = self.myWidget.set_comboBox_01.currentText()
		else:
			project = self.current_project
		
		self.clear_table()
		
		if project == '-- select project --':
			self.current_project = False
			self.default_state_series_table(table)
		else:
			self.fill_series_table(table, project)
		
	def fill_series_table(self, *args):
		table = args[0]
		project = args[1]
		
		if project == '-- select project --':
			self.current_project = False
			self.default_state_series_table(table)
			return
			
		else:
			self.current_project = project
			
		# get table data
		series = []
		#copy = db.series()
		#result = copy.get_list(project)
		result = self.db_series.get_list(project)
		if result[0]:
			series = result[1]
		
		columns = self.series_columns
		num_row = len(series)
		num_column = len(columns)
		headers = columns
		
		# make table
		table.setColumnCount(num_column)
		table.setRowCount(num_row)
		table.setHorizontalHeaderLabels(headers)
    
		# fill table
		for i, data in enumerate(series):
			for j,key in enumerate(headers):
				newItem = QtGui.QTableWidgetItem()
				newItem.setText(data[key])
				if key == 'name':
					color = self.series_color
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
	
				table.setItem(i, j, newItem)
				
		#  edit label
		self.myWidget.studio_editor_label.setText(('Series Editor / \"' + project + '\"'))
		
		table.resizeRowsToContents()
		table.resizeColumnsToContents()
		
		print('fill series table', result)
		
	def new_series_ui(self):
		# get project
		project = self.myWidget.set_comboBox_01.currentText()
		if project == '-- select project --':
			self.message('Not Project!', 3)
			return
		
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.new_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.createSeriesDialog = loader.load(file, self)
		file.close()
		
		# edit widget
		window.setWindowTitle(('Create Series to \"' + project + '\"'))
		window.new_dialog_label.setText('Name of Series:')
		window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.new_dialog_ok.clicked.connect(partial(self.new_series_action, window, project))
				
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()
		
		print('new series ui')
		
	def new_series_action(self, window, project):
		#copy = db.series()
		#result = copy.create(project, window.new_dialog_name.text())
		result = self.db_series.create(project, window.new_dialog_name.text())
		
		if not result[0]:
			self.message(result[1], 2)
			return
		
		self.reload_series_list(self.myWidget.studio_editor_table)
		self.close_window(window)
		print('new series action')
		
	def rename_series_ui(self, table):
		# get project
		project = self.myWidget.set_comboBox_01.currentText()
		if project == '-- select project --':
			self.message('Not Project!', 3)
			return
			
		# get old series
		column = table.columnCount()
		name_column = None
		for i in range(0, column):
			head_item = table.horizontalHeaderItem(i)
			if head_item.text() == 'name':
				name_column = i
				break
		
		# get selected rows
		selected = table.selectedItems()
		lists = []
		for item in selected:
			if item.column() == name_column:
				lists.append(item.text())
				
		if lists == []:
			self.message('Not Selected Series', 2)
			return
		
		name = lists[0]
		
		
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.new_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.createSeriesDialog = loader.load(file, self)
		file.close()
		
		# edit widget
		window.setWindowTitle(('Rename Series: \"' + name + '\"'))
		window.new_dialog_label.setText('New Name of Series:')
		window.new_dialog_name.setText(name)
		window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.new_dialog_ok.clicked.connect(partial(self.rename_series_action, window, name))
				
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()
		print('rename series ui')
	
	def rename_series_action(self, window, name):
		# get project
		project = self.myWidget.set_comboBox_01.currentText()
		if project == '-- select project --':
			self.message('Not Project!', 3)
			return
				
		# rename
		#copy = db.series()
		#result = copy.rename(project, name, window.new_dialog_name.text())
		result = self.db_series.rename(project, name, window.new_dialog_name.text())
		
		if not result[0]:
			self.message(result[1])
			return
			
		self.reload_series_list(self.myWidget.studio_editor_table)
		self.close_window(window)		
		print('rename series action')
		
	# ******************* STUDIO EDITOR /// GROUP EDITOR ****************************
	def edit_ui_to_group_editor(self):
		window = self.myWidget
		table = window.studio_editor_table
		
		self.group_columns = ('name', 'type', 'comment', 'series')
		
		button01 = window.studio_butt_1
		button02 = window.studio_butt_2
		button03 = window.studio_butt_3
		button04 = window.studio_butt_4
		button05 = window.studio_butt_5
		button06 = window.studio_butt_6
		button07 = window.studio_butt_7
		button08 = window.studio_butt_8
		button09 = window.studio_butt_9
		button10 = window.studio_butt_10
		
		# edit label
		window.studio_editor_label.setText('Group Editor')
				
		# edit button
		button01.setVisible(True)
		button01.setText('Reload')
		try:
			button01.clicked.disconnect()
		except:
			pass
		button01.clicked.connect(partial(self.reload_group_list, table))
		button02.setVisible(True)
		button02.setText('Create')
		try:
			button02.clicked.disconnect()
		except:
			pass
		button02.clicked.connect(self.new_group_ui)
		button03.setVisible(True)
		button03.setText('Rename')
		try:
			button03.clicked.disconnect()
		except:
			pass
		button03.clicked.connect(partial(self.rename_group_ui, table))
		button04.setVisible(True)
		button04.setText('Edit Comment')
		try:
			button04.clicked.disconnect()
		except:
			pass
		button04.clicked.connect(partial(self.edit_comment_group_ui, table))
		button05.setVisible(True)
		button05.setText('Asset List')
		try:
			button05.clicked.disconnect()
		except:
			pass
		button05.clicked.connect(partial(self.pre_edit_ui_to_group_content_editor))
		button06.setVisible(False)
		button07.setVisible(False)
		button08.setVisible(False)
		button09.setVisible(False)
		button10.setVisible(False)
		
		# edit combobox
		# -- get project list
		projects = ['-- select project --'] + self.list_active_projects
		window.set_comboBox_01.setVisible(True)
		window.set_comboBox_01.clear()
		window.set_comboBox_01.addItems(projects)
		if self.current_project:
			window.set_comboBox_01.setCurrentIndex(projects.index(self.current_project))
		try:
			window.set_comboBox_01.activated[str].disconnect()
		except:
			pass
		window.set_comboBox_01.activated[str].connect(partial(self.fill_group_table, table))
		# -- get type of asset list
		window.set_comboBox_02.setVisible(True)
		window.set_comboBox_02.clear()
		window.set_comboBox_02.addItems((['-all types-'] + self.db_studio.asset_types))
		try:
			window.set_comboBox_02.activated[str].disconnect()
		except:
			pass
		window.set_comboBox_02.activated[str].connect(partial(self.fill_group_table, table, 'get_project'))
		window.set_comboBox_03.setVisible(False)
		self.myWidget.group_search_qline.setVisible(False)
		
		# edit table
		#self.myWidget.studio_editor_table_2.setVisible(False)
		self.myWidget.right_table_frame.setVisible(False)
		# -- selection mode   
		table.setSortingEnabled(True)
		table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		
		self.clear_table()
		if not self.current_project:
			self.default_state_group_table(table)
		else:
			self.fill_group_table(table, self.current_project)
		
	def default_state_group_table(self, table):
		# get table data
		columns = self.group_columns
		num_row = 0
		num_column = len(columns)
		headers = columns
		
		# make table
		table.setColumnCount(num_column)
		table.setRowCount(num_row)
		table.setHorizontalHeaderLabels(headers)
		
		# edit label
		self.myWidget.studio_editor_label.setText('Group Editor')
		#self.myWidget.set_comboBox_02.setVisible(False)
		print('default state group table')
		
	def fill_group_table(self, *args):
		# ge filter    window.set_comboBox_02.addItems((['-all types-']
		f = self.myWidget.set_comboBox_02.currentText()
		if f == '-all types-':
			f = False
		
		table = args[0]
		project = args[1]
		
		if project == 'get_project':
			if not self.current_project:
				self.message('Not Current project!', 2)
				return
			else:
				project = self.current_project
		elif project == '-- select project --':
			self.current_project = False
			self.default_state_group_table(table)
			return
		else:
			self.current_project = project
			
		# get table data
		groups = []
		copy = self.db_group
		result = copy.get_list(project)
		'''
		if result[0]:
			groups = result[1]
		'''
		if result[0]:
			if f:
				for group in result[1]:
					if group['type'] == f:
						groups.append(group)
			else:
				groups = result[1]
		
		columns = self.group_columns
		num_row = len(groups)
		num_column = len(columns)
		headers = columns
		
		# make table
		table.setColumnCount(num_column)
		table.setRowCount(num_row)
		table.setHorizontalHeaderLabels(headers)
    
		# fill table
		for i, data in enumerate(groups):
			for j,key in enumerate(headers):
				newItem = QtGui.QTableWidgetItem()
				newItem.setText(data[key])
				if key == 'name':
					color = self.group_color
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
				elif key == 'series':
					#copy = db.series()
					#data_ = copy.get_by_id(project, data[key])
					data_ = self.db_series.get_by_id(project, data[key])
					if data_[0]:
						newItem.setText(data_[1]['name'])
					else:
						print(data_[1])
				newItem.group = data
				table.setItem(i, j, newItem)
				
		# disconnect table
		try:
			self.myWidget.studio_editor_table.itemDoubleClicked.disconnect()
		except:
			pass
		# connect table
		#self.myWidget.studio_editor_table.itemClicked.connect(self.set_context_group)
		self.myWidget.studio_editor_table.itemDoubleClicked.connect(self.edit_ui_to_group_content_editor)
				
		#  edit label
		self.myWidget.studio_editor_label.setText(('Group Editor / \"' + project + '\"'))
		
		table.resizeRowsToContents()
		table.resizeColumnsToContents()
		
		print('fill group table')
		
	def set_context_group(self, item):
		self.current_group = item.group
		
	def reload_group_list(self, table):
		self.clear_table()
		project = self.myWidget.set_comboBox_01.currentText()
		self.fill_group_table(table, project)
		#print('reload group list')
		
	def new_group_ui(self):
		# get project
		project = self.myWidget.set_comboBox_01.currentText()
		if project == '-- select project --':
			self.message('Not Project!', 3)
			return
		
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.new_dialog_4_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.createGroupDialog = loader.load(file, self)
		file.close()
		
		# edit widget
		window.setWindowTitle(('Create Group to \"' + project + '\"'))
		window.new_dialog_label.setText('Name of Group:')
		window.new_dialog_comment_label.setText('Comment:')
		window.new_dialog_label_2.setText('Type:')
		window.new_dialog_label_3.setText('Series:')
		window.new_dialog_frame_3.setVisible(False)
		window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.new_dialog_ok.clicked.connect(partial(self.new_group_action, window, project))
		
		# edit comobox
		#copy = db.studio()
		copy = self.db_studio
		types = ['-- select type --'] + copy.asset_types
		window.new_dialog_combo_box_2.addItems(types)
		window.new_dialog_combo_box_2.activated[str].connect(partial(self.new_group_ui_series_activation, window, project))
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()
		print('new group ui')
		
	def new_group_ui_series_activation(self, *args):
		window = args[0]
		project = args[1]
		type_ = args[2]
		
		self.series_current_data = {}
		
		#copy = db.series()
		
		#if type_ in copy.asset_types_with_series:
		if type_ in self.db_series.asset_types_with_series:
			window.new_dialog_frame_3.setVisible(True)
			
			series = ['-- select series --']
			#result = copy.get_list(project)
			result = self.db_series.get_list(project)
			if result[0]:
				for data in result[1]:
					series.append(data['name'])
					self.series_current_data[data['name']] = data['id']
				print(self.series_current_data)
			else:
				print(result)
			window.new_dialog_combo_box_3.clear()
			window.new_dialog_combo_box_3.addItems(series)
			
		else:
			window.new_dialog_frame_3.setVisible(False)
		
		print('series activation')
		
	def new_group_action(self, window, project):
		# get name, comment
		name = 	window.new_dialog_name.text()
		comment = window.new_dialog_comment.text()
		
		if name == '':
			self.message('Not Name!', 3)
			return
			
		# get type
		type_ = window.new_dialog_combo_box_2.currentText()
		
		# get series
		#copy = db.group()
		
		series = ''
		#if type_ in copy.asset_types_with_series:
		if type_ in self.db_group.asset_types_with_series:
			series_name = window.new_dialog_combo_box_3.currentText()
			if series_name == '-- select series --':
				self.message('Not Series', 3)
				return
					
		# create group
		# -- get series id
		series_id = ''
		try:
			series_id = self.series_current_data[series_name]
		except:
			pass
		
		keys = {
		'name': name,
		'type': type_,
		'comment': comment,
		'series': series_id,
		}
		
		#result = copy.create(project, keys)
		result = self.db_group.create(project, keys)
		
		self.fill_group_table(self.myWidget.studio_editor_table, project)
		self.close_window(window)
		print('new group action')
		
	def rename_group_ui(self, table):
		# get project
		project = self.myWidget.set_comboBox_01.currentText()
		if project == '-- select project --':
			self.message('Not Project!', 3)
			return
		
		name = table.selectedItems()[0].group['name']
		group_id = table.selectedItems()[0].group['id']
		
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.new_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.createSeriesDialog = loader.load(file, self)
		file.close()
		
		# edit widget
		window.setWindowTitle(('Rename Group: \"' + name + '\"'))
		window.new_dialog_label.setText('New Name of Group:')
		window.new_dialog_name.setText(name)
		window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.new_dialog_ok.clicked.connect(partial(self.rename_group_action, window, group_id, project))
				
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()
		
		print('rename group ui')
		
	def rename_group_action(self, window, group_id, project):
		# get name
		new_name = window.new_dialog_name.text()
				
		if new_name == '':
			self.message('Not Name!', 3)
			return
			
		result = self.db_group.rename(project, group_id, new_name)
		if not result[0]:
			self.message('Could not rename the group, see details in the console', 2)
			print('*'*25, result[1])
			return
		
		self.close_window(window)
		self.fill_group_table(self.myWidget.studio_editor_table, project)
		print('rename group action')
		
	def edit_comment_group_ui(self, table):
		# get project
		project = self.myWidget.set_comboBox_01.currentText()
		if project == '-- select project --':
			self.message('Not Project!', 3)
			return
			
		# get old series
		column = table.columnCount()
		columns = {}
		for i in range(0, column):
			head_item = table.horizontalHeaderItem(i)
			if head_item.text() == 'comment':
				columns['comment_column'] = i
			elif head_item.text() == 'name':
				columns['name_column'] = i
				
		
		# -- name and comment
		selected = table.selectedItems()
		name = None
		comment = None
		for item in selected:
			if item.column() == columns['name_column']:
				name = item.text()
			elif item.column() == columns['comment_column']:
				comment = item.text()
				
		if not name:
			self.message('Not Selected Series', 2)
			return
		
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.new_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.createSeriesDialog = loader.load(file, self)
		file.close()
		
		# edit widget
		window.setWindowTitle(('Edit Comment Group: \"' + name + '\"'))
		window.new_dialog_label.setText('New Comment:')
		if comment:
			window.new_dialog_name.setText(comment)
		window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.new_dialog_ok.clicked.connect(partial(self.edit_comment_group_action, window, name, project))
				
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()		
		
		print('edit comment group ui')
		
	def edit_comment_group_action(self, window, name, project):
		# get comment
		comment = window.new_dialog_name.text()
		
		# edit comment
		#copy = db.group()
		#result = copy.edit_comment_by_name(project, name, comment)
		result = self.db_group.edit_comment_by_name(project, name, comment)
		if not result[0]:
			self.message(result[1], 2)
			return
		
		self.close_window(window)
		self.fill_group_table(self.myWidget.studio_editor_table, project)
		print('edit comment group action')
		
	# ******************* ASSET EDITOR
	
	def pre_edit_ui_to_group_content_editor(self, *args):
		item = self.myWidget.studio_editor_table.currentItem()
		self.edit_ui_to_group_content_editor(item)
		
	def edit_ui_to_group_content_editor(self, *args):
		self.current_group = args[0].group
		
		window = self.myWidget
		table = window.studio_editor_table
		
		# get project
		self.current_project = window.set_comboBox_01.currentText()
		self.asset_columns = ('icon', 'name', 'comment', 'priority', 'type')
		
		button01 = window.studio_butt_1
		button02 = window.studio_butt_2
		button03 = window.studio_butt_3
		button04 = window.studio_butt_4
		button05 = window.studio_butt_5
		button06 = window.studio_butt_6
		button07 = window.studio_butt_7
		button08 = window.studio_butt_8
		button09 = window.studio_butt_9
		button10 = window.studio_butt_10
		
		# edit label
		label_trext = '\"%s\" / \"%s\" / Assets' % (self.current_project, self.current_group['name'])
		window.studio_editor_label.setText(label_trext)
				
		# edit button
		button01.setVisible(True)
		button01.setText('Reload')
		try:
			button01.clicked.disconnect()
		except:
			pass
		button01.clicked.connect(partial(self.reload_asset_list, table))
		button02.setVisible(False)
		'''
		button02.setVisible(True)
		button02.setText('Rename')
		try:
			button02.clicked.disconnect()
		except:
			pass
		button02.clicked.connect(partial(self.rename_asset_ui, table))
		'''
		button03.setVisible(True)
		button03.setText('Change Group')
		try:
			button03.clicked.disconnect()
		except:
			pass
		button03.clicked.connect(partial(self.change_asset_group_ui, table))
		button04.setVisible(True)
		button04.setText('Edit Priority')
		try:
			button04.clicked.disconnect()
		except:
			pass
		button04.clicked.connect(partial(self.edit_asset_priority_ui, table))
		button05.setVisible(True)
		button05.setText('Back')
		try:
			button05.clicked.disconnect()
		except:
			pass
		button05.clicked.connect(partial(self.edit_ui_to_group_editor))
		button06.setVisible(True)
		button06.setText('Add Assets')
		try:
			button06.clicked.disconnect()
		except:
			pass
		button06.clicked.connect(partial(self.add_assets_to_group_ui))
		button07.setVisible(True)
		button07.setText('Copy Asset')
		try:
			button07.clicked.disconnect()
		except:
			pass
		button07.clicked.connect(partial(self.copy_asset_ui))
		# 8
		button08.setVisible(True)
		button08.setText('Remove Asset')
		try:
			button08.clicked.disconnect()
		except:
			pass
		button08.clicked.connect(partial(self.remove_asset_action, table))
		# 9
		button09.setVisible(True)
		button09.setText('To Task Manager >>>')
		try:
			button09.clicked.disconnect()
		except:
			pass
		button09.clicked.connect(partial(self.asset_to_task_manager, 'from_asset_editor'))
		button10.setVisible(False)
		
		# -- get group list
		groups = []
		rows = self.db_group.get_list(self.current_project)
		if rows[0]:
			for row in rows[1]:
				groups.append(row['name'])
		else:
			print(rows[1])
		
		# edit combobox
		#groups = ['-- select group --'] + groups
		index = groups.index(self.current_group['name'])
		print('index: ', index)
		window.set_comboBox_01.setVisible(True)
		window.set_comboBox_01.clear()
		window.set_comboBox_01.addItems(groups)
		window.set_comboBox_01.setCurrentIndex(index)
		try:
			window.set_comboBox_01.activated[str].disconnect()
		except:
			pass
		window.set_comboBox_01.activated[str].connect(partial(self.fill_group_content_list, window, table))
		window.set_comboBox_02.setVisible(False)
		window.set_comboBox_03.setVisible(False)
		# unhide search lineEdit 
		self.myWidget.group_search_qline.setVisible(True)
		
		# edit table
		#self.myWidget.studio_editor_table_2.setVisible(False)
		self.myWidget.right_table_frame.setVisible(False)
		# -- selection mode   
		table.setSortingEnabled(True)
		table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		
		self.clear_table()
		self.fill_group_content_list(window, table, self.current_group['name'])
		
		print('edit ui to group content editor')
		
	def reload_group_content_list(self):
		self.fill_group_content_list(self.myWidget, self.myWidget.studio_editor_table, self.current_group['name'])
		
	def fill_group_content_list(self, *args):
		window = args[0]
		table = args[1]
		group = args[2]
		
		# get self.current_group 
		copy = self.db_group
		result = copy.get_by_name(self.current_project, group)
		if not result[0]:
			self.message(result[1], 3)
			return
		else:
			self.current_group = result[1]
			
		if self.current_group['type'] == 'all':
			self.myWidget.studio_butt_4.setVisible(False)
			self.myWidget.studio_butt_6.setVisible(False)
			self.myWidget.studio_butt_7.setVisible(False)
			self.myWidget.studio_butt_8.setVisible(False)
			self.myWidget.studio_butt_9.setVisible(False)
		else:
			self.myWidget.studio_butt_4.setVisible(True)
			self.myWidget.studio_butt_6.setVisible(True)
			self.myWidget.studio_butt_7.setVisible(True)
			self.myWidget.studio_butt_8.setVisible(True)
			self.myWidget.studio_butt_9.setVisible(True)
		
		# edit label
		window.studio_editor_label.setText(('\"' + self.current_project + '\" / \"' + group + '\" / Assets'))
		
		# get table data
		f = self.myWidget.group_search_qline.text()
		copy = self.db_asset
		assets_list = copy.get_list_by_group(self.current_project, self.current_group['id'])
		if assets_list[0]:
			if f:
				assets_list_filter = []
				for asset in assets_list[1]:
					if f.lower() in asset['name'].lower():
						assets_list_filter.append(asset)
				assets_list = assets_list_filter
			else:
				assets_list = assets_list[1]
				
		headers = self.asset_columns
		num_row = len(assets_list)
		num_column = len(headers)
		
		# make table
		table.setColumnCount(num_column)
		table.setRowCount(num_row)
		table.setHorizontalHeaderLabels(headers)
    
		# fill table
		for i, row in enumerate(assets_list):
			for j,key in enumerate(headers):
				newItem = QtGui.QTableWidgetItem()
				if key in row.keys():
					newItem.setText(row[key])
				if key == 'name':
					color = self.asset_color
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
				elif key == 'priority':
					newItem.setText(copy.priority[int(row[key])])
				elif key == 'icon':
					# get img path
					icon_path = os.path.join(self.db_asset.preview_img_path, (row['name'] + '_icon.png'))
					# label
					label = QtGui.QLabel()
					
					if os.path.exists(icon_path):
						# img
						image = QtGui.QImage(icon_path)
						pix = QtGui.QPixmap(image)
																
						label.setPixmap(pix)
						label.show()
					else:
						label.setText('no image')
					
					label.asset = dict(row)
					table.setCellWidget(i, j, label)
				
				if key != 'icon':
					newItem.asset = dict(row)
					table.setItem(i, j, newItem)
					
		table.resizeRowsToContents()
		table.resizeColumnsToContents()
			
		print('fill group content list', self.current_group)
		
	def reload_asset_list(self, table):
		# reload assets list
		self.fill_group_content_list(self.myWidget, table, self.current_group['name'])
		
	def asset_to_task_manager(self, action):
		print(action)
		if action == 'from_asset_editor':
			asset_data = None
			try:
				asset_data = self.myWidget.studio_editor_table.currentItem().asset
			except:
				self.message('Asset is not selected!', 2)
				return
				
			# -- group dict
			result = self.db_group.get_groups_dict_by_id(self.current_project)
			if not result[0]:
				self.message(result[1], 3)
				return
			group_dict = result[1]
				
			# load task manager
			# -- open tab
			self.myWidget.main_tabWidget.setCurrentIndex(1)
			# -- fill current project
			for i in range(0, self.myWidget.task_manager_comboBox_1.model().rowCount()):
				if self.myWidget.task_manager_comboBox_1.itemText(i) == self.current_project:
					self.myWidget.task_manager_comboBox_1.setCurrentIndex(i)
					#self.tm_reload_task_list()
					break
			
			#self.myWidget.global_search_qline.setText(asset_data['name'])
			#self.tm_fill_series_groups(self.current_project)
			
			self.tm_reload_task_list_by_global_search_action(None, group_dict, self.myWidget.studio_editor_table.currentItem())
		
		elif action == 'from_content_editor':
			print(self.action_to_tm)
			if self.action_to_tm == 'from_content':
				task_data = None
				item = None
				
				# get asset_data
				try:
					item = self.myWidget.studio_editor_table_2.currentItem()
					task_data = item.task
				except:
					self.message('Task is not selected!', 2)
					return
					
				if not task_data:
					self.message('Task is not selected!', 2)
					return
					
				asset_data = self.myWidget.studio_editor_table_2.assets_by_name[task_data['asset']]
				item.asset = asset_data
					
				# -- group dict
				result = self.db_group.get_groups_dict_by_id(self.current_project)
				if not result[0]:
					self.message(result[1], 3)
					return
				group_dict = result[1]
				
				# load task manager
				# -- open tab
				self.myWidget.main_tabWidget.setCurrentIndex(1)
				# -- fill current project
				for i in range(0, self.myWidget.task_manager_comboBox_1.model().rowCount()):
					if self.myWidget.task_manager_comboBox_1.itemText(i) == self.current_project:
						self.myWidget.task_manager_comboBox_1.setCurrentIndex(i)
						#self.tm_reload_task_list()
						break
					
				self.tm_reload_task_list_by_global_search_action(None, group_dict, item)
		
			elif self.action_to_tm == 'from_service':
				task_data = None
				item = None
				
				# get asset_data
				try:
					item = self.myWidget.studio_editor_table.currentItem()
					task_data = item.task
				except:
					self.message('Task is not selected!', 2)
					return
					
				if not task_data:
					self.message('Task is not selected!', 2)
					return
					
				asset_data = self.myWidget.studio_editor_table_2.assets_by_name[task_data['asset']]
				item.asset = asset_data
					
				# -- group dict
				result = self.db_group.get_groups_dict_by_id(self.current_project)
				if not result[0]:
					self.message(result[1], 3)
					return
				group_dict = result[1]
				
				# load task manager
				# -- open tab
				self.myWidget.main_tabWidget.setCurrentIndex(1)
				# -- fill current project
				for i in range(0, self.myWidget.task_manager_comboBox_1.model().rowCount()):
					if self.myWidget.task_manager_comboBox_1.itemText(i) == self.current_project:
						self.myWidget.task_manager_comboBox_1.setCurrentIndex(i)
						#self.tm_reload_task_list()
						break
					
				self.tm_reload_task_list_by_global_search_action(None, group_dict, item)
				
	'''
	def rename_asset_ui(self, table):
		column = table.columnCount()
		name_column = None
		for i in range(0, column):
			head_item = table.horizontalHeaderItem(i)
			if head_item.text() == 'name':
				name_column = i
				break
		
		# get selected rows
		selected = table.selectedItems()
		lists = []
		for item in selected:
			if item.column() == name_column:
				lists.append(item.text())
				
		if lists == []:
			self.message('Not Selected Group', 2)
			return
		
		asset_name = lists[0]
		
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.new_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.setProjectDialog = loader.load(file, self)
		file.close()
		
		# edit widget
		window.setWindowTitle(('Rename Asset: \"' + asset_name + '\"'))
		window.new_dialog_label.setText('New Name:')
		if asset_name:
			window.new_dialog_name.setText(asset_name)
		window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.new_dialog_ok.clicked.connect(partial(self.rename_asset_action, window, asset_name))
				
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()
		print('rename aset ui')
		
	def rename_asset_action(self, window, asset_name):
		# get new name
		new_name = window.new_dialog_name.text()
		
		copy = db.asset()
		result = copy.rename_asset(self.current_project, self.current_group['type'], asset_name, new_name)
		if not result[0]:
			self.message(result[1], 2)
			return
		
		# reload assets list
		self.fill_group_content_list(self.myWidget, self.myWidget.studio_editor_table, self.current_group['name'])
		
		self.close_window(window)
		print('rename asset action', result)
	'''
		
	def change_asset_group_ui(self, table):
		column = table.columnCount()
		name_column = None
		for i in range(0, column):
			head_item = table.horizontalHeaderItem(i)
			if head_item.text() == 'name':
				name_column = i
				break
		'''
		# get selected rows
		selected = table.selectedItems()
		lists = []
		for item in selected:
			if item.column() == name_column:
				lists.append(item.text())
				
		if lists == []:
			self.message('Not Selected Group', 2)
			return
		asset_name = lists[0]
		'''
		# get asset data
		asset_data = table.currentItem().asset
		asset_name = asset_data['name']
		
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.combo_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.setProjectDialog = loader.load(file, self)
		file.close()
		
		# edit widget
		#copy = db.group()
		group_list = ['-- new groups --']
		#result = copy.get_by_type_list(self.current_project, [self.current_group['type']])
		#result = copy.get_by_type_list(self.current_project, [asset_data['type']])
		result = self.db_group.get_by_type_list(self.current_project, [asset_data['type']])
		if result[0]:
			for row in result[1]:
				if row['name'] != self.current_group['name']:
					group_list.append(row['name'])
					
			window.groups = result[1]
		else:
			print(result[1])
		
		window.setWindowTitle(('Change Group Asset: \"' + asset_name + '\"'))
		window.combo_dialog_label.setText('Select New Group:')
		window.combo_dialog_combo_box.addItems(group_list)
		window.combo_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.combo_dialog_ok.clicked.connect(partial(self.change_asset_group_action, asset_data, window))
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()
		
		print('change asset group')
		
	def change_asset_group_action(self, asset_data, window):
		# get new group name asset_name
		group_name = window.combo_dialog_combo_box.currentText()
		group_id = None
		if group_name == '-- new groups --':
			self.message('The Group is not Selected!', 2)
			return
		else:
			for row in window.groups:
				if row['name'] == group_name:
					group_id = row['id']
		
		# change group
		#print(window.groups, group_name, group_id)
		
		copy = self.db_asset
		result = copy.change_group_of_asset(self.current_project, asset_data['type'], asset_data['name'], group_id)
		if not result[0]:
			self.message(result[1], 2)
			return
		
		# reload assets list
		self.fill_group_content_list(self.myWidget, self.myWidget.studio_editor_table, self.current_group['name'])
		
		self.close_window(window)
		#print('change asset group action', result[1])
		
	def remove_asset_action(self, table):
		asset_data = table.currentItem().asset
		ask = self.message(('Are you sure you want to delete Asset \"' + asset_data['name'] + '\"?'), 0)
		if not ask:
			return
		
		result = self.db_chat.remove_asset(self.current_project, asset_data)
		if not result[0]:
			self.message(str(result[1]), 2)
		
		# reload assets list
		self.fill_group_content_list(self.myWidget, self.myWidget.studio_editor_table, self.current_group['name'])
		
	def edit_asset_priority_ui(self, table):
		print('edit asset priority')
		
	def add_assets_to_group_ui(self):
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.select_from_list_dialog_3button_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.addAssetsDialog = loader.load(file, self)
		file.close()
		
		add_asset_columns = ['asset_name','set_of_tasks']
		
		# -- get table data
		num_row = 100
		num_column = len(add_asset_columns)
		headers = add_asset_columns
		    
		# -- make table
		table = window.select_from_list_data_list_table
		table.setColumnCount(num_column)
		table.setRowCount(num_row)
		table.setHorizontalHeaderLabels(headers)
		
		# -- edit table
		#table.setDragEnabled(True)
		#table.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
		
		# -- Fill table
		data = []
		#copy = db.list_of_assets()
		#get_ = copy.get(self.current_project, self.current_group['name'])
		get_ = self.db_list_of_assets.get(self.current_project, self.current_group['name'])
		if get_[0]:
			data = get_[1]
		
		for i in range(0, num_row):
			for j in range(0, num_column):
				newItem = QtGui.QTableWidgetItem()
				if i>=len(data):
					table.setItem(i, j, newItem)
					continue
				if table.horizontalHeaderItem(j).text() == 'asset_name':
					newItem.setText(data[i]['asset_name'])
					color = self.asset_color
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
				elif table.horizontalHeaderItem(j).text() == 'set_of_tasks':
					newItem.setText(data[i]['set_of_tasks'])
				table.setItem(i, j, newItem)
		
		# -- add context menu
		# -- add menu
		#copy = db.set_of_tasks()
		set_of_tasks_list = self.db_set_of_tasks.get_list()
		#print(set_of_tasks_list)
		
		if set_of_tasks_list[0]:
			set_list = []
			for key_ in set_of_tasks_list[1]:
				if set_of_tasks_list[1][key_]['asset_type'] == self.current_group['type']:
					set_list.append(key_)
			table.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
			# workroom menu
			addgrup_action = QtGui.QAction( '-- sets of tasks -- ', window)
			table.addAction( addgrup_action )
			for key in set_list:
				addgrup_action = QtGui.QAction( key, window)
				#addgrup_action.setToolTip( 'to WorkRoom column' )
				addgrup_action.triggered.connect(partial(self.insert_asset_list_in_table, key, table))
				table.addAction( addgrup_action )
		
		
		# edit widget
		window.setWindowTitle(('add New Assets to: ' + self.current_group['name']))
		window.select_from_list_cansel_button.clicked.connect(partial(self.close_window, window))
		window.pushButton_01.setText('Save List')
		window.pushButton_01.clicked.connect(partial(self.save_aseets_list, table, window))
		window.pushButton_02.setText('Create Assets')
		window.pushButton_02.clicked.connect(partial(self.create_assets_from_list, table, window))
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()
		
		print('add asset to group ui')
		
	def copy_asset_ui(self):
		try:
			asset_data = self.myWidget.studio_editor_table.currentItem().asset
		except:
			self.message('Asset is not selected!', 2)
			return
		if not asset_data['type'] in self.db_chat.copied_asset:
			self.message('This type can not be copied!', 2)
			return
			
		# -- GROUP LIST
		# -- get All Group Dict
		result = self.db_group.get_dict_by_all_types(self.current_project)
		if not result[0]:
			self.message(result[1], 2)
			return
		group_dict_by_all_types = result[1]
		
		if not asset_data['type'] in group_dict_by_all_types:
			self.message('No Found Group with This Type!', 2)
			return
		
		group_list = []
		group_id_list = []
		for group in group_dict_by_all_types[asset_data['type']]:
			group_list.append(group['name'])
			group_id_list.append(group['id'])
		'''	
		result = self.db_group.get_by_type_list(self.current_project, [asset_data['type']])
		if not result[0]:
			self.message(result[1], 2)
			return
		
		group_list = []
		group_id_list = []
		for group in result[1]:
			group_list.append(group['name'])
			group_id_list.append(group['id'])
		'''	
		
		# -- SET OF TASKS LIST
		set_of_tasks_list = {}
		#set_of_tasks_list = []
		#set_of_tasks_data = {}
		
		result = self.db_set_of_tasks.get_dict_by_all_types()
		if not result[0]:
			self.message(result[1], 2)
			return
		
		for asset_type in result[1]:
			set_of_tasks_list[asset_type] = result[1][asset_type].keys()
		'''
		if asset_data['type'] in self.db_chat.copied_with_task:
			for asset_type in self.db_chat.copied_asset[asset_data['type']]:
				result = self.db_set_of_tasks.get_list_by_type(asset_type)
				if not result[0]:
					self.message(result[1], 2)
					return
				#set_of_tasks_data = result[1]
				#set_of_tasks_list  = result[1].keys()
				set_of_tasks_list[asset_type] = result[1].keys()
		'''
		
		# window  self.new_dialog_3_path
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.new_dialog_4_2_path)
		#file = QtCore.QFile(self.new_dialog_3_path)
		file.open(QtCore.QFile.ReadOnly)
		window = self.addAssetsDialog = loader.load(file, self)
		file.close()
		
		# edit window
		window.setWindowTitle(('Copy of Asset: /// ' + asset_data['name']))
		window.new_dialog_label.setText('New Name of Asset:')
		window.new_dialog_label_0.setText('New Type:')
		window.new_dialog_label_2.setText('Group:')
		window.new_dialog_label_3.setText('Set Of Task:')
		if not asset_data['type'] in self.db_chat.copied_with_task:
			window.new_dialog_frame_3.setVisible(False)
		
		# -- type list
		if asset_data['type'] in self.db_chat.copied_asset:
			window.new_dialog_combo_box_0.addItems(self.db_chat.copied_asset[asset_data['type']])
		else:
			window.new_dialog_combo_box_0.addItems([asset_data['type']])
		# -- group list
		window.new_dialog_combo_box_2.addItems(group_list)
		window.new_dialog_combo_box_2.setCurrentIndex(group_id_list.index(asset_data['group']))
		# -- set_of_task list
		if asset_data['type'] in self.db_chat.copied_with_task:
			window.new_dialog_combo_box_3.addItems(set_of_tasks_list[asset_data['type']])
		else:
			window.new_dialog_combo_box_3.addItems([''])
		
		# -- meta data
		window.asset = asset_data
		window.groups = group_dict_by_all_types
		window.set_of_tasks_list = set_of_tasks_list
		
		# -- connect button
		window.new_dialog_combo_box_0.activated[str].connect(partial(self.edit_copy_asset_ui, window))
		window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.new_dialog_ok.clicked.connect(partial(self.copy_asset_action, window))
		
		window.show()
		
	def edit_copy_asset_ui(self, window, asset_type):
		asset_data = window.asset
		
		# edit group list
		group_list = []
		group_id_list = []
		for group in window.groups[asset_type]:
			group_list.append(group['name'])
			group_id_list.append(group['id'])
		
		window.new_dialog_combo_box_2.clear()
		window.new_dialog_combo_box_2.addItems(group_list)
		if asset_data['group'] in group_id_list:
			window.new_dialog_combo_box_2.setCurrentIndex(group_id_list.index(asset_data['group']))
		
		# edit set_of_tasks list
		print(window.set_of_tasks_list)
		window.new_dialog_combo_box_3.clear()
		if asset_type in self.db_chat.copied_with_task:
			window.new_dialog_combo_box_3.addItems(window.set_of_tasks_list[asset_type])
		else:
			window.new_dialog_combo_box_3.addItems([''])
		
		
	def copy_asset_action(self, window):
		new_asset_name = window.new_dialog_name.text()
		new_group_name = window.new_dialog_combo_box_2.currentText()
		set_of_tasks = window.new_dialog_combo_box_3.currentText()
		new_asset_type = window.new_dialog_combo_box_0.currentText()
		
		result = self.db_chat.copy_of_asset(self.current_project, new_group_name, new_asset_name, new_asset_type, set_of_tasks, window.asset)
		if not result[0]:
			self.message(result[1], 3)
			return
			
		# reload assets list
		self.myWidget.group_search_qline.setText(new_asset_name)
		
		for i in range(0, self.myWidget.set_comboBox_01.model().rowCount()):
			if self.myWidget.set_comboBox_01.itemText(i) == new_group_name:
				self.myWidget.set_comboBox_01.setCurrentIndex(i)
				#self.tm_reload_task_list()
				break
		
		self.fill_group_content_list(self.myWidget, self.myWidget.studio_editor_table, new_group_name)
		
		self.close_window(window)
		
	def insert_asset_list_in_table(self, key, table):
		# get selected rows
		selected = table.selectedItems()
		if not selected:
			self.message('Not Selected!', 2)
			return
		
		rows = []
		for item in selected:
			if not item.row() in rows:
				rows.append(item.row())
				
		# get num column "set_of_tasks"
		num_column = table.columnCount()
		column = False
		for j in range(0, num_column):
			head_item = table.horizontalHeaderItem(j)
			if head_item.text() == 'set_of_tasks':
				column = j
				break
				
		if not column:
			self.message('Column \"set_of_tasks\' Not Found!', 2)
			return
			
		# insert set_of_tasks
		for row in rows:
			item = table.item(row, column)
			item.setText(key)
		print('inser set in table')
		
	def save_aseets_list(self, table, window):
		num_row = table.rowCount()
		num_column = table.columnCount()
		
		rows = []
		names = {}
		for i in range(0, num_row):
			row = {}
			for j in range(0, num_column):
				if table.horizontalHeaderItem(j).text() == 'asset_name':
					row['asset_name'] = table.item(i, j).text()
				elif table.horizontalHeaderItem(j).text() == 'set_of_tasks':
					row['set_of_tasks'] = table.item(i, j).text()
				row['asset_type'] = self.current_group['type']
				
			if row['asset_name'] and not row['asset_name'] in names:
				rows.append(row)
				names[row['asset_name']] = i
			elif row['asset_name'] in names:
				self.message(('match names - lines: ' + str(names[row['asset_name']] + 1) + ', ' + str(i + 1)), 2)
				return
				
		result = self.db_list_of_assets.save_list(self.current_project, self.current_group['name'], rows)
		if not result[0]:
			self.message(result[1], 2)
			return
		
		self.close_window(window)
		self.add_assets_to_group_ui()
		print('save assets list')
		
	def create_assets_from_list(self, table, window):
		num_row = table.rowCount()
		num_column = table.columnCount()
		
		rows = []
		names = {}
		for i in range(0, num_row):
			row = {}
			for j in range(0, num_column):
				if table.horizontalHeaderItem(j).text() == 'asset_name':
					row['name'] = table.item(i, j).text()
				elif table.horizontalHeaderItem(j).text() == 'set_of_tasks':
					row['set_of_tasks'] = table.item(i, j).text()
					
				row['asset_type'] = self.current_group['type']
				row['path'] = ''
				row['group'] = self.current_group['id']
				row['series'] = self.current_group['series']
				row['priority'] = '0'
				
			if row['name'] and not row['set_of_tasks']:
				self.message(('Unknown Set Of Tasks in Line ' + str(i + 1)), 2)
				return
				
			if row['name'] and not row['name'] in names:
				rows.append(row)
				names[row['name']] = i
			elif row['name'] in names:
				self.message(('match names - lines: ' + str(names[row['name']] + 1) + ', ' + str(i + 1)), 2)
				return
		
		# create assets
		#copy = self.db_asset
		create_result = self.db_asset.create(self.current_project, self.current_group['type'], rows)
		if not create_result[0]:
			self.message(create_result[1], 2) 
			return
		
		# remove asset list
		#copy = self.db_list_of_assets
		result = self.db_list_of_assets.remove(self.current_project, self.current_group['name'])
		if not result[0]:
			print(result[1])
		
		self.close_window(window)
		self.reload_asset_list(self.myWidget.studio_editor_table)
		print('create assets from list')
		
	# ******************* STUDIO EDITOR /// LOCATION EDITOR ****************************
	def edit_ui_to_location_editor(self, type_editor):
		window = self.myWidget
		table = window.studio_editor_table
		self.action_to_tm = None
		
		# service Fields
		if type_editor == 'location':
			label_text = 'Content of Locations'
			self.load_group_type = 'location'
			self.load_asset_types = ['char', 'obj']
		elif type_editor == 'animation':
			label_text = 'Content of Anim Shots'
			self.load_group_type = 'shot_animation'
			self.load_asset_types = ['char', 'obj', 'location']
		elif type_editor == 'render':
			label_text = 'Content of Render Shots'
			self.load_group_type = 'shot_render'
			self.load_asset_types = ['camera', 'light', 'shot_animation']
		
		self.type_editor = type_editor
		self.location_columns = ('name', 'type', 'comment', 'series')
		
		button01 = window.studio_butt_1
		button02 = window.studio_butt_2
		button03 = window.studio_butt_3
		button04 = window.studio_butt_4
		button05 = window.studio_butt_5
		button06 = window.studio_butt_6
		button07 = window.studio_butt_7
		button08 = window.studio_butt_8
		button09 = window.studio_butt_9
		button10 = window.studio_butt_10
		
		# edit label
		window.studio_editor_label.setText(label_text)
				
		# edit button
		button01.setVisible(True)
		button01.setText('Reload')
		try:
			button01.clicked.disconnect()
		except:
			pass
		#button01.clicked.connect(partial(self.reload_group_list, table))
		button02.setVisible(True)
		button02.setText('Add Service Task')
		try:
			button02.clicked.disconnect()
		except:
			pass
		#button02.clicked.connect(self.new_group_ui)
		button03.setVisible(False)
		button03.setText('Add Asset')
		try:
			button03.clicked.disconnect()
		except:
			pass
		button03.clicked.connect(partial(self.loc_add_asset_to_input_ui))
		button04.setVisible(False)
		button04.setText('Add Task')
		try:
			button04.clicked.disconnect()
		except:
			pass
		button04.clicked.connect(partial(self.loc_add_this_asset_task_to_input_ui))
		button05.setVisible(False)
		button05.setText('Remove Task')
		try:
			button05.clicked.disconnect()
		except:
			pass
		button05.clicked.connect(partial(self.loc_remove_task_from_input_action, table))
		button06.setVisible(False)
		'''
		button06.setText('Change Task')
		try:
			button06.clicked.disconnect()
		except:
			pass
		button06.clicked.connect(self.loc_change_input_task)
		'''
		button07.setVisible(False)
		button07.setText('To Task Manager >>>')
		try:
			button07.clicked.disconnect()
		except:
			pass
		button07.clicked.connect(partial(self.asset_to_task_manager, 'from_content_editor'))
		button08.setVisible(False)
		button09.setVisible(False)
		button10.setVisible(False)
		
		# edit combobox
		projects = ['-- select project --'] + self.list_active_projects
		window.set_comboBox_01.setVisible(True)
		
		try:
			window.set_comboBox_01.activated[str].disconnect()
		except:
			pass
		window.set_comboBox_01.clear()
		window.set_comboBox_01.addItems(projects)
		window.set_comboBox_01.activated[str].connect(partial(self.loc_load_group_box))
		
		if self.current_project:
			window.set_comboBox_01.setCurrentIndex(projects.index(self.current_project))
			self.loc_load_group_box(self.current_project)
		else:
			window.set_comboBox_02.setVisible(False)
		
		window.set_comboBox_03.setVisible(False)
		self.myWidget.group_search_qline.setVisible(False)
				
		# edit table
		#self.myWidget.studio_editor_table_2.setVisible(True)
		self.myWidget.right_table_frame.setVisible(True)
		self.myWidget.title_label.setVisible(False)
		self.myWidget.studio_editor_table_2.task = False
		
		# -- selection mode   
		table.setSortingEnabled(True)
		table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		
		self.clear_table()
		self.clear_table(table = self.myWidget.studio_editor_table_2)
				
	def loc_load_group_box(self, project_name):
		if project_name == '-- select project --':
			self.myWidget.set_comboBox_02.setVisible(False)
			self.myWidget.set_comboBox_03.setVisible(False)
			self.myWidget.group_search_qline.setVisible(False)
			self.current_project = False
			self.loc_default_state()
			return
		
		self.current_project = project_name
		# load group list
		result = self.db_group.get_list(self.current_project)
		if not result[0]:
			self.message(result[1], 2)
			return
		
		group_list = result[1]
		right_group_list = ['-- select group --']
		for group in group_list:
			if group['type'] == self.load_group_type:
				right_group_list.append(group['name'])
		try:
			self.myWidget.set_comboBox_02.activated[str].disconnect()
		except:
			pass		
		self.myWidget.set_comboBox_02.clear()		
		self.myWidget.set_comboBox_02.addItems(right_group_list)
		self.myWidget.set_comboBox_02.activated[str].connect(self.loc_load_location_box)
		self.myWidget.set_comboBox_02.setVisible(True)
		
		#print('load group list')
		
	def loc_load_location_box(self, group_name):
		if group_name == '-- select group --':
			self.myWidget.set_comboBox_03.setVisible(False)
			self.myWidget.group_search_qline.setVisible(False)
			self.loc_default_state()
			return
		
		# get group id
		result = self.db_group.get_by_name(self.current_project, group_name)
		if not result[0]:
			self.message(result[1], 2)
			return
		group_data = result[1]
		group_id = group_data['id']
		print(group_id)
		
		# get list of locations
		result = self.db_asset.get_list_by_group(self.current_project, group_id)
		if not result[0]:
			self.message(result[1], 2)
			return
		asset_list = []
		for asset in result[1]:
			asset_list.append(asset['name'])
		
		if self.type_editor == 'location':
			right_locations_list = ['-- select location --'] + asset_list
		elif self.type_editor == 'animation':
			right_locations_list = ['-- select shot --'] + asset_list
			
		try:
			self.myWidget.set_comboBox_03.activated[str].disconnect()
		except:
			pass		
		self.myWidget.set_comboBox_03.clear()
		self.myWidget.set_comboBox_03.addItems(right_locations_list)
		self.myWidget.set_comboBox_03.activated[str].connect(partial(self.loc_load_service_tasks_table, result[1]))
		self.myWidget.set_comboBox_03.setVisible(True)
		
	def loc_load_service_tasks_table(self, asset_rows, asset_name):
		self.loc_default_state()
		if asset_name == '-- select location --' or asset_name == '-- select shot --':
			return
				
		# get asset_id
		asset_id = None
		for row in asset_rows:
			if row['name'] == asset_name:
				asset_id = row['id']
				break
		if not asset_id:
			self.message('asset id not found', 2)
			return
			
		# get task list
		result = self.db_chat.get_list(self.current_project, asset_id)
		if not result[0]:
			self.message(result[1], 2)
			return
		task_list = result[1]
		
		# get service tasks list
		service_task_list = []
		for task in task_list:
			if task['task_type'] == 'service' and task['task_name'].split(':')[1] != 'final':
				service_task_list.append(task)
			if task['task_name'].split(':')[1] == 'all_input':
				# get inputs assets
				inputs = []
				try:
					inputs = json.loads(task['input'])
				except:
					pass
				inputs_assets = []
				for task_name in inputs:
					inputs_assets.append(task_name.split(':')[0])
				self.myWidget.studio_editor_table.all_input = inputs_assets
		
		#print(service_task_list)
		
		
		# ==================== FILL TABLE ====================
		# get num_column, num_row, head
		head = ['Service Tasks:']
		num_row = len(service_task_list)
		num_column = len(head)
		
		# make table
		self.myWidget.studio_editor_table.setColumnCount(num_column)
		self.myWidget.studio_editor_table.setRowCount(num_row)
		self.myWidget.studio_editor_table.setHorizontalHeaderLabels(head)
		
		# edit table
		# -- selection mode   
		self.myWidget.studio_editor_table.setSortingEnabled(True)
		self.myWidget.studio_editor_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
		self.myWidget.studio_editor_table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		  
		# fill table
		for i, task in enumerate(service_task_list):
			newItem = QtGui.QTableWidgetItem()
			newItem.setText(task['task_name'].replace((task['asset'] + ':'), ''))
			newItem.task = dict(task)
			
			rgb = self.db_chat.color_status[task['status']]
			r = (rgb[0]*255)
			g = (rgb[1]*255)
			b = (rgb[2]*255)
			color = QtGui.QColor(r, g, b)
			brush = QtGui.QBrush(color)
			newItem.setBackground(brush)
			'''
			color = self.tasks_color
			brush = QtGui.QBrush(color)
			newItem.setBackground(brush)
			'''
			self.myWidget.studio_editor_table.setItem(i, 0, newItem)
			
		try:
			self.myWidget.studio_editor_table.itemClicked.disconnect()
		except:
			pass
		self.myWidget.studio_editor_table.itemClicked.connect(self.loc_load_content_of_asset_table)
		
	def loc_default_state(self):
		# clear table
		self.clear_table()
		self.clear_table(table = self.myWidget.studio_editor_table_2)
		# hide button and label
		self.myWidget.title_label.setVisible(False)
		self.myWidget.studio_butt_3.setVisible(False)
		self.myWidget.studio_butt_4.setVisible(False)
		self.myWidget.studio_butt_5.setVisible(False)
		self.myWidget.studio_butt_7.setVisible(False)
			
	def loc_load_content_of_asset_table(self, item, update = False):
		self.action_to_tm = 'from_service'
		
		if update:
			task_data = item
		else:
			task_data = item.task
		input_list = []
		if task_data['input']:
			input_list = json.loads(task_data['input'])
		
		# debug
		print('\n')
		print(task_data['input'], task_data['output'])
		
		# ************* view color status *********************** start
		# get asset data list
		all_assets_dict = None
		if input_list:
			result = self.db_asset.get_name_data_dict_by_all_types(self.current_project)
			if not result[0]:
				self.message(result[1])
				return
			else:
				all_assets_dict = result[1]
		# read task read_task(self, project_name, task_name, asset_id, keys)
		inpun_tasks_data = {}
		for task_name in input_list:
			asset_id = all_assets_dict[task_name.split(':')[0]]['id']
			keys = {}
			result = self.db_chat.read_task(self.current_project, task_name, asset_id, 'all')
			if not result[0]:
				self.message(result[1])
				return
			else:
				inpun_tasks_data[task_name] = dict(result[1])
		# ************* view color status *********************** end
			
		# Show Buttons  loc_change_input_task
		self.myWidget.title_label.setVisible(True)
		self.myWidget.studio_butt_3.setVisible(True)
		self.myWidget.studio_butt_4.setVisible(True)
		self.myWidget.studio_butt_5.setVisible(True)
		self.myWidget.studio_butt_7.setVisible(True)
				
		# fill label
		self.myWidget.title_label.setText(task_data['task_name'].replace((task_data['asset']+ ':'), '').replace(':',' : '))
			
		# ==================== FILL TABLE ====================
		# get num_column, num_row, head
		head = ['icon', 'Asset', 'Task Name']
		num_row = len(input_list)
		num_column = len(head)
		
		#clear table ?
		self.clear_table(table = self.myWidget.studio_editor_table_2)
		
		# apply task_data to table  all_assets_dict
		self.myWidget.studio_editor_table_2.task = task_data
		self.myWidget.studio_editor_table_2.assets_by_name = all_assets_dict
		
		# make table
		self.myWidget.studio_editor_table_2.setColumnCount(num_column)
		self.myWidget.studio_editor_table_2.setRowCount(num_row)
		self.myWidget.studio_editor_table_2.setHorizontalHeaderLabels(head)
		
		# -- selection mode   
		self.myWidget.studio_editor_table_2.setSortingEnabled(True)
		self.myWidget.studio_editor_table_2.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.myWidget.studio_editor_table_2.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		
		# fill table
		for i, input_task_name in enumerate(input_list):
			for j, head_label in enumerate(head):
				asset_name = input_task_name.split(':')[0]
				task_name = input_task_name.replace((asset_name + ':'), '')
				if head_label == 'Asset':
					newItem = QtGui.QTableWidgetItem()
					newItem.setText(asset_name)
					newItem.task = inpun_tasks_data[input_task_name]
					
					rgb = self.db_chat.color_status[inpun_tasks_data[input_task_name]['status']]
					r = (rgb[0]*255)
					g = (rgb[1]*255)
					b = (rgb[2]*255)
					color = QtGui.QColor(r, g, b)
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
					
					
				elif head_label == 'Task Name':
					newItem = QtGui.QTableWidgetItem()
					newItem.setText(task_name)
					newItem.task = inpun_tasks_data[input_task_name]
					
				elif head_label == 'icon':
					# get img path
					icon_path = os.path.join(self.db_asset.preview_img_path, (asset_name + '_icon.png'))
					# label
					label = QtGui.QLabel()
					
					if os.path.exists(icon_path):
						# img
						image = QtGui.QImage(icon_path)
						pix = QtGui.QPixmap(image)
																
						label.setPixmap(pix)
						label.show()
					else:
						label.setText('no image')
					
					self.myWidget.studio_editor_table_2.setCellWidget(i, j, label)
					
				if head_label != 'icon':
					self.myWidget.studio_editor_table_2.setItem(i, j, newItem)
					
		self.myWidget.studio_editor_table_2.resizeRowsToContents()
		self.myWidget.studio_editor_table_2.resizeColumnsToContents()
		
		# debug
		try:
			self.myWidget.studio_editor_table_2.itemClicked.disconnect()
		except:
			pass
		self.myWidget.studio_editor_table_2.itemClicked.connect(self.print_item_data)
		
	def print_item_data(self, item):
		if item.task:
			print('\n')
			#print(item.task['input'])
			#print(item.task['output'])
			print(json.dumps(item.task, sort_keys = True, indent = 4))
			
		self.action_to_tm = 'from_content'
			
	def loc_change_input_task_ui(self, *args):
		table2 = self.myWidget.studio_editor_table_2
		service_task_data = self.myWidget.studio_editor_table_2.task
		
		# test service_task_data
		if not service_task_data:
			self.message('Service Task_Data Not Found!', 2)
			return
			
		# get list removed tasks
		list_removed_tasks = []
		task_names = []
		select_items = table2.selectedItems()
		for item in select_items:
			if item.task and not item.task['task_name'] in task_names:
				list_removed_tasks.append(item.task)
				task_names.append(item.task['task_name'])

		if len(list_removed_tasks) > 1:
			self.message('Selected more than one task!', 2)
			return
		elif len(list_removed_tasks) == 0:
			self.message('No task selected!', 2)
			return
			
		removed_task_data = list_removed_tasks[0]
		if removed_task_data['asset_id'] == service_task_data['asset_id']:
			self.message('You can not change the task in this Asset!', 2)
			return
		
		# ask
		ask = self.message('You are sure?', 0)
		if not ask:
			return
			
		# get tasks_list
		result = self.db_chat.get_list(self.current_project, table2.assets_by_name[removed_task_data['asset']]['id'])
		if not result[0]:
			self.message(result[1], 2)
			return
		tasks_list = []
		for task in result[1]:
			if task['task_name'] == removed_task_data['task_name']:
				continue
			elif task['task_name'].split(':')[1] == 'all_input' or task['task_name'].split(':')[1] == 'pre_input':
				continue
			tasks_list.append(task)
					
		ui_path = self.select_from_list_dialog_path
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(ui_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.addAssetsDialog = loader.load(file, self)
		file.close()
		
		# add attr to window
		window.task = removed_task_data
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		# edit Widget
		window.setWindowTitle(('Change Task: \"' + removed_task_data['task_name'].replace(':', ' : ', 2) + '\"'))
		window.select_from_list_cansel_button.clicked.connect(partial(self.close_window, window))
		window.select_from_list_apply_button.clicked.connect(partial(self.loc_change_input_task_action, window))
		
		# fill table
		# table size
		headers = ['task_name', 'activity']
		num_row = len(tasks_list)
		num_column = len(headers)
		
		# -- make table
		table = window.select_from_list_data_list_table
		table.setColumnCount(num_column)
		table.setRowCount(num_row)
		table.setHorizontalHeaderLabels(headers)
		
		# -- selection mode table 
		table.setSortingEnabled(True)
		table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		
		# -- fill table
		for i, task in enumerate(tasks_list):
			for j, head in enumerate(headers):
				newItem = QtGui.QTableWidgetItem()
				#newItem.setText(task[head])
				newItem.setText(task[head].replace((task['task_name'].split(':')[0] + ':'), ''))
				if head == 'task_name':
					newItem.task = None
					
					color = self.tasks_color
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
					
				elif head == 'activity':
					newItem.task = task
					
				table.setItem(i, j, newItem)
				
		window.show()
	
	def loc_add_asset_to_input_ui(self, *args):
		# test task_data
		if not self.myWidget.studio_editor_table_2.task:
			self.message('Service Task_Data Not Found!', 2)
			return
			
		# get task data
		task_data = self.myWidget.studio_editor_table_2.task
		
		all_input = False
		ui_path = self.select_from_list_dialog_path
		if task_data['task_name'].split(':')[1] == 'all_input':
			all_input = True
			ui_path = self.select_from_list_dialog_combobox_path
		
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(ui_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.addAssetsDialog = loader.load(file, self)
		file.close()
		
		# get inputs
		inputs = []
		try:
			inputs = json.loads(task_data['input'])
		except:
			pass
		inputs_assets = []
		for task_name in inputs:
			inputs_assets.append(task_name.split(':')[0])
		window.inputs = inputs_assets
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		# edit Widget
		window.setWindowTitle(('Add Assets To: \"' + task_data['task_name'].replace(':', ' : ', 2) + '\"'))
		window.select_from_list_cansel_button.clicked.connect(partial(self.close_window, window))
		window.select_from_list_apply_button.clicked.connect(partial(self.loc_add_asset_to_input_action, window))
		
		window.group_list = []
		if all_input:
			# load group list
			result = self.db_group.get_list(self.current_project)
			if not result[0]:
				self.message(result[1], 2)
				return
			
			group_list = result[1]
			#window.group_list = []
			right_group_list = ['-- select group --']
			for group in group_list:
				if group['type'] in self.load_asset_types:
					window.group_list.append(group)
					right_group_list.append(group['name'])
			window.dialog_comboBox_1.addItems(right_group_list)
			window.dialog_comboBox_1.activated[str].connect(partial(self.loc_edit_dialog_table, True))
		else:
			self.loc_edit_dialog_table(False, None)
		
		window.all_input = all_input
		window.show()
		
	def loc_add_this_asset_task_to_input_ui(self):
		task_data = self.myWidget.studio_editor_table_2.task
		# test task_data
		if not task_data:
			self.message('Service Task_Data Not Found!', 2)
			return
		elif task_data['task_name'].split(':')[1] == 'all_input':
			self.message('only for Pre_Input!', 2)
			return
		
		ui_path = self.select_from_list_dialog_path
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(ui_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.addAssetsDialog = loader.load(file, self)
		file.close()
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		# edit Widget
		window.setWindowTitle(('Add Assets To: \"' + task_data['task_name'].replace(':', ' : ', 2) + '\"'))
		window.select_from_list_cansel_button.clicked.connect(partial(self.close_window, window))
		window.select_from_list_apply_button.clicked.connect(partial(self.loc_add_this_asset_task_to_input_action, window))
		
		#window.all_input = False
		
		# fill table
		result = self.db_chat.get_list(self.current_project, task_data['asset_id'])
		if not result[0]:
			self.message(result[1], 2)
			return
		task_list = result[1]
		for task_ in task_list:
			if task_['task_type'] == 'service':
				task_list.remove(task_)
		
		# table size
		headers = ['task_name', 'activity']
		num_row = len(task_list)
		num_column = len(headers)
		
		# -- make table
		table = window.select_from_list_data_list_table
		table.setColumnCount(num_column)
		table.setRowCount(num_row)
		table.setHorizontalHeaderLabels(headers)
		
		# -- fill table
		service_input = json.loads(task_data['input'])
		service_output = json.loads(task_data['output'])
		for i, task in enumerate(task_list):
			for j, head in enumerate(headers):
				newItem = QtGui.QTableWidgetItem()
				newItem.setText(task[head].replace((task['task_name'].split(':')[0] + ':'), ''))
				
				if task['task_name'] in service_input:
					newItem.task = None
					
					color = self.grey_color
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
					
				elif task['task_name'] in service_output:
					newItem.task = None
					
					color = self.stop_color
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
				
				elif head == 'task_name':
					newItem.task = None
					
					color = self.tasks_color
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
					
				elif head == 'activity':
					newItem.task = task
				
				table.setItem(i, j, newItem)
		
		table.resizeRowsToContents()
		table.resizeColumnsToContents()
		
		# selection mode
		table.setSortingEnabled(True)
		table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		table.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		
		window.show()
	
	def loc_add_this_asset_task_to_input_action(self, window):
		table = window.select_from_list_data_list_table
		task_data = self.myWidget.studio_editor_table_2.task
		
		# get asset list
		select_items = table.selectedItems()
		task_list = []
		for item in select_items:
			if item.task:
				task_list.append(item.task)
				
		if not task_list:
			self.message('Not Selected Assets!', 2)
			return
			
		result = self.db_chat.service_add_list_to_input(self.current_project, task_data, task_list)
		if not result[0]:
			self.message(result[1], 2)
			return
			
		new_status = result[1][0]
		input_task_list = result[1][1]
		
		self.loc_update_tables('add_input', new_status, input_task_list)
		
		self.close_window(window)
		
	def loc_change_input_task_action(self, window):
		srv_td = self.myWidget.studio_editor_table_2.task
		rm_td = window.task
		
		# get asset list
		table = window.select_from_list_data_list_table
		select_items = table.selectedItems()
		task_list = []
		for item in select_items:
			if item.task:
				task_list.append(item.task)
		
		if not task_list:
			self.message('Not Task Selekted!', 2)
			return
				
		add_td = task_list[0]
		
		result = self.db_chat.service_change_task_in_input(self.current_project, srv_td, rm_td, add_td)
		if not result[0]:
			self.message(result[1], 2)
			return
			
		new_status = result[1][0]
		input_task_list = result[1][1]
		
		self.loc_update_tables('change_input', new_status, input_task_list)
		
		self.close_window(window)
		
	def loc_edit_dialog_table(self, all_input, group_name):
		asset_list = []
		
		if all_input:
			# get asset list
			# -- get group id
			group_id = None
			for group in self.addAssetsDialog.group_list:
				if group['name'] == group_name:
					group_id = group['id']
					break
			# -- get asset list
			result = self.db_asset.get_list_by_group(self.current_project, group_id)
			if not result[0]:
				self.message(result[1], 2)
				return
			asset_list = result[1]
			
		else:
			srv_td = self.myWidget.studio_editor_table_2.task
			
			result = self.db_asset.get_list_by_all_types(self.current_project)
			if not result[0]:
				self.message(result[1], 2)
				return
			for asset in result[1]:
				if asset['name'] == srv_td['asset']:
					continue
			
				if asset['name'] in self.myWidget.studio_editor_table.all_input:
					asset_list.append(asset)
		
		# edit Table
		# -- get table data
		headers = ['icon', 'Asste Name', 'Type']
		num_row = len(asset_list)
		num_column = len(headers)
				    
		# -- make table
		table = self.addAssetsDialog.select_from_list_data_list_table
		self.clear_table(table = table)
		table.setColumnCount(num_column)
		table.setRowCount(num_row)
		table.setHorizontalHeaderLabels(headers)
		
		# -- fill table
		for i, asset in enumerate(asset_list):
			for j, head in enumerate(headers):
				if head == 'Asste Name':
					newItem = QtGui.QTableWidgetItem()
					newItem.setText(asset['name'])
					newItem.asset = None
					
					if asset['name'] in self.addAssetsDialog.inputs:
						color = self.grey_color
						brush = QtGui.QBrush(color)
						newItem.setBackground(brush)
					else:
						color = self.asset_color
						brush = QtGui.QBrush(color)
						newItem.setBackground(brush)
										
				elif head == 'Type':
					newItem = QtGui.QTableWidgetItem()
					newItem.setText(asset['type'])
					newItem.asset = asset
					
					if asset['name'] in self.addAssetsDialog.inputs:
						color = self.grey_color
						brush = QtGui.QBrush(color)
						newItem.setBackground(brush)
						newItem.asset = None
						
				elif head == 'icon':
					# get img path
					icon_path = os.path.join(self.db_asset.preview_img_path, (asset['name'] + '_icon.png'))
					# label
					label = QtGui.QLabel()
					
					if os.path.exists(icon_path):
						# img
						image = QtGui.QImage(icon_path)
						pix = QtGui.QPixmap(image)
																
						label.setPixmap(pix)
						label.show()
					else:
						label.setText('no image')
					
					table.setCellWidget(i, j, label)
				
				if head != 'icon':
					table.setItem(i, j, newItem)
					
		table.resizeRowsToContents()
		table.resizeColumnsToContents()
		
		# debug
		#table.itemClicked.connect(self.print_table_item)
				
		# -- selection mode   
		table.setSortingEnabled(True)
		table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		table.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		
	def print_table_item(self, item):
		print(item.asset)
		
	def loc_add_asset_to_input_action(self, window):
		table = window.select_from_list_data_list_table
		task_data = self.myWidget.studio_editor_table_2.task
		
		# get asset list
		select_items = table.selectedItems()
		asset_list = []
		for item in select_items:
			if item.asset:
				asset_list.append(item.asset)
				
		if not asset_list:
			self.message('Not Selected Assets!', 2)
			return
			
		result = self.db_chat.service_add_list_to_input_from_asset_list(self.current_project, task_data, asset_list)
		if not result[0]:
			self.message(result[1], 2)
			return
			
		new_status = result[1][0]
		input_task_list = result[1][1]
		
		self.loc_update_tables('add_input', new_status, input_task_list)
		
		self.close_window(window)
		
	def loc_remove_task_from_input_action(self, *args):
		ask = self.message('you are sure?', 0)
		if not ask:
			return
		
		# 	
		table2 = self.myWidget.studio_editor_table_2
		service_task_data = self.myWidget.studio_editor_table_2.task
		
		# get list removed tasks
		list_removed_tasks = []
		select_items = table2.selectedItems()
		for item in select_items:
			if item.task:
				list_removed_tasks.append(item.task)
		
		# remove tasks
		result = self.db_chat.service_remove_task_from_input(self.current_project, service_task_data, list_removed_tasks)
		if not result[0]:
			self.message(result[1], 2)
			return
		
		new_status = result[1][0]
		input_task_list = result[1][1]
		
		self.loc_update_tables('remove_input', new_status, input_task_list)
							
	def loc_update_tables(self, action, new_status, input_task_list):
		# get service task item
		table = self.myWidget.studio_editor_table
		table_2 = self.myWidget.studio_editor_table_2
		if action == 'add_input':
			# edit service task data
			for i in range(0, table.rowCount()):
				item = table.item(i,0)
				if item.task['task_name'] == table_2.task['task_name']:
					item.task['status'] = new_status
					if item.task['input']:
						ex_inputs = json.loads(item.task['input'])
						new_inputs = ex_inputs + input_task_list
						item.task['input'] = json.dumps(new_inputs)
					else:
						item.task['input'] = json.dumps(input_task_list)
						
					rgb = self.db_chat.color_status[new_status]
					r = (rgb[0]*255)
					g = (rgb[1]*255)
					b = (rgb[2]*255)
					color = QtGui.QColor(r, g, b)
					brush = QtGui.QBrush(color)
					item.setBackground(brush)
			
			# add asset to table.all_input
			for task in input_task_list:
				table.all_input.append(task.split(':')[0])
				
		elif action == 'remove_input':
			# edit service task data
			for i in range(0, table.rowCount()):
				item = table.item(i,0)
				if item.task['task_name'] == table_2.task['task_name']:
					item.task['status'] = new_status
					item.task['input'] = json.dumps(input_task_list)
											
					rgb = self.db_chat.color_status[new_status]
					r = (rgb[0]*255)
					g = (rgb[1]*255)
					b = (rgb[2]*255)
					color = QtGui.QColor(r, g, b)
					brush = QtGui.QBrush(color)
					item.setBackground(brush)
			
			if table_2.task['task_name'].split(':')[1] == 'all_input':
				# clear table.all_input
				table.all_input = []
				# add asset to table.all_input
				for task in input_task_list:
					table.all_input.append(task.split(':')[0])
					
		elif action == 'change_input':
			# edit service task data
			for i in range(0, table.rowCount()):
				item = table.item(i,0)
				if item.task['task_name'] == table_2.task['task_name']:
					item.task['status'] = new_status
					# edit input
					input_list = json.loads(item.task['input'])
					for tm in input_list:
						if tm.split(':')[0] == input_task_list[0].split(':')[0]:
							input_list.remove(tm)
					input_list.append(input_task_list[0])		
					item.task['input'] = json.dumps(input_list)
					# edit color						
					rgb = self.db_chat.color_status[new_status]
					r = (rgb[0]*255)
					g = (rgb[1]*255)
					b = (rgb[2]*255)
					color = QtGui.QColor(r, g, b)
					brush = QtGui.QBrush(color)
					item.setBackground(brush)
								
		# reload table_2
		self.loc_load_content_of_asset_table(table_2.task, update = True)
		
	# *********************** TASKS MANAGER *********************************************
	
	def preparation_to_task_manager(self):
		self.myWidget.task_manager_reload_button.setText('reload')
		#self.myWidget.task_manager_reload_button.clicked.connect(self.tm_fill_project_workroom_list)
		self.myWidget.task_manager_comboBox_2.setVisible(False)
		self.myWidget.task_manager_comboBox_3.setVisible(False)
		self.myWidget.task_manager_comboBox_4.setVisible(False)
		self.myWidget.task_manager_comboBox_5.setVisible(False)
		# fill type of assets box
		self.myWidget.task_manager_comboBox_5.addItems((['-all types-'] + self.db_studio.asset_types))
		self.myWidget.task_manager_comboBox_5.activated[str].connect(self.tm_reload_group_list_by_type)
		self.myWidget.local_search_qline.setVisible(False)
		self.myWidget.local_search_qline.returnPressed.connect(self.tm_reload_task_list)
		self.myWidget.global_search_qline.setVisible(False)
		self.myWidget.global_search_qline.returnPressed.connect(self.tm_reload_task_list_by_global_search_ui)
		
		self.myWidget.button_area.setVisible(False)
		
		# ----------- POPUP MENU --------------------------
		# LOCAL SEARCH
		self.myWidget.local_search_qline.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
		for status in self.db_chat.task_status:
			addgrup_action = QtGui.QAction( status, self.myWidget)
			addgrup_action.triggered.connect(partial(self.tm_reload_task_list_by_status, status))
			self.myWidget.local_search_qline.addAction( addgrup_action )
		
		# ACTIVITY
		self.myWidget.tm_data_label_2.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
		addgrup_action = QtGui.QAction( 'change Activity', self.myWidget)
		addgrup_action.triggered.connect(partial(self.tm_change_task_activity_ui))
		self.myWidget.tm_data_label_2.addAction( addgrup_action )
		
		# WORKROOM
		self.myWidget.tm_data_label_3.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
		addgrup_action = QtGui.QAction( 'change Workroom', self.myWidget)
		addgrup_action.triggered.connect(partial(self.tm_change_task_workroom_ui))
		self.myWidget.tm_data_label_3.addAction( addgrup_action )
		
		# PRICE
		self.myWidget.tm_data_label_5.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
		addgrup_action = QtGui.QAction( 'change Price', self.myWidget)
		addgrup_action.triggered.connect(partial(self.tm_change_task_price_ui))
		self.myWidget.tm_data_label_5.addAction( addgrup_action )
		
		# ARTIST
		self.myWidget.tm_data_label_1.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
		addgrup_action = QtGui.QAction( 'change Artist', self.myWidget)
		addgrup_action.triggered.connect(partial(self.tm_change_task_artist_ui))
		self.myWidget.tm_data_label_1.addAction( addgrup_action )
		
		# INPUT
		self.myWidget.tm_data_label_4.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
		addgrup_action = QtGui.QAction( 'change Input Task', self.myWidget)
		addgrup_action.triggered.connect(partial(self.tm_change_task_input_ui))
		self.myWidget.tm_data_label_4.addAction( addgrup_action )
		
		# TASK_ TYPE
		self.myWidget.tm_data_label_6.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
		addgrup_action = QtGui.QAction( 'change Task Type', self.myWidget)
		addgrup_action.triggered.connect(partial(self.tm_change_task_type_ui))
		self.myWidget.tm_data_label_6.addAction( addgrup_action )
		
		# EXTENSION
		self.myWidget.tm_data_label_7.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
		addgrup_action = QtGui.QAction( 'change Extension', self.myWidget)
		addgrup_action.triggered.connect(partial(self.tm_change_task_extension_ui))
		self.myWidget.tm_data_label_7.addAction( addgrup_action )
		
		# EXTENSION
		self.myWidget.tm_data_label_8.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
		addgrup_action = QtGui.QAction( 'change Link', self.myWidget)
		addgrup_action.triggered.connect(partial(self.tm_change_tz_link_ui))
		self.myWidget.tm_data_label_8.addAction( addgrup_action )
		
		# EDIT READERS
		self.myWidget.readers_list.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
		addgrup_action = QtGui.QAction( 'Edit Readers', self.myWidget)
		addgrup_action.triggered.connect(partial(self.tm_edit_readers_ui))
		self.myWidget.readers_list.addAction( addgrup_action )
		
		# connect button
		self.myWidget.make_preview_button.clicked.connect(self.tm_make_preview_ui)
		self.myWidget.task_manager_reload_button.clicked.connect(self.tm_reload_task_list)
		self.myWidget.chat_button.clicked.connect(self.chat_ui)
		self.myWidget.chat_button.setMinimumHeight(50)
		self.myWidget.tz_button.clicked.connect(self.tm_tz)
		self.myWidget.tz_button.setMinimumHeight(50)
		self.myWidget.assept_button.clicked.connect(self.tm_accept_task_action)
		self.myWidget.close_task_button.clicked.connect(self.tm_close_task_action)
		self.myWidget.to_rework_button.clicked.connect(self.tm_rework_action)
		self.myWidget.return_a_job_button.clicked.connect(self.tm_return_a_job_action)
		self.myWidget.look_file_button.clicked.connect(self.tm_look_file_action)
		self.myWidget.look_version_file_button.clicked.connect(self.tm_look_version_file_ui)
		self.myWidget.add_task_button.clicked.connect(self.tm_add_task_ui)
		self.myWidget.add_task_button.setText('Add Single Task')
		self.myWidget.edit_readers_button.clicked.connect(self.tm_edit_readers_ui)
		
		# fill projects list
		self.tm_fill_project_list()
		
	def chat_ui(self):
		self.chat_status = 'manager'
		#self.current_task = G.current_task
		#self.current_user = G.current_user
		#self.current_project = G.current_project
		
		import lineyka_chat
		chat_window = lineyka_chat.lineyka_chat(self)
		#chat_class.__init__(self)
		
	def boxes_default_state(self):
		self.myWidget.task_manager_comboBox_2.setVisible(False)
		self.myWidget.task_manager_comboBox_2.clear()
		self.myWidget.task_manager_comboBox_3.setVisible(False)
		self.myWidget.task_manager_comboBox_3.clear()
		self.myWidget.task_manager_comboBox_5.setVisible(False)
		self.myWidget.local_search_qline.setVisible(False)
		self.myWidget.local_search_qline.clear()
		self.myWidget.global_search_qline.setVisible(False)
		self.myWidget.global_search_qline.clear()
		
		self.myWidget.button_area.setVisible(False)
		self.clear_table(table = self.myWidget.task_manager_table)
				
	def tm_fill_project_list(self):
		copy = self.db_workroom
		
		# get studio
		copy.get_list_projects()
		self.db_group.get_list_projects()
		self.db_series.get_list_projects()
		self.db_chat.get_list_projects()
		self.db_asset.get_list_projects()
		self.db_log.get_list_projects()
		
		if not self.artist.nik_name:
			self.message('Not User!', 2)
			self.boxes_default_state()
			self.myWidget.task_manager_comboBox_1.clear()
			self.myWidget.task_manager_comboBox_4.clear()
			return
		elif copy.user_levels.index(self.artist.level) < copy.user_levels.index('manager'):
			self.message('No Access!', 2)
			self.boxes_default_state()
			self.myWidget.task_manager_comboBox_1.clear()
			self.myWidget.task_manager_comboBox_4.clear()
			return
		
		# fill project list
		items = ['-- select project --'] + self.list_active_projects
		self.myWidget.task_manager_comboBox_1.clear()
		self.myWidget.task_manager_comboBox_1.addItems(items)
		self.myWidget.task_manager_comboBox_1.activated[str].connect(partial(self.tm_fill_series_groups))
		
		# fill workroom list
		self.tm_fill_workroom_list()
		
	def tm_fill_workroom_list(self):
		copy = self.db_workroom
		result = copy.get_list_workrooms()
		if copy.user_levels.index(self.artist.level) >= copy.user_levels.index('root'):
			#result = copy.get_list_workrooms()
			if result[0]:
				wr_list = []
				for wr in result[1]:
					wr_list.append(wr['name'])
				items = ['all workrooms'] + wr_list
				self.myWidget.task_manager_comboBox_4.setVisible(True)
				self.myWidget.task_manager_comboBox_4.clear()
				self.myWidget.task_manager_comboBox_4.addItems(items)
				self.myWidget.task_manager_comboBox_4.wr_list = wr_list
		else:
			user_wr_list = json.loads(self.artist.workroom)
			if result[0]:
				wr_list = []
				for wr in result[1]:
					if wr['id'] in user_wr_list:
						wr_list.append(wr['name'])
									
				items = ['all workrooms'] + wr_list
				self.myWidget.task_manager_comboBox_4.setVisible(True)
				self.myWidget.task_manager_comboBox_4.clear()
				self.myWidget.task_manager_comboBox_4.addItems(items)
				self.myWidget.task_manager_comboBox_4.wr_list = wr_list
		
		self.myWidget.task_manager_comboBox_4.activated[str].connect(self.tm_reload_task_list)
			
		
	def tm_fill_series_groups(self, project_name):
		copy = self.db_group
		filter_of_type = self.myWidget.task_manager_comboBox_5.currentText()
		if filter_of_type == '-all types-':
			f = copy.asset_types
		else:
			f = filter_of_type
		
		result = copy.get_list(project_name, f = f)
		
		copy_s = self.db_series
		result_s = copy_s.get_list(project_name)
		
		if project_name == '-- select project --':
			self.boxes_default_state()
			return
		else:
			self.current_project = project_name
			self.myWidget.global_search_qline.setVisible(True)
		
		if result[0]:
			# fil series list
			if result_s[0]:
				series_list = []
				for row in result_s[1]:
					series_list.append(row['name'])
				items_ = ['-- all series --'] + series_list
				self.myWidget.task_manager_comboBox_2.setVisible(True)
				self.myWidget.task_manager_comboBox_2.clear()
				self.myWidget.task_manager_comboBox_2.addItems(items_)
				self.myWidget.task_manager_comboBox_2.activated[str].connect(self.tm_reload_group_list)
			
			# fill group list
			group_list = []
			group_id_list = []
			for row in result[1]:
				group_list.append(row['name'])
				group_id_list.append(row['id'])
			items = ['-- select group --'] + group_list
			G.id_group_items = [''] + group_id_list
			
			self.myWidget.task_manager_comboBox_3.setVisible(True)
			self.myWidget.task_manager_comboBox_3.clear()
			self.myWidget.task_manager_comboBox_3.addItems(items)
			try:
				self.myWidget.task_manager_comboBox_3.activated[str].disconnect()
			except:
				pass
			#self.myWidget.task_manager_comboBox_3.activated[str].connect(self.tm_reload_task_list)
			self.myWidget.task_manager_comboBox_3.activated[int].connect(self.tm_reload_task_list)
			# unhide asset types box
			self.myWidget.task_manager_comboBox_5.setVisible(True)
			
		else:
			try:
				self.myWidget.task_manager_comboBox_3.activated[str].disconnect()
			except:
				pass
			self.boxes_default_state()
			self.message(result[1], 2)
			
	def tm_reload_group_list_by_type(self, filter_of_type):
		series = self.myWidget.task_manager_comboBox_2.currentText()
		if filter_of_type != '-all types-':
			self.tm_reload_group_list(series, filter_of_type = filter_of_type)
		else:
			self.tm_reload_group_list(series)
			
	def tm_reload_group_list(self, series, filter_of_type = False):
		if not filter_of_type:
			filter_of_type = self.db_studio.asset_types
		# get group list
		result = self.db_group.get_list(self.current_project, f = filter_of_type)
		
		# get series id
		series_id = ''
		if series != '-- all series --':
			copy_s = self.db_series
			res = copy_s.get_by_name(self.current_project, series)
			if not res[0]:
				self.message(res[1], 2)
				self.myWidget.task_manager_comboBox_2.setCurrentIndex(0)
				return
			else:
				series_id = res[1]['id']
		
		# fill combobox
		if result[0]:
			group_list = []
			group_id_list = []
			for row in result[1]:
				if row['series'] == series_id or series == '-- all series --':
					group_list.append(row['name'])
					group_id_list.append(row['id'])
									
			items = ['-- select group --'] + group_list
			G.id_group_items = [''] + group_id_list
			
			self.myWidget.task_manager_comboBox_3.setVisible(True)
			self.myWidget.task_manager_comboBox_3.clear()
			self.myWidget.task_manager_comboBox_3.addItems(items)
	
	# ---------- RELOAD TASK_ LIST ----------------------------------------------
	
	def tm_reload_task_list_by_global_search_ui(self):
		# Get Data
		# -- get search
		search = self.myWidget.global_search_qline.text()
		
		# -- asset list
		result = self.db_asset.get_list_by_all_types(self.current_project)
		if not result[0]:
			self.message(result[1], 3)
			return
			
		asset_list = []
		for asset in result[1]:
			if search.lower() in asset['name'].lower():
				asset_list.append(asset)
				
		if not asset_list:
			self.message('Not Found!', 2)
			return
			
		# -- group dict
		result = self.db_group.get_groups_dict_by_id(self.current_project)
		if not result[0]:
			self.message(result[1], 3)
			return
		group_dict = result[1]
		
		
		self.searchDialog = QtGui.QDialog(self)
		self.searchDialog.setModal(True)
		self.searchDialog.setWindowTitle('Search Results')
		
		# add widget
		v_layout = QtGui.QVBoxLayout()
		table = QtGui.QTableWidget()
		v_layout.addWidget(table)
		close_button = QtGui.QPushButton('Close')
		close_button.clicked.connect(partial(self.close_window, self.searchDialog))
		v_layout.addWidget(close_button)
		self.searchDialog.setLayout(v_layout)
		
		
		headers = ['icon', 'name', 'group', 'type']
		num_column = len(headers)
		num_row = len(asset_list)
		
		table.setColumnCount(num_column)
		table.setRowCount(num_row)
		table.setHorizontalHeaderLabels(headers)
		
		table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		table.itemClicked.connect(partial(self.tm_reload_task_list_by_global_search_action, self.searchDialog, group_dict))
		
		for i, row in enumerate(asset_list):
			for j,header in enumerate(headers):
				newItem = QtGui.QTableWidgetItem()
				newItem.asset = row
				
				if header == 'group':
					newItem.setText(group_dict[row[header]]['name'])
				else:
					if header != 'icon':
						newItem.setText(row[header])
				
				if header == 'name':
					color = QtGui.QColor(self.asset_color)
					brush = QtGui.QBrush(color)
					newItem.setBackground(brush)
					
				elif header == 'icon':
					# get img path
					icon_path = os.path.join(self.db_asset.preview_img_path, (row['name'] + '_icon.png'))
					# label
					label = QtGui.QLabel()
					
					if os.path.exists(icon_path):
						# img
						image = QtGui.QImage(icon_path)
						pix = QtGui.QPixmap(image)
						label.setPixmap(pix)
						label.show()
					else:
						label.setText('no image')
					
					table.setCellWidget(i, j, label)
				
				if header != 'icon':
					table.setItem(i, j, newItem)
				
				#table.setItem(i, j, newItem)
				#print(i,j)
				
		table.resizeRowsToContents()
		table.resizeColumnsToContents()
		
		self.searchDialog.show()
		
	def tm_reload_task_list_by_global_search_action(self, window, group_dict, item):
		asset_data = item.asset
		
		# 1 - 3 load comboboxes
		self.myWidget.task_manager_comboBox_4.setCurrentIndex(0)
		self.myWidget.task_manager_comboBox_2.setCurrentIndex(0)
		self.myWidget.task_manager_comboBox_5.setCurrentIndex(0)
		self.tm_fill_series_groups(self.myWidget.task_manager_comboBox_1.currentText())
		
		self.myWidget.local_search_qline.setText(asset_data['name'])
		for i in range(0, self.myWidget.task_manager_comboBox_3.model().rowCount()):
			if self.myWidget.task_manager_comboBox_3.itemText(i) == group_dict[asset_data['group']]['name']:
				self.myWidget.task_manager_comboBox_3.setCurrentIndex(i)
				self.tm_reload_task_list()
				break
		
		self.close_window(window)
		
	def tm_reload_task_list_by_status(self, status):
		self.myWidget.local_search_qline.setText(status)
		self.tm_reload_task_list()
		
	def tm_reload_task_list(self, *args):
		#if search:
		group_name = self.myWidget.task_manager_comboBox_3.currentText()
		index = self.myWidget.task_manager_comboBox_3.currentIndex()
		search = self.myWidget.local_search_qline.text().lower().replace(' ', '_')
		self.myWidget.button_area.setVisible(False)
		
		SEARCH_IDENTIFIERS = ('#','@')
		
		group_id = G.id_group_items[index]
				
		#if group_name == '-- select group --':
		if not group_id:
			self.myWidget.button_area.setVisible(False)
			self.clear_table(table = self.myWidget.task_manager_table)
			return
		else:
			self.myWidget.local_search_qline.setVisible(True)
			
		# get self.current_group 
		#copy = db.group()
		result = self.db_group.get_by_id(self.current_project, group_id)
		if not result[0]:
			self.message(result[1], 3)
			return
		else:
			self.current_group = result[1]
			
		
		# ==================== METADATA ==================== self.tasks_rows, num_column, num_row
		# get current workroom
		wr_name = self.myWidget.task_manager_comboBox_4.currentText()
		copy_wr = self.db_workroom
		current_wr_id = []
		if wr_name != 'all workrooms':
			result = copy_wr.get_id_by_name(wr_name)
			if not result[0]:
				self.message(result[1], 2)
				return
			else:
				current_wr_id.append(result[1])
		else:
			current_wr_name = self.myWidget.task_manager_comboBox_4.wr_list
			result = copy_wr.name_list_to_id_list(current_wr_name)
			if not result[0]:
				self.message(result[1], 2)
				return
			else:
				current_wr_id = result[1]
		
		# get workroom list
		result = copy_wr.get_list_workrooms(DICTONARY = 'by_id')
		if not result[0]:
			self.message(result[1], 2)
			return
		else:
			self.myWidget.task_manager_table.workrooms = result[1]
						
		# get asset list
		#copy = self.db_task
		result = self.db_chat.get_list_by_group(self.current_project, self.current_group['id'])
		asset_list = []
		if result[0]:
			if not search or search in self.db_chat.task_status: # пустая строка поиска либо в строке поиска статус задачи
				asset_list = result[1]
			else:
				for row in result[1]:
					if search in row['name'].lower():
						asset_list.append(row)
		else:
			self.message(result[1], 2)
			return
		
		'''
		# get assets_name_by_id
		result = copy.get_id_name_dict_by_type(self.current_project, self.current_group['type'])
		if not result[0]:
			self.message(result[1], 2)
			return
		else:
			self.myWidget.task_manager_table.assets_name_by_id = result[1]
		'''
		
		# create tasks rows
		num_column = []
		self.tasks_rows = {}
		fin_asset_list = []
		for asset_ in asset_list:
			#self.tasks_rows[asset_['name']] = []
			# -- get task list
			task_list = []
			if search and search in self.db_chat.task_status:
				result = self.db_chat.get_list(self.current_project, asset_['id'], search)
			
			else:
				result = self.db_chat.get_list(self.current_project, asset_['id'])
			if result[0]:
				if not result[1]: # в смысле вернулся пустой список
					continue
				else:
					task_list = result[1]
					fin_asset_list.append(asset_)
			else:
				continue
			self.tasks_rows[asset_['name']] = []
			# -- -- tasks labels
			len_ = len(task_list)
			for task_ in task_list:
				if task_['task_type'] == 'service':
					len_ = len_ - 1
					continue
					#self.tasks_rows[asset_['name']].append(task_)
				#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
				elif wr_name != 'all workrooms':
					if not task_['workroom'] in current_wr_id:
						len_ = len_ - 1
						continue
				else:
					self.tasks_rows[asset_['name']].append(task_)
			num_column.append(len_)
		if num_column:
			num_column = max(num_column) + 1
		else:
			num_column = 0
		
		#num_row = len(asset_list)
		num_row = len(fin_asset_list)
		
		print(num_column, num_row)
		
		# ==================== FILL TABLE ====================
		#clear table ?
		self.clear_table(table = self.myWidget.task_manager_table)
		
		# make table
		self.myWidget.task_manager_table.setColumnCount(num_column)
		self.myWidget.task_manager_table.setRowCount(num_row)
		self.myWidget.task_manager_table.setVerticalHeaderLabels(self.tasks_rows.keys())
		
		# edit table
		# -- selection mode  
		#self.myWidget.task_manager_table.setSortingEnabled(True)
		self.myWidget.task_manager_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
		self.myWidget.task_manager_table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		  
				
		# fill table
		for i, asset in enumerate(self.tasks_rows):
			
			# get img path
			icon_path = os.path.join(self.db_chat.preview_img_path, (asset + '_icon.png'))
			# label
			label = QtGui.QLabel()
			
			if os.path.exists(icon_path):
				# img
				image = QtGui.QImage(icon_path)
				pix = QtGui.QPixmap(image)
														
				label.setPixmap(pix)
				label.show()
			else:
				label.setText('no image')
			'''
			label = QtGui.QLabel()
			label.setText(asset)
			'''
			self.myWidget.task_manager_table.setCellWidget(i, 0, label)
			
			for j,task_ in enumerate(self.tasks_rows[asset]):
				j = j+1
				'''
				if task_['task_type'] == 'service':
					continue
				'''
				newItem = QtGui.QTableWidgetItem()
				newItem.setText(task_['task_name'].replace((task_['asset'] + ':'), ''))
				newItem.task = task_
				
				rgb = self.db_chat.color_status[task_['status']]
				r = (rgb[0]*255)
				g = (rgb[1]*255)
				b = (rgb[2]*255)
				color = QtGui.QColor(r, g, b)
				brush = QtGui.QBrush(color)
				newItem.setBackground(brush)
				
				self.myWidget.task_manager_table.setItem(i, j, newItem)
			# add empty item	
			if not self.tasks_rows[asset]:
				#print(asset)
				for jj in range(0, num_column):
					newItem = QtGui.QTableWidgetItem()
					newItem.task = None
					self.myWidget.task_manager_table.setItem(i, jj, newItem)
			elif len(self.tasks_rows[asset])<num_column:
				for jj in range((j+1), num_column):
					newItem = QtGui.QTableWidgetItem()
					newItem.task = None
					self.myWidget.task_manager_table.setItem(i, jj, newItem)
					
		self.myWidget.task_manager_table.resizeRowsToContents()
		self.myWidget.task_manager_table.resizeColumnsToContents()
			
		try:
			self.myWidget.task_manager_table.itemClicked.disconnect()
		except:
			pass
		self.myWidget.task_manager_table.itemClicked.connect(self.tm_load_buttons_of_tasks)
		
	def tm_load_buttons_of_tasks(self, *args):
		
		print(json.dumps(dict(args[0].task), sort_keys = True, indent = 4))
		
		try:
			old_asset = self.current_task['asset']
		except:
			old_asset = None
		
		task_data = None
		try:
			task_data = args[0].task
			# visible button frame
			self.myWidget.button_area.setVisible(True)
			
			# -- ACCEPT button
			if task_data['status'] in self.db_chat.working_statuses or task_data['status'] == 'checking':
				self.myWidget.assept_button.setVisible(True)
			else:
				self.myWidget.assept_button.setVisible(False)
			# -- SEND TO AUTSOURCE button
			if task_data['status'] == 'ready_to_send':
				self.myWidget.send_to_outsource_button.setVisible(True)
			else:
				self.myWidget.send_to_outsource_button.setVisible(False)
			
			# -- TO REWORK button
			if task_data['status'] == 'checking':
				self.myWidget.to_rework_button.setVisible(True)
			else:
				self.myWidget.to_rework_button.setVisible(False)
				
			# -- CLOSE button
			if not task_data['status'] in self.db_chat.end_statuses:
				self.myWidget.close_task_button.setVisible(True)
			else:
				self.myWidget.close_task_button.setVisible(False)
			
			# -- RETURN A JOB button
			if task_data['status'] in self.db_chat.end_statuses:
				self.myWidget.return_a_job_button.setVisible(True)
			else:
				self.myWidget.return_a_job_button.setVisible(False)
			
		except:
			self.myWidget.button_area.setVisible(False)
			return
		if not task_data:
			self.myWidget.button_area.setVisible(False)
			return
		'''	
		# asset_name_by_id
		asset_id_name = self.myWidget.task_manager_table.assets_name_by_id
		'''					
		# ------------ Fill Task Labels -------------------
		'''
		# -- get task label
		task_label = task_data['task_name'].replace(task_data['asset'], asset_id_name[task_data['asset']]).replace(':', ' : ')
		# -- get input name
		input_label = ''
		if task_data['input']:
			input_label = task_data['input'].replace(task_data['asset'], asset_id_name[task_data['asset']]).replace(':', ' : ')
		'''
		# get labels
		task_label = task_data['task_name'].replace(':', ' : ')
		input_label = task_data['input'].replace(':', ' : ')
		
		# -- set labels
		self.myWidget.tm_task_name_label.setText(task_label)
		self.myWidget.tm_data_label_1.setText(task_data['artist'])
		self.myWidget.tm_data_label_2.setText(task_data['activity'])
		self.myWidget.tm_data_label_3.setText(self.myWidget.task_manager_table.workrooms[task_data['workroom']]['name'])
		self.myWidget.tm_data_label_4.setText(input_label)
		self.myWidget.tm_data_label_5.setText(str(task_data['price']))
		self.myWidget.tm_data_label_6.setText(task_data['task_type'])
		self.myWidget.tm_data_label_7.setText(task_data['extension'])
		self.myWidget.tm_data_label_8.setText(task_data['tz'])
		
		# -- load to preview img
		if old_asset != task_data['asset']:
			#print('change image')
			preview_path = os.path.join(self.db_chat.preview_img_path, (task_data['asset'] + '.png'))
			if os.path.exists(preview_path):
				image = QtGui.QImage(preview_path)
				self.myWidget.image_label.setPixmap(QtGui.QPixmap.fromImage(image))
			else:
				icon_path = os.path.join(self.lineyka_path, 'icons', 'no_image_300.png')
				image = QtGui.QImage(icon_path)
				self.myWidget.image_label.setPixmap(QtGui.QPixmap.fromImage(image))
		else:
			pass
			#print('old image')
			
		# -- READERS visibility, content
		# get CURRENT readers list
		self.current_readers_list = {}
		try:
			self.current_readers_list = json.loads(task_data['readers'])
		except:
			pass
		
		# get CLEANED readers list
		self.cleaned_readers_list = {}
		for key in self.current_readers_list:
			if key == 'first_reader':
				continue
			self.cleaned_readers_list[key] = self.current_readers_list[key]
		
		# set visible
		if not self.current_readers_list:
			self.myWidget.readers_list.setVisible(False)
			self.myWidget.edit_readers_button.setVisible(True)
		else:
			self.tm_load_readers_list()
		
		# fill field for chat
		self.current_task = task_data
		
	# ---- readers editor ----------------
		
	def tm_load_readers_list(self):
		self.myWidget.readers_list.clear()
		
		# get CLEANED readers list
		self.cleaned_readers_list = {}
		for key in self.current_readers_list:
			if key == 'first_reader':
				continue
			self.cleaned_readers_list[key] = self.current_readers_list[key]
		
		if not self.cleaned_readers_list:
			self.myWidget.readers_list.setVisible(False)
			self.myWidget.edit_readers_button.setVisible(True)
			return
		
		string = 'readers:\n'
		for key in self.cleaned_readers_list:
			new_string = key + '- '*(20 - len(key)) + str(self.cleaned_readers_list[key]) + '\n'
			if 'first_reader' in self.current_readers_list:
				if key == self.current_readers_list['first_reader']:
					new_string = '(***)' + key + '- '*(20 - len(key)) + str(self.cleaned_readers_list[key]) + '\n'
			string = string + new_string
		self.myWidget.readers_list.append(string)
		
		# -- change visible
		self.myWidget.edit_readers_button.setVisible(False)
		self.myWidget.readers_list.setVisible(True)
		
	def tm_edit_readers_ui(self):
		# create window
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.select_from_list_dialog_3button_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.editReadersDialog = loader.load(file, self)
		file.close()
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		# edit Widget
		window.setWindowTitle('Edit Readers List')
		window.pushButton_01.setText('Remove Readers')
		window.pushButton_02.setText('Add Readers')
		
		# -- selection mode
		table = window.select_from_list_data_list_table
		table.setSortingEnabled(True)
		table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		table.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		
		# table_2 context menu
		table.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
		addgrup_action = QtGui.QAction( 'make First', self.myWidget)
		addgrup_action.triggered.connect(partial(self.tm_make_first_reader, table))
		table.addAction( addgrup_action )
		
		# button connect
		window.select_from_list_cansel_button.clicked.connect(partial(self.close_window, window))
		window.pushButton_01.clicked.connect(partial(self.tm_remove_reader_action))
		window.pushButton_02.clicked.connect(self.tm_add_readers_ui)
		
		# load table
		self.tm_edit_readers_ui_reload_table()
		
		window.show()
		
	def tm_edit_readers_ui_reload_table(self):
		table = self.editReadersDialog.select_from_list_data_list_table
		
		# load table
		headers = ['nik_name']
		num_column = len(headers)
		num_row = 0
		
		if self.cleaned_readers_list:
			num_row = len(self.cleaned_readers_list)
		
		
		table.setColumnCount(num_column)
		table.setRowCount(num_row)
		table.setHorizontalHeaderLabels(headers)
		
		if self.cleaned_readers_list:
			for i,reader_name in enumerate(self.cleaned_readers_list):
				if reader_name == 'first_reader':
					continue
				for j,key in enumerate(headers):
					newItem = QtGui.QTableWidgetItem()
					if key == 'nik_name':
						newItem.setText(reader_name)
						if 'first_reader' in self.current_readers_list:
							if self.current_readers_list['first_reader'] == reader_name:
								newItem.setText((reader_name + ' (***)'))
						color = self.artist_color
						brush = QtGui.QBrush(color)
						newItem.setBackground(brush)
						
						newItem.reader_name = reader_name
		
					table.setItem(i, j, newItem)
		
	def tm_add_readers_ui(self):
		# create window
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.select_from_list_dialog_combobox_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.selectReadersDialog = loader.load(file, self)
		file.close()
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		# edit Widget
		table = window.select_from_list_data_list_table
		# -- labels
		window.setWindowTitle('Select Readers')
		window.select_from_list_apply_button.setText('Add')
		
		# -- selection mode
		table.setSortingEnabled(True)
		table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		table.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
		
		# -- load workroom_list
		result = self.db_workroom.get_list_workrooms(DICTONARY = 'by_name')
		if not result[0]:
			self.message(result[1], 2)
		workroom_dict = result[1]
		window.workroom_dict = workroom_dict
		window.dialog_comboBox_1.addItems((['-select workroom-'] + workroom_dict.keys()))
		window.dialog_comboBox_1.activated[str].connect(partial(self.tm_add_readers_ui_load_artist_list))
		
		# button connect
		window.select_from_list_cansel_button.clicked.connect(partial(self.close_window, window))
		window.select_from_list_apply_button.clicked.connect(partial(self.tm_add_readers_action))
		
		window.show()
		
	def tm_add_readers_ui_load_artist_list(self, workrom_name):
		table = self.selectReadersDialog.select_from_list_data_list_table
		workroom_dict = self.selectReadersDialog.workroom_dict
		
		self.clear_table(table)
		result = self.db_workroom.read_artist_of_workroom(workroom_dict[workrom_name]['id'])
		if not result[0]:
			self.message(result[1], 2)
			
		artirs_dict = result[1]
		
		# load table
		headers = ['nik_name', 'level']
		num_column = len(headers)
		num_row = 0
		if artirs_dict:
			num_row = len(artirs_dict)
				
		table.setColumnCount(num_column)
		table.setRowCount(num_row)
		table.setHorizontalHeaderLabels(headers)
		
		if artirs_dict:
			for i,reader_name in enumerate(artirs_dict):
				for j,key in enumerate(headers):
					newItem = QtGui.QTableWidgetItem()
					newItem.setText(artirs_dict[reader_name][key])
					newItem.reader_name = reader_name
					
					if key == 'nik_name':
						color = self.artist_color
						brush = QtGui.QBrush(color)
						newItem.setBackground(brush)
					if self.current_readers_list:
						if reader_name in self.current_readers_list.keys():
							color = self.grey_color
							brush = QtGui.QBrush(color)
							newItem.setBackground(brush)
						
					table.setItem(i, j, newItem)
	
	def tm_add_readers_action(self):
		table = self.selectReadersDialog.select_from_list_data_list_table
		
		readers = []
		items = table.selectedItems()
		for item in items:
			name = item.reader_name
			if not name in readers:
				if self.current_readers_list:
					if not name in self.current_readers_list.keys():
						readers.append(name)
				else:
					readers.append(name)
				
		if not readers:
			self.message('Not Selected Artists!', 2)
			return
			
		# edit task data
		result = self.db_chat.add_readers(self.current_project, self.current_task, readers)
		if not result[0]:
			self.message(result[1], 2)
			
		self.current_readers_list = result[1]
		
		# reload widgets
		# -- task_list
		if result[2]:
			self.tm_reload_task_list()
		else:
			print('*'*25)
			# -- 
			table = self.myWidget.task_manager_table
			edit_task_data = dict(table.currentItem().task)
			edit_task_data['readers'] = json.dumps(self.current_readers_list)
			table.currentItem().task = edit_task_data
		
		# -- readers list
		self.tm_load_readers_list()
		
		# -- readers editor list
		self.tm_edit_readers_ui_reload_table()
		
		# -- workroom list
		workrom_name = self.selectReadersDialog.dialog_comboBox_1.currentText()
		self.tm_add_readers_ui_load_artist_list(workrom_name)
	
	def tm_remove_reader_action(self):
		ask = self.message('Are you sure you want to delete these readers?', 0)
		if not ask:
			return
		
		table = self.editReadersDialog.select_from_list_data_list_table
		
		readers = []
		items = table.selectedItems()
		
		for item in items:
			name = item.reader_name
			if not name in readers:
				readers.append(name)
				
		if not readers:
			self.message('Not Selected Artists!', 2)
			return
		
		# edit task data
		result = self.db_chat.remove_readers(self.current_project, self.current_task, readers)
		if not result[0]:
			self.message(result[1], 2)
			
		self.current_readers_list = result[1]
		
		# reload widgets
		# -- task_list
		if result[2]:
			self.tm_reload_task_list()
		else:
			# -- 
			table = self.myWidget.task_manager_table
			edit_task_data = dict(table.currentItem().task)
			edit_task_data['readers'] = json.dumps(self.current_readers_list)
			table.currentItem().task = edit_task_data
			
		# -- readers list
		self.tm_load_readers_list()
		
		# -- readers editor list
		self.tm_edit_readers_ui_reload_table()
		
	def tm_make_first_reader(self, table):
		
		name = table.currentItem().reader_name
		
		result, data = self.db_chat.make_first_reader(self.current_project, self.current_task, name)
		if not result:
			self.message(data, 3)
			return
			
		self.current_readers_list = data
		
		# edit data in tm_table
		tm_table = self.myWidget.task_manager_table
		edit_task_data = dict(tm_table.currentItem().task)
		edit_task_data['readers'] = json.dumps(self.current_readers_list)
		tm_table.currentItem().task = edit_task_data
	
		self.tm_edit_readers_ui_reload_table()
		self.tm_load_readers_list()
		
		
	# ---- look file ----------------
	def tm_look_file_action(self):
		# get item
		item = self.myWidget.task_manager_table.currentItem()
		task_data = item.task
		
		#print(json.dumps(dict(task_data), sort_keys = True, indent = 4))
		
		result = self.db_chat.get_final_file_path(self.current_project, task_data)
		if not result[0]:
			return(False, result[1])
		
		open_path = result[1]
				
		if not open_path:
			self.message('Not Saved Version!', 2)
			return(False, 'Not Saved Version!')
		
		# get tmp_file_path
		tmp_path = self.db_chat.tmp_folder
		tmp_file_name = task_data['task_name'].replace(':','_', 2) + '_' + hex(random.randint(0, 1000000000)).replace('0x', '') + task_data['extension']
		tmp_file_path = os.path.join(tmp_path, tmp_file_name)
		
		# copy to tmp
		shutil.copyfile(open_path, tmp_file_path)
				
		# open file
		soft = self.db_studio.soft_data[task_data['extension']]
		cmd = '\"%s\" \"%s\"' % (soft, tmp_file_path)
		print(cmd)
		print('$PATH:', os.environ['PATH'])
		
		subprocess.Popen(cmd, shell = True)
		#os.system(cmd)
		
		
	def tm_look_version_file_ui(self):
		item = self.myWidget.task_manager_table.currentItem()
		self.current_task = item.task
		
		#get versions_list
		result = self.db_log.get_push_logs(self.current_project, self.current_task)
		if not result[0]:
			G.versions_list = []
			self.message('Not Versions of Activity!', 2)
			return
		else:
			G.versions_list = result[1]
			
		print(len(G.versions_list))
		
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
		window.setWindowTitle('Look Version')
		window.select_from_list_apply_button.clicked.connect(partial(self.tm_look_version_file_action, window))
				
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
		
		
	def tm_look_version_file_action(self, window):
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
		result = self.db_chat.get_version_file_path(self.current_project, self.current_task, version)
		if not result[0]:
			print("*"*50, result[1])
			self.message('No read file path of this version! Look console', 2)
			return(False, result[1])
			
		open_path = result[1]
		
		if not open_path:
			return(False, 'Not Saved Version!')
			
		# get tmp_file_path
		task_data = self.current_task
		tmp_path = self.db_chat.tmp_folder
		tmp_file_name = task_data['task_name'].replace(':','_', 2) + '_' + hex(random.randint(0, 1000000000)).replace('0x', '') + task_data['extension']
		tmp_file_path = os.path.join(tmp_path, tmp_file_name)
		
		# copy to tmp
		shutil.copyfile(open_path, tmp_file_path)
				
		# open file
		soft = self.db_studio.soft_data[task_data['extension']]
		#cmd = soft + " \"" + tmp_file_path + "\""
		cmd = "\"" + soft + "\"  \"" + tmp_file_path + "\""
		subprocess.Popen(cmd, shell = True)

		
	# ---- accept task --------------
	def tm_accept_task_action(self):
		# get item
		item = self.myWidget.task_manager_table.currentItem()
		
		# change task
		ask = self.message(('Do you want to accept the task: %s ?') % item.task['task_name'], 0)
		if not ask:
			return
		
		# get readers
		readers = {}
		try:
			readers = json.loads(item.task['readers'])
		except:
			pass
		
		# accept task
		result = None
		if self.artist.nik_name in readers:
			result = self.db_chat.readers_accept_task(self.current_project, item.task, self.artist.nik_name)
		else:
			result = self.db_chat.accept_task(self.current_project, item.task)
		
		if not result[0]:
			self.message(result[1], 2)
			#return #to reload the page in the accident with the publish!
			
		# reload table
		self.tm_reload_task_list()
		
		''' pablish in edit_db.py
		# **************** PUBLISH ********************************
		result = self.publish.publish(self.current_project, item.task)
		if not result[0]:
			self.message(result[1], 2)
			return
		'''
		
	# ---- close task --------------
	def tm_close_task_action(self):
		# get item
		item = self.myWidget.task_manager_table.currentItem()
		
		# change task
		ask = self.message(('Do you want to close the task: ' + item.task['task_name'] + ' ?'), 0)
		if ask:
			result = self.db_chat.close_task(self.current_project, item.task)
			if not result[0]:
				self.message(result[1], 2)
				return
		# reload table
		self.tm_reload_task_list()
	
	# ----- to rework task --------------
	def tm_rework_action(self):
		# get item
		item = self.myWidget.task_manager_table.currentItem()
		
		# change task
		ask = self.message(('Do you want to Rework the task: ' + item.task['task_name'] + ' ?'), 0)
		if ask:
			result = self.db_chat.rework_task(self.current_project, item.task, current_user = self.artist.nik_name)
			if not result[0]:
				if result[1] == 'not chat!':
					self.message('no posts in the chat!', 2)
					self.chat_ui()
					return
				self.message(result[1], 2)
				return
		# reload table
		self.tm_reload_task_list()
		
	# ---- return a job -------------
	def tm_return_a_job_action(self):
		# get item
		item = self.myWidget.task_manager_table.currentItem()
		
		# change task
		ask = self.message(('Do you want to return a job the task: ' + item.task['task_name'] + ' ?'), 0)
		if ask:
			result = self.db_chat.return_a_job_task(self.current_project, item.task)
			if not result[0]:
				self.message(result[1], 2)
				return
		# reload table
		self.tm_reload_task_list()
			
	# ---- change activity ----------
			
	def tm_change_task_activity_ui(self, *args):
		# get item
		item = self.myWidget.task_manager_table.currentItem()
				
		# get list of activity
		#copy = db.asset()
		activity_list = self.db_asset.activity_folder[self.current_group['type']].keys()
		activity_list.sort()
		
		# create window
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.combo_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.changeActivityWindow = loader.load(file, self)
		file.close()
		
		# edit window
		window.setWindowTitle(('Change Activity of Task: \'' + item.task['task_name'] + '\"'))
		window.combo_dialog_label.setText('Select Activity:')
		window.combo_dialog_combo_box.addItems(activity_list)
		window.combo_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.combo_dialog_ok.clicked.connect(partial(self.tm_change_task_activity_action, window, item))
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()
		
	def tm_change_task_activity_action(self, window, item_):
		# get new activity
		new_activity = window.combo_dialog_combo_box.currentText()
				
		# change activity
		task_data = dict(item_.task)
		#copy = self.db_chat
		result = self.db_chat.change_activity(self.current_project, task_data, new_activity)
		if not result[0]:
			self.message(result[1], 2)
			return
		
		# change table
		task_data['activity'] = new_activity
		item_.task = task_data
		self.myWidget.tm_data_label_2.setText(new_activity)
		
		self.close_window(window)
		
	# ------ change workroom --------------
	
	def tm_change_task_workroom_ui(self, *args):
		# get item
		item = self.myWidget.task_manager_table.currentItem()
				
		# get list of activity
		copy = self.db_workroom
		result = copy.get_list_workrooms(DICTONARY = 'by_name')
		if not result[0]:
			self.message(result[1], 2)
			return
		workroom_list = result[1].keys()
		workroom_list.sort()
		
		# create window
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.combo_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.changeActivityWindow = loader.load(file, self)
		file.close()
		
		# edit window
		window.setWindowTitle(('Change Workroom of Task: \'' + item.task['task_name'] + '\"'))
		window.combo_dialog_label.setText('Select WorkRoom:')
		window.combo_dialog_combo_box.addItems(workroom_list)
		window.combo_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.combo_dialog_ok.clicked.connect(partial(self.tm_change_task_workroom_action, window, item))
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()
		
	def tm_change_task_workroom_action(self, window, item_):
		# get new workroom
		new_workroom = window.combo_dialog_combo_box.currentText()
				
		# change workroom
		task_data = dict(item_.task)
		copy = self.db_chat # db_task
		result = copy.change_workroom(self.current_project, task_data, new_workroom)
		if not result[0]:
			self.message(result[1], 2)
			return
			
		new_workroom_id = result[1]
		
		# change table
		task_data['workroom'] = new_workroom_id
		item_.task = task_data
		self.myWidget.tm_data_label_3.setText(new_workroom)
		
		self.close_window(window)
	
	# ------ change price --------------
	
	def tm_change_task_price_ui(self, *args):
		# get item
		item = self.myWidget.task_manager_table.currentItem()
				
		# create window
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.new_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.changeActivityWindow = loader.load(file, self)
		file.close()
		
		# edit window
		window.setWindowTitle(('Change Price of Task: \'' + item.task['task_name'] + '\"'))
		window.new_dialog_label.setText('Select WorkRoom:')
		window.new_dialog_name.setText(str(item.task['price']))
		window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.new_dialog_ok.clicked.connect(partial(self.tm_change_task_price_action, window, item))
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		window.show()
		
	def tm_change_task_price_action(self, window, item_):
		# get new workroom
		new_price = float(window.new_dialog_name.text())
				
		# change workroom
		task_data = dict(item_.task)
		copy = self.db_chat # db_task
		result = copy.change_price(self.current_project, task_data, new_price)
		if not result[0]:
			self.message(result[1], 2)
			return
			
		# change table
		task_data['price'] = new_price
		item_.task = task_data
		self.myWidget.tm_data_label_5.setText(str(new_price))
		
		self.close_window(window)
		
	# ------ change artist --------------
	
	def tm_change_task_artist_ui(self, *args):
		# get item
		item = self.myWidget.task_manager_table.currentItem()
		
		# task workroom
		task_workroom = item.task['workroom']
				
		# get list of active artists
		result = self.db_workroom.read_artist({'status':'active'})
		if not result[0]:
			self.message(result[1], 2)
			return
		active_artists_list = []
		for row in result[1]:
			if row['workroom']:
				artist_workrooms = json.loads(row['workroom'])
				if task_workroom in artist_workrooms:
					active_artists_list.append(row['nik_name'])
			else:
				continue
		
		active_artists_list.sort()
		active_artists_list.insert(0, '-None-')
		
		# create window
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.combo_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.changeActivityWindow = loader.load(file, self)
		file.close()
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		# edit window
		window.setWindowTitle(('Change Artist of Task: \'' + item.task['task_name'] + '\"'))
		window.combo_dialog_label.setText('Select Artist:')
		window.combo_dialog_combo_box.addItems(active_artists_list)
		window.combo_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.combo_dialog_ok.clicked.connect(partial(self.tm_change_task_artist_action, window, item))
		
		window.show()
		
	def tm_change_task_artist_action(self, window, item_):
		# get new artist
		new_artist = window.combo_dialog_combo_box.currentText()
		if new_artist in ['None', '-None-']:
			new_artist = ''
		
		# change artist
		task_data = dict(item_.task)
		result = self.db_chat.change_artist(self.current_project, task_data, new_artist)
		if not result[0]:
			self.message(result[1], 2)
			return
		new_status = result[1][0]
		outsource = result[1][1]
		#print(new_status)
		
		# edit labels
		self.myWidget.tm_data_label_1.setText(new_artist)
		task_data['artist'] = new_artist
		if new_status:
			task_data['status'] = new_status
		task_data['outsource'] = outsource
		item_.task = task_data
		
		# change table color
		rgb = self.db_chat.color_status[task_data['status']]
		r = (rgb[0]*255)
		g = (rgb[1]*255)
		b = (rgb[2]*255)
		color = QtGui.QColor(r, g, b)
		brush = QtGui.QBrush(color)
		item_.setBackground(brush)
		
		self.close_window(window)
		
	# ------ change input --------------
	
	def tm_change_task_input_ui(self, *args):
		# get item
		item = self.myWidget.task_manager_table.currentItem()
				
		# get task list
		task_list = []
		result = self.db_chat.get_list(self.current_project, item.task['asset_id'])
		if result[0]:
			task_list = result[1]
			
		task_name_list = ['None']
		for task in task_list:
			if task['task_name'].replace((task['asset'] + ':'),'') == 'final':
				continue
			elif task['task_name'] == item.task['task_name']:
				continue
			task_name_list.append(task['task_name'])
		
		print(task_name_list)
		
		
		# create window
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.combo_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.changeActivityWindow = loader.load(file, self)
		file.close()
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		# edit window
		window.setWindowTitle(('Change Input Task: \'' + item.task['task_name'] + '\"'))
		window.combo_dialog_label.setText('Select Task:')
		window.combo_dialog_combo_box.addItems(task_name_list)
		window.combo_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.combo_dialog_ok.clicked.connect(partial(self.tm_change_task_input_action, window, item))
		
		window.show()
		
	def tm_change_task_input_action(self, window, item_):
		# get input task
		input_task = window.combo_dialog_combo_box.currentText()
		if input_task == 'None':
			input_task = False
					
		# change input
		result = self.db_chat.change_input(self.current_project, item_.task, input_task)
		if not result[0]:
			self.message(result[1], 2)
			return
			
		new_status = result[1][0]
		old_input_task_data = result[1][1]
		new_input_task_data = result[1][2]
		
		# edit table
		task_data = dict(item_.task)
		if new_status:
			task_data['status'] = new_status
			# change table color
			rgb = self.db_chat.color_status[new_status]
			r = (rgb[0]*255)
			g = (rgb[1]*255)
			b = (rgb[2]*255)
			color = QtGui.QColor(r, g, b)
			brush = QtGui.QBrush(color)
			item_.setBackground(brush)
		if new_input_task_data:
			task_data['input'] = new_input_task_data['task_name']
		else:
			task_data['input'] = ''
		item_.task = task_data
		
		# edit label
		self.myWidget.tm_data_label_4.setText(task_data['input'])
		
		
		self.close_window(window)
		
	# ------ change task type ------------
	def tm_change_task_type_ui(self):
		# create window
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.combo_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.changeActivityWindow = loader.load(file, self)
		file.close()
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		# edit window
		content_list = self.db_studio.task_types
		content_list.sort()
		window.setWindowTitle(('Change Task Type: \'' + self.current_task['task_name'] + '\"'))
		window.combo_dialog_label.setText('Select Task Type:')
		window.combo_dialog_combo_box.addItems(content_list)
		try:
			window.combo_dialog_combo_box.setCurrentIndex(content_list.index(self.current_task['task_type']))
		except:
			pass
		window.combo_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.combo_dialog_ok.clicked.connect(partial(self.tm_change_task_type_action, window))
		
		window.show()
		
	def tm_change_task_type_action(self, window):
		task_type = window.combo_dialog_combo_box.currentText()
		
		result = self.db_chat.changes_without_a_change_of_status('task_type', self.current_project, self.current_task, task_type)
		if not result[0]:
			self.message(result[1], 2)
			return
		
		# edit label
		self.myWidget.tm_data_label_6.setText(task_type)
		
		# get item
		item = self.myWidget.task_manager_table.currentItem()
		item.task = dict(item.task)
		item.task['task_type'] = task_type
		
		self.close_window(window)
		
	# ------ change task extension ------------
	def tm_change_task_extension_ui(self):
		# create window
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.combo_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.changeActivityWindow = loader.load(file, self)
		file.close()
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		# edit window
		content_list = self.db_studio.extensions
		content_list.sort()
		window.setWindowTitle(('Change Extension: \'' + self.current_task['task_name'] + '\"'))
		window.combo_dialog_label.setText('Select Extension:')
		window.combo_dialog_combo_box.addItems(content_list)
		try:
			window.combo_dialog_combo_box.setCurrentIndex(content_list.index(self.current_task['extension']))
		except:
			pass
		window.combo_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.combo_dialog_ok.clicked.connect(partial(self.tm_change_task_extension_action, window))
		
		window.show()
		
	def tm_change_task_extension_action(self, window):
		extension = window.combo_dialog_combo_box.currentText()
		
		result = self.db_chat.changes_without_a_change_of_status('extension', self.current_project, self.current_task, extension)
		if not result[0]:
			self.message(result[1], 2)
			return
		
		# edit label
		self.myWidget.tm_data_label_7.setText(extension)
		
		# get item
		item = self.myWidget.task_manager_table.currentItem()
		item.task = dict(item.task)
		item.task['extension'] = extension
		
		self.close_window(window)
		
	# ------- change TZ link ----------- self.new_dialog_path
	def tm_change_tz_link_ui(self):
		# create window
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(self.new_dialog_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.changeTzLinkWindow = loader.load(file, self)
		file.close()
		
		# set modal window
		window.setWindowModality(QtCore.Qt.WindowModal)
		window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		# edit window
		window.setWindowTitle(('Change Tz Link: \'' + self.current_task['task_name'] + '\"'))
		window.new_dialog_label.setText('Link:')
		window.new_dialog_name.setText(self.current_task['tz'])
		window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
		window.new_dialog_ok.clicked.connect(partial(self.tm_change_tz_link_action, window))
		
		window.show()
		
	def tm_change_tz_link_action(self, window):
		link = window.new_dialog_name.text()
		
		result = self.db_chat.changes_without_a_change_of_status('tz', self.current_project, self.current_task, link)
		if not result[0]:
			self.message(result[1], 2)
			return
		
		# edit label
		self.myWidget.tm_data_label_8.setText(link)
		
		# get item
		item = self.myWidget.task_manager_table.currentItem()
		item.task = dict(item.task)
		item.task['tz'] = link
		self.current_task = dict(self.current_task)
		self.current_task['tz'] = link
		
		self.close_window(window)
		
	# ------- make preview ----------
	def tm_make_preview_ui(self):
		self.makePreviewDialog = QtGui.QDialog(self)
		self.makePreviewDialog.setModal(True)
		#self.makePreviewDialog.resize(300, 300)
		self.makePreviewDialog.setWindowTitle(('Make Preview: /// ' + self.current_task['asset']))
		
		# add widgets
		v_layout = QtGui.QVBoxLayout()
		# -- image Label
		self.makePreviewDialog.imageLabel = QtGui.QLabel()
		self.makePreviewDialog.imageLabel.setFixedSize(300,300)
		v_layout.addWidget(self.makePreviewDialog.imageLabel)
		
		# -- button
		h__layout = QtGui.QHBoxLayout()
		button_frame = QtGui.QFrame(parent = self.makePreviewDialog)
		cansel_button = QtGui.QPushButton('Cansel', parent = button_frame)
		h__layout.addWidget(cansel_button)
		paste_button = QtGui.QPushButton('Paste', parent = button_frame)
		h__layout.addWidget(paste_button)
		save_button = QtGui.QPushButton('Save', parent = button_frame)
		h__layout.addWidget(save_button)
		button_frame.setLayout(h__layout)
		
		v_layout.addWidget(button_frame)
		self.makePreviewDialog.setLayout(v_layout)
		
		# connect buttons
		cansel_button.clicked.connect(partial(self.close_window, self.makePreviewDialog))
		paste_button.clicked.connect(partial(self.tm_paste_image_from_clipboard, self.makePreviewDialog.imageLabel))
		save_button.clicked.connect(partial(self.tm_save_preview_image_action, self.makePreviewDialog))
		
		# -- load img to label
		img_path = os.path.join(self.db_chat.preview_img_path, (self.current_task['asset'] + '.png'))
		if not os.path.exists(img_path):
			self.makePreviewDialog.imageLabel.setText('No Image')
		else:
			image = QtGui.QImage(img_path)
			self.makePreviewDialog.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image))
					
		self.makePreviewDialog.show()
	
	def tm_paste_image_from_clipboard(self, img_label):
		rand  = hex(random.randint(0, 1000000000)).replace('0x', '')
		img_path = os.path.normpath(os.path.join(self.db_chat.tmp_folder, ('tmp_image_' + rand + '.png')))
		
		clipboard = QtGui.QApplication.clipboard()
		img = clipboard.image()
		if img:
			img.save(img_path)
			cmd = '%s %s -resize 300 %s' % (os.path.normpath(self.db_chat.convert_exe), img_path, img_path)
			cmd2 = '%s %s -resize 300x300 %s' % (os.path.normpath(self.db_chat.convert_exe), img_path, img_path)
			cmd3 = '\"%s\" \"%s\" -resize 300 \"%s\"' % (os.path.normpath(self.db_chat.convert_exe), img_path, img_path)
			print(cmd)
			print(cmd2)
			print(cmd3)
			try:
				os.system(cmd)
			except:
				try:
					os.system(cmd2)
				except:
					try:
						os.system(cmd3)
					except:	
						return(False, 'in tm_paste_image_from_clipboard - problems with conversion resize.png')
		else:
			self.message('Cannot Image!', 2)
			return(False, 'Cannot Image!')
			
		image = QtGui.QImage(img_path)
		img_label.setPixmap(QtGui.QPixmap.fromImage(image))
		self.makePreviewDialog.img_path = img_path
		
		
	def tm_save_preview_image_action(self, window):
		# self.preview_img_path
		if not os.path.exists(self.db_chat.preview_img_path):
			try:
				os.mkdir(self.db_chat.preview_img_path)
			except:
				print(self.db_chat.preview_img_path)
				
		# copyfile
		save_path = os.path.join(self.db_chat.preview_img_path, (self.current_task['asset'] + '.png'))
		icon_path = os.path.join(self.db_chat.preview_img_path, (self.current_task['asset'] + '_icon.png'))
		tmp_icon_path = window.img_path.replace('.png','_icon.png')
		# -- copy
		shutil.copyfile(window.img_path, save_path)
		
		# -- resize
		cmd = '%s %s -resize 100 %s' % (os.path.normpath(self.db_chat.convert_exe), window.img_path, tmp_icon_path)
		cmd2 = '%s %s -resize 100x100 %s' % (os.path.normpath(self.db_chat.convert_exe), window.img_path, tmp_icon_path)
		cmd3 = '\"%s\" \"%s\" -resize 100 \"%s\"' % (os.path.normpath(self.db_chat.convert_exe), window.img_path, tmp_icon_path)
		try:
			os.system(cmd)
		except:
			try:
				os.system(cmd2)
			except:
				try:
					os.system(cmd3)
				except:
					self.message('problems with conversion _icon.png', 2)
					return(False, 'in tm_save_preview_image_action - problems with conversion resize.png')
				
		shutil.copyfile(tmp_icon_path, icon_path)
		
		# load to preview  image_label
		image = QtGui.QImage(save_path)
		self.myWidget.image_label.setPixmap(QtGui.QPixmap.fromImage(image))
		
		self.close_window(window)
		
	# ------ show tz ------------
	def tm_tz(self):
		if self.current_task['tz']:
			webbrowser.open_new_tab(self.current_task['tz'])
		else:
			self.message('Not Link!', 2)
		
	# ------ add task --------------
	def tm_add_task_ui(self):
		self.addTaskDialog = QtGui.QDialog(self)
		self.addTaskDialog.setModal(True)
		self.addTaskDialog.resize(500, 200)
		self.addTaskDialog.setWindowTitle(('Create Single Task to Asset: /// ' + self.current_task['asset']))
		
		# root frames
		v_layout = QtGui.QVBoxLayout()
		# -- 
		headers_frame = QtGui.QFrame(parent = self.addTaskDialog)
		# -- buttons frame
		button_frame = QtGui.QFrame(parent = self.addTaskDialog)
		# -- add frames to layout
		v_layout.addWidget(headers_frame)
		v_layout.addWidget(button_frame)
		self.addTaskDialog.setLayout(v_layout)
		
		# buttons
		h_layout = QtGui.QHBoxLayout()
		# -- buttons
		close_button = QtGui.QPushButton(parent = button_frame)
		close_button.setMaximumWidth(100)
		close_button.setText('Close')
		close_button.clicked.connect(partial(self.close_window, self.addTaskDialog))
		apply_button = QtGui.QPushButton(parent = button_frame)
		apply_button.setMaximumWidth(100)
		apply_button.setText('Create Task')
		apply_button.clicked.connect(partial(self.tm_add_task_action, self.addTaskDialog))
		# -- add buttons to layout
		h_layout.addWidget(close_button)
		h_layout.addWidget(apply_button)
		button_frame.setLayout(h_layout)
		
		# get task_list of asset
		result = self.db_chat.get_list(self.current_project, self.current_task['asset_id'])
		if not result[0]:
			self.message(result[1], 2)
			return
		task_list = result[1]
		for tsk in task_list:
			if tsk['task_type'] == 'service':
				#print(tsk['task_name'].split(':')[1][:5])
				if tsk['task_name'].split(':')[1][:5] == 'final':
					task_list.remove(tsk)
		
		# -- Labels <-> Fields
		self.addTaskDialog.new_task_data = {}
		
		hh_layout = QtGui.QGridLayout()
		headers = ['task_name', 'input', 'output', 'activity', 'workroom', 'task_type', 'planned_time','price','tz', 'extension']
		for i, head in enumerate(headers):
			label = QtGui.QLabel(head, parent = headers_frame)
			line = QtGui.QLineEdit(parent = headers_frame)	
			# -- line context menu
			if head in ['input', 'output', 'activity', 'workroom', 'task_type', 'extension']:
				textes = []
				if head == 'activity':
					textes = self.db_chat.activity_folder[self.current_task['asset_type']].keys()
				elif head == 'extension':
					textes = self.db_chat.extensions
				elif head == 'workroom':
					textes = self.workrooms
				elif head == 'task_type':
					textes = self.db_chat.task_types
				elif head == 'input':
					textes = ['None']
					for task_ in task_list:
						textes.append(task_['task_name'])
				elif head == 'output':
					textes = ['None']
					for tsk_ in task_list:
						if tsk_['task_type'] != 'service':
							textes.append(tsk_['task_name'])
				line.setReadOnly(True)
				for text in textes:
					# context menu
					line.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
					addgrup_action = QtGui.QAction( (text), self.myWidget)
					addgrup_action.triggered.connect(partial(self.tm_set_text, line, text))
					line.addAction( addgrup_action )
			
			hh_layout.addWidget(label, i, 0)
			hh_layout.addWidget(line, i, 1)
			
			if head == 'task_type':
				help_button = QtGui.QPushButton('Help', parent = headers_frame)
				help_button.setMaximumWidth(50)
				hh_layout.addWidget(help_button, i, 2)
				
			self.addTaskDialog.new_task_data[head] = line
				
		headers_frame.setLayout(hh_layout)
		
		self.addTaskDialog.show()
		
	def tm_set_text(self, widget, text):
		widget.setText(text)
	
	def tm_add_task_action(self, dialog):
		task_keys = {}
		task_keys['asset'] = self.current_task['asset']
		task_keys['asset_id'] = self.current_task['asset_id']
		task_keys['asset_type'] = self.current_task['asset_type']
		task_keys['asset_path'] = self.current_task['asset_path']
		
		required_keys = ['task_name', 'activity', 'workroom', 'task_type', 'extension']
		for key in dialog.new_task_data:
			# test exists fields
			if key in required_keys and not dialog.new_task_data[key].text():
				self.message(('Not Key Data: ' + key), 2)
				return
			# remove 'spaces'
			if not key in ['workroom']:
				task_keys[key] = dialog.new_task_data[key].text().replace(' ','_')
			else:
				task_keys[key] = dialog.new_task_data[key].text()
		
		# test input <-> output
		if task_keys['input'] == task_keys['output'] and (task_keys['input'] != '' and task_keys['input'] != 'None'):
			self.message('Input and Output Match!', 2)
			return
			
		# edit input <-> output
		if task_keys['output'] == 'None':
			task_keys['output'] = json.dumps([])
		elif not task_keys['output']:
			task_keys['output'] = json.dumps([])
		else:
			task_keys['output'] = json.dumps([task_keys['output']])
		if task_keys['input'] == 'None':
			task_keys['input'] = ''
			
		# edit task_name
		task_keys['task_name'] = task_keys['asset'] + ':' + task_keys['task_name']
			
		# create
		result = self.db_chat.add_single_task(self.current_project, task_keys)
		if not result[0]:
			self.message(result[1], 2)
			return
		else:
			self.close_window(dialog)
			self.tm_reload_task_list()
					
	# *********************** SETTING ****************************************************
    
	def help_user_manual(self):
		webbrowser.open_new_tab('http://www.lineyka.org.ru/')
		#print("go to user manual!")

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
			h_layout.addWidget(line)
			line.returnPressed.connect(partial(self.set_exe_string, line, key))
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
		folder = QtGui.QFileDialog.getExistingDirectory(self, dir = home)
		
		if folder:
			self.setWindow.set_studio_field.setText(str(folder))
			#return
			# set studio path
			copy = self.db_studio
			result = copy.set_studio(folder)
			if not result[0]:
				self.message(result[1], 2)
          
		# finish
		print('set studio folder')
    
	def set_tmp_path_action(self):
		# get path
		home = os.path.expanduser('~')
		folder = QtGui.QFileDialog.getExistingDirectory(self, dir = home)
		
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
		#copy = db.artist()

		nik_name = self.loginWindow.login_nik_name_field.text()
		password = self.loginWindow.login_password_field.text()

		login = self.artist.login_user(nik_name, password)
    
		if login[0]:
			self.loginWindow.close()
		else:
			self.message(login[1], 2)
			return
			
		# ---- get artist data
		self.get_artist_data(read=False)
		    
		# finish
		self.tm_fill_project_list()
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
		
		# get Data
		data = {
		'nik_name' : self.myWidget.registrWindow.nik_name_field.text(),
		'password' : self.myWidget.registrWindow.password_field.text(),
		'email' : self.myWidget.registrWindow.email_field.text(),
		'phone' : self.myWidget.registrWindow.phone_field.text(),
		'speciality' : self.myWidget.registrWindow.specialty_field.text(),
		'status' : 'active'
		}
    
		# add artist
		result = self.artist.add_artist(data)
		if result[0]:
			self.myWidget.registrWindow.close()
		else:
			self.message(result[1], 2)
			return
		
		self.get_artist_data(read = False)
		
		# finish
		self.reload_artist_list()
		self.tm_fill_project_list()
		print('user registration action')
    
	#*********************** UTILITS ******************************************* 
	def get_list_active_projects(self):
		self.db_studio.get_list_projects()
		self.list_active_projects = self.db_studio.list_active_projects
	
	def set_self_workrooms(self, workrooms = False):
		self.workrooms = []
		if not workrooms:
			copy = self.db_workroom
			workrooms = copy.get_list_workrooms()
			
			if not workrooms[0]:
				return
		
		for row in workrooms[1]:
			self.workrooms.append(row['name'])
			
	
	def get_artist_data(self, read = True):
		# ---- get artist data
		#artist_row = None
		if read:
			result = self.artist.get_user()
			if result[0]:
				#artist_row = result[1][3]
				#self.current_user = artist_row['nik_name']
				self.current_user = self.artist.nik_name
			else:
				self.message(result[1], 2)
			try:
				self.setWindowTitle(('Lineyka  ' + self.artist.nik_name))
			except:
				self.setWindowTitle('Lineyka  Not User!')
		else:
			self.current_user = self.artist.nik_name
			self.setWindowTitle(('Lineyka  ' + self.artist.nik_name))
	
	def close_window(self, window):
		if window:
			window.close()
	
	def clear_table(self, table = False):
		if not table:
			table = self.myWidget.studio_editor_table
		
		# -- clear table
		num_row = table.rowCount()
		num_column = table.columnCount()
		
		# old
		'''
		for i in range(0, num_row):
			for j in range(0, num_column):
				item = self.myWidget.studio_editor_table.item(i, j)
				self.myWidget.studio_editor_table.takeItem(i, j)

				#self.myWidget.studio_editor_table.removeCellWidget(i, j)
		'''
		
		# new
		table.clear()
		table.setColumnCount(0)
		table.setRowCount(0)
				
	
	def message(self, m, i):
		#m = str(m)
		
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
      
	def print_data(self, *args):
		print(args[0])
		
    
app = QtGui.QApplication(sys.argv)
mw = MainWindow()
mw.show()
app.exec_()
