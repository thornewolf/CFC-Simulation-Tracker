import cv2
import numpy as np
import glob
import os
import logging

def images_to_video(base_name: str):
    '''
    Takes a set of images generated by the visualization code to make a video
    in .avi format. Saves to current working directory.
    
    Args:
        base_name: the base name of the run that was used to generate the images originally.

    Returns:
        None:
    '''
    logger = logging.getLogger(f'AutomateSims.images_to_video.{base_name}')
    img_array = []
    root = os.getcwd()
    for part in ['A', 'B', 'C']:
      matching_files = glob.glob(f'{base_name}*{part}.jpg')
      logger.info(f'Found {len(matching_files)} files corresponding to {base_name}.\n e.g. {matching_files[:1]}')
      matching_file_numbers = [int(f.split('_')[-2]) for f in matching_files]
      ordered_files = sorted(zip(matching_file_numbers, matching_files))
      if len(ordered_files) == 0:
        logger.info(f'Could not find any files matching {base_name} for part {part} of image generation. Perhaps the image generation failed?')
        continue
      for i,filename in ordered_files:
        print(i, filename)
        path = os.path.join(root,filename)
        img = cv2.imread(path)
        print(path)
        height, width, layers = img.shape
        size = (width,height)
        img_array.append(img)
      out = cv2.VideoWriter(f'{base_name}_{part}.avi',
      cv2.VideoWriter_fourcc(*'MJPG'),
        15,
        size)
      for i in range(len(img_array)):
        out.write(img_array[i])
      print(out)
      out.release()

def main():
  base_name = "Run1_JetA0p001_JetF0p007"
  images_to_video(base_name)

if __name__ == '__main__':
  main()
