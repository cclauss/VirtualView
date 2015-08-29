# coding: utf-8
# Pythonista 1.6
# many things just copied from omz starter code
# all the bad stuff, thats me :)
# still learning


###### VirtualView #######
# for displaying large amounts of data


# needed for 1.6 at the moment, if importing from same dir
'''
import sys
if '.' not in sys.path:
    sys.path.insert(0, '.')
   
'''

# using Faker to demo....data
from faker import Faker
fake = Faker()

import time, os
from time import strftime

'''
	
	17 Aug 2015
	1. color_demo, added random color when clicked.
	
	18 Aug 2015
	1. using gistcheck.py to commit this file to gisthub.
	i thought it was working, its not working though.
	i want to punch it, drives me crazy. 
	
	2. **** Important *****
	no need to add a button for a hit test now. when you create your cell, you can set self.action to a method/function. if the cell is clicked/hit, the self.action will be called if defined.
	Changed all the demo cells to work off the new mechanism. 
	
	3. changing the click mechanism had a side effect. the cell was not being released from memory when setting self.action = some_method. In the release
	function i now set self.action = None, the memory leak stopped.
	
	4. added 'Top' and 'Bottom' menu items to the titlebar. just to take you to the top abd bottom of the list.
	
	5. the initial cell count is 100 million. its a VirtualView. 5 or 500 million cells should not matter. if you are not comportable with that number, just change _item_count below to a smaller number!
	6. changed the ui.Label width to be able to display the number correcly. did it the lazy way :(
	
	20 Aug 2015
	1. i stopped using self.bounds etc for calculations. the scrollview is used now as it should have been. this is required if you need to but anyother view inside the same containing view.
	
	22 Aug 2015
	1. added a scroll navigator. lets you move through the list in percent increments
	2. adder Faker for more real world data examples 
	3. have a list called subview_destroy_register.if a view is appended to this list, the release method will remove the view
	4. added a Stress class. this just keeps scrolling the list, using ui.delay. the nice thing about this is that no code is requied inside the virtualview class.
	
	23 Aug 2015
	1. added the concept of a table.  there is a new class TableHeader that can be added to the top of the view, and i did a demo of making columns. because in the colums, the views are views inside views, there is a list subview_destroy_register you can append views to. when the release is called, any view in that list is removed from the view. we think about this more. maybe, i am just being stuip. maybe i should just walk all the subviews and remove them.
	
	26 Aug 2015
	1. added a Class ThreadedCell. Like all of this is, its just work in progress.  the idea is that will try and get slow loading resouces from the web etc. i have just tried to simulate this with time.sleep at the moment. but pretty sure urs going to get more involved than that once i start using something like requests.  some fun and homework coming my way :)
	2. added, ActivityIndicator to the ThreadedCell class.
	
	27 Aug 2015
	1. added a DataProvider class. this seemed smarter. all is ok when i am using sample data, but as the data requirements get more sophisiticated, more logic code will creep into the VirtualView, which is bad in my view.
	
	
	
	General Notes
	=============================================
	1. when creating a cell/row and set a callback function, other than the ones already definded, you should explicitly set the action field to none in the release method of the VirtualCell class. 
	if you dont do this, your objects will not be freed from memory resulting in a memory leak.
	
	
	To-do, ideas
	============================================
	1. to create cells on a thread. maybe the cell is trying to get a image from a url etc. but a lot for me to think about.
	
	2. load cell from pyui file. i dont expect this to be difficut. i think at least. but trying to keep on publishable source file for the moment.
	
	3. will merge ThreadedCell and VirtualCell together at some point. i seperated them because i am learning. easier this way, to develop and test.
	
	4. have a goto cell method. this should be easy by calling self.frame_for_item. scoll to the y
	
'''


import ui
from random import randint
import random
import time, sys
import console

import threading
import requests
from bs4 import BeautifulSoup
import urllib2

# CellBaseClass.py
from CellBaseClass import CellBase

# determining if Phytonista 1.5 or 1.6xxx
__ver__ = 0
try:
	import dialogs
	__ver__ = 1.6
except ImportError:
	__ver__ = 1.5


