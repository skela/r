import os

from r import R, RUtils
from rplatform.base import RBase


class RWeb(RBase):

	def __init__(self, path_destination_folder, path_inkscape=None, path_convert=None):
		self.r = R(path_inkscape, path_convert)
		self.path_destination_folder = path_destination_folder
		self.densities = [RFlutterDensity(1)]

	def set_densities(self, densities):
		self.densities = []
		dens = densities
		if not isinstance(densities, (list, tuple)):
			dens = densities.split(",")
		for density in dens:
			scale = float(density)
			self.densities.append(RFlutterDensity(scale))

	def out_path_from_out_name(self, density, svg_file, out_name=None):

		if not os.path.exists(self.path_destination_folder):
			os.mkdir(self.path_destination_folder)

		if density.folder is not None:
			dr = os.path.join(self.path_destination_folder, density.folder)
		else:
			dr = self.path_destination_folder

		if not os.path.exists(dr):
			os.mkdir(dr)

		o_name = out_name
		if o_name is None:
			icon_name = os.path.basename(svg_file)
			o_name = icon_name.replace('.svg', '.png')
		out_path = os.path.join(dr, o_name)
		return out_path

	def svg2png(self, w_1x, h_1x, svg_file, out_name=None):
		for density in self.densities:
			out_path = self.out_path_from_out_name(density, svg_file, out_name)
			w = RUtils.number_from_object(w_1x) * density.scale
			h = RUtils.number_from_object(h_1x) * density.scale
			self.r.svg2png(w, h, out_path, svg_file)

	def svg2pngs(self, w_1x, h_1x, svg_file, out_name=None):
		self.svg2png(w_1x, h_1x, svg_file, out_name)

	def png2png(self, w_1x, h_1x, svg_file, out_name=None):
		for density in self.densities:
			out_path = self.out_path_from_out_name(density, svg_file, out_name)
			w = RUtils.number_from_object(w_1x) * density.scale
			h = RUtils.number_from_object(h_1x) * density.scale
			self.r.png2png(w, h, out_path, svg_file)

	def png2pngs(self, w_1x, h_1x, svg_file, out_name=None):
		self.png2png(w_1x, h_1x, svg_file, out_name)

	def webp2webp(self, w_1x, h_1x, svg_file, out_name=None):
		for density in self.densities:
			out_path = self.out_path_from_out_name(density, svg_file, out_name)
			w = RUtils.number_from_object(w_1x) * density.scale
			h = RUtils.number_from_object(h_1x) * density.scale
			self.r.webp2webp(w, h, out_path, svg_file)

	def webp2webps(self, w_1x, h_1x, svg_file, out_name=None):
		self.webp2webp(w_1x, h_1x, svg_file, out_name)

	def xcf2png(self, w_1x, h_1x, xcf_file, out_name=None):
		for density in self.densities:
			out_path = self.out_path_from_out_name(density, xcf_file, out_name)
			w = RUtils.number_from_object(w_1x) * density.scale
			h = RUtils.number_from_object(h_1x) * density.scale
			self.r.xcf2png(w, h, out_path, xcf_file)

	def xcf2pngs(self, w_1x, h_1x, svg_file, out_name=None):
		self.xcf2png(w_1x, h_1x, svg_file, out_name)

	def svg2pdf(self, svg_file, out_name=None):
		print("svg2pdf is not supported on web")


class RFlutterDensity(object):

	def __init__(self, scale):
		if scale == 1:
			self.folder = None
			self.scale = scale
		else:
			self.folder = "%.1fx" % scale
			self.scale = scale
