import os

from platform.base import RBase
from platform.droid import RDroid
from platform.ios import RiOS


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