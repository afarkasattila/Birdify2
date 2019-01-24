from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from .dataset_utils import image_to_tfexample
from json import dump
from numpy import arange, empty, array, empty_like
from numpy.random import shuffle
from os import walk
from PIL import Image
from six.moves import urllib
import sys
import tensorflow as tf

_IMAGE_SIZE = 224
_NUM_CHANNELS = 3


def _get_labels(filename, nr_of_labels):
    print('Get labels from: ', filename)
    with open("%s/labels.txt"%(filename), "r") as f:
        data = f.read()
    labels = empty_like(arange(nr_of_labels))
    labels = data.split(" ")
    labels_1 = []
    k =0
    for x in labels:
        k += 1
        if x == '':
            labels_1.append(0)
        else:
            labels_1.append(int(x))
    return labels_1

def _shuffle_all(data_names, labels, path_to_file_names=None):
    indexes = arange(len(data_names))
    shuffle(indexes)
    indexes = [ int(x) for x in indexes ]
    shuffled_labels = []
    shuffled_names = []
    shuffled_path_to_file_names = []
    for i in arange(len(data_names)):
        shuffled_labels.append(labels[indexes[i]])
        shuffled_names.append(data_names[indexes[i]])
        if path_to_file_names is not None:
            shuffled_path_to_file_names.append(path_to_file_names[indexes[i]])
    return shuffled_names, shuffled_labels, shuffled_path_to_file_names


def _create_all_tf_record_name(destination_directory, num_images, nr_of_train):
    nr_of_val = nr_of_train
    tfrecord_name = []
    len_max = len(str(nr_of_train))
    len_number = len_max + 1
    str_tran_and_val = "0"
    str_tran_and_val += str(nr_of_train)
    for i in arange(nr_of_train):
        len_i = len(str(i))
        nr_0 = len_number - len_i
        str_nr = ""
        for _ in arange(nr_0):
            str_nr += "0"
        str_nr += str(i)
        tfrecord_name.append("%s/birdify_train_%s-of-%s.tfrecord"%(destination_directory, str_nr, str_tran_and_val))
        tfrecord_name.append("%s/birdify_validation_%s-of-%s.tfrecord"%(destination_directory,str_nr, str_tran_and_val))
    return tfrecord_name

def _add_to_tfrecord(images, labels, num_images, tfrecord_writer):
    """
    Loads data from the binary MNIST files and writes files to a TFRecord.
    Args:
        data_filename: The filename of the MNIST images.
        labels_filename: The filename of the MNIST labels.
        num_images: The number of images in the dataset.
    """
    shape = (_IMAGE_SIZE, _IMAGE_SIZE, _NUM_CHANNELS)
    with tf.Graph().as_default():
        image = tf.placeholder(dtype=tf.uint8, shape=shape)
        encoded_png = tf.image.encode_png(image)
        with tf.Session('') as sess:
            for j in range(num_images):
                sys.stdout.write('\r>> Converting image %d/%d' % (j + 1, num_images))
                sys.stdout.flush()
                png_string = sess.run(encoded_png, feed_dict={image: images[j]})
                example = image_to_tfexample(png_string, 'png'.encode(), _IMAGE_SIZE, _IMAGE_SIZE, labels[j])
                tfrecord_writer.write(example.SerializeToString())

def _get_image_data(path_filename, filenames, num_data_per_tfrecord):
    data = empty([num_data_per_tfrecord, _IMAGE_SIZE, _IMAGE_SIZE, _NUM_CHANNELS])
    i = 0
    for picture in filenames:
        with Image.open("%s/%s"%(path_filename[i], picture)) as im:
            pix = array(im)[:,:,:3]
        data[i] = pix
        i += 1
    return data

def run(destination_directory, spectro_path, num_data_per_tfrecord_train, num_data_per_tfrecord_val):
    num_data = 0
    file_names = []
    path_to_file_names = []
    labels = []
    class_names = {}
    for root, dirs, files in walk(spectro_path):
        root = root.replace("\\","/")
        print(root)
        if len(dirs) > 0:
            nr_of_classes = 0
            for name_class in dirs:
                class_names[name_class] = nr_of_classes
                nr_of_classes += 1
        else:
            class_id = -1
            for key in class_names:
                if key in root:
                    class_id = class_names[key]
            for spectro_file in files:
                num_data += 1
                file_names.append(spectro_file)
                labels.append(class_id)
                path_to_file_names.append(root)
    
    print(num_data)
    nr_train_tfrecord = int(num_data / (num_data_per_tfrecord_train + num_data_per_tfrecord_val))
    nr_of_tfrecord = nr_train_tfrecord * 2

    file_names, labels, path_to_file_names = _shuffle_all(file_names, labels, path_to_file_names)
    tfrecord_name = _create_all_tf_record_name(destination_directory, num_data, nr_train_tfrecord)

    end_ind = 0
    for i in arange(nr_of_tfrecord):
        tfrecords_filename = tfrecord_name[i]
        if "train" in tfrecords_filename:
            num_data_per_tfrecord = num_data_per_tfrecord_train
        else:
            num_data_per_tfrecord = num_data_per_tfrecord_val
        start_ind = end_ind
        end_ind = start_ind + num_data_per_tfrecord
        data = _get_image_data(path_to_file_names[start_ind:end_ind], file_names[start_ind:end_ind], num_data_per_tfrecord)
        label = labels[start_ind:end_ind]
        print("%d'th tfrecord %s: pictures %d to %d" % (i, tfrecords_filename, start_ind, end_ind))
        writer = tf.python_io.TFRecordWriter(tfrecords_filename)
        _add_to_tfrecord(data, label, num_data_per_tfrecord, writer)
    
    with open('%s/labels.txt'%(destination_directory), 'w+') as fp:
        dump(class_names, fp)