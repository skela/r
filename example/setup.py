import os
import subprocess

image = "skela/rod:latest"
volumes = [
	f'-v {os.path.abspath("Rodfile")}:/res/Rodfile',
	f'-v {os.path.abspath("Rodfile.locked")}:/res/Rodfile.locked',
	f'-v {os.path.abspath("raw/")}:/res/raw/',
	f'-v {os.path.abspath("droid/")}:/res/droid/',
	f'-v {os.path.abspath("flutter/")}:/res/flutter/',
	f'-v {os.path.abspath("web/")}:/res/web/',
]
volumes = " ".join(map(lambda x: x, volumes))
cmd = f"docker run -i {volumes} {image} rod -u"
command_run = subprocess.call(cmd, stderr=subprocess.STDOUT, shell=True)
if command_run != 0:
	exit("Failed to generate images")
