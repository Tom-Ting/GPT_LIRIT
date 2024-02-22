import json
import os
import cv2
import numpy as np
from vgg16 import pred

widget_types = {"add": ["加号", "添加新页面、新数据等"],
                "arrow_down": ["向下箭头", "向下滑动页面，翻到下一页等"],
                "arrow_left": ["向左箭头", "返回上级页面、向左滑动页面等"],
                "check_mark": ["check mark", "确认、正确、打勾、已检查等"],
                "close": ["叉", "关闭页面、禁止操作、出现异常等"],
                "delete": ["删除", "删除等"],
                "menu": ["菜单", "菜单等"],
                "settings": ["设置", "设置等"],
                "share": ["分享", "分享、导出等"],
                "other": ["其他或未识别", "null"],
                }


def my_resize(im, target_height, target_width):
    """
    功能

    Parameters:
    a (int): The first number.
    b (int): The second number.

    Returns:
    int: The sum of a and b.
    """
    height, width = im.shape[:2]  # 取彩色图片的长、宽。

    ratio_h = height / target_height
    ration_w = width / target_width

    ratio = max(ratio_h, ration_w)

    # 缩小图像  resize(...,size)--size(width，height)
    size = (int(width / ratio), int(height / ratio))
    try:
        shrink = cv2.resize(im, size, interpolation=cv2.INTER_AREA)  # 双线性插值
        tianchong = [255, 255, 255]
    except Exception:
        print("image: ", im)
        print("size: ", size)
        print(Exception)
        raise

    a = (target_width - int(width / ratio)) / 2
    b = (target_height - int(height / ratio)) / 2

    constant = cv2.copyMakeBorder(shrink, int(b), int(b), int(a), int(a), cv2.BORDER_CONSTANT, value=tianchong)
    constant = cv2.resize(constant, (target_width, target_height), interpolation=cv2.INTER_AREA)
    return constant


def cut(path, left, upper, right, lower):
    """
    按矩形剪切图片。不修改原图片
    :param path: 图片路径
    :param left: 左边界
    :param upper: 上边界
    :param right: 右边界
    :param lower: 下边界
    :return: 剪切后的图片
    """
    img = cv2.imread(path)  # 打开图像
    cropped = img[upper:lower, left:right]
    return cropped


