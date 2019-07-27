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
import uuid
import subprocess
import datetime
'''
import ui
import edit_db as db
'''

class lineyka_chat:
	
	#def chat_ui(self, root):
	def __init__(self, MW):
		self.MW = MW
		
		self.selected_task = MW.selected_task
		try:
			self.db_artist = MW.db_artist
		except:
			self.db_artist = MW.artist
		self.db_chat = MW.db_chat
		self.db_chat.task = self.selected_task
		
		self.chat_status = MW.chat_status
		self.chat_add_topic_path = MW.chat_add_topic_path
		#self.chatAddTopic = MW.chatAddTopic
		
		self.message = MW.message
		self.close_window = MW.close_window
		
		# page
		self.topics=None
		self.page=1
		self.num_topics = 10
		
		# make widjet
		ui_path = MW.chat_main_path
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(ui_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = self.chatMain = loader.load(file, MW)
		file.close()
		
		# fill meta data
		window.setWindowTitle('Lineyka Chat')
		window.chat_nik_name_label.setText(self.db_artist.nik_name)
		window.chat_asset_name_label.setText(self.db_chat.task.asset.name)
		window.chat_task_name_label.setText(self.db_chat.task.task_name.split(':')[1])
		
		# button connect
		window.close_button.clicked.connect(partial(self.close_window, window))
		window.reload_button.clicked.connect(partial(self.chat_load_topics, window, True))
		window.chat_add_topic_button.clicked.connect(partial(self.chat_new_topic_ui, window))
		
		# add button '\u9758'
		#root_layout = window.buttonVerticalLayout
		#layout = QtGui.QHBoxLayout()
		#root_layout.addLayout(layout)
		layout=window.pagesHorizontalLayout
		
		# widgets
		pages_label = QtGui.QLabel()
		next_button = QtGui.QPushButton(u'\u25B6')
		next_button.setFlat(True)
		next_button.clicked.connect(partial(self.flipping_page, 'next', pages_label, window))
		previous_button = QtGui.QPushButton(u'\u25C0')
		previous_button.setFlat(True)
		previous_button.clicked.connect(partial(self.flipping_page, 'previous', pages_label, window))
		#
		label2 = QtGui.QLabel('Per page:')
		#
		num_field = QtGui.QLineEdit()
		num_field.setMaxLength(3)
		num_field.setValidator(QtGui.QIntValidator(1, 100))
		num_field.setText(unicode(self.num_topics))
		num_field.textChanged.connect(partial(self.rebild_size_pages, window, pages_label))
		
		#
		layout.addWidget(label2)
		layout.addWidget(num_field)
		layout.addWidget(previous_button)
		layout.addWidget(pages_label)
		layout.addWidget(next_button)
				
		window.show()
		
		self.chat_load_topics(window, reload_db=True)
		
		pages_label.setText('%s / %s' % (str(self.page), self.max_pages))
		
		print(self.chat_status)
		
		window.rejected.connect(partial(self.MW.chat_close, MW))
		
		'''
		# edit read_status
		if self.chat_status == 'manager':
			result = self.db_chat.task_edit_rid_status_read(project, task_data, nik_name)
			if not result[0]:
				self.message(result[1], 2)
				return
		'''
		
	def rebild_size_pages(self, *args):
		pass
		#print(args)
		#return
		num = int(args[2])
		if not num:
			return
		self.num_topics=num
		self.page=1
		self.chat_load_topics(args[0])
		args[1].setText('%s / %s' % (str(self.page), self.max_pages))
	
	def flipping_page(self, action, label, window):
		pass
		if action == 'next':
			#
			if self.page<self.max_pages:
				self.page+=1
				label.setText('%s / %s' % (str(self.page), self.max_pages))
		elif action == 'previous':
			if self.page>1:
				self.page-=1
				label.setText('%s / %s' % (str(self.page), self.max_pages))
				
		self.chat_load_topics(window, )
		
	def chat_load_topics(self, window, reload_db=False):
		pass
		
		# read chat data
		topics = None
		
		if reload_db:
			result = self.db_chat.read_the_chat(sort_key='date_time', reverse=True)
			if not result[0]:
				#self.message(result[1], 2)
				pass
			else:
				topics = result[1]
				#topics = sorted(result[1], key=lambda x: x['date_time'], reverse=True)
				self.topics = topics
				#
		else:
			topics=self.topics
		
		if topics is None:
			self.max_pages=1
		else:
			self.max_pages = len(topics)//self.num_topics
			if len(topics) % self.num_topics:
				self.max_pages+=1
		
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
			#for topic in topics:
			for i in range(0, self.num_topics):
				pass
				# pages
				num = i+((self.page-1)*self.num_topics)
				if num >= len(topics):
					break
				topic = topics[num]
				
				#dt = topic['date_time']
				#date = str(dt.year) + '/' + str(dt.month) + '/' + str(dt.day) + '/' + str(dt.hour) + ':' + str(dt.minute)
				date = topic['date_time'].strftime("%m/%d/%Y, %H:%M:%S")
				header = '%s     %s'  % (date, topic['author'])
				
				#lines = json.loads(topic['topic'])
				lines = topic['topic']
				
				topic_widget = QtGui.QFrame()
				v_layout = QtGui.QVBoxLayout()
				for key in lines:
					widget = QtGui.QFrame(parent = topic_widget)
					layout = QtGui.QHBoxLayout()
					# button
					if lines[key][1]:
						button = QtGui.QPushButton(QtGui.QIcon(lines[key][1]), '', parent = widget)
						button.setFlat(True)
					else:
						button = QtGui.QPushButton('not Image', parent = widget)
						button.setFlat(True)
					button.setIconSize(QtCore.QSize(100, 100))
					button.setFixedSize(100, 100)
					button.img_path = lines[key][0]
					button.clicked.connect(partial(self.chat_image_view_ui, button))
					layout.addWidget(button)
					
					# text field
					text_field = QtGui.QTextEdit(lines[key][2], parent = widget)
					text_field.setMaximumHeight(100)
					text_field.setFrameStyle(0)
					layout.addWidget(text_field)
					
					widget.setLayout(layout)
					#print(widget.sizeHint())
					
					v_layout.addWidget(widget)
				topic_widget.setLayout(v_layout)
				topic_widget.topic = topic
				#self.changeable_message = topic
				
				#
				if topic['author'] == self.db_artist.nik_name:
					topic_widget.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
					addgrup_action = QtGui.QAction( 'Edit messege', window)
					addgrup_action.triggered.connect(partial(self.chat_edit_topic_ui, topic_widget))
					#addgrup_action.triggered.connect(partial(self.chat_edit_topic_ui))
					topic_widget.addAction( addgrup_action )
							
				tool_box.addItem(topic_widget, header)
				
	def chat_edit_topic_ui(self, in_widget):
		print(in_widget.topic['message_id'])
		
		# make widjet
		ui_path = self.chat_add_topic_path
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(ui_path)
		#file.open(QtCore.QFile.ReadOnly)
		edit_window = self.chatEditTopic = loader.load(file, self.MW)
		file.close()
		
		#
		edit_window.setWindowTitle('Edit Message')
		
		# set modal window
		edit_window.setWindowModality(QtCore.Qt.WindowModal)
		edit_window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		edit_window.line_data = {}
		
		# V
		v_layout = QtGui.QVBoxLayout()
		lines = in_widget.topic['topic']
		for i, key in enumerate(lines.keys()):
			widget = QtGui.QFrame(parent = edit_window.new_topics_frame)
			layout = QtGui.QHBoxLayout()
			# button
			if lines[key][1]:
				button = QtGui.QPushButton(QtGui.QIcon(lines[key][1]), '', parent = widget)
				button.setFlat(True)
			else:
				button = QtGui.QPushButton('not Image', parent = widget)
				button.setFlat(True)
			button.setIconSize(QtCore.QSize(100, 100))
			button.setFixedSize(100, 100)
			button.img_path = lines[key][0]
			button.clicked.connect(partial(self.chat_image_view_ui, button))
			# context
			button.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
			addgrup_action = QtGui.QAction( 'Inser Image From Clipboard', edit_window)
			addgrup_action.triggered.connect(partial(self.chat_add_img_to_line, button))
			button.addAction( addgrup_action )
			
			layout.addWidget(button)
			
			# text field
			text_field = QtGui.QTextEdit(lines[key][2], parent = widget)
			text_field.setMaximumHeight(100)
			text_field.setFrameStyle(0)
			layout.addWidget(text_field)
			
			widget.setLayout(layout)
			#print(widget.sizeHint())
						
			v_layout.addWidget(widget)
			
			edit_window.line_data[str(i)] = (button, text_field)
		
		edit_window.new_topics_frame.setLayout(v_layout)
		
		# connect button
		edit_window.cansel_button.clicked.connect(partial(self.close_window, edit_window))
		edit_window.add_line_button.clicked.connect(partial(self.chat_add_line_to_message, edit_window, v_layout))
		edit_window.send_message_button.clicked.connect(partial(self.chat_new_topic_action, edit_window, self.chat_status, message_id=in_widget.topic['message_id']))
		
		
		edit_window.show()
	
	def chat_new_topic_ui(self, window):
		pass
		# make widjet
		ui_path = self.chat_add_topic_path
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(ui_path)
		#file.open(QtCore.QFile.ReadOnly)
		add_window = self.chatAddTopic = loader.load(file, self.MW)
		file.close()
		
		#
		add_window.setWindowTitle('New Message')
		
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
		button.setFlat(True)
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
		text_field.setFrameStyle(0)
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
		rand  = uuid.uuid4().hex
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
		ui_path = self.MW.chat_img_viewer_path
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(ui_path)
		#file.open(QtCore.QFile.ReadOnly)
		img_window = self.MW.chatImgViewer = loader.load(file, self.MW)
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
		pass
		# H
		h_layout = QtGui.QHBoxLayout()
		line_frame = QtGui.QFrame(parent = add_window.new_topics_frame)
		# button
		button = QtGui.QPushButton('img', parent = line_frame)
		button.setFixedSize(100, 100)
		button.img_path = False
		button.setFlat(True)
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
		text_field.setFrameStyle(0)
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
		
	def chat_new_topic_action(self, add_window, status, message_id=False):
		nik_name = self.db_artist.nik_name
		
		# get color
		if status == 'manager' or status == 'manager_to_outsource':
			color = self.db_chat.color_status['checking']
		elif status == 'user' or status == 'user_outsource':
			color = self.db_chat.color_status['work']
		else:
			color = self.db_chat.color_status['done']
			
		message = {}
		line_data = add_window.line_data
		for key in line_data:
			# GET Img
			tmp_img_path = line_data[key][0].img_path
			
			if tmp_img_path and os.path.exists(tmp_img_path):
				icon_tmp_img_path = tmp_img_path.replace('.png', '_icon.png')
				
				# -- copy to img_path
				rand  = uuid.uuid4().hex
				img_path = os.path.normpath(os.path.join(self.db_chat.task.asset.project.chat_img_path, (self.db_chat.task.task_name.replace(':','_') + rand + '.png')))
				shutil.copyfile(tmp_img_path, img_path)
				
				# -- make icon
				icon_path = img_path.replace('.png', '_icon.png')
				cmd = self.db_chat.convert_exe + ' \"' + tmp_img_path + '\" -resize 100 \"' + icon_tmp_img_path + '\"'
				
				os.system(cmd)
				shutil.copyfile(icon_tmp_img_path, icon_path)
				
				'''
				try:
					os.system(cmd)
				except:
					G.MW.message('in chat_new_topic_action - problems with conversion icon.png', 2)
					#return(False, 'in chat_new_topic_action - problems with conversion icon.png')
					return
				'''
			else:
				img_path = False
				icon_path = False
				
			# GET Text
			text = line_data[key][1].toPlainText()
			
			# append message
			message[key] = (img_path, icon_path, text)
		
		#topic = json.dumps(message, sort_keys=True, indent=4)
		
		# save message 
		chat_keys = {
		'author':nik_name,
		'color':color,
		'topic':message,
		'status':status,
		'reading_status': 'none',
		}
		if message_id:
			result= self.db_chat.edit_message(message_id, chat_keys, artist_ob=self.db_artist)
		else:
			result = self.db_chat.record_messages(chat_keys, self.db_artist)
		if not result[0]:
			self.message(result[1], 2)
			return
		else:
			print(result[1])
			self.close_window(add_window)
			self.chat_load_topics(self.chatMain, reload_db=True)
		'''
		# edit read_status
		if self.chat_status == 'user':
			result = self.db_chat.task_edit_rid_status_unread(project, task_data)
			if not result[0]:
				self.message(result[1], 2)
				return
		'''
		
	def chat_edit_topic_action(self, add_window, status):
		pass
