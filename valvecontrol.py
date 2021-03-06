from RPi import GPIO
from time import sleep
from logmanager import *
from settings import version
from threading import Timer



print('Application starting')
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
channellist = [23, 17, 13, 19, 18, 27, 9, 24, 22, 11, 21, 26, 20]
GPIO.setup(channellist, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)

valves = [
    {
        'id': 1,
        'gpio': channellist[0],
        'description': '4He pipette input',
        'excluded': 2
    },
    {
        'id': 2,
        'gpio': channellist[1],
        'description': '4He pipette output',
        'excluded': 1
    },
    {
        'id': 3,
        'gpio': channellist[2],
        'description': '3He pipette output',
        'excluded': 4
    },
    {
        'id': 4,
        'gpio': channellist[3],
        'description': '3He pipette input',
        'excluded': 3
    },
    {
        'id': 5,
        'gpio': channellist[4],
        'description': 'port 1',
        'excluded': 8
    },
    {
        'id': 6,
        'gpio': channellist[5],
        'description': 'ion pump',
        'excluded': 5
    },
    {
        'id': 7,
        'gpio': channellist[6],
        'description': 'gas analyser',
        'excluded': 5
    },
    {
        'id': 8,
        'gpio': channellist[7],
        'description': 'gallery A',
        'excluded': 5
    },
    {
        'id': 10,
        'gpio': channellist[8],
        'description': 'laser cell',
        'excluded': 5
    },
    {
        'id': 11,
        'gpio': channellist[9],
        'description': 'getter',
        'excluded': 5
    },
    {
        'id': 12,
        'gpio': channellist[10],
        'description': 'buffer tank',
        'excluded': 5
    },
    {
        'id': 13,
        'gpio': channellist[11],
        'description': 'turbo pump',
        'excluded': 5
    }
]


def parsecontrol(item, command):
    # print('%s : %s' % (item, command))
    try:
        if item[:5] == 'valve':
            valve = int(item[5:])
            if 0 < valve < 14:
                if command == 'open':
                    valveopen(valve)
                elif command == 'close':
                    valveclose(valve)
                else:
                    print('bad valve command')
            else:
                print('bad valve number')
        elif item[:7] == 'pipette':
            pipette = int(item[7:])
            if pipette == 1:
                if command == 'load':
                    he4pipetteload()
                elif command == 'unload':
                    he4pipetteunload()
                elif command == 'close':
                    he4pipetteclose()
                else:
                    print('bad pipette command')
            elif pipette == 2:
                if command == 'load':
                    he3pipetteload()
                elif command == 'unload':
                    he3pipetteunload()
                elif command == 'close':
                    he3pipetteclose()
                else:
                    print('bad pipette command')
            else:
                print('bad pipette number')
        elif item == 'laser':
            if command == 'on':
                laser(1)
            else:
                laser(0)
        elif item == 'closeallvalves':
            allclose()
    except ValueError:
        print('incorrect json message')
    except IndexError:
        print('bad valve number')


def valveopen(valveid):
    valve = [valve for valve in valves if valve['id'] == valveid]
    if GPIO.input([valvex for valvex in valves if valvex['id'] == valve[0]['excluded']][0]['gpio']) == 1:
        print('cannot open valve as the excluded one is also open valve %s' % valveid)
    else:
        GPIO.output(valve[0]['gpio'], 1)
        print('Valve %s opened' % valveid)


def valveclose(valveid):
    valve = [valve for valve in valves if valve['id'] == valveid]
    GPIO.output(valve[0]['gpio'], 0)
    print('Valve %s closed' % valveid)


def allclose():
    GPIO.output(channellist, 0)
    print('All Valves Closed')


def he3pipetteload():
    valveclose(3)
    sleep(1)
    valveopen(4)


def he3pipetteclose():
    valveclose(3)
    valveclose(4)


def he3pipetteunload():
    valveclose(4)
    sleep(1)
    valveopen(3)


def he4pipetteload():
    valveclose(2)
    sleep(1)
    valveopen(1)


def he4pipetteclose():
    valveclose(2)
    valveclose(1)


def he4pipetteunload():
    valveclose(1)
    sleep(1)
    valveopen(2)


def status(value):
    if value == 0:
        return 'closed'
    else:
        return 'open'


def laser(state):
    if state == 1:
        print('Laser is on')
        GPIO.output(20, 1)
        # Start a 5 minute timeer for the laser, if the laser is not shutdown by PyMS then this timer will shut it down
        timerthread = Timer(300, lambda: laser(0))
        timerthread.start()
    else:
        print('Laser is off')
        GPIO.output(20, 0)


def valvestatus():
    statuslist = []
    for valve in valves:
        if valve['id'] > 0:
            statuslist.append({'valve': valve['id'], 'status': status(GPIO.input(valve['gpio']))})
    statuslist.append(laserstatus())
    return statuslist


def httpstatus():
    statuslist = []
    for valve in valves:
        if valve['id'] > 0:
            statuslist.append({'id': valve['id'], 'description': valve['description'],
                               'status': status(GPIO.input(valve['gpio']))})
    return statuslist


def laserstatus():
    if GPIO.input(20) == 1:
        return {'laser': 0, 'status': 'on'}
    else:
        return {'laser': 0, 'status': 'off'}


GPIO.output(12, 1)   # set ready
print('Running version %s' % version)
print('Application ready')
