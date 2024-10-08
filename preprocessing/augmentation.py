import os
import sys

import Augmentor
import cv2
import numpy as np
import pandas as pd
from PIL import Image

from dataset_formatting import preprocess_dataset


def save_image_from_row(row, index):
    emotion = row['emotion']
    pixels = row['pixels']

    pixel_array = np.array([int(p) for p in pixels.split()]).reshape(48, 48)
    pixel_array = pixel_array.astype(np.uint8)
    img = Image.fromarray(pixel_array)
    # we must include the index of the image to create a unique name in the folder
    img_filename = os.path.join('../datasets/orig_images', f"{emotion}_emotion_{index}.jpg")
    img.save(img_filename)

def create_set_from_jpg_dir(directory_path):

    images = list()

    for image in os.listdir(directory_path):
        splitstr = image.split('_')
        emotion = splitstr[3] if len(splitstr) > 4 else splitstr[0]
        img = cv2.imread(os.path.join(directory_path, image), cv2.IMREAD_GRAYSCALE)
        images.append([emotion, img])

    return images


if __name__ == '__main__':
    read_pixels = pd.read_csv('../datasets/train.csv')
    if not os.path.exists('../datasets/orig_images') or not os.path.exists('../datasets/aug_images'):
        if not os.path.exists('../datasets/orig_images'):
            os.makedirs('../datasets/orig_images')
        if not os.path.exists('../datasets/aug_images'):
            os.makedirs('../datasets/aug_images')

        for index, row in read_pixels.iterrows():
            save_image_from_row(row, index)

        p = Augmentor.Pipeline(source_directory='orig_images', output_directory='aug_images')
        p.rotate(probability=0.2, max_left_rotation=25, max_right_rotation=25)
        p.skew(probability=0.2, magnitude=0.2)
        p.zoom_random(probability=0.3, percentage_area=0.8)
        p.gaussian_distortion(
            probability=0.2,
            grid_width=4,
            grid_height=4,
            magnitude=8,
            corner="bell",
            method="in"
        )
        p.random_erasing(probability=0.1, rectangle_area=0.2)
        p.sample(10000)
        print('Images have sucessfully been augumented.', file=sys.stderr)
    else:
        print("Images are probably already augmented, if not, delete both directories: aug_images and orig_images"
              " if present", file=sys.stderr)

    augmented_images_path = '../datasets/aug_images'
    train_set_images_path = '../datasets/orig_images'
    train_dataset_csv_path = '../datasets/train_augmented.csv'

    res = create_set_from_jpg_dir(augmented_images_path) + create_set_from_jpg_dir(train_set_images_path)
    df = pd.DataFrame(res, columns=['emotion', 'pixels'])
    df = preprocess_dataset(df)
    df.to_csv(path_or_buf=train_dataset_csv_path, index=False)