# for tableview style...will expand on this later
# i think will use a list of named tuples. Column should include, width, alignment, possibly font etc.
table_def = [('Name'), ('Company'), ('User Name'), ('CT')]

# some helper functions
def random_color():
	# for demo purposes
	return(randint(0,255) / 255., randint(0,255) / 255., randint(0,255) / 255.)

def invert_rgb(color):
	return(255 - color[0], 255 - color[1], 255 - color[2], 0)

def rand_image():
	# just return an image from, a list (subset)
	# of pythonista built images.
	# testing/demo purposes
	return ui.Image.named(images[randint(0,len(images) -1)])

def inset_frame(f, left, top, w, h):
		return (f[0] + left, f[1] + top, f[2] + w, f[3] + h)
# end helper functions
	

# whether or not to add a scroll navigation bar
_add_nav_bar = False

# whether or not to add a title header
_add_table_header = False



class RandomImage(object):
	def __init__(self):
		pics_path = os.path.abspath(os.path.join(os.__file__, '../../../../Textures'))

		self.images = os.listdir(pics_path)
		
	def get_image(self):
		# just testing
		ui.Image.named(random.choice(self.images)).show()

# cell we are using in the VirtualView
class TestCellVirtualViewCell(ui.View , CellBase):
	def __init__(self, w, h, item_index, Threaded = False, auto_start_thread =True):
		CellBase.__init__(self, w, h , item_index, threaded = Threaded, thread_auto_start = auto_start_thread)
		
		self.add_item_id_label()

# cellwe are using as a standalone, so to speak!		 
class TestCellFreeStanding(ui.View , CellBase):
	def __init__(self, w, h, item_index, Threaded = False, auto_start_thread =True):
		CellBase.__init__(self, w, h , item_index, threaded = Threaded, thread_auto_start = auto_start_thread)
	
	# overridden
	def cell_clicked(self):
		self.start_thread()

# this is a mess. just wanted to get a data provider
# so not to blog the VirtualView down with data
# collecting... for me requies a lot of thought
class DataProvider(object):
	def __init__(self, rec_count = 0):
		
		# regardless, self.rec_count has to represent
		# the number rows of data. is the only real
		# count that can be relied upon!
		self.rec_count = rec_count
		
		
		self.data_list = []
		self.data_loaded = False
		self.data_row_proc = self._get_data_row_faker
		
	def data_load(self):
		pass
		
	def get_nth_record(self, record_index):
		if record_index > self.rec_count:
			# guess i should raise an error here
			return ''
		# call the func pointed to by self.data_row_proc
		# if the class gets more complex, aviod a lot
		# of logic code here. could potentially change
		# func during exec if it made sense.
		return self.data_row_proc(record_index)	
		
	@property
	def num_records(self):
		return(self.rec_count)
	
	# methods that actually return the data
	def _get_data_row_faker(self, record_index):
		return  [fake.name(), fake.company(), fake.user_name(), fake.country_code()]
		
	def release(self):
		pass
	

