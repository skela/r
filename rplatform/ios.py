import json
import os
import shutil

from r import R, RUtils
from rplatform.base import RBase

class ImageSetUnit(object):

	def __init__(self,name:str,scale:str,folder:str,desired_name:str,path:str):
		self.name = name
		self.scale = scale
		self.folder = folder
		self.desired_name = desired_name
		self.path = path

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

	def image_set_unit_from_path(self,img_path,xcassets) -> ImageSetUnit:
		img_name = os.path.splitext(os.path.basename(img_path))[0]
		img_ext = os.path.splitext(os.path.basename(img_path))[1]
		img_scale = "1x"
		ats = ["@2x","@3x","@4x","@5x","@6x","@7x","@8x"]
		for at in ats:
			if img_name.endswith(at):
				img_name = img_name[:-3]
				img_scale = at[1:]
				break
		return ImageSetUnit(
			name=img_name,
			scale=img_scale,
			folder=os.path.join(xcassets, img_name + '.imageset'),
			desired_name=img_name + "-" + img_scale + img_ext,
			path=img_path
		)

	def image_set_folder_path(self,img_paths,xcassets) -> str:
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

	def png2pngs(self, w_1x, h_1x, png_file, out_name=None, use_assets=True):
		in_file = png_file
		out_file = RiOS.out_path_from_out_name(self.path_ios_resources, png_file, out_name)
		out = self.r.png2pngs_r(w_1x, h_1x, out_file, in_file)
		if use_assets:
			out = self.create_image_assets_folders_and_move_images_there(out,self.path_ios_resources,self.paths_ios_assets)
		return out

	def svg2pngs(self, w_1x, h_1x, svg_file, out_name=None, use_assets=True):
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

	def xcf2pngs(self, w_1x, h_1x, xcf_file, out_name=None, use_assets=True):
		in_file = xcf_file
		out_file = RiOS.out_path_from_out_name(self.path_ios_resources, xcf_file, out_name)
		out = self.r.xcf2pngs(w_1x, h_1x, out_file, in_file)
		if use_assets:
			out = self.create_image_assets_folders_and_move_images_there(out,self.path_ios_resources,self.paths_ios_assets)
		return out

	def xcf2png(self, w_1x, h_1x, xcf_file, out_name=None):
		in_file = xcf_file
		out_file = RiOS.out_path_from_out_name(self.path_ios_resources, xcf_file, out_name)
		return self.r.xcf2png(w_1x, h_1x, out_file, in_file)

	def svg2pdf(self, svg_file, out_name=None):
		output_folder = self.path_ios_resources
		if self.paths_ios_assets is not None and len(self.paths_ios_assets) > 0:
			output_folder = self.paths_ios_assets[0]
		in_file = svg_file
		out_file = RiOS.out_path_from_out_name_pdf(output_folder, svg_file, out_name)
		return self.r.svg2pdf(in_file, out_file)

	def icon(self,svg_file,device=None):
		#default_xcassets = os.path.join(self.path_ios_resources,"Images.xcassets")
		#self.r.svg2appiconset(svg_file, default_xcassets)
		xcassets = self.paths_ios_assets
		if xcassets is not None:
			for xc in xcassets:
				self.r.svg2appiconset(svg_file, os.path.abspath(xc), device=device)
				#if xc != default_xcassets:
				#self.r.svg2appiconset(svg_file, xc)

	def launch_image(self, svg_bg, svg_centred, w, h):
		width = RUtils.number_from_object(w)
		height = RUtils.number_from_object(h)
		svg_centred_size_1x = [width, height]
		return self.r.svg2launch_image(svg_bg, svg_centred, svg_centred_size_1x, self.path_ios_resources, for_iphone=True, for_ipad=True)


