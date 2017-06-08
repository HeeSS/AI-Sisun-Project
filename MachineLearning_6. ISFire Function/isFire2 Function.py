﻿# 32VGG+LRN 우분투에러수정Model
import tensorflow as tf
import numpy as np
import os




image_depth = 2

# lrn(2, 2e-05, 0.75, name='norm1')
radius = 2
alpha = 2e-05
beta = 0.75
bias = 1.0

# ---------------------------------------------------------------------------------------------------
# X: input 32*32*image_depth
# Y: output '1' or '0'
X = tf.placeholder(tf.float32, [None, 32 * 32 * image_depth])
Y = tf.placeholder(tf.int32, [None, 1])  # 0,1

# 출력 class 개수 = 1(fire), 0(not fire)
nb_classes = 2

# one hot & reshape
Y_one_hot = tf.one_hot(Y, nb_classes)  # print("one_hot", Y_one_hot)
Y_one_hot = tf.reshape(Y_one_hot, [-1, nb_classes])  # print("reshape", Y_one_hot)

# img 32x32x1 (black/white)
X_img = tf.reshape(X, [-1, 32, 32, image_depth])

# ---------------------------------------------------------------------------------------------------
# L1 ImgIn shape = (?, 32, 32, image_depth)
W1 = tf.Variable(tf.random_normal([3, 3, image_depth, 64], stddev=0.01))

# Conv1 -> (?, 32, 32, 64)
L1 = tf.nn.conv2d(X_img, W1, strides=[1, 1, 1, 1], padding='SAME')

# Conv2 -> (?, 32, 32, 64)
L1 = tf.nn.conv2d(X_img, W1, strides=[1, 1, 1, 1], padding='SAME')
L1 = tf.nn.relu(L1)

# lrn1
# lrn(2, 2e-05, 0.75, name='norm1')
L1 = tf.nn.local_response_normalization(L1, depth_radius=radius, alpha=alpha, beta=beta, bias=bias)

