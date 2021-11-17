import bitmath


# TODO: Use the following page to implement a better set associative
#  cache with byte arrays and etc
#  https://www.sciencedirect.com/topics/computer-science/set-associative-cache




class MemoryHandler:
	def __init__(self,
		ram_size,
		cache_size,
		cache_line_size,
		cache_associativity
	):
		self.cache_line_size = cache_line_size

		self.ram = RandomAccessMemory(
			size=ram_size,
			cache_line_size=cache_line_size)

		self.cache = SetAssociativeCache(
			size=cache_size,
			associativity=cache_associativity,
			cache_line_size=cache_line_size)

		self.address_size = bitmath.log2(ram_size)


	def __repr__(self):
		return ("<"
			+ f"Memory Handler: "
			+ f"ram size={self.ram.size}, "
			+ f"cache size={self.cache.size}, "
			+ f"cache associativity={self.cache.associativity}, "
			+ f"line size={self.cache.cache_line_size}"
		+ ">")


	def read_line(self, address):
		# Try read from cache first
		_, cache_line = self.cache.read(address)
		if cache_line != None:
			# Cache hit!
			print("CACHE HIT")
			return cache_line
		print("CACHE MISS")

		# Cache miss. Read from RAM and store in cache
		cache_line = self.ram.read_line(address)
		popped_address, popped_line = self.cache.write(address, cache_line)

		# If there was a popped cache line, write to RAM
		if popped_address != None:
			self.ram.write_line(popped_address, popped_line)

		return cache_line


	def read_byte(self, address):
		cache_line = self.read_line(address)

		# Calculate the offset from the address
		offset = address & (self.cache_line_size-1)

		# Just return the requested byte
		return cache_line[offset]


	def write_line(self, address, cache_line):
		# Write line to cache
		popped_address, popped_line = self.cache.write(address, cache_line)

		# If there was a popped cache line, write to RAM
		if popped_address != None:
			self.ram.write_line(popped_address, popped_line)


	def write_byte(self, address, b):
		# Access line
		cache_line = self.read_line(address)

		# Calculate the offset from the address
		offset = address & (self.cache_line_size-1)

		# Modify cache line
		cache_line[offset] = b

		# Rewrite to memory!
		self.write_line(address, cache_line)


	def load_ram_from_bytearray(self, b):
		self.ram.load_from_bytearray(b)



class RandomAccessMemory:

	def __init__(self,
		size,
		cache_line_size=1
	):
		self.size = size
		self.cache_line_size = cache_line_size
		self.data = bytearray(size)


	def __repr__(self):
		return ("<"
			+ f"Random Access Memory: "
			+ f"size={self.size}, "
			+ f"line size={self.cache_line_size}"
		+ ">")


	def _calc_cache_line_address(self, address):
		# Strip 'cache line size' bits from lowest
		#  address bits.
		return address & (self.size - self.cache_line_size)


	def read_line(self, address):
		cache_line_address = self._calc_cache_line_address(address)
		return self.data[cache_line_address:cache_line_address+self.cache_line_size]


	def write_line(self, address, cache_line):
		cache_line_address = self._calc_cache_line_address(address)
		self.data[cache_line_address:cache_line_address+self.cache_line_size] = cache_line


	def load_from_bytearray(self, b):
		self.data[:len(b)] = b


	def memdump(self):
		print("== MEMORY DUMP START ==")
		row_width = 16
		for x in range(0, self.size, row_width):
			print(self.data[x:x+row_width].hex())
		print("== MEMORY DUMP END ==")



