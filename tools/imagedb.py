#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 15 19:09:40 2018

@author: wujiyang
"""

import os
import numpy as np


class ImageDB(object):
    def __init__(self, image_annotation_file, prefix_path="", mode="train"):
        self.prefix_path = prefix_path
        self.image_annotation_file = image_annotation_file
        self.classes = ["__background__", "face"]
        self.num_classes = 2
        self.image_set_index = self.load_image_set_index()
        self.num_images = len(self.image_set_index)
        self.mode = mode

    def load_image_set_index(self):
        """Get image index

        Returns:
            image_set_index: str, relative path of image
        """
        assert os.path.exists(
            self.image_annotation_file
        ), "Path does not exist: {}".format(self.image_annotation_file)
        with open(self.image_annotation_file, "r") as f:
            image_set_index = [x.strip().split(" ")[0] for x in f.readlines()]
        return image_set_index

    def load_imdb(self):
        """Get and save ground truth image database

        Returns:
            gt_imdb: dict, image database with annotations
        """

        gt_imdb = self.load_annotations()

        return gt_imdb

    def real_image_path(self, index):
        """Given image's relative index, return full path of image"""

        index = index.replace("\\", "/")

        if not os.path.exists(index):
            image_file = os.path.join(self.prefix_path, index)
        else:
            image_file = index
        if not image_file.endswith(".jpg"):
            image_file = image_file + ".jpg"
        assert os.path.exists(image_file), "Path does not exist: {}".format(image_file)

        return image_file

    def load_annotations(self, annotation_type=1):
        """Load annotations

        what's the meaning of annotation_type ? I don't know !
        Returns:
            imdb: dict, image database with annotations
        """

        assert os.path.exists(
            self.image_annotation_file
        ), "annotations not found at {}".format(self.image_annotation_file)
        with open(self.image_annotation_file, "r") as f:
            annotations = f.readlines()

        imdb = []
        for i in range(self.num_images):
            annotation = annotations[i].strip().split(" ")
            index = annotation[0]
            im_path = self.real_image_path(index)
            imdb_ = dict()
            imdb_["image"] = im_path

            if self.mode == "test":
                pass
            else:
                label = annotation[1]
                imdb_["label"] = int(label)
                imdb_["flipped"] = False
                imdb_["bbox_target"] = np.zeros((4,))
                imdb_["landmark_target"] = np.zeros((10,))
                if len(annotation[2:]) == 4:
                    bbox_target = annotation[2:6]
                    imdb_["bbox_target"] = np.array(bbox_target).astype(float)
                if len(annotation[2:]) == 14:
                    bbox_target = annotation[2:6]
                    imdb_["bbox_target"] = np.array(bbox_target).astype(float)
                    landmark = annotation[6:]
                    imdb_["landmark_target"] = np.array(landmark).astype(float)
            imdb.append(imdb_)
        return imdb

    def append_flipped_images(self, imdb):
        """append flipped images to imdb

        Returns:
            imdb: dict, image database with flipped image annotations
        """
        print(f"append flipped images to imdb {len(imdb)}")
        for i in range(len(imdb)):
            imdb_ = imdb[i]
            m_bbox = imdb_["bbox_target"].copy()
            m_bbox[0], m_bbox[2] = -m_bbox[2], -m_bbox[0]

            landmark_ = imdb_["landmark_target"].copy()
            landmark_ = landmark_.reshape((5, 2))
            landmark_ = np.asarray([(1 - x, y) for (x, y) in landmark_])
            landmark_[[0, 1]] = landmark_[[1, 0]]
            landmark_[[3, 4]] = landmark_[[4, 3]]

            item = {
                "image": imdb_["image"],
                "label": imdb_["label"],
                "bbox_target": m_bbox,
                "landmark_target": landmark_.reshape((10)),
                "flipped": True,
            }

            imdb.append(item)
        self.image_set_index *= 2
        print(f"after flipped images appended to imdb {len(imdb)}")

        return imdb