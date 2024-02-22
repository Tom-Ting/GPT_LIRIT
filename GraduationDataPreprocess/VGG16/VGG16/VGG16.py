#from keras.utils import image_utils
from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input
import numpy as np
import os
from sklearn.preprocessing import LabelBinarizer
from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn.metrics import recall_score
import matplotlib as mlp
import matplotlib.pyplot as plt
from PIL import Image
from keras.preprocessing.image import img_to_array,load_img
from tensorflow.python.keras.models import load_model
# 载入VGG16结构（去除全连接层）
model_vgg = VGG16(weights='imagenet', include_top=False)

def modelProcess(img_path, model):
    img = load_img(img_path, target_size=(224, 224))  # 读取图片途径，裁成224,224
    img = img_to_array(img)  # 转换成图像数组
    x = np.expand_dims(img, axis=0)  # 加一个维度这样能载入VGG
    x = preprocess_input(x)  # 预处理
    x_vgg = model.predict(x)  # 特征提取，这是全连接层之前的shape
    # shape（1,7,7,512）
    x_vgg = x_vgg.reshape(1, 25088)  # 摊开来进行和全连接层的对接
    return x_vgg

# list file names of the training datasets
def transform_format(path):  # 转换格式
    folders = os.listdir(path)  # 读取爷爷路径下的所有文件名，也就是5个分类标签
    for j in range(len(folders)):
        dirName = path + '//' + folders[j] + '//'
        li = os.listdir(dirName)
        for filename in li:
            newname = filename
            newname = newname.split(".")
            if newname[-1] != "png":
                newname[-1] = "png"
                newname = str.join(".", newname)
                filename = dirName + filename
                newname = dirName + newname
                os.rename(filename, newname)
                print('reading the images:%s' % (newname))
                a = np.array(Image.open(newname))
                if ((len(a.shape) != 3) or (a.shape[2] != 3)):
                    a = np.array(Image.open(newname).convert('RGB'))
                    img = Image.fromarray(a.astype('uint8'))
                    img.save(newname)  # 替换原来的图片
                    print(a.shape)  # 用来测试的print
    print("全部图片已成功转换为PNG格式")
    print("全部图片已成功转换为RGB通道")

def read_data(path):
    folders = os.listdir(path)
    for j in range(len(folders)):
        folder = path + '//' + folders[j]
        dirs = os.listdir(folder)
        # 产生图片的路径
        img_path = []
        for i in dirs:
            if os.path.splitext(i)[1] == ".png":  # 已经转换过png了
                img_path.append(i)
        img_path = [folder + "//" + i for i in img_path]

        # 开始处理
        features1 = np.zeros([len(img_path), 25088])
        for i in range(len(img_path)):
            feature_i = modelProcess(img_path[i], model_vgg)
            print('preprocessed:', img_path[i])
            features1[i] = feature_i
        if j == 0:
            X = features1
        else:
            X = np.concatenate((X, features1), axis=0)
    return X


def devide(path):
    y = []
    folders = os.listdir(path)
    for j in range(len(folders)):
        dirName = path + '//' + folders[j] + '//'
        lens = len(os.listdir(dirName))
        for i in range(lens):
            y.append(j)

    lb = LabelBinarizer()
    y = lb.fit_transform(y)  # 进行one-hot编码
    transform_format(path)  # 转换格式
    X = read_data(path)
    # 分隔训练集和验证集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=50)
    return X_train, X_test, y_train, y_test

def train():
    # 模型初始化
    model.add(Dense(units=40, activation='relu', input_dim=25088))
    # 输入的维度是25088
    model.add(Dense(units=10, activation='softmax'))
    model.summary()
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    # train the model
    model.fit(X_train, y_train, epochs=30, batch_size=64)
    y_train_predict = (model.predict(X_train) > 0.5).astype("int32")
    accuracy_train = recall_score(y_train.argmax(axis=1), y_train_predict.argmax(axis=1),
                                  average='macro')  # 把实际的和预测的往里丢
    print('-' * 35)
    print('accuracy_train:', accuracy_train)

def test():
    # 验证集准确率
    y_test_predict = (model.predict(X_test) > 0.5).astype("int32")
    accuracy_test = recall_score(y_test.argmax(axis=1), y_test_predict.argmax(axis=1), average='macro')  # 把实际的和预测的往里丢
    print('-' * 35)
    print('accuracy_test:', accuracy_test)

def pred(test_path):
    mlp.rcParams['axes.unicode_minus'] = False
    pokemon_dict = {0:'add',1: 'arrow_down', 2: 'arrow_left', 3: 'check_mark', 4: 'close', 5: 'delete', 6: 'menu',7:'other',8:'settings',9:'share'}
    folders = os.listdir(test_path)
    num = len(folders)
    fig = plt.figure(figsize=(10, 10 * (int(num / 9) + int(num % 9 / 3) + 1 * (num % 9 % 3))))
    for j in range(num):
        img_name = test_path + folders[j]
        img_path = img_name
        img = load_img(img_path, target_size=(224, 224))
        img = img_to_array(img)
        x = np.expand_dims(img, axis=0)
        x = preprocess_input(x)
        x_vgg = model_vgg.predict(x)
        x_vgg = x_vgg.reshape(1, 25088)
        result = (model.predict(x_vgg) > 0.5).astype("int32")
        print(result.argmax(axis=1)[0])
        print('{}'.format(pokemon_dict[result.argmax(axis=1)[0]]))
        print("0" * 35)
        img_ori = load_img(img_name, target_size=(250, 250))
        plt.subplot(int(num / 3) + 1, 3, j + 1)
        plt.imshow(img_ori)  # 展示
        plt.title('{}'.format(pokemon_dict[result.argmax(axis=1)[0]]))
        # 每个预测图题目写上预测结果
    plt.subplots_adjust(top=0.99, bottom=0.003, left=0.1, right=0.9, wspace=0.18, hspace=0.15)
    # 控制每个子图间距
    plt.savefig('1.png')



path = 'data/train'
X_train, X_test, y_train, y_test =devide(path)
model = Sequential()
train()
test()
#save model
model.save('save/my_model.h5')
#load model
model = load_model('save/my_model.h5')
test_path = 'data/test/'
pred(test_path)


