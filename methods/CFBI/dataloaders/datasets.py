from __future__ import division
import json
import os
import shutil
import numpy as np
import torch, cv2
from random import choice
from torch.utils.data import Dataset
import json
from PIL import Image
import random
from utils.image import _palette

class _EVAL_TEST(Dataset):
    def __init__(self, transform, seq_name):
        self.seq_name = seq_name
        self.num_frame = 10
        self.transform = transform

    def __len__(self):
        return self.num_frame

    def __getitem__(self, idx):
        current_frame_obj_num = 2
        height = 400
        width = 400
        img_name = 'test{}.jpg'.format(idx)
        current_img = np.zeros((height, width, 3)).astype(np.float32)
        if idx == 0:
            current_label = (current_frame_obj_num * np.ones((height, width))).astype(np.uint8)
            sample = {'current_img':current_img, 'current_label':current_label}
        else:
            sample = {'current_img':current_img}

        sample['meta'] = {'seq_name':self.seq_name, 'frame_num':self.num_frame, 'obj_num':current_frame_obj_num,
                          'current_name':img_name, 'height':height, 'width':width, 'flip':False}

        if self.transform is not None:
            sample = self.transform(sample)
        return sample
    
class EVAL_TEST(object):
    def __init__(self, transform=None, result_root=None):
        self.transform = transform
        self.result_root = result_root

        self.seqs = ['test1', 'test2', 'test3']

    def __len__(self):
        return len(self.seqs)

    def __getitem__(self, idx):
        seq_name = self.seqs[idx]

        if not os.path.exists(os.path.join(self.result_root, seq_name)):
            os.makedirs(os.path.join(self.result_root, seq_name))

        seq_dataset = _EVAL_TEST(self.transform, seq_name)
        return seq_dataset

class VOS_Test(Dataset):
    def __init__(self, image_root, label_root, seq_name, images, labels, rgb=False, transform=None, single_obj=False):
        self.image_root = image_root
        self.label_root = label_root
        self.seq_name = seq_name
        self.images = images
        self.labels = labels
        self.obj_num = 1
        self.num_frame = len(self.images)
        self.transform = transform
        self.rgb = rgb
        self.single_obj = single_obj

        self.obj_nums = []
        temp_obj_num = 0
        for img_name in self.images:
            self.obj_nums.append(temp_obj_num)
            current_label_name = img_name.split('.')[0] + '.png'
            if current_label_name in self.labels:
                current_label = self.read_label(current_label_name)

                # print("current_label:" , current_label.shape)
                # print("current_label:" , np.unique(current_label) )
                if temp_obj_num < np.unique(current_label)[-1]:
                    temp_obj_num = np.unique(current_label)[-1]
                    # print(np.unique(current_label))
                    # print("temp_obj_num:", temp_obj_num)

                

    def __len__(self):
        # print("[LEN] ", len(self.images))
        return len(self.images)

    def read_image(self, idx):
        img_name = self.images[idx]
        img_path = os.path.join(self.image_root, self.seq_name, img_name)
        img = cv2.imread(img_path)
        img = np.array(img, dtype=np.float32)
        if self.rgb:
            img = img[:, :, [2, 1, 0]]
        return img

    def read_label(self, label_name):
        label_path = os.path.join(self.label_root, self.seq_name, label_name)
        label = Image.open(label_path)
        label = np.array(label, dtype=np.uint8)
        if self.single_obj:
            label = (label > 0).astype(np.uint8)
        return label

    def __getitem__(self, idx):
        img_name = self.images[idx]
        current_img = self.read_image(idx)
        height, width, channels = current_img.shape
        current_label_name = img_name.split('.')[0] + '.png'
        obj_num = self.obj_nums[idx]

        if current_label_name in self.labels:
            current_label = self.read_label(current_label_name)
            sample = {'current_img':current_img, 'current_label':current_label}
        else:
            sample = {'current_img':current_img}
        
        sample['meta'] = {'seq_name':self.seq_name, 'frame_num':self.num_frame, 'obj_num':obj_num,
                          'current_name':img_name, 'height':height, 'width':width, 'flip':False}

        if self.transform is not None:
            sample = self.transform(sample)
        return sample

# class VOS_Test_forROVES(Dataset):
#     def __init__(self, image_root, label_root, seq_name, images, labels, rgb=False, transform=None, single_obj=False):
#         self.image_root = image_root
#         self.label_root = label_root
#         self.seq_name = seq_name
#         self.images = images
#         self.labels = labels
#         self.obj_num = 1
#         self.num_frame = len(self.images)
#         self.transform = transform
#         self.rgb = rgb
#         self.single_obj = single_obj

