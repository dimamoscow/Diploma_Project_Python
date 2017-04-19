#!/usr/bin/env python3
import sys

PNG_SIG_LENGTH = 8
LENGTH_DATA_FIELD = 4
LENGTH_CRC = 4
LENGTH_NAME = 4

PNG_SIG = [0x89, 0x50, 0x4e, 0x47, 0xd, 0xa, 0x1a, 0xa]

crctable_init = 0
crctable = []

"Dictionary for IHDR Chunk"
IHDR = {
	'Data Length' : 13,
	'Width' : '',
	'Height' : '',
	'Bit_depth' : '',
	'Color_type' : '',
	'Compression_method' : 0,
    'Filter method' : 0,
    'Interlace method' : '',
    'CRC:' : ''
}

"Dictionary for PLTE Chunk"
PLTE = {
	'Data Length' : '',
	'Red' : '',
	'Green' : '',
	'Blue' : '',
	'CRC:' : ''
}

"Dictionary for IDAT Chunk"
IDAT_LIST = []
IDAT = {
	'Data Length' : '',
	'Position': '',
	'Data' : '',
	'CRC':''
}

"Dictionary for IEND Chunk"
IEND = {
	'Data Length' : 0,
	'CRC' : ''
}

def make_crc_table():
	for i in range(0,256):
		c = i
		for j in range(0,8):
			if (c & 1) == False:
				c >>= 1
			else:
				c = 0xedb88320 ^ (c >> 1)
		crctable.append(c)
	crctable_init = 1
	return crctable_init

def crc32(buf):
	if crctable_init == 0:
		make_crc_table()

	crcreg = 0xffffffff
	for i in range(0,len(buf)):
		crcreg = crctable[(crcreg ^ buf[i]) & 0xff]\
		 ^ ((crcreg >> 8) & 0xffffffff)
	crc = ~crcreg & 0xffffffff
	return hex(crc)

def png_check(image_dump):
	for i in range(0, PNG_SIG_LENGTH):
		if bin(image_dump[i]) != bin(PNG_SIG[i]):
			return 0
	return 1

def read_data_IHDR(chunk_data, begin = 16):
	
	width = 0
	for i in range(begin, begin + 4):
		width = width << 8 | chunk_data[i]
	IHDR['Width'] = int(width)
	
	begin += 4
	heigt = 0
	for i in range(begin, begin + 4):
		heigt = heigt << 8 | chunk_data[i]	
	IHDR['Height'] = int(heigt)

	begin += 4
	IHDR['Bit_depth'] = int(chunk_data[begin])

	begin += 1
	IHDR['Color_type'] = int(chunk_data[begin])

	begin += 1
	if chunk_data[begin] or chunk_data[begin + 1] != 0:
		sys.exit('IHDR Error with CM and Filter')
	
	IHDR['Interlace method'] = int(chunk_data[begin + 2])

	print(IHDR)
	return IHDR

def read_data_PLTE(chunk_data, length_of_data = 3):

	if length_of_data != 3:
		sys.exit('PLTE Error')

	PLTE['Red'] = int(chunk_data[begin])
	PLTE['Green'] = int(chunk_data[begin + 1])
	PLTE['Blue'] = int(chunk_data[begin + 2])
	
	if PLTE['Red'] or PLTE['Green'] or PLTE['Blue'] < 0:
		sys.exit('PLTE Error')
	
	if PLTE['Red'] or PLTE['Green'] or PLTE['Blue'] > 255:
		sys.exit('PLTE Error')	
	
	print(PLTE)
	return PLTE

#def read_data_IDAT(chunk_data,)


def read_critical_chunks(image_dump, begin = PNG_SIG_LENGTH):
	
	if png_check(image_dump) == 0:
		print('This picture is not PNG!')
		sys.exit("ERROR!")
	else: 
		print('This is PNG picture!')

	chunk_number = 0
	name = ''
	PLTE_chunk = 0
	while name != 'IEND':
		chunk_number +=1

		length_of_data = 0
		for i in range(begin, begin + LENGTH_DATA_FIELD):
			length_of_data = length_of_data << 8 | image_dump[i]	

		begin += LENGTH_DATA_FIELD
		criticatl_reg = bin(image_dump[begin])
		
		if critical_reg[3] == 0:
			name = ''
			for i in range(begin, begin + LENGTH_NAME):
				name += chr(image_dump[i])

			crc_buf_start += begin 
			begin += LENGTH_NAME

			if name == 'IHDR':
				if chunk_number != 1 or int(length_of_data)!=13:
					sys.exit('IHDR Chunk error!')
				
				read_data_IHDR( picture_dump[begin - 1 : begin + int( length_of_data) -1], begin)
				crc_buf_end += crc_buf_start + begin + int( length_of_data)
				
				IHDR['CRC'] = crc32( picture_dump[ crc_buf - 1 : crc_buf_end - 1 ])

				begin += int(length_of_data)
				pic_crc = 0

				for i in range(begin, begin + LENGTH_CRC):
					pic_crc = pic_crc << 8 | image_dump[i]

				if IHDR['CRC'] != hex(pic_crc):
					sys.exit('IHDR Chunk error! Different CRC')

			elif name == 'PLTE':
				if IHDR['Color_type'] != 3:
					sys.exit('PNG Sig Error!')

				read_data_PLTE( picture_dump[begin - 1 : begin + int( length_of_data) -1], begin)
				crc_buf_end += crc_buf_start + begin + int( length_of_data)
				
				PLTE['CRC'] = crc32( picture_dump[ crc_buf - 1 : crc_buf_end - 1 ])

				begin += int(length_of_data)
				pic_crc = 0
				for i in range(begin, begin + LENGTH_CRC):
					pic_crc = pic_crc << 8 | image_dump[i]

				if PLTE['CRC'] != hex(pic_crc):
					sys.exit('PLTE Chunk error! Different CRC')
				PLTE_chunk = chunk_number

			elif name == 'IDAT':
				
			elif name == 'IEND':
				crc_buf_end += crc_buf_start + begin
				IEND['CRC'] = crc32( picture_dump[ crc_buf - 1 : crc_buf_end - 1 ])

				pic_crc = 0
				for i in range(begin, begin + LENGTH_CRC):
					pic_crc = pic_crc << 8 | image_dump[i]

				if IEND['CRC'] != hex(pic_crc):
					sys.exit('IEND Chunk error! Different CRC')									
		else:
			begin += LENGTH_NAME + int(length_of_data) + LENGTH_CRC		
	
	return 'All critical chunk succsessful reading'		


f = open('test3.png','rb')
picture_dump = []

for data in f:
	for i in data:
		picture_dump.append(i)
f.close()

print('Image hexdump:')
for i in picture_dump:
	print('{0:02x}'.format(i), end = ' ')