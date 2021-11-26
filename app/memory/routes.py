from flask import escape, render_template

from app import memory_handler
from app.memory import bp


@bp.route("/memory")
def memory_index():
	return escape(memory_handler.__repr__())

@bp.route("/memory/read/<address>")
def memory_read(address):
	try:
		address = int(address, 16)
	except ValueError:
		return "Invalid address"

	val = memory_handler.read_byte(address)
	return str(val)



@bp.route("/memory/ram")
def memory_ram():
	return escape(memory_handler.ram.__repr__())

@bp.route("/memory/ram/content")
def memory_ram_content():
	x = memory_handler.ram.dumps()
	return "<pre><code>" + x + "</code></pre>"



@bp.route("/memory/cache")
def memory_cache():
	return escape(memory_handler.cache.__repr__())

@bp.route("/memory/cache/content")
def memory_cache_content():
	x = memory_handler.cache.dumps()
	return "<pre><code>" + x + "</code></pre>"
