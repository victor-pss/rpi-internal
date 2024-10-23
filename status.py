import subprocess

def import_or_install(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.call(['sudo', 'pip', 'install', package])

import_or_install('requests')
import_or_install('socket')
import_or_install('platform')
import_or_install('gpiozero')

import requests
import socket
import platform
import gpiozero
import os
import sys
from PIL import Image

# define a function for
# compressing an image
def compressMe(file, verbose = False):
    # Get the path of the file
    filepath = os.path.join(os.getcwd(), file)

    # open the image
    picture = Image.open(filepath)

    # Save the picture with desired quality
    # To change the quality of image,
    # set the quality variable at
    # your desired level, The more
    # the value of quality variable
    # and lesser the compression
    picture.save("Compressed_" + file, "JPEG", optimize = True, quality = 10)

    return

verbose = False

# checks for verbose flag
if (len(sys.argv) > 1):
    if (sys.argv[1].lower() == "-v"):
        verbose = True

# finds current working dir
cwd = os.getcwd()
print(cwd)
print(os.listdir(cwd))

formats = ('.jpg', '.jpeg')

def getserial():
    cpuserial = "0000000000"
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:6] == 'Serial':
                cpuserial = line[10:26]
        f.close()
    except:
        cpuserial = 'ERROR0000000000'

    return cpuserial

def cleanup():
    dir_name = "/home/pi"
    test = os.listdir(dir_name)

    for item in test:
        if item.endswith('.jpg'):
            os.remove(os.path.join(dir_name, item))

deviceserial = getserial()
cpu = gpiozero.CPUTemperature()
pi = subprocess.check_output(['cat', '/proc/device-tree/model'])
pi = pi.decode('utf-8')
py = platform.python_version()
osv = subprocess.check_output(['cat', '/etc/os-release', '-E'])
osv = osv.decode('utf-8')
osv = osv.split('$')[0].split('=')[1].split('"')[1]

# looping through all the files
# in a current directory
for file in os.listdir(cwd):

    # If the file format is JPG or JPEG
    if os.path.splitext(file)[1].lower() in formats:
        print('compressing', file)
        compressMe(file, verbose)
path_img = '/home/pi/Compress_%s.jpg' % deviceserial
files = {}
url = 'https://device-status-lypegykfyq-uw.a.run.app/v1/file-upload'
status = ''
with open(path_img, 'rb') as img:
    name_image = os.path.basename(path_img)
    files = {'image': (name_image, img, 'multipart/form-data', {'Expires': '0'})}
    with requests.Session() as s:
        r = s.post(url, files = files)
        status = r.status_code
        print(status)

try:
    #get connected wifi netowrk on wlan0
    output = subprocess.check_output(['sudo', 'iwgetid'])
    output = output.decode('utf-8')

    ssid = output.split('"')[1]

    url = 'https://device-status-lypegykfyq-uw.a.run.app/v1/wifi-log'
    body = {'serial': deviceserial, 'device': socket.gethostname(), 'wifi': ssid, 'temperature': cpu.temperature, 'pi': pi, 'pyversion': py, 'os': osv, 'cstatus': status}
    x = requests.post(url, data = body)
    print(x.json())
except subprocess.CalledProcessError:
    ssid = 'No Wifi Networks Connected'

    url = 'https://device-status-lypegykfyq-uw.a.run.app/v1/wifi-log'
    body = {'serial': deviceserial, 'device': socket.gethostname(), 'wifi': ssid, 'temperature': cpu.temperature, 'pi': pi, 'pyversion': py, 'os': osv, 'cstatus': status}
    x = requests.post(url, data = body)
    print(x.json())

cleanup()