def canny_boundings(image, canny_sigma=0.33, dilate_count=4):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 色彩空间转换
    v = np.median(gray)
    # 修改阈值，用于识别关闭符号，屏蔽背景的影响
    # todo 需要一个更好地方法来选择阈值
    # lower_threshold = int(max(0, (1 - canny_sigma) * v))
    upper_threshold = int(min(255, (1 + canny_sigma) * v))
    img_binary = cv2.Canny(gray, 120, upper_threshold, -1)
    # cv2.imshow("1",img_binary)
    # cv2.waitKey(0)
    img_dilated = cv2.dilate(img_binary, None, iterations=dilate_count)
    # cv2.imshow("2", img_dilated)
    # cv2.waitKey(0)
    contours, _ = cv2.findContours(img_dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Find bounding using contours.
    boundings = []
    for c in contours:
        boundings.append(cv2.boundingRect(c))
    return boundings


def boundings_sorting_by_x_y(boundings: list, cal_x, cal_y):
    """
    用于排序外边框，从左上到右下
    :param boundings:
    :param cal_y:
    :param cal_x:
    :return:
    """
    return sorted(boundings, key=lambda x: ((x[0] + x[2] / 2 - cal_x) ** 2 + (x[1] + x[3] / 2 - cal_y) ** 2))


def process_bounding(img, bounding_list):
    """
    对图片边界做筛选和处理，并返回新的边界
    :param img: 图片
    :param bounding_list:  处理前边界列表
    :return: 处理后边界列表
    """
    non_blanks = []
    i_h, i_w, _ = img.shape
    # 删除了全白或全黑  筛除过小的部件
    # todo 下面的面积筛选阈值需要调整
    for bounding in bounding_list:
        x, y, w, h = bounding
        node = img[y:y + h, x:x + w, :]
        # np.count_nonzero(ndarray) : 统计矩阵中非0元素的个数
        if not np.count_nonzero(node) == 0 and not np.count_nonzero(255 - node) == 0 and w * h > i_w * i_h * 0.0005:
            non_blanks.append(bounding)

    enlarge_width = 5
    img_h, img_w, _ = img.shape
    enlarged_bounding = []
    for x, y, w, h in non_blanks:
        enlarged_x = max(0, x - enlarge_width)
        enlarged_y = max(0, y - enlarge_width)
        enlarged_w = min(w + 2 * enlarge_width, img_w - enlarged_x)
        enlarged_h = min(h + 2 * enlarge_width, img_h - enlarged_y)
        enlarged_bounding.append((enlarged_x, enlarged_y, enlarged_w, enlarged_h))
    draw_rectangle_show_save(img, enlarged_bounding, "/enlarged_image.png")
    return enlarged_bounding


def draw_rectangle_show_save(src, bboxs, output_path, show=False, show_title='image', line=3, color=(0, 255, 255)):
    """
    用于
    :param show:
    :param src: 图片
    :param bboxs: 边界列表
    :param output_path: 图片名称
    :return:
    """
    image = src.copy()
    for bbox in bboxs:
        x, y, w, h = bbox
        """
        cv2.rectangle(img, pt1, pt2, color, thickness=None, lineType=None, shift=None)
        用于绘制矩形框
        :param img: 图片
        :param pt1: 矩形左上角
        :param pt2: 矩形右下角
        :param color: 线条颜色
        :param thickness: 线条粗细（以像素为单位）
        :return: 无
        """
        cv2.rectangle(image, (x, y), (x + w, y + h), color, line)
    # 创建路径，并写入
    if show:
        cv2.imshow(show_title, image)
        cv2.waitKey(0)


def extract(image_path):
    image = cv2.imread(image_path)
    assert image is not None, 'Cannot read the image file %s.' % image_path
    boundings = canny_boundings(image)
    draw_rectangle_show_save(image, boundings, "/extract_image.png")
    return boundings


def image_type_match(screen_path):
    """
    从图片中找出对应类型的图标
    :param screen_path: 回放图片路径，该图片也是被控件匹配的对象
    :return: widget_types_and_locations；返回匹配到的控件列表
    """
    # 图像匹配
    screen_img = cv2.imread(screen_path)
    transformer_x = 0
    transformer_y = 0

    # 获得经过筛选的边界
    boundarys = boundings_sorting_by_x_y(process_bounding(screen_img, extract(screen_path)), transformer_x,
                                         transformer_y)
    widget_types_and_locations = []
    for boundary in boundarys:
        left, upper, right, lower = boundary[0], boundary[1], boundary[2] + boundary[0], boundary[3] + boundary[1]
        try:
            cropped = cut(screen_path, left, upper, right, lower)  # 不用把图保存下来，直接做参数就好
            # 填充到正方形
            new_size = max(right - left, upper - lower)
            cropped = my_resize(cropped, new_size, new_size)
            # 判断该控件的类型
            widget_type = pred(cropped)
            location_xy = [int((left + right) / 2), int((upper + lower) / 2)]

            widget_type_and_location = {"type": "",
                                        "value": "",
                                        "location": {}
                                        }
            if widget_type in widget_types and widget_type != "other":
                widget_type_and_location["type"] = widget_type
                widget_type_and_location["location"]["x"] = location_xy[0]
                widget_type_and_location["location"]["y"] = location_xy[1]
                widget_types_and_locations.append(widget_type_and_location)
        except Exception:
            print("boundary: ", boundary)
            print("left, upper, right, lower = ", left, upper, right, lower)

    screenshot_widget_info_path = os.path.dirname(screen_path) + r"\screenshot_widget_info.json"
    with open(screenshot_widget_info_path, 'w') as file:
        data_str = json.dumps(widget_types_and_locations, ensure_ascii=False)
        file.write(data_str)
    print("控件识别：成功将screenshot的控件信息数据写入screenshot_widget_info.json")

    prompt_path = os.path.dirname(screen_path) + r"\prompt.json"

    data_json_list = widget_types_and_locations
    # 判断文件是否存在或为空
    if os.path.exists(prompt_path):
        file_size = os.stat(prompt_path).st_size
        if file_size != 0:
            # 如果文件存在且不为空，则从本地文件提取旧数据
            with open(prompt_path, 'r', encoding='utf-8') as file:
                olddata_json_list = json.load(file)
                # 旧数据合并新数据
                data_json_list = olddata_json_list + widget_types_and_locations

    with open(prompt_path, 'w', encoding='utf-8') as file:
        data_json = json.dumps(data_json_list, ensure_ascii=False)
        file.write(data_json)
        print("控件识别：成功将控件识别信息写入数据！")
    return widget_types_and_locations
	
	
def widget_type_match(widget_path):
    """
    从控件图片中找出对应类型的图标
    :param widget_path: 控件图片路径
    :return: widget_type；返回匹配到的控件列表
    """
    # 图像匹配
    widget_img = cv2.imread(widget_path)
    widget_type = pred(widget_img)
    element_widget_type_path = os.path.dirname(widget_path) + r"\element_widget_type.json"
    with open(element_widget_type_path, "w", encoding='utf-8') as file:
        file.write(widget_type)


if __name__ == '__main__':
    # a = r"C:\MyGraduation\database_test\MapLIRATDatabase\dianpingApp\script1\android\step1\screenshot.png"
    # image_type_match(a)

    # 测试控件类型的函数
    step_path = r"C:\MyGraduation\database_test\MapLIRATDatabase\dianpingApp\script1\android\step2"
    widget_path = step_path + r"\element.png"
    widget_type_match(widget_path)
