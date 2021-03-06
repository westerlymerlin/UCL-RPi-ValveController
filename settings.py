import json

version = '1.1.3'
settings = {}


def writesettings():
    with open('settings.json', 'w') as outfile:
        json.dump(settings, outfile, indent=4, ensure_ascii=True, sort_keys=True)


def initialise():
    global settings
    settings['logging'] = {}
    settings['logging']['logfilepath'] = './logs/valvecontroller.log'
    settings['logging']['logappname'] = 'Valve-Controller-Py'
    settings['logging']['gunicornpath'] = './logs/'
    settings['logging']['cputemp'] = '/sys/class/thermal/thermal_zone0/temp'
    with open('settings.json', 'w') as outfile:
        json.dump(settings, outfile, indent=4, ensure_ascii=True, sort_keys=True)


def readsettings():
    global settings
    try:
        with open('settings.json') as json_file:
            settings = json.load(json_file)
    except FileNotFoundError:
        initialise()


readsettings()