# Pool -> (?, 16, 16, 64)
L1 = tf.nn.max_pool(L1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

# ---------------------------------------------------------------------------------------------------
# L2 ImgIn shape = (?, 16, 16, 64)
W2 = tf.Variable(tf.random_normal([3, 3, 64, 128], stddev=0.01))

# Conv1 -> (?, 16, 16, 128)
L2 = tf.nn.conv2d(L1, W2, strides=[1, 1, 1, 1], padding='SAME')

# Conv2 -> (?, 16, 16, 128)
L2 = tf.nn.conv2d(L1, W2, strides=[1, 1, 1, 1], padding='SAME')
L2 = tf.nn.relu(L2)

# lrn2
# lrn(2, 2e-05, 0.75, name='norm1')
L2 = tf.nn.local_response_normalization(L2, depth_radius=radius, alpha=alpha, beta=beta, bias=bias)

# Pool -> (?, 8, 8, 128)
L2 = tf.nn.max_pool(L2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

# ---------------------------------------------------------------------------------------------------
# L3 ImgIn shape = (?, 8, 8, 128)
W3 = tf.Variable(tf.random_normal([3, 3, 128, 256], stddev=0.01))

# Conv1 -> (?, 8, 8, 256)
L3 = tf.nn.conv2d(L2, W3, strides=[1, 1, 1, 1], padding='SAME')

# Conv2 -> (?, 8, 8, 256)
L3 = tf.nn.conv2d(L2, W3, strides=[1, 1, 1, 1], padding='SAME')

# Conv3 -> (?, 8, 8, 256)
L3 = tf.nn.conv2d(L2, W3, strides=[1, 1, 1, 1], padding='SAME')
L3 = tf.nn.relu(L3)

# Pool -> (?, 4, 4, 256)
L3 = tf.nn.max_pool(L3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

# ---------------------------------------------------------------------------------------------------
# L4 ImgIn shape = (?, 4, 4, 256)
W4 = tf.Variable(tf.random_normal([3, 3, 256, 512], stddev=0.01))

# Conv1 -> (?, 4, 4, 512)
L4 = tf.nn.conv2d(L3, W4, strides=[1, 1, 1, 1], padding='SAME')

# Conv2 -> (?, 4, 4, 512)
L4 = tf.nn.conv2d(L3, W4, strides=[1, 1, 1, 1], padding='SAME')

# Conv3 -> (?, 4, 4, 512)
L4 = tf.nn.conv2d(L3, W4, strides=[1, 1, 1, 1], padding='SAME')
L4 = tf.nn.relu(L4)

# Pool -> (?, 2, 2, 512)
L4 = tf.nn.max_pool(L4, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

# ---------------------------------------------------------------------------------------------------
# L5 ImgIn shape = (?, 2, 2, 512)
W5 = tf.Variable(tf.random_normal([2, 2, 512, 512], stddev=0.01))

# Conv1 -> (?, 2, 2, 512)
L5 = tf.nn.conv2d(L4, W5, strides=[1, 1, 1, 1], padding='SAME')

# Conv2 -> (?, 2, 2, 512)
L5 = tf.nn.conv2d(L4, W5, strides=[1, 1, 1, 1], padding='SAME')

# Conv3 -> (?, 2, 2, 512)
L5 = tf.nn.conv2d(L4, W5, strides=[1, 1, 1, 1], padding='SAME')
L5 = tf.nn.relu(L5)

# Pool -> (?, 1, 1, 512)
L5 = tf.nn.max_pool(L5, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

# Reshape -> (?, 1 * 1 * 512) - Flatten them for FC
L5_flat = tf.reshape(L5, [-1, 1 * 1 * 512])

# ---------------------------------------------------------------------------------------------------
# L6 FC 1x1x512 inputs ->  4096 outputs
W6 = tf.get_variable("W6", shape=[512 * 1 * 1, 4096], initializer=tf.contrib.layers.xavier_initializer())
b6 = tf.Variable(tf.random_normal([4096]))
L6 = tf.nn.relu(tf.matmul(L5_flat, W6) + b6)

# ---------------------------------------------------------------------------------------------------
# L7 FC 4096 inputs ->  1000 outputs
W7 = tf.get_variable("W7", shape=[4096, 1000], initializer=tf.contrib.layers.xavier_initializer())
b7 = tf.Variable(tf.random_normal([1000]))
L7 = tf.nn.relu(tf.matmul(L6, W7) + b7)

# ---------------------------------------------------------------------------------------------------
# L8 FC 1000 inputs -> 1 outputs
W8 = tf.get_variable("W8", shape=[1000, nb_classes], initializer=tf.contrib.layers.xavier_initializer())
b8 = tf.Variable(tf.random_normal([nb_classes]))
logits = tf.matmul(L7, W8) + b8

prediction = tf.argmax(logits, 1)

# ---------------------------------------------------------------------------------------------------
init = tf.global_variables_initializer()
sess = tf.Session()

# ---------------------------------------------------------------------------------------------------

def MLOpen():
    tf.set_random_seed(777)
    # ---------------------------------------------------------------------------------------------------
    # initialize
    global sess
    sess.run(init)
    # ---------------------------------------------------------------------------------------------------
    saver = tf.train.Saver()
    saver.restore(sess, os.getcwd() + "/ISFire(new model).ckpt")
    print(os.getcwd() + "/ISFire(new model).ckpt")

def isFire(*Tinput):
    XInput = Tinput[0]

    # predict
    global sess
    global prediction
    predict_output = sess.run(prediction, feed_dict={X: XInput})

    return predict_output

def MLClose():
    sess.close()

tup = ((183,32,184,31,185,31,181,31,179,31,177,32,176,33,172,34,167,35,164,35,160,35,156,34,151,34,149,34,149,33,142,31,136,29,133,26,134,25,131,28,133,26,133,24,132,21,135,17,133,15,132,13,130,12,135,18,138,18,141,19,147,21,154,24,183,33,185,31,186,31,183,32,180,33,178,32,176,34,172,34,167,35,163,35,159,35,156,34,152,35,150,35,150,34,146,32,141,29,137,27,136,26,132,29,132,27,132,25,131,22,135,18,135,16,134,13,133,13,134,18,138,19,141,20,146,21,153,24,184,33,185,33,186,31,184,33,181,33,178,33,176,34,173,34,167,35,163,36,159,35,156,36,153,36,151,36,152,36,152,34,148,31,143,29,139,27,136,30,134,28,132,26,131,23,134,19,137,17,137,15,135,14,134,18,137,19,140,19,146,21,152,24,184,33,185,33,186,33,186,34,182,34,177,34,175,35,172,35,166,35,162,36,158,36,155,37,152,37,152,37,153,37,155,35,154,32,150,30,145,29,142,31,137,29,134,27,134,24,134,21,137,19,138,17,137,16,135,19,138,19,140,19,145,22,152,25,182,35,184,34,185,34,185,35,181,35,176,35,173,35,170,36,164,36,161,36,157,36,154,38,152,38,153,38,155,38,156,36,158,34,156,31,153,30,148,32,141,31,137,29,136,26,134,24,137,21,138,19,137,18,136,19,138,19,141,20,146,23,152,26,179,35,181,35,183,34,183,35,179,36,174,36,172,36,168,36,162,36,160,36,156,36,154,40,153,40,155,40,157,40,158,38,162,36,161,34,159,33,152,34,146,34,140,31,138,28,136,25,136,23,137,21,138,20,138,20,140,19,142,21,146,23,152,27,176,34,179,35,180,35,180,36,176,36,172,36,170,37,165,37,160,37,159,37,156,37,155,40,155,41,157,41,160,41,163,40,165,37,165,35,163,34,159,36,154,35,147,33,143,30,140,27,137,25,137,23,139,23,139,20,141,21,143,22,147,24,153,28,175,34,177,35,179,35,178,36,175,36,171,36,169,37,163,37,159,37,158,38,155,37,157,42,157,43,160,43,163,43,167,42,167,40,166,38,165,37,165,38,161,37,154,35,149,32,143,30,138,28,137,26,140,25,140,21,142,22,143,22,148,25,153,29,170,33,171,34,173,35,172,35,172,36,169,36,166,37,161,38,156,38,155,38,156,39,156,42,158,43,158,44,161,44,166,43,169,41,168,39,168,38,168,39,167,38,160,36,154,34,148,31,145,29,142,28,142,27,145,23,147,24,147,24,147,26,154,29,162,32,162,33,165,33,168,34,168,34,165,35,162,36,159,38,154,38,153,39,154,39,155,43,157,43,158,44,161,44,167,43,170,41,169,40,170,39,170,40,170,39,165,38,159,35,153,33,147,31,144,30,144,29,145,26,147,25,148,26,148,28,154,30,156,29,157,31,160,32,162,32,162,32,160,34,157,35,156,37,151,39,149,39,151,40,152,43,156,44,158,45,162,45,168,44,171,43,171,41,172,40,173,41,174,40,170,38,166,36,160,34,152,32,147,31,146,30,146,27,148,27,149,27,150,28,154,30,150,228,152,28,156,30,155,30,156,30,155,33,152,35,151,37,146,39,145,40,147,41,150,43,154,44,157,45,162,45,167,44,171,43,171,41,172,40,175,41,176,40,175,38,173,37,166,35,157,33,150,32,149,32,148,30,149,29,150,29,152,29,153,31,143,231,143,229,146,28,149,28,151,29,150,31,148,34,145,36,141,39,141,41,144,41,148,44,153,45,157,46,162,46,165,45,170,44,171,42,172,41,175,41,177,41,178,39,177,38,172,35,162,34,155,33,152,32,151,32,150,31,151,30,153,30,153,30,138,233,138,231,139,229,142,26,144,28,144,30,143,33,138,36,136,39,138,42,141,43,146,43,151,44,155,45,161,46,164,45,170,44,171,42,173,41,176,41,178,41,180,39,180,38,177,36,169,34,161,33,157,33,154,34,152,33,152,31,153,31,153,31,131,234,133,233,135,231,136,24,139,26,139,29,138,33,133,37,132,39,136,42,140,43,145,43,150,44,154,45,159,46,165,45,171,44,172,42,175,41,177,41,179,41,181,39,182,38,181,36,177,35,169,34,163,34,157,35,153,34,152,32,153,31,153,31,120,234,125,233,130,231,132,23,135,25,135,29,134,32,131,37,130,40,135,42,139,44,145,43,150,44,154,45,158,45,166,45,172,44,174,42,176,41,178,41,180,41,182,39,184,38,184,36,181,35,174,34,167,33,159,36,154,34,152,33,153,32,153,31,91,243,102,243,121,243,123,238,128,233,126,28,130,34,127,37,131,38,134,39,139,39,144,42,149,43,152,42,159,42,167,42,172,44,173,45,180,45,180,39,182,39,183,39,183,37,183,37,183,36,178,36,174,35,164,34,157,33,155,33,153,31,153,30,86,243,89,243,95,243,109,237,119,234,125,228,122,33,122,36,127,38,130,38,135,38,141,43,148,43,153,42,162,42,168,42,172,44,173,44,179,44,181,39,183,39,183,38,183,37,184,37,185,36,181,36,177,36,169,34,162,33,158,33,155,32,153,30,86,242,84,242,80,242,92,237,105,235,118,231,113,29,120,34,126,37,128,38,131,39,135,43,146,43,153,42,164,42,169,42,173,43,173,44,178,44,181,39,183,39,184,38,184,37,185,37,186,36,184,36,182,36,175,34,169,34,164,34,157,32,153,31,82,241,83,241,82,242,82,237,91,236,105,234,109,229,116,225,122,35,122,38,123,40,130,42,141,42,149,42,160,42,168,42,173,43,173,43,177,43,182,38,184,38,184,38,184,37,185,37,186,36,186,36,184,36,180,35,176,35,169,34,160,33,153,32,70,240,74,241,79,241,78,237,79,238,89,236,106,233,108,229,115,224,115,37,114,39,125,42,135,42,142,42,152,42,165,42,172,42,172,41,177,41,181,38,183,38,184,37,184,37,183,36,184,36,185,36,185,36,183,36,179,35,172,35,163,34,155,32,62,240,66,240,72,240,76,238,71,238,77,239,96,238,102,233,113,227,114,220,112,217,120,41,129,41,135,41,145,41,160,41,169,41,171,40,176,39,180,37,182,37,183,36,183,37,182,36,182,36,183,36,184,35,184,37,181,36,176,36,168,35,159,33,64,239,65,239,68,239,70,238,69,240,72,242,78,241,93,237,108,230,113,222,113,219,117,40,126,40,132,40,141,40,154,40,166,39,170,38,176,37,179,37,181,36,182,36,182,35,181,36,181,36,182,35,183,35,185,38,183,37,179,37,173,35,165,34,67,238,67,238,67,239,64,238,68,241,71,244,64,244,81,240,99,232,107,224,108,221,115,37,124,38,131,39,140,39,151,39,164,38,170,36,176,36,179,35,181,35,181,36,181,35,181,35,181,35,182,35,183,35,185,38,183,37,181,37,177,36,170,35,66,238,66,238,66,238,63,238,63,241,63,244,63,245,61,241,80,235,105,228,102,224,112,34,119,35,132,37,137,38,150,38,156,37,164,35,173,34,176,35,180,35,179,34,180,35,180,35,180,35,181,35,182,35,184,38,184,38,183,38,183,36,177,35,65,238,65,238,65,238,63,239,63,241,63,245,62,246,61,243,66,238,88,231,108,228,113,30,121,32,134,35,142,36,147,36,153,35,162,33,170,33,175,34,179,34,178,34,179,34,180,34,181,35,181,35,182,34,184,38,184,38,183,38,183,36,178,35,63,238,63,239,63,239,63,238,62,241,62,244,61,246,60,243,55,239,69,235,100,233,110,230,122,227,131,32,141,34,144,34,150,34,158,32,167,32,173,33,178,33,178,33,180,34,181,34,181,35,181,34,181,35,183,38,183,37,182,37,182,36,180,34,62,239,61,239,61,239,62,238,61,241,60,243,60,244,60,244,56,241,58,239,77,237,101,234,118,231,125,28,135,32,140,33,147,33,155,31,164,31,171,32,177,32,178,33,180,33,181,34,181,34,181,34,181,35,182,38,182,37,181,37,181,35,181,34,61,239,61,239,60,240,61,240,60,240,59,241,58,242,58,243,57,243,58,242,62,242,85,238,109,235,120,229,131,30,137,32,143,32,151,30,160,30,168,31,174,32,176,33,179,33,179,34,179,34,180,34,180,35,181,37,181,36,180,36,180,35,181,34,62,240,61,240,60,240,61,240,59,239,58,239,57,240,56,242,53,244,60,245,61,247,69,241,95,237,115,232,128,29,132,31,138,31,146,30,155,28,162,31,169,32,173,31,176,33,177,34,178,34,179,35,180,35,180,37,180,36,179,36,179,34,180,33,64,240,63,240,61,241,60,240,59,238,57,238,56,238,55,241,52,244,58,248,61,249,60,243,77,239,102,234,119,27,127,30,133,31,141,29,150,28,155,31,163,31,168,31,171,33,174,33,176,34,178,35,179,35,180,36,179,36,179,35,178,34,178,33,65,240,64,241,62,241,60,239,58,239,56,237,55,237,55,240,54,245,55,249,57,251,58,244,64,240,89,235,108,27,124,30,130,30,138,29,147,28,151,31,159,31,164,31,168,32,172,33,175,34,178,35,179,35,179,36,179,35,178,35,178,34,176,32),)


MLOpen()
print(isFire(tup))
MLClose()

