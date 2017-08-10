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
import numpy as np
import PIL as pil
from PIL import Image
import math
import re
import struct


class ZeroSizeError(BaseException):
	pass


class OverByteError(BaseException):
	pass


def push(x: str):
	x = re.sub(' ', '', x)
	if len(x) > 8:
		raise OverByteError
	# print(x)
	# print(int(x, 2))
	esi.write(struct.pack('<1B', int(x, 2)))


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


with Image.open(sys.argv[1]) as im:
	filename = str(str(sys.argv[1]).split("/")[-1:][0])
	path = "/".join(str(sys.argv[1]).split("/")[:-1]) + "/"
	create_file = str(filename.split(".")[:-1][0]) + ".esi"
	if path != "/":
		new_file = path + create_file
	else:
		new_file = create_file
	# print(new_file)
	with open(new_file, "xb") as esi:
		rgb_im = im.convert('RGB')
		input_data = list(rgb_im.getdata())
		# print(input_data)
		horiz, vert = rgb_im.size
		# output = np.full((horiz * vert * 3 + 12), 0, "uint8")
		multipush("01100101 01110011 01101001 00110001")
		# print(big_endian16(horiz))
		multipush(big_endian16(horiz))
		color = "1"  # color
		bit_depth = "01000"  # 8bit color since I can't find a way to get that from the input image
		multipush(color + bit_depth + "00 00000000")
		multipush("00000000 00000000 00000000 00000000")
		horiz_at = vert_at = 0
		# print("loop")
		for value in input_data:
			multipush(big_endian8(value[0]) + big_endian8(value[1]) + big_endian8(value[2]))
			if horiz_at >= horiz:
				horiz_at = 0
				vert_at += 1
