# metaseg GUI
GUI for editing metaseg labels from ecSeg (https://github.com/UCRajkumar/ecSeg) output

ecSeg publication:
Rajkumar, U. et al. ecSeg: Semantic Segmentation of Metaphase Images containing Extrachromosomal DNA. iScience. 21, 428-435. (2019)

## Example screenshot
![alt text](https://github.com/yanglum/metaseg_gui/blob/main/screenshot.png)

## Instructions
Using the Anaconda distribution of python is recommended

2 options for setting up the environment using the Anaconda prompt, python v3.9.2

1) 	conda env create -f environment.yml

2) 	conda create --name msgui python=3.9.2
	
	  pip install -r requirements.txt
    
	  pip install opencv-python==4.5.3.56
  
Place metaseg_gui.py into the ecSeg directory (or the Example directory provided here) containing the config.yaml file and subdirectory containing the ecSeg inputs and outputs

# Helpful information

## Image acquisition
Open image: opens windows dialog box for selecting image to open, then opens another windows dialog box for selecting the mask (labels) file to open. If "Mass analysis" mode is checked, will open images (and corresponding masks) from "Image directory" (and "Mask directory") sequentially each time "Open image" is clicked. If there is an updated version of the mask (filename starts with "updated_", it will be preferentially loaded. Also loads the original image file in the working directory; if subdirectory "Original" exists, will load the image file in that subdirectory with the closest name to the current image file.

Save mask: save the current mask to the "Mask directory" as a .png file with "updated_" at the beginning of the file name. This will also update the "ec_quantification.csv" file produced by ecSeg with a new column "updated #" displaying the updated ecDNA count (this overrides the "Mark inadequate" button).

Mass analysis: check to enter mass analysis mode ("Open image" will open image files in "Image directory" sequentially).

Continue: if both "Mass analysis" and "Continue" are checked, "Open image" will open files in "Image directory" that do not have corresponding updated masks in "Mask directory".

Image directory: specify directory to image files for mass analysis mode.

Mask directory: specify directory to mask files for mass analysis mode.

## Show masks
Select masks (labels) to display from the mask file. The four labels from ecSeg ("background", "nuclei", "chromosome", "ecdna") are available. Additionally, a user defined "true background" label is available as well, which is colored black. Allows for multiple selections at the same time.

Hide all: hide all masks.

Mark inadequate: labels this image as "inadequate" (i.e. inadequately labeled) in the "ec_quantification.csv" file, under column "updated #".

## Toolbar
Allows manual label adjustment of the mask file

Flip from: select masks to be changed

Flip to: select what to change to

Polygon flip: draw vertices of a polygon encirling the part of the mask image to flip. Double click to finish polygon.

Reset polygon: restart drawing polygon

Undo: undo last change made to mask

Reset mask: reset mask to original

## Hot keys
Tab: open image

Hold left shift: display dapi image

Hold control: display original image

Right shift: save mask
