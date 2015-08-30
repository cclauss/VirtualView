# coding: utf-8

# for use in VirtualView

# this is a mess. just wanted to get a data provider
# so not to blog the VirtualView down with data
# collecting... for me requies a lot of thought

# using Faker to demo....data
from faker import Faker
fake = Faker()

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
	
