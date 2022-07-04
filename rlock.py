import os
import json
import hashlib
from pathlib import Path


class RLock(object):

	def __init__(self):
		self.lock_file = os.path.join(os.getcwd(),"Rodfile.locked")
	
	def _load_lock_file(self) -> dict:
		if not os.path.exists(self.lock_file):
			return None
		f = open(self.lock_file)
		s = f.read()
		f.close()
		d = json.loads(s)
		return d

	def _save_lock_file(self, d: dict):
		f = open(self.lock_file, "w")
		js = json.dumps(d,sort_keys = True, indent=2)
		f.write(js)
		f.close()

	def _key(self, method:str, width: str, height: str, input: str, output: str) -> str:
		cwd = Path(os.getcwd())
		rel_input = Path(input).relative_to(cwd)
		rel_output = Path(output).relative_to(cwd)        
		key = f"{method}|{width}x{height}|{rel_input}->{rel_output}"
		return key

	def _create_hash(self, file_path):
		sha256_hash = hashlib.sha256()
		with open(file_path,"rb") as f:
			for byte_block in iter(lambda: f.read(4096),b""):
				sha256_hash.update(byte_block)
			return sha256_hash.hexdigest()
		return None

	def check_for_skippage(self, method:str, width: str, height: str, input: str, output: str) -> bool:
		if not os.path.exists(input) or not os.path.exists(output):
			return False
		
		key = self._key(method,width,height,input,output)

		d = self._load_lock_file()
		if d is None:
			return False
		
		if key not in d:
			return False

		input_hash = self._create_hash(input)
		output_hash = self._create_hash(output)        
		old_input_hash = d[key]["input"]
		old_output_hash = d[key]["output"]
		if old_input_hash != input_hash or old_output_hash != output_hash:
			return False

		return True

	def update(self, method:str, width: str, height: str, input: str, output: str):
		key = self._key(method,width,height,input,output)
		input_hash = self._create_hash(input)
		output_hash = self._create_hash(output)

		d = self._load_lock_file()
		if d is None:
			d = {}
		d[key] = {"input": input_hash, "output": output_hash}
		self._save_lock_file(d)