class VirtualView(ui.View):
	def __init__(self, w, h, item_size, buf_size = 0, data_provider = None, use_threaded_cell = False):

		"""
		A VirtualView for displaying large
		amounts of data in scrollable area. 

		Attributes:
		item_width:
		width of cell
		item_height:    
		heigth of cell
		buf_size:
		items:
		item_count:
		"""
		
		# set the width and height of the view
		self.background_color = 'white'
		self.width = w
		self.height = h
		self.threaded_cell = use_threaded_cell
		# buf_size gets set in the layout method.
		# currently if its smaller than one screen
		# of items, its resized to be able to hold
		# at least one screen of items
		self.buf_size = buf_size

		# a list of VirtualCell objects, the number of
		# buffered Cells, dedends on bufsize
		self.buffer = []

		# calculated in layout method
		self.items_per_row = 0

		# store the the w,h like this for ease of reading
		self.item_width = item_size[0]
		self.item_height = item_size[1]
		
		# not in use yet. rather than hand coding extra
		# views into this parent, i want to add views 
		# via a method. Things like a table header.
		# but want them to behave correctly with 
		# orientation, overlapping etc...
		self.added_views = []
		
		# flags to indicate that the width of height or
		# both should be overwridden.  if item_width or
		# item height is 0, the width or height if the
		# scrollview is used
		self.override_width = False
		self.override_height = False

		if self.item_width == 0:
			self.override_width = True

		if self.item_height == 0:
			self.override_height = True

		# to make sure we are called by layout
		self.flex = 'WH'

		# set up a scrollview, with delagate
		#self.sv = ui.ScrollView(flex='WH')
		self.sv = ui.ScrollView()
		self.sv.delegate = self
		self.add_subview(self.sv)

		# a class that provides the data.
		# seperated this into a class to clean it up
		# a bit 
		self.dp = data_provider
		
		# just demo/debug menu title btns
		btn = ui.ButtonItem(title = 'Top')
		btn.action = self.goto_top
		
		# spacer button :(
		btn1 = ui.ButtonItem(title =' ' * 5)
		
		btn2 = ui.ButtonItem(title ='Bottom')
		btn2.action = self.goto_end
		self.right_button_items = [btn2, btn1, btn]
		
		
		# some debug vars
		self.created_cells = 0
		self.deleted_cells = 0
		self.used_buffered_cells = 0
		self.start = time.time()
		
		# add a navigation bar
		# going to chang the way i add these views
		self.nav_bar = None
		_add_nav_bar = False
		if _add_nav_bar:
			self.nav_bar = NavClass( 32, increments = 5, callback = self.goto_percent)
			self.add_subview(self.nav_bar)
		
		#add table header
		#going to chang the way i add these views
		self.table_header = None
		_add_table_header = False
		if _add_table_header:
			self.table_header = TableHeader(self.width, 32, table_def)
			self.add_subview(self.table_header)

	def goto_top(self, sender):
		self.sv.content_offset = (0,0)
		
	def goto_end(self, sender):
		self.sv.content_offset = (0, self.sv.content_size[1] - self.height)
		
	def goto_percent(self, sender):
		scroll_value = self.sv.content_size[1]
		percent = float(sender.name) / 10. 
		new_scroll_value = (0, scroll_value * percent)
		self.sv.content_offset = new_scroll_value
	
	def add_view(the_view, where):
		pass
		
	# this method returns the data item count
	def item_count(self):
		# dataprovider does the checks
		return self.dp.num_records

	# ui.View callback
	def layout(self):
		w,h = self.bounds[2:]
		
		# if we have added a navigation bar
		if self.nav_bar:
			w -= self.nav_bar.width
		
		# if we have a header row
		if self.table_header:
			h -= self.table_header.height
			
		
		# set the content height of the scrollview
		sv = self.sv
		sv.width = w
	 	sv.height = h
	 	if self.table_header:
	 		sv.y = self.table_header.height
		
		# see if we are overriding the item_size
		if self.override_width and self.override_height:
			self.item_width , self.item_heigth = sv.bounds[2:]
		elif self.override_width:
			self.item_width = w
		elif self.override_height:
			self.item_height = h

		# number of visible rows
		self.visible_rows = int(h / self.item_height)

		# adding 2 addtional visible rows here. nicer
		# scrolling. extra line and comment, just so
		# its not just a magic + 2
		self.visible_rows += 2

		# items per row
		self.items_per_row =int(w / self.item_width)

		# maximum num of rows
		max_rows = (self.item_count() / self.items_per_row)

		# add an extra row if not an exact multiple
		if self.item_count() % self.items_per_row <> 0:
			max_rows += 1
			
		sv.content_size =(w, max_rows * self.item_height)
		
		# adjust the the navigation bar if we have one
		if self.nav_bar:
			nav_bar = self.nav_bar
			nav_bar.x = self.width - nav_bar.width
			#nav_bar.heigth = self.height
			nav_bar.user_layout(self.height)
			
		if self.table_header:
			self.table_header.user_layout(self.width)
			
			
		# the way the buffer is implemented it does
		# not work correctly if it is smaller than
		# the number of items on the screen.
		# can be done, more a performance issue
		# so the buffer is resized here if required.
		min_buf_size = self.visible_rows * self.items_per_row
		if self.buf_size < min_buf_size:
			self.buf_size = min_buf_size
		
		# clear the buffer, remove all the subviews
		# needed when the orientation changes, is not
		# called on all presentation styles. Not an
		# issue, layout is called by ui when req.
		for cell in self.buffer:
			cell.release()
			del cell
			self.deleted_cells += 1 # debug

		self.buffer = []
		
		

	# ui.View callback
	def draw(self):
		# useful to use the draw method of ui
		# on startup and orientation change we
		# are called as expected.
		# this method is also called explictly from
		# scrollview_did_scroll

		v_offset = self.sv.content_offset[1]

		# get the first visible row
		row = int(v_offset / self.item_height)

		# get the visible items to draw
		visible_items = self.items_visible()
		
		# draw each item
		for item_index in visible_items:
			self.draw_item(item_index)

	# ui callback, ui.scrollview delegate
	def scrollview_did_scroll(self, scrollview):
		self.draw()

	def draw_item(self, item_index):
		# if the item_index is found in the buffer
		# we know the cell is still present in the
		# scrollview. so we exit, we dont need to
		# recreate the cell
		for cell in self.buffer:
			if cell.item_index == item_index:
				self.used_buffered_cells += 1 # debug
				return
		
		# get the data for the item_index
		data_item = self.dp.get_nth_record(item_index)
		
		# create a cell (view), that is added to the
		# subviews of the scrollview. once the buffer
		# is full, the oldest cell is removed from
		# the scrollview.subviews
		cell = TestCellVirtualViewCell(self.item_width, self.item_height, item_index, Threaded = self.threaded_cell)
		
		self.created_cells += 1	# debug

		self.sv.add_subview(cell)
		cell.frame = self.frame_for_item(item_index)
		
		# maintain the buffer
		self.buffer.append(cell)

		if len(self.buffer) > self.buf_size:
			cell = self.buffer[0]
			if hasattr(cell, 'release'):
				cell.release()
			del cell
			self.buffer.pop(0)
			self.deleted_cells += 1 # debug
			if len(self.sv.subviews) > len(self.buffer):
				raise StandardError('Views are not being released from memory correctly.')

	# get the frame for the given item index
	def frame_for_item(self, item_index):
		w, h = self.sv.bounds[2:]
		items_per_row = self.items_per_row
		row = item_index / items_per_row
		col = item_index % items_per_row

		if items_per_row == 1:
			x_spacing = (w - (items_per_row * self.item_width)) / (items_per_row)
		else:
			x_spacing = (w - (items_per_row * self.item_width)) / (items_per_row-1)

		return (col*(self.item_width + x_spacing), row*self.item_height, self.item_width, self.item_height)

	# get the visible indices as a range...
	def items_visible(self):

		y = self.sv.content_offset[1]
		w, h = self.sv.bounds[2:]

		items_per_row = self.items_per_row
		num_visible_rows = self.visible_rows

		first_visible_row = max(0, int(y / self.item_height))

		range_start = first_visible_row * items_per_row

		range_end = min(self.item_count(), range_start + num_visible_rows * items_per_row)

		return range(range_start, range_end)

	# ui.View callback
	def will_close(self):
		# do some clean up, make sure nothing
		# left behind in memory.
		# maybe this is not need, but easy to do it
		for cell in self.buffer:
			cell.release()
			del cell
			self.deleted_cells += 1 #debug
		self.buffer = []


		# print out some debug info
		print 'Created Cells = {}, Deleted Cells = {}, Used buffered Cells = {}'.format(self.created_cells, self.deleted_cells, self.used_buffered_cells)

