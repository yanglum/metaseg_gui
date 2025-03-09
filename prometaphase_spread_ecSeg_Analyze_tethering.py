#!/usr/bin/env python
# coding: utf-8

# In[186]:


#!/usr/bin/env python3
import pandas as pd
import numpy as np
from skimage import io, exposure, color, measure, morphology
import os
import yaml


# In[187]:


config = open("config.yaml")
var = yaml.load(config, Loader=yaml.FullLoader)['metaseg']
inpath = var['inpath']
mask_dir = os.path.join(inpath, 'labels')


# In[188]:


csv_file = pd.read_csv(os.path.join(inpath, 'ec_quantification.csv'))
mask_files = [x for x in os.listdir(mask_dir) if 'updated_' in x]


# In[191]:


for f in mask_files:
    mask = io.imread(os.path.join(mask_dir,f))

    filename = f[8:-4]+'.tif'
    if 'chromosome area' not in csv_file.columns:
        csv_file['chromosome area'] = [0]*len(csv_file['# of ec'])
    if 'tethered ec' not in csv_file.columns:
        csv_file['tethered ec'] = [0]*len(csv_file['# of ec'])
    if 'untethered ec' not in csv_file.columns:
        csv_file['untethered ec'] = [0]*len(csv_file['# of ec'])
    if 'trapped ec' not in csv_file.columns:
        csv_file['trapped ec'] = [0]*len(csv_file['# of ec'])

    #back_mask = np.full((mask.shape[0], mask.shape[1]), False)
    #nuclei_mask = np.full((mask.shape[0], mask.shape[1]), False)
    chromo_mask = np.full((mask.shape[0], mask.shape[1]), False)
    ecdna_mask = np.full((mask.shape[0], mask.shape[1]), False)

    #back_mask[np.where(np.all(mask==[56, 108, 176], axis=-1))] = True
    #nuclei_mask[np.where(np.all(mask==[255, 255, 153], axis=-1))] = True
    chromo_mask[np.where(np.all(mask==[127, 201, 127], axis=-1))] = True
    ecdna_mask[np.where(np.all(mask==[240, 2, 127], axis=-1))] = True

    simple_mask = np.zeros((mask.shape[0], mask.shape[1]), dtype=np.uint8)
    simple_mask[np.where(np.all(mask==[255, 255, 153], axis=-1))] = 1 # nuclei
    simple_mask[np.where(np.all(mask==[127, 201, 127], axis=-1))] = 2 # chromo
    simple_mask[np.where(np.all(mask==[240, 2, 127], axis=-1))] = 3 # ecdna

    # add total chromosome area
    csv_file.loc[csv_file['image name']==filename, 'chromosome area']=sum(sum(chromo_mask))

    # connected component analysis on ecDNA labels
    ecdna_cc, count = measure.label(ecdna_mask, connectivity=2, return_num=True)

    # loop through each ecDNA CC
    trapped_ecdna = 0 # ecDNA that are completely surrounded by chromosome pixels
    tethered_ecdna = 0 # ecDNA with at least 25% of border pixels touching chromosome pixels (but are not trapped)
    untethered_ecdna = 0 # ecDNA that only border background or nuclei
    tethered_cutoff = 0.25

    for i in range(1, count+1):
        current_ecdna = np.full((mask.shape[0], mask.shape[1]), False)
        current_ecdna[ecdna_cc==i]=True
        dilated_ecdna = morphology.dilation(current_ecdna)

        border_pixels = [x for x in simple_mask[dilated_ecdna] if x!=3]
        border_length = len(border_pixels)

        non_chr_border = [x for x in border_pixels if x!=2] # remove chrDNA pixels, leaving just background and nuc pixels
        if len(non_chr_border) == 0:
            trapped_ecdna += 1
            continue

        if len(non_chr_border) >= (1-tethered_cutoff)*border_length:
            untethered_ecdna += 1
        else:
            tethered_ecdna += 1

    csv_file.loc[csv_file['image name']==filename, 'tethered ec']=tethered_ecdna
    csv_file.loc[csv_file['image name']==filename, 'untethered ec']=untethered_ecdna
    csv_file.loc[csv_file['image name']==filename, 'trapped ec']=trapped_ecdna
    print('.')


# In[192]:


csv_file.to_csv(os.path.join(inpath, 'ec_quantification.csv'), index=False)
print(inpath+'/ec_quantification.csv updated')


# In[ ]:




