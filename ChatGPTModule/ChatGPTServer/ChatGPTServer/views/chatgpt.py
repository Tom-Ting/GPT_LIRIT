import os

from django.http import HttpResponse
from ChatGPTServer.utils.conversation import chatGPT_request, chatGPT_advice
from ChatGPTServer.utils.prompt import prompt_generate


def entrance(request):
    """
    作为服务的对外接口。
    :param request: 请求信息。主要包含 待回放图片 所在的文件夹路径
        record_element_path 以element.png结尾
        replay_screen_path 以screenshot.png结尾
    :return: 返回chatGPT的操作建议
    """
    record_element_path = request.GET["recordElementPath"]
    replay_screen_path = request.GET["replayScreenPath"]
    replay_screen_dir = os.path.dirname(replay_screen_path)
    chatGPT_response_path = replay_screen_dir + "\\ChatGPTResponse.txt"
    # 若不想直接读取本地文件，则在判断语句后加一个 and False
    if os.path.exists(chatGPT_response_path) and os.stat(chatGPT_response_path).st_size != 0 and False:
        with open(chatGPT_response_path, 'r', encoding='utf-8') as f:
            chatGPT_response = f.read()
        print("chatGPT_response 从已存文件中读取")
    else:
        prompt_path = replay_screen_dir + "\\prompt.json"
        ChatGPT_prompt = prompt_generate(record_element_path, prompt_path)
        with open(replay_screen_dir + "\\ChatGPT_prompt.json", "w", encoding='utf-8') as file:
            file.write(ChatGPT_prompt)
        print("chatGPT_prompt 已保存至本地")
        chatGPT_response = chatGPT_request(ChatGPT_prompt)
    try:
        with open(chatGPT_response_path, 'w', encoding='utf-8') as file:
            file.write(chatGPT_response)
        print("成功将ChatGPT的判断数据保存至文件！")
    except Exception as e:
        print(e)
        return HttpResponse("Fail")
    advice = chatGPT_advice(chatGPT_response)
    return HttpResponse(advice)


if __name__ == "__main__":
    class request:
        GET = {"replayScreenPath": r"C:\MyGraduation\database_test\MapLIRATDatabase\CookidooApp\script1\android\step1\screenshot.png"}
    entrance(request)
