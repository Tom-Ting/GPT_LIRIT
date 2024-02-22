import json

if __name__ == "__main__":
    prompt_path = r"C:\MyGraduation\database_test\MapLIRATDatabase\dianpingApp\script1\android\step1\prompt.json"
    with open(prompt_path, 'r', encoding='utf-8') as file:
        data_json_list = json.load(file)
        print(data_json_list)
        print(type(data_json_list))

    data_json_list = data_json_list + data_json_list
    with open(prompt_path, 'w', encoding='utf-8') as file:
        data_json = json.dumps(data_json_list, ensure_ascii=False)
        file.write(data_json)
        # 两个list要合并
        print("成功写入数据！")