#         self.obj_nums = []
#         temp_obj_num = 0
#         for img_name in self.images:
#             self.obj_nums.append(temp_obj_num)
#             current_label_name = img_name.split('.')[0] + '.png'
#             if current_label_name in self.labels:
#                 current_label = self.read_label(current_label_name)
#                 # print( np.unique(current_label))
#                 if temp_obj_num < np.unique(current_label)[-1]:
#                     temp_obj_num = np.unique(current_label)[-1]
  

#     def __len__(self):
#         # print("[LEN] ", len(self.images))
#         return len(self.images)

#     def read_image(self, idx):
#         img_name = self.images[idx]
#         img_path = os.path.join(self.image_root, img_name)
#         img = cv2.imread(img_path)
#         img = np.array(img, dtype=np.float32)
#         if self.rgb:
#             img = img[:, :, [2, 1, 0]]
#         return img

#     def read_label(self, label_name):
#         label_path = os.path.join(self.label_root,  label_name)
#         label = Image.open(label_path)
#         label = np.array(label, dtype=np.uint8)
#         if self.single_obj:
#             label = (label > 0).astype(np.uint8)
#         return label

#     def __getitem__(self, idx):
#         img_name = self.images[idx]
#         current_img = self.read_image(idx)
#         height, width, channels = current_img.shape
#         current_label_name = img_name.split('.')[0] + '.png'
#         obj_num = self.obj_nums[idx]

#         if current_label_name in self.labels:
#             current_label = self.read_label(current_label_name)
#             sample = {'current_img':current_img, 'current_label':current_label}
#         else:
#             sample = {'current_img':current_img}
        
#         sample['meta'] = {'seq_name':self.seq_name, 'frame_num':self.num_frame, 'obj_num':obj_num,
#                           'current_name':img_name, 'height':height, 'width':width, 'flip':False}

#         if self.transform is not None:
#             sample = self.transform(sample)
#         return sample



class VOS_Test_forVOST(Dataset):
    def __init__(self, image_root, label_root, seq_name, images, labels, rgb=False, transform=None, single_obj=False):
        self.image_root = image_root
        self.label_root = label_root
        self.seq_name = seq_name
        self.images = images
        self.labels = labels
        self.obj_num = 1
        self.num_frame = len(self.images)
        self.transform = transform
        self.rgb = rgb
        self.single_obj = single_obj

        self.obj_nums = []
        temp_obj_num = 0
        for img_name in self.images:
            self.obj_nums.append(temp_obj_num)
            current_label_name = img_name.split('.')[0] + '.png'
            if current_label_name in self.labels:
                current_label = self.read_label(current_label_name)
                # print(np.unique(current_label))
                if 255 in np.unique(current_label):
                    
                    if temp_obj_num < np.unique(current_label)[-2]:
                        temp_obj_num = np.unique(current_label)[-2]
                else:
                    if temp_obj_num < np.unique(current_label)[-1]:
                        temp_obj_num = np.unique(current_label)[-1]          
  

    def __len__(self):
        # print("[LEN] ", len(self.images))
        return len(self.images)

    def read_image(self, idx):
        img_name = self.images[idx]
        img_path = os.path.join(self.image_root, self.seq_name, img_name)
        img = cv2.imread(img_path)
        img = np.array(img, dtype=np.float32)
        if self.rgb:
            img = img[:, :, [2, 1, 0]]
        return img

    def read_label(self, label_name):
        label_path = os.path.join(self.label_root, self.seq_name, label_name)
        label = Image.open(label_path)
        label = np.array(label, dtype=np.uint8)
        if self.single_obj:
            label = (label > 0).astype(np.uint8)
        return label

    def __getitem__(self, idx):
        img_name = self.images[idx]
        current_img = self.read_image(idx)
        height, width, channels = current_img.shape
        current_label_name = img_name.split('.')[0] + '.png'
        obj_num = self.obj_nums[idx]

        if current_label_name in self.labels:
            current_label = self.read_label(current_label_name)
            sample = {'current_img':current_img, 'current_label':current_label}
        else:
            sample = {'current_img':current_img}
        
        sample['meta'] = {'seq_name':self.seq_name, 'frame_num':self.num_frame, 'obj_num':obj_num,
                          'current_name':img_name, 'height':height, 'width':width, 'flip':False}

        if self.transform is not None:
            sample = self.transform(sample)
        return sample

# class ROVES_Test(object):
#     def __init__(self, root='/ROVES', transform=None, rgb=False, result_root=None, split = ["val"]):
#         self.db_root_dir = root
#         self.result_root = result_root
#         self.rgb = rgb
#         self.transform = transform
#         self.seqs = []

#         self.seqs = os.listdir(os.path.join(self.db_root_dir, "Annotations"))

#         self.annotations_root = os.path.join(self.db_root_dir, "Annotations")

