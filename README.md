r
=

## ROD - Resource Ordnance Declaration - rod.py

Resource generation system based on declarations in Rodfile (Resource Ordnance Declaration)

Currently supported platforms: ios, android, flutter, xamarin-ios, xamarin-android

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

Resource Recipes for converting svg, xcf, pdf, png, webp to pngs in the differents scales required so that they can be used by iOS and Android apps.
