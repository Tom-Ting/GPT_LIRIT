from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input
import numpy as np
import os
import cv2
import json
from tensorflow.python.keras.models import load_model
from keras.preprocessing.image import img_to_array, load_img

# 载入VGG16结构（去除全连接层）
model_vgg = VGG16(weights='imagenet', include_top=False)
model = load_model('VGG16/my_model.h5')
# 曾：threshold = 0.5
threshold = 0.6


def pred(img):
    widget_dict = {0: 'add', 1: 'arrow_down', 2: 'arrow_left', 3: 'check_mark', 4: 'close', 5: 'delete', 6: 'menu', 7: 'other', 8: 'settings', 9: 'share'}
    img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_CUBIC)
    img = img_to_array(img)
    x = np.expand_dims(img, axis=0)
    x = preprocess_input(x)
    x_vgg = model_vgg.predict(x)
    x_vgg = x_vgg.reshape(1, 25088)
    result = (model.predict(x_vgg) > threshold).astype("int32")  # 这就是预测结果了
    return '{}'.format(widget_dict[result.argmax(axis=1)[0]])