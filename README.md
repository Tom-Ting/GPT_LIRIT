# 项目运行文档

## 算法端服务

### Python环境安装

python版本为3.6，具体使用的库参考requirement，建议使用conda安装环境后，利用pip一键安装requirements。 

需要安装rust环境，不然安装python依赖时会报错。 


如果使用python 3.8+，可能出现如下报错:
`pip is configured with locations that require TLS/SSL, however the ssl module in Python`

### 百度OCR配置

需要配置百度云OCR的API密钥，具体参考[百度云OCR](https://cloud.baidu.com/product/ocr)。

代码配置位置为" AlgorithmServer/utils/ocr.py "。

### 语义模型下载

下载语义模型至"AlgorithmServer\AlgorithmServer\models"。

保证与"AlgorithmServer\utils\semantic_model.py"中的路径一至。

```
git lfs install
git clone https://huggingface.co/uer/sbert-base-chinese-nli
```

如果有需要，可以去“[Huggingface](https://huggingface.co/)”上寻找更好的语义模型。

可能会遇到如下报错

`fatal: unable to access 'https://huggingface.co/uer/sbert-base-chinese-nli/': Failed to connect to huggingface.co port 443 after 21023 ms: Couldn't connect to server
`
可使用如下方法解决：
`git config --global http.proxy 127.0.0.1:10809`

`git config --global https.proxy 127.0.0.1:10809`



### 图像分类模型下载

下载语义模型至"AlgorithmServer\AlgorithmServer\models".

保证与"AlgorithmServer/utils/vgg16.py"中的路径一至。

```
git clone https://github.com/tata0516/VGG16
```

## 启动

正常的django启动方式，命令行进入AlgorithmServer目录，执行

```shell
python manage.py runserver
```



## ChatGPT服务端启动

- 在`ChatGPTModule\ChatGPTServer`路径下执行如下命令，启动服务

```shell
python manage.py runserver
```



##  实验文件

- `GPTLIRAT\LIT-Backend\LIT\src\test\java\cn\iselab\mooctest\lit\experimentMultipleTest.java`文件为实验启动入口
- 变量` androidStep`和`iosStep`为步骤匹配关系，需要实验者进行填写
- 变量` androidTotalScriptCount `和`iosTotalScriptCount `为当前脚本步骤数