class SetAssociativeCache:

	def __init__(self,
		size,
		associativity,
		cache_line_size
	):
		self.size = size
		self.associativity = associativity
		self.cache_line_size = cache_line_size

		self.set_count = int(size / (associativity * cache_line_size))

		# Calculating size of offset, index, tag

		# Offset: Specifies a byte within a cache line.
		#  Lowest X bits of an address
		self.offset_size = bitmath.log2(self.cache_line_size)

		# Index: Set index specifies which set.
		#  Lowest X bits after Offset
		self.index_size = bitmath.log2(self.set_count)

		# Tag: Uniquely identifies lines with the same Offset and Index
		#  Rest of the bits
		...

		# Create the sets!
		self.sets = [
			SetAssociativeCacheSet(self.associativity)
			for _ in range(self.set_count)]


	def __repr__(self):
		return ("<"
			+ f"Set Associative Cache: "
			+ f"size={self.size}, "
			+ f"associativity={self.associativity}, "
			+ f"set count={self.set_count}"
		+ ">")

	def _calc_offset(self, address):
		# Offset: Specifies a byte within a cache line.
		#  Lowest X bits of an address
		# 2**offset_size - 1
		#	= 2**log2(line_size) - 1
		#	= line_size - 1
		return address & (self.cache_line_size-1)
	def _calc_index(self, address):
		# Index: Set index specifies which set
		#  Lowest X bits after Offset
		# 2**index_size - 1
		# 	= 2**log2(set_count) - 1
		# 	= set_count - 1
		return (address >> self.offset_size) & (self.set_count-1)
	def _calc_tag(self, address):
		# Tag: Uniquely identifies lines with the same Offset and Index
		#  Rest of the bits
		# offset_size + index_size
		# 	= log2(line_size) + log2(set_count)
		# 	= log2(line_size) + log2(size / (assoc * line_size))
		# 	= log2(line_size) + log2(size) - log2(assoc) - log2(line_size)
		# 	= log2(size) - log2(assoc)
		return address >> (self.offset_size + self.index_size)


	def read(self, address):
		# Access set
		index = self._calc_index(address)
		s = self.sets[index]

		# Try read using tag
		tag = self._calc_tag(address)
		cache_line = s.read(tag)

		# Calculate address actually used from tag and index
		used_address = (
			tag << (self.offset_size + self.index_size)
			| index << (self.offset_size))

		# NOTE: If cache_line is None, cache miss.
		return used_address, cache_line


	def write(self, address, cache_line):
		# Access set
		index = self._calc_index(address)
		s = self.sets[index]

		# Write using tag
		tag = self._calc_tag(address)
		popped_tag, popped_line = s.write(tag, cache_line)

		# If data was removed from cache, return the address of it. We
		#  can calculate it from the index we read from along with the
		#  popped tag.
		if popped_tag != None:
			# Address format is (TAG + INDEX + OFFSET), so we can
			#  shift the tag all the way to the right, then add the
			#  shifted index
			popped_address = (
				popped_tag << (self.offset_size + self.index_size)
				| index << (self.offset_size))
		else:
			popped_address = None

		# Return popped data
		return popped_address, popped_line


	def memdump(self):
		print("== CACHE DUMP START ==")
		for x in range(self.set_count):
			print(f"Set {x}:")
			self.sets[x].memdump(indent=2, header=False)
		print("== CACHE DUMP END ==")



class SetAssociativeCacheSet:
	def __init__(self, associativity):
		self.associativity = associativity

		# TODO: Use a bit for availability
		# self.available = [0]*associativity
		self.stored_count = 0

		self.tags = [None]*associativity
		self.data = [None]*associativity


	def read(self, given_tag):
		# Check each index.
		cache_line = None
		for i in range(self.stored_count):
			tag = self.tags[i]

			if tag == given_tag:
				# Cache hit! Get the data and update order
				cache_line = self.data[i]
				self.tags.pop(i)
				self.tags.insert(0, tag)
				self.data.pop(i)
				self.data.insert(0, cache_line)
				return cache_line

		# If we missed after looking at all the tags
		return None


	def write(self, given_tag, cache_line):
		# First check if the tag already exists so we can overwrite
		i = 0 # Set i so that if stored count is zero, i is not undefined
		for i in range(self.stored_count):
			tag = self.tags[i]

			if tag == given_tag:
				# Cache hit! We can pop this and then write a new one.
				self.tags.pop(i)
				self.data.pop(i)
				self.tags.insert(0, given_tag)
				self.data.insert(0, cache_line)
				# Nothing removed, so nothing to return
				return None, None

		# If we get to here, either we got to the end of the cache, or
		#  we had no hits.
		if i == self.associativity-1:
			# If we got to the end of a full cache, eviction time!
			print("EVICTION")
			popped_tag = self.tags.pop(i)
			popped_line = self.data.pop(i)
		else:
			# We got to the end of a non-full cache. Just insert!
			popped_tag = None
			popped_line = None
			self.stored_count += 1

		# Insert new data
		self.tags.insert(0, given_tag)
		self.data.insert(0, cache_line)

		# Return popped data if any.
		return popped_tag, popped_line


	def memdump(self, indent=0, header=True):
		if header: print("== CACHE SET DUMP START ==")
		for x in range(self.associativity):
			if self.tags[x] == None:
				print(f"{' '*indent}tag:{self.tags[x]}, data:{self.data[x]}")
			else:
				print(f"{' '*indent}tag:{bin(self.tags[x])}, data:{self.data[x].hex()}")
		if header: print("== CACHE SET DUMP END ==")




