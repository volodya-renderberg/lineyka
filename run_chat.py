#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PySide import QtCore, QtGui, QtUiTools, QtSql
import os
import json

import ui
import edit_db as db
import lineyka_chat

class MainWindow(QtGui.QMainWindow):
	def __init__(self, task, parent = None):
		path = os.path.dirname(ui.__file__)
		self.chat_main_path = os.path.join(path, "chat_dialog.ui")
		self.chat_add_topic_path = os.path.join(path, "chat_add_topic.ui")
		self.chat_img_viewer_path = os.path.join(path, "chat_img_viewer.ui")
		
		#self.app = app
		
		self.selected_task = task
		self.db_chat = db.chat(self.selected_task)
		self.artist = db.artist()
		self.artist.get_user()
		
		self.chat_status = 'user'
		
		# create widget
		QtGui.QMainWindow.__init__(self, parent)
		self.setWindowTitle('Chat Message Window')
		
		self.textBox = QtGui.QTextEdit(parent = self)
		self.textBox.setReadOnly(True)
		self.setCentralWidget(self.textBox)
		
		self.textBox.setPlainText(task.task_name)
		chat_window = lineyka_chat.lineyka_chat(self)
		
	def chat_close(self, mw):
		self.close_window(mw)
		
	def close_window(self, window):
		if window:
			window.close()
			
	def message(self, m, i):
		#m = str(m)
		
		mBox = QtGui.QMessageBox()
		mBox.setText(m)
		#mBox.setStandardButtons( QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok )
		ok_button = mBox.addButton(QtGui.QMessageBox.Ok)
		cancel_button = mBox.addButton(QtGui.QMessageBox.Cancel)
    
		if i==1:
			mBox.setIcon(QtGui.QMessageBox.Information)
			mBox.setWindowTitle('Info')
		elif i == 2:
			mBox.setIcon(QtGui.QMessageBox.Warning)
			mBox.setWindowTitle('Warning!')
		elif i == 3:
			mBox.setIcon(QtGui.QMessageBox.Critical)
			mBox.setWindowTitle('Error!')
		elif i == 0:
			mBox.setIcon(QtGui.QMessageBox.Question)
			mBox.setWindowTitle('Confirm!')
    
		com = mBox.exec_()
    
		if mBox.clickedButton() == ok_button:
			return(True)
		elif mBox.clickedButton() == cancel_button:
			return(False)

if __name__=='__main__':
	app = QtGui.QApplication(sys.argv)
	mw = MainWindow(sys.argv[1])
	mw.show()
	app.exec_()
	
def run(task):
	app = QtGui.QApplication(sys.argv)
	mw = MainWindow(task)
	mw.show()
	app.exec_()