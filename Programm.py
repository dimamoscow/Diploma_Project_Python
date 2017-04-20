#!/usr/bin/env python3
import sys

PNG_SIG_LENGTH = 8
LENGTH_DATA_FIELD = 4
LENGTH_CRC = 4
LENGTH_NAME = 4

PNG_SIG = [0x89, 0x50, 0x4e, 0x47, 0xd, 0xa, 0x1a, 0xa]

crctable_init = 0
crctable = []
compress_data = 0

chunk_number = 0
PLTE_chunk = 0
crc_buf_start = 0
crc_buf_end = 0

name = ''
index = PNG_SIG_LENGTH

IHDR = {
	'Width' : '',
	'Height' : '',
	'Bit_depth' : '',
	'Color_type' : '',
	'Compression_method' : 0,
    'Filter method' : 0,
    'Interlace method' : '',
    'CRC' : ''
}

PLTE = {
	'Red' : '',
	'Green' : '',
	'Blue' : '',
	'CRC:' : ''
}

IDAT_LIST = []
IDAT = {
	'Position': '',
	'Data' : '',
	'CRC':''
}

IEND = {
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

def read_data_IHDR(chunk_data, index = 16):
	
	width = 0
	for i in range(index, index + 4):
		width = width << 8 | chunk_data[i]
	
	IHDR['Width'] = int(width)
	
	index += 4
	heigt = 0
	for i in range(index, index + 4):
		heigt = heigt << 8 | chunk_data[i]	
	IHDR['Height'] = int(heigt)

	index += 4
	IHDR['Bit_depth'] = int(chunk_data[index])

	index += 1
	IHDR['Color_type'] = int(chunk_data[index])

	index += 1
	if chunk_data[index] or chunk_data[index + 1] != 0:
		sys.exit('IHDR Error with CM and Filter')
	
	IHDR['Interlace method'] = int(chunk_data[index + 2])

	return IHDR

def read_data_PLTE(chunk_data):

	if length_of_data != 3:
		sys.exit('PLTE Error')

	PLTE['Red'] = int(chunk_data[index])
	PLTE['Green'] = int(chunk_data[index + 1])
	PLTE['Blue'] = int(chunk_data[index + 2])
	
	if PLTE['Red'] or PLTE['Green'] or PLTE['Blue'] < 0:
		sys.exit('PLTE Error')
	
	if PLTE['Red'] or PLTE['Green'] or PLTE['Blue'] > 255:
		sys.exit('PLTE Error')	
	
	return PLTE

def read_data_IDAT(chunk_data):
	global compress_data
	for i in range(len(chunk_data)):
		compress_data = compress_data << 8 | chunk_data[i]
	IDAT['Data'] = compress_data
	return compress_data	

f = open('test3.png','rb')
picture_dump = []

for data in f:
	for i in data:
		picture_dump.append(i)
f.close()

print('Image hexdump:')
for i in picture_dump:
	print('{0:02x}'.format(i), end = ' ')

if png_check(picture_dump) == 0:
	print('This picture is not PNG!')
	sys.exit("ERROR!")
else: 
	print('\nThis is PNG picture!')

while name != 'IEND':
	chunk_number +=1

	length_of_data = 0

	print("Начало чанка :{}".format(index))


	for i in range(index, index + LENGTH_DATA_FIELD):
		print(hex(picture_dump[i]))
		length_of_data = length_of_data << 8 | picture_dump[i]	

	print("Длина данных: {}".format(int(length_of_data)))
	print("Начало имени: {}".format(index + LENGTH_DATA_FIELD))
	
	index += LENGTH_DATA_FIELD
	critical_reg = bin(picture_dump[index])

	print(critical_reg[3])

	if critical_reg[3] == '0':
		name = ''
		
		for i in range(index, index + LENGTH_NAME):
			name += chr(picture_dump[i])
		print(name)

		crc_buf_start = index 
		index += LENGTH_NAME

		if name == 'IHDR':
			if chunk_number != 1 or int(length_of_data)!=13:
				sys.exit('IHDR Chunk error!')
			
			read_data_IHDR( picture_dump, index)

			crc_buf_end = index + int( length_of_data)
			
			print('Index crc start {}, index crc end {}'.format(crc_buf_start,crc_buf_end))
			IHDR['CRC'] = crc32( picture_dump[crc_buf_start : crc_buf_end])

			index += int(length_of_data)
			pic_crc = 0

			for i in range(index, index + LENGTH_CRC):
				pic_crc = pic_crc << 8 | picture_dump[i]

			index += LENGTH_CRC
			print('skdjf {}'.format(index))
			if IHDR['CRC'] != hex(pic_crc):
				sys.exit('IHDR Chunk error! Different CRC')

			print(IHDR)
			print('Чанк распознан!\n')

		elif name == 'PLTE':
			if IHDR['Color_type'] != 3:
				sys.exit('PNG Sig Error!')

			read_data_PLTE(picture_dump[index:index + int(length_of_data)])
			crc_buf_end = index + int(length_of_data)
				
			PLTE['CRC'] = crc32( picture_dump[crc_buf_start : crc_buf_end])

			index += int(length_of_data)
			
			pic_crc = 0
			for i in range(index, index + LENGTH_CRC):
				pic_crc = pic_crc << 8 | picture_dump[i]

			if PLTE['CRC'] != hex(pic_crc):
				sys.exit('PLTE Chunk error! Different CRC')
			index += LENGTH_CRC
		
		elif name == 'IDAT':
			
			read_data_IDAT(picture_dump[index:index + int(length_of_data)])
			
			crc_buf_end = index + int(length_of_data)
			print(index)
			print('Index crc start {}, index crc end {}'.format(crc_buf_start,crc_buf_end))
			IDAT['CRC'] = crc32( picture_dump[crc_buf_start : crc_buf_end])

			index += int(length_of_data)

			pic_crc = 0
			for i in range(index, index + LENGTH_CRC):
				pic_crc = pic_crc << 8 | picture_dump[i]

			if IDAT['CRC'] != hex(pic_crc):
				sys.exit('PLTE Chunk error! Different CRC')
			index += LENGTH_CRC

			print(IDAT)	
			print('Чанк распознан! \n')


		elif name == 'IEND':
			crc_buf_end = index + int(length_of_data)
			print('Index crc start {}, index crc end {}'.format(crc_buf_start,crc_buf_end))
			
			IEND['CRC'] = crc32( picture_dump[crc_buf_start : crc_buf_end])

			pic_crc = 0
			for i in range(index, index + LENGTH_CRC):
				pic_crc = pic_crc << 8 | picture_dump[i]

			if IEND['CRC'] != hex(pic_crc):
				sys.exit('IEND Chunk error! Different CRC')	

			print(IEND)	
			print('Чанк распознан!\n')							
	else:
		index += LENGTH_NAME + int(length_of_data) + LENGTH_CRC		