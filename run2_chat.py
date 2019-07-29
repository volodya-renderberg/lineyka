#!/usr/bin/python
# -*- coding: utf-8 -*-

import edit_db as db
#import run_chat
import sys
import subprocess as sub
import os

def run(project_name, task_name):
	path = os.path.join(os.path.dirname(__file__), 'run_chat.py')
	print(path)
	
	cmd = 'python %s %s %s' % (path, project_name, task_name)
	sub.Popen(cmd, shell = True)
