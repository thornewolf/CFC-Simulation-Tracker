import cv2
import numpy as np
import glob
import os
import logging

def images_to_video(base_name: str):
    logger = logging.getLogger(f'AutomateSims.images_to_video.{base_name}')
    img_array = []
    root = os.getcwd()
    matching_files = glob.glob(f'{base_name}*.jpg')
    logger.info(f'Found {len(matching_files)} files corresponding to {base_name}.\n e.g. {matching_files[:1]}')
    for filename in matching_files:
        print(filename)
        path = os.path.join(root,filename)
        img = cv2.imread(path)
        print(path)
        height, width, layers = img.shape
        size = (width,height)
        img_array.append(img)
    out = cv2.VideoWriter(f'{base_name}.avi',
        cv2.VideoWriter_fourcc(*'MJPG'),
        15,
        size)
    for i in range(len(img_array)):
        out.write(img_array[i])
    print(out)
    out.release()
