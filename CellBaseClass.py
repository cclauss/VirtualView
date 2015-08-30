# coding: utf-8
import threading
import ui
import random, time
from random import randint

class CellBase(object):
	def __init__(self, w, h, item_index, threaded = False,  thread_auto_start = False):
		
		self.width = w
		self.height = h
		self.item_index = item_index
		
		# threading stuff
		self.threading = threaded
		self.event = None
		self.thread = None
		
		# activity indicator
		self.act_ind = None
		
		# flags
		self.data_loaded = False
		self.data_loading_error = 0
		
		# create the view for the cell.
		self.create_cell_contents()
		if thread_auto_start:
			self.start_thread()
		
	def start_thread(self):
		# if we are threaded, and we have a thread that
		# is alive, bug out. if it made sense, these 
		# exta request could be queued. will try to get
		# this going properly first :)
		if self.threading:
			if self.thread:
				if self.thread.isAlive():
					print 'thread failed - thread still running' # debug
					return
					
			# Was going to try and resuse the thread.
			# apprently, you cant. at least try to clean
			# it up
			# i will look at using thread 'with thread'..
			# apprently the Threading module supports
			# the cobtext manager. i need to read more
			if self.thread:
				self.thread = None
				
			self.thread =threading.Thread(target = self.fetch_data)
			self.event = threading.Event()
			self.thread.start()
	
	def start_activity(self):
		# if we dont have an activity indicator
		# create one...
		if not self.act_ind:
			self.act_ind = ui.ActivityIndicator()
			self.act_ind.style = 12
			self.add_subview(self.act_ind)
			
		#self.act_ind.center = self.center
		self.act_ind.frame = (0,0, self.act_ind.width, self.act_ind.height)
			
		self.act_ind.start()
		
	def stop_activity(self):
		# if we have a activity ind. ,try and stop it
		if self.act_ind:
			self.act_ind.stop()
			
	# this method to be overriden in the child
	def create_cell_contents(self):
		# the place you would typically create your
		# cells ui elements
		#self.add_item_id_label()
		self.border_width = .5
		self._set_row_alt_color('tan', 'orange')
	
	# this method to be overriden in the child
	def fetch_data(self):
		self.start_activity()
		
		for i in range(3):
			if self.event.isSet() : 
				self.stop_activity()
				self.data_loaded = 'False'
				self.data_loading_error = 1
				return
			# same as do something
			time.sleep(random.random())
			
		if not self.event.isSet():
			self.set_bgcolor_to_random()
			
	
		self.stop_activity()
		self.data_loaded = True
		self.data_loading_error = 0
			
			
	# aux , helper methods	
	def random_color(self):
		return(randint(0,255) / 255., randint(0,255) / 255., randint(0,255) / 255.)
	
	def set_bgcolor_to_random(self):
		self.background_color = self.random_color()
	
	def get_random_image(self):
		pass

	def _set_row_alt_color(self, color_1, color_2):
		if not self.item_index % 2:
			self.background_color = color_1
		else:
			self.background_color = color_2
			
	def add_item_id_label(self):
		# just add a label to see the item_index.
		# handy for debugging
		
		txt = '{:,}'.format(self.item_index)
		w, h = 10 * len(txt), 20
		f = (self.width - w, 0, w , h)
		lb = ui.Label( frame = f)
		lb.frame = f
		lb.background_color = 'black'
		lb.text_color = 'white'
		lb.text = txt
		lb.alignment = ui.ALIGN_RIGHT
		self.add_subview(lb)
		lb.bring_to_front()

	# might need this if a single frame
	def layout(self):
		pass
	
	# no need to add a btn to the view for a click
	# event. this works very well.
	# As long as we are ok with the whole cell 
	# ignoring, touch_began, touch_moved. Of course,
	# other opporturnities to use these events.
	# KISS at the moment :)
	def touch_ended(self, touch):
		self.cell_clicked()
		
	def cell_clicked(self):
		print self.item_index #debug
		pass
		
	# explicity call this method, to free up
	# resources. whatever they maybe. dont rely on
	# __del__
	# can override this method, but then have to do all
	# your own clean up. The general idea is to get 
	# this method working enough so you dont need to
	# override it.
	# hmmm, will add a callback, that if set, this 
	# method will call it.
	def release(self):
		
		# deal with the threading first
		if self.threading:
			if self.thread:
				if self.thread.isAlive():
					self.event.set()
				
		self.stop_activity()
		
		# call a user release method. one that can
		# be overriden without disturbing this method!
		# Not sure about the placement of this call. 
		# i was tempted to put it at the end of this
		# method, would mean all the subviews would 
		# have been removed! hmmmm, not sure
		self.user_release()
		
		# remove ourself from the superview
		# maybe this is a stupid idea. Maybe
		# smarter for the caller to remove us?
		if hasattr(self, 'superview'):
			self.superview.remove_subview(self)

		# this would not always be required. but
		# i found when a button for example has a
		# action attached, even internal to this
		# class. Memory is not being released unless
		# the subviews are removed. thats only one
		# example. could be others, if using other
		# callbacks such as delegates.
		
		for sv in self.subviews:
			self.remove_subview(sv)
		
		self.thread = None
		
	
	# if you need to release memory/resources in the 
	# child, override this method. Its called from
	# inside the release method. threads are stopped
	# and cleaned up, all views are still avaliable
	# and released after this method returns.
	def user_release(self):
		pass
		
		