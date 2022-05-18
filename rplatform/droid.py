import os

from r import R, RUtils
from rplatform.base import RBase


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
		if not os.path.exists(dr):
			os.mkdir(dr)
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

	def png2png(self, w_1x, h_1x, svg_file, out_name=None):
		for density in self.densities:
			out_path = self.out_path_from_out_name(density, svg_file, out_name)
			w = RUtils.number_from_object(w_1x)*density.scale
			h = RUtils.number_from_object(h_1x)*density.scale
			self.r.png2png(w, h, out_path, svg_file)

	def png2pngs(self, w_1x, h_1x, svg_file, out_name=None):
		self.png2png(w_1x, h_1x, svg_file, out_name)

	def xcf2png(self, w_1x, h_1x, xcf_file, out_name=None):
		for density in self.densities:
			out_path = self.out_path_from_out_name(density, xcf_file, out_name)
			w = RUtils.number_from_object(w_1x)*density.scale
			h = RUtils.number_from_object(h_1x)*density.scale
			self.r.xcf2png(w, h, out_path, xcf_file)

	def xcf2pngs(self, w_1x, h_1x, svg_file, out_name=None):
		self.xcf2png(w_1x, h_1x, svg_file, out_name)

	def svg2pdf(self, svg_file, out_name=None):
		print("svg2pdf is not supported on android")

	def icon(self,svg_file,device=None):
		name = os.path.basename(svg_file)
		altname = name.replace(".svg","_round.svg")
		folder = os.path.dirname(svg_file)
		svg_round_file = os.path.join(folder,altname)
		self.r.svg2android_icons(svg_file,self.path_droid_resources)
		if os.path.exists(svg_round_file):
			self.r.svg2android_icons(svg_round_file,self.path_droid_resources,round=True)


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