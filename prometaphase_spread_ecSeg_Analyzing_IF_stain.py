#!/usr/bin/env python
# coding: utf-8

# ### change log
# 24-08-20: add connected component analysis to count # of CCs for each stain within each ROI

# python 3.8.5, skimage 0.18.1
# env = cv2
# uses ROI_selector_config.yaml
# IMPORTANT: does not handle double digit channel numbers

import os
import pickle
from skimage import io, img_as_ubyte, measure, draw, morphology
import numpy as np
import pandas as pd
import cv2
from skimage.filters import threshold_multiotsu, threshold_otsu

import yaml

config = open("config.yaml")
var = yaml.load(config, Loader=yaml.FullLoader)['metaseg']
superpath = var['inpath']
channels = var['stains']

def analyze_stains(inpath, channels): 
	ecseg_path = os.path.join(inpath, 'labels')

	# make dictionaries

	master_path_dict = {} # dictionary of channels, each of which is a dictionary
	master_path_dict['ecseg_mask'] = {}
	for channel in channels:
		master_path_dict[channel] = {} # subdictionary containing image#: filename
		for file in os.listdir(os.path.join(inpath, channel)):
			master_path_dict[channel][file.split("_")[0]] = file # for file name access with imageno
	for file in os.listdir(ecseg_path):
		if 'updated_' in file: # only use updated masks
			master_path_dict['ecseg_mask'][file] = file.split("_")[1] # for imageno access
			
	analysis_dict = {
		'Image_no': [],
		'mask_file': [],
		'ecseg_chr_count': [],
		'ecseg_chr_pixel_count': [],
		'ecseg_ec_count': [],
		'ecseg_ec_pixel_count': [],
	}

	channel_list_dict = {}
	for channel in channels:
		channel_list_dict[channel+'_pixel_count'] = []
		channel_list_dict[channel+'_total_intensity'] = []
		channel_list_dict[channel+'_chr_pixel_count'] = []
		channel_list_dict[channel+'_chr_total_intensity'] = []
		channel_list_dict[channel+'_ec_pixel_count'] = []
		channel_list_dict[channel+'_ec_total_intensity'] = []

	# test
	test_path = os.path.join(inpath, channels[0], 'labels')
	test_list = os.listdir(test_path)
	test_mask = io.imread(os.path.join(test_path, test_list[0]))

	for file in master_path_dict['ecseg_mask'].keys():
		imageno = master_path_dict['ecseg_mask'][file]
		# append lists
		analysis_dict['Image_no'].append(imageno)
		analysis_dict['mask_file'].append(file)
		
		ecseg_mask = io.imread(os.path.join(ecseg_path, file))

		chr_mask = np.zeros(ecseg_mask.shape[:2], dtype=bool)
		ec_mask = np.zeros(ecseg_mask.shape[:2], dtype=bool)
		#chr_mask[np.all(ecseg_mask==[255, 255, 153], axis=2) | np.all(ecseg_mask==[127, 201, 127], axis=2)] = True # this is if ecseg mask is used
		chr_mask[np.all(ecseg_mask==[127, 201, 127], axis=2)] = True
		ec_mask[np.all(ecseg_mask==[240, 2, 127], axis=2)] = True
		
		ecseg_chr_pixel_count = np.count_nonzero(chr_mask)
		ecseg_ec_pixel_count = np.count_nonzero(ec_mask)
		
		analysis_dict['ecseg_chr_pixel_count'].append(ecseg_chr_pixel_count)				
		analysis_dict['ecseg_ec_pixel_count'].append(ecseg_ec_pixel_count)
		
		labeled_mask, chr_count = measure.label(chr_mask, connectivity=2, return_num=True)
		labeled_mask, ec_count = measure.label(ec_mask, connectivity=2, return_num=True)
		analysis_dict['ecseg_chr_count'].append(chr_count)				
		analysis_dict['ecseg_ec_count'].append(ec_count)
		
		## for each channel
		for channel in channels:

			# load image and mask (for given channel and imageno)
			img_path = os.path.join(inpath, channel, master_path_dict[channel][imageno])
			mask_path = os.path.join(inpath, channel, 'labels', master_path_dict[channel][imageno])
			image = io.imread(img_path)
			image = img_as_ubyte(image) # convert to uint8 from uint16 to avoid overflow
			stain_mask = io.imread(mask_path)
			stain_mask = stain_mask==255

			pixel_count = np.count_nonzero(stain_mask)
			total_intensity = sum(image[stain_mask])	
			
			chrstain_mask = stain_mask & chr_mask
			chr_channel_pixel_count = np.count_nonzero(chrstain_mask)
			chr_channel_total_intensity = sum(image[chr_mask])
			
			ecstain_mask = stain_mask & ec_mask
			ec_channel_pixel_count = np.count_nonzero(ecstain_mask)
			ec_channel_total_intensity = sum(image[ec_mask])				 

			# append channel lists
			channel_list_dict[channel+'_pixel_count'].append(pixel_count)
			channel_list_dict[channel+'_total_intensity'].append(total_intensity)				 
			channel_list_dict[channel+'_chr_pixel_count'].append(chr_channel_pixel_count)
			channel_list_dict[channel+'_chr_total_intensity'].append(chr_channel_total_intensity)
			channel_list_dict[channel+'_ec_pixel_count'].append(ec_channel_pixel_count)
			channel_list_dict[channel+'_ec_total_intensity'].append(ec_channel_total_intensity)				
			
		print('.', end='', flush=True)

	series1 = pd.DataFrame(analysis_dict)
	series2 = pd.DataFrame(channel_list_dict)
	df = pd.concat([series1, series2], axis=1)

	df.to_csv(os.path.join(inpath, 'ecseg_stain_analysis.csv'), index=False)
	print('CSV file saved to '+inpath, end='', flush=True)

print('initiating...', end='', flush=True)	
for dir in os.listdir(superpath):
	if os.path.isdir(os.path.join(superpath, dir)):
		inpath = os.path.join(superpath, dir)
		print('\nanalyzing stains ' + dir, end='', flush=True)
		analyze_stains(inpath, channels)
	else:
		print(dir+" is not a directory...skipping...")
print('done')
