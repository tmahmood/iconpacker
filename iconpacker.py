#!/usr/bin/env python
#
#this python script helps creation of icon themes

import sys
import os
from string import Template

try:
 	import pygtk
  	pygtk.require("2.0")
	import gtk
  	import gtk.glade
	from xml.dom import minidom
except:
	sys.exit(1)
""" 
:::::::::::::::INDEX::::::::::::::::
Class||Methods
IconList 
		__init__
		build_icon_theme 
		clear_list
		load_themes
		read_theme_file
		setup_treeview 
		write_icon_theme
IconPacker
		__init__
		btn_build_icon_theme
		clear_list
		collapse_treeview
		dropped_something
		expand_treeview
		load_from_file
		row_acivated
		save_icon_list
		set_icon_path
		text_changed
		theme_selected
main	
::::::::::::::::::::::::::::::::::::
"""
tpl_theme_file = """
[Icon Theme]
Name=%s
Comment=Build with Icon packer
Inherits=gnome
Directories=%s
%s
"""
tpl_dirs_desc = """
[%(size)sx%(size)s/%(category)s]
Size=%(size)s
Context=%(category)s
Type=%(type)s
"""
tpl_html = """
<html>
	<head>
		<title>
			Log File
		</title>
		<style type="text/css">
			.error li
			{
				border: 1px solid Red;				
			}

			.warning li
			{
				border: 1px solid #ddd;	
			}

			.notice li
			{
				border: 1px solid Green;
			}
		</style>
	</head>
	<body>
		<ul>
			%s
		</ul>
	</body>
"""