class NavClass(ui.View):
	def __init__(self, width, increments = 10, callback = None):
		
		self.hit_callback = callback
		self.width = width
		
		btn_font = ('<system-bold>', 12)
		
		for i in range((100 / increments)):
			inc = str((i * increments)/10.)
			btn = ui.Button(name = str(inc))
			btn.title = str( i * increments) + '%'
			btn.action = self.hit
			btn.font = btn_font
			self.add_subview(btn)
		
		self.background_color = 'orange'
		
	def user_layout(self, height):
		# when the parent classes layout method is
		# called, we manually call thus method to
		# redraw our views objects
		self.height = height
		w = self.width
		h = height / len(self.subviews)
		
		for i, btn in enumerate(self.subviews):
			btn.frame = (0, i * h, w, h )
	
	def hit(self, sender):
		# communicate with parent
		if self.hit_callback:
			self.hit_callback(sender)
			
class TableHeader(ui.View):
	def __init__(self,w, h,  tb_def):
		self.num_cols = len(tb_def)
		self.table_def = tb_def
		print self.num_cols
		self.width = w
		self.height = h
		col_width = w / self.num_cols
		header_font = ('Menlo', 18)

		for i, rec in enumerate(tb_def):
			col_header = ui.Label(name = str(i))
			col_header.border_width =.5
			col_header.border_color = 'white'
			col_header.alignment = ui.ALIGN_CENTER
			col_header.text = rec
			col_header.background_color = 'black'
			col_header.text_color = 'white'
			col_header.font = header_font
			col_header.border_width = .5
			self.add_subview(col_header)
			
		
	def user_layout(self, w):
		self.width = w
		col_width = w / self.num_cols
	
		for i, rec in enumerate(self.table_def):
			f = (i * col_width, 0, col_width, self.height)
			lb = self[str(i)]
			lb.frame = f

