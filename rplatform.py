
import os
import json
import shutil

from r import R
from r import RUtils


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

			if method is not "launch_image":
				sfile = os.path.join(path_to_resources_folder, sfile)
				if len(os.path.splitext(sfile)[1]) == 0:
					sfile += ".svg"

			ret = None
			if method == "auto":
				if sfile.endswith(".xcf"):
					self.xcf2pngs(w, h, sfile, png)
				elif sfile.endswith(".png"):
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
		c = '''#  w,h,sfile,png
#  w,h,sfile,png|white->black
#  w,sfile,png
#  w,sfile
#  method,w,h,sfile,png
#  method,w,sfile,png
'''
		return c


class RDroidDensity(object):

	def __init__(self, density):
		self.drawable_folder = "drawable-" + density
		self.scale = 1
		if density == "ldpi":
			self.scale = 0.75
		elif density == "mdpi":
			self.scale = 1
		elif density == "hdpi":
			self.scale = 1.5
		elif density == "xhdpi":
			self.scale = 2
		elif density == "xxhdpi":
			self.scale = 3
		elif density == "xxxhdpi":
			self.scale = 4


class RDroid(RBase):

	def __init__(self, path_droid_resources, path_inkscape=None, path_convert=None):
		self.r = R(path_inkscape, path_convert)
		self.path_droid_resources = path_droid_resources
		self.densities = [RDroidDensity("xhdpi")]

	def set_densities(self, densities):
		self.densities = []
		dens = densities
		if not isinstance(densities, (list, tuple)):
			dens = densities.split(",")
		for density in dens:
			self.densities.append(RDroidDensity(density))

	def out_path_from_out_name(self, density, svg_file, out_name=None):
		dr = os.path.join(self.path_droid_resources, density.drawable_folder)
		o_name = out_name
		if o_name is None:
			icon_name = os.path.basename(svg_file)
			o_name = icon_name.replace('.svg', '.png')
		out_path = os.path.join(dr, o_name)
		return out_path

	def ic_menu_icon(self, svg_file, out_name=None):

		for density in self.densities:
			out_path = self.out_path_from_out_name(density, svg_file, out_name)
			self.r.svg2png(32*density.scale, 32*density.scale, out_path, svg_file)

			in_path = out_path

			# 333333
			out_path_dark = out_path.replace(".png", "_light.png")
			self.r.convert_color(in_path, out_path_dark, 'white', "rgb(51,51,51)")

			# FFFFFF
			out_path_light = out_path.replace(".png", "_dark.png")
			self.r.convert_color(in_path, out_path_light, 'white', "rgb(255,255,255)")

			cmd = 'rm "%s"' % in_path
			os.system(cmd)

	def svg2png(self, w_1x, h_1x, svg_file, out_name=None):
		for density in self.densities:
			out_path = self.out_path_from_out_name(density, svg_file, out_name)
			w = RUtils.number_from_object(w_1x)*density.scale
			h = RUtils.number_from_object(h_1x)*density.scale
			self.r.svg2png(w, h, out_path, svg_file)

	def svg2pngs(self, w_1x, h_1x, svg_file, out_name=None):
		self.svg2png(w_1x, h_1x, svg_file, out_name)

	def xcf2png(self, w_1x, h_1x, xcf_file, out_name=None):
		for density in self.densities:
			out_path = self.out_path_from_out_name(density, xcf_file, out_name)
			w = RUtils.number_from_object(w_1x)*density.scale
			h = RUtils.number_from_object(h_1x)*density.scale
			self.r.xcf2png(w, h, out_path, xcf_file)

	def xcf2pngs(self, w_1x, h_1x, svg_file, out_name=None):
		self.xcf2png(w_1x, h_1x, svg_file, out_name)

	def svg2pdf(self, svg_file, out_name=None):
		print "svg2pdf is not supported on android"


class ImageSetUnit(object):

	def __init__(self):
		self.name = None
		self.scale = None
		self.folder = None
		self.desired_name = None
		self.path = None


