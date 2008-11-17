import sys
import os

class Constants:
	def __init__(self, *args):
		if len(args) > 0:
			self.__configs['user_dir'] = args[0]
		else:
			self.__configs['user_dir'] = os.path.expanduser('~')

		self.__configs = {}
		self.__configs['app_config'] = '.iconpacker'
		self.__configs['theme_dir'] = '.iconpacker/themes'
		self.__configs['user_icon_path'] = '.icons'
		self.__configs['tmp_path'] = '/tmp'
		self.__configs['icon_build_path']=self._temp_path()

	def _temp_path(self):
		tpath = self.__configs('tmp_path')
		fpath = tpath + "/ipck"
		def dir_ok (): 
			if os.access(fpath, os.F_OK):
				return False		
			return True

		j = 0
		while not dir_ok():
			fpath =  self.tmp_dir+'/ipck-testing_'+j

		self.tmp_ico_path = fpath

	def config(self, key):
		return self.__configs[key]

class PathManager:
	def __init__(self, constants):
		self.constants = constants
		
	def root_path_exists (self):
		return os.path.exists(self.root_dir)

	def theme_path_exists (self):
		return os.path.exists(self.theme_dir)
		
	def make_root_path (self):
		os.system('mkdir ' + self.root_dir)

	def make_theme_path (self):
		os.system('mkdir ' + self.theme_dir)

	def validate_paths (self):
		if not self.root_path_exists ():
			self.make_root_path()

		if not self.theme_path_exists ():
			self.make_theme_path()

		return (self.root_path_exists() and self.theme_path_exists())

	def build_paths (self, dir_list):
		print (self.ico_path)
		for dir in dir_list:
			if not os.mkdir(self.ico_path + "/" + dir):
				return False
		return True


if __name__ == "__main__":
	status = True
	test_dir =  'test_dir'

	def test_status ():
		if status == True:
			return "GOOD"
		return "BAD"

	constants = Constants(test_dir)
	path_manager = PathManager(constants)

	if not os.path.exists(test_dir):
		print ("Creating test directory!")
		os.system('mkdir ' + test_dir)

	if not path_manager.validate_paths():
		status = False
	
	print ("Path creation test is : %s" % test_status())

	path_manager.build_paths(['dir1', 'dir2', 'dir3', 'dir4'])
	os.system('ls -Ra %s' % test_dir)

	os.system('rm -rf ' + test_dir)
	os.system('rmdir /tmp/ipck-*')
