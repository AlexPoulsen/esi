"""
>                            Extremely Simple Image file format                            <
>------------------------------------------------------------------------------------------<
> Designed for databending or glitching
> Has very little fancy features that could cause problems with decoding
> Decoder is designed to assume, without any penalties if it assumes wrong
> Width can be forced, or can be half of the length of the data, rounded up
> Color format is assumed to be 8 bit color
> Can support grayscale or color in a variety of bit depths
> There is no data between or around pixels, or at the end of the file
> It is literally a sequence of bits after the minimal header
> This should prevent any issues with databending
> Header is encoded with 16 bits for width for a maximum width of 65536 pixels, errors on 0
> All data is big-endian encoded
> This is followed by 6 bits for color depth which is followed by 42 ignored bits:
>     | 0
>     |  0000 1 bit black and white
>     |  #### 4 bits encoding bit depth, 1 indexed
>     -----------------------------------------
>     | 1
>     |  #### 4 bits encoding bit depth per channel, errors on 0
> Sample header:
>     | 01100101 01110011 01101001 00110001 ( esi1 in ascii binary )
>     | 00000000 00010000 10100000 00000000
>     | 00000000 00000000 00000000 00000000 ( 4 ignored bytes      )
>     -----------------------------------------
>     | 00000000
>     |          00010000 width of 16
>     |                   1 color
>     |                    01000 8 bit depth
>     |                         00 00000000 ignored bits
>     |                                   ( to ease databending the entire image )
>     |                                   (         without affecting the header )
> Flags
>     | -fw width ( chops to an int, will error on not a number )
>     | -g        ( guesses width )
"""

import sys
from PIL import Image
import math
import re
import struct
from bitstring import BitArray
import os


class ZeroSizeError(BaseException):
	pass


class OverByteError(BaseException):
	pass


def push(x: str):
	x = re.sub(' ', '', x)
	if len(x) > 8:
		raise OverByteError
	print(x)
	print(int(x, 2))
	esi.write(struct.pack('>1B', int(x, 2)))


def multipush(x: str):
	bound1 = 0
	bound2 = 8
	x = re.sub(' ', '', x)
	for n in range(int(math.floor((int(len(x))/8)))):
		push(x[bound1:bound2])
		bound1 += 8
		bound2 += 8


def big_endian16(x):
	if x == 0:
		raise ZeroSizeError
	return format(x, "016b")


def big_endian8(x):
	return format(x, "08b")


with open(sys.argv[1], "rb") as esi:
	# contents = esi.read()
	contents = BitArray(bytes=esi.read()).bin
	# print(contents)
	if contents[:32] == "01100101011100110110100100110001":
		print("Image is ESI")
	else:
		print("Header does not identify image as ESI")
	contents = contents[32:]
	width_bytes = contents[:16]
	contents = contents[16:]
	power = int(len(width_bytes))
	width = 0
	for bit in width_bytes:
		width += (2 ** power) * int(bit)
		power -= 1
	# print(width)
	contents = contents[48:]
	# print(contents)
	length = len(contents)
	custom_name = None
	try:
		if sys.argv[2] == "-fw":
			width = int(sys.argv[3])
			# print(width)
		elif sys.argv[2] == "-g":
			width = math.ceil(length / 24) * 24
		elif sys.argv[2] == "-n":
			custom_name = sys.argv[3]
	except IndexError:
		pass
	try:
		if sys.argv[3] == "-n":
			custom_name = sys.argv[4]
		elif sys.argv[4] == "-n":
			custom_name = sys.argv[5]
		elif sys.argv[3] == "-fw":
			width = int(sys.argv[4])
		elif sys.argv[4] == "-fw":
			width = int(sys.argv[5])
		elif sys.argv[4] == "-g":
			width = math.ceil(length / 24) * 24
	except IndexError:
		pass
	try:
		if sys.argv[5] == "-n":
			custom_name = sys.argv[6]
		elif sys.argv[6] == "-n":
			custom_name = sys.argv[7]
		elif sys.argv[5] == "-fw":
			width = int(sys.argv[6])
		elif sys.argv[6] == "-fw":
			width = int(sys.argv[7])
		elif sys.argv[6] == "-g":
			width = math.ceil(length / 24) * 24
	except IndexError:
		pass
	'''filename = str(str(sys.argv[1]).split("/")[-1:][0])
	path = "/".join(str(sys.argv[1]).split("/")[:-1]) + "/"
	create_file = str(filename.split(".")[:-1][0]) + ".png"
	if custom_name is not None:
		create_file = custom_name + ".png"
	if path != "/":
		new_file = path + create_file
	else:
		new_file = create_file'''
	path, file = os.path.split(sys.argv[1])
	if custom_name is not None:
		file = custom_name + ".png"
	else:
		file = str(file.split(".")[:-1][0]) + ".png"
	new_file = os.path.join(path, file)
	height = int(math.ceil(length / width / 12))
	width = int(math.ceil(width / 2))
	size = width, height
	print(size)
	im = Image.new("RGB", size)
	counter = 0
	total_amount = len(contents)
	done_amount = 0
	segment_value = total_amount / 8 / 80 / 3
	segments = [int(segment_value * n) for n in range(1, 81)]
	print("#", end="")
	print("-" * 78, end="")
	print("#")
	seg_counter = 0
	for x in range(height):
		for y in range(width):
			try:
				color_tuple = (int(contents[counter] + contents[counter + 1] + contents[counter + 2] + contents[counter + 3] + contents[counter + 4] + contents[counter + 5] + contents[counter + 6] + contents[counter + 7], 2), int(contents[counter + 8] + contents[counter + 9] + contents[counter + 10] + contents[counter + 11] + contents[counter + 12] + contents[counter + 13] + contents[counter + 14] + contents[counter + 15], 2), int(contents[counter + 16] + contents[counter + 17] + contents[counter + 18] + contents[counter + 19] + contents[counter + 20] + contents[counter + 21] + contents[counter + 22] + contents[counter + 23], 2))
			except IndexError:
				color_tuple = (0, 0, 0)
			done_amount += 1
			if int(done_amount) == segments[seg_counter]:
				seg_counter += 1
				print("#", end="", flush=True)
			im.putpixel((y, x), color_tuple)
			counter += 24
	print()
	im.save(new_file)