class Stress(object):
	# an auto scroller for VirtualView class
	# to stress test it. 
	def __init__(self, obj, delay = .1): 
		
		# doing for saftey
		ui.cancel_delays()
		
		# no sleeping...
		console.set_idle_timer_disabled(True)
		
		self.obj = obj
		self.delay = delay
		self.busy = False
		# record the start time
		self.start = time.time()
		ui.delay(self.auto_scroll, 2)
		
		
	def auto_scroll(self):
		# this busy signal, probably not required.
		# but will keep it in anyway. its a small price
		# to pay for extra saftey.
		if self.busy:
			ui.cancel_delays()
			return 
		
		# thanks @JonB
		# if the view is not onscreen, we delete ourself
		# moments later our __del__ is called...
		if not self.obj.on_screen:
			print 'off screen'
			ui.cancel_delays()
			return
			
		self.busy = True
			
		# the scrollview
		sv = self.obj.sv
		
		# current offset of the scrollview
		v_offset = sv.content_offset[1]
		# calc new_offset, to be + one page 
		new_offset = v_offset + sv.height
		
		# wrap around if we reach the bottom if the list
		if new_offset > sv.content_size[1]:
			new_offset = 0
			
		sv.content_offset = (0, new_offset )
		
		ui.cancel_delays()
		ui.delay(self.auto_scroll, self.delay)
		self.busy = False
	
def VirtualViewTest( w, h, data_provider,demo_type,  use_stress = False, present = 'sheet'):
	
	_buf_size = 80 
	_item_size = (128, 128)
	
	if demo_type == 'image':
		_item_size = (128, 128)
	elif demo_type == 'row':
		_item_size = (0, 44)
	else:
		return
	
	vv = VirtualView(w, h,  _item_size, _buf_size, data_provider = data_provider , use_threaded_cell = True)
	vv.present(present)
	if use_stress:
		Stress(vv, delay = 1.5)
	
def StandAloneTest(w, h, present):
	v = ui.View(frame = (0,0,w, h))
	v.name = 'Click the cell to start download'
	item_w = w / 2
	item_h = h / 2
	for i in range(0,4):
		cell= TestCellFreeStanding(item_w, item_h, i, Threaded = True, auto_start_thread = False)
		cell.frame = ((i % 2) * item_w, (i / 2) * cell.height , cell.width, cell.height)
		v.add_subview(cell)
		cell.start_thread()
	v.present(present)
	

if __name__ == '__main__':
	
	if __ver__ == 1.6:
		# because i can't see!!
		console.set_font('Menlo', 22)
	
	_present = ''
	# stick with 1.5 sizes at the moment	
	#w , h = 540, 576
	# for the repo, do differently...
	w,h = ui.get_screen_size()
	
	
	__STANDALONE_TEST = False
	if __STANDALONE_TEST:
		StandAloneTest(w, h, _present)
	else:
		dp = DataProvider(rec_count = 100000)
		# only 
		VirtualViewTest(w,h, dp, demo_type = 'image', use_stress = True, present = _present)
