import os
import json

from aip import AipOcr


def ocr(image_bytes, lang='CHN_ENG', show_char=False):
    # Use your own id and keys below.
    # Request your app id and keys on https://cloud.baidu.com.
    APP_ID = '45051593'
    API_KEY = 'yMHg2emGscvcvdcGSvPlNibN'
    SECRET_KEY = 'Gdg8WeygRgkRemDiMsGYfMYQNp9Ii4gH'

    os.environ["HTTP_PROXY"] = "http://localhost:7890"
    os.environ["HTTPS_PROXY"] = "http://localhost:7890"

    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    options = {
        'language-type': lang,
        'recognize_granularity': 'small' if show_char else 'big',
        'probability': 'true'
    }
    return client.general(image_bytes, options)


def ocr_for_step(step_path, ignore_cache=False):
    """
    将step文件夹下element.png和screenshot.png文件进行ocr处理，并本地保存
    将ocr处理的结果格式化保存至prompt.json文件夹中
    :param ignore_cache: 是否要忽略已有的OCR结果文件
    :param step_path: step文件夹路径
    :return: 无
    """
    widget_path = step_path + "\\element.png"
    screenshot_path = step_path + "\\screenshot.png"

    # 判断数据是否完整
    if not os.path.exists(widget_path) or not os.path.exists(screenshot_path):
        print("OCR错误：step文件夹下无element.png文件或screenshot.png文件")
        return None

    widget_ocr_result_path = step_path + "\\widget_ocr_result.json"
    screenshot_ocr_result_path = step_path + "\\screenshot_ocr_result.json"

    # 判断是否已经OCR处理过。若已处理过，则直接读取现存文件
    if ignore_cache is False and (os.path.exists(widget_ocr_result_path) and os.path.exists(screenshot_ocr_result_path)):
        print("OCR已完成：从已存文件中读取数据")
        return None

    # element.png图片处理
    w_image = open(widget_path, 'rb').read()
    w_ocr_json = ocr(w_image)
    if w_ocr_json['words_result_num'] == 0:
        print("widget OCR处理：未检测到部件中的文字")
    else:
        try:
            with open(widget_ocr_result_path, 'w', encoding="utf-8") as file:
                w_ocr_str = json.dumps(w_ocr_json, ensure_ascii=False)
                file.write(w_ocr_str)
        except Exception as e:
            print("widget OCR处理发生错误：", str(e))

    # screenshot.png图片处理
    s_image = open(screenshot_path, 'rb').read()
    s_ocr_json = ocr(s_image)
    if s_ocr_json['words_result_num'] == 0:
        print("screenshot OCR处理：未检测到部件中的文字")
    else:
        try:
            with open(screenshot_ocr_result_path, 'w', encoding="utf-8") as file:
                s_ocr_str = json.dumps(s_ocr_json, ensure_ascii=False)
                file.write(s_ocr_str)
        except Exception as e:
            print("screenshot OCR处理发生错误：", str(e))

    # 将screenshot.png的OCR结果格式化保存至prompt.json文件中
    prompt_path = step_path + "\\prompt.json"
    prompt_data_list = []
    '''
        "top":      竖直方向与上方边界的距离
        "left":     水平方向与左边界的距离
        "width":    水平方向跨度
        "height":   竖直方向的跨度

        "x":        水平方向与左边界的距离
        "y":        竖直方向与上方边界的距离
        '''
    for words_result in s_ocr_json["words_result"]:
        ocr_dict = {"type": "text", "value": words_result["words"], "location": {}}
        ocr_dict["location"]["x"] = words_result["location"]["left"] + 0.5 * words_result["location"]["width"]
        ocr_dict["location"]["y"] = words_result["location"]["top"] + 0.5 * words_result["location"]["height"]
        prompt_data_list.append(ocr_dict)
    try:
        with open(prompt_path, 'w', encoding="utf-8") as file:
            prompt_json = json.dumps(prompt_data_list, ensure_ascii=False)
            file.write(prompt_json)
        print("OCR过程：已成功将数据保存至prompt_json")
        return None
    except Exception as e:
        print("OCR过程：数据保存至prompt_json失败，原因：", str(e))
