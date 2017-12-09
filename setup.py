#!/usr/bin/python
# -*- coding: utf-8 -*-

import platform
import os
import sys

linux_manager_file_data = '''
[Desktop Entry]
Name=Lineyka for Managers
Comment=
GenericName=Lineyka Gui for Managers
Keywords=lineyka manager линейка менеджер
Exec=%s
Terminal=true
Type=Application
Icon=%s
Path=%s
Categories=
NoDisplay=false
'''

linux_artist_file_data = '''
[Desktop Entry]
Name=Lineyka for Artists
Comment=
GenericName=Lineyka Gui for Artists
Keywords=lineyka user artist линейка артист пользователь
Exec=%s
Terminal=true
Type=Application
Icon=%s
Path=%s
Categories=
NoDisplay=false
'''

def linux_setup():
	#manager
	save_path = os.path.join(os.path.expanduser('~'),'.local/share/applications/lineyka_manager.desktop')
	#save_path = os.path.join(os.path.expanduser('~'), 'lineyka_manager.desktop')
	path_dir = os.getcwd()
	manager_exec = os.path.join(path_dir, 'lineyka_manager.py')
	manager_icon = os.path.join(path_dir, 'manager_icon.png')
	
	cmd = 'sudo chmod +x %s' % manager_exec
	os.system(cmd)
	
	with open(save_path, 'w') as f:
		f.write(linux_manager_file_data % (manager_exec, manager_icon, path_dir))
		
	#user
	save_path = os.path.join(os.path.expanduser('~'),'.local/share/applications/lineyka_artist.desktop')
	#save_path = os.path.join(os.path.expanduser('~'), 'lineyka_artist.desktop')
	user_exec = os.path.join(path_dir, 'lineyka_user.py')
	user_icon = os.path.join(path_dir, 'user_icon.png')
	
	cmd = 'sudo chmod +x %s' % user_exec
	os.system(cmd)
	
	with open(save_path, 'w') as f:
		f.write(linux_artist_file_data % (user_exec, user_icon, path_dir))
		
if platform.system() == 'Linux':
	linux_setup()