if __name__ == "__main__":
	ram_size = 256
	cache_size = 32
	cache_line_size = 4
	cache_associativity = 2

	mh = MemoryHandler(
		ram_size=ram_size,
		cache_size=cache_size,
		cache_line_size=cache_line_size,
		cache_associativity=cache_associativity)

	# Print all our memory objects
	print(mh)
	print(mh.ram)
	print(mh.cache)

	# Load some initial data
	init_data = (
		b"\x02\x06\x06\x01\x05\x01\x06\x06\x04\x08\x06\x08\x05\x00\x02\x02" +
		b"\x06\x02\x08\x03\x09\x00\x00\x02\x04\x02\x06\x09\x00\x06\x02\x09" +
		b"\x02\x04\x04\x06\x06\x04\x01\x04\x06\x04\x06\x09\x01\x01\x06\x03" +
		b"\x02\x02\x05\x01\x00\x04\x05\x08\x03\x03\x03\x01\x03\x08\x08\x00" +
		b"\x00\x00\x07\x09\x00\x05\x06\x01\x04\x05\x04\x05\x07\x03\x08\x08" +
		b"\x03\x09\x09\x06\x05\x03\x00\x03\x07\x09\x07\x07\x08\x09\x07\x04" +
		b"\x06\x03\x03\x00\x06\x04\x05\x08\x08\x04\x03\x09\x04\x00\x02\x00" +
		b"\x09\x00\x05\x05\x01\x01\x06\x06\x00\x07\x01\x09\x04\x08\x06\x02" +
		b"\x08\x05\x02\x00\x01\x04\x05\x01\x05\x06\x05\x09\x05\x06\x00\x09" +
		b"\x08\x09\x02\x03\x04\x04\x07\x04\x00\x04\x08\x04\x01\x03\x03\x05" +
		b"\x09\x03\x00\x05\x09\x00\x03\x03\x03\x01\x09\x06\x04\x07\x03\x06" +
		b"\x06\x09\x03\x07\x01\x03\x07\x01\x07\x01\x04\x06\x06\x04\x02\x02" +
		b"\x05\x07\x04\x08\x04\x05\x01\x03\x09\x06\x03\x05\x07\x07\x01\x07" +
		b"\x06\x00\x00\x03\x07\x01\x02\x04\x08\x08\x09\x08\x00\x07\x08\x06" +
		b"\x03\x04\x06\x03\x01\x00\x06\x00\x01\x08\x07\x01\x07\x07\x03\x02" +
		b"\x04\x05\x06\x04\x04\x06\x02\x08\x02\x08\x04\x08\x01\x00\x07\x03")
	mh.load_ram_from_bytearray(init_data)

	# Dump the state
	mh.ram.memdump()
	mh.cache.memdump()


	print("\n\n\nTESTING READING!!!")
	# Perform our first read
	x = mh.read_byte(0x73)
	print(hex(x))
	mh.cache.memdump()

	# Perform second read. Should be from cache
	x = mh.read_byte(0x70)
	print(hex(x))
	mh.cache.memdump()


	print("\n\n\nTESTING EVICTION!!!!")
	# Reset ready for cache eviction test
	mh = MemoryHandler(
		ram_size=ram_size,
		cache_size=cache_size,
		cache_line_size=cache_line_size,
		cache_associativity=cache_associativity)
	mh.load_ram_from_bytearray(init_data)

	# Perform some more reads to set up cache eviction
	_ = mh.read_line(0x50)
	_ = mh.read_line(0x00)
	_ = mh.read_line(0x94)
	_ = mh.read_line(0x14)
	_ = mh.read_line(0x48)
	_ = mh.read_line(0xC8)
	_ = mh.read_line(0x7C)
	_ = mh.read_line(0xAC)
	mh.cache.memdump()

	x = mh.read_byte(0xEA)
	print(hex(x)) # Should be 7
	mh.cache.memdump()



	print("\n\n\nTESTING WRITING!!!!")
	# Writing to memory test
	mh.write_byte(0x00, 0)
	mh.ram.memdump()
	mh.cache.memdump()

	# Perform two more reads to force cache
	_ = mh.read_line(0x10)
	mh.ram.memdump()
	_ = mh.read_line(0x20)
	mh.ram.memdump()
	mh.cache.memdump()
