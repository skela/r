# r

## ROD - Resource Ordnance Declaration - rod.py

Resource generation system based on declarations in Rodfile (Resource Ordnance Declaration).

Example Rodfile

```
### OUTPUT=assets/images
### INPUT=raw
### PLATFORM=flutter

50,50,a.svg,a.webp

### OUTPUT=app/src/main/res
### INPUT=raw
### PLATFORM=android

50,50,a.svg,a.png

### OUTPUT=assets/
### INPUT=raw
### PLATFORM=web

50,50,a.svg,a.webp
```

Currently supported platforms: ios, android, flutter, web

First init to get started:

`rod --init`

To run it:

`rod -u`

More info in help:

`rod -h`

# Using docker

You can also use docker so you don't have to install anything.

```
image = "skela/rod:latest"
volumes = [
	f'-v {os.path.abspath("Rodfile")}:/res/Rodfile',
	f'-v {os.path.abspath("Rodfile.locked")}:/res/Rodfile.locked',
	f'-v {os.path.abspath("raw/")}:/res/raw/',
	f'-v {os.path.abspath("assets/images/")}:/res/assets/images/'
]
volumes = " ".join(map(lambda x: x,volumes))
command_run = subprocess.call(f"docker run -i {volumes} {image} python3 /rod/rod.py -u -f Rodfile", stderr=subprocess.STDOUT, shell=True)
if command_run != 0:
	exit("Failed to generate images")
```

# R - r.py

Resource Recipes for converting between svg, xcf, pdf, png, webp and pngs in the different scales required so that they can be used by iOS, Android and Web apps.