class IconList:
	""" This class handles icon list, builds the theme, 
		does all the logical stuffs
	"""
	def __init__(self):	
		"""Constructor"""
		dir=os.path.expanduser('~')

		#Setup application directories
		self.categories_list= []		# List of categories available
		self.icon_list		= {}		# List of Icons available/set
		self.tmp_ico_path	= ''		# Where we building the icon theme
		self.icon_count 	= 0			# no of icons set
		self.sizes			= "128x128 64x64 48x48 32x32 24x24 16x16"
		self.theme_name 	= ""
		self.theme_dir		= dir+'/.iconpacker/themes'
		self.tmp_dir		= '/tmp'	
		self.root_dir		= dir+'/.iconpacker'
		self.icon_path 		= dir+"/.icons"
		self.app_dir		= os.getcwd()
		self.reports		= ''

		self.logs = Logger(self.root_dir+"/"+"logs")

		if not self.check_paths():
			#May be the path is not writable or
			#Low harddisk space, either way we cannot 
			#Continue. So we exit now.
			self.logs.log("Failed to create user directories!", 'error')
			print "Error occurred."
			sys.exit(1)

	def close_log(self):
		self.logs.save_log()

	def check_paths (self):
		"""
		This function checks all the required path, if they exists or not
		if they don't then make them
		"""
		pe=os.path.exists(self.root_dir)
		if pe==False:			
			self.logs.log("Warning: Setting Directory do not exists!", "warning")
			self.logs.log("Action: Creating directory [%s]" % self.root_dir, 'notice')
			os.system('mkdir '+self.root_dir)
			if not os.path.exists(self.root_dir):
				self.logs.log("Failed to create directory", 'error')
				return False

		pe=os.path.exists(self.theme_dir)
		if pe==False:			
			self.logs.log("Warning: Theme Directory do not exists!", 'warning')
			self.logs.log("Action: Creating directory [%s]" % self.theme_dir, 'notice')
			os.system('mkdir '+self.theme_dir)
			if not os.path.exists(self.theme_dir):
				self.logs.log("Failed", 'error')
				return False

		return True

	def create_temp_path(self):
		fpath = os.tempnam('','ipck-')
		os.mkdir(fpath)
		if not os.access(fpath, os.F_OK):
			self.logs.log('Failed to create temporary path, will not continue', 'error')
			return False		
		os.chdir(fpath)
		self.tmp_ico_path = fpath
		return True

	def build_paths (self):
		# create the category directories here
		dirs =  (' ').join(self.categories_list)
		res = os.system('mkdir -p %s' % dirs)
		if res != 0:
			self.logs.log('Failed to create required directories, will not continue', 'error')
			return False

		return True

	def copy_icon_files(self):
		for key in self.icon_list:
			ico_path = self.icon_list[key]
			# for a parent type we would get [category folder, icon name]
			# for a child we would get [category folder, parent, icon name]
			ico_type = key.split('/')
			cmd =''
			if len(ico_type)==3:
				# is this one is set?
				if ico_path != '':
					cmd = "cp \"%s\" %s/%s.png" % (ico_path, ico_type[0], ico_type[2])
				else:
					if self.icon_list[ico_type[0]+'/'+ico_type[1]] != '':
						ico_name = ico_type[0]+"/"+ico_type[2]+".png"
						cmd = "ln -s %s.png %s" % (ico_type[1], ico_name)
			else:
				if ico_path !='':
					cmd = "cp \"%s\" %s/%s.png"% (ico_path, ico_type[0], ico_type[1])
			
			if cmd != '':
				res = os.system(cmd)
				self.logs.log("[Failed]: "+cmd, 'warning')
		return True 

	def build_icon_theme(self, theme_name):
		""" Takes a file name and creates an Icon theme
			of that name

			returns status
		"""
		self.theme_name = theme_name

		if self.icon_list == {}:
			return False

		#[DM]
		#print "[I] Creating temp path ...\n"
		if not self.create_temp_path():
			return False
		print "Done, path is"+self.tmp_ico_path

		
		#[DM]
		#print "[I] Creating build paths ...\n"
		if not self.build_paths():
			return False
	
		#print "[I] Coping icons to temp path ..."
		if not self.copy_icon_files():
			return False

		print "[I] Resizing icons"
		if not self.resize_icons():
			return False
			
		print "[I] Coping to ..."+self.icon_path + "/"+self.theme_name
		if not self.copy_to_icon_path():
			return False

		if not self.write_theme_file():
			return False

		return True

	def copy_to_icon_path(self):
		ipath = self.icon_path + "/" + self.theme_name
		if not os.access(ipath, os.F_OK):
			os.mkdir(ipath)
		else:
			os.system("rm -rf %s/*" % ipath)

		cmd = "cp -R "+self.sizes+" "+ipath
		if os.system(cmd) != 0:
			return False
		return True

	def write_theme_file(self):
		tpl = {}
		s_list = ''
		directories = ''
		for i_size in self.sizes.split():
			size = i_size.split('x')[0]
			tpl['size'] = size

			for cats in self.categories_list:
				directories += i_size + "/" + cats + ","
				tpl['category'] = cats
				if size != "Scalable":					
					tpl['type'] = "Fixed"
				else:
					tpl['size'] = "128"
					tpl['type'] = "Scalable"

				s_list += tpl_dirs_desc % tpl

		directories = directories.rstrip(',')
		final_theme_file = tpl_theme_file % (self.theme_name, directories, s_list)

		fp = open(self.icon_path + "/" + self.theme_name +"/index.theme", "w")
		fp.write(final_theme_file)
		fp.close()

		return True

	def resize_icons(self):
		res = os.system("mkdir %s" % self.sizes)
		if res != 0:
			return False
			
		for size in self.sizes.split():
			# copying each categories to each of the available sizes
			print "copying each categories to each of the available sizes"
			cmd = "cp -r %s %s" % (' '.join(self.categories_list), size)
			res = os.system(cmd)
			if res != 0:
				return False

			# Now to want to resize them
			print "Resizing ..."
			if size != "Scalable":
				for cats in self.categories_list:
					print "starting ", cats
					path = size+"/"+cats+"/"
					print "working path", path
					for files in os.listdir(path):
						cmd = "mogrify -resize %s %s/%s" % (size, path, files)
						print "x\r"
						res = os.system(cmd)
					print "ending ", cats
			else:
				for cats in self.categories_list:
					print "starting ", cats
					path = "Scalable/"+cats+"/"
					for files in os.listdir(path):
						cmd = "mogrify -resize 128x128  %s/%s" % (path, files)
						print "o\r"
						res = os.system(cmd)
					print "ending ", cats
		return True


	def get_icon_count(self):
		return len(self.icon_list)

	def remove_build_dir(self):
		if self.tmp_ico_path!='':
			cmd = "rm -rf " + self.tmp_ico_path
			if cmd != "rm -rf /" or cmd !="rm -rf ~/":
				os.system(cmd)

	def clear_list(self):
		""" Clears the list

			returns nothing
		"""
		self.icon_count = 0
		self.icon_list.clear()

	def load_themes(self):
		""" loads all the themes previousley 
			saved in the theme folder

			returns an liststore object containing all the themes
		"""
		liststore = gtk.ListStore(str)
		files = [f for f in os.listdir(self.theme_dir) if f[0] <> '.']
		files.sort()

		for s in files:
			liststore.append([s])
		return liststore

	def read_theme_file(self, fname):
		""" reads a xml file and loads the custom icons

			returns: number of the icons
		"""
		file_content = open(self.theme_dir + "/" + fname , "r").readlines()
		self.icon_count = 0

		for ln in file_content:
			line = ln.split(':')
			self.icon_list[line[0]] = line[1].strip()
			self.icon_count += 1

		self.theme_name = fname
		return self.icon_count
		
	def write_icon_theme(self):
		"""	saves icon theme by the given name

			returns status as True/False
		"""
		if self.theme_name == '':
			return False
		else:
			fp = open (self.theme_dir+ "/" + self.theme_name+".gip", "w")
			for key in self.icon_list:
				if self.icon_list[key] != '':
					fp.writelines("%s:%s\n"%(key, self.icon_list[key]))
			fp.close()
		return True

	def set_item(self, key, value):
		if self.icon_list[key] == "":
			self.icon_count += 1

		self.icon_list[key] = value

	def setup_treeview(self, filename):
		""" 
			reads the xml file and loads the icon list			

			returns: the treestore object containing all 
			the icons
		"""
		treestore = gtk.TreeStore(str)
		xmldoc=minidom.parse(filename)
		all_categories=xmldoc.getElementsByTagName('context')
		i=0

		for categories in all_categories:
			cat_dir=categories.attributes['dir'].value
			piter=treestore.append(None, [cat_dir])
			all_icons=categories.getElementsByTagName("icon")
			self.categories_list.append(cat_dir.encode('utf-8'))

			i=i+1

			for icons in all_icons:
				icn_name=icons.attributes['name'].value
				piter2=treestore.append(piter, [icn_name])
				all_link = icons.getElementsByTagName("link")
				self.icon_list[cat_dir+"/"+icn_name]=""

				for links in all_link:
					lnk=links.childNodes[0].data
					treestore.append(piter2,[lnk]) 
					self.icon_list[cat_dir+"/"+icn_name+"/"+lnk]=""

		return treestore

