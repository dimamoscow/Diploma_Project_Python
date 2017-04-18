#!/usr/bin/env python3
import sys

PNG_SIG_LENGTH = 8
LENGTH_DATA_FIELD = 4
LENGTH_CRC = 4
LENGTH_NAME = 4

PNG_SIG = [0x89, 0x50, 0x4e, 0x47, 0xd, 0xa, 0x1a, 0xa]

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
IDAT = {
	'Data Length' : '',
	'Position': '',
	'Data' : '',
	'CRC':''
}

"Dictionary for IEND Chunk"
IEND = {
	'Data Length' : 0,
	'CRC' : [0xae, 0x42,  0x60, 0x82]
}

'''Open my png picture '''
f = open('test3.png','rb')
picture_dump = []

'''Read bytes in png picture'''
for data in f:
	for i in data:
		picture_dump.append(i)
f.close()

'''Print PNG hexdump'''
print('Image hexdump:')
for i in picture_dump:
	print('{0:02x}'.format(i), end = ' ')

'''Check this picture PNG or not'''
def png_check(image_dump):
	'''
	Check, this picture PNG or not
	'''
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
	else:
		IHDR['Interlace method'] = int(chunk_data[begin + 2])

	print(IHDR)
	return IHDR

def read_data_PLTE(chunk_data, length_of_data = 3):

	if length_of_data != 3:
		sys.exit('PLTE Error')
	elif int(chunk_data[begin]) and int(chunk_data[begin + 1]) and int(chunk_data[begin + 2]) < 256:
		PLTE['Red'] = int(chunk_data[begin])
		PLTE['Green'] = int(chunk_data[begin + 1])
		PLTE['Blue'] = int(chunk_data[begin + 2])
	else:
		sys.exit('PLTE Error')
		
	print(PLTE)
	return PLTE


def read_critical_chunks(image_dump, begin = PNG_SIG_LENGTH):
	
	if png_check(image_dump) == 0:
		print('This picture is not PNG!')
		sys.exit("ERROR!")
	else: 
		print('This is PNG picture!')

	name = ''
	chunk_pos = 0
	
	while name != 'IEND':
		chunk_pos +=1

		for i in range(begin, begin + LENGTH_DATA_FIELD):
			length_of_data = length_of_data << 8 | image_dump[i]	

		begin += LENGTH_DATA_FIELD
		criticatl_reg = bin(image_dump[begin])
		
		if critical_reg[3] == 0:
			
			for i in range(begin, begin + LENGTH_NAME):
				name += chr(image_dump[i])

			begin +=LENGTH_NAME

			if name == 'IHDR':
				if chunk_pos != 1 or int(length_of_data)!=13:
					sys.exit('IHDR Chunk error!')
				else:
					read_data_IHDR(picture_dump[begin, begin + int(length_of_data)], begin)
					"Добавить сюда проверку CRC"
					begin += int(length_of_data) + LENGTH_CRC

					if IHDR['Color_type'] == 3:
						chunk_pos +=1
						for i in range(begin, begin + LENGTH_DATA_FIELD):
							length_of_data = length_of_data << 8 | image_dump[i]
						begin += LENGTH_DATA_FIELD
						
						for i in range(begin, begin + LENGTH_NAME):
							name += chr(image_dump[i])
						begin +=LENGTH_NAME
						"Добавить сюда проверку на имя"	
						read_data_PLTE(picture_dump[begin, begin + int(length_of_data)], int(length_of_data))
						"Добавить сюда проверку CRC"
						begin += int(length_of_data) + LENGTH_CRC
					else:
						pass
			elif name = 'IDAT':
					
					

		else		
			begin += LENGTH_NAME + int(length_of_data) + LENGTH_CRC


	

begin += 4
critical_reg = bin(chunk_data[begin])

print(chr(0x49))

image_dump = [0x49, 0x48, 0x44, 0x52]
length_of_data = 0
name = ''
for i in range(0, 4):
	name += chr(image_dump[i])
print(name)