#         self.seqs = list( map(lambda x: x.strip(), self.seqs  ))
#         self.seqs = [ seq for seq in self.seqs if seq != "chanlleng_label.json" ]

        
#     def __len__(self):
#         # print("LEN:" , len(self.seqs))
#         return len(self.seqs)
    

#     def __getitem__(self, idx):
#         seq_name = self.seqs[idx]

#         images = []
#         labels= []

#         image_root= os.path.join(self.annotations_root,seq_name ,"images")
#         label_root = os.path.join(self.annotations_root, seq_name,"masks")
#         # print(label_root)

#         # print( os.listdir(os.path.join(self.image_root)))

#         images = list( filter(lambda x: x.endswith(".jpg"), os.listdir( image_root)  )) 
#         labels =  list( filter(lambda x: x.endswith(".png"),os.listdir( label_root) ))  

#         images = np.sort(np.unique(images))
#         labels = np.sort(np.unique(labels))

#         # print("images:" , images)
#         # print("labels:" , labels)

#         if not os.path.isfile(os.path.join(self.result_root, seq_name, labels[0])):
#             if not os.path.exists(os.path.join(self.result_root, seq_name)):
#                 os.makedirs(os.path.join(self.result_root, seq_name))
#             shutil.copy(os.path.join(label_root, labels[0]), os.path.join(self.result_root, seq_name, labels[0]))

#         seq_dataset = VOS_Test_forROVES(image_root, label_root, seq_name, images, labels, transform=self.transform, rgb=self.rgb)
#         return seq_dataset

        
class ROVES_Test(object):
    def __init__(self, root='/VOST', transform=None, rgb=False, result_root=None, split = [""], oracle = False, week_num = 0):
        self.db_root_dir = os.path.join(root ,"ROVES_week_" + str(week_num ) )
        self.result_root = result_root
        self.rgb = rgb
        self.transform = transform
        self.seqs = []

        self.seqs = os.listdir(os.path.join(self.db_root_dir, "Annotations" ))

        # print(self.seqs)
        self.seqs = list( map(lambda x: x.strip(), self.seqs  ))
        print(self.seqs)

        self.image_root = os.path.join(self.db_root_dir, 'JPEGImages')
        self.label_root = os.path.join(self.db_root_dir, 'Annotations')

        self.oracle = oracle

        
    def __len__(self):
        # print("LEN:" , len(self.seqs))
        return len(self.seqs)
    

    def __getitem__(self, idx):
        seq_name = self.seqs[idx]

        images = []
        labels= []

        # print( os.listdir(os.path.join(self.image_root)))

        images = list( filter(lambda x: x.endswith(".jpg"), os.listdir(os.path.join(self.image_root, seq_name)) )) 
        labels =  list( filter(lambda x: x.endswith(".png"), os.listdir(os.path.join(self.label_root,seq_name)) ))  

        images = np.sort(np.unique(images))
        labels = np.sort(np.unique(labels))

        if not self.oracle:
            labels = [labels[0]]

        # print("images:" , images)
        # print("labels:" , labels)

        if not os.path.isfile(os.path.join(self.result_root, seq_name, labels[0])):
            if not os.path.exists(os.path.join(self.result_root, seq_name)):
                os.makedirs(os.path.join(self.result_root, seq_name))
            shutil.copy(os.path.join(self.label_root, seq_name, labels[0]), os.path.join(self.result_root, seq_name, labels[0]))

        seq_dataset = VOS_Test_forVOST(self.image_root, self.label_root, seq_name, images, labels, transform=self.transform, rgb=self.rgb)
        return seq_dataset

        

class VOST_Test(object):
    def __init__(self, root='/VOST', transform=None, rgb=False, result_root=None, split = ["val"]):
        self.db_root_dir = root
        self.result_root = result_root
        self.rgb = rgb
        self.transform = transform
        self.seqs = []

        for spl in split:
            with open(os.path.join(self.db_root_dir, "ImageSets", spl + ".txt"), "r") as file:
                self.seqs += file.readlines()
        # print(self.seqs)
        self.seqs = list( map(lambda x: x.strip(), self.seqs  ))
        print(self.seqs)

        self.image_root = os.path.join(root, 'JPEGImages')
        self.label_root = os.path.join(root, 'Annotations')

        
    def __len__(self):
        # print("LEN:" , len(self.seqs))
        return len(self.seqs)
    

    def __getitem__(self, idx):
        seq_name = self.seqs[idx]

        images = []
        labels= []

        # print( os.listdir(os.path.join(self.image_root)))

        images = list( filter(lambda x: x.endswith(".jpg"), os.listdir(os.path.join(self.image_root, seq_name)) )) 
        labels =  list( filter(lambda x: x.endswith(".png"), os.listdir(os.path.join(self.label_root,seq_name)) ))  

        images = np.sort(np.unique(images))
        labels = np.sort(np.unique(labels))

        # print("images:" , images)
        # print("labels:" , labels)

        if not os.path.isfile(os.path.join(self.result_root, seq_name, labels[0])):
            if not os.path.exists(os.path.join(self.result_root, seq_name)):
                os.makedirs(os.path.join(self.result_root, seq_name))
            shutil.copy(os.path.join(self.label_root, seq_name, labels[0]), os.path.join(self.result_root, seq_name, labels[0]))

        seq_dataset = VOS_Test_forVOST(self.image_root, self.label_root, seq_name, images, labels, transform=self.transform, rgb=self.rgb)
        return seq_dataset

        
        

