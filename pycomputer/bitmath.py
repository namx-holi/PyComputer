
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


def set_bit(x, index):
	return (1<<index) | x


def clear_bit(x, index):
	return ~(1<<index) & x


def toggle_bit(x, index):
	return (1 << index) ^ x


def convert_trailing_to_one(x):
	return (x - 1) | x


def extract_least_significant_set_bit(x):
	return x & -x


def masked_copy(a, b, mask):
	# Copy bits from B into A where Mask = 1
	return (b & m) | (a & ~m)


def swap_bits(x, a, b):
	# Swap values in indices A and B
	p = ((x >> a) ^ (x >> b)) & 1 # represents need to swap
	if p == 0: return x # no swap needed
	return (x ^ (p << a)) ^ (p << b)


def count_set_bits(x):
	count = 0
	while x != 0:
		# Zero lowest set bit
		x = x & (x - 1)
		count += 1
	return count