import os
import openai
import re


# content: 即chatGPT的输入prompt
def chatGPT_request(content):
    openai.api_key = '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'
    os.environ["HTTP_PROXY"] = "http://localhost:7890"
    os.environ["HTTPS_PROXY"] = "http://localhost:7890"

    openai.default_headers = {"x-foo": "true"}

    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": content,
                },
            ],
        )
    except Exception as e:
        print("ChatGPT Server Error : " + str(e))
        return "Error"
    # 返回ChatGPT的文字回复
    return completion.choices[0].message.content


# 将chatGPT的文字回复转化成回放建议
def chatGPT_advice(chatGPT_content):
    """
    根据chatGPT的文字回答，生成格式化的chatGPT建议
    :param chatGPT_content: String类型，chatGPT的文字回答
    :return:坐标值   如果为"-1 -1"，则表明为录制冗余
                    如果为其他坐标，则表明为回放冗余，且返回的坐标是需要操作的坐标
                    为与其他模块格式统一，该模块返回值格式为  str(int)(空格)str(int)
    """

    if chatGPT_content == "Error":
        print("chatGPT_content Error")
        return "-1 -1"

    new_string = chatGPT_content.replace("\n", "。")
    sentences = new_string.split("。")
    # 方式1：倒序遍历。用最后一个出现'录制冗余'或'回放冗余'的句子来定性
    for sentence in reversed(sentences):
        if '录制冗余' in sentence:
            return "-1 -1"
        elif '回放冗余' in sentence:
            locations = re.findall(r'\{(\d+),(\d+)\}', chatGPT_content)
            if locations is None:
                last_location = locations[-1]
                x_loc = last_location[0]
                y_loc = last_location[1]
                return str(x_loc) + " " + str(y_loc)
        return "-1 -1"
    return "无法在ChatGPT Content中解析出ChatGPT Advice。\n chatGPT_content: " + chatGPT_content


if __name__ == '__main__':
    chatGPT_content_test1 = "首先，我们需要明确录制步骤与回放步骤的目的和内容。录制步骤为点击一个控件，其信息为{相对位置：{518,1007};文本信息：null;额外信息：“是一个关闭弹窗按钮”}。这意味着，录制时的主要操作是为了关闭一个弹窗。回放步骤的控件信息都不包含“关闭弹窗”的描述或相似功能。这意味着，在当前的回放步骤中，没有出现需要点击以关闭的弹窗。综上所述：**当前的情况是“录制冗余”。**这是因为，尽管在录制步骤中明确了关闭弹窗的操作，但在回放步骤中，没有找到任何需要这样操作的弹窗。因此，无需进行额外操作，直接跳过此录制步骤，并继续进行后续操作。"

    chatGPT_content_test2 = "根据给出的信息，我们需要分析录制步骤与回放步骤的差异以确定当前的问题类型。录制步骤为：点击控件，控件信息为{相对位置：{518,1007};文本信息：null;额外信息：“是一个关闭弹窗按钮”}。在回放步骤界面中，我们没有看到与录制步骤完全匹配的控件。然而，我们可以找到一个接近{518,1007}的控件，即控件5，其相对位置为{267.0, 1004.5}，并且其文本信息为：“搜索CookidooTM”。根据录制步骤的描述，我们期望找到一个文本信息为null的控件，并且这个控件是一个关闭弹窗的按钮。由于我们没有找到完全匹配的控件，**我们可以判断：当前状况是“回放冗余”。**对于“回放冗余”的情况，我们建议操作：点击控件5：“搜索CookidooTM”。"
    print(chatGPT_request(chatGPT_content_test1))
    # print(chatGPT_advice(chatGPT_content_test2))
