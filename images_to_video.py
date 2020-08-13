import cv2
import numpy as np
import glob
import os

def images_to_video(base_name: str):
    img_array = []
    root = os.getcwd()
    for filename in glob.glob(f'{base_name}*.jpg'):
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
