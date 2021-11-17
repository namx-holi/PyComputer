
def log2(x):
	# NOTE: Can be made faster via divide/conquer. e.g. shift 4 bits
	#  at a time until 0 is reached, then go back and look at the last
	#  4 bits. That means at most 16 shifts and 19 compares for a 64
	#  bit number, instead of 63.
	result = 0
	while (x >> 1):
		x = x >> 1
		result += 1
	return result