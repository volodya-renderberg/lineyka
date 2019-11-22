import os
import json
import sys
import tempfile

import edit_db as db

def make_studio():
	db.studio()
	
	tmp = tempfile.gettempdir()
	studio_path = os.path.join(tmp, 'studio')
	
	# studio
	if not os.path.exists(studio_path):
		os.mkdir(studio_path)
	db.studio.set_studio(studio_path)
	
	# project
	project = db.project()
	print(project.add_project('Project', ''))
	#
	project.init('Project', new=False)
	
	# set of tasks
	modul_dir = os.path.dirname(__file__)
	path = os.path.join(modul_dir, 'Set_Of_Tasks_Library.json')
	b, r = db.set_of_tasks().get_list(path = path)
	if b:
		for sett in r:		
			db.set_of_tasks().create(sett.name, sett.asset_type, sett.loading_type, sett.sets)
	
	# workrooms
	wr = db.workroom()
	main = wr.add({'type': db.studio.task_types, 'name': 'Main'}, new=True)
	
	# artists
	artist = db.artist()
	artist.add_artist({'nik_name': 'vofka', 'password': '1234', 'workroom': [main.id], 'status': 'active'}, registration=True)
	artist.add_artist({'nik_name': 'dimka', 'password': '1234', 'workroom': [main.id], 'status': 'active'}, registration=False)
	artist.add_artist({'nik_name': 'slavka', 'password': '1234', 'workroom': [main.id], 'status': 'active', 'outsource': 1}, registration=False)
	artist.get_user()
	artists = [artist.init('vofka'), artist.init('dimka'), artist.init('slavka')]
	
	# props
	# -- group
	group = db.group(project)
	print(group.create({'name':'props', 'type':'object'}))
	props = group.init('props')
	
	# -- asset
	asset = db.asset(project)
	# -- topor
	keys = {'name':'topor', 'set_of_tasks':'Props_simple', 'group':props.id}
	print(asset.create('object', [keys]))
	topor = asset.init('topor')
	# -- vedro
	keys = {'name':'vedro', 'set_of_tasks':'Props_simple', 'group':props.id}
	print(asset.create('object', [keys]))
	vedro = asset.init('vedro')
	# -- task
	tasks = [db.task(topor), db.task(vedro)]
	
	for task in tasks:
		i=0
		for tsk in task.get_list()[1]:
			if tsk.task_type == 'service':
				continue
			tsk.change_artist(artists[i])
			i=i+1
	
	# locations
	# -- group
	print(group.create({'name':'locations', 'type':'location'}))
	locations = group.init('locations')
	# -- asset
	keys = {'name':'location_01', 'set_of_tasks':'Location', 'group':locations.id}
	print(asset.create('location', [keys]))
	location = asset.init('location_01')
	
	return(project, topor, vedro, location)

if __name__=='__main__':
	if len(sys.argv) < 2:
		make_studio()
	elif sys.argv[1] == 'make':
		make_studio()