class RiOS(RBase):

	def __init__(self, path_ios_resources, path_inkscape=None, path_convert=None):
		self.r = R(path_inkscape, path_convert)
		self.path_ios_resources = path_ios_resources
		self.paths_ios_assets = None

	def set_ios_assets(self, paths):
		self.paths_ios_assets = paths

	@staticmethod
	def out_path_from_out_name(path_ios_resources, source_file, out_name=None):
		dr = path_ios_resources
		o_name = out_name
		if o_name is None:
			icon_name = os.path.basename(source_file)
			icon_ext = os.path.splitext(source_file)[1]
			o_name = icon_name.replace(icon_ext, '.png')
		out_path = os.path.join(dr, o_name)
		return out_path

	@staticmethod
	def out_path_from_out_name_pdf(path_ios_resources, source_file, out_name=None):
		img_assets = path_ios_resources
		if not os.path.exists(source_file):
			exit("Failed to locate %s" % source_file)
		o_name = out_name
		if o_name is None:
			icon_name = os.path.basename(source_file)
			icon_ext = os.path.splitext(source_file)[1]
			o_name = icon_name.remove(icon_ext)
		out_path = os.path.join(img_assets, o_name + '.imageset')

		if not os.path.exists(out_path):
			os.mkdir(out_path)

		d = dict()
		d["images"] = [{"idiom": "universal", "filename": o_name + ".pdf"}]
		d["info"] = {"version": 1, "author": "xcode"}
		s = json.dumps(d)
		f = open(os.path.join(out_path, "Contents.json"), 'w')
		f.write(s)
		f.close()

		out_path = os.path.join(out_path, o_name + ".pdf")

		out_path = os.path.abspath(out_path)

		return out_path

	def assets_folder_path_from_parameters(self, path_resources, xcassets_path=None):
		if xcassets_path is not None:
			return xcassets_path
		dr = path_resources
		if 'Images.xcassets' not in dr:
			img_assets = os.path.join(dr, 'Images.xcassets')
		else:
			img_assets = dr
		return img_assets

	def image_set_unit_from_path(self,img_path,xcassets):
		img_name = os.path.splitext(os.path.basename(img_path))[0]
		img_ext = os.path.splitext(os.path.basename(img_path))[1]
		img_scale = "1x"
		ats = ["@2x","@3x","@4x","@5x","@6x","@7x","@8x"]
		for at in ats:
			if img_name.endswith(at):
				img_name = img_name[:-3]
				img_scale = at[1:]
				break
		img = ImageSetUnit()
		img.path = img_path
		img.name = img_name
		img.scale = img_scale
		img.folder = os.path.join(xcassets, img_name + '.imageset')
		img.desired_name = img_name + "-" + img_scale + img_ext
		return img

	def image_set_folder_path(self,img_paths,xcassets):
		img = self.image_set_unit_from_path(img_paths[0],xcassets)
		return img.folder

	def image_set_dict(self, imgs):
		images = list()
		for img in imgs:
			images.append({"idiom":"universal","filename" : img.desired_name,"scale" : img.scale})
		d = dict()
		d["images"] = images
		d["info"] = {"version": 1, "author": "xcode"}
		return d

	def create_image_assets_folders_and_move_images_there(self,img_paths,path_resources,xcassets_paths=None):

		if len(img_paths) == 0:
			exit("Cannot proceed, no image paths in img_paths list")

		xcassets_path = None
		if xcassets_paths is not None and len(xcassets_paths) > 0:
			xcassets_path = xcassets_paths[0]

		xcassets_folder_path = self.assets_folder_path_from_parameters(path_resources,xcassets_path)
		if not os.path.exists(xcassets_folder_path):
			os.mkdir(xcassets_folder_path)

		image_folder = self.image_set_folder_path(img_paths,xcassets_folder_path)
		if not os.path.exists(image_folder):
			os.mkdir(image_folder)

		imgs = list()
		for img_path in img_paths:
			imgs.append(self.image_set_unit_from_path(img_path,xcassets_folder_path))

		contents_json_path = os.path.join(image_folder, "Contents.json")
		idic = self.image_set_dict(imgs)

		s = json.dumps(idic)
		f = open(contents_json_path, 'w')
		f.write(s)
		f.close()

		moved_img_paths = list()
		for img in imgs:
			dest_path = os.path.join(image_folder,img.desired_name)
			cmd = 'mv "%s" "%s"' % (img.path,dest_path)
			os.system(cmd)
			moved_img_paths.append(dest_path)

		if xcassets_paths is not None and len(xcassets_paths) > 1:
			dest_name = os.path.basename(image_folder)
			src_path = os.path.join(xcassets_paths[0],dest_name)
			for xcasset_folder in xcassets_paths[1:len(xcassets_paths)]:
				dest_path = os.path.join(xcasset_folder,dest_name)
				if os.path.exists(dest_path):
					shutil.rmtree(dest_path)
				shutil.copytree(src_path,dest_path)

		return moved_img_paths

	def png2pngs(self, w_1x, h_1x, png_file, out_name=None, use_assets=False):
		in_file = png_file
		out_file = RiOS.out_path_from_out_name(self.path_ios_resources, png_file, out_name)
		out = self.r.png2pngs_r(w_1x, h_1x, out_file, in_file)
		if use_assets:
			out = self.create_image_assets_folders_and_move_images_there(out,self.path_ios_resources,self.paths_ios_assets)
		return out

	def svg2pngs(self, w_1x, h_1x, svg_file, out_name=None, use_assets=False):
		in_file = svg_file
		out_file = RiOS.out_path_from_out_name(self.path_ios_resources, svg_file, out_name)
		out = self.r.svg2pngs(w_1x, h_1x, out_file, in_file)
		if use_assets:
			out = self.create_image_assets_folders_and_move_images_there(out,self.path_ios_resources,self.paths_ios_assets)
		return out

	def svg2png(self, w_1x, h_1x, svg_file, out_name=None):
		in_file = svg_file
		out_file = RiOS.out_path_from_out_name(self.path_ios_resources, svg_file, out_name)
		return self.r.svg2png(w_1x, h_1x, out_file, in_file)

	def xcf2pngs(self, w_1x, h_1x, xcf_file, out_name=None, use_assets=False):
		in_file = xcf_file
		out_file = RiOS.out_path_from_out_name(self.path_ios_resources, xcf_file, out_name)
		out = self.r.xcf2pngs(w_1x, h_1x, out_file, in_file)
		if use_assets:
			out = self.create_image_assets_folders_and_move_images_there(out,self.path_ios_resources,self.paths_ios_assets)
		return out

	def xcf2png(self, w_1x, h_1x, xcf_file, out_name=None):
		in_file = xcf_file
		out_file = RiOS.out_path_from_out_name(self.path_ios_resources, xcf_file, out_name)
		self.r.xcf2png(w_1x, h_1x, out_file, in_file)

	def svg2pdf(self, svg_file, out_name=None):
		output_folder = self.path_ios_resources
		if self.paths_ios_assets is not None and len(self.paths_ios_assets) > 0:
			output_folder = self.paths_ios_assets[0]
		in_file = svg_file
		out_file = RiOS.out_path_from_out_name_pdf(output_folder, svg_file, out_name)
		return self.r.svg2pdf(in_file, out_file)

	def icon(self, svg_file):
		#default_xcassets = os.path.join(self.path_ios_resources,"Images.xcassets")
		#self.r.svg2appiconset(svg_file, default_xcassets)
		xcassets = self.paths_ios_assets
		if xcassets is not None:
			for xc in xcassets:
				self.r.svg2appiconset(svg_file, xc)
				#if xc != default_xcassets:
				#self.r.svg2appiconset(svg_file, xc)

	def launch_image(self, svg_bg, svg_centred, w, h):
		width = RUtils.number_from_object(w)
		height = RUtils.number_from_object(h)
		svg_centred_size_1x = [width, height]
		self.r.svg2launch_image(svg_bg, svg_centred, svg_centred_size_1x, self.path_ios_resources, for_iphone=True, for_ipad=True)


class RResources(RBase):

	def __init__(self, path_to_source_files=None, path_to_destination_ios=None, path_to_destination_droid=None, path_inkscape=None, path_convert=None):
		self.path_source_resources = path_to_source_files
		if path_to_destination_ios is not None:
			self.ios_resources = RiOS(path_to_destination_ios, path_inkscape, path_convert)
		if path_to_destination_droid is not None:
			self.droid_resources = RDroid(path_to_destination_droid, path_inkscape, path_convert)

	def svg2pngs(self, w_1x, h_1x, in_name, out_name=None):
		in_file = in_name
		if not os.path.exists(in_file) and self.path_to_source_files is not None:
			in_file = os.path.join(self.path_source_resources, in_name)
		if self.ios_resources is not None:
			self.ios_resources.svg2pngs(w_1x, h_1x, in_file, out_name)
		if self.droid_resources is not None:
			self.droid_resources.svg2png(w_1x, h_1x, in_file, out_name)
