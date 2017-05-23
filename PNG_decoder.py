#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import os
import time
import zlib

if __name__ != "__main__":
	sys.exit(1)

PNG_SIG_LENGTH = 8
LENGTH_DATA_FIELD = 4
LENGTH_CRC = 4
LENGTH_NAME = 4
index = PNG_SIG_LENGTH

crctable_init = 0
crctable = []
compress_data = 0

chunk_number = 0
PLTE_chunk = 0
crc_buf_start = 0
crc_buf_end = 0
name = ''
buf_compress_data = []

PNG_SIG = [0x89, 0x50, 0x4e, 0x47, 0xd, 0xa, 0x1a, 0xa]

IHDR = {
	'Length' : 13,
	'Width' : '',
	'Height' : '',
	'Bit_depth' : '',
	'Color_type' : '',
	'Compression_method' : 0,
	'Filter_method' : 0,
	'Interlace_method' : '',
	'CRC' : ''
}

PLTE = {
	'Length' : 0,
	'Data' : [],
	'CRC:' : ''
}

def print_critical_chunk_struct(name_of_chunk):
	if name_of_chunk == IHDR:
		print('\nIHDR recongnizer!\nIHDR info:')
		print('\tData length: {}'.format(IHDR['Length']))
		print('\tWidth: {0}'.format(IHDR['Width']))
		print('\tHeight: {0}'.format(IHDR['Height']))
		print('\tBit depth : {0}'.format(IHDR['Bit_depth']))
		
		if int(IHDR['Color_type']) == 0:
			print('\tColor type : {0}(Greyscale)'.format(IHDR['Color_type']))
		elif int(IHDR['Color_type']) == 2:
			print('\tColor type : {0}(Truecolour)'.format(IHDR['Color_type']))
		elif int(IHDR['Color_type']) == 3:
			print('\tColor type : {0}(Indexed-color)'.format(IHDR['Color_type']))
		elif int(IHDR['Color_type']) == 4:
			print('\tColor type : {0}(Greyscale with alpha)'.format(IHDR['Color_type']))
		elif int(IHDR['Color_type']) == 6:
			print('\tColor type : {0}(Truecolour with alpha)'.format(IHDR['Color_type']))
		
		print('\tCompression method: {0}(deflate/inflate compression with a sliding window)'\
			.format(IHDR['Compression_method']))
		print('\tFilter method: {}(adaptive filtering)'.format(IHDR['Filter_method']))

		if int(IHDR['Interlace_method']) == 0:
			print('\tInterlace_method: 0(no interlace)')
		elif int(IHDR['Interlace_method']) == 1:
			print('\tInterlace_method: 0(Adam7 interlace)')
		else:
			sys.exit('IHDR Error! Unknown interlace')

		print('CRC: {0:X}'.format(IHDR['CRC']))
	elif name_of_chunk == PLTE:
		print('\nPLTE recongnizer!\nPLTE info:')
		print('\tData length: {}'.format(PLTE['Length']))
		print('\tPixel data:')
		for li in PLTE['Data']:
			print('\t\t{}'.format(li))
		print('CRC: {0:X}'.format(PLTE['CRC']))

	elif name_of_chunk == 'IDAT':
		print('\nIDAT recognizer!\nIDAT info:')
		print('\tLenght: {}'.format(length_of_data))
		print('CRC: {0:X}'.format(CRC))

	elif name_of_chunk == 'IEND':
		print('\nIEND Recongnizer!\nIEND info:')
		print('\tData length: {}'.format(iend_len))
		print('CRC: {0:X}'.format(CRC))

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
	return crc

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
	
	IHDR['Interlace_method'] = int(chunk_data[index + 2])

	return IHDR

def read_data_PLTE(chunk_data):
	PLTE['Length'] = len(chunk_data)
	if length_of_data % 3 != 0:
		sys.exit('PLTE error! Data not multiples of 3')

	for i in range(0,length_of_data,3):
		if int(chunk_data[i]) and int(chunk_data[i]) and int(chunk_data[i]) < 0:
			sys.exit('PLTE error! Incorrect pixel data')
		if int(chunk_data[i]) and int(chunk_data[i]) and int(chunk_data[i]) > 255:
			sys.exit('PLTE error! Incorrect pixel data')
		
		PLTE['Data'].append(chunk_data[i:i+3])
	return PLTE

def read_data_IDAT(chunk_data):

	global buf_compress_data
	buf_compress_data.extend(chunk_data)
	compress_data = chunk_data[0]
	for i in range(1,len(chunk_data)):
		compress_data = compress_data << 8 | chunk_data[i]
	return compress_data	

if len(sys.argv) < 3:
	sys.exit('ERROR! Too few parametrs')
elif len(sys.argv) > 3:
	sys.exit('ERROR! So many parametrs')

InputFile = open(sys.argv[1],'rb')
picture_dump = []

for data in InputFile:
	for i in data:
		picture_dump.append(i)
InputFile.close()

for i in range(0, PNG_SIG_LENGTH):
	if bin(picture_dump[i]) != bin(PNG_SIG[i]):
		sys.exit('This is not PNG format!')
print('This is picture {} is PNG'.format(sys.argv[1]))

while name != 'IEND':
	chunk_number += 1
	length_of_data = 0

	for i in range(index, index + LENGTH_DATA_FIELD):
		length_of_data = length_of_data << 8 | picture_dump[i]	

	index += LENGTH_DATA_FIELD
	critical_reg = bin(picture_dump[index])

	if critical_reg[3] == '0':
		name = ''
		
		for i in range(index, index + LENGTH_NAME):
			name += chr(picture_dump[i])
		
		crc_buf_start = index 
		index += LENGTH_NAME

		if name == 'IHDR':
			if chunk_number != 1 or int(length_of_data)!=13:
				sys.exit('IHDR Chunk error!')
			read_data_IHDR( picture_dump, index)
			crc_buf_end = index + int( length_of_data)
			IHDR['CRC'] = crc32( picture_dump[crc_buf_start : crc_buf_end])
			index += int(length_of_data)
			pic_crc = 0
			for i in range(index, index + LENGTH_CRC):
				pic_crc = pic_crc << 8 | picture_dump[i]

			index += LENGTH_CRC
			if IHDR['CRC'] != pic_crc:
				sys.exit('IHDR Chunk error! Different CRC')
			print_critical_chunk_struct(IHDR)

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
			
			index += LENGTH_CRC	
			if PLTE['CRC'] != pic_crc:
				sys.exit('PLTE Chunk error! Different CRC')
			
			print_critical_chunk_struct(PLTE)
		
		elif name == 'IDAT':
			
			read_data_IDAT(picture_dump[index:index + int(length_of_data)])
			crc_buf_end = index + int(length_of_data)
			CRC = crc32(picture_dump[crc_buf_start : crc_buf_end])
			index += int(length_of_data)
			pic_crc = 0
			for i in range(index, index + LENGTH_CRC):
				pic_crc = pic_crc << 8 | picture_dump[i]

			if CRC != pic_crc:
				sys.exit('IDAT Chunk error! Different CRC')
			index += LENGTH_CRC
			print_critical_chunk_struct('IDAT')
			
		elif name == 'IEND':
			iend_len = 0
			crc_buf_end = index + int(length_of_data)
			CRC = crc32( picture_dump[crc_buf_start : crc_buf_end])
			pic_crc = 0
			for i in range(index, index + LENGTH_CRC):
				pic_crc = pic_crc << 8 | picture_dump[i]

			if CRC != pic_crc:
				sys.exit('IEND Chunk error! Different CRC')	
			print_critical_chunk_struct('IEND')							
	else:
		index += LENGTH_NAME + int(length_of_data) + LENGTH_CRC		

length_idat = len(buf_compress_data)
cd = 0
for i in buf_compress_data:
	cd = cd << 8 | i

cd = cd.to_bytes(length_idat, byteorder = 'big')

decompressor = zlib.decompressobj()
DecomressData = decompressor.decompress(cd)
CompressData = zlib.compress(DecomressData, 9)
length_idat = len(CompressData)

OutFile = open(sys.argv[2], 'wb')
png = b''
crccheck = b''

for i in range(len(PNG_SIG)):
	png += PNG_SIG[i].to_bytes(1, byteorder = 'big')
 
png += IHDR['Length'].to_bytes(4, byteorder = 'big')
png += bytes('I' + 'H' + 'D' + 'R', encoding = 'utf-8')
png += IHDR['Width'].to_bytes(4, byteorder = 'big')
png += IHDR['Height'].to_bytes(4, byteorder = 'big')
png += IHDR['Bit_depth'].to_bytes(1, byteorder = 'big')
png += IHDR['Color_type'].to_bytes(1, byteorder = 'big')
png += IHDR['Compression_method'].to_bytes(1, byteorder = 'big')
png += IHDR['Filter_method'].to_bytes(1, byteorder = 'big')
png += IHDR['Interlace_method'].to_bytes(1, byteorder = 'big')
png += IHDR['CRC'].to_bytes(4, byteorder = 'big')

if IHDR['Color_type'] == 3:
	png += PLTE['Length'].to_bytes(4, byteorder = 'big')
	png += bytes('P' + 'L' + 'T' + 'E', encoding = 'utf-8')
	for li in PLTE['Data']:
		for i in li:
			png += i.to_bytes(1, byteorder = 'big')
	png += PLTE['CRC'].to_bytes(4, byteorder = 'big')

index = 0
length_idat = len(CompressData)
max_len = 32768

while length_idat > max_len:

	png += max_len.to_bytes(4, byteorder = 'big')

	for sym in 'IDAT':
		png += bytes(sym, encoding = 'utf-8')
	crccheck += bytes('I' + 'D' + 'A' + 'T', encoding = 'utf-8')
	crccheck += CompressData[index : index + max_len]
	png += CompressData[index : index + max_len]
	png += crc32(crccheck).to_bytes(4, byteorder = 'big')
	index += max_len
	crccheck =b''
	length_idat -= max_len

png += length_idat.to_bytes(4, byteorder = 'big')
for sym in 'IDAT':
	png += bytes(sym, encoding = 'utf-8')
crccheck += bytes('I' + 'D' + 'A' + 'T', encoding = 'utf-8')
crccheck += CompressData[index:]
png += CompressData[index:]
png += crc32(crccheck).to_bytes(4, byteorder = 'big')

png += iend_len.to_bytes(4, byteorder = 'big')
png += bytes('I' + 'E' + 'N' + 'D', encoding = 'utf-8')
png += CRC.to_bytes(4, byteorder = 'big')

OutFile.write(png)
OutFile.close()