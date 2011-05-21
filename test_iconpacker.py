import os
from iconpacker import IconList

test_icon = "/media/hda7/Graphics/png/Classic_Truck/128.png"
icon_theme = IconList()

def initialization():
	treestore = icon_theme.setup_treeview('data/legacy-icon-mapping.xml')
	if treestore != None:
		for i in icon_theme.icon_list:
			icon_theme.set_item(i, test_icon)
		return True
	return False

def test_read_theme_file(fname):
	treestore = icon_theme.setup_treeview('data/legacy-icon-mapping.xml')
	if treestore != None:
		return icon_theme.read_theme_file(fname)
	return False

"""
def path_generation():
	test_path = os.tempnam()
	os.mkdir(test_path)

	for i in range(0,101):
		os.system("mkdir %s/test_dir_%s>/dev/null" % (test_path, i))

	if get_unique_path (test_path, "test_dir"):
		return False
	else:
		os.rmdir(test_path+"/test_dir_50")
		fpath, name = icon_theme.get_unique_path (test_path, "test_dir")

		if name=="test_dir_50":
			os.system("rm -rf %s" % test_path)
			return True
		else:
			return False
"""

def build_icon_paths ():
	icon_theme.build_paths()
	return True

def test_icon_copying():
	if icon_theme.copy_icon_files():
		d = os.stat(test_icon)
		expected_size = d[6] * len(icon_theme.icon_list) - (4096 * len(icon_theme.categories_list))
		print expected_size
		os.system ('du -c -b ' + icon_theme.tmp_ico_path)
		return True
	return False

def test_resizing():
	if icon_theme.resize_icons():
		return True
	else:
		return False

def test_make_theme():
	if icon_theme.make_icon_theme('TestTheme'):
		return True
	else:
		return False

def test_write_icon_theme():
	icon_theme.write_theme_file()

def start_testing():
	print "Testing treeview initialization ..."
	if initialization():
		print "treeview initialization [PASSED]"
	else:
		print "treeview initialization [FAILED]"
		return False 
	"""
	print "Testing Unique path generator ..."
	if path_generation():
		print "Unique Path generation [PASSED]"		
	else:
		print "Unique Path generation [FAILED]"
		return False 
	"""

	print "Testing directory generation ..."
	if build_icon_paths():
		print "building icon paths [PASSED]"
	else:
		print "building icon paths [FAILED]"
		return False

	print "Testing Icon copying ..."
	if test_icon_copying():
		print "Icon copying [PASSED]"
	else:
		print "Icon copying [FAILED]"
		return False

	print "Testing icon resizing ..."
	if test_resizing():
		print "Resizing [PASSED]"
	else:
		print "Resizing [FAILED]"
		return False

	print "Testing Theme creation ..."
	if test_make_theme():
		print "Theme creation [PASSES]"
	else:
		print "Theme Creation [FAILED]"
		return False

	print "Testing index file creation ..."
	if test_write_icon_theme():
		print "Index file creation [PASSED]"
	else:
		print "Index file creation [FAILED]"
		return False

	
	#os.system("rm -rf %s/*" % icon_theme.build_path)

def test_writing_themes():
	initialization()
	icon_theme.theme_name = "TestTheme"
	if icon_theme.write_icon_theme():
		print "Theme Written"
	else:
		print "Failed"

if __name__=="__main__":
	start_testing()
