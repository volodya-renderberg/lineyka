#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PySide2 import QtCore, QtGui, QtUiTools, QtSql, QtWidgets
import os
import shutil
import webbrowser
import getpass
from functools import partial
import json
import random
import subprocess
import uuid
import datetime
from urllib import parse
import requests

# from lineyka 
#import ui
import edit_db as db
import lineyka_chat
#import lineyka_publish

# sudo chmod +x "/home/vofka/Yandex.Disk/Lineyka/lineyka_manager.py"

class G(object):
    pass

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        pass
        self.cloud='django' # тип используемого облака
        # get Path
        root_dir = os.path.dirname(db.__file__)
        path = db.NormPath(os.path.join(root_dir, 'ui'))
        #path = os.path.dirname(ui.__file__)
        self.lineyka_path = os.path.dirname(path)
        self.main_window_path = os.path.join(path, "lineyka_manager.ui")
        self.set_window_path = os.path.join(path, "qt_settings.ui")
        self.create_cloud_studio_path = os.path.join(path, 'create_cloud_studio.ui')
        self.set_dir_cloud_studio_path = os.path.join(path, 'set_dir_cloud_studio.ui')
        self.login_window_path = os.path.join(path, "login.ui")
        self.user_registr_window_path = os.path.join(path, "registration.ui")
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
        self.select_from_list_dialog_combobox_line_path = os.path.join(path, "select_from_list_dialog_combobox_line.ui")
        self.select_from_list_dialog_3button_path = os.path.join(path, "select_from_list_dialog_3_button.ui")
        self.select_from_check_button_dialog_path = os.path.join(path, "select_from_check_button_dialog.ui")
        self.select_from_list_dialog_4combobox_path = os.path.join(path, "select_from_list_dialog_4combobox.ui")
        
        # -- chat path
        self.chat_main_path = os.path.join(path, "chat_dialog.ui")
        self.chat_add_topic_path = os.path.join(path, "chat_add_topic.ui")
        self.chat_img_viewer_path = os.path.join(path, "chat_img_viewer.ui")
        
        # colors
        #self.project_color = QtGui.QColor(106, 229, 255)
        self.project_color = QtGui.QColor(63, 152, 171)
        #self.workroom_color = QtGui.QColor(145, 185, 246)
        self.workroom_color = QtGui.QColor(85, 123, 183)
        #self.artist_color = QtGui.QColor(200, 250, 100)
        self.artist_color = QtGui.QColor(91, 130, 14)
        self.grey_color = QtGui.QColor(150, 150, 150)
        #self.set_of_tasks_color = QtGui.QColor(183, 231, 178)
        self.set_of_tasks_color = QtGui.QColor(89, 144, 83)
        #self.tasks_color = QtGui.QColor(255, 241, 150)
        self.tasks_color = QtGui.QColor(159, 143, 84)
        #self.season_color = QtGui.QColor(255, 205, 227)
        self.season_color = QtGui.QColor(192, 142, 164)
        #self.group_color = QtGui.QColor(255, 201, 190)
        self.group_color = QtGui.QColor(185, 124, 112)
        #self.asset_color = QtGui.QColor(255, 218, 160)
        self.asset_color = QtGui.QColor(166, 125, 61)
        self.stop_color = QtGui.QColor(142, 160, 193)
        self.red_text_color = QtGui.QColor(223, 45, 32)
        #
        self.conformity_colors = {
        'pull':self.project_color,
        'commit':self.workroom_color,
        'push':self.set_of_tasks_color,
        'publish':self.tasks_color,
        'open':'work',
        'report':'checking',
        'recast':'recast',
        'change_artist':self.artist_color,
        'close':'close',
        'done':'done',
        'reader_accept':'done',
        'return_a_job':'ready',
        'send_to_outsource':'ready_to_send',
        'load_from_outsource':'checking',
        }
        
        # load db.
        # studio level
        self.db_studio = db.studio
        self.studio = self.db_studio()
        self.artist = db.artist() # - по совместительству current user - все объекты artist - не текущего юзера, должны быть другими объектами.
        self.db_workroom = db.workroom()
        self.db_set_of_tasks = db.set_of_tasks()
        self.project = db.project() # он же текущий проект
        # self.project.get_list() # заполнение полей списков проектов. # debug
        # project level
        self.db_season = db.season(self.project)
        self.db_asset = db.asset(self.project)
        self.db_group = db.group(self.project)
        self.db_list_of_assets = db.list_of_assets(self.db_group)
        self.db_task = db.task(self.db_asset)
        self.db_chat = db.chat(self.db_task)
        self.db_log = db.log(self.db_task)
        
        # other moduls
        #self.publish = lineyka_publish.publish()
        
        # VARIABLES
        #self.workrooms = {} # словарь отделов(объекты) по id - заполняется в set_self_workrooms()
        #self.workrooms_by_name = {} # словарь отделов(объекты) по name - заполняется в set_self_workrooms()
        self.workroom = None # текущий отдел (объект)
        self.selected_artist = None # выбранный в таблице артист (объект)
        #self.current_user = None # авторизированный юзер (объект) - устарело
        self.selected_project = None # выбранный в таблице проект (объект)
        self.set_of_tasks_list = None # список наборов (объекты) - заполняется в fill_set_of_tasks_table()
        self.selected_set_of_tasks = None # выбранный в таблице set_of_tasks (объект)
        self.selected_season = None # выбранный в таблице сезон season (объект)
        self.selected_group = None # выбранная в таблице группа (объект)
        self.selected_asset = None # выбранный в таблице ассет (объект)
        self.selected_task = None # выбранный так в таблице в task editor
        self.current_artists_dict = None # словарь артистов по именам, полученный парсером по отделам.
        #self.current_readers_dict = None # словарь ридеров (артисты) по именам - получаемый при назанчении ридеров в tm_ - не нужен теперь это self.selected_task.readers
        self.date_start = None # временной диапазон, для различных целей, определяется в tm_choice_dates()
        self.date_end = None # временной диапазон, для различных целей, определяется в tm_choice_dates()
        
        # CONSTANTS
        self.SEASON_COLUMNS = ['name', 'status']
        self.GROUP_COLUMNS = ['name', 'type', 'description', 'season']
        self.look_keys = ['icon', 'username','specialty','outsource','level']
        self.REQUIRED_KEYS = ['task_name', 'activity', 'workroom', 'task_type', 'extension'] # обязательные параметры при создании одной задачи для ассета.
        
        #self.current_project = False # удаляем.
        self.current_group = False
        self.type_editor = False
        
        QtWidgets.QMainWindow.__init__(self, parent)
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.main_window_path)
        file.open(QtCore.QFile.ReadOnly)
        self.myWidget = loader.load(file, self)
        file.close()
        
        # ---- get artist data
        self.get_artist_data() # debug

        # setWindowIcon
        if hasattr(self.studio, 'image'):
            icon_path = self.get_cache_path_from_url(self.studio.image)
            if icon_path:
                # self.myWidget.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(icon_path)))
                self.myWidget.menu_set_studio.setIcon(QtGui.QIcon(QtGui.QPixmap(icon_path)))
        
        # menu Studio
        self.myWidget.action_set_studio.triggered.connect(self.set_studio_ui)
        self.myWidget.action_go_to_web_page.triggered.connect(self.go_to_studio_web_page)

        # menu User
        self.myWidget.actionLogin.triggered.connect(self.user_login_ui)
        self.myWidget.actionRegistration.triggered.connect(self.user_registration_ui)
        self.myWidget.actionUser_manual.triggered.connect(self.help_user_manual)
        self.myWidget.action_edit_profile.triggered.connect(self.edit_profile_ui)

                
        # at studio 
        self.myWidget.artist_editor_button.clicked.connect(self.edit_ui_to_artist_editor)
        self.myWidget.workroom_editor_button.clicked.connect(self.edit_ui_to_workroom_editor)
        self.myWidget.project_editor_button.clicked.connect(self.edit_ui_to_project_editor)
        self.myWidget.set_of_tasks_editor_button.clicked.connect(self.edit_ui_to_set_of_tasks_editor)
        
        # at project
        self.myWidget.season_editor_button.clicked.connect(self.edit_ui_to_season_editor)
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
        self.myWidget.group_search_qline.returnPressed.connect(self.reload_asset_list)
        
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
        addgrup_action = QtWidgets.QAction( 'change Task', self.myWidget)
        addgrup_action.triggered.connect(partial(self.loc_change_input_task_ui))
        self.myWidget.studio_editor_table_2.addAction( addgrup_action )
        
        self.launcher()
        
        # ---- TASKS MANAGER ----------------------------
        # self.preparation_to_task_manager() # debug
        
        # -----STILE-------
        self.setStyleSheet(open(os.path.join(root_dir,'darkorange.qss')).read())
        
                                
    # ******************* STUDIO EDITOR ************************************************
    
    # task (bool) - если тру, то ассет достаётся через задачу
    def _edit_loading_type_ui(self, fn, table=False, task=False):
        pass
        if not table:
            table = self.myWidget.studio_editor_table
        #
        if not table.selectedItems():
            self.message('No asset selected!', 2)
        if task:
            self.selected_asset=table.selectedItems()[0].task.asset
        else:
            self.selected_asset=table.selectedItems()[0].asset
        
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.combo_dialog_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.setProjectDialog = loader.load(file, self)
        file.close()
        
        # edit widget
        #copy = db.studio()
        window.setWindowTitle(('Edit of Loading Type: %s' % self.selected_asset.name))
        window.combo_dialog_label.setText('New Loading Type:')
        window.combo_dialog_combo_box.addItems(self.selected_asset.loading_types)
        window.combo_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.combo_dialog_ok.clicked.connect(partial(fn, window))
        
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()
        print('edit loading type of asset "%s" ui' % self.selected_asset.name)
    
    # ******************* STUDIO EDITOR /// ARTIST EDITOR ****************************
    def edit_ui_to_artist_editor(self):
        pass
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
        self.myWidget.studio_butt_4.setVisible(True)
        self.myWidget.studio_butt_4.setText('Look Logs')
        try:
            self.myWidget.studio_butt_4.clicked.disconnect()
        except:
            pass
        self.myWidget.studio_butt_4.clicked.connect(self.artist_look_logs_ui)
        #self.myWidget.studio_butt_4.setVisible(False)
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
        self.myWidget.studio_editor_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.myWidget.studio_editor_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
        self.clear_table()
        self.fill_artist_table()
                
    def fill_artist_table(self):
        pass
        #copy = self.db_artist
        artists = self.artist.read_artists({'status': 'active'})
        
        if not artists[0]:
            self.message(artists[1], 2)
            return
        
        # get workroom data
        #wr_id_dict = {}
        #wr_name_dict = {}
        
        '''
        result = self.db_workroom.get_list('by_id', True)
        if not result[0]:
            self.message(result[1], 3)
            #return
        else:
            self.workrooms = result[1]
        '''
        self.db_workroom.get_list()
           
        # get table data
        look_keys = [
            'icon',
            'username',
            'level',
            'status',
            'specialty',
            'workroom',
            'date_joined_to_studio',
            'email',
            'phone',
            'outsource',
            # 'share_dir',
            ]
        num_row = len(artists[1])
        num_column = len(look_keys)
        headers = []
        
        for item in look_keys:
            headers.append(item)
    
        # make table
        self.myWidget.studio_editor_table.setColumnCount(num_column)
        self.myWidget.studio_editor_table.setRowCount(num_row)
        self.myWidget.studio_editor_table.setHorizontalHeaderLabels(headers)
    
        # fill table
        table = self.myWidget.studio_editor_table
        #
        for i, artist in enumerate(artists[1]):
            for j,key in enumerate(headers):
                newItem = QtWidgets.QTableWidgetItem()
                if key == 'date_joined_to_studio':
                    newItem.setText(getattr(artist, key).strftime("%d-%m-%Y"))
                    #newItem.setText('time')
                elif key == 'workroom':
                    if getattr(artist, key):
                        wr_list = []
                        for wr_id in getattr(artist, key):
                            wr_list.append(self.db_workroom.dict_by_id[wr_id].name)
                        item_text = ','.join(wr_list).replace(',', ',\n')
                        newItem.setText(item_text)
                elif key == 'username':
                    color = self.artist_color
                    brush = QtGui.QBrush(color)
                    newItem.setBackground(brush)
                    newItem.setText(str(getattr(artist, key)))
                elif key == 'icon':
                    # label
                    label = QtWidgets.QLabel()
                    #
                    if db.studio.studio_database=='django':
                        # img
                        icon_path = self.get_cache_path_from_url(artist.profile.get('image'))
                        if icon_path:
                            image = QtGui.QImage(icon_path)
                            pix = QtGui.QPixmap(image)
                            #
                            label.setPixmap(pix)
                            label.show()
                        else:
                            label.setText('no image')
                    else:
                        label.setText('no image')
                    
                    label.artist = artist
                    table.setCellWidget(i, j, label)
                else:
                    newItem.setText(str(getattr(artist, key)))
                newItem.artist = artist
                table.setItem(i, j, newItem)
                
        table.resizeRowsToContents()
        table.resizeColumnsToContents()
                
        # context menu
        table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self._artist_editor_context_menu)

        print('fill artist table')
        
    def _artist_editor_context_menu(self, pos):
        pass
        #print(pos.__reduce__())
        table = self.myWidget.studio_editor_table
        item = table.selectedItems()[0]
        #print(item.column_name)
        menu = QtWidgets.QMenu(table)
        menu_items = ['Edit Artist Data', 'Look Logs']
        for label in menu_items:
            if label == menu_items[0]:
                action = menu.addAction(label)
                action.triggered.connect(partial(self._artist_editor_context_menu_action, label, item))
            elif label == menu_items[1]:
                action = menu.addAction(label)
                action.triggered.connect(partial(self.artist_look_logs_ui))
        menu.exec_(QtGui.QCursor.pos())
    
    def _artist_editor_context_menu_action(self, label, item):
        pass
        #print(label, item.set_of_tasks.name)
        if label=='Edit Artist Data':
            self.edit_artist_ui(artist=item.artist)
    
    def reload_artist_list(self):
        pass
        self.clear_table()
        '''
        # clear table
        num_row = self.myWidget.studio_editor_table.rowCount()
        num_column = self.myWidget.studio_editor_table.columnCount()
    
        for i in range(0, num_row):
            for j in range(0, num_column):
                item = self.myWidget.studio_editor_table.item(i, j)
                self.myWidget.studio_editor_table.takeItem(i, j)

                #self.myWidget.studio_editor_table.removeCellWidget(i, j)
        '''
    
        # fill table
        self.fill_artist_table()

        # finish
        print('reload artist list')
    
    # ------------------- Add Artist ---------------------------------------------------------
    def add_artist_ui(self):
        if not self.artist.level:
            self.message('No Access! (you must register or login)', 3)
            return
        elif self.artist.level not in self.artist.MANAGER_LEVELS:
            self.message('No Access! (level "%s" is not enough to perform this operation)' % self.artist.level, 3)
            return
            
        # get levels
        levels = []
        for level in self.artist.USER_LEVELS:
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
        'username' : self.newArtistDialog.nik_name_field.text(),
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
        data['workroom'] = wr_id_list
        
        # get Outsource
        if data['outsource'] == QtCore.Qt.CheckState.Checked:
            data['outsource'] = True
        else:
            data['outsource'] = False
            
        # get NikName Password
        if data['username'] == '' or data['password'] == '':
            self.message('Not Nik_Name or Password', 2)
            return
        
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
    def edit_artist_ui(self, artist=False):
        if not artist:
            current_item = self.myWidget.studio_editor_table.currentItem()
            if not current_item:
                self.message('Not Selected Artists!', 2)
                return
            self.selected_artist = current_item.artist
        else:
            self.selected_artist = artist
        
        
        level = getattr(self.selected_artist, 'level')
        
        if self.artist.level not in self.artist.MANAGER_LEVELS:
            self.message('No Access! your level: "%s"' % self.artist.level, 3)
            return
        
        # get levels
        levels = []
        for level in self.artist.USER_LEVELS:
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
        wr_name_list = []
        if self.selected_artist.workroom:
            for wr_id in  self.selected_artist.workroom:
                wr_name_list.append(self.db_workroom.dict_by_id[wr_id].name)
        
        # edit widget
        window.setWindowTitle('Edit Artist Data')
        window.nik_name_field.setEnabled(False)
        window.nik_name_field.setText(self.selected_artist.username)
        window.workroom_field.setEnabled(False)
        window.workroom_field.setText(json.dumps(wr_name_list))
        window.share_dir_field.setEnabled(False)
        window.share_dir_field.setText(self.selected_artist.share_dir)
        window.password_field.setText(self.selected_artist.password)
        window.email_field.setText(self.selected_artist.email)
        window.phone_field.setText(self.selected_artist.phone)
        window.specialty_field.setText(self.selected_artist.specialty)
        
        window.level_combobox.addItems(levels)
        window.level_combobox.setCurrentIndex(window.level_combobox.findText(self.selected_artist.level))
        
        if self.selected_artist.outsource == 1:
            window.autsource_check_box.setCheckState(QtCore.Qt.CheckState.Checked)
            
        # button connect
        window.get_share_dir_button.clicked.connect(partial(self.get_share_dir, window.share_dir_field))
        window.artist_edit_workroom_button.clicked.connect(partial(self.artist_edit_workroom2_ui, window))
        window.artist_dialog_ok.clicked.connect(partial(self.edit_artist_action))
        window.artist_dialog_cancel.clicked.connect(partial(self.close_window, window))
        
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()
        
        # finish
        print('edit artist ui')
        
    
    def edit_artist_action(self):
        window = self.editArtistDialog
        # get data
        # -- get workroom id list
        wr_name_list = json.loads(window.workroom_field.text())
        wr_id_list = []
        
        bool_, r_data = self.db_workroom.name_list_to_id_list(wr_name_list)
        if not bool_:
            self.message(r_data, 2)
            return
        wr_id_list=r_data
        
        # -- fill table
        username = window.nik_name_field.text()
        data = {
        'username' : username,
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
        result = self.selected_artist.edit_artist(data, current_user = self.artist)
        
        if not result[0]:
            self.message(result[1], 2)
            return
        
        # get artist data
        #print('*'*5, self.current_user, username)
        if self.artist.username == username:
            self.get_artist_data()
            
        # finish
        self.reload_artist_list()
        window.close()
            
        print('edit artist action', data)
    
    # ----------------- Artist Edit Workroom ----------------------------
    def artist_edit_workroom2_ui(self, current_widget): # используется при редактировании артиста (с чек боксами).
        pass
        # get all workrooms
        bool_, workrooms = self.db_workroom.get_list()
        
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
        layout = QtWidgets.QVBoxLayout()
        for wr in workrooms:
            wr_name = wr.name
            box = QtWidgets.QCheckBox(wr_name, window.check_buttons_frame)
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
        pass
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
        
    
    def artist_edit_workroom_ui(self, current_widget): # используется при создании артиста (с таблицей).
        pass
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
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        
        
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
            data.append(self.db_workroom.dict_by_id[item.id].name)
            
        data = set(data)
        data = list(data)
        
        current_widget.workroom_field.setText(json.dumps(data))
        self.close_window(self.selectWorkroomDialog)
        
        # get artist data
        #self.get_artist_data()
        
    
    # ------------------ Artist Get Share Dir ---------------------------
    def get_share_dir(self, field):
        pass
        # get path
        home = os.path.expanduser('~')
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, home)
        field.setText(str(folder))
        
    # ------------------ Time Logs --------------------------------------
    
    # task_ob (task) - если не передавать - то использует selected_task
    def artist_look_logs_ui(self, artist=False):
        pass
        if not artist:
            current_item = self.myWidget.studio_editor_table.currentItem()
            if not current_item:
                self.message('Not Selected Artists!', 2)
                return
            self.selected_artist = current_item.artist
        else:
            self.selected_artist = artist
    
        # make widjet
        ui_path = self.select_from_list_dialog_4combobox_path
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(ui_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.lookVersionDialog = loader.load(file, self)
        file.close()
        
        # set window texts
        window.setWindowTitle('Logs of: %s' % self.selected_artist.username)
        window.select_from_list_cansel_button.setText('Close')
        window.label_1.setText('For all time')
        window.dialog_comboBox_1.addItems(self.date_choice_variants + ['Choice dates'])
        window.dialog_comboBox_2.addItems(['All Projects'])
        window.dialog_comboBox_3.addItems(['Start', 'Finish'])
        window.dialog_comboBox_4.addItems(['All Tasks'])
        
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        # edit Widget
        window.select_from_list_cansel_button.clicked.connect(partial(self.close_window, window))
        window.dialog_comboBox_1.activated[str].connect(partial(self.tm_choice_dates, window, self.artist_look_logs_fill_table))
        window.dialog_comboBox_3.activated.connect(partial(self.artist_look_logs_fill_table, window))
        window.dialog_comboBox_2.activated.connect(partial(self.artist_look_logs_fill_table, window))
        window.dialog_comboBox_4.activated.connect(partial(self.artist_look_logs_fill_table, window))
        window.select_from_list_apply_button.setVisible(False)
        
        window.show()
        
        # read_log
        b, r_data = self.db_log.artist_read_log(all=True, artist_ob=self.selected_artist)
        if not b:
            self.message(r_data, 2)
            return
        self.selected_artist_logs = r_data
        # fill table
        self.artist_look_logs_fill_table(window)
        
    def artist_look_logs_fill_table(self, window, *args):
        pass
        #
        def get_start_end_dates(date_mode):
            if date_mode==self.date_choice_variants[1]:
                start_date = datetime.date.today() - datetime.timedelta(days=7)
                end_date = datetime.date.today()
            elif date_mode==self.date_choice_variants[2]:
                start_date = datetime.date.today() - datetime.timedelta(days=30)
                end_date = datetime.date.today()
            elif date_mode=='Choice dates':
                start_date = self.date_start
                end_date = self.date_end
            return(start_date, end_date)
    
        table = window.select_from_list_data_list_table
        # clear table
        self.clear_table(table=table)
        if not self.selected_artist_logs:
            self.message('Logs not found!', 1)
            return
        
        # filters
        fin_logs = list()
        tasks = list()
        projects = list()
        for log in self.selected_artist_logs:
            projects.append(log['project_name'])
            tasks.append(log['task_name'])
            date_mode = window.dialog_comboBox_1.currentText()
            project = window.dialog_comboBox_2.currentText()
            task_name = window.dialog_comboBox_4.currentText()
            #
            if project != 'All Projects' and project != log['project_name']:
                continue
            elif task_name != 'All Tasks' and task_name != log['task_name']:
                continue
            elif date_mode != self.date_choice_variants[0]:
                start_date, end_date = get_start_end_dates(date_mode)
                #
                if not log[window.dialog_comboBox_3.currentText().lower()]:
                    continue
                elif not start_date <= log[window.dialog_comboBox_3.currentText().lower()].date() <= end_date:
                    continue
                else:
                    fin_logs.append(log)
            elif date_mode == self.date_choice_variants[0]:
                if not log[window.dialog_comboBox_3.currentText().lower()]:
                    continue
                else:
                    fin_logs.append(log)
            else:
                fin_logs.append(log)
        
        # fill table
        #headers = self.db_log.artists_logs_keys.keys()
        headers = ['project_name', 'task_name', 'start', 'finish', 'full_time', 'price']
        num_column = len(headers)
        num_row = len(fin_logs)
        
        table.setColumnCount(num_column)
        table.setRowCount(num_row)
        table.setHorizontalHeaderLabels(headers)
        
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
        all_time = 0
        all_cost = 0
        
        for i, log in enumerate(fin_logs):
            pass
            for j,header in enumerate(headers):
                newItem = QtWidgets.QTableWidgetItem()
                # content item
                if header == 'start' or header == 'finish':
                    if log[header]:
                        newItem.setText(log[header].strftime("%m/%d/%Y, %H:%M:%S"))
                    else:
                        newItem.setText('')
                elif header == 'full_time':
                    if log[header]:
                        time = log[header]/3600
                    else:
                        time=0
                    all_time = all_time + time
                    newItem.setText('%s h' % str(round(time, 2)))
                elif header == 'price':
                    if log[header]:
                        all_cost += log[header]
                    newItem.setText(str(log[header]))
                else:
                    newItem.setText(str(log[header]))
                
                # item
                if False:
                    color = QtGui.QColor(self.artist_color)
                    brush = QtGui.QBrush(color)
                    newItem.setBackground(brush)
                    #
                    table.setItem(i, j, newItem)
                else:
                    table.setItem(i, j, newItem)
                    
        table.resizeRowsToContents()
        table.resizeColumnsToContents()
        
        # edit window
        if window.dialog_comboBox_1.currentText() in self.date_choice_variants:
            window.label_1.setText('%s (%s h, %s $)' % (window.dialog_comboBox_1.currentText(), round(all_time, 2), all_cost))
        else:
            window.label_1.setText('from %s to %s (%s h, %s $)' % (self.date_start, self.date_end, round(all_time, 2), all_cost))
        #
        window.dialog_comboBox_2.clear()
        project_items = ['All Projects']+ sorted(list(set(projects)))
        window.dialog_comboBox_2.addItems(project_items)
        window.dialog_comboBox_2.setCurrentIndex(project_items.index(project))
        #
        window.dialog_comboBox_4.clear()
        tasks_items = ['All Tasks']+ sorted(list(set(tasks)))
        window.dialog_comboBox_4.addItems(tasks_items)
        window.dialog_comboBox_4.setCurrentIndex(tasks_items.index(task_name))
    
    
    
    # ******************* STUDIO EDITOR /// WORKROOM EDITOR ****************************
    
    def edit_ui_to_workroom_editor(self):
        pass
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
        self.myWidget.studio_butt_3.setVisible(True)
        self.myWidget.studio_butt_3.setText('Edit Type')
        try:
            self.myWidget.studio_butt_3.clicked.disconnect()
        except:
            pass
        self.myWidget.studio_butt_3.clicked.connect(self.edit_type_workroom_ui)
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
        #self.myWidget.studio_editor_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.myWidget.studio_editor_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.myWidget.studio_editor_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
        self.clear_table()
        self.fill_workroom_table(self.myWidget.studio_editor_table)
                
    def fill_workroom_table(self, table):
        self.db_workroom.get_list()
        if not self.db_workroom.dict_by_id:
                    return
        
        # look_keys
        look_keys = ['name', 'type']
        
        # get table data
        num_row = len(self.db_workroom.dict_by_id)
        num_column = len(look_keys)
        headers = []
        
        for item in look_keys:
            headers.append(item)
            
        # make table
        table.setColumnCount(num_column)
        table.setRowCount(num_row)
        table.setHorizontalHeaderLabels(headers)    
        
        # fill table
        for i, name in enumerate(sorted(self.db_workroom.dict_by_name.keys())):
            workroom = self.db_workroom.dict_by_name[name]
            for j,key in enumerate(headers):
                if key == 'date_time':
                    continue
                newItem = QtWidgets.QTableWidgetItem()
                #
                if key == 'type':
                    if workroom.type:
                        type_string = ','.join(workroom.type).replace(',', ',\n')
                        newItem.setText(type_string)
                    else:
                        newItem.setText('')
                else:
                    data = getattr(workroom, key)
                    newItem.setText(data)
                #
                #newItem.id = workroom.id
                newItem.workroom = workroom
                #
                if key == 'name':
                    color = self.workroom_color
                    brush = QtGui.QBrush(color)
                    newItem.setBackground(brush)
    
                table.setItem(i, j, newItem)
        
        table.resizeRowsToContents()
        table.resizeColumnsToContents()
        
        # context menu
        table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self._workroom_editor_context_menu)
        
        print('fill workroom table')
        
    def _workroom_editor_context_menu(self, pos):
        pass
        #print(pos.__reduce__())
        table = self.myWidget.studio_editor_table
        item = table.selectedItems()[0]
        #print(item.column_name)
        menu = QtWidgets.QMenu(table)
        menu_items = ['Rename','Edit Type', 'Edit Artist List']
        for label in menu_items:
            action = menu.addAction(label)
            action.triggered.connect(partial(self._workroom_editor_context_menu_action, label, item))
        menu.exec_(QtGui.QCursor.pos())
        
    def _workroom_editor_context_menu_action(self, label, item):
        pass
        #print(label, item.set_of_tasks.name)
        if label=='Rename':
            self.rename_workroom_ui(workroom=item.workroom)
        elif label=='Edit Type':
            self.edit_type_workroom_ui(workroom=item.workroom)
        elif label=='Edit Artist List':
            self.edit_ui_to_edit_artist_list(workroom=item.workroom)
                
    def reload_workroom_list(self):
        self.clear_table()
        self.fill_workroom_table(self.myWidget.studio_editor_table)
        print('reload workroom list')
        
    # -------------------- New Workroom ---------------------------------------
        
    def new_workroom_ui(self):
        loader = QtUiTools.QUiLoader()
        #file = QtCore.QFile(self.new_dialog_path)
        file = QtCore.QFile(self.qt_set_project_path)
        #file.open(QtCore.QFile.ReadOnly)
        self.newWorkroomDialog = loader.load(file, self)
        file.close()
        
        # edit widget
        self.newWorkroomDialog.setWindowTitle('add New WorkRoom')
        #self.newWorkroomDialog.new_dialog_label.setText('Name:')
        self.newWorkroomDialog.label_2.setText('* Name:')
        self.newWorkroomDialog.label.setText('Type:')
        self.newWorkroomDialog.set_project_path_button.setText('Set the Type')
        
        # edit button
        #self.newWorkroomDialog.new_dialog_cancel.clicked.connect(partial(self.new_workroom_action, False))
        #self.newWorkroomDialog.new_dialog_ok.clicked.connect(partial(self.new_workroom_action, True))
        self.newWorkroomDialog.set_project_path_button.clicked.connect(partial(self.new_workroom_set_type_ui, self.newWorkroomDialog.set_project_folder))
        self.newWorkroomDialog.set_project_cansel_button.clicked.connect(partial(self.new_workroom_action, False)) #set_project_cansel_button
        self.newWorkroomDialog.set_project_ok_button.clicked.connect(partial(self.new_workroom_action, True)) # set_project_ok_button
                
        # set modal window
        self.newWorkroomDialog.setWindowModality(QtCore.Qt.WindowModal)
        self.newWorkroomDialog.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        self.newWorkroomDialog.show()
        print('new workroom ui')
        
    def new_workroom_set_type_ui(self, field):
        pass
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.select_from_check_button_dialog_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.setWorkroomTypeDialog = loader.load(file, self)
        file.close()
        
        # -- add checkbox
        checkbox_list = []
        layout = QtWidgets.QVBoxLayout()
        for task_type in self.db_workroom.task_types:
            box = QtWidgets.QCheckBox(task_type, window.check_buttons_frame)
            checkbox_list.append(box)
            if field.text():
                if task_type in json.loads(field.text()):
                    box.setCheckState(QtCore.Qt.CheckState.Checked)
            
            layout.addWidget(box)
        window.check_buttons_frame.setLayout(layout)
        
        # -- edit button
        window.select_from_chbut_cansel_button.clicked.connect(partial(self.close_window, window))
        window.select_from_chbut_apply_button.clicked.connect(partial(self.new_workroom_set_type_action, field, window, checkbox_list))
        
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        #field.setText('type')
        window.show()
        
    def new_workroom_set_type_action(self, field, window, checkbox_list):
        pass
        # get data
        data = []
        for obj in checkbox_list:
            if obj.checkState() == QtCore.Qt.CheckState.Checked:
                data.append(obj.text())
        # set data
        field.setText(json.dumps(data))
        self.close_window(window)
        
    def new_workroom_action(self, action):
        if not action:
            self.newWorkroomDialog.close()
            return
        
        #name = self.newWorkroomDialog.new_dialog_name.text().replace(' ','_')
        name = self.newWorkroomDialog.priject_name_field.text().replace(' ','_')
        if name == '':
            self.message('Not Name!', 2)
            return
        # get types
        list_of_types = self.newWorkroomDialog.set_project_folder.text()
        if list_of_types :
            list_of_types = json.loads(list_of_types)
            if list_of_types.__class__.__name__== 'list':
                keys = {
                    'name': name,
                    'type': list_of_types,
                    }
            else:
                keys = {'name': name}
        else:
            keys = {'name': name}
        # create
        result = self.db_workroom.add(keys)
        if not result[0]:
            self.message(result[1], 3)
        self.newWorkroomDialog.close()
        self.fill_workroom_table(self.myWidget.studio_editor_table)
        
    # -------------------- Edit Type Workroom ---------------------------------------
    
    def edit_type_workroom_ui(self, workroom=False):
        if not workroom:
            table = self.myWidget.studio_editor_table
            current_item = table.currentItem()
            if not current_item:
                self.message('Not Selected Workroom!', 2)
                return
            else:
                self.workroom = current_item.workroom
        else:
            self.workroom=workroom
        
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.select_from_check_button_dialog_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.editWorkroomTypeDialog = loader.load(file, self)
        file.close()
        
        # -- add checkbox
        checkbox_list = []
        layout = QtWidgets.QVBoxLayout()
        for task_type in self.db_workroom.task_types:
            box = QtWidgets.QCheckBox(task_type, window.check_buttons_frame)
            checkbox_list.append(box)
            if self.workroom.type and task_type in self.workroom.type:
                box.setCheckState(QtCore.Qt.CheckState.Checked)
            
            layout.addWidget(box)
        window.check_buttons_frame.setLayout(layout)
        
        # -- edit button
        window.select_from_chbut_cansel_button.clicked.connect(partial(self.close_window, window))
        window.select_from_chbut_apply_button.clicked.connect(partial(self.edit_type_workroom_action, window, checkbox_list))
        
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        #field.setText('type')
        window.show()
        
    def edit_type_workroom_action(self, window, checkbox_list):
        data = []
        for obj in checkbox_list:
            if obj.checkState() == QtCore.Qt.CheckState.Checked:
                data.append(obj.text())
        # set data
        bool_, return_data = self.workroom.edit_type(data)
        if not bool_:
            return(False, return_data)
        
        self.close_window(window)
        self.fill_workroom_table(self.myWidget.studio_editor_table)
    
    # -------------------- Rename Workroom ---------------------------------------
    
    def rename_workroom_ui(self, workroom=False):
        if not workroom:
            table = self.myWidget.studio_editor_table
            current_item = table.currentItem()
            if not current_item:
                self.message('Not Selected Workroom!', 2)
                return
            else:
                self.workroom = current_item.workroom
        else:
            self.workroom = workroom
        
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.new_dialog_path)
        #file.open(QtCore.QFile.ReadOnly)
        self.newWorkroomDialog = loader.load(file, self)
        file.close()
        
        # edit widget
        self.newWorkroomDialog.setWindowTitle('Rename WorkRoom')
        self.newWorkroomDialog.new_dialog_label.setText('New Name:')
        self.newWorkroomDialog.new_dialog_name.setText(self.workroom.name)
        
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
            # rename
            new_name = self.newWorkroomDialog.new_dialog_name.text().replace(' ','_')
            bool_, rdata = self.workroom.rename_workroom(new_name)
            if not bool_:
                self.message(rdata, 3)
                return
            # close dialog
            self.newWorkroomDialog.close()
            # reload workroom table
            self.fill_workroom_table(self.myWidget.studio_editor_table)
            
    # -------------------- Workroom ADD  Artists Editor ---------------------------------------
    
    def edit_ui_to_edit_artist_list(self, workroom=False):
        pass
        if not workroom:
            current_item = self.myWidget.studio_editor_table.currentItem()
            if not current_item:
                self.message('Not Selected Workroom!', 2)
                return
            else:
                self.workroom = current_item.workroom
        else:
            self.workroom=workroom
                
        # edit label
        self.myWidget.studio_editor_label.setText(('WorkRoom Editor / "%s" - edit Artist List' % self.workroom.name))
        
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
        self.myWidget.studio_editor_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.myWidget.studio_editor_table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        
        # fill table
        self.clear_table()
        self.fill_active_artist_table_at_workroom()
                
        
        print('edit ui to edit artist list')
        
    def add_artists_to_workroom_dialog(self):
        pass
        # widget
        loader = QtUiTools.QUiLoader()
        #file = QtCore.QFile(self.select_from_list_dialog_path)
        file = QtCore.QFile(self.select_from_list_dialog_combobox_line_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.addArtistToWorkroomDialog = loader.load(file, self)
        file.close()
        
        # get wr_name_list
        wr_name_list = ['-- all --'] + sorted(list(self.db_workroom.dict_by_name.keys()))
        
        # edit widget
        window.setWindowTitle(('Add Artist To \"' + self.workroom.name + '\"'))
        window.select_from_list_apply_button.setText('Add Select Artists')
        window.select_from_list_apply_button.clicked.connect(partial(self.add_select_artists_to_workroom, window))
        window.select_from_list_cansel_button.clicked.connect(partial(self.close_window, window))
        window.dialog_comboBox_1.addItems(wr_name_list)
        #window.dialog_comboBox_1.activated[str].connect(partial(self.print_data, window))
        window.dialog_comboBox_1.activated[str].connect(partial(self.fill_active_artist_table_for_workroom, window))
        window.name_filter.setPlaceholderText('Filter by Name')
        window.name_filter.textChanged.connect(partial(self.fill_active_artist_table_for_workroom, window))
        
        # edit table
        #self.myWidget.studio_editor_table_2.setVisible(False)
        self.myWidget.right_table_frame.setVisible(False)
        # -- selection mode   
        window.select_from_list_data_list_table.setSortingEnabled(True)
        window.select_from_list_data_list_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        window.select_from_list_data_list_table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()
        
        self.fill_active_artist_table_for_workroom(window)
        print('add artist to workroom dialog')
        
    def fill_active_artist_table_at_workroom(self):
        print(self.workroom.id)
        b,r = self.artist.read_artists_of_workroom(self.workroom)
        if not b:
            self.message(r, 2)
            return
        active_artists=list(r.values())
    
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
                newItem = QtWidgets.QTableWidgetItem()
                if key in ['outsource']:
                    newItem.setText(str(getattr(artist, key)))
                elif key == 'icon':
                    # label
                    label = QtWidgets.QLabel()
                    #
                    if db.studio.studio_database=='django':
                        # img
                        icon_path = self.get_cache_path_from_url(artist.profile.get('image'))
                        if icon_path:
                            image = QtGui.QImage(icon_path)
                            pix = QtGui.QPixmap(image)
                            #
                            label.setPixmap(pix)
                            label.show()
                        else:
                            label.setText('no image')
                    else:
                        label.setText('no image')
                    
                    label.artist = artist
                    self.myWidget.studio_editor_table.setCellWidget(i, j, label)
                else:
                    newItem.setText(getattr(artist, key))
                newItem.artist = artist
                if key == 'username':
                    color = self.artist_color
                    brush = QtGui.QBrush(color)
                    newItem.setBackground(brush)                
                self.myWidget.studio_editor_table.setItem(i, j, newItem)

        self.myWidget.studio_editor_table.resizeRowsToContents()
        self.myWidget.studio_editor_table.resizeColumnsToContents()
        
        print('fill active artist table')
        
    def fill_active_artist_table_for_workroom(self, window, arg=False):
        artists = self.artist.read_artists('all')
        if not artists[0]:
            return
        filter_ = window.name_filter.text().lower()
        wr_name = window.dialog_comboBox_1.currentText()
        #
        active_artists = []
        #
        if wr_name and wr_name != '-- all --':
            wr_id = self.db_workroom.dict_by_name[wr_name].id
            self.clear_table(window.select_from_list_data_list_table)
            for artist in artists[1]:
                if artist.status == 'active' and wr_id in artist.workroom:
                    if not filter_ or filter_ in artist.username:
                        active_artists.append(artist)
        elif not wr_name or wr_name == '-- all --':
            # get active list
            for artist in artists[1]:
                if artist.status == 'active':
                    if not filter_ or filter_ in artist.username:
                        active_artists.append(artist)
                
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
            if artist.workroom:
                wr_list = artist.workroom
            for j,key in enumerate(headers):
                if not (key in self.look_keys):
                    continue
                newItem = QtWidgets.QTableWidgetItem()
                if key=='outsource':
                    newItem.setText(str(getattr(artist, key)))
                elif key == 'icon':
                    # label
                    label = QtWidgets.QLabel()
                    #
                    if db.studio.studio_database=='django':
                        # img
                        icon_path = self.get_cache_path_from_url(artist.profile.get('image'))
                        if icon_path:
                            image = QtGui.QImage(icon_path)
                            pix = QtGui.QPixmap(image)
                            #
                            label.setPixmap(pix)
                            label.show()
                        else:
                            label.setText('no image')
                    else:
                        label.setText('no image')
                    
                    label.artist = artist
                    window.select_from_list_data_list_table.setCellWidget(i, j, label)
                else:
                    newItem.setText(getattr(artist, key))
                newItem.artist = artist
                if key == 'username' and not self.workroom.id in wr_list:
                    color = self.artist_color
                    brush = QtGui.QBrush(color)
                    newItem.setBackground(brush)
                elif self.workroom.id in wr_list:
                    color = self.grey_color
                    brush = QtGui.QBrush(color)
                    newItem.setBackground(brush)
                
                window.select_from_list_data_list_table.setItem(i, j, newItem)

        window.select_from_list_data_list_table.resizeRowsToContents()
        window.select_from_list_data_list_table.resizeColumnsToContents()
        
        print('fill active artist table')
        
    def add_select_artists_to_workroom(self, window):
        table = window.select_from_list_data_list_table
        column = table.columnCount()
        #
        name_column = None # номер колонки с именем
        for i in range(0, column):
            head_item = table.horizontalHeaderItem(i)
            if head_item.text() == 'username':
                name_column = i
                break
        
        # get selected rows
        selected = table.selectedItems()
        artists = []
        for item in selected:
            if item.column() == name_column:
                artists.append(item.artist)
        
        #wr_id = self.workroom.get('id')
        
        for artist in artists:
            workrooms = []
            if artist.workroom:
                workrooms = artist.workroom
            
            if not self.workroom.id in workrooms:
                workrooms.append(self.workroom.id)
                #keys = {'username': artist_, 'workroom' : json.dumps(workrooms)}
                keys = {'username': artist.username, 'workroom' : workrooms}
                bool_, return_data = artist.edit_artist(keys, self.artist)
                if not bool_:
                    self.message(return_data, 2)
                
            #print(self.workroom.id, workrooms)
                
        self.fill_active_artist_table_for_workroom(window)
        self.fill_active_artist_table_at_workroom()
        
        # get artist data
        #self.get_artist_data()
        
        #
        print('add artists to workroom "%s"' % self.workroom.name)
        
        
    def remove_artists_from_workroom_action(self, table):
        column = table.columnCount()
        name_column = None
        for i in range(0, column):
            head_item = table.horizontalHeaderItem(i)
            if head_item.text() == 'username':
                name_column = i
                break
        
        # get selected rows
        selected = table.selectedItems()
        artists = []
        for item in selected:
            if item.column() == name_column:
                artists.append(item.artist)
                
        #wr_id = self.workroom.get('id')
        
        # remove artist from workroom
        b,r=self.workroom.remove_artists(artists)
        if not b:
            self.message(f'{r}\n Look the terminal!', 2)
            return
               
        # get artist data
        self.get_artist_data()
                
        self.fill_active_artist_table_at_workroom()
        print('remove select artists from workroom "%s"' % self.workroom.name)
        
    # ******************* STUDIO EDITOR /// PROJECT EDITOR ****************************
    def edit_ui_to_project_editor(self):
        pass
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
        self.myWidget.studio_butt_3.clicked.connect(partial(self.rename_project_ui))
        self.myWidget.studio_butt_4.setVisible(True)
        self.myWidget.studio_butt_4.setText('Remove')
        try:
            self.myWidget.studio_butt_4.clicked.disconnect()
        except:
            pass
        self.myWidget.studio_butt_4.clicked.connect(self.remove_project_action)
        self.myWidget.studio_butt_5.setVisible(True)
        self.myWidget.studio_butt_5.setText('Deactivate')
        try:
            self.myWidget.studio_butt_5.clicked.disconnect()
        except:
            pass
        self.myWidget.studio_butt_5.clicked.connect(partial(self.edit_status_project_action, 'none'))
        self.myWidget.studio_butt_6.setVisible(True)
        self.myWidget.studio_butt_6.setText('Set Active')
        try:
            self.myWidget.studio_butt_6.clicked.disconnect()
        except:
            pass
        self.myWidget.studio_butt_6.clicked.connect(partial(self.edit_status_project_action, 'active'))
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
        self.myWidget.studio_editor_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.myWidget.studio_editor_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
        self.reload_project_list()
        
    def reload_project_list(self):
        self.clear_table()
        self.fill_project_table(self.myWidget.studio_editor_table)
        
    def fill_project_table(self, table):
        pass
        self.project.get_list() # ?
        
        # get table data
        columns = ('name', 'fps', 'units', 'status', 'path')
        num_row = len(self.project.list_projects)
        num_column = len(columns)
        headers = columns
        
        # make table
        table.setColumnCount(num_column)
        table.setRowCount(num_row)
        table.setHorizontalHeaderLabels(headers)
    
        
        # fill table
        for i, project in enumerate(self.project.list_projects):
            for j,key in enumerate(headers):
                newItem = QtWidgets.QTableWidgetItem()
                newItem.setText(str(getattr(project, key)))
                newItem.project = project
                if key == 'name':
                    color = self.project_color
                    brush = QtGui.QBrush(color)
                    newItem.setBackground(brush)
    
                table.setItem(i, j, newItem)
        
        table.resizeRowsToContents()
        table.resizeColumnsToContents()
        
        table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self._project_editor_context_menu)
        
        print('fill project table')
        
    def _project_editor_context_menu(self, pos):
        pass
        #print(pos.__reduce__())
        table = self.myWidget.studio_editor_table
        item = table.selectedItems()[0]
        #print(item.column_name)
        menu = QtWidgets.QMenu(table)
        menu_items = ['Rename', 'Set Fps', 'Set Units', 'Remove', 'Deactivate', 'Set Active']
        for label in menu_items:
            action = menu.addAction(label)
            action.triggered.connect(partial(self._project_editor_context_menu_action, label, item))
        menu.exec_(QtGui.QCursor.pos())
        
    def _project_editor_context_menu_action(self, label, item):
        pass
        if label=='Rename':
            self.rename_project_ui(project=item.project)
        elif label=='Set Fps':
            self.set_fps_ui(project=item.project)
        elif label=='Set Units':
            self.set_units_ui(project=item.project)
        elif label=='Remove':
            self.remove_project_action(project=item.project)
        elif label=='Deactivate':
            self.edit_status_project_action('none', project=item.project)
        elif label=='Set Active':
            self.edit_status_project_action('active', project=item.project)
            
    def new_project_ui(self):
        pass
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
        pass
        # get data
        name = window.priject_name_field.text()
        path = window.set_project_folder.text()
        
        result = self.project.add_project(name, path)
        if not result[0]:
            self.message(result[1], 3)
            return
        
        self.reload_project_list()
        self.close_window(window)
        
        self.tm_fill_project_list()
        
    def rename_project_ui(self, project=False):
        pass
        if not project:
            # get selected rows
            table = self.myWidget.studio_editor_table
            selected = table.selectedItems()
                            
            if not selected:
                self.message('Not Selected Project', 2)
                return
            project = selected[0].project
            
        self.selected_project = project
        
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.new_dialog_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.setProjectDialog = loader.load(file, self)
        file.close()
        
        # edit widget
        window.setWindowTitle(('Rename Project: ' + self.selected_project.name))
        window.new_dialog_label.setText('New Name:')
        window.new_dialog_name.setText(self.selected_project.name)
        window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.new_dialog_ok.clicked.connect(partial(self.rename_project_action, window))
        
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()
        print('new project ui', self.selected_project.name)
        
    def rename_project_action(self, window):
        pass
        # get data
        new_name = window.new_dialog_name.text()
                    
        result = self.selected_project.rename_project(new_name)
        if not result[0]:
            self.message(result[1], 2)
            return
        
        self.clear_table()
        self.fill_project_table(self.myWidget.studio_editor_table)
        self.close_window(window)
        
        self.tm_fill_project_list()
        
    def set_fps_ui(self, project=False):
        pass
        if not project:
            # get selected rows
            table = self.myWidget.studio_editor_table
            selected = table.selectedItems()
                            
            if not selected:
                self.message('Not Selected Project', 2)
                return
            project = selected[0].project
            
        self.selected_project = project
        
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.new_dialog_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.setProjectDialog = loader.load(file, self)
        file.close()
        
        # edit widget
        window.setWindowTitle(('Set Fps for Project: %s' % self.selected_project.name))
        window.new_dialog_label.setText('New Fps:')
        #window.new_dialog_name.setText(str(self.selected_project.fps))
        window.new_dialog_name.setMaxLength(3)
        window.new_dialog_name.setValidator(QtGui.QIntValidator(1, 100))
        window.new_dialog_name.setText(unicode(int(self.selected_project.fps)))
        window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.new_dialog_ok.clicked.connect(partial(self.set_fps_action, window))
        
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()
        print('new project ui', self.selected_project.name)
    
    def set_fps_action(self, window):
        pass
        fps = window.new_dialog_name.text()
        b, r = self.selected_project.change_fps(fps)
        if not b:
            self.message(r, 2)
        
        self.clear_table()
        self.fill_project_table(self.myWidget.studio_editor_table)
        self.close_window(window)
        self.tm_fill_project_list()
    
    def set_units_ui(self, project=False):
        pass
        if not project:
            # get selected rows
            table = self.myWidget.studio_editor_table
            selected = table.selectedItems()
                            
            if not selected:
                self.message('Not Selected Project', 2)
                return
            project = selected[0].project
            
        self.selected_project = project
        
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.new_dialog_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.setProjectDialog = loader.load(file, self)
        file.close()
        
        # edit widget
        window.setWindowTitle(('Set Units for Project: %s' % self.selected_project.name))
        window.new_dialog_label.setText('New Units:')
        
        window.new_dialog_name.setVisible(False)
        
        window.units_combo = QtGui.QComboBox()
        window.units_combo.addItems(self.db_studio.PROJECTS_UNITS)
        window.horizontalLayout.addWidget(window.units_combo)
        
        window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.new_dialog_ok.clicked.connect(partial(self.set_units_action, window))
        
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()
    
    def set_units_action(self, window):
        pass
        units = window.units_combo.currentText()
        b, r = self.selected_project.change_units(units)
        if not b:
            self.message(r, 2)
    
        self.clear_table()
        self.fill_project_table(self.myWidget.studio_editor_table)
        self.close_window(window)
        self.tm_fill_project_list()
        
    def remove_project_action(self, project=False):
        if not project:
            table = self.myWidget.studio_editor_table
            selected = table.selectedItems()
                            
            if not selected:
                self.message('Not Selected Project', 2)
                return
            project = selected[0].project
        
        self.selected_project = project
        
        ask = self.message('Are you sure you want to delete the project - "%s"?' % self.selected_project.name, 0)
        if not ask:
            return
        
        result = self.selected_project.remove_project()
        if not result[0]:
            self.message(result[1], 2)
            return
        
        self.reload_project_list()
        
        self.tm_fill_project_list()
        
    def edit_status_project_action(self, status,  project=False):
        pass
        if not project:
            table = self.myWidget.studio_editor_table
            selected = table.selectedItems()
                            
            if not selected:
                self.message('Not Selected Project', 2)
                return
            project = selected[0].project
        
        self.selected_project = project
        
        if self.selected_project.status == status:
            self.message('This project already has status "%s"' % status, 2)
            return
        
        ask = self.message('Change project(%s) status to "%s"?' % (self.selected_project.name, status), 0)
        if not ask:
            return
        
        result = self.selected_project.edit_status(status)
        if not result[0]:
            self.message(result[1], 2)
            return
        
        self.reload_project_list()
        self.tm_fill_project_list()
        print('deactivate project action')
        
    # ******************* STUDIO EDITOR /// SET OF TASKS EDITOR ****************************
    
    def edit_ui_to_set_of_tasks_editor(self):
        pass
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
        self.myWidget.studio_editor_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.myWidget.studio_editor_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
        self.clear_table()
        self.fill_set_of_tasks_table(self.myWidget.studio_editor_table)
        
    def fill_set_of_tasks_table(self, table):
        pass        
        # get data list
        b, r = self.db_set_of_tasks.get_dict_by_all_types()
        if not b:
            print('***')
            print(r)
            return
        
        data_to_fill = []
        for key in sorted(r.keys()):
            for name in sorted(r[key].keys()):
                data_to_fill.append(r[key][name])
                
        self.set_of_tasks_list = data_to_fill
        
        # get table data
        columns = ('name', 'asset_type', 'loading_type',  'edit_time')
        num_row = len(data_to_fill)
        num_column = len(columns)
        headers = columns
        
        # make table
        table.setColumnCount(num_column)
        table.setRowCount(num_row)
        table.setHorizontalHeaderLabels(headers)
    
        
        # fill table
        for i, data in enumerate(data_to_fill):
            for j,key in enumerate(headers):
                newItem = QtWidgets.QTableWidgetItem()
                if key == 'edit_time':
                    newItem.setText(getattr(data, key).strftime("%d-%m-%Y %H:%M:%S"))
                else:
                    if not getattr(data, key):
                        newItem.setText('')
                    else:
                        newItem.setText(str(getattr(data, key)))
                newItem.set_of_tasks = data
                if key == 'name':
                    color = self.set_of_tasks_color
                    brush = QtGui.QBrush(color)
                    newItem.setBackground(brush)
    
                table.setItem(i, j, newItem)
                
        table.resizeRowsToContents()
        table.resizeColumnsToContents()
                
        table.itemDoubleClicked.connect(partial(self.pre_edit_set_of_tasks_ui, self.myWidget.studio_editor_table))
        
        # context menu
        table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self._set_of_tasks_context_menu)
                    
        print('fill set of tasks table')
        
    def _set_of_tasks_context_menu(self, pos):
        pass
        #print(pos.__reduce__())
        table = self.myWidget.studio_editor_table
        item = table.selectedItems()[0]
        #print(item.column_name)
        menu = QtWidgets.QMenu(table)
        menu_items = ['Rename','Edit of Asset Type', 'Edit of Loading Type', 'Make Copy', 'Edit', 'Remove']
        for label in menu_items:
            action = menu.addAction(label)
            action.triggered.connect(partial(self._set_of_tasks_context_menu_action, label, item))
        menu.exec_(QtGui.QCursor.pos())
        
    def _set_of_tasks_context_menu_action(self, label, item):
        pass
        #print(label, item.set_of_tasks.name)
        if label=='Rename':
            self.rename_set_of_tasks_ui(False, set_of_tasks=item.set_of_tasks)
        elif label=='Edit of Asset Type':
            self.edit_asset_type_ui(False, set_of_tasks=item.set_of_tasks)
        elif label=='Edit of Loading Type':
            self.edit_loading_type_ui(False, set_of_tasks=item.set_of_tasks)
        elif label=='Make Copy':
            self.copy_set_of_tasks_ui(set_of_tasks=item.set_of_tasks)
        elif label=='Edit':
            self.edit_set_of_tasks_ui(False, set_of_tasks=item.set_of_tasks)
        elif label=='Remove':
            self.remove_set_of_tasks_action(False, set_of_tasks=item.set_of_tasks)
        
    def reload_set_of_tasks_list(self):
        self.clear_table()
        self.fill_set_of_tasks_table(self.myWidget.studio_editor_table)
        
    def new_set_of_tasks_ui(self):
        pass
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
        pass
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
        
    # set_of_tasks (set_of_tasks) - если False, то изменяемый объект будет доставаться из table.currentItem().set_of_tasks
    def copy_set_of_tasks_ui(self, set_of_tasks=False):
        if not set_of_tasks:
            current_set = self.myWidget.studio_editor_table.currentItem().set_of_tasks
        else:
            current_set=set_of_tasks
        
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.new_dialog_path)
        file.open(QtCore.QFile.ReadOnly)
        window = self.setProjectDialog = loader.load(file, self)
        file.close()
        
        # edit widget
        window.setWindowTitle(('Make Copy: %s' % current_set.name))
        window.new_dialog_label.setText('New Name of Set:')
        window.new_dialog_name.setText(current_set.name)
        window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.new_dialog_ok.clicked.connect(partial(self.copy_set_of_tasks_action, window, current_set))
        
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()
    
    def copy_set_of_tasks_action(self, window, current_set):
        pass
        
        # get new_name
        new_name = window.new_dialog_name.text()
                    
        b, data = current_set.copy(new_name)
        if not b:
            self.message(data, 3)
            return
        
        self.reload_set_of_tasks_list()
        window.close()
        
    # table (QtGui.QTable / False) - если передаём set_of_tasks, то вместо table передаём False, он всё равно использоваться не будет
    # set_of_tasks (set_of_tasks) - если False, то изменяемый объект будет доставаться из table.selectedItems.set_of_tasks
    def rename_set_of_tasks_ui(self, table, set_of_tasks=False):
        pass
        if not set_of_tasks:
            #name = lists[0]
            if not table.selectedItems():
                self.message('Not Selected Set', 2)
                return
            current_set = table.selectedItems()[0].set_of_tasks
        else:
            current_set=set_of_tasks
        
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.new_dialog_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.setProjectDialog = loader.load(file, self)
        file.close()
        
        # edit widget
        window.setWindowTitle(('Rename: %s' % current_set.name))
        window.new_dialog_label.setText('New Name of Set:')
        window.new_dialog_name.setText(current_set.name)
        window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.new_dialog_ok.clicked.connect(partial(self.rename_set_of_tasks_action, current_set, window))
        
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()
        
        print('rename set of tasks ui')
        
    def rename_set_of_tasks_action(self, current_set, window):
        pass
        # get data
        new_name = window.new_dialog_name.text()
        
        # rename
        #copy = db.set_of_tasks()
        result = current_set.rename(new_name)
        
        if not result[0]:
            self.message(result[1], 2)
            return
        
        self.close_window(window)
        self.reload_set_of_tasks_list()
        print('rename set action')
        
    # table (QtGui.QTable / False) - если передаём set_of_tasks, то вместо table передаём False, он всё равно использоваться не будет
    # set_of_tasks (set_of_tasks) - если False, то изменяемый объект будет доставаться из table.selectedItems.set_of_tasks
    def remove_set_of_tasks_action(self, table, set_of_tasks=False):
        pass
        if not set_of_tasks:
            #name = lists[0]
            if not table.selectedItems():
                self.message('Not Selected Set', 2)
                return
            current_set = table.selectedItems()[0].set_of_tasks
        else:
            current_set=set_of_tasks
        
        # ask
        ask = self.message('You Are Soure?', 0)
        if not ask:
            return
        
        # remove
        #copy = db.set_of_tasks()
        result = current_set.remove()
        
        if not result[0]:
            self.message(result[1], 2)
            return
                
        self.reload_set_of_tasks_list()
        print('remove set of tasks ui')
        
    def pre_edit_set_of_tasks_ui(*args):
        args[0].edit_set_of_tasks_ui(args[1])
    
    # table (QtGui.QTable / False) - если передаём set_of_tasks, то вместо table передаём False, он всё равно использоваться не будет
    # geometry (QGeometry) - геометрия окна
    # set_of_tasks (set_of_tasks) - если False, то изменяемый объект будет доставаться из table.selectedItems()[0].set_of_tasks
    def edit_set_of_tasks_ui(self, table, geometry = False, set_of_tasks=False):
        pass
        if not set_of_tasks:
            #name = lists[0]
            if not table.selectedItems():
                self.message('Not Selected Set', 2)
                return
            self.selected_set_of_tasks = current_set = table.selectedItems()[0].set_of_tasks
        else:
            self.selected_set_of_tasks = current_set = set_of_tasks
                
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.select_from_list_dialog_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.selectWorkroomDialog = loader.load(file, self)
        file.close()
        
        # fill table
        right_data = current_set.sets
        asset_type = current_set.asset_type
            
        # -- get table data
        num_row = 100
        num_column = len(current_set.sets_keys)
        headers = current_set.sets_keys
            
        # -- make table
        window.select_from_list_data_list_table.setColumnCount(num_column)
        window.select_from_list_data_list_table.setRowCount(num_row)
        window.select_from_list_data_list_table.setHorizontalHeaderLabels(headers)
        
        # -- edit table
        window.select_from_list_data_list_table.setDragEnabled(True)
        window.select_from_list_data_list_table.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        
        # context menu
        #window.select_from_list_data_list_table.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
        table = window.select_from_list_data_list_table
        table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self._edit_set_of_tasks_context_menu)
    
        # fill table
        for i, set_of_tasks in enumerate(right_data):
            for j,key in enumerate(headers):
                if not (key in current_set.sets_keys):
                    continue
                newItem = QtWidgets.QTableWidgetItem()
                try:
                    newItem.setText(set_of_tasks[key])
                except:
                    pass
                if key == 'task_name':
                    color = self.tasks_color
                    brush = QtGui.QBrush(color)
                    newItem.setBackground(brush)
                    
                newItem.column_name = key
                                
                window.select_from_list_data_list_table.setItem(i, j, newItem)
        
        # fill empty items
        for i in range(len(right_data), num_row):
            for j in range(0, num_column):
                newItem = QtWidgets.QTableWidgetItem()
                newItem.column_name = headers[j]
                window.select_from_list_data_list_table.setItem(i, j, newItem)
                
        # edit widjet
        window.setWindowTitle(('Edit Set Of Tasks: %s' % current_set.name))
        window.select_from_list_cansel_button.clicked.connect(partial(self.close_window, window))
        window.select_from_list_apply_button.setText('Save Data')
        window.select_from_list_apply_button.clicked.connect(partial(self.edit_set_of_tasks_action, window, window.select_from_list_data_list_table, current_set))
        
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        if geometry:
            window.setGeometry(geometry)
        else:
            window.resize(1000, 412)
            
        window.show()
        
    def _edit_set_of_tasks_context_menu(self, pos):
        pass
        #print(pos.__reduce__())
        item = self.selectWorkroomDialog.select_from_list_data_list_table.selectedItems()[0]
        #print(item.column_name)
        menu = QtWidgets.QMenu(self.selectWorkroomDialog.select_from_list_data_list_table)
        
        menu_items = []
        if item.column_name == 'extension':
            menu_items = self.db_set_of_tasks.EXTENSIONS
        elif item.column_name == 'task_type':
            menu_items = self.db_set_of_tasks.task_types
        elif item.column_name == 'activity':
            list_activity = list(self.db_asset.ACTIVITY_FOLDER[self.selected_set_of_tasks.asset_type].keys())
            list_activity.sort()
            menu_items = list_activity
        elif item.column_name == 'input':
            menu_items = self.db_set_of_tasks.service_tasks
            exists_tasks = []
            for task_data in self.selected_set_of_tasks.sets:
                exists_tasks.append(task_data.get('task_name'))
            menu_items = list(menu_items) + exists_tasks
            
        menu_items = list(menu_items) + ['Copy','Paste','Delete']
            
        for label in menu_items:
            action = menu.addAction(label)
            action.triggered.connect(partial(self._edit_set_of_tasks_context_menu_action, label, item))
                
        menu.exec_(QtGui.QCursor.pos())
        
    def _edit_set_of_tasks_context_menu_action(self, text, item):
        if text == 'Delete':
            item.setText('')
        elif text == 'Copy':
            clipboard = QtGui.QApplication.clipboard()
            clipboard.setText(item.text())
        elif text=='Paste':
            clipboard = QtGui.QApplication.clipboard()
            text = clipboard.text()
            item.setText(text)
        else:
            item.setText(text)

    def edit_set_of_tasks_action(self, window, table, current_set):
        pass
            
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
        result, reply = current_set.edit_sets(data)
        if not result:
            self.message(reply, 3)
        
        geometry = window.frameGeometry()
        
        self.close_window(window)
        #self.reload_set_of_tasks_list()
        self.edit_set_of_tasks_ui(self.myWidget.studio_editor_table, geometry = geometry)
        print('edit set of tasks action')
        
    def save_set_of_task_to_library_ui(self, action = 'all'):
        home = os.path.expanduser('~')
        path, f = QtWidgets.QFileDialog.getSaveFileName(self, caption = 'Save Set_Of_Tasks To Library',  dir = home, filter = u'Json files (*.json)')
        
        split = os.path.splitext(path)
        
        if not split[1]:
            path = db.NormPath(path + '.json')
        else:
            if split[1] != '.json':
                path = db.NormPath(split[0] + '.json')
        
        self.save_set_of_task_to_library_action(path, self.set_of_tasks_list)
        
    def save_set_of_task_to_library_action(self, path, save_objects):
        result = self.db_set_of_tasks.save_to_library(path)
        if not result[0]:
            self.message(result[1], 3)
                
    def load_set_of_task_from_library_ui(self):
        home = os.path.expanduser('~')
        path, f = QtWidgets.QFileDialog.getOpenFileNames(self, caption = 'Load Set_Of_Tasks Library',  dir = home, filter = u'Json files (*.json)')
        
        
        b, data = self.db_set_of_tasks.get_list(path = path[0])
        
        if not b:
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
        window.select_from_list_data_list_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        window.select_from_list_data_list_table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        
        columns = ['name','asset_type', 'loading_type']
        
        # -- get table data
        num_row = len(data)
        num_column = len(columns)
        headers = columns
            
        # -- make table
        table = window.select_from_list_data_list_table
        table.setColumnCount(num_column)
        table.setRowCount(num_row)
        table.setHorizontalHeaderLabels(headers)
        
        # fill table
        for i, set_ob in enumerate(data):
            for j,key in enumerate(headers):
                newItem = QtWidgets.QTableWidgetItem()
                
                if key == 'name':
                    color = self.set_of_tasks_color
                    brush = QtGui.QBrush(color)
                    newItem.setBackground(brush)
                    newItem.setText(set_ob.name)
                #elif key == 'asset_type':
                else:
                    newItem.setText(getattr(set_ob, key))
                    
                newItem.set_of_tasks = set_ob
    
                table.setItem(i, j, newItem)
                
        # connect buttons
        window.pushButton_01.setText('Load Selected')
        window.pushButton_02.setText('Load All')
        window.select_from_list_cansel_button.clicked.connect(partial(self.close_window, window))
        window.pushButton_01.clicked.connect(partial(self.load_set_of_task_from_library_action, window, data, 'selected'))
        window.pushButton_02.clicked.connect(partial(self.load_set_of_task_from_library_action, window, data, 'all'))
        
        # context menu
        table.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
        addgrup_action = QtWidgets.QAction( 'Look Set_of_Tasks', self.myWidget)
        addgrup_action.triggered.connect(partial(self.look_set_of_task_from_library, table))
        table.addAction( addgrup_action )
        
        window.show()
        
    def load_set_of_task_from_library_action(self, window, data, action):
        if action == 'selected':
            data = []
            names = []
            for item in window.select_from_list_data_list_table.selectedItems():
                if not item.set_of_tasks.name in names:
                    data.append(item.set_of_tasks)
                    names.append(item.set_of_tasks.name)
        elif action == 'all':
            pass
        
        for ob in data:
            b, r = self.db_set_of_tasks.create(ob.name, ob.asset_type, loading_type=ob.loading_type, keys=ob.sets, force=True)
            if not b:
                self.message(r, 3)
        
        self.reload_set_of_tasks_list()
        window.close()
        
    def look_set_of_task_from_library(self, table):
        set_ob = table.currentItem().set_of_tasks
        
        right_data = set_ob.sets
        
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.select_from_list_dialog_path)
        file.open(QtCore.QFile.ReadOnly)
        window = self.selectWorkroomDialog = loader.load(file, self)
        file.close()
        
        # -- get table data
        num_row = len(right_data)
        num_column = len(self.db_set_of_tasks.sets_keys)
        headers = self.db_set_of_tasks.sets_keys
            
        # -- make table
        window.select_from_list_data_list_table.setColumnCount(num_column)
        window.select_from_list_data_list_table.setRowCount(num_row)
        window.select_from_list_data_list_table.setHorizontalHeaderLabels(headers)
        
        # fill table
        for i, set_of_tasks in enumerate(right_data):
            for j,key in enumerate(headers):
                if not (key in self.db_set_of_tasks.sets_keys):
                    continue
                newItem = QtWidgets.QTableWidgetItem()
                try:
                    newItem.setText(set_of_tasks[key])
                except:
                    pass
                if key == 'task_name':
                    color = self.tasks_color
                    brush = QtGui.QBrush(color)
                    newItem.setBackground(brush)
                                
                window.select_from_list_data_list_table.setItem(i, j, newItem)
        
        # edit widjet
        window.setWindowTitle(('Set Of Tasks: ' + set_ob.name))
        window.select_from_list_cansel_button.clicked.connect(partial(self.close_window, window))
        window.select_from_list_apply_button.setVisible(False)
        
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()
    
    def edit_loading_type_ui(self, table, set_of_tasks=False):
        pass
        if not set_of_tasks:
            #name = lists[0]
            if not table.selectedItems():
                self.message('Not Selected Set', 2)
                return
            current_set = table.selectedItems()[0].set_of_tasks
        else:
            current_set=set_of_tasks
        
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.combo_dialog_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.setProjectDialog = loader.load(file, self)
        file.close()
        
        # edit widget
        #copy = db.studio()
        window.setWindowTitle(('Edit of Loading Type: %s' % current_set.name))
        window.combo_dialog_label.setText('New Loading Type:')
        window.combo_dialog_combo_box.addItems(current_set.loading_types)
        window.combo_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.combo_dialog_ok.clicked.connect(partial(self.edit_loading_type_action, current_set, window))
        
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()
        print('edit loading type')
        
    def edit_loading_type_action(self, ob, window):
        pass
        #copy = db.set_of_tasks()
        b, message = ob.edit_loading_type(window.combo_dialog_combo_box.currentText())
        if not b:
            self.message(message, 2)
        
        self.close_window(window)
        self.reload_set_of_tasks_list()
        print('edit loading type action')
    
    # table (QtGui.QTable / False) - если передаём set_of_tasks, то вместо table передаём False, он всё равно использоваться не будет
    # set_of_tasks (set_of_tasks) - если False, то изменяемый объект будет доставаться из table.selectedItems.set_of_tasks
    def edit_asset_type_ui(self, table, set_of_tasks=False):
        pass
        if not set_of_tasks:
            #name = lists[0]
            if not table.selectedItems():
                self.message('Not Selected Set', 2)
                return
            current_set = table.selectedItems()[0].set_of_tasks
        else:
            current_set=set_of_tasks
        
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.combo_dialog_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.setProjectDialog = loader.load(file, self)
        file.close()
        
        # edit widget
        #copy = db.studio()
        window.setWindowTitle(('Edit Asset Type: ' + current_set.name))
        window.combo_dialog_label.setText('New Name of Set:')
        window.combo_dialog_combo_box.addItems(current_set.asset_types)
        window.combo_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.combo_dialog_ok.clicked.connect(partial(self.edit_asset_type_action, current_set, window))
        
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()
        print('edit asset type')
        
    def edit_asset_type_action(self, ob, window):
        pass
        #copy = db.set_of_tasks()
        ob.edit_asset_type(window.combo_dialog_combo_box.currentText())
        
        self.close_window(window)
        self.reload_set_of_tasks_list()
        print('edit asset type action')
        
    
    # ******************* STUDIO EDITOR /// SEASON EDITOR ****************************
    
    def edit_ui_to_season_editor(self):
        window = self.myWidget
        table = window.studio_editor_table
            
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
        window.studio_editor_label.setText('Season Editor')
                
        # edit button
        button01.setVisible(True)
        button01.setText('Reload')
        try:
            button01.clicked.disconnect()
        except:
            pass
        button01.clicked.connect(partial(self.reload_season_list, table))
        button02.setVisible(True)
        button02.setText('Create')
        try:
            button02.clicked.disconnect()
        except:
            pass
        button02.clicked.connect(self.new_season_ui)
        button03.setVisible(True)
        button03.setText('Rename')
        try:
            button03.clicked.disconnect()
        except:
            pass
        button03.clicked.connect(self.rename_season_ui)
        button04.setVisible(False)
        button05.setVisible(False)
        button06.setVisible(False)
        button07.setVisible(False)
        button08.setVisible(False)
        button09.setVisible(False)
        button10.setVisible(False)
        
        # edit combobox
        projects = ['-- select project --'] + self.project.list_active_projects
        window.set_comboBox_01.setVisible(True)
        window.set_comboBox_01.clear()
        window.set_comboBox_01.addItems(projects)
        if self.selected_project and self.selected_project.name:
            window.set_comboBox_01.setCurrentIndex(projects.index(self.selected_project.name))
        try:
            window.set_comboBox_01.activated[str].disconnect()
        except:
            pass
        window.set_comboBox_01.activated[str].connect(self.fill_season_table)
        window.set_comboBox_02.setVisible(False)
        window.set_comboBox_03.setVisible(False)
        
        # edit table
        #self.myWidget.studio_editor_table_2.setVisible(False)
        self.myWidget.right_table_frame.setVisible(False)
        # -- selection mode   
        table.setSortingEnabled(True)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
        self.reload_season_list(table)
        
    def default_state_season_table(self, table):
        pass
        # get table data
        columns = self.SEASON_COLUMNS
        num_row = 0
        num_column = len(columns)
        headers = columns
        
        # make table
        table.setColumnCount(num_column)
        table.setRowCount(num_row)
        table.setHorizontalHeaderLabels(headers)
        
        #  edit label
        self.myWidget.studio_editor_label.setText('Season Editor')
        
        print('season table to default state')
        
    def reload_season_list(self, table):
        pass
        self.clear_table()
        
        # get project
        project_name = self.myWidget.set_comboBox_01.currentText()
        print('*** reload_season_list()')
                
        if project_name == '-- select project --':
            self.default_state_season_table(table)
        else:
            pass
            self.fill_season_table(project_name)
        
    def fill_season_table(self, *args):
        table = self.myWidget.studio_editor_table
        project_name = args[0]
        
        if project_name == '-- select project --':
            self.selected_project = None
            self.default_state_season_table(table)
            return
            
        else:
            self.selected_project = self.project.dict_projects[project_name]
            
        # get table data
        seasons = None
        self.db_season.project = self.selected_project
        result = self.db_season.get_list()
        if result[0]:
            seasons = result[1]
            
        if not seasons:
            self.default_state_season_table(table)
            return
        
        columns = self.SEASON_COLUMNS
        num_row = len(seasons)
        num_column = len(columns)
        headers = columns
        
        # make table
        table.setColumnCount(num_column)
        table.setRowCount(num_row)
        table.setHorizontalHeaderLabels(headers)
    
        # fill table
        for i, data in enumerate(seasons):
            for j,key in enumerate(headers):
                newItem = QtWidgets.QTableWidgetItem()
                newItem.setText(getattr(data, key))
                if key == 'name':
                    color = self.season_color
                    brush = QtGui.QBrush(color)
                    newItem.setBackground(brush)
    
                newItem.season = data
                table.setItem(i, j, newItem)
                
        #  edit label
        self.myWidget.studio_editor_label.setText(('Season Editor / "%s"' % project_name))
        
        table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self._season_editor_context_menu)
        
        table.resizeRowsToContents()
        table.resizeColumnsToContents()
        
        print('fill season table')
        
    def _season_editor_context_menu(self, pos):
        pass
        table = self.myWidget.studio_editor_table
        item = table.currentItem()
        #print(item.column_name)
        menu = QtWidgets.QMenu(table)
        menu_items = ['Rename']
        for label in menu_items:
            action = menu.addAction(label)
            action.triggered.connect(partial(self._season_editor_context_menu_action, label, item))
        menu.exec_(QtGui.QCursor.pos())
        
    def _season_editor_context_menu_action(self, label, item):
        pass
        if label=='Rename':
            self.rename_season_ui(season=item.season)
        
    def new_season_ui(self):
        pass
        # get project
        #project = self.myWidget.set_comboBox_01.currentText()
        if not self.selected_project: #project == '-- select project --':
            self.message('Project Not Specified!', 2)
            return
        
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.new_dialog_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.createSeasonDialog = loader.load(file, self)
        file.close()
        
        # edit widget
        window.setWindowTitle(('Create Season to "%s"' % self.selected_project.name))
        window.new_dialog_label.setText('Name of Season:')
        window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.new_dialog_ok.clicked.connect(partial(self.new_season_action, window))
                
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()
        
        print('new season ui')
        
    def new_season_action(self, window):
        pass
        #copy = db.season()
        #result = copy.create(project, window.new_dialog_name.text())
        self.db_season.project = self.selected_project
        result = self.db_season.create(window.new_dialog_name.text())
        
        if not result[0]:
            self.message(result[1], 2)
            return
        
        self.reload_season_list(self.myWidget.studio_editor_table)
        self.close_window(window)
        print('new season action')
        
    def rename_season_ui(self, season=False):
        pass
        # get project
        table = self.myWidget.studio_editor_table
        project = self.myWidget.set_comboBox_01.currentText()
        if project == '-- select project --':
            self.message('Project not specified!', 3)
            return
        
        if not season:
            item = table.currentItem()
            if not item:
                self.message('No season selected!', 2)
                return
            self.selected_season = item.season
        else:
            self.selected_season=season
        
        
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.new_dialog_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.createSeasonDialog = loader.load(file, self)
        file.close()
        
        # edit widget
        window.setWindowTitle(('Rename Season: "%s"' % self.selected_season.name))
        window.new_dialog_label.setText('New name of season:')
        window.new_dialog_name.setText(self.selected_season.name)
        window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.new_dialog_ok.clicked.connect(partial(self.rename_season_action, window))
                
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()
        print('rename season ui')
    
    def rename_season_action(self, window):
        pass
        # get project
        project = self.myWidget.set_comboBox_01.currentText()
        if project == '-- select project --':
            self.message('Project not specified!', 2)
            return
        
        #new name
        new_name = window.new_dialog_name.text()
        if not new_name:
            self.message('"New name" not npecified!', 2)
            return
        elif self.selected_season.name == new_name:
            self.message('"New name" matches existing one!', 2)
            return
                
        # rename
        result = self.selected_season.rename(new_name)
        
        if not result[0]:
            self.message(result[1])
            return
            
        self.reload_season_list(self.myWidget.studio_editor_table)
        self.close_window(window)       
        print('rename season action')
        
    # ******************* STUDIO EDITOR /// GROUP EDITOR ****************************
    def edit_ui_to_group_editor(self):
        window = self.myWidget
        table = window.studio_editor_table
        
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
        button01.clicked.connect(self.fill_group_table)
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
        button03.clicked.connect(self.rename_group_ui)
        button04.setVisible(True)
        button04.setText('Edit Description')
        try:
            button04.clicked.disconnect()
        except:
            pass
        button04.clicked.connect(self.edit_description_group_ui)
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
        projects = ['-- select project --'] + self.project.list_active_projects
        window.set_comboBox_01.setVisible(True)
        window.set_comboBox_01.clear()
        window.set_comboBox_01.addItems(projects)
        if self.selected_project and self.selected_project.name:
            window.set_comboBox_01.setCurrentIndex(projects.index(self.selected_project.name))
        try:
            window.set_comboBox_01.activated[str].disconnect()
        except:
            pass
        window.set_comboBox_01.activated[str].connect(self.fill_group_table)
        # -- get type of asset list
        window.set_comboBox_02.setVisible(True)
        window.set_comboBox_02.clear()
        window.set_comboBox_02.addItems((['-all types-'] + self.db_studio.asset_types))
        try:
            window.set_comboBox_02.activated[str].disconnect()
        except:
            pass
        window.set_comboBox_02.activated[str].connect(self.fill_group_table)
        window.set_comboBox_03.setVisible(False)
        self.myWidget.group_search_qline.setVisible(False)
        
        # edit table
        #self.myWidget.studio_editor_table_2.setVisible(False)
        self.myWidget.right_table_frame.setVisible(False)
        # -- selection mode   
        table.setSortingEnabled(True)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
        if not self.selected_project:
            self.default_state_group_table(table)
        else:
            self.fill_group_table()
        
    def default_state_group_table(self, table):
        pass
        self.clear_table()
        # get table data
        columns = self.GROUP_COLUMNS
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
        pass
        table = self.myWidget.studio_editor_table
        self.clear_table()
        
        # ge filter    window.set_comboBox_02.addItems((['-all types-']
        f = self.myWidget.set_comboBox_02.currentText()
        if f == '-all types-':
            f = False
        
        if self.myWidget.set_comboBox_01.currentText() == '-- select project --':
            self.selected_project = None
            self.default_state_group_table(table)
            return
        else:
            self.selected_project = self.project.dict_projects[self.myWidget.set_comboBox_01.currentText()]
            self.db_season.project = self.selected_project
            self.db_season.get_list()
        
        # get table data
        self.db_group.project = self.selected_project
        groups = []
        b, r = self.db_group.get_list()
        if not b:
            self.message(r, 2)
            return
        
        if f:
            groups = self.db_group.dict_by_type[f]
        else:
            groups = self.db_group.list_group
        
        columns = self.GROUP_COLUMNS
        num_row = len(groups)
        num_column = len(columns)
        headers = columns
        
        # make table
        table.setColumnCount(num_column)
        table.setRowCount(num_row)
        table.setHorizontalHeaderLabels(headers)
    
        # fill table
        for i, ob in enumerate(groups):
            for j,key in enumerate(headers):
                newItem = QtWidgets.QTableWidgetItem()
                newItem.setText(getattr(ob, key))
                if key == 'name':
                    color = self.group_color
                    brush = QtGui.QBrush(color)
                    newItem.setBackground(brush)
                elif key == 'season':
                    if ob.season:
                        newItem.setText(self.db_season.dict_by_id[ob.season].name)
                    else:
                        #print(r)
                        pass
                newItem.group = ob
                table.setItem(i, j, newItem)
                
        # connect table
        self.myWidget.studio_editor_table.itemDoubleClicked.connect(self.edit_ui_to_group_content_editor)
                
        #  edit label
        self.myWidget.studio_editor_label.setText(('Group Editor / "%s"' % self.db_group.project.name))
        
        table.resizeRowsToContents()
        table.resizeColumnsToContents()
        
        table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self._group_editor_context_menu)
        
        print('fill group table')
        
    def _group_editor_context_menu(self, pos):
        pass
        #print(pos.__reduce__())
        table = self.myWidget.studio_editor_table
        #print(item.column_name)
        menu = QtWidgets.QMenu(table)
        menu_items = ['Rename', 'Edit Description', 'Asset List']
        for label in menu_items:
            action = menu.addAction(label)
            action.triggered.connect(partial(self._group_editor_context_menu_action, label))
        menu.exec_(QtGui.QCursor.pos())
        
    def _group_editor_context_menu_action(self, label):
        pass
        if label=='Rename':
            self.rename_group_ui()
        elif label=='Edit Description':
            self.edit_description_group_ui()
        elif label=='Asset List':
            self.pre_edit_ui_to_group_content_editor()
        
    def new_group_ui(self):
        pass
    
        #
        if self.myWidget.set_comboBox_01.currentText() == '-- select project --':
            self.message('No project selected!', 2)
            return
        
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.new_dialog_4_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.createGroupDialog = loader.load(file, self)
        file.close()
        
        # edit widget
        window.setWindowTitle(('Create Group to "%s"' % self.selected_project.name))
        window.new_dialog_label.setText('Name of Group:')
        window.new_dialog_comment_label.setText('description:')
        window.new_dialog_label_2.setText('Type:')
        window.new_dialog_label_3.setText('Season:')
        window.new_dialog_frame_3.setVisible(False)
        window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.new_dialog_ok.clicked.connect(partial(self.new_group_action, window))
        
        # edit comobox
        types = ['-- select type --'] +  self.db_studio.asset_types
        window.new_dialog_combo_box_2.addItems(types)
        window.new_dialog_combo_box_2.activated[str].connect(partial(self.new_group_ui_season_activation, window))
        
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()
        print('new group ui')
        
    def new_group_ui_season_activation(self, *args):
        window = args[0]
        type_ = args[1]
        
        self.db_season.project = self.selected_project
        
        #if type_ in copy.asset_types_with_season:
        if type_ in self.db_season.asset_types_with_season:
            window.new_dialog_frame_3.setVisible(True)
            
            season = ['-- select season --']
            #result = copy.get_list(project)
            b , r = self.db_season.get_list()
            if b:
                for ob in r:
                    season.append(ob.name)
            else:
                print(r)
            window.new_dialog_combo_box_3.clear()
            window.new_dialog_combo_box_3.addItems(season)
            
        else:
            window.new_dialog_frame_3.setVisible(False)
        
        print('season activation')
        
    def new_group_action(self, window):
        pass
        # get name, description
        name =  window.new_dialog_name.text()
        description = window.new_dialog_comment.text()
        
        if not name:
            self.message('Group name not specified!', 2)
            return
        elif name in self.db_group.dict_by_name.keys():
            self.message('A group with that name "%s" already exists!' % name, 2)
            return
            
        # get type
        type_ = window.new_dialog_combo_box_2.currentText()
        
        # get season
        #copy = db.group()
        
        season = ''
        #if type_ in copy.asset_types_with_season:
        if type_ in self.db_group.asset_types_with_season:
            season_name = window.new_dialog_combo_box_3.currentText()
            if season_name == '-- select season --':
                self.message('Season not specified', 2)
                return
                    
        # create group
        # -- get season id
        season_id = ''
        try:
            season_id = self.db_season.dict_by_name[season_name].id
        except:
            pass
        
        keys = {
        'name': name,
        'type': type_,
        'description': description,
        'season': season_id,
        }
        
        #result = copy.create(project, keys)
        result = self.db_group.create(keys)
        if not result[0]:
            self.message(result[1], 3)
            return
        
        self.fill_group_table()
        self.close_window(window)
        print('new group action')
        
    def rename_group_ui(self, group=False):
        pass
        table = self.myWidget.studio_editor_table
        #
        if self.myWidget.set_comboBox_01.currentText() == '-- select project --':
            self.message('No project selected!', 2)
            return
        
        if not table.selectedItems():
            self.message('No group selected!', 2)
            return
        
        if not group:
            self.selected_group = table.selectedItems()[0].group
        else:
            self.selected_group = group
        name = self.selected_group.name
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.new_dialog_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.createSeasonDialog = loader.load(file, self)
        file.close()
        
        # edit widget
        window.setWindowTitle(('Rename Group: "%s"' % name))
        window.new_dialog_label.setText('New Name of Group:')
        window.new_dialog_name.setText(name)
        window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.new_dialog_ok.clicked.connect(partial(self.rename_group_action, window))
                
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()
        
        print('rename group ui')
        
    def rename_group_action(self, window):
        pass
        # get name
        new_name = window.new_dialog_name.text()
                
        if not new_name:
            self.message('New name not specified!', 2)
            return
        elif new_name in self.selected_group.dict_by_name.keys():
            self.message('A group with that name "%s" already exists!' % new_name, 2)
            return
            
        result = self.selected_group.rename(new_name)
        if not result[0]:
            self.message('Could not rename the group, see details in the console', 3)
            print('*'*25, result[1])
            return
        
        self.fill_group_table()
        self.close_window(window)
        print('rename group action')
        
    def edit_description_group_ui(self, group=False):
        pass
        table = self.myWidget.studio_editor_table
        #
        if self.myWidget.set_comboBox_01.currentText() == '-- select project --':
            self.message('No project selected!', 2)
            return
        
        if not table.selectedItems():
            self.message('No group selected!', 2)
            return
                
        if not group:
            self.selected_group = table.selectedItems()[0].group
        else:
            self.selected_group = group
        description = self.selected_group.description
        
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.new_dialog_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.createSeasonDialog = loader.load(file, self)
        file.close()
        
        # edit widget
        window.setWindowTitle(('Edit Description Group: "%s"' % self.selected_group.name))
        window.new_dialog_label.setText('New Description:')
        if description:
            window.new_dialog_name.setText(description)
        window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.new_dialog_ok.clicked.connect(partial(self.edit_description_group_action, window))
                
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()   
        
        print('edit description group ui')
        
    def edit_description_group_action(self, window):
        pass
        # get description
        description = window.new_dialog_name.text()
        
        # edit description
        #copy = db.group()
        #result = copy.edit_description_by_name(project, name, description)
        result = self.selected_group.edit_description(description)
        if not result[0]:
            self.message(result[1], 2)
            return
        
        self.fill_group_table()
        self.close_window(window)
        print('edit description group action')
        
    # ******************* ASSET EDITOR
    
    def pre_edit_ui_to_group_content_editor(self, *args):
        item = self.myWidget.studio_editor_table.currentItem()
        if not item:
            self.message('Group not selected!', 2)
            return
        self.edit_ui_to_group_content_editor()
        
    def edit_ui_to_group_content_editor(self, *args):
        pass
        #self.current_group = args[0].group
        self.selected_group = self.myWidget.studio_editor_table.currentItem().group
        
        window = self.myWidget
        table = window.studio_editor_table
        
        # get project
        if self.selected_group.type == 'object':
            self.asset_columns = ('icon', 'name', 'description', 'priority', 'type', 'loading_type')
        else:
            self.asset_columns = ('icon', 'name', 'description', 'priority', 'type')
        
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
        label_trext = '\"%s\" / \"%s\" / Assets' % (self.selected_project.name, self.selected_group.name)
        window.studio_editor_label.setText(label_trext)
                
        # edit button
        # 1
        button01.setVisible(True)
        button01.setText('Reload')
        try:
            button01.clicked.disconnect()
        except:
            pass
        button01.clicked.connect(partial(self.reload_asset_list))
        # 2
        button02.setVisible(True)
        button02.setText('<< Back')
        try:
            button02.clicked.disconnect()
        except:
            pass
        button02.clicked.connect(partial(self.edit_ui_to_group_editor))
        # 3
        button03.setVisible(True)
        button03.setText('Change Group')
        try:
            button03.clicked.disconnect()
        except:
            pass
        button03.clicked.connect(partial(self.change_asset_group_ui))
        # 4
        button04.setVisible(True)
        button04.setText('Change Priority')
        try:
            button04.clicked.disconnect()
        except:
            pass
        button04.clicked.connect(partial(self.change_asset_priority_ui))
        # 5
        button05.setVisible(True)
        button05.setText('Change Description')
        try:
            button05.clicked.disconnect()
        except:
            pass
        button05.clicked.connect(partial(self.change_asset_description_ui))
        # 6
        button06.setVisible(True)
        button06.setText('Add Assets')
        try:
            button06.clicked.disconnect()
        except:
            pass
        button06.clicked.connect(partial(self.add_assets_to_group_ui))
        # 7
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
        button08.clicked.connect(partial(self.remove_asset_action))
        # 9
        button09.setVisible(True)
        button09.setText('To Task Manager >>>')
        try:
            button09.clicked.disconnect()
        except:
            pass
        button09.clicked.connect(partial(self.asset_to_task_manager, 'from_asset_editor'))
        button10.setVisible(False)
        
        # edit combobox
        #groups = ['-- select group --'] + self.db_group.dict_by_name.keys()
        groups = self.db_group.dict_by_name.keys()
        index = groups.index(self.selected_group.name)
        #print('index: ', index)
        window.set_comboBox_01.setVisible(True)
        window.set_comboBox_01.clear()
        window.set_comboBox_01.addItems(groups)
        window.set_comboBox_01.setCurrentIndex(index)
        try:
            window.set_comboBox_01.activated[str].disconnect()
        except:
            pass
        window.set_comboBox_01.activated[str].connect(partial(self.fill_group_content_list))
        window.set_comboBox_02.setVisible(False)
        window.set_comboBox_03.setVisible(False)
        # unhide search lineEdit 
        self.myWidget.group_search_qline.setVisible(True)
        
        # edit table
        #self.myWidget.studio_editor_table_2.setVisible(False)
        self.myWidget.right_table_frame.setVisible(False)
        # -- selection mode   
        table.setSortingEnabled(True)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
        self.clear_table()
        self.fill_group_content_list(self.selected_group.name)
        
        print('edit ui to group content editor')
        
    def reload_asset_list(self):
        self.fill_group_content_list(self.selected_group.name)
        
    def fill_group_content_list(self, *args):
        window = self.myWidget
        table = window.studio_editor_table
        group_name = args[0]
        
        # get self.current_group
        self.selected_group = self.db_group.dict_by_name[group_name]
        self.db_asset.project = self.selected_project
                
        if self.selected_group.type == 'recycle_bin':
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
        window.studio_editor_label.setText(('\"' + self.selected_project.name + '\" / \"' + group_name + '\" / Assets'))
        
        # get table data
        f = self.myWidget.group_search_qline.text()
        #copy = self.db_asset
        b, r = self.db_asset.get_list_by_group(self.selected_group)
        if b:
            if f:
                assets_list_filter = []
                for asset in r:
                    if f.lower() in asset.name.lower():
                        assets_list_filter.append(asset)
                assets_list = assets_list_filter
            else:
                assets_list = r
                
        headers = self.asset_columns
        num_row = len(assets_list)
        num_column = len(headers)
        
        # make table
        table.setColumnCount(num_column)
        table.setRowCount(num_row)
        table.setHorizontalHeaderLabels(headers)
    
        # fill table
        for i, row in enumerate(assets_list):
            pass
            #print('**** %s' % row.loading_type)
            #self.db_asset.init(row)
            for j,key in enumerate(headers):
                newItem = QtWidgets.QTableWidgetItem()
                # -- get final task
                task_name = '%s:final' % row.name
                self.db_task.asset = row
                final_task = self.db_task.init(task_name)
                
                #newItem.setText(str(getattr(row, key)))
                if key == 'name':
                    if final_task.status in final_task.END_STATUSES:
                        rgb = final_task.COLOR_STATUS[final_task.status]
                        color =  QtGui.QColor(rgb[0]*255, rgb[1]*255, rgb[2]*255)
                    else:
                        color = self.asset_color
                    brush = QtGui.QBrush(color)
                    newItem.setBackground(brush)
                    #
                    newItem.setText(getattr(row, key))
                    newItem.asset = row
                    table.setItem(i, j, newItem)
                elif key == 'priority':
                    newItem.setText(str(getattr(row, key)))
                    newItem.asset = row
                    table.setItem(i, j, newItem)
                elif key == 'icon':
                    # get img path
                    icon_path = os.path.join(self.db_asset.project.preview_img_path, (row.name + '_icon.png'))
                    # label
                    label = QtWidgets.QLabel()
                    
                    if os.path.exists(icon_path):
                        # img
                        image = QtGui.QImage(icon_path)
                        pix = QtGui.QPixmap(image)
                                                                
                        label.setPixmap(pix)
                        label.show()
                    else:
                        label.setText('no image')
                    
                    label.asset = row
                    table.setCellWidget(i, j, label)
                
                else:
                    data = getattr(row, key)
                    if not data:
                        data=''
                    else:
                        data=str(data)
                    newItem.setText(data)
                    newItem.asset = row
                    table.setItem(i, j, newItem)
                    
        table.resizeRowsToContents()
        table.resizeColumnsToContents()

        table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self._asset_editor_context_menu)
            
        print('fill group content list', self.selected_group.name)
        
    def _asset_editor_context_menu(self, pos):
        pass
        #print(pos.__reduce__())
        table = self.myWidget.studio_editor_table
        #print(item.column_name)
        menu = QtWidgets.QMenu(table)
        if self.selected_group.type=='recycle_bin':
                menu_items = ['Gange Group', 'Gange Description']
        elif self.selected_group.type=='object':
            menu_items = ['Gange Group', 'Gange Priority', 'Gange Description','Change Loading Type',  'Copy Asset', 'Remove Asset', 'To Task Manager']
        else:
            menu_items = ['Gange Group', 'Gange Priority', 'Gange Description', 'Copy Asset', 'Remove Asset', 'To Task Manager']
        for label in menu_items:
            action = menu.addAction(label)
            action.triggered.connect(partial(self._asset_editor_context_menu_action, label))
        menu.exec_(QtGui.QCursor.pos())
        
    def _asset_editor_context_menu_action(self, label):
        pass
        if label=='Gange Group':
            self.change_asset_group_ui()
        elif label=='Gange Priority':
            self.change_asset_priority_ui()
        elif label=='Gange Description':
            self.change_asset_description_ui()
        elif label=='Change Loading Type':
            self._edit_loading_type_ui(self.asset_edit_loading_type_action, table=False)
        elif label=='Copy Asset':
            self.copy_asset_ui()
        elif label=='Remove Asset':
            self.remove_asset_action()
        elif label=='To Task Manager':
            self.asset_to_task_manager('from_asset_editor')
            
    def asset_edit_loading_type_action(self, window):
        pass
        #copy = db.set_of_tasks()
        b, message = self.selected_asset.change_loading_type(window.combo_dialog_combo_box.currentText())
        if not b:
            self.message(message, 2)
        
        self.close_window(window)
        self.reload_asset_list()
        print('edit loading type action')
    
    def asset_to_task_manager(self, action):
        pass
        print(action)
        if action == 'from_asset_editor':
            table = self.myWidget.studio_editor_table
            if not table.selectedItems():
                self.message('No asset selected!', 2)
            self.selected_asset = table.selectedItems()[0].asset
            
            '''
            # -- group dict
            result = self.db_group.get_groups_dict_by_id()
            if not result[0]:
                self.message(result[1], 3)
                return
            group_dict = result[1]
            '''
            # load task manager
            # -- open tab
            self.myWidget.main_tabWidget.setCurrentIndex(1)
            # -- fill current project
            for i in range(0, self.myWidget.task_manager_comboBox_1.model().rowCount()):
                if self.myWidget.task_manager_comboBox_1.itemText(i) == self.selected_project.name:
                    self.myWidget.task_manager_comboBox_1.setCurrentIndex(i)
                    #self.tm_reload_task_list()
                    break
            
            #self.myWidget.global_search_qline.setText(asset_data['name']) #old
            #self.tm_fill_season_groups(self.current_project) # old
            
            self.tm_reload_task_list_by_global_search_action()
        
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
                result = self.db_group.get_groups_dict_by_id()
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
                result = self.db_group.get_groups_dict_by_id()
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
                
    def change_asset_group_ui(self):
        pass
        table = self.myWidget.studio_editor_table
        if not table.selectedItems():
            self.message('No asset selected!', 2)
        self.selected_asset = table.selectedItems()[0].asset
        
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.combo_dialog_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.setProjectDialog = loader.load(file, self)
        file.close()
        
        # edit widget
        group_list = ['-- new groups --']
        for grp in self.db_group.dict_by_type[self.selected_asset.type]:
            if grp.name != self.selected_group.name:
                group_list.append(grp.name)
        
        window.setWindowTitle(('Change group of asset: %s' % self.selected_asset.name))
        window.combo_dialog_label.setText('Select New Group:')
        window.combo_dialog_combo_box.addItems(group_list)
        window.combo_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.combo_dialog_ok.clicked.connect(partial(self.change_asset_group_action, window))
        
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()
        
        print('change asset group')
        
    def change_asset_group_action(self, window):
        pass
        # get new group name asset_name
        group_name = window.combo_dialog_combo_box.currentText()
        if group_name == '-- new groups --':
            self.message('The Group is not Selected!', 2)
            return
        else:
            new_group = self.selected_group.dict_by_name.get(group_name)
        
        if not new_group:
            print('not found group "%s"' % group_name)
            return
        
        # change group
        #print(window.groups, group_name, group_id)
        
        result = self.selected_asset.change_group(new_group.id)
        if not result[0]:
            self.message(result[1], 2)
            return
        
        # reload assets list
        self.fill_group_content_list(self.selected_group.name)
        
        self.close_window(window)
        #print('change asset group action', result[1])
        
    def remove_asset_action(self):
        table = self.myWidget.studio_editor_table
        if not table.currentItem():
            self.message('No asset selected!', 2)
            return
        asset = table.currentItem().asset
        ask = self.message(('Are you sure you want to delete Asset \"%s\"?' % asset.name), 0)
        if not ask:
            return
        
        b,r = asset.remove()
        if not b:
            self.message(str(r), 2)
        
        # reload assets list
        self.fill_group_content_list(self.selected_group.name)
        
    def change_asset_priority_ui(self):
        pass
        table = self.myWidget.studio_editor_table
        if not table.selectedItems():
            self.message('No asset selected!', 2)
            return
        self.selected_asset = table.selectedItems()[0].asset
        
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.new_dialog_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.createSeasonDialog = loader.load(file, self)
        file.close()
        
        # edit widget
        window.setWindowTitle(('Change priority of asset: "%s"' % self.selected_asset.name))
        window.new_dialog_label.setText('New Priority:')
        priority_str = str(self.selected_asset.priority)
        if priority_str:
            window.new_dialog_name.setText(priority_str)
        window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.new_dialog_ok.clicked.connect(partial(self.change_asset_priority_action, window))
                
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()
                
        print('change asset priority ui')
        
    def change_asset_priority_action(self, window):
        pass
    
        priority_str = window.new_dialog_name.text()
        try:
            new_priority = int(priority_str)
        except:
            new_priority=None
        if not new_priority:
            self.message('priority must be an integer!', 2)
            return
        
        b,r = self.selected_asset.change_priority(new_priority)
        if not b:
            self.message(r, 2)
            return
        
        # reload assets list
        self.fill_group_content_list(self.selected_group.name)
        #
        self.close_window(window)
        print('change asset priority action %s' % priority_str)
        
    def change_asset_description_ui(self):
        pass
        table = self.myWidget.studio_editor_table
        if not table.selectedItems():
            self.message('No asset selected!', 2)
        self.selected_asset = table.selectedItems()[0].asset
        
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.new_dialog_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.createSeasonDialog = loader.load(file, self)
        file.close()
        
        # edit widget
        window.setWindowTitle(('Change description of asset: "%s"' % self.selected_asset.name))
        window.new_dialog_label.setText('Description:')
        description = self.selected_asset.description
        if description:
            window.new_dialog_name.setText(description)
        window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.new_dialog_ok.clicked.connect(partial(self.change_asset_description_action, window))
                
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()
    
        print('change asset description ui')
        
    def change_asset_description_action(self, window):
        pass
    
        description = window.new_dialog_name.text()
                
        b,r = self.selected_asset.change_description(description)
        if not b:
            self.message(r, 2)
            return
        
        # reload assets list
        self.fill_group_content_list(self.selected_group.name)
        #
        self.close_window(window)
        print ('change asset description action')
        
    def add_assets_to_group_ui(self):
        pass
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
        #table.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        
        # -- Fill table
        data = []
        #copy = db.list_of_assets()
        self.db_list_of_assets.group = self.selected_group
        b,r = self.db_list_of_assets.get(self.selected_group.name)
        if b:
            data = r
        
        for i in range(0, num_row):
            for j in range(0, num_column):
                newItem = QtWidgets.QTableWidgetItem()
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
        set_of_tasks_list = self.db_set_of_tasks.get_list(f = {'asset_type': self.selected_group.type})
        #print(set_of_tasks_list)
        
        if set_of_tasks_list[0]:
            set_list = []
            for ob in set_of_tasks_list[1]:
                set_list.append(ob.name)
            table.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
            # workroom menu
            addgrup_action = QtWidgets.QAction( '-- sets of tasks -- ', window)
            table.addAction( addgrup_action )
            for key in set_list:
                addgrup_action = QtWidgets.QAction( key, window)
                #addgrup_action.setToolTip( 'to WorkRoom column' )
                addgrup_action.triggered.connect(partial(self.insert_asset_list_in_table, key, table))
                table.addAction( addgrup_action )
        
        
        # edit widget
        window.setWindowTitle(('Add new assets to: %s' % self.selected_group.name))
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
        pass
        table = self.myWidget.studio_editor_table
        if not table.selectedItems():
            self.message('No asset selected!', 2)
        self.selected_asset = table.selectedItems()[0].asset
        
        if not self.selected_asset.type in self.db_asset.COPIED_ASSET:
            self.message('This assets type can not be copied!', 2)
            return
        
        group_list = []
        group_id_list = []
        for type_ in self.db_asset.COPIED_ASSET[self.selected_asset.type]:
            for group in self.db_group.dict_by_type[type_]:
                group_list.append('%s (%s)' % (group.name, group.type))
                group_id_list.append(group.id)
        
        b,r = self.db_set_of_tasks.get_dict_by_all_types()
        if not b:
            self.message(r, 2)
            return
        self.set_of_tasks_dict_by_type = r
        
        # window  self.new_dialog_3_path
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.new_dialog_4_2_path)
        #file = QtCore.QFile(self.new_dialog_3_path)
        file.open(QtCore.QFile.ReadOnly)
        window = self.addAssetsDialog = loader.load(file, self)
        file.close()
        
        # edit window
        window.setWindowTitle(('Copy of asset: /// %s' % self.selected_asset.name))
        window.new_dialog_label.setText('New Name of Asset:')
        window.new_dialog_label_0.setText('New Type:')
        window.new_dialog_label_2.setText('Group:')
        window.new_dialog_label_3.setText('Set Of Task:')
        if not self.selected_asset.type in self.db_asset.COPIED_WITH_TASK:
            window.new_dialog_frame_3.setVisible(False)
        
        # -- type list
        window.new_dialog_combo_box_0.addItems(self.db_asset.COPIED_ASSET[self.selected_asset.type])
        # -- group list
        window.new_dialog_combo_box_2.addItems(group_list)
        window.new_dialog_combo_box_2.setCurrentIndex(group_id_list.index(self.selected_asset.group))
        # -- set_of_task list
        if self.selected_asset.type in self.db_asset.COPIED_WITH_TASK:
            window.new_dialog_combo_box_3.addItems(self.set_of_tasks_dict_by_type[self.selected_asset.type].keys())
        else:
            window.new_dialog_combo_box_3.addItems([''])
        
        # -- connect button
        window.new_dialog_combo_box_0.activated[str].connect(partial(self.edit_copy_asset_ui, window))
        window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.new_dialog_ok.clicked.connect(partial(self.copy_asset_action, window))
        
        window.show()
        
    def edit_copy_asset_ui(self, window, asset_type):
        pass
    
        # edit group list
        group_list = []
        group_id_list = []
        for type_ in self.db_asset.COPIED_ASSET[asset_type]:
            for group in self.db_group.dict_by_type[type_]:
                group_list.append('%s (%s)' % (group.name, group.type))
                group_id_list.append(group.id)
        
        window.new_dialog_combo_box_2.clear()
        window.new_dialog_combo_box_2.addItems(group_list)
        if self.selected_asset.group in group_id_list:
            window.new_dialog_combo_box_2.setCurrentIndex(group_id_list.index(self.selected_asset.group))
        
        # edit set_of_tasks list
        window.new_dialog_combo_box_3.clear()
        if asset_type in self.db_asset.COPIED_WITH_TASK:
            window.new_dialog_combo_box_3.addItems(self.set_of_tasks_dict_by_type[asset_type].keys())
        else:
            window.new_dialog_combo_box_3.addItems([''])
        
        
    def copy_asset_action(self, window):
        new_asset_name = window.new_dialog_name.text()
        new_group_name = window.new_dialog_combo_box_2.currentText().split()[0]
        set_of_tasks = window.new_dialog_combo_box_3.currentText()
        new_asset_type = window.new_dialog_combo_box_0.currentText()
        
        #self.message('name: %s,\ngroup: %s,\nset_of_tasks: %s,\ntype: %s' % (new_asset_name, new_group_name, set_of_tasks, new_asset_type), 1)
        #return
        
        b, r = self.selected_asset.copy_of_asset(new_group_name, new_asset_name, new_asset_type, set_of_tasks)
        if not b:
            self.message(r, 3)
            return
            
        # reload assets list
        self.myWidget.group_search_qline.setText(new_asset_name)
        
        for i in range(0, self.myWidget.set_comboBox_01.model().rowCount()):
            if self.myWidget.set_comboBox_01.itemText(i) == new_group_name:
                self.myWidget.set_comboBox_01.setCurrentIndex(i)
                #self.tm_reload_task_list()
                break
        
        self.fill_group_content_list(new_group_name)
        
        self.close_window(window)
        
    def insert_asset_list_in_table(self, key, table):
        pass
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
                row['asset_type'] = self.selected_group.type
                
            if row['asset_name'] and not row['asset_name'] in names:
                rows.append(row)
                names[row['asset_name']] = i
            elif row['asset_name'] in names:
                self.message(('match names - lines: ' + str(names[row['asset_name']] + 1) + ', ' + str(i + 1)), 2)
                return
                
        result = self.db_list_of_assets.save_list(rows)
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
                    
                row['asset_type'] = self.selected_group.type
                row['path'] = ''
                row['group'] = self.selected_group.id
                row['season'] = self.selected_group.season
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
        self.db_asset.project = self.selected_project
        create_result = self.db_asset.create(self.selected_group.type, rows)
        if not create_result[0]:
            self.message(create_result[1], 2) 
            return
        
        # remove asset list
        result = self.db_list_of_assets.remove()
        if not result[0]:
            print(result[1])
        
        self.close_window(window)
        self.reload_asset_list()
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
        self.location_columns = ('name', 'type', 'description', 'season')
        
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
        projects = ['-- select project --'] + self.project.list_active_projects
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
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
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
        self.project.get_project(self.current_project)
        # load group list
        result = self.db_group.get_list()
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
        result = self.db_group.get_by_name(group_name)
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
        self.myWidget.studio_editor_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.myWidget.studio_editor_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
          
        # fill table
        for i, task in enumerate(service_task_list):
            newItem = QtWidgets.QTableWidgetItem()
            newItem.setText(task['task_name'].replace((task['asset'] + ':'), ''))
            newItem.task = dict(task)
            
            rgb = self.db_chat.COLOR_STATUS[task['status']]
            r = (rgb[0]*255)
            g = (rgb[1]*255)
            b = (rgb[2]*255)
            color = QtGui.QColor(r, g, b)
            brush = QtGui.QBrush(color)
            newItem.setBackground(brush)
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
        # print('\n')
        # print(task_data['input'], task_data['output'])
        
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
        self.myWidget.studio_editor_table_2.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.myWidget.studio_editor_table_2.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        
        # fill table
        for i, input_task_name in enumerate(input_list):
            for j, head_label in enumerate(head):
                asset_name = input_task_name.split(':')[0]
                task_name = input_task_name.replace((asset_name + ':'), '')
                if head_label == 'Asset':
                    newItem = QtWidgets.QTableWidgetItem()
                    newItem.setText(asset_name)
                    newItem.task = inpun_tasks_data[input_task_name]
                    
                    rgb = self.db_chat.COLOR_STATUS[inpun_tasks_data[input_task_name]['status']]
                    r = (rgb[0]*255)
                    g = (rgb[1]*255)
                    b = (rgb[2]*255)
                    color = QtGui.QColor(r, g, b)
                    brush = QtGui.QBrush(color)
                    newItem.setBackground(brush)
                    
                    
                elif head_label == 'Task Name':
                    newItem = QtWidgets.QTableWidgetItem()
                    newItem.setText(task_name)
                    newItem.task = inpun_tasks_data[input_task_name]
                    
                elif head_label == 'icon':
                    # get img path
                    icon_path = os.path.join(self.db_asset.preview_img_path, (asset_name + '_icon.png'))
                    # label
                    label = QtWidgets.QLabel()
                    
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
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
        # -- fill table
        for i, task in enumerate(tasks_list):
            for j, head in enumerate(headers):
                newItem = QtWidgets.QTableWidgetItem()
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
            result = self.db_group.get_list()
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
                newItem = QtWidgets.QTableWidgetItem()
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
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        
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
            
        result = self.db_chat._service_add_list_to_input(self.current_project, task_data, task_list)
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
        
        result = self.db_chat._service_change_task_in_input(self.current_project, srv_td, rm_td, add_td)
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
                    newItem = QtWidgets.QTableWidgetItem()
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
                    newItem = QtWidgets.QTableWidgetItem()
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
                    label = QtWidgets.QLabel()
                    
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
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        
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
            
        result = self.db_chat._service_add_list_to_input_from_asset_list(self.current_project, task_data, asset_list)
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
        result = self.db_chat._service_remove_task_from_input(self.current_project, service_task_data, list_removed_tasks)
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
                        
                    rgb = self.db_chat.COLOR_STATUS[new_status]
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
                                            
                    rgb = self.db_chat.COLOR_STATUS[new_status]
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
                    rgb = self.db_chat.COLOR_STATUS[new_status]
                    r = (rgb[0]*255)
                    g = (rgb[1]*255)
                    b = (rgb[2]*255)
                    color = QtGui.QColor(r, g, b)
                    brush = QtGui.QBrush(color)
                    item.setBackground(brush)
                                
        # reload table_2
        self.loc_load_content_of_asset_table(table_2.task, update = True)
    
    # ******************* TASKS MANAGER *********************************************
    
    def preparation_to_task_manager(self):
        self.myWidget.task_manager_reload_button.setText('reload')
        #self.myWidget.task_manager_reload_button.clicked.connect(self.tm_fill_project_workroom_list)
        self.myWidget.task_manager_comboBox_2.setVisible(False)
        self.myWidget.task_manager_comboBox_3.setVisible(False)
        self.myWidget.task_manager_comboBox_4.setVisible(False)
        self.myWidget.task_manager_comboBox_5.setVisible(False)
        # fill type of assets box
        self.myWidget.task_manager_comboBox_5.addItems((['-all types-'] + list(self.db_studio.asset_types)))
        self.myWidget.task_manager_comboBox_5.activated[str].connect(self.tm_reload_group_list_by_type)
        self.myWidget.local_search_qline.setVisible(False)
        self.myWidget.local_search_qline.returnPressed.connect(self.tm_reload_task_list)
        self.myWidget.global_search_qline.setVisible(False)
        self.myWidget.global_search_qline.returnPressed.connect(self.tm_reload_task_list_by_global_search_ui)
        
        self.myWidget.button_area.setVisible(False)
        
        # ----------- POPUP MENU --------------------------
        # LOCAL SEARCH
        self.myWidget.local_search_qline.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
        for status in self.db_studio.task_status:
            addgrup_action = QtWidgets.QAction( status, self.myWidget)
            addgrup_action.triggered.connect(partial(self.tm_reload_task_list_by_status, status))
            self.myWidget.local_search_qline.addAction( addgrup_action )
        
        # ACTIVITY
        self.myWidget.tm_data_label_2.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
        addgrup_action = QtWidgets.QAction( 'change Activity', self.myWidget)
        addgrup_action.triggered.connect(partial(self.tm_change_task_activity_ui))
        self.myWidget.tm_data_label_2.addAction( addgrup_action )
        
        # WORKROOM
        self.myWidget.tm_data_label_3.hide()
        self.myWidget.label_6.hide()
        #self.myWidget.tm_data_label_3.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
        #addgrup_action = QtWidgets.QAction( 'change Workroom', self.myWidget)
        #addgrup_action.triggered.connect(partial(self.tm_change_task_workroom_ui))
        #self.myWidget.tm_data_label_3.addAction( addgrup_action )
        
        # PRICE
        self.myWidget.tm_data_label_5.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
        addgrup_action = QtWidgets.QAction( 'change Price', self.myWidget)
        addgrup_action.triggered.connect(partial(self.tm_change_task_price_ui))
        self.myWidget.tm_data_label_5.addAction( addgrup_action )
        
        # ARTIST
        self.myWidget.tm_data_label_1.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
        addgrup_action = QtWidgets.QAction( 'change Artist', self.myWidget)
        addgrup_action.triggered.connect(partial(self.tm_change_task_artist_ui))
        self.myWidget.tm_data_label_1.addAction( addgrup_action )
        
        # INPUT
        self.myWidget.tm_data_label_4.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
        addgrup_action = QtWidgets.QAction( 'change Input Task', self.myWidget)
        addgrup_action.triggered.connect(partial(self.tm_change_input_ui))
        self.myWidget.tm_data_label_4.addAction( addgrup_action )
        
        # TASK_ TYPE
        self.myWidget.tm_data_label_6.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
        addgrup_action = QtWidgets.QAction( 'change Task Type', self.myWidget)
        addgrup_action.triggered.connect(partial(self.tm_change_task_type_ui))
        self.myWidget.tm_data_label_6.addAction( addgrup_action )
        
        # EXTENSION
        self.myWidget.tm_data_label_7.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
        addgrup_action = QtWidgets.QAction( 'change Extension', self.myWidget)
        addgrup_action.triggered.connect(partial(self.tm_change_task_extension_ui))
        self.myWidget.tm_data_label_7.addAction( addgrup_action )
        
        # LOADING TYPE
        self.myWidget.tm_data_label_9.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
        addgrup_action = QtWidgets.QAction( 'change Loading Type', self.myWidget)
        addgrup_action.triggered.connect(partial(self._edit_loading_type_ui, self.tm_change_loading_type, table=self.myWidget.task_manager_table, task=True)) #
        self.myWidget.tm_data_label_9.addAction( addgrup_action )
        
        # LINK
        self.myWidget.tm_data_label_8.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
        addgrup_action = QtWidgets.QAction( 'change Link', self.myWidget)
        addgrup_action.triggered.connect(partial(self.tm_change_tz_link_ui))
        self.myWidget.tm_data_label_8.addAction( addgrup_action )
        
        # EDIT READERS
        self.myWidget.readers_list.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
        addgrup_action = QtWidgets.QAction( 'Edit Readers', self.myWidget)
        addgrup_action.triggered.connect(partial(self.tm_edit_readers_ui))
        self.myWidget.readers_list.addAction( addgrup_action )
        
        # connect button
        self.myWidget.make_preview_button.clicked.connect(self.tm_make_preview_ui)
        self.myWidget.task_manager_reload_button.clicked.connect(self.tm_reload_task_list)
        self.myWidget.chat_button.clicked.connect(self.chat_ui)
        self.myWidget.chat_button.setMinimumHeight(50)
        self.myWidget.tz_button.clicked.connect(self.tm_tz)
        self.myWidget.tz_button.setMinimumHeight(50)
        #
        self.myWidget.publish_button.clicked.connect(self.tm_publish_action)
        #
        self.myWidget.look_task_logs.clicked.connect(self.tm_look_task_logs_ui)
        self.myWidget.assept_button.clicked.connect(self.tm_accept_task_action)
        self.myWidget.close_task_button.clicked.connect(self.tm_close_task_action)
        self.myWidget.to_rework_button.clicked.connect(self.tm_rework_action)
        self.myWidget.return_a_job_button.clicked.connect(self.tm_return_a_job_action)
        self.myWidget.look_file_button.clicked.connect(self.tm_look_file_action)
        self.myWidget.look_publish_button.clicked.connect(partial(self.tm_look_file_action, action='publish'))
        self.myWidget.look_version_file_button.clicked.connect(self.tm_look_version_file_ui)
        self.myWidget.look_publish_version_button.clicked.connect(partial(self.tm_look_version_file_ui, action='publish'))
        self.myWidget.publish_version_button.clicked.connect(partial(self.tm_publish_version_ui, republish=False))
        self.myWidget.republish_button.clicked.connect(partial(self.tm_publish_version_ui, republish=True))
        self.myWidget.add_task_button.clicked.connect(self.tm_add_task_ui)
        self.myWidget.add_task_button.setText('Add Single Task')
        self.myWidget.edit_readers_button.clicked.connect(self.tm_edit_readers_ui)
        
        # new attributes
        self.date_choice_variants = ['For all time', 'last 7 days', 'last 30 days']
        
        # fill projects list
        self.tm_fill_project_list()
        
    # предполагается запуск из Combobox
    # current_item - это строка передаваемая из combobox.activated[str]
    def tm_choice_dates(self, window, fn, current_item):
        pass
        def run_function():
            pass
            self.date_start = date_start.date().toPython()
            self.date_end = date_end.date().toPython()
            self.close_window(self.ChoiceDateDialog)
            fn(window)
    
        if current_item != 'Choice dates':
            fn(window)
            return
    
        self.ChoiceDateDialog = QtWidgets.QDialog(self)
        self.ChoiceDateDialog.setModal(True)
        self.ChoiceDateDialog.setWindowTitle('Choice Dates')
        
        # add widget
        v_layout = QtWidgets.QVBoxLayout()
        #
        date_start = QtGui.QDateEdit(datetime.date.today() - datetime.timedelta(days=7))
        date_start.setCalendarPopup(True)
        #date_start.calendarWidget().installEventFilter(self)
        v_layout.addWidget(date_start)
        #
        date_end = QtGui.QDateEdit(datetime.date.today())
        date_end.setCalendarPopup(True)
        v_layout.addWidget(date_end)
        #
        frame = QtWidgets.QFrame()
        v_layout.addWidget(frame)
        h_layout = QtWidgets.QHBoxLayout(frame)
        #
        close_button = QtWidgets.QPushButton('Cancel')
        close_button.clicked.connect(partial(self.close_window, self.ChoiceDateDialog))
        h_layout.addWidget(close_button)
        #
        ok_button = QtWidgets.QPushButton('Ok')
        ok_button.clicked.connect(partial(run_function))
        h_layout.addWidget(ok_button)
        #
        self.ChoiceDateDialog.setLayout(v_layout)
        
        self.ChoiceDateDialog.show()
        
    # task_ob (task) - если не передавать - то использует selected_task
    def tm_look_task_logs_ui(self, task_ob=False):
        pass
        #
        if not task_ob:
            task_ob = self.selected_task
    
        # make widjet
        ui_path = self.select_from_list_dialog_4combobox_path
        # widget
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(ui_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.lookVersionDialog = loader.load(file, self)
        file.close()
        
        # set window texts
        window.setWindowTitle('Logs of Task: %s' % task_ob.task_name)
        window.select_from_list_cansel_button.setText('Close')
        window.label_1.setText('For all time')
        window.dialog_comboBox_1.addItems(self.date_choice_variants + ['Choice dates'])
        window.dialog_comboBox_2.addItems(['All Artists'])
        window.dialog_comboBox_3.addItems(['All Actions']+ sorted(self.db_log.log_actions))
        window.dialog_comboBox_4.addItems(['All Tasks'])
        
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        # edit Widget
        window.select_from_list_cansel_button.clicked.connect(partial(self.close_window, window))
        window.dialog_comboBox_1.activated[str].connect(partial(self.tm_choice_dates, window, self.tm_look_task_logs_fill_table))
        window.dialog_comboBox_3.activated.connect(partial(self.tm_look_task_logs_fill_table, window))
        window.dialog_comboBox_2.activated.connect(partial(self.tm_look_task_logs_fill_table, window))
        window.dialog_comboBox_4.activated.connect(partial(self.tm_look_task_logs_fill_table, window))
        window.select_from_list_apply_button.setVisible(False)
        
        window.show()
        
        # read_log
        self.db_log.task = task_ob
        b, r_data = self.db_log.read_log()
        if not b:
            self.message(r_data, 2)
            return
        self.selected_task_logs = r_data[0]
        # fill table
        self.tm_look_task_logs_fill_table(window)
        
    def tm_look_task_logs_fill_table(self, window, *args):
        pass
        #
        def get_start_end_dates(date_mode):
            if date_mode==self.date_choice_variants[1]:
                start_date = datetime.date.today() - datetime.timedelta(days=7)
                end_date = datetime.date.today()
            elif date_mode==self.date_choice_variants[2]:
                start_date = datetime.date.today() - datetime.timedelta(days=30)
                end_date = datetime.date.today()
            elif date_mode=='Choice dates':
                start_date = self.date_start
                end_date = self.date_end
            return(start_date, end_date)
    
        table = window.select_from_list_data_list_table
        # clear table
        self.clear_table(table=table)
        if not self.selected_task_logs:
            self.message('Logs not found!', 1)
            return
        
        # filters
        fin_logs = list()
        artists = list()
        tasks = list()
        for log in self.selected_task_logs:
            artists.append(log['artist'])
            tasks.append(log['task_name'])
            date_mode = window.dialog_comboBox_1.currentText()
            action = window.dialog_comboBox_3.currentText()
            artist = window.dialog_comboBox_2.currentText()
            task_name = window.dialog_comboBox_4.currentText()
            #
            if action in self.db_log.log_actions and action != log['action']:
                continue
            elif artist != 'All Artists' and artist != log['artist']:
                continue
            elif task_name != 'All Tasks' and task_name != log['task_name']:
                continue
            elif date_mode != self.date_choice_variants[0]:
                start_date, end_date = get_start_end_dates(date_mode)
                print(not start_date <= log['date_time'].date() <= end_date)
                if not start_date <= log['date_time'].date() <= end_date:
                    continue
                else:
                    fin_logs.append(log)
            else:
                fin_logs.append(log)
        
        # fill table
        headers = self.db_log.logs_keys.keys()
        num_column = len(headers)
        num_row = len(fin_logs)
        
        table.setColumnCount(num_column)
        table.setRowCount(num_row)
        table.setHorizontalHeaderLabels(headers)
        
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
        all_time = 0
        
        for i, log in enumerate(fin_logs):
            pass
            for j,header in enumerate(headers):
                newItem = QtWidgets.QTableWidgetItem()
                # content item
                if header == 'date_time':
                    newItem.setText(log[header].strftime("%m/%d/%Y, %H:%M:%S"))
                elif header == 'time':
                    if log[header]:
                        time = log[header]/3600
                    else:
                        time=0
                    all_time = all_time + time
                    newItem.setText('%s h' % str(time))
                else:
                    to_string = log[header]
                    if to_string is False or to_string is None:
                        to_string=''
                    newItem.setText(str(to_string))
                
                # item
                if header == 'artist':
                    color = QtGui.QColor(self.artist_color)
                    brush = QtGui.QBrush(color)
                    newItem.setBackground(brush)
                    #
                    table.setItem(i, j, newItem)
                elif header == 'action':
                    pass
                    #
                    if self.conformity_colors[log[header]] in self.db_log.COLOR_STATUS.keys():
                        rgb = self.db_log.COLOR_STATUS[self.conformity_colors[log[header]]]
                        color = QtGui.QColor(rgb[0]*255, rgb[1]*255, rgb[2]*255)
                    else:
                        color=self.conformity_colors[log[header]]
                    #
                    brush = QtGui.QBrush(color)
                    newItem.setBackground(brush)
                    #
                    table.setItem(i, j, newItem)
                else:
                    table.setItem(i, j, newItem)
                    
        table.resizeRowsToContents()
        table.resizeColumnsToContents()
        
        # edit window
        if window.dialog_comboBox_1.currentText() in self.date_choice_variants:
            window.label_1.setText('%s (%s h)' % (window.dialog_comboBox_1.currentText(), round(all_time, 2)))
        else:
            window.label_1.setText('from %s to %s (%s h)' % (self.date_start, self.date_end, round(all_time, 2)))
        #
        window.dialog_comboBox_2.clear()
        artist_items = ['All Artists']+ sorted(list(set(artists)))
        window.dialog_comboBox_2.addItems(artist_items)
        window.dialog_comboBox_2.setCurrentIndex(artist_items.index(artist))
        #
        window.dialog_comboBox_4.clear()
        tasks_items = ['All Tasks']+ sorted(list(set(tasks)))
        window.dialog_comboBox_4.addItems(tasks_items)
        window.dialog_comboBox_4.setCurrentIndex(tasks_items.index(task_name))
        
    def chat_ui(self):
        self.chat_status = 'manager'
        #self.current_task = G.current_task
        #self.current_user = G.current_user
        #self.current_project = G.current_project
        
        #import lineyka_chat
        chat_window = lineyka_chat.lineyka_chat(self)
        #chat_class.__init__(self)
        
    def chat_close(*args):
        pass
        
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
        pass
        return # debug
        
        self.project.get_list() # ?????? скорее всего надо
                
        # fill project list
        items = ['-- select project --'] + self.project.list_active_projects
        self.myWidget.task_manager_comboBox_1.clear()
        self.myWidget.task_manager_comboBox_1.addItems(items)
        self.myWidget.task_manager_comboBox_1.activated[str].connect(partial(self.tm_fill_season_groups))
        
        # fill workroom list
        self.tm_fill_workroom_list()
        
    def tm_fill_workroom_list(self):
        b, r_data = self.db_workroom.get_list()
        if not self.artist.user_name:
            return
        if self.db_workroom.USER_LEVELS.index(self.artist.level) >= self.db_workroom.USER_LEVELS.index('root'): # root и выше!!!! куда выше не известно, может super_root
            if b:
                wr_list = []
                wr_type_list = []
                for wr in r_data:
                    wr_list.append(wr.name)
                    if wr.type:
                        wr_type_list = wr_type_list + wr.type
                items = ['all workrooms'] + sorted(wr_list)
                self.myWidget.task_manager_comboBox_4.setVisible(True)
                self.myWidget.task_manager_comboBox_4.clear()
                self.myWidget.task_manager_comboBox_4.addItems(items)
                self.myWidget.task_manager_comboBox_4.wr_type_list = list(set(wr_type_list))
        else:
            if b:
                wr_list = []
                wr_type_list = []
                for wr in r_data:
                    if wr.id in self.artist.workroom:
                        wr_list.append(wr.name)
                        if wr.type:
                            wr_type_list = wr_type_list + wr.type
                items = ['all workrooms'] + sorted(wr_list)
                self.myWidget.task_manager_comboBox_4.setVisible(True)
                self.myWidget.task_manager_comboBox_4.clear()
                self.myWidget.task_manager_comboBox_4.addItems(items)
                self.myWidget.task_manager_comboBox_4.wr_type_list = list(set(wr_type_list))
        
        self.myWidget.task_manager_comboBox_4.activated[str].connect(self.tm_reload_task_list)
            
        
    def tm_fill_season_groups(self, project_name):
        pass
        if project_name == '-- select project --':
            self.boxes_default_state()
            return
        else:
            self.selected_project = self.project.dict_projects.get(project_name)
            self.myWidget.global_search_qline.setVisible(True)
        
        filter_of_type = self.myWidget.task_manager_comboBox_5.currentText()
        if filter_of_type == '-all types-':
            f = self.db_studio.asset_types
        else:
            f = filter_of_type
        
        self.db_group.project = self.selected_project
        result = self.db_group.get_list(f = f)
        
        self.db_season.project = self.selected_project
        result_s = self.db_season.get_list()
        
        if result[0]:
            # fil season list
            if result_s[0]:
                season_list = list(self.db_season.dict_by_name.keys())
                items_ = ['-- all season --'] + season_list
                self.myWidget.task_manager_comboBox_2.setVisible(True)
                self.myWidget.task_manager_comboBox_2.clear()
                self.myWidget.task_manager_comboBox_2.addItems(items_)
                self.myWidget.task_manager_comboBox_2.activated[str].connect(self.tm_reload_group_list)
            else:
                print('***\n%s\n***\n' % str(result_s[1]))
            
            # fill group list
            items = ['-- select group --'] + list(self.db_group.dict_by_name.keys())
            G.id_group_items = [''] + list(self.db_group.dict_by_id.keys())
            
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
        season = self.myWidget.task_manager_comboBox_2.currentText()
        if filter_of_type != '-all types-':
            self.tm_reload_group_list(season, filter_of_type = filter_of_type)
        else:
            self.tm_reload_group_list(season)
            
    def tm_reload_group_list(self, season_name, filter_of_type = False):
        if not filter_of_type:
            filter_of_type = self.db_studio.asset_types
        # get group list
        self.db_group.project = self.selected_project
        b, r = self.db_group.get_list(f = filter_of_type)
        if not b:
            self.message(r, 3)
            self.myWidget.task_manager_comboBox_2.setCurrentIndex(0)
            return
        
        # fill combobox
        group_list = []
        group_id_list = []
        if season_name != '-- all season --':
            self.db_season.project = self.selected_project
            season_ob = self.db_season.init(season_name)
            if not season_ob:
                self.message('Failed to get object "Season"', 2) # ? может только принт
                self.myWidget.task_manager_comboBox_2.setCurrentIndex(0)
                return
            for group_ob in self.db_group.list_group:
                if group_ob.season == season_ob.id:
                    group_list.append(group_ob.name)
                    group_id_list.append(group_ob.id)
        else: # -- all season --
            group_list = list(self.db_group.dict_by_name.keys())
            group_id_list = list(self.db_group.dict_by_id.keys())
                                    
        items = ['-- select group --'] + group_list
        G.id_group_items = [''] + group_id_list
        
        self.myWidget.task_manager_comboBox_3.setVisible(True)
        self.myWidget.task_manager_comboBox_3.clear()
        self.myWidget.task_manager_comboBox_3.addItems(items)
    
    # ---------- RELOAD TASK_ LIST ----------------------------------------------
    
    def tm_reload_task_list_by_global_search_ui(self):
        pass
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
        result = self.db_group.get_groups_dict_by_id()
        if not result[0]:
            self.message(result[1], 3)
            return
        group_dict = result[1]
        
        
        self.searchDialog = QtWidgets.QDialog(self)
        self.searchDialog.setModal(True)
        self.searchDialog.setWindowTitle('Search Results')
        
        # add widget
        v_layout = QtWidgets.QVBoxLayout()
        table = QtGui.QTableWidget()
        v_layout.addWidget(table)
        close_button = QtWidgets.QPushButton('Close')
        close_button.clicked.connect(partial(self.close_window, self.searchDialog))
        v_layout.addWidget(close_button)
        self.searchDialog.setLayout(v_layout)
        
        
        headers = ['icon', 'name', 'group', 'type']
        num_column = len(headers)
        num_row = len(asset_list)
        
        table.setColumnCount(num_column)
        table.setRowCount(num_row)
        table.setHorizontalHeaderLabels(headers)
        
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        table.itemClicked.connect(partial(self.tm_reload_task_list_by_global_search_action, self.searchDialog, group_dict))
        
        for i, row in enumerate(asset_list):
            for j,header in enumerate(headers):
                newItem = QtWidgets.QTableWidgetItem()
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
                    label = QtWidgets.QLabel()
                    
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
        
    def tm_reload_task_list_by_global_search_action(self, window=False):
        pass
        '''
        asset_data = item.asset
        
        # 1 - 3 load comboboxes
        self.myWidget.task_manager_comboBox_4.setCurrentIndex(0)
        self.myWidget.task_manager_comboBox_2.setCurrentIndex(0)
        self.myWidget.task_manager_comboBox_5.setCurrentIndex(0)
        self.tm_fill_season_groups(self.myWidget.task_manager_comboBox_1.currentText())
        
        self.myWidget.local_search_qline.setText(asset_data['name'])
        for i in range(0, self.myWidget.task_manager_comboBox_3.model().rowCount()):
            if self.myWidget.task_manager_comboBox_3.itemText(i) == group_dict[asset_data['group']]['name']:
                self.myWidget.task_manager_comboBox_3.setCurrentIndex(i)
                self.tm_reload_task_list()
                break
        
        self.close_window(window)
        '''
        self.myWidget.task_manager_comboBox_4.setCurrentIndex(0)
        self.myWidget.task_manager_comboBox_2.setCurrentIndex(0)
        self.myWidget.task_manager_comboBox_5.setCurrentIndex(0)
        self.tm_fill_season_groups(self.myWidget.task_manager_comboBox_1.currentText())
        
        self.myWidget.local_search_qline.setText(self.selected_asset.name)
        for i in range(0, self.myWidget.task_manager_comboBox_3.model().rowCount()):
            if self.myWidget.task_manager_comboBox_3.itemText(i) == self.selected_group.name:
                self.myWidget.task_manager_comboBox_3.setCurrentIndex(i)
                self.tm_reload_task_list()
                break
        
        if window:
            self.close_window(window)
        
    def tm_reload_task_list_by_status(self, status):
        self.myWidget.local_search_qline.setText(status)
        self.tm_reload_task_list()
        
    def tm_reload_task_list(self, *args):
        pass
        #if search:
        group_name = self.myWidget.task_manager_comboBox_3.currentText()
        #index = self.myWidget.task_manager_comboBox_3.currentIndex()
        search = self.myWidget.local_search_qline.text().lower().replace(' ', '_')
        self.myWidget.button_area.setVisible(False)
        
        SEARCH_IDENTIFIERS = ('#','@')
        
        #
        if self.db_group.dict_by_name is None:
            self.db_group.get_list()
        group_ob = self.db_group.dict_by_name.get(group_name)
                
        #
        if not group_ob:
            self.myWidget.button_area.setVisible(False)
            self.clear_table(table = self.myWidget.task_manager_table)
            return
        else:
            self.myWidget.local_search_qline.setVisible(True)
            self.selected_group = group_ob          
        
        # ==================== METADATA ==================== self.tasks_rows, num_column, num_row
        # get current workroom id list
        wr_name = self.myWidget.task_manager_comboBox_4.currentText()
        #print('*'*15, wr_name)
        current_wr_type_list = [] # список id читаемых отделов.
        if wr_name != 'all workrooms':
            if self.db_workroom.dict_by_name:
                current_wr_type_list = self.db_workroom.dict_by_name.get(wr_name).type
        else:
            current_wr_type_list = self.myWidget.task_manager_comboBox_4.wr_type_list
        
        # get asset list
        self.db_asset.project = self.selected_project
        b, r_data = self.db_asset.get_list_by_group(self.selected_group)
        asset_list = []
        if b:
            if not search or search in self.db_studio.task_status: # пустая строка поиска либо в строке поиска статус задачи
                asset_list = r_data
            else:
                for asset_ob in r_data:
                    if search in asset_ob.name.lower():
                        asset_list.append(asset_ob)
        else:
            self.message(r_data, 2)
            return
        
        # create tasks rows
        num_column = []
        self.tasks_rows = {}
        fin_asset_list = []
        for asset_ob in asset_list:
            #self.tasks_rows[asset_['name']] = []
            # -- get task list
            task_list = []
            self.db_task.asset = asset_ob
            if search and search in self.db_studio.task_status:
                result = self.db_task.get_list(task_status=search)
            
            else:
                result = self.db_task.get_list()
            if result[0]:
                if not result[1]: # в смысле вернулся пустой список
                    continue
                else:
                    task_list = result[1]
                    fin_asset_list.append(asset_ob)
            else:
                continue
            self.tasks_rows[asset_ob.name] = []
            # -- -- tasks labels
            len_ = len(task_list)
            for task_ob in task_list:
                if task_ob.task_type == 'service':
                    len_ = len_ - 1
                    continue
                    #self.tasks_rows[asset_ob['name']].append(task_ob)
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                elif wr_name != 'all workrooms':
                    if not task_ob.task_type in current_wr_type_list:
                        len_ = len_ - 1
                        continue
                else:
                    self.tasks_rows[asset_ob.name].append(task_ob)
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
        self.myWidget.task_manager_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.myWidget.task_manager_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
          
                
        # fill table
        for i, asset_name in enumerate(self.tasks_rows):
            
            # get img path
            icon_path = os.path.join(self.selected_project.preview_img_path, '%s_icon.png' % asset_name) 
            # label
            label = QtWidgets.QLabel()
            
            if os.path.exists(icon_path):
                # img
                image = QtGui.QImage(icon_path)
                pix = QtGui.QPixmap(image)
                                                        
                label.setPixmap(pix)
                label.show()
            else:
                label.setText('no image')
            
            self.myWidget.task_manager_table.setCellWidget(i, 0, label)
            
            for j,task_ob in enumerate(self.tasks_rows[asset_name]):
                j = j+1
                
                newItem = QtWidgets.QTableWidgetItem()
                #item_text = '%s\n---' % task_ob.task_name.replace('%s:' % task_ob.asset.name, '')
                #for attr in self.db_studio.SETTING_DATA['task_visible_fields']:
                    #item_text = '%s\n%s: %s' % (item_text, attr, getattr(task_ob, attr))
                item_text = self.tm_get_item_text(task_ob)
                newItem.setText(item_text)
                #newItem.setText('%s\ntype:%s\nartist: %s' % (task_ob.task_name.replace('%s:' % task_ob.asset.name, ''), task_ob.task_type, task_ob.artist))
                newItem.task = task_ob
                
                rgb = self.db_studio.COLOR_STATUS[task_ob.status]
                r = (rgb[0]*255)
                g = (rgb[1]*255)
                b = (rgb[2]*255)
                color = QtGui.QColor(r, g, b)
                brush = QtGui.QBrush(color)
                newItem.setBackground(brush)
                
                self.myWidget.task_manager_table.setItem(i, j, newItem)
            # add empty item    
            if not self.tasks_rows[asset_name]:
                #print(asset_name)
                for jj in range(0, num_column):
                    newItem = QtWidgets.QTableWidgetItem()
                    newItem.task = None
                    self.myWidget.task_manager_table.setItem(i, jj, newItem)
            elif len(self.tasks_rows[asset_name])<num_column:
                for jj in range((j+1), num_column):
                    newItem = QtWidgets.QTableWidgetItem()
                    newItem.task = None
                    self.myWidget.task_manager_table.setItem(i, jj, newItem)
                    
        self.myWidget.task_manager_table.resizeRowsToContents()
        self.myWidget.task_manager_table.resizeColumnsToContents()
            
        try:
            self.myWidget.task_manager_table.itemClicked.disconnect()
        except:
            pass
        self.myWidget.task_manager_table.itemClicked.connect(self.tm_load_buttons_of_tasks)
        
    def tm_get_item_text(self, task_ob):
        item_text = '%s\n---' % task_ob.task_name.replace('%s:' % task_ob.asset.name, '')
        for attr in self.db_studio.SETTING_DATA['task_visible_fields']:
            item_text = '%s\n%s: %s' % (item_text, attr, getattr(task_ob, attr))
        return(item_text)
        
    def tm_load_buttons_of_tasks(self, *args):
        pass
        print(args[0].task.task_name)
        #
        if self.selected_task:
            old_asset_name = self.selected_task.asset.name
        else:
            old_asset_name = None
        #
        self.selected_task = args[0].task
        
        if self.selected_task:
            # visible button frame
            self.myWidget.button_area.setVisible(True)
            
            # -- Loading Type
            if not self.selected_task.asset.type in ['object']:
                self.myWidget.label_11.setVisible(False)
                self.myWidget.tm_data_label_9.setVisible(False)
            else:
                self.myWidget.label_11.setVisible(True)
                self.myWidget.tm_data_label_9.setVisible(True)
                self.myWidget.tm_data_label_9.setText(self.selected_task.asset.loading_type)
            
            # -- ACCEPT button
            if self.selected_task.status in self.db_studio.WORKING_STATUSES or self.selected_task.status == 'checking':
                self.myWidget.assept_button.setEnabled(True)
            else:
                self.myWidget.assept_button.setEnabled(False)
            # -- SEND TO AUTSOURCE button
            if self.selected_task.status == 'ready_to_send':
                self.myWidget.send_to_outsource_button.setEnabled(True)
            else:
                self.myWidget.send_to_outsource_button.setEnabled(False)
            self.myWidget.load_from_outsource.setEnabled(False)
            
            # -- TO REWORK button
            if self.selected_task.status == 'checking':
                self.myWidget.to_rework_button.setEnabled(True)
            else:
                self.myWidget.to_rework_button.setEnabled(False)
                
            # -- CLOSE button
            if not self.selected_task.status in self.db_studio.END_STATUSES:
                self.myWidget.close_task_button.setEnabled(True)
            else:
                self.myWidget.close_task_button.setEnabled(False)
            
            # -- RETURN A JOB button
            if self.selected_task.status in self.db_studio.END_STATUSES:
                self.myWidget.return_a_job_button.setEnabled(True)
            else:
                self.myWidget.return_a_job_button.setEnabled(False)
            
        else:
            self.myWidget.button_area.setVisible(False)
            return
        
        # ------------ Fill Task Labels -------------------
        
        # get labels
        task_label = self.selected_task.task_name.replace(':', ' : ')
        input_label = self.selected_task.input.replace(':', ' : ')
        
        # -- set labels
        self.myWidget.tm_task_name_label.setText(task_label)
        self.myWidget.tm_data_label_1.setText(self.selected_task.artist)
        self.myWidget.tm_data_label_2.setText(self.selected_task.activity)
        #self.myWidget.tm_data_label_3.setText(self.db_workroom.dict_by_id[self.selected_task.workroom].name)
        self.myWidget.tm_data_label_4.setText(input_label)
        self.myWidget.tm_data_label_5.setText(str(self.selected_task.price))
        self.myWidget.tm_data_label_6.setText(self.selected_task.task_type)
        self.myWidget.tm_data_label_7.setText(self.selected_task.extension)
        self.myWidget.tm_data_label_8.setText(self.selected_task.specification)
        
        # -- load to preview img
        if old_asset_name != self.selected_task.asset.name:
            #print('change image')
            preview_path = os.path.join(self.selected_project.preview_img_path, '%s.png' % self.selected_task.asset.name)
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
        # get CLEANED readers list
        self.cleaned_readers_dict = {}
        if self.selected_task.readers:
            for key in self.selected_task.readers:
                if key == 'first_reader':
                    continue
                self.cleaned_readers_dict[key] = self.selected_task.readers[key]
        
        # set visible
        if not self.selected_task.readers:
            self.myWidget.readers_list.setVisible(False)
            self.myWidget.edit_readers_button.setVisible(True)
        else:
            self.tm_load_readers_list()
        
    # ---- readers editor ----------------
        
    def tm_load_readers_list(self):
        self.myWidget.readers_list.clear()
        
        # get CLEANED readers list
        self.cleaned_readers_dict = {}
        for key in self.selected_task.readers:
            if key == 'first_reader':
                continue
            self.cleaned_readers_dict[key] = self.selected_task.readers[key]
        
        if not self.cleaned_readers_dict:
            self.myWidget.readers_list.setVisible(False)
            self.myWidget.edit_readers_button.setVisible(True)
            return
        
        string = 'readers:\n'
        for key in self.cleaned_readers_dict:
            new_string = key + '- '*(20 - len(key)) + str(self.cleaned_readers_dict[key]) + '\n'
            if 'first_reader' in self.selected_task.readers:
                if key == self.selected_task.readers['first_reader']:
                    new_string = '(***)' + key + '- '*(20 - len(key)) + str(self.cleaned_readers_dict[key]) + '\n'
            string = string + new_string
        self.myWidget.readers_list.append(string)
        
        # -- change visible
        self.myWidget.edit_readers_button.setVisible(False)
        self.myWidget.readers_list.setVisible(True)
        
    def tm_edit_readers_ui(self):
        pass
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
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        
        # table_2 context menu
        table.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
        addgrup_action = QtWidgets.QAction( 'make First', self.myWidget)
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
        headers = ['username']
        num_column = len(headers)
        num_row = 0
        
        if self.cleaned_readers_dict:
            num_row = len(self.cleaned_readers_dict)
        
        
        table.setColumnCount(num_column)
        table.setRowCount(num_row)
        table.setHorizontalHeaderLabels(headers)
        
        if self.cleaned_readers_dict:
            for i,reader_name in enumerate(sorted(list(self.cleaned_readers_dict.keys()))):
                if reader_name == 'first_reader':
                    continue
                for j,key in enumerate(headers):
                    newItem = QtWidgets.QTableWidgetItem()
                    if key == 'username':
                        if self.selected_task.readers.get('first_reader') == reader_name:
                            newItem.setText('%s (***)' % reader_name)
                        else:
                            newItem.setText(reader_name)
                        color = self.artist_color
                        brush = QtGui.QBrush(color)
                        newItem.setBackground(brush)
                        
                        newItem.reader_name = reader_name
        
                    table.setItem(i, j, newItem)
        
    def tm_add_readers_ui(self):
        pass
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
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        
        # -- load workroom_list
        #result = self.db_workroom.get_list() # под вопросом
        wr_list = []
        for wr in self.db_workroom.list_workroom:
            if self.selected_task.task_type in wr.type:
                wr_list.append(wr.name)
        window.dialog_comboBox_1.addItems((['-select workroom-'] + wr_list))
        window.dialog_comboBox_1.activated[str].connect(partial(self.tm_add_readers_ui_load_artist_list))
        
        # button connect
        window.select_from_list_cansel_button.clicked.connect(partial(self.close_window, window))
        window.select_from_list_apply_button.clicked.connect(partial(self.tm_add_readers_action))
        
        window.show()
        
    def tm_add_readers_ui_load_artist_list(self, workrom_name):
        table = self.selectReadersDialog.select_from_list_data_list_table
        #workroom_dict = self.selectReadersDialog.workroom_dict
        
        self.clear_table(table)
        result = self.artist.read_artists_of_workroom(self.db_workroom.dict_by_name[workrom_name])
        if not result[0]:
            self.message(result[1], 2)
            
        artirs_dict = result[1]
        #print(artirs_dict)
        
        # load table
        headers = ['username', 'level', 'outsource']
        num_column = len(headers)
        num_row = 0
        if artirs_dict:
            num_row = len(artirs_dict)
                
        table.setColumnCount(num_column)
        table.setRowCount(num_row)
        table.setHorizontalHeaderLabels(headers)
        
        if artirs_dict:
            for i,reader_name in enumerate(sorted(list(artirs_dict.keys()))):
                for j,key in enumerate(headers):
                    newItem = QtWidgets.QTableWidgetItem()
                    newItem.setText(str(getattr(artirs_dict[reader_name], key)))
                    #newItem.reader_name = reader_name
                    newItem.reader = artirs_dict[reader_name]
                    
                    if key == 'username':
                        color = self.artist_color
                        brush = QtGui.QBrush(color)
                        newItem.setBackground(brush)
                    if self.selected_task.readers:
                        if reader_name in self.selected_task.readers.keys():
                            color = self.grey_color
                            brush = QtGui.QBrush(color)
                            newItem.setBackground(brush)
                        
                    table.setItem(i, j, newItem)
    
    def tm_add_readers_action(self):
        table = self.selectReadersDialog.select_from_list_data_list_table
        
        readers = []
        items = table.selectedItems()
        for item in items:
            name = item.reader.username
            if not name in readers:
                if self.selected_task.readers:
                    if not name in self.selected_task.readers.keys():
                        readers.append(name)
                else:
                    readers.append(name)
                
        if not readers:
            self.message('Not Selected Artists!', 2)
            return
            
        # edit task data
        result = self.selected_task.add_readers(readers)
        if not result[0]:
            self.message(result[1], 2)
            
        #self.current_readers_dict = result[1]
        
        # reload widgets
        # -- task_list
        if result[2]:
            self.tm_reload_task_list()
        else:
            print('*'*25)
            # -- 
            #table = self.myWidget.task_manager_table
            #edit_task_data = dict(table.currentItem().task)
            #edit_task_data['readers'] = json.dumps(self.current_readers_dict)
            #table.currentItem().task = edit_task_data
        
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
        result = self.selected_task.remove_readers(readers)
        if not result[0]:
            self.message(result[1], 2)
            
        #self.current_readers_dict = result[1]
        
        # reload widgets
        # -- task_list
        if result[2]:
            self.tm_reload_task_list()
        else:
            pass
            # -- 
            #table = self.myWidget.task_manager_table
            #edit_task_data = dict(table.currentItem().task)
            #edit_task_data['readers'] = json.dumps(self.selected_task.readers)
            #table.currentItem().task = edit_task_data
            
        # -- readers list
        self.tm_load_readers_list()
        
        # -- readers editor list
        self.tm_edit_readers_ui_reload_table()
        
    def tm_make_first_reader(self, table):
        pass
        name = table.currentItem().reader_name
        
        result, data = self.selected_task.make_first_reader(name)
        if not result:
            self.message(data, 3)
            return
            
        #self.current_readers_dict = data
        
        ## edit data in tm_table
        #tm_table = self.myWidget.task_manager_table
        #edit_task_data = dict(tm_table.currentItem().task)
        #edit_task_data['readers'] = json.dumps(self.current_readers_dict)
        #tm_table.currentItem().task = edit_task_data
    
        self.tm_edit_readers_ui_reload_table()
        self.tm_load_readers_list()
        
        
    # ---- look file ----------------
    def tm_look_file_action(self, action='push', version=False):
        pass
        #b, r = self.selected_task.open_file( look=True)
        b, r = self.selected_task.look(action=action, version=version)
        if not b:
            self.message(r, 2)
            return
        
        # MULTI_PUBLISH_TASK_TYPES
        if not self.selected_task.task_type in self.selected_task.MULTI_PUBLISH_TASK_TYPES:
            return
        
        # *************** viewers methods ******************
        def to_viewer(window):
            item = window.select_from_list_data_list_table.currentItem()
            if not item:
                self.message('No branch selected!', 2)
                return
            path = item.path['viewer_path']
            b,r = self.selected_task.run_file(path, viewer=True)
            if not b:
                self.message(r, 2)
        def to_editor(window):
            item = window.select_from_list_data_list_table.currentItem()
            if not item:
                self.message('No branch selected!', 2)
                return
            path = item.path['editor_path']
            b,r = self.selected_task.run_file(path, viewer=False)
            if not b:
                self.message(r, 2)
        
        # **************** MAKE WIDJET ********************
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
        window.select_from_list_apply_button.clicked.connect(partial(to_viewer, window))
        window.select_from_list_apply_button.setText('By Viewer')
        to_editor_button = QtWidgets.QPushButton('By Editor')
        window.horizontalLayout.addWidget(to_editor_button)
        to_editor_button.clicked.connect(partial(to_editor, window))
        window.setWindowTitle('Look Branches')
        
        # make table
        headers = ['Branch']
        if not version is False:
            data=r
        else:
            print(r)
            #data=r
            data=r[0]
        viewer_dict = data['look_path']
        if action=='push':
            editor_dict = data['push_path']
        elif action=='publish':
            editor_dict = data['publish_path']
        
        window.select_from_list_data_list_table.setColumnCount(len(headers))
        window.select_from_list_data_list_table.setRowCount(len(viewer_dict))
        window.select_from_list_data_list_table.setHorizontalHeaderLabels(headers)
        
        # selection mode   
        window.select_from_list_data_list_table.setSortingEnabled(True)
        window.select_from_list_data_list_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        window.select_from_list_data_list_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
        # make tabel
        for i,branch in enumerate(viewer_dict):
            for j,key in enumerate(headers):
                newItem = QtWidgets.QTableWidgetItem()
                newItem.path = {'viewer_path':viewer_dict[branch], 'editor_path':editor_dict[branch]}
                                
                newItem.setText(branch)
                    
                window.select_from_list_data_list_table.setItem(i, j, newItem)
                
        window.show()
        
    def tm_look_version_file_ui(self, action='push'):
        pass
        #item = self.myWidget.task_manager_table.currentItem()
        #self.current_task = item.task
        
        #get versions_list
        self.db_log.task = self.selected_task
        result = self.db_log.read_log(action=action)
        if not result[0] or not result[1][0]:
            if action=='push':
                self.message('Push versions not Found!', 2)
            elif action=='publish':
                self.message('Publish versions not Found!', 2)
            return
        else:
            versions_list = result[1][0]
            branches = result[1][1]
            
        #print(len(versions_list))
        
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
        if action=='push':
            window.setWindowTitle('Look Push Version')
        else:
            window.setWindowTitle('Look Publish Version')
        window.select_from_list_apply_button.clicked.connect(partial(self.tm_look_version_file_action, window, action))
                
        # make table
        headers = []
        for key in self.db_log.logs_keys:
            headers.append(key)
        
        window.select_from_list_data_list_table.setColumnCount(len(headers))
        window.select_from_list_data_list_table.setRowCount(len(versions_list))
        window.select_from_list_data_list_table.setHorizontalHeaderLabels(headers)
        
        # selection mode   
        window.select_from_list_data_list_table.setSortingEnabled(True)
        window.select_from_list_data_list_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        window.select_from_list_data_list_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
        # make tabel
        for i,log in enumerate(versions_list):
            print(log)
            for j,key in enumerate(headers):
                newItem = QtWidgets.QTableWidgetItem()
                newItem.log = log
                                
                if key == 'time':
                    if log.get(key):
                        newItem.setText(str(log.get(key)/3600))
                elif key == 'date_time':
                    newItem.setText(log[key].strftime("%m/%d/%Y, %H:%M:%S"))
                else:
                    newItem.setText(str(log[key]))
                    
                window.select_from_list_data_list_table.setItem(i, j, newItem)
                
        window.show()
        
    
    def tm_publish_version_ui(self, republish=False):
        pass
        #get versions_list
        self.db_log.task = self.selected_task
        if republish:
            action='publish'
        else:
            action='push'
        result = self.db_log.read_log(action=action)
        if not result[0] or not result[1][0]:
            if action=='push':
                self.message('Push versions not Found!', 2)
            elif action=='publish':
                self.message('Publish versions not Found!', 2)
            return
        else:
            versions_list = result[1][0]
            branches = result[1][1]
            
        #print(len(versions_list))
        
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
        if republish:
            window.setWindowTitle('Republish of publish Version')
        else:
            window.setWindowTitle('Publish of push Version')
        window.select_from_list_apply_button.clicked.connect(partial(self.tm_publish_action, window=window, republish=republish))
                
        # make table
        headers = []
        for key in self.db_log.logs_keys:
            headers.append(key)
        
        window.select_from_list_data_list_table.setColumnCount(len(headers))
        window.select_from_list_data_list_table.setRowCount(len(versions_list))
        window.select_from_list_data_list_table.setHorizontalHeaderLabels(headers)
        
        # selection mode   
        window.select_from_list_data_list_table.setSortingEnabled(True)
        window.select_from_list_data_list_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        window.select_from_list_data_list_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
        # make tabel
        for i,log in enumerate(versions_list):
            print(log)
            for j,key in enumerate(headers):
                newItem = QtWidgets.QTableWidgetItem()
                newItem.log = log
                                
                if key == 'time':
                    if log.get(key):
                        newItem.setText(str(log.get(key)/3600))
                elif key == 'date_time':
                    newItem.setText(log[key].strftime("%m/%d/%Y, %H:%M:%S"))
                else:
                    newItem.setText(str(log[key]))
                    
                window.select_from_list_data_list_table.setItem(i, j, newItem)
                
        window.show()
    
    def tm_look_version_file_action(self, window, action):
        pass
        item = None
        if window.select_from_list_data_list_table.selectedItems():
            item = window.select_from_list_data_list_table.selectedItems()[0]
        if not item:
            self.message('No version selected!', 2)
            return
            
        version = item.log['version']
        
        # get file_path
        self.tm_look_file_action(action=action, version=version)
        '''
        b, r = self.selected_task.open_file( look=True, version=version)
        if not b:
            self.message(r, 2)
            return
        '''

    def tm_publish_action(self, window=False, republish=False, source_log=False):
        pass
        # change task
        if not window and not source_log:
            ask = self.message(('Do you want to publish the task: "%s" ?') % self.selected_task.task_name, 0)
            if not ask:
                return
        elif window and not source_log:
            pass
            # get source log
            item = None
            if window.select_from_list_data_list_table.selectedItems():
                item = window.select_from_list_data_list_table.selectedItems()[0]
            if not item:
                self.message('No version selected!', 2)
                return
            source_log=item.log
        
        b, r = self.selected_task.publish_task(source_log=source_log, republish=republish, current_artist=self.artist)
        if not b:
            ask = self.message(r, 2)
        else:
            ask = self.message(r, 1)
            if window:
                self.close_window(window)
        
    # ---- accept task --------------
    def tm_accept_task_action(self): # v2 не ткстилось с контентом
        pass        
        # change task
        ask = self.message(('Do you want to accept the task: "%s" ?') % self.selected_task.task_name, 0)
        if not ask:
            return
        
        # get readers
        readers = self.selected_task.readers
        
        # accept task
        result = None
        if self.artist.username in readers:
            result = self.selected_task.readers_accept_task(self.artist)
        else:
            result = self.selected_task.accept_task()
        
        if not result[0]:
            self.message(result[1], 2)
            #return #to reload the page in the accident with the publish!
            
        # reload table
        self.tm_reload_task_list()
        
    # ---- close task --------------
    def tm_close_task_action(self): # v2
        pass
        
        # change task
        ask = self.message(('Do you want to close the task: "%s"?' % self.selected_task.task_name), 0)
        if ask:
            result = self.selected_task.close_task()
            if not result[0]:
                self.message(result[1], 2)
                return
        # reload table
        self.tm_reload_task_list()
    
    # ----- to rework task --------------
    def tm_rework_action(self):
        pass
        # get item
        item = self.myWidget.task_manager_table.currentItem()
        
        # change task
        ask = self.message(('Do you want to Rework the task: "%s" ?'  % self.selected_task.task_name), 0)
        if ask:
            result = self.selected_task.rework_task(self.artist)
            if not result[0]:
                self.message(result[1], 2)
                return
        # reload table
        self.tm_reload_task_list()
        
    # ---- return a job -------------
    def tm_return_a_job_action(self): # v2
        pass
        
        # change task
        ask = self.message(('Do you want to return a job the task: "%s"?' % self.selected_task.task_name), 0)
        if ask:
            result = self.selected_task.return_a_job_task()
            if not result[0]:
                self.message(result[1], 2)
                return
        # reload table
        self.tm_reload_task_list()
            
    # ---- change activity ----------
            
    def tm_change_task_activity_ui(self, *args): # v2
        pass
        # get list of activity
        #copy = db.asset()
        activity_list = self.db_asset.ACTIVITY_FOLDER[self.selected_group.type].keys()
        activity_list.sort()
        
        # create window
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.combo_dialog_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.changeActivityWindow = loader.load(file, self)
        file.close()
        
        # edit window
        window.setWindowTitle(('Change Activity of Task: %s' % self.selected_task.task_name))
        window.combo_dialog_label.setText('Select Activity:')
        window.combo_dialog_combo_box.addItems(activity_list)
        window.combo_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.combo_dialog_ok.clicked.connect(partial(self.tm_change_task_activity_action, window))
        
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()
        
    def tm_change_task_activity_action(self, window): # v2
        pass
        # get new activity
        new_activity = window.combo_dialog_combo_box.currentText()
                
        b, r_data = self.selected_task.change_activity(new_activity)
        if not b:
            self.message(r_data, 2)
            return
        
        # change table
        self.myWidget.tm_data_label_2.setText(new_activity)
        
        # edit table item (no change status)
        item_text = self.tm_get_item_text(self.selected_task)
        item = self.myWidget.task_manager_table.currentItem()
        item.setText(item_text)
        
        self.close_window(window)
        
    # ------ change price --------------
    
    def tm_change_task_price_ui(self, *args): # v2
        pass
        # get item
        item = self.myWidget.task_manager_table.currentItem()
                
        # create window
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.new_dialog_path)
        #file.open(QtCore.QFile.ReadOnly)
        window = self.changeActivityWindow = loader.load(file, self)
        file.close()
        
        # edit window
        window.setWindowTitle(('Change Price of Task: %s' % self.selected_task.task_name))
        window.new_dialog_label.setText('Select WorkRoom:')
        window.new_dialog_name.setText(str(self.selected_task.price))
        window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.new_dialog_ok.clicked.connect(partial(self.tm_change_task_price_action, window))
        
        # set modal window
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        
        window.show()
        
    def tm_change_task_price_action(self, window): # v2
        pass
        # get new workroom
        new_price = float(window.new_dialog_name.text())
                
        # change workroom
        b, r_data = self.selected_task.change_price(new_price)
        if not b:
            self.message(r_data, 2)
            return
            
        # change table
        self.myWidget.tm_data_label_5.setText(str(new_price))
        
        # edit table item (no change status)
        item_text = self.tm_get_item_text(self.selected_task)
        item = self.myWidget.task_manager_table.currentItem()
        item.setText(item_text)
        
        self.close_window(window)
        
    # ------ change artist --------------
    
    def tm_change_task_artist_ui(self, *args): # v2
        pass
        
        r_data = self.artist.get_artists_for_task_type(self.selected_task.task_type, self.db_workroom)
        if not r_data[0]:
            self.message(r_data[1], 3)
            return
        else:
            active_artists_list, self.current_artists_dict = r_data[1], r_data[2]
        
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
        window.setWindowTitle(('Change Artist of Task: "%s"' % self.selected_task.task_name))
        window.combo_dialog_label.setText('Select Artist:')
        window.combo_dialog_combo_box.addItems(active_artists_list)
        window.combo_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.combo_dialog_ok.clicked.connect(partial(self.tm_change_task_artist_action, window))
        
        window.show()
        
    def tm_change_task_artist_action(self, window): # v2
        pass
        # get new artist
        new_artist = window.combo_dialog_combo_box.currentText()
        if new_artist in ['None', '-None-']:
            new_artist = ''
        
        # change artist
        result = self.selected_task.change_artist(self.current_artists_dict.get(new_artist))
        if not result[0]:
            self.message(result[1], 2)
            return
        new_status = result[1][0]
        outsource = result[1][1]
        print(new_status, outsource)
        
        # edit labels
        self.myWidget.tm_data_label_1.setText(self.selected_task.artist)
        #task_data['artist'] = new_artist
        #if new_status:
            #task_data['status'] = new_status
        #task_data['outsource'] = outsource
        #item_.task = task_data
        
        # change table color
        rgb = self.db_task.COLOR_STATUS[self.selected_task.status]
        r = (rgb[0]*255)
        g = (rgb[1]*255)
        b = (rgb[2]*255)
        color = QtGui.QColor(r, g, b)
        brush = QtGui.QBrush(color)
        #
        item_text = self.tm_get_item_text(self.selected_task)
        item = self.myWidget.task_manager_table.currentItem()
        item.setBackground(brush)
        item.setText(item_text)
        
        self.close_window(window)
        
    # ------ change input --------------
    
    def tm_change_input_ui(self, *args): # v2
        pass        
        # get task list
        task_list = []
        result = self.selected_task.get_list()
        if result[0]:
            task_list = result[1]
            
        task_name_list = ['None']
        for task in task_list:
            if task.task_name.replace(('%s:' % task.asset.name),'') == 'final':
                continue
            elif task.task_name == self.selected_task.task_name:
                continue
            task_name_list.append(task.task_name)
        
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
        window.setWindowTitle(('Change Input Task: %s' % self.selected_task.task_name))
        window.combo_dialog_label.setText('Select Task:')
        window.combo_dialog_combo_box.addItems(task_name_list)
        window.combo_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.combo_dialog_ok.clicked.connect(partial(self.tm_change_input_action, window))
        
        window.show()
        
    def tm_change_input_action(self, window): # v2
        pass
        # get input task
        input_task = window.combo_dialog_combo_box.currentText()
        if input_task == 'None':
            input_task = False
                    
        # change input
        result = self.selected_task.change_input(input_task)
        if not result[0]:
            self.message(result[1], 2)
            return
            
        new_status = result[1][0]
        old_input_task_data = result[1][1]
        new_input_task_data = result[1][2]
        
        # edit table
        if new_status:
            item = self.myWidget.task_manager_table.currentItem()
            # change table color
            rgb = self.db_studio.COLOR_STATUS[new_status]
            r = (rgb[0]*255)
            g = (rgb[1]*255)
            b = (rgb[2]*255)
            color = QtGui.QColor(r, g, b)
            brush = QtGui.QBrush(color)
            item.setBackground(brush)
                
        # edit label
        self.myWidget.tm_data_label_4.setText(self.selected_task.input)
        
        
        self.close_window(window)
        
    # ------ change task type ------------
    def tm_change_task_type_ui(self): # v2
        pass
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
        window.setWindowTitle(('Change Task Type: %s' % self.selected_task.task_name))
        window.combo_dialog_label.setText('Select Task Type:')
        window.combo_dialog_combo_box.addItems(content_list)
        try:
            window.combo_dialog_combo_box.setCurrentIndex(content_list.index(self.selected_task.task_type))
        except:
            pass
        window.combo_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.combo_dialog_ok.clicked.connect(partial(self.tm_change_task_type_action, window))
        
        window.show()
        
    def tm_change_task_type_action(self, window): # v2
        task_type = window.combo_dialog_combo_box.currentText()
        
        b, r_data = self.selected_task.changes_without_a_change_of_status('task_type', task_type)
        if not b:
            self.message(r_data, 2)
            return
        
        # edit label
        self.myWidget.tm_data_label_6.setText(task_type)
        
        # edit table item (no change status)
        item_text = self.tm_get_item_text(self.selected_task)
        item = self.myWidget.task_manager_table.currentItem()
        item.setText(item_text)
        
        self.close_window(window)
        
    # ------ change task extension ------------
    def tm_change_task_extension_ui(self): # v2
        pass
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
        content_list = self.db_studio.EXTENSIONS
        content_list.sort()
        window.setWindowTitle(('Change Extension: %s' % self.selected_task.task_name))
        window.combo_dialog_label.setText('Select Extension:')
        window.combo_dialog_combo_box.addItems(content_list)
        try:
            window.combo_dialog_combo_box.setCurrentIndex(content_list.index(self.selected_task.extension))
        except:
            pass
        window.combo_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.combo_dialog_ok.clicked.connect(partial(self.tm_change_task_extension_action, window))
        
        window.show()
        
    def tm_change_task_extension_action(self, window): # v2
        extension = window.combo_dialog_combo_box.currentText()
        
        result = self.selected_task.changes_without_a_change_of_status('extension', extension)
        if not result[0]:
            self.message(result[1], 2)
            return
        
        # edit label
        self.myWidget.tm_data_label_7.setText(extension)
        
        # edit table item (no change status)
        item_text = self.tm_get_item_text(self.selected_task)
        item = self.myWidget.task_manager_table.currentItem()
        item.setText(item_text)
        
        self.close_window(window)
        
    # ------- change Loading Type -------------------
    
    def tm_change_loading_type(self, window):
        pass
        #copy = db.set_of_tasks()
        b, message = self.selected_task.asset.change_loading_type(window.combo_dialog_combo_box.currentText())
        if not b:
            self.message(message, 2)
        
        self.close_window(window)
        self.myWidget.tm_data_label_9.setText(self.selected_task.asset.loading_type)
        #self.reload_asset_list()
        print('change loading type action')
        
    # ------- change TZ link ----------- self.new_dialog_path
    def tm_change_tz_link_ui(self): # v2
        pass
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
        window.setWindowTitle(('Change Specification Link: %s' % self.selected_task.task_name))
        window.new_dialog_label.setText('Link:')
        window.new_dialog_name.setText(self.selected_task.specification)
        window.new_dialog_cancel.clicked.connect(partial(self.close_window, window))
        window.new_dialog_ok.clicked.connect(partial(self.tm_change_tz_link_action, window))
        
        window.show()
        
    def tm_change_tz_link_action(self, window): # v2
        link = window.new_dialog_name.text()
        
        result = self.selected_task.changes_without_a_change_of_status('specification', link)
        if not result[0]:
            self.message(result[1], 2)
            return
        
        # edit label
        self.myWidget.tm_data_label_8.setText(link)
        
        self.close_window(window)
        
    # ------- make preview ----------
    def tm_make_preview_ui(self): # v2
        self.makePreviewDialog = QtWidgets.QDialog(self)
        self.makePreviewDialog.setModal(True)
        #self.makePreviewDialog.resize(300, 300)
        self.makePreviewDialog.setWindowTitle(('Make Preview: /// %s' %  self.selected_task.asset.name))
        
        # add widgets
        v_layout = QtWidgets.QVBoxLayout()
        # -- image Label
        self.makePreviewDialog.imageLabel = QtWidgets.QLabel()
        self.makePreviewDialog.imageLabel.setFixedSize(300,300)
        v_layout.addWidget(self.makePreviewDialog.imageLabel)
        
        # -- button
        h__layout = QtWidgets.QHBoxLayout()
        button_frame = QtWidgets.QFrame(parent = self.makePreviewDialog)
        cansel_button = QtWidgets.QPushButton('Cansel', parent = button_frame)
        h__layout.addWidget(cansel_button)
        paste_button = QtWidgets.QPushButton('Paste', parent = button_frame)
        h__layout.addWidget(paste_button)
        save_button = QtWidgets.QPushButton('Save', parent = button_frame)
        h__layout.addWidget(save_button)
        button_frame.setLayout(h__layout)
        
        v_layout.addWidget(button_frame)
        self.makePreviewDialog.setLayout(v_layout)
        
        # connect buttons
        cansel_button.clicked.connect(partial(self.close_window, self.makePreviewDialog))
        paste_button.clicked.connect(partial(self.tm_paste_image_from_clipboard, self.makePreviewDialog.imageLabel))
        save_button.clicked.connect(partial(self.tm_save_preview_image_action, self.makePreviewDialog))
        
        # -- load img to label
        img_path = os.path.join(self.selected_project.preview_img_path, ('%s.png' % self.selected_task.asset.name))
        if not os.path.exists(img_path):
            self.makePreviewDialog.imageLabel.setText('No Image')
        else:
            image = QtGui.QImage(img_path)
            self.makePreviewDialog.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image))
                    
        self.makePreviewDialog.show()
    
    def tm_paste_image_from_clipboard(self, img_label): # v2
        rand  = uuid.uuid4().hex
        img_path = os.path.normpath(os.path.join(self.db_studio.tmp_folder, ('tmp_image_%s.png' % rand)))
        
        clipboard = QtGui.QApplication.clipboard()
        img = clipboard.image()
        if img:
            img.save(img_path)
            cmd = '%s %s -resize 300 %s' % (os.path.normpath(self.db_studio.convert_exe), img_path, img_path)
            cmd2 = '%s %s -resize 300x300 %s' % (os.path.normpath(self.db_studio.convert_exe), img_path, img_path)
            cmd3 = '\"%s\" \"%s\" -resize 300 \"%s\"' % (os.path.normpath(self.db_studio.convert_exe), img_path, img_path)
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
        
        
    def tm_save_preview_image_action(self, window): # v2
        pass
        # self.preview_img_path
        if not os.path.exists(self.selected_project.preview_img_path):
            try:
                os.mkdir(self.selected_project.preview_img_path)
            except:
                print(self.selected_project.preview_img_path)
                
        # copyfile
        save_path = os.path.join(self.selected_project.preview_img_path, ('%s.png' % self.selected_task.asset.name))
        icon_path = os.path.join(self.selected_project.preview_img_path, ('%s_icon.png' % self.selected_task.asset.name))
        tmp_icon_path = window.img_path.replace('.png','_icon.png')
        # -- copy
        shutil.copyfile(window.img_path, save_path)
        
        # -- resize
        cmd = '%s %s -resize 100 %s' % (os.path.normpath(self.db_studio.convert_exe), window.img_path, tmp_icon_path)
        cmd2 = '%s %s -resize 100x100 %s' % (os.path.normpath(self.db_studio.convert_exe), window.img_path, tmp_icon_path)
        cmd3 = '\"%s\" \"%s\" -resize 100 \"%s\"' % (os.path.normpath(self.db_studio.convert_exe), window.img_path, tmp_icon_path)
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
    def tm_tz(self): # v2
        if self.selected_task.specification:
            webbrowser.open_new_tab(self.selected_task.specification)
        else:
            self.message('Link not specified!', 1)
        
    # ------ add task --------------
    def tm_add_task_ui(self):
        self.addTaskDialog = QtWidgets.QDialog(self)
        self.addTaskDialog.setModal(True)
        self.addTaskDialog.resize(500, 200)
        self.addTaskDialog.setWindowTitle(('Create Single Task to Asset: /// %s' % self.selected_task.asset.name))
        
        # root frames
        v_layout = QtWidgets.QVBoxLayout()
        # -- 
        headers_frame = QtWidgets.QFrame(parent = self.addTaskDialog)
        # -- buttons frame
        button_frame = QtWidgets.QFrame(parent = self.addTaskDialog)
        # -- add frames to layout
        v_layout.addWidget(headers_frame)
        v_layout.addWidget(button_frame)
        self.addTaskDialog.setLayout(v_layout)
        
        # buttons
        h_layout = QtWidgets.QHBoxLayout()
        # -- buttons
        close_button = QtWidgets.QPushButton(parent = button_frame)
        close_button.setMaximumWidth(100)
        close_button.setText('Close')
        close_button.clicked.connect(partial(self.close_window, self.addTaskDialog))
        apply_button = QtWidgets.QPushButton(parent = button_frame)
        apply_button.setMaximumWidth(100)
        apply_button.setText('Create Task')
        apply_button.clicked.connect(partial(self.tm_add_task_action, self.addTaskDialog))
        # -- add buttons to layout
        h_layout.addWidget(close_button)
        h_layout.addWidget(apply_button)
        button_frame.setLayout(h_layout)
        
        # get task_list of asset
        result = self.selected_task.get_list()
        if not result[0]:
            self.message(result[1], 2)
            return
        task_list = result[1]
        for tsk in task_list:
            if tsk.task_type == 'service':
                #print(tsk['task_name'].split(':')[1][:5])
                if tsk.task_name.split(':')[1].endswith('final'):
                    task_list.remove(tsk)
        
        # -- Labels <-> Fields
        self.addTaskDialog.new_task_data = {}
        
        hh_layout = QtGui.QGridLayout()
        headers = ['task_name', 'input', 'output', 'activity', 'task_type', 'planned_time','price','specification', 'extension']
        for i, head in enumerate(headers):
            if head in self.REQUIRED_KEYS:
                label = QtWidgets.QLabel('%s*' % head, parent = headers_frame)
            else:
                label = QtWidgets.QLabel(head, parent = headers_frame)
            line = QtWidgets.QLineEdit(parent = headers_frame)  
            # -- line context menu
            if head in ['input', 'output', 'activity', 'task_type', 'extension']:
                textes = []
                if head == 'activity':
                    textes = self.selected_task.asset.ACTIVITY_FOLDER[self.selected_task.asset.type].keys()
                elif head == 'extension':
                    textes = self.selected_task.EXTENSIONS
                elif head == 'task_type':
                    textes = self.selected_task.task_types
                elif head == 'input':
                    textes = ['None']
                    for task_ in task_list:
                        textes.append(task_.task_name)
                elif head == 'output':
                    textes = ['None']
                    for tsk_ in task_list:
                        if tsk_.task_type != 'service':
                            textes.append(tsk_.task_name)
                line.setReadOnly(True)
                for text in textes:
                    # context menu
                    line.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
                    addgrup_action = QtWidgets.QAction( (text), self.myWidget)
                    addgrup_action.triggered.connect(partial(self.tm_set_text, line, text))
                    line.addAction( addgrup_action )
            
            hh_layout.addWidget(label, i, 0)
            hh_layout.addWidget(line, i, 1)
            
            if head == 'task_type':
                help_button = QtWidgets.QPushButton('Help', parent = headers_frame)
                help_button.setMaximumWidth(50)
                hh_layout.addWidget(help_button, i, 2)
                
            self.addTaskDialog.new_task_data[head] = line
                
        headers_frame.setLayout(hh_layout)
        
        self.addTaskDialog.show()
        
    def tm_set_text(self, widget, text): # v2
        widget.setText(text)
    
    def tm_add_task_action(self, dialog):
        task_keys = {}
        #print(dialog.new_task_data)
        
        for key in dialog.new_task_data:
            # test exists required fields
            if key in self.REQUIRED_KEYS and not dialog.new_task_data[key].text():
                self.message(('Not Key Data: "%s"' % key), 2)
                return
            if dialog.new_task_data[key].text():
                # fill task_keys
                if self.db_studio.tasks_keys[key] == 'text':
                    task_keys[key] = dialog.new_task_data[key].text().replace(' ','_')
                elif self.db_studio.tasks_keys[key] == 'integer':
                    task_keys[key] = int(dialog.new_task_data[key].text())
                elif self.db_studio.tasks_keys[key] == 'real':
                    task_keys[key] = float(dialog.new_task_data[key].text().replace(',','.'))
                elif self.db_studio.tasks_keys[key] == 'json':
                    try:
                        task_keys[key] = json.loads(dialog.new_task_data[key].text())
                    except:
                        task_keys[key] = dialog.new_task_data[key].text()
                else:
                    task_keys[key] = dialog.new_task_data[key].text()
                
            
        # edit fields
        # -- output
        if task_keys.get('output'):
            if task_keys['output'] == 'None':
                task_keys['output'] = []
            elif not task_keys['output']:
                task_keys['output'] = []
            else:
                task_keys['output'] = [task_keys['output']]
        else:
            task_keys['output'] = []
        # -- input
        if task_keys.get('input'):
            if task_keys['input'] == 'None':
                task_keys['input'] = ''
        else:
            task_keys['input'] = ''
            
        # -- task_name
        task_keys['task_name'] = '%s:%s' % (self.selected_task.asset.name, task_keys['task_name'])
        
        # test input <-> output
        if task_keys['input'] in task_keys['output']:
            self.message('Input and Output Match!', 2)
            return
        
        print(json.dumps(task_keys, sort_keys=1, indent=4))
        #return
            
        # create
        result = self.selected_task.add_single_task(task_keys)
        if not result[0]:
            self.message(result[1], 2)
            return
        else:
            self.close_window(dialog)
            self.tm_reload_task_list()
                    
    # *********************** SETTING ****************************************************
    
    def help_user_manual(self):
        webbrowser.open_new_tab('http://www.lineyka.org.ru/')

    def edit_profile_ui(self):
        webbrowser.open_new_tab(parse.urljoin(self.studio.HOST, '/users/profile/edit/'))

    def go_to_studio_web_page(self):
        webbrowser.open_new_tab(parse.urljoin(self.studio.HOST, f'/studios/{self.studio.studio_name}/'))

    def set_studio_ui(self):
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.set_window_path)
        #file.open(QtCore.QFile.ReadOnly)
        self.setWindow = loader.load(file, self)
        file.close()

        self.setWindow.setWindowTitle('Studio Settings')
        
        # add line
        # -- get extension_dict
        ext_dict = {}
        result = self.db_studio().get_extension_dict()
        if result[0]:
            ext_dict = result[1]
        
        # -- add widgets
        layout = QtWidgets.QVBoxLayout()
        for key in ext_dict:
            print(key)
            frame = QtWidgets.QFrame(parent = self.setWindow.additional_frame)
            # frame content
            h_layout = QtWidgets.QHBoxLayout()
            # -- label
            label = QtWidgets.QLabel(('exe for extension:  \"' + key + '\"'), parent = frame)
            h_layout.addWidget(label)
            # -- line edit
            line = QtWidgets.QLineEdit(parent = frame)
            line.setText(ext_dict[key])
            h_layout.addWidget(line)
            line.returnPressed.connect(partial(self.set_exe_string, line, key))
            # -- button
            button = QtWidgets.QPushButton(key, parent = frame)
            button.clicked.connect(partial(self.set_exe_path, line, key))
            h_layout.addWidget(button)
            
            frame.setLayout(h_layout)
            # frame content end
            
            layout.addWidget(frame)
            
        # EDIT EXTENSION
        frame = QtWidgets.QFrame(parent = self.setWindow.additional_frame)
        # frame content
        h_layout = QtWidgets.QHBoxLayout()
        # -- line edit
        line = QtWidgets.QLineEdit(parent = frame)
        h_layout.addWidget(line)
        # -- add button
        button = QtWidgets.QPushButton('Add Extension', parent = frame)
        button.clicked.connect(partial(self.edit_extension, line, 'ADD', self.setWindow))
        h_layout.addWidget(button)
        # -- remove button
        button = QtWidgets.QPushButton('Remove Extension', parent = frame)
        button.clicked.connect(partial(self.edit_extension, line, 'REMOVE', self.setWindow))
        h_layout.addWidget(button)
        # -- final
        frame.setLayout(h_layout)
        layout.addWidget(frame)
        # pass button
        button = QtWidgets.QPushButton(key, parent = self.setWindow.additional_frame)
        button.setDefault(True)
        button.setVisible(False)
        layout.addWidget(button)
        # --
        self.setWindow.additional_frame.setLayout(layout)
        
        # SET WORK FOLDER
        main_frame = self.setWindow.main_frame
        grid_layout = self.setWindow.gridLayout
        #
        label = QtWidgets.QLabel(parent = main_frame)
        label.setText('Work Folder:')
        grid_layout.addWidget(label, row=3, column=0)
        #
        self.wf_line = QtWidgets.QLineEdit(parent = main_frame)
        grid_layout.addWidget(self.wf_line, row=3, column=1)
        #
        wf_button = QtWidgets.QPushButton('Set Work Folder', parent = main_frame)
        grid_layout.addWidget(wf_button, row=3, column=2)

        # fill field
        data = self.db_studio.get_studio()
        if data[0]:
            self.setWindow.set_studio_field.setText(str(self.db_studio.studio_folder))
            self.setWindow.set_tmp_field.setText(str(self.db_studio.tmp_folder))
            self.setWindow.set_convert_exe_field.setText(str(self.db_studio.convert_exe))
            self.wf_line.setText(str(self.db_studio.work_folder))
    
        else:
            self.setWindow.set_studio_field.setText('set studio_folder')
            self.setWindow.set_tmp_field.setText('set tmp_folder')
            print(data[0])
            
        # connect fields
        self.setWindow.set_studio_field.returnPressed.connect(self.set_studio_action_from_line)
        self.setWindow.set_tmp_field.returnPressed.connect(self.set_tmp_path_action_from_line)
        self.setWindow.set_convert_exe_field.returnPressed.connect(self.set_convert_path_action_from_line)
        self.wf_line.returnPressed.connect(self.set_the_work_folder_action_from_line)
            
        # set modal window
        self.set_modal(self.setWindow)
        # show   
        self.setWindow.show()

        # connect button
        self.setWindow.set_studio_button.clicked.connect(self.set_studio_action)
        self.setWindow.cloud_button_01.clicked.connect(self.create_cloud_studio_ui)
        self.setWindow.cloud_button_02.clicked.connect(self.set_dir_cloud_studio_ui)
        self.setWindow.set_tmp_button.clicked.connect(self.set_tmp_path_action)
        self.setWindow.set_convert_button.clicked.connect(self.set_convert_path_action)
        wf_button.clicked.connect(self.set_the_work_folder_action)
        
        self.setWindow.rejected.connect(self.launcher)

        print('set studio ui')

    def create_cloud_studio_ui(self):
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.create_cloud_studio_path)
        # file.open(QtCore.QFile.ReadOnly)
        dialog = loader.load(file, self)
        file.close()
        #
        if hasattr(self, 'cache_cloud_studio_name'):
            dialog.text_1.setText(self.cache_cloud_studio_name)
        if hasattr(self, 'cache_cloud_studio_label'):
            dialog.text_2.setText(self.cache_cloud_studio_label)
        #
        dialog.exists_button.clicked.connect(partial(self.test_exists_studio, dialog))
        dialog.button_box.accepted.connect(partial(self.create_cloud_studio_action, dialog))

        # set modal window
        self.set_modal(dialog)
        # show
        dialog.show()

    def test_exists_studio(self, dialog):
        name=dialog.text_1.text()
        if not name:
            return
        b,r = self.studio.test_unicum(name)
        if not b:
            self.message(r, 2)
        else:
            self.message(r, 1)

    def create_cloud_studio_action(self, dialog):
        name=dialog.text_1.text()
        label=dialog.text_2.text()
        #
        if not name:
            self.message('Studio name not specified!', 2)
            return
        if not label:
            label=name
        #
        self.cache_cloud_studio_name = name
        self.cache_cloud_studio_label = label

        b,r = self.studio.studio_create(name, label)

        if not b:
            self.message(r, 2)
        else:
            self.cache_cloud_studio_name = ''
            self.cache_cloud_studio_label = ''
            self.message(f'Studio with the name "{name}", successfully created!', 1)


    def set_dir_cloud_studio_ui(self):
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.set_dir_cloud_studio_path)
        # file.open(QtCore.QFile.ReadOnly)
        dialog = loader.load(file, self)
        file.close()

        # get studios list
        b,r = self.studio.get_studios_list()
        if not b:
            self.message(r, 2)
            del dialog
            return
        self.studios = dict()
        for item in r:
            self.studios[item['studio_name']]=item

        # edit gui
        items = ['select studio']
        items.extend(list(self.studios.keys()))
        dialog.combo_box.addItems(items)
        dialog.select_button.setText('<<Set Folder')
        # dialog.text_browser.setEnabled(False)
        dialog.text_browser.setReadOnly(True)
        dialog.setWindowTitle('Set Directory of Cloud Studio')
        if hasattr(self, 'cache_cloud_studio_path'):
            dialog.path.setText(self.cache_cloud_studio_path)

        #
        def select_folder(dialog):
            home = os.path.expanduser('~')
            folder = QtWidgets.QFileDialog.getExistingDirectory(self, dir = home)
            if folder:
                dialog.path.setText(str(folder))
        # buttons
        dialog.select_button.clicked.connect(partial(select_folder, dialog))
        dialog.button_box.rejected.connect(partial(self.close_window, dialog))
        dialog.button_box.accepted.connect(partial(self.set_dir_cloud_studio_action, dialog))

        # set modal window
        self.set_modal(dialog)
        # show
        dialog.show()

    def set_dir_cloud_studio_action(self, dialog):
        studio_name=dialog.combo_box.currentText()
        path=dialog.path.text()
        # print(studio_name)
        if not studio_name in self.studios.keys():
            self.cache_cloud_studio_path = path
            self.message('Studio not selected!', 1)
            return
        else:
            b,r=self.studio.set_studio(path, self.studios[studio_name])
            if not b:
                self.message(r, 2)
                return
            self.cache_cloud_studio_path=''

    def set_studio_action(self):
        # get path
        home = os.path.expanduser('~')
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, dir = home)
        
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
        self.launcher()
        
    def set_studio_action_from_line(self):
        pass
        folder = self.setWindow.set_studio_field.text()
        
        if os.path.exists(folder):
            result = self.db_studio.set_studio(folder)
            if not result[0]:
                self.message(result[1], 2)
                
        else:
            self.message('This path is not found!', 2)
            return
          
        # finish
        print('set studio folder')
        self.message('Data saved!', 1)
        self.launcher()
    
    def set_tmp_path_action(self):
        # get path
        home = os.path.expanduser('~')
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, dir = home)
        
        if folder:
            self.setWindow.set_tmp_field.setText(str(folder))
            # set studio path
            copy = self.db_studio
            result = copy.set_tmp_dir(folder)
            if not result[0]:
                self.message(result[1], 2)
      
        # finish
        print('set tmp folder')
        
    def set_tmp_path_action_from_line(self):
        pass
        folder = self.setWindow.set_tmp_field.text()
        
        if os.path.exists(folder):
            result = self.db_studio.set_tmp_dir(folder)
            if not result[0]:
                self.message(result[1], 2)
        else:
            self.message('This path is not found!', 2)
            return
      
        # finish
        self.message('Data saved!', 1)
        print('set tmp folder')
        
    def set_convert_path_action(self):
        # get path
        home = os.path.expanduser('~')
        file_ = QtWidgets.QFileDialog.getOpenFileName(self, dir = home)[0]
        
        if file_:
            self.setWindow.set_convert_exe_field.setText(str(file_))
            # set studio path
            copy = self.db_studio
            result = copy.set_convert_exe_path(file_)
            if not result[0]:
                self.message(result[1], 2)
      
        # finish
        print('set convert.exe path')
        
    def set_convert_path_action_from_line(self):
        pass
        path = self.setWindow.set_convert_exe_field.text()
        
        result = self.db_studio.set_convert_exe_path(path)
        if not result[0]:
            self.message(result[1], 2)
        
        #if os.path.exists(path):
            #result = self.db_studio.set_convert_exe_path(path)
            #if not result[0]:
                #self.message(result[1], 2)
        #else:
            #self.message('This path is not found!', 2)
            #return
      
        # finish
        self.message('Data saved!', 1)
        print('set convert.exe path')
        
    def set_the_work_folder_action(self):
        # get path
        home = os.path.expanduser('~')
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, dir = home)
        #print(folder)
        #
        if folder:
            self.wf_line.setText(folder)
            # set studio path
            result = self.db_studio.set_work_folder(folder)
            if not result[0]:
                self.message(result[1], 2)
        # finish
        print('set work_folder path')
        
    def set_the_work_folder_action_from_line(self):
        # get path
        folder = self.wf_line.text()
        #
        if folder:
            self.wf_line.setText(folder)
            # set studio path
            result = self.db_studio.set_work_folder(folder)
            if not result[0]:
                self.message(result[1], 2)
                return
        # finish
        self.message('Data saved!', 1)
        print('set work_folder path')
        
    def set_exe_path(self, line, key):
        # get path
        home = os.path.expanduser('~')
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, dir = home)[0]
        
        if file_path:
            line.setText(str(file_path))
            
            # edit data
            result = self.studio.edit_extension_dict(key, file_path)
            if not result[0]:
                self.message(result[1], 2)
                
    def edit_extension(self, line, action, window):
        result = self.db_studio().edit_extension(line.text(), action)
        if not result[0]:
            self.message(result[1], 2)
            return
                
        window.close()
        self.set_studio_ui()
            
    def set_exe_string(self, line, key):
        text = line.text()
        
        # edit data
        result = self.studio.edit_extension_dict(key, text)
        if not result[0]:
            self.message(result[1], 2)
        else:
            self.message((key + ' changed!'), 1)
    
    def user_login_ui(self):
        pass
        #
        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile(self.login_window_path)
        #file.open(QtCore.QFile.ReadOnly)
        self.loginWindow = loader.load(file, self)
        file.close()

        # edit window
        self.loginWindow.check_box.setChecked(True)
        
        # set modal window
        self.set_modal(self.loginWindow)
        
        self.loginWindow.show()

        # connect
        self.loginWindow.rejected.connect(self.launcher)
        self.loginWindow.login_button.clicked.connect(self.user_login_action)

        # finish
        print('login ui')
    
    def user_login_action(self):
        pass
        #copy = db.artist()

        username = self.loginWindow.login_nik_name_field.text()
        password = self.loginWindow.login_password_field.text()
        
        cloud=False
        if self.loginWindow.check_box.isChecked():
            cloud=self.cloud

        login = self.artist.login_user(username, password, cloud=cloud)
    
        if login[0]:
            self.loginWindow.accept()
        else:
            self.message(login[1], 2)
            return
        
        # ---- get artist data
        self.get_artist_data(read=True, cloud=cloud)
                    
        # finish
        self.tm_fill_project_list()
        print('login action')
        
        self.launcher()
    
    def user_registration_ui(self):
        loader = QtUiTools.QUiLoader()
        f = QtCore.QFile(self.user_registr_window_path)
        #file.open(QtCore.QFile.ReadOnly)
        self.registrWindow = loader.load(f, self)
        f.close()

        # edit window
        self.registrWindow.check_box.setChecked(True)
        self.registrWindow.frame_2.setVisible(False)
        
        # set modal window
        self.set_modal(self.registrWindow)
        
        self.registrWindow.show()

        # connect
        self.registrWindow.exists_button.clicked.connect(partial(self.test_exists_artist, self.registrWindow))
        self.registrWindow.rejected.connect(self.launcher)
        self.registrWindow.user_registration_button.clicked.connect(self.user_registration_action)

        # finish
        print('registration ui')

    def test_exists_artist(self, window):
        name=window.nik_name_field.text()
        if not name:
            return
        b,r = self.artist.test_unicum( name)
        if not b:
            self.message(r, 2)
        else:
            self.message(r, 1)
    
    def user_registration_action(self):
        pass
        # get Data
        data = {
        'username' : self.registrWindow.nik_name_field.text(),
        'password' : self.registrWindow.password_field.text(),
        'email' : self.registrWindow.email_field.text(),
        'phone' : self.registrWindow.phone_field.text(),
        'speciality' : self.registrWindow.specialty_field.text(),
        'status' : 'active'
        }

        cloud=False
        if self.registrWindow.check_box.isChecked():
            cloud=self.cloud
    
        # add artist
        result = self.artist.add_artist(data, cloud=cloud)
        if result[0]:
            self.registrWindow.accept()
        else:
            self.message(result[1], 2)
            return
        
        self.get_artist_data(read = True, cloud=cloud)
                
        # finish
        # self.reload_artist_list() # debug
        self.tm_fill_project_list()
        print('user registration action')
        
        self.launcher()
    
    #*********************** UTILITS *******************************************
    def get_cache_path_from_url(self, url, r_cashe=False):
        """
        Сохраняет файл в директорию :attr:`edit_db.studio.cache_folder`. Возвращает путь до кешфайла, или *None*.

        Parameters
        ----------
        url : str
            Url до файла.
        r_cashe : bool
            Если *True* - то кеш файл перезаписывается, если *False* - то при наличии кеш файла перезаписи не будет.

        Returns
        -------
        str
            Путь до кеш файла или *None*.
        """
        if not url:
            return None
        #
        url=parse.urljoin(self.studio.HOST, url)
        icon_path = os.path.join(self.studio.cache_folder, os.path.basename(url))
        if not os.path.exists(icon_path) or r_cashe:
            response = requests.get(url)
            if not response.ok:
                return None
            with open(icon_path, 'wb') as f:
                f.write(response.content)
        #
        return icon_path

    def launcher(self):
        # return # debug
        if not self.db_studio.studio_folder or not os.path.exists(self.db_studio.studio_folder):
            self.login_or_registration_ui(message='Path to the studio directory is not specified or not correct!')
            return
        elif not self.artist.username:
            self.login_or_registration_ui(message='Nikname is: "%s"' % self.artist.username)
            return

        # ---- self.WORKROOM ---- 
        b,r = self.db_workroom.get_list() # загрузка списка отделов с проверкой на причастность юзера к данной студии.
        if not b:
            self.login_or_registration_ui(message=r)

        ''' # debug
        elif not self.artist.level or not self.artist.level in self.db_studio.MANAGER_LEVELS:
            self.login_or_registration_ui(message='No permission. Level is: "%s"' % self.artist.level)
        '''
            
    def login_or_registration_ui(self, message=False):
        def login_or_registration_to_login(dialog):
            dialog.accept()
            self.user_login_ui()
            
        def login_or_registration_to_registration(dialog):
            dialog.accept()
            self.user_registration_ui()
        
        def login_or_registration_to_set_studio(dialog):
            dialog.accept()
            self.set_studio_ui()
        #
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle('Login or register')
        dialog.setModal(True)
        dialog.resize(200, 100)
        
        #
        v_layout = QtWidgets.QVBoxLayout()
        button_frame = QtWidgets.QFrame(parent = dialog)

        if message:
            text_block = QtWidgets.QTextBrowser()
            m=f"<span style=\" color:#ff6600;\" > {message} </span>"
            text_block.setText(m)
            text_block.setReadOnly(True)

        # set_studio_button
        set_studio_button = QtWidgets.QPushButton()
        # set_studio_button.setMaximumWidth(200)
        set_studio_button.setMinimumHeight(40)
        set_studio_button.setText('Set Studio')
        set_studio_button.clicked.connect(partial(login_or_registration_to_set_studio, dialog))
        # login_button
        login_button = QtWidgets.QPushButton()
        # login_button.setMaximumWidth(200)
        login_button.setMinimumHeight(40)
        login_button.setText('Login')
        login_button.clicked.connect(partial(login_or_registration_to_login, dialog))
        # reg_button
        reg_button = QtWidgets.QPushButton()
        # reg_button.setMaximumWidth(200)
        reg_button.setMinimumHeight(40)
        reg_button.setText('Registration')
        reg_button.clicked.connect(partial(login_or_registration_to_registration, dialog))
        
        v_layout.addWidget(text_block)
        v_layout.addWidget(set_studio_button)
        v_layout.addWidget(login_button)
        v_layout.addWidget(reg_button)
        
        #v_layout.addWidget(button_frame)
        dialog.setLayout(v_layout)
        
        dialog.rejected.connect(partial(self.close_window, self))
        dialog.show()
        
    def get_artist_data(self, read = True, cloud=False):
        # get studio data $ 
        studio = 'Undefined Studio'
        if os.path.exists(self.studio.studio_folder):
            if self.studio.studio_database[0] == 'sqlite3':
                studio = 'Local Studio'
            elif self.studio.studio_label:
                studio = self.studio.studio_label

        # ---- get artist data
        if read:
            b,r = self.artist.get_user(cloud=cloud)
            if not b:
                self.message(r, 2)
                self.setWindowTitle(f'Lineyka : {studio} : Undefined User')
            else:
                self.setWindowTitle(f'Lineyka : {studio} : {self.artist.username}')
                
        else:
            self.setWindowTitle(f'Lineyka : {studio} : {self.artist.username}')
    
    def close_window(self, window):
        if window:
            window.close()
    
    def set_modal(self, window):
        window.setWindowModality(QtCore.Qt.WindowModal)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

    def clear_table(self, table = False):
        if not table:
            table = self.myWidget.studio_editor_table
        
        # disconnects
        # -- context menu
        try:
            table.customContextMenuRequested.disconnect()
        except Exception as e:
            print(e)
            
        # -- context menu
        try:
            table.itemDoubleClicked.disconnect()
        except Exception as e:
            print(e)
        
        # -- clear table
        num_row = table.rowCount()
        num_column = table.columnCount()
        
        # new
        table.clear()
        table.setColumnCount(0)
        table.setRowCount(0)
                
    
    def message(self, m, i):
        #m = str(m)
        
        mBox = QtWidgets.QMessageBox()
        mBox.setText(m)
        #mBox.setStandardButtons( QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok )
        ok_button = mBox.addButton(QtWidgets.QMessageBox.Ok)
        cancel_button = mBox.addButton(QtWidgets.QMessageBox.Cancel)
    
        if i==1:
            mBox.setIcon(QtWidgets.QMessageBox.Information)
            mBox.setWindowTitle('Info')
        elif i == 2:
            mBox.setIcon(QtWidgets.QMessageBox.Warning)
            mBox.setWindowTitle('Warning!')
        elif i == 3:
            mBox.setIcon(QtWidgets.QMessageBox.Critical)
            mBox.setWindowTitle('Error!')
        elif i == 0:
            mBox.setIcon(QtWidgets.QMessageBox.Question)
            mBox.setWindowTitle('Confirm!')
    
        com = mBox.exec_()
    
        if mBox.clickedButton() == ok_button:
            return(True)
        elif mBox.clickedButton() == cancel_button:
            return(False)
      
    def print_data(self, *args):
        print(args)

if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    app.exec_()