class IconPacker:
	""" This is the main gui class
		Handles all the  GUI related stuffs
	"""
	def __init__(self):		
		self.icon_theme = IconList()
		if os.system('convert -version')!=0:
			print "ERROR: 'convert' is missing. Please install imagemagik"

		self.current_node=None
		self.current_path=None
		self.icon_path=None

		#Set the Glade file
		self.glade_file = "ui/iconpacker.glade"
		self.wTree = gtk.glade.XML(self.glade_file) 

		#Create our dictionay and connect it
		dic = { "on_iconpacker_destroy" 		: self.exit_application, 
				"on_btnCollapseAll_clicked"		: self.collapse_treeview,
				"on_btnExpandAll_clicked"		: self.expand_treeview,
				"on_treeview_row_activated"		: self.row_acivated,
				"on_eIcnPath_changed"			: self.text_changed,
				"on_eIcnPath_drag_data_received": self.dropped_something,
				"on_setImage_clicked"			: self.set_icon_path,
				"on_btnSave_clicked"			: self.save_icon_list,
				"on_tbClear_clicked"			: self.clear_list,
				"on_cIconThemeList_changed"		: self.theme_selected,
				"on_displayInformation_clicked"	: self.print_information,
				"on_imgIcon_drag_drop"			: self.print_information,
				"on_fcImage_file_activated"		: self.set_image_icon,
				"on_fcImage_selection_changed"	: self.preview_image_icon,
				"on_btnRefresh_clicked"			: self.btn_refresh_theme_list,
				"on_btnBuild_clicked"			: self.btn_build_icon_theme }

		self.window 	= self.wTree.get_widget("IconPacker")
		self.treeview	= self.wTree.get_widget("treeview")
		self.IconPath	= self.wTree.get_widget("eIcnPath")
		self.item_name	= self.wTree.get_widget("itemname")
		self.ThemeName	= self.wTree.get_widget("ThemeName")
		self.lblStatus	= self.wTree.get_widget("lblStatus")
		self.entry		= self.wTree.get_widget("eLoadTheme")
		self.cIlist		= self.wTree.get_widget("cIconThemeList")
		self.imgIcon	= self.wTree.get_widget("imgIcon")
		self.fileSelect	= self.wTree.get_widget("fcImage")
		self.statusBar	= self.wTree.get_widget("stat_messages")
		self.context_id = self.statusBar.get_context_id("StatusBar Message")

		ff = gtk.FileFilter()
		ff.add_pattern("*.png")
		self.fileSelect.set_filter(ff)

		#getting up the existing themes
		liststore=self.icon_theme.load_themes()

		self.cIlist.set_model(liststore)
		cell = gtk.CellRendererText()
		self.cIlist.pack_start(cell, True)
		self.cIlist.add_attribute(cell, 'text', 0) 

		#connects all other events
		self.wTree.signal_autoconnect(dic)
		self.load_from_file()
		self.lblStatus.set_text("0/%s" % self.icon_theme.get_icon_count())
		self.display_status("Ready ...")

	def display_status(self, msg):
		self.statusBar.push(self.context_id, msg)

	def set_image_icon(self, fcBox):
		if self.current_node == None or self.current_path == None:
			self.display_status("Please select the icon tobe set")
			return
		img_path = fcBox.get_filename()
		self.IconPath.set_text(img_path)
		self.set_icon_path(None)

	def preview_image_icon(self, fcBox):
		img_path = fcBox.get_filename()
		self.imgIcon.set_from_file(img_path)

	def exit_application(self, widget):
		self.icon_theme.close_log()
		self.icon_theme.remove_build_dir()
		gtk.main_quit()

	def btn_build_icon_theme(self, widget):		
		fname=self.ThemeName.get_text()
		fname=fname.replace(' ', '_')
		self.display_status("Working, Please wait ...")
		self.icon_theme.build_icon_theme(fname)
		self.display_status("Done!")

	def clear_list(self, w):
		self.icon_theme.clear_list()
		
	def collapse_treeview(self,data):
		self.treeview.collapse_all()

	def dropped_something(self, widget, dcontext, data2, data3, data4, data5, data6):
		widget.set_text('')

	def expand_treeview(self,data):
		self.treeview.expand_all()

	def get_selected_item_info(self, parent_obj, path):
		"""
			Gets the current selected item

			returns a list containing required info
		"""
		model=parent_obj.get_model()

		iter=model.get_iter(path[0])
		head=model.get_value(iter, 0)

		iter=model.get_iter(path[:2])
		r1=model.get_value(iter, 0)

		if len(path)==3:
			iter=model.get_iter(path)
			r2=model.get_value(iter, 0)
			ipath = "%s/%s/%s"%(head, r1, r2)
			text = r2
		else:
			ipath = "%s/%s"%(head, r1)
			text =r1

		return [text,ipath,model]	

	def load_from_file(self):
		"""
		loads basic information

		returns Nothing
		"""
		#sets the item names
		treestore = self.icon_theme.setup_treeview('data/legacy-icon-mapping.xml')
		self.treeview.set_model(treestore)
		
		self.tvcolumn=gtk.TreeViewColumn('Icons you can set')
		
		self.treeview.append_column(self.tvcolumn)		
		
		self.treeview.set_search_column(0)	
		self.cell = gtk.CellRendererText()

		self.tvcolumn.pack_start(self.cell, True)
		self.tvcolumn.add_attribute(self.cell, 'text', 0)
		self.lblStatus.set_text("0/%s" % self.icon_theme.get_icon_count())

	def print_information(self, w):
		"""
			This is for debug purpose only!
		"""
		print "Icon list: "
		for key in self.icon_theme.icon_list:
			print key+"="+self.icon_theme.icon_list[key]

		print "Category List: "
		print self.icon_theme.categories_list 
		print "Theme dir: "
		print self.icon_theme.theme_dir
		print "Tmp dir: "
		print self.icon_theme.tmp_dir
		print "Current no of icons set: "
		print self.icon_theme.icon_count

	def row_acivated(self, parent_obj, path, col_obj):		
		"""
		Activates the selected row for applying icon to

		returns nothing
		"""
		try:
			# check if its a root path or not, it it is then ignore it
			if path[1]!=None:
				#gets info about the selected path
				text,ipath,model = self.get_selected_item_info(parent_obj, path)
				self.icon_path = ipath

				self.item_name.set_text(text)
				self.imgIcon.set_from_file('')
				self.IconPath.set_text('')

				try:
					self.IconPath.set_text(self.icon_theme.icon_list[self.icon_path])
				except:
					pass

				self.current_node=model
				self.current_path=path
		except: 
			pass
	
	def save_icon_list(self, widget):
		tname=self.ThemeName.get_text()
		if tname!="":
			self.icon_theme.theme_name = tname
			self.icon_theme.write_icon_theme()
		else:
			self.display_status("No Name given")	
		self.lblStatus.set_text("0/%s" % self.icon_theme.get_icon_count())

	
	def btn_refresh_theme_list(self, widget):
 		liststore=self.icon_theme.load_themes()
		self.cIlist.clear ()
		self.cIlist.set_model(liststore)
		cell = gtk.CellRendererText()
		self.cIlist.pack_start(cell, True)
		self.cIlist.add_attribute(cell, 'text', 0)  
		self.lblStatus.set_text("0/%s" % self.icon_theme.get_icon_count())

	
	def set_icon_path(self, widget):
		ipath=self.IconPath.get_text()
		if ipath!= '':
			self.icon_theme.set_item(self.icon_path, ipath)
			self.imgIcon.set_from_file('')
			self.IconPath.set_text('')
			str= "%s/%s" % (self.icon_theme.icon_count, len(self.icon_theme.icon_list))
			self.lblStatus.set_text(str)
			self.display_status("Icon was set for %s" % self.icon_path)
		else:
			self.display_status("No Image is selected")

	def text_changed(self, entry):		
		ipath=entry.get_text().lstrip('file:///')
		ipath=ipath.rstrip('\r\n')
		ipath=ipath.replace('%20', ' ')
		self.imgIcon.set_from_file('/'+ipath)
		entry.set_text('/'+ipath)

	def theme_selected(self, data):
		model = data.get_model()
		active = data.get_active()
		if active < 0:
			print "None"
		else:
			md=model[active][0]
			self.ThemeName.set_text(md.rstrip('.gip'))
			len=self.icon_theme.read_theme_file(md)
			self.lblStatus.set_text("%d"%(len))

class Logger:
	def __init__(self, filename):
		self.filename = filename
		self.log_lines = ''

	def save_log(self):
		fp = open (self.filename, "w")
		fp.writelines(tpl_html % self.log_lines )
		fp.close()

	def log(self, log_message, type):
		if type=="error":
			self.log_lines += '<li class="error">%s</li>' % log_message
		elif type =="warning":
			self.log_lines += '<li class="warning">%s</li>' % log_message
		else:
			self.log_lines += '<li> class="notice">%s</li>' % log_message

def get_unique_path(path, fname, limit):
	i = 0
	res = True
	while res:
		fpath=("%s/%s_%d")%(path,fname,i)
		name = ("%s_%s") % (fname, i) 
		res=os.access(fpath, os.F_OK)
		i=i+1
		# we stop trying after 100 attempts...
		if i > limit:
			return False

	return [fpath, name]

		


if __name__ == "__main__":
	hwg = IconPacker()
	gtk.main()
