import os
import xml.etree.ElementTree as ET

import cv2


def convert(size, box):
    dw = 1./size[0]
    dh = 1./size[1]
    # size0为宽度 size1为高度 求倒数用于归一化坐标

    x = (box[0] + box[1])/2.
    y = (box[2] + box[3])/2.
    # 用xmin+xmax除2得到的就是边界框的中心坐标
    # y同理

    w = box[1] - box[0]
    h = box[3] - box[2]
    # 得到边界框的宽度和高度

    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)
    # 计算出来yolo可接受的归一化坐标

def convert_annotation(image_id):
    in_file = open(f'../annotations/{image_id}')
    out_file = open(f'../label/{image_id}.txt', 'w')
    # 定义处理标注的输入文件和输出文件

    tree = ET.parse(in_file)
    root = tree.getroot()
    # 获取xml的根元素

    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
    # 找到size标签 提取其内部的width和height的文本内容
    # 并将其转换为整数

    for obj in root.iter('object'):
        # 遍历xml文件中所有的object标签

        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        # 获取物体的检测难度和类别名称

        if cls not in classes or int(difficult) == 1:
            continue
        # 如果物体不为车牌且难检测的话直接跳过
        # 难检测的对象会增加训练复杂度和降低模型精度 所以跳过最好

        cls_id = classes.index(cls)
        # 提取索引
        # 因为训练数据只有车牌 所以其实这里直接写0就可以
        # 包括classes这个列表也是不必要的
        # 但是为了代码的可读性还是写出来比较好

        xmlbox = obj.find('bndbox')
        box = (
            float(xmlbox.find('xmin').text),
            float(xmlbox.find('xmax').text),
            float(xmlbox.find('ymin').text),
            float(xmlbox.find('ymax').text)
        )
        # 提取边界框坐标 并转换为浮点数元组

        convert_box = convert((w, h), box)
        # 投入convert函数进行归一化处理

        out_file.write(f"{cls_id} "+ " ".join([str(a) for a in convert_box]) + "\n")
        # 将类别索引和边界框坐标写入文件

if __name__ == '__main__':

    classes = ["licence"]

    if not os.path.exists('../label'):
        os.mkdir('../label')

    for image_id in os.listdir('../annotations'):
        convert_annotation(image_id)
        # 循环传入xml文件处理