class YOUTUBE_VOS_Test(object):
    def __init__(self, root='./valid', transform=None, rgb=False, result_root=None):

        self.db_root_dir = root
        self.result_root = result_root
        self.rgb = rgb
        self.transform = transform
        self.seq_list_file = os.path.join(self.db_root_dir, 'meta.json')
        self._check_preprocess()
    
        self.seqs = list(self.ann_f.keys())
        self.image_root = os.path.join(root, 'JPEGImages')
        self.label_root = os.path.join(root, 'Annotations')

    def __len__(self):
        return len(self.seqs)

    def __getitem__(self, idx):
        seq_name = self.seqs[idx]
        data = self.ann_f[seq_name]['objects']
        obj_names = list(data.keys())
        images = []
        labels = []
        for obj_n in obj_names:
            images += map(lambda x: x + '.jpg', list(data[obj_n]["frames"]))
            labels.append(data[obj_n]["frames"][0] + '.png')
        images = np.sort(np.unique(images))
        labels = np.sort(np.unique(labels))

        if not os.path.isfile(os.path.join(self.result_root, seq_name, labels[0])):
            if not os.path.exists(os.path.join(self.result_root, seq_name)):
                os.makedirs(os.path.join(self.result_root, seq_name))
            shutil.copy(os.path.join(self.label_root, seq_name, labels[0]), os.path.join(self.result_root, seq_name, labels[0]))

        print("res path:", os.path.join(self.result_root, seq_name, labels[0]))

        seq_dataset = VOS_Test(self.image_root, self.label_root, seq_name, images, labels, transform=self.transform, rgb=self.rgb)
        return seq_dataset

    def _check_preprocess(self):
        _seq_list_file = self.seq_list_file
        print("check pretrain:" , os.path.isfile(_seq_list_file))
        print(_seq_list_file)

        if not os.path.isfile(_seq_list_file):
            print(_seq_list_file)
            return False
        else:
            self.ann_f = json.load(open(self.seq_list_file, 'r'))['videos']
            return True



    

class DAVIS_Test(object):
    def __init__(self, split=['val'], root='./DAVIS', year=2017, transform=None, rgb=False, full_resolution=False, result_root=None):
        self.transform = transform
        self.rgb = rgb
        self.result_root = result_root
        if year == 2016:
            self.single_obj = True
        else:
            self.single_obj = False
        if full_resolution:
            resolution = 'Full-Resolution'
        else:
            resolution = '480p'
        self.image_root = os.path.join(root, 'JPEGImages', resolution)
        self.label_root = os.path.join(root, 'Annotations', resolution)
        seq_names = []
        for spt in split:
            with open(os.path.join(root, 'ImageSets', str(year), spt + '.txt')) as f:
                seqs_tmp = f.readlines()
            seqs_tmp = list(map(lambda elem: elem.strip(), seqs_tmp))
            seq_names.extend(seqs_tmp)
        self.seqs = list(np.unique(seq_names))

    def __len__(self):
        return len(self.seqs)

    def __getitem__(self, idx):
        seq_name = self.seqs[idx]
        images = list(np.sort(os.listdir(os.path.join(self.image_root, seq_name))))
        labels = [images[0].replace('jpg', 'png')]

        if not os.path.isfile(os.path.join(self.result_root, seq_name, labels[0])):
            if not os.path.exists(os.path.join(self.result_root, seq_name)):
                os.makedirs(os.path.join(self.result_root, seq_name))
            source_label_path = os.path.join(self.label_root, seq_name, labels[0])
            result_label_path = os.path.join(self.result_root, seq_name, labels[0])
            if self.single_obj:
                label = Image.open(source_label_path)
                label = np.array(label, dtype=np.uint8)
                label = (label > 0).astype(np.uint8)
                label = Image.fromarray(label).convert('P')
                label.putpalette(_palette)
                label.save(result_label_path)
            else:
                shutil.copy(source_label_path, result_label_path)


        seq_dataset = VOS_Test(self.image_root, self.label_root, seq_name, images, labels, 
                               transform=self.transform, rgb=self.rgb, single_obj=self.single_obj)
        return seq_dataset

