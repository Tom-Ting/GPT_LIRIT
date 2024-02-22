# -*- coding: utf-8 -*-
import os
import json


widget_types = {"add": "加号，添加新页面、新数据等",
                "arrow_down": "向下箭头，向下滑动页面，翻到下一页等",
                "arrow_left": "向左箭头，返回上级页面、向左滑动页面等",
                "check_mark": "check mark，确认、正确、打勾、已检查等",
                "close": "叉，关闭页面、禁止操作、出现异常等",
                "delete": "删除，删除等",
                "menu": "菜单，菜单等",
                "settings": "设置，设置等",
                "share": "分享，分享、导出等",
                "other": "其他或未识别，null",
                }


def prompt_generate(record_element_path, prompt_path):
    """
    利用数据源，生成ChatGPT可接受的prompt
    数据源：info.json  widget_ocr_result.json  prompt.json
    无文件生成
    :param record_element_path: 以element.png结尾
    :param prompt_path: 以prompt.json结尾
    :return: 字符串类型的变量；若无法生成，则返回空串
    """
    str1 = "现在，你是一个经验丰富的软件测试工程师，需要完成录制回放的任务。该任务的主要目标是在回放(replay)设备上模拟在录制(record)设备上的录制(record)操作。测试团队中的你的其他同事已经完成了其他任务。你的任务是，根据录制信息和当前的回放页面信息，判断当前测试存在“录制冗余”，还是“回放冗余”。二者只能二选一，既不能同时存在，也不能同时不存在。" \
           "\n\n" \
           "下面举一个例子来说明回放冗余。录制步骤为点击控件，控件信息为{相对位置：0.4,0.1;文本信息：“会议信息”;}。此时，回放步骤界面有如下控件：" \
           "\n控件A：{相对位置：0.3,0.6;文本信息：“拒绝”;}；" \
           "\n控件B：{相对位置：0.6,0.6;文本信息：“允许”;}；" \
           "\n控件C：{相对位置：0.5,0.4;文本信息：“腾讯会议想使用你的语音权限”;}；" \
           "\n控件D：{相对位置：0.9,0.1;文本信息：“宫格视图”;}；" \
           "\n控件E：{相对位置：0.5,0.2;文本信息：“正在讲话”;}；" \
           "\n控件F：{相对位置：0.7,0.7;文本信息：“null”;}；" \
           "\n\n" \
           "请注意，控件F的文本信息null，这代表该控件没有文本信息。" \
           "在这个例子中，正确操作是点击控件B。因为根据控件信息推断出，当前界面可能出现了一个弹窗，可能是软件向用户申请某些权限。通过点击控件B，使弹窗消失。然后可进行下一步操作，实现录制步骤的目的。需要注意的是，点击控件A也可以关闭弹窗，但是该操作可能代表用户拒绝了软件了某个权限申请。一旦拒绝，可能引起整个软件的关闭，从而无法继续完成回放步骤。综合考虑，选择点击控件B。" \
           "\n\n" \
           "下面举一个例子来说明录制冗余。有时，多个录制步骤可能仅需要一个回放步骤就能实现，当前录制步骤不需要回放实现。录制步骤是关闭弹窗操作，而在回放时，并没有出现弹窗，因此也不需要关闭。此时，只需要跳过当前录制步骤，继续执行下一步录制步骤即可。" \
           "\n\n" \
           "你需要根据当前回放页面的控件信息进行合理的推理和判断。" \
           "\n\n" \
           "根据以上信息和实例，结合你卓越的推理和判断能力来帮助我们解决真正的问题吧！下面是一个需要你解决的问题。"

    # 以录制路径下的info.json文件内坐标作为参考
    widget_info_path = os.path.dirname(record_element_path) + "\\info.json"
    try:
        with open(widget_info_path, 'r', encoding="utf-8") as file:
            widget_info = json.load(file)
            recordX = widget_info["x"]
            recordY = widget_info["y"]
    except Exception as e:
        print("录制控件位置读取错误！路径为" + widget_info_path)
        print("错误类型为" + str(e))

    # 读取录制控件文本信息（OCR结果）
    widget_text = ""
    widget_text_path = os.path.dirname(record_element_path) + "\\widget_ocr_result.json"
    try:
        with open(widget_text_path, 'r', encoding="utf-8") as file:
            widget_info = json.load(file)
            widget_text = widget_info["words_result"][0]["words"]
    except Exception as e:
        print("录制控件OCR结果读取错误！路径为" + widget_text_path)
        print("错误类型为" + str(e))

    # 读取控件类型信息（模型识别结果）
    element_type = ""
    element_type_path = os.path.dirname(record_element_path) + "\\element_widget_type.json"
    try:
        with open(element_type_path, 'r', encoding="utf-8") as file:
            element_type = file.read()
    except Exception as e:
        print("录制控件OCR结果读取错误！路径为" + element_type_path)
        print("错误类型为" + str(e))
    str2 = "已知的录制步骤为：点击控件，控件信息为{相对位置：{" + str(recordX) + "," + str(recordY) + "};文本信息：" + widget_text + ";额外信息：" + widget_types[element_type] + "}\n\n"

    str4 = "首先请告诉我当前状况，是“录制冗余”，还是“回放冗余”？如果是录制冗余，则不需要进行额外操作。如果是回放冗余，请告诉我对哪一个位置坐标的哪一个控件进行什么样的操作。请告诉我你的判断和选择。如果有不明白的地方，请告诉我。确保你的回答是经过推测和准确的。"
    if not os.path.exists(prompt_path):
        print("prompt_generate Error: prompt.json文件不存在!")
        return ""
    if os.stat(prompt_path).st_size == 0:
        print("prompt_generate Error: prompt.json文件为空文件！")
        return ""
    try:
        with open(prompt_path, 'r', encoding="utf-8") as file:
            prompts = json.load(file)
            N = 1
            str3 = "回放步骤界面有如下控件：\n\n"
            for prompt in prompts:
                if prompt["type"] == "text":
                    str3 += "控件" + str(N) + "：{相对位置：" + str(prompt["location"]["x"]) + ", " + str(prompt["location"]["y"]) + ";文本信息：“" + prompt["value"] + "”;}；" + "\n"
                else:
                    str3 += "控件" + str(N) + "：{相对位置：" + str(prompt["location"]["x"]) + ", " + str(prompt["location"]["y"]) + "”;额外信息：“" + widget_types[prompt["type"]] + "”}；" + "\n"
                N += 1
        return str1 + str2 + str3 + str4
    except Exception as e:
        print("prompt_generate Error!")
        print("prompt_path: " + prompt_path)
        print("Error info: " + str(e))
        return ""


if __name__ == '__main__':
    record_element_path = r"C:\MyGraduation\database_test\MapLIRATDatabase\dianpingApp\script1\android\step2" + r"\element.png"
    prompt_path = r"C:\MyGraduation\database_test\MapLIRATDatabase\dianpingApp\script1\android\step2" + r"\prompt.json"
    prompt_generate(record_element_path, prompt_path)
