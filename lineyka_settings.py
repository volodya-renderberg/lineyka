# -*- coding: utf-8 -*-

HOST = "http://localhost:8000/"
COOKIE_NAME = '.cookie'
USER_DATA_FILE_NAME = '.user_data.json'
FARME_OFFSET = 100
STUDIO_SETTINGS_FILE = 'settings.py'
CACHE = '.lineyka_cache'
EXTENSIONS = ['.blend', '.ma', '.tiff', '.ntp']
SETTING_DATA = {
'extension': {
    '.tiff':'krita',
    '.blend': 'blender',
    '.ntp': 'natron',
    '.ma': 'maya',
    '.ods':'libreoffice',
    },
'task_visible_fields':[
    'activity',
    'task_type',
    'artist',
    'priority',
    'extension',]}
LOOK_EXTENSION = '.jpg'
PREVIEW_EXTENSION = '.png'
PUBLISH_FOLDER_NAME = 'publish'
USER_LEVELS = ('user', 'extend_user', 'manager', 'root')
MANAGER_LEVELS = ('manager', 'root')
task_status = ('null','ready', 'ready_to_send', 'work', 'work_to_outsorce', 'pause', 'recast', 'checking', 'done', 'close')
WORKING_STATUSES = ('ready', 'ready_to_send', 'work', 'work_to_outsorce', 'pause', 'recast')
END_STATUSES = ('done', 'close')
EMPTY_FILES_DIR_NAME = 'empty_files'
COLOR_STATUS = {
'null':(0.451000005, 0.451000005, 0.451000005),
#'ready':(0.7627863884, 0, 1),
'ready':(0.826, 0.249, 1),
'ready_to_send':(0.9367088675, 0.2608556151, 0.4905878305),
'work':(0.520749867, 0.7143493295, 0.8227847815),
'work_to_outsorce':(0.2161512673, 0.5213058591, 0.8987341523),
#'pause':(0.3417721391, 0.2282493114, 0.1557442695),
'pause':(0.670, 0.539, 0.827),
'recast':(0.8481012583, 0.1967110634, 0.1502964497),
'checking':(1, 0.5872552395, 0.2531645298),
'done':(0.175, 0.752, 0.113),
#'close':(0.1645569652, 0.08450711519, 0.02499599569)
'close':(0.613, 0.373, 0.195)
}
PROJECTS_UNITS = ('m', 'cm', 'mm')
PROJECTS_STATUSES = ('active', 'none')
TASK_TYPES = (
# -- film
'animatic',
'film',
#
'sketch',
'textures',
# -- model
'sculpt',
'model',
# -- rig
'rig',
'test_animation', # анимация для проверки рига - активити test_animation
# -- location,
'specification',
'location',
#'location_full',
#'location_for_anim',
# -- animation
'animation_shot',
'tech_anim',
'simulation_din',
#'simulation_fluid',
'render',
'composition',
)
MULTI_PUBLISH_TASK_TYPES = ('sketch',)
SERVICE_TASKS = ('all', 'pre')
ASSET_TYPES = (
'object',
'location',
'shot_animation',
'film'
)
ASSET_TYPES_WITH_SEASON = (
'animatic',
'shot_animation',
'camera',
'shot_render',
'shot_composition',
'film'
)
LOADING_TYPES = ('mesh', 'group', 'rig')
INIT_FOLDER = '.lineyka'
INIT_FILE = 'lineyka_init.json'
SET_FILE = 'user_setting.json'
LOCATION_POSITION_FILE = 'location_content_position.json'
USER_REGISTR_FILE_NAME = 'user_registr.json'
LIST_OF_ASSETS_NAME = '.list_of_assets.json'
PROJECT_SETTING = '.project_setting.json'
BLEND_SERVICE_IMAGES = {
'preview_img_name' : 'Lineyka_Preview_Image',
'bg_image_name' : 'Lineyka_BG_Image',
}