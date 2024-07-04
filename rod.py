import os
import argparse
import xmltodict
import json

from collections import OrderedDict

from rplatform.base import RBase
from rplatform.flutter import RFlutter
from rplatform.ios import RiOS
from rplatform.droid import RDroid
from rplatform.web import RWeb
from r import R


class RodFolderReference(object):

	def __init__(self, line):
		c = line.split(",")
		self.path = c[1]
		self.name = c[2]
		self.ignores = c[3:len(c)]

	def __str__(self):
		return "%s -> %s" % (self.path, self.name)


class RodSettings(object):

	def __init__(self, xcode_projects, img_folder, input_folder, assets_folders, cs_projects, platform, densities, folders, should_update_xcode_proj):
		self.xcode_projects = xcode_projects
		self.img_folder = img_folder
		self.input_folder = input_folder
		self.assets_folders = assets_folders
		self.cs_projects = cs_projects
		self.platform = platform
		self.densities = densities
		self.folders = folders
		self.should_update_xcode_proj = should_update_xcode_proj


class Rod(object):

	def __init__(self, rod_file="Rodfile", path_inkscape=None, path_convert=None):
		self.path_inkscape = path_inkscape
		self.path_convert = path_convert
		self.rodfile = rod_file

	@staticmethod
	def locate_xcodeproject_file(folder_full_path):
		xcodeproj_file_name = None
		files = os.listdir(folder_full_path)
		for f in files:
			if f.endswith(".xcodeproj"):
				xcodeproj_file_name = f
				break
		if xcodeproj_file_name is not None:
			return os.path.join(folder_full_path, xcodeproj_file_name)
		return None

	@staticmethod
	def locate_image_assets_folder(folder_full_path, xcode_project_path):
		res = os.path.join(folder_full_path, "Images.xcassets")
		if os.path.exists(res):
			if os.path.isdir(res):
				return res
		res = os.path.join(folder_full_path, "Resources", "Images.xcassets")
		if os.path.exists(res):
			if os.path.isdir(res):
				return res
		if xcode_project_path is None:
			return None
		name = os.path.basename(xcode_project_path)
		name = name.replace(".xcodeproj", "")
		res = os.path.join(folder_full_path, name, "Images.xcassets")
		if os.path.exists(res):
			if os.path.isdir(res):
				return res
		res = os.path.join(folder_full_path, name, "Resources", "Images.xcassets")
		if os.path.exists(res):
			if os.path.isdir(res):
				return res
		return None

	@staticmethod
	def locate_image_resources_output_folder(folder_path, xcode_project_path):

		if xcode_project_path is None:
			return folder_path

		name = os.path.basename(xcode_project_path)
		name = name.replace(".xcodeproj", "")
		root = os.path.split(xcode_project_path)[0]
		code_folder = os.path.join(root, name)
		resources_folder = os.path.join(code_folder, "Resources")
		images_folder = os.path.join(resources_folder, "Images")
		if os.path.exists(code_folder):
			if os.path.isdir(images_folder):
				return images_folder
		return None

	@staticmethod
	def locate_input_resources_folder(folder_full_path):
		res = os.path.join(folder_full_path, "Resources")
		if os.path.exists(res):
			if os.path.isdir(res):
				return res
		res = os.path.join(folder_full_path, "Res")
		if os.path.exists(res):
			if os.path.isdir(res):
				return res
		return None

	def r_for_platform(self, output_folder, output_assets_folders, platform, densities):
		if platform == "droid" or platform == "android":
			rd = RDroid(output_folder, self.path_inkscape, self.path_convert)
			rd.set_densities(densities)
			return rd
		if platform == "web":
			rd = RWeb(output_folder, self.path_inkscape, self.path_convert)
			return rd
		if platform == "flutter":
			rd = RFlutter(output_folder, self.path_inkscape, self.path_convert)
			rd.set_densities(densities)
			return rd
		ri = RiOS(output_folder, self.path_inkscape, self.path_convert)
		ri.set_ios_assets(output_assets_folders)
		return ri

	def regenerate_resources(self, input_folder, output_folder, output_assets_folders, platform="ios", densities="xhdpi"):
		r = self.r_for_platform(output_folder, output_assets_folders, platform, densities)
		r.run_file(self.rodfile, input_folder)

	def generate_resources(self, rod_lines, input_folder, output_folder, output_assets_folders, platform="ios", densities="xhdpi"):
		r = self.r_for_platform(output_folder, output_assets_folders, platform, densities)
		r.run_lines(rod_lines, input_folder)

	@staticmethod
	def update_xcode_project(xcodeproj, img_folder):

		pbxproj = os.path.join(xcodeproj, "project.pbxproj")

		from mod_pbxproj import XcodeProject
		project = XcodeProject.Load(pbxproj)

		groups = project.get_groups_by_name("Images")
		if groups is None or len(groups) == 0:
			exit("XCode group named Images missing")
		if len(groups) > 1:
			exit("Too many groups named 'Images', so bailing'")

		group = groups[0]

		res_files = os.listdir(img_folder)
		for a_file in res_files:
			if a_file.startswith("."):
				continue
			a_file_path = os.path.join(img_folder, a_file)
			res = project.add_file_if_doesnt_exist(a_file_path, group)
			if len(res) > 0:
				print("Adding new file - %s" % res)

		project.save()

	@staticmethod
	def update_cs_project(cs_proj, img_folder, platform, ref_folders=None):

		cs_folder = os.path.join(os.path.dirname(cs_proj))
		rel_path = os.path.relpath(img_folder, cs_folder)    # '../iOSResources/Resources'

		xcasset_folders = []
		resources_folder = os.path.join(cs_folder, "Resources")
		for a_file in os.listdir(resources_folder):
			if a_file.endswith(".xcassets"):
				if a_file == "Images.xcassets":
					xcasset_folders.insert(0, os.path.join(resources_folder, a_file))
				else:
					xcasset_folders.append(os.path.join(resources_folder, a_file))

		def winshit_to_posix(p):
			return p.replace('\\', '/')

		def posix_to_winshit(p):
			return p.replace('/', '\\')

		def remove_winshit(p):
			return p.replace("%40", "@")

		def add_winshit(p):
			return p.replace("@", "%40")

		def add_missing_ios_resource_files(bundle_resource_group, folders):
			existing_bundle_resources = {}
			for bundle_resource in bundle_resource_group:
				inc = bundle_resource["@Include"]
				inc = winshit_to_posix(inc)
				if inc.startswith(rel_path):
					inc = remove_winshit(inc)
					existing_bundle_resources[inc] = bundle_resource

			missing_resources = []
			files = os.listdir(img_folder)
			for name in files:

				if name == ".DS_Store":
					continue
				if name.endswith(".lproj"):
					continue
				if name.endswith(".xcassets"):
					continue

				file_path = os.path.join(rel_path, name)

				if file_path not in existing_bundle_resources:
					if not os.path.isdir(file_path):
						missing_resources.append(name)
			missing_resource_dicts = []
			for mrname in missing_resources:
				mrname = add_winshit(mrname)
				mrpath = posix_to_winshit(os.path.join(rel_path, mrname))
				mrlink = posix_to_winshit(os.path.join("Resources", mrname))
				od = OrderedDict()
				od["@Include"] = mrpath
				od["Link"] = mrlink
				od["#text"] = ""
				missing_resource_dicts.append(od)

			for d in missing_resource_dicts:
				bundle_resource_group.append(d)

		def handle_resource_folder_references(bundle_resource_group, folders, resource_folder):
			bundle_resources_for_removal = {}
			for bundle_resource in bundle_resource_group:
				inc = bundle_resource["@Include"]
				inc = winshit_to_posix(inc)
				for folder in folders:
					folder_rel_path = os.path.relpath(os.path.abspath(folder.path), cs_folder)
					if inc.startswith(folder_rel_path):
						bundle_resources_for_removal[inc] = bundle_resource

			for k in bundle_resources_for_removal:
				bur = bundle_resources_for_removal[k]
				bundle_resource_group.remove(bur)

			for folder in folders:
				for dirName, _, files in os.walk(folder.path, followlinks=True):
					for f in files:
						if not f.startswith("."):
							file_rel_path = os.path.join(dirName, f)
							file_link_path = file_rel_path[len(folder.path):len(file_rel_path)]
							if not file_link_path in folder.ignores:
								file_link_path = os.path.join(resource_folder, folder.name, file_link_path)
								file_rel_path = os.path.relpath(os.path.abspath(file_rel_path), cs_folder)

								mrpath = posix_to_winshit(file_rel_path)
								mrlink = posix_to_winshit(file_link_path)
								od = OrderedDict()
								od["@Include"] = mrpath
								od["Link"] = mrlink
								od["#text"] = ""
								bundle_resource_group.append(od)

		def handle_ios_resource_folder_references(bundle_resource_group, folders, resource_folder):
			if bundle_resource_group is None:
				print("Warning: Failed to locate iOS %s group for %s" % (resource_folder, os.path.basename(cs_proj)))
				return
			handle_resource_folder_references(bundle_resource_group, folders, resource_folder)

		def handle_android_resource_folder_references(bundle_resource_group, folders, resource_folder):
			if bundle_resource_group is None:
				print("Warning: Failed to locate Android %s group for %s" % (resource_folder, os.path.basename(cs_proj)))
				return
			handle_resource_folder_references(bundle_resource_group, folders, resource_folder)

		def add_xcasset_folder_assets(asset_folders):
			things = []
			for catalogue in asset_folders:
				catalogue_name = os.path.basename(catalogue)
				catalogue_items = os.listdir(catalogue)
				for imageset_name in catalogue_items:
					if imageset_name.endswith(".imageset") or imageset_name.endswith(".appiconset") or imageset_name.endswith(".launchimage"):
						imageset_folder = os.listdir(os.path.join(catalogue, imageset_name))
						for imageset_item in imageset_folder:
							if imageset_item == ".DS_Store":
								continue
							include_path = os.path.join("Resources", catalogue_name, imageset_name, imageset_item)
							include_path = posix_to_winshit(include_path)
							#<ImageAsset Include="Resources\Flags.xcassets\flag-ecocell-WS.imageset\Contents.json"></ImageAsset>
							od = OrderedDict()
							od["@Include"] = include_path
							things.append(od)
			return things

		f = open(cs_proj)
		s = f.read()
		dom = xmltodict.parse(s, strip_whitespace=True)
		f.close()

		item_groups = dom['Project']['ItemGroup']

		if platform == "ios":

			folder_group = None
			bundle_resource_group = None
			image_asset_group = None

			for group in item_groups:
				if group is None:
					continue
				if "Folder" in group:
					folder_group = group["Folder"]
				if "BundleResource" in group:
					bundle_resource_group = group["BundleResource"]
				if "ImageAsset" in group:
					image_asset_group = group["ImageAsset"]

			assets = add_xcasset_folder_assets(xcasset_folders)

			if image_asset_group is None:
				od = OrderedDict()
				od["ImageAsset"] = assets
				item_groups.insert(len(item_groups) - 1, od)
			else:
				del image_asset_group[:]
				image_asset_group.extend(assets)

			# Check for folder_group folder called Resources
			if folder_group is None:
				exit("Folder group not found - You need a Folder in the project tree called Resources for this to work")
			else:
				fres = None
				for folder in folder_group:
					fg = folder["@Include"]
					if fg == "Resources\\":
						fres = fg
						break
				if fres is None:
					exit("'Resources' folder missing from project")

			# Check for bundle resources group
			if bundle_resource_group is None:
				exit("Bundle resources group not found - You need at least one item in the Resources folder for the script to identify which is the correct item group")

			add_missing_ios_resource_files(bundle_resource_group, ref_folders)
			if ref_folders is not None and len(ref_folders) > 0:
				handle_ios_resource_folder_references(bundle_resource_group, ref_folders, "Resources")

		elif platform == "android" or platform == "droid":

			android_resources_group = None
			android_assets_group = None
			for node in item_groups:
				if "AndroidResource" in node:
					android_resources_group = node["AndroidResource"]
				if "AndroidAsset" in node:
					android_assets_group = node["AndroidAsset"]

			if android_resources_group is None:
				exit("Android resources group not found - You need at least one item in the Resources folder for the script to identify which is the correct item group")

			folders = os.listdir(img_folder)
			for folder in folders:

				if folder == ".DS_Store":
					continue

				existing_bundle_resources = {}
				for bundle_resource in android_resources_group:
					inc = bundle_resource["@Include"]
					inc = winshit_to_posix(inc)
					if folder + "/" in inc:
						if inc.startswith(rel_path):
							inc = remove_winshit(inc)
							existing_bundle_resources[inc] = bundle_resource

				missing_resources = []
				files = os.listdir(os.path.join(img_folder, folder))
				for name in files:
					if name == ".DS_Store":
						continue
					file_path = os.path.join(rel_path, folder, name)
					if file_path not in existing_bundle_resources:
						if not os.path.isdir(file_path):
							missing_resources.append(name)

				missing_resource_dicts = []
				for mrname in missing_resources:
					mrname = add_winshit(mrname)
					mrpath = posix_to_winshit(os.path.join(rel_path, folder, mrname))
					mrlink = posix_to_winshit(os.path.join('Resources', folder, mrname))
					od = OrderedDict()
					od["@Include"] = mrpath
					od["Link"] = mrlink
					od["#text"] = ""
					missing_resource_dicts.append(od)

				for d in missing_resource_dicts:
					android_resources_group.append(d)
			if ref_folders is not None and len(ref_folders) > 0:
				handle_android_resource_folder_references(android_assets_group, ref_folders, 'Assets')

		xml = xmltodict.unparse(dom, pretty=True)
		with open(cs_proj, "w") as g:
			g.write(xml)

	@staticmethod
	def read_rod_lines(rod_file) -> list[str]:
		folder_path = os.curdir
		if folder_path == ".":
			folder_path = os.path.abspath(folder_path)
		rod_file = os.path.join(folder_path, rod_file)

		f = open(rod_file, 'r')
		lines = f.readlines()
		f.close()
		return lines

	@staticmethod
	def read_rod_overrides(rod_file) -> dict:
		d = {}
		lines = Rod.read_rod_lines(rod_file)
		for line in lines:
			if line.startswith('###'):
				l = line[3:len(line)]
				l = l.strip()
				parts = l.split("=")
				if len(parts) >= 2:
					k = parts[0].strip()
					v = parts[1].strip()
					d[k] = v
		return d

	@staticmethod
	def read_rod_folder_references(rod_file) -> list[RodFolderReference]:
		folders = []
		lines = Rod.read_rod_lines(rod_file)
		for line in lines:
			if line.startswith("resources_folder"):
				folders.append(RodFolderReference(line))
			if line.startswith("assets_folder"):
				folders.append(RodFolderReference(line))
		return folders

	@staticmethod
	def override_rod_setting_if_exists(d, current: str, key: str) -> str:
		if key in d:
			val = d[key]
			return val
		return current

	@staticmethod
	def override_rod_path_setting_if_exists(d, current, key: str):
		if key in d:
			val = d[key]
			if val.startswith('.'):
				val = os.path.abspath(val)
			return val
		return current

	@staticmethod
	def override_rod_bool_setting_if_exists(d, current: bool, key: str) -> bool:
		if key in d:
			return True
		return current

	@staticmethod
	def read_projects(d, key):
		cs = []
		if key in d:
			vals = d[key].split(",")
			for val in vals:
				if val.startswith("."):
					val = os.path.abspath(val)
				cs.append(val)
		return cs

	def init(self):
		folder_path = os.curdir
		if folder_path == ".":
			folder_path = os.path.abspath(folder_path)

		rod_file = os.path.join(folder_path, self.rodfile)
		if os.path.exists(rod_file):
			if os.path.isfile(rod_file):
				print("[!] Existing Rodfile found in directory")
			else:
				exit("Folder with the name Rodfile detected - This should be a file")
		else:

			c = RBase.create_run_file_header()
			f = open(rod_file, "w")
			f.write(c)
			f.close()

			print("[*] Rodfile created successfully")

	def update(self):
		s = self.check(should_print_map=False)
		if s.input_folder is not None:
			self.regenerate_resources(s.input_folder, s.img_folder, s.assets_folders, s.platform, s.densities)
		self.update_projects()

	def update_projects(self):
		s = self.check(should_print_map=False)
		for csproj in s.cs_projects:
			Rod.update_cs_project(csproj, s.img_folder, s.platform, s.folders)
		if s.should_update_xcode_proj:
			for xcodeproj in s.xcode_projects:
				Rod.update_xcode_project(xcodeproj, s.img_folder)

	def check(self, should_print_map: bool) -> RodSettings:
		folder_path = os.curdir
		if folder_path == '.':
			folder_path = os.path.abspath(folder_path)
		xcodeproj = Rod.locate_xcodeproject_file(folder_path)
		output_folder = Rod.locate_image_resources_output_folder(folder_path, xcodeproj)
		input_folder = Rod.locate_input_resources_folder(folder_path)
		assets_folder = Rod.locate_image_assets_folder(folder_path, xcodeproj)

		r = R(self.path_inkscape, self.path_convert)
		r.check_for_inkscape()
		r.check_for_convert()

		folders = Rod.read_rod_folder_references(self.rodfile)

		# Rod overrides
		d = Rod.read_rod_overrides(self.rodfile)
		output_folder = Rod.override_rod_path_setting_if_exists(d, output_folder, "OUTPUT")
		input_folder = Rod.override_rod_path_setting_if_exists(d, input_folder, "INPUT")
		should_update_xcode_proj = Rod.override_rod_bool_setting_if_exists(d, False, "XCODE_PROJ_UPDATE")
		platform = Rod.override_rod_setting_if_exists(d, "ios", "PLATFORM").lower()
		densities = Rod.override_rod_setting_if_exists(d, "hdpi,mdpi,xhdpi,xxhdpi,xxxhdpi", "DENSITIES").lower()
		if platform == "flutter":
			densities = Rod.override_rod_setting_if_exists(d, "1.0,2.0,3.0", "DENSITIES").lower()

		assets_folders = []
		xc_assets = Rod.read_projects(d, "XCASSETS")
		if len(xc_assets) > 0:
			assets_folders.extend(xc_assets)
			assets_folder = xc_assets[0]
			if output_folder is None:
				output_folder = os.path.join(assets_folder, '..')
		elif assets_folder is not None:
			assets_folders.append(assets_folder)

		if platform == "ios" and assets_folder is None:
			exit("Failed to locate assets folder")
		if platform == "ios" and output_folder is None:
			exit("Failed to locate xcode resources/images folder")

		xc_projects = Rod.read_projects(d, "XCPROJ")
		cs_projects = Rod.read_projects(d, "CSPROJ")

		if xcodeproj is not None:
			if xcodeproj not in xc_projects:
				xc_projects.append(xcodeproj)

		if should_print_map:
			print("> Image Output folder maps to %s" % output_folder)
			if platform == "ios":
				print("> Image Assets Output folders map to: ")
				for assf in assets_folders:
					print("  %s" % assf)
			print("> Res Input folder maps to %s" % input_folder)
			print("> Platform system to use %s" % platform)
			if platform == "android" or platform == "droid" or platform == "flutter":
				print("> Densities to use %s" % densities)
			print("")

			print("> inkscape maps to: %s" % r.path_inkscape)
			print("> convert maps to: %s" % r.path_convert)

			if len(xc_projects) > 0:
				print("> xcodeproj maps to: ")
				for xproj in xc_projects:
					print("  %s" % xproj)
				if should_update_xcode_proj:
					print("> Should update xcode projects: Yes")
				else:
					print("> Should update xcode projects: No")
			else:
				if platform == "ios" and len(cs_projects) == 0:
					print("Failed to locate xcode project - i.e. Missing .xcodeproj file in folder %s\n(So Xcodeproject will not be updated, you have to manually add/remove image resources)" %
							folder_path)
			print("")

			if len(cs_projects) > 0:
				print("> csproj maps to: ")
				for cs_proj in cs_projects:
					print("  %s" % cs_proj)

			if len(folders) > 0:
				print("> folder references: ")
				for folder in folders:
					print("  %s" % folder)

		return RodSettings(xc_projects, output_folder, input_folder, assets_folders, cs_projects, platform, densities, folders, should_update_xcode_proj)


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--init", help="Generate a Rodfile for the current directory.", action="store_true", default=False)
	parser.add_argument("-u", "--update", help="Regenerate resources and update the Xcode project.", action="store_true", default=False)
	parser.add_argument("-c", "--check", help="Check to see if Rod can figure out where the resource inputs and the target outputs are.", action="store_true", default=False)
	parser.add_argument("-r", "--repopulate", help="Repopulate the XCode Project's image folder reference or Monodevelop's image definitions", action="store_true", default=False)
	parser.add_argument("-f", "--rodfile", help="The name of the rodfile", default=None)
	parser.add_argument("-v", "--version", help="Version of Rod", action="store_true", default=False)
	args = parser.parse_args()

	rodfiles = []
	if args.rodfile is None:
		for n in os.listdir(os.curdir):
			if n.startswith("Rodfile") and not n.endswith(".locked"):
				rodfiles.append(n)
		if len(rodfiles) == 0:
			rodfiles.append("Rodfile")
	else:
		rodfiles.append(args.rodfile)

	for rodfile in rodfiles:

		rod = Rod(rodfile)

		if args.init:
			rod.init()
		elif args.update:
			rod.update()
		elif args.check:
			if len(rodfiles) > 1:
				print("Rod file : %s" % rodfile)
			rod.check(should_print_map=True)
			print("")
		elif args.repopulate:
			rod.update_projects()
		elif args.version:
			f = open("setup.json")
			s = f.read()
			d = json.loads(s)
			version = d["version"]
			f.close()
			print(f"Rod {version}")
		else:
			parser.print_help()
			break
