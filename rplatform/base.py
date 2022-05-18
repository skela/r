import os


class RBase(object):

	@staticmethod
	def is_number(s):
		try:
			float(s)
			return True
		except ValueError:
			return False

	@staticmethod
	def components_for_line(line):

		succeeded = False
		w = None
		h = None
		method = "auto"
		svg = None
		png = None
		action = None

		if not line.startswith("#"):

			sline = line
			if "|" in line:
				sline = line[0:line.find("|")]
				action = line[line.find("|")+1:len(line)]

			comps = sline.split(",")
			if not len(comps) == 0:
				if len(comps) >= 2:
					if not RBase.is_number(comps[0]):
						method = comps[0]
						comps = comps[1:len(comps)]
					if RBase.is_number(comps[0]):
						w = comps[0]
						comps = comps[1:len(comps)]
					if RBase.is_number(comps[0]):
						h = comps[0]
						comps = comps[1:len(comps)]
					if len(comps) > 0:
						svg = comps[0]
						if len(comps) > 0:
							comps = comps[1:len(comps)]
						succeeded = True
					if len(comps) > 0:
						png = comps[0]
		return succeeded, method, w, h, svg, png, action

	@staticmethod
	def script_for_line(line):
		if not line.startswith("#"):
			comps = line.split(",")
			if len(comps) == 1:
				c = comps[0]
				if c.endswith('.sh') or c.endswith('.py'):
					return os.path.join(os.curdir, c)
		return None

	# Load File
	#   path_to_resources_file = path to the file that lists resources in the following format:
	#       w,h,sfile,png
	#       w,sfile,png
	#       w,sfile
	#       method,w,h,sfile,png
	#       method,w,sfile,png
	#   path_to_resources_folder = path to the folder containing all the input graphics
	def run_file(self, path_to_resources_file, path_to_resources_folder):
		f = open(path_to_resources_file)
		s = f.read()
		f.close()
		l = s.split("\n")
		self.run_lines(l, path_to_resources_folder)

	def run_lines(self, lines, path_to_resources_folder):

		for line in lines:

			if line.startswith('exit'):
				break

			script = RBase.script_for_line(line)
			if script is not None:
				os.system(script)

			(succeeded, method, w, h, sfile, png, action) = RBase.components_for_line(line)
			if not succeeded:
				continue

			if method != "launch_image":
				sfile = os.path.join(path_to_resources_folder, sfile)
				if len(os.path.splitext(sfile)[1]) == 0:
					sfile += ".svg"

			ret = None
			if method == "auto":
				if sfile.endswith(".xcf"):
					self.xcf2pngs(w, h, sfile, png)
				elif sfile.endswith(".png") or sfile.endswith(".jpg") or sfile.endswith(".jpeg"):
					self.png2pngs(w, h, sfile, png)
				else:
					ret = self.svg2pngs(w, h, sfile, png)
			elif method == "asset":
				if sfile.endswith(".xcf"):
					ret = self.xcf2pngs(w, h, sfile, png, use_assets=True)
				elif sfile.endswith(".png"):
					ret = self.png2pngs(w, h, sfile, png, use_assets=True)
				else:
					ret = self.svg2pngs(w, h, sfile, png, use_assets=True)
			elif method == "svg" or method == "inkscape":
				ret = self.svg2pngs(w, h, sfile, png)
			elif method == "svg2png":
				ret = self.svg2png(w, h, sfile, png)
			elif method == "ic_menu_icon":
				self.ic_menu_icon(sfile, png)
			elif method == "icon" or method == "app_icon":
				self.icon(sfile)
			elif method == "watch_icon" or method == "icon_watch":
				self.icon(sfile,device="watch")
			elif method == "launch_image":
				sfiles = sfile.split(':')
				svg_bg = sfiles[0]
				svg_centred = sfiles[1]
				#svg_bg = os.path.abspath(os.path.join(path_to_resources_folder, svg_bg))
				svg_bg = os.path.abspath(svg_bg)
				svg_centred = os.path.abspath(os.path.join(path_to_resources_folder, svg_centred))
				self.launch_image(svg_bg, svg_centred, w, h)
			elif method == "pdf":
				self.svg2pdf(sfile, png)

			if ret is not None and action is not None:
				action = action.strip()
				if "->" in action:
					clrs = action.split("->")
					clr_from = clrs[0]
					clr_to = clrs[1]
					for img in ret:
						self.r.convert_color(img, img, clr_from, clr_to)
				elif action.startswith("-"):
					for img in ret:
						self.r.convert(img, img, action)

	@staticmethod
	def create_run_file_header():
		c = '''#Resource Ordnance Declaration File
# Download ROD here https://github.com/skela/r
# To run this `rod -u` 
#
# Examples:
# w,h,sfile,png
# w,h,sfile,png|white->black
# w,sfile,png
# w,sfile
# method,w,h,sfile,png
# method,w,sfile,png
#
# Most will be of the form:
# w,h,source_file,destination_file
# For example:
# 14,14,test.svg,test.png
#
# Methods: 
# > auto (default, if no method is defined)
# > asset 
# > svg
# > inkscape
# > svg2png
# > ic_menu_icon
# > icon
# > app_icon
# > watch_icon
# > icon_watch
# > launch_image
# > pdf  
#

# Remove the ROD overrides below that you don't need or want, the ones you do want, they do need to start with ### to take effect

### PLATFORM=ios
### XCASSETS=AppProject/Assets.xcassets/

### PLATFORM=droid
### OUTPUT=app/src/main/res/
### INPUT=raw/

### PLATFORM=flutter
### OUTPUT=images/
### INPUT=raw/

'''
		return c


