import cv2
import torch
import easyocr
from datetime import datetime

stolen_vehicles = ['GX15 OGJ', 'AP05 JEO', 'NA54 ABG']
suspected_stolen_vehicles = []
# 建立被盗车辆和检测出来的疑似被盗车辆的车牌列表

model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5/runs/train/exp/weights/last.pt').cuda()
# 加载模型并使用cuda进行处理

video_path = '../demo.mp4'
# 设置视频文件路径

cap = cv2.VideoCapture(video_path)
# 通过VideoCapture打开视频文件

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
# 获取视频帧的宽度、高度和帧率

window_width = 1920
window_height = 1080
# 设置窗口大小

reader = easyocr.Reader(['en'])
# 初始化EasyOCR读取器并设置英文

def correct_recognition(text):

    corrections = {
        'S': '5', 'O': '0', 'I': '1', 'B': '8', 'G': '6', 'Q': '0', 'Z': '2',
        '5': 'S', '0': 'O', '1': 'I', '8': 'B', '6': 'G', '2': 'Z'
    }
    # 定义常见识别错误字符的替换

    if len(text) >= 4:
        if text[2].isalpha():
            text = text[:2] + corrections.get(text[2], text[2]) + text[3:]
        if text[3].isalpha():
            text = text[:3] + corrections.get(text[3], text[3]) + text[4:]
        # 按照英国车牌的规律进行测试 如果第三个字符和第四个字符为字母的话
        # 则去字典里查找是否可以替换 如果可以替换则替换后拼接输出 否则直接输出

    if len(text) == 7:
        for i in range(4, 7):
            if text[i].isdigit():
                text = text[:i] + corrections.get(text[i], text[i]) + text[i + 1:]
            # 后三位字符在英国车牌规律为字母 因此如果检测出数字则查找替换

    return text

output_path = '../out_demo.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
# 传入输出的文件路径 定义的解码器 视频帧率和帧数的宽高


with (open('../stolen_vehicles.txt','w') as f):
    # 打开记录疑似被盗车辆信息的文件

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # 打开视频捕获 并读取每一帧
        # ret是一个布尔值 表示是否成功读取到了视频帧 frame是读取帧数的信息
        # 如果ret为false则证明读取失败或者视频结束 则跳出循环

        results = model(frame)
        # 预测结果

        for pred in results.pred[0].cpu().numpy():
            # 将所有的结果转移到cpu上供numpy处理
            # 并用pred遍历每个预测到的检测框

            x1, y1, x2, y2, conf, cls = pred
            # 提取出检测框的坐标 置信度和类别

            if int(cls) == 0:
                # 这个if是多余的 但是为了代码的可读性还是写出来比较好

                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                # 在图像上绘制一个绿色的边框 宽度为2个像素

                plate_img = frame[int(y1):int(y2), int(x1):int(x2)]
                result = reader.readtext(plate_img)
                # 将预测的车牌位置剪裁下来并用EasyOCR的readtext方法进行字符识别

                if result:

                    text = result[0][-2]
                    # 这里解释一下为什么选择0和-2
                    # EasyOCR返回的结果通常是以下格式
                    # [[1, 2], [3, 4], [5, 6], [7, 8], 'ABC123', 0.88]
                    # 分别为四个坐标(左上、右上、右下、左下)也就是识别出的文字的坐标
                    # 然后是识别结果(-2)和置信度
                    # 结果是一个二维列表 其中每个元素是一个一维列表 包含上述信息
                    # 选择0是因为在处理单个车牌图像时 车牌通常是最显著的特征
                    # 因此有理由相信第一个检测结果就是车牌

                    cleaned_text = ''.join(filter(str.isalnum, text))
                    # 通过isalnum方法只保留识别结果中的字母和数字

                    if len(cleaned_text) == 7:

                        corrected_text = correct_recognition(cleaned_text.upper())
                        corrected_text = corrected_text[:4] + ' ' + corrected_text[4:]
                        # 等correct_recognition函数处理完之后 把前四个字符和后三个字符中间加上空格
                        # 以符合车牌标准格式

                        if corrected_text in stolen_vehicles and corrected_text not in suspected_stolen_vehicles:
                            suspected_stolen_vehicles.append(corrected_text)
                            # 如果该车牌属于被盗车辆且之前没有被识别过 则添加到疑似列表中

                            text = f'Suspected stolen vehicle: {corrected_text}'
                            # current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            # 记录当前时间 这个主要用于实时识别 视频识别可不加
                            print(text)
                            f.write(text + ' at ' + '''current_time''' + '\n')
                            # 将识别信息写入文件

                        font_scale = 0.6
                        font_thickness = 1
                        # 设置缩放比例和厚度
                        text_size, _ = cv2.getTextSize(corrected_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
                        # 并且计算在上述字体 缩放比例和厚度的情况下文本应该显示的宽度和高度

                        text_w, text_h = text_size
                        cv2.putText(frame, corrected_text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), font_thickness)
                        # 提取文本的高度宽度 上移十个像素防止与边界框重叠并设置成绿色

        out.write(frame)
        # 将处理后的图像写入视频文件中

        resized_frame = cv2.resize(frame, (window_width, window_height))
        cv2.imshow('License Palate Detection', resized_frame)
        # 调整帧大小以适应窗口 并设置窗口名称 显示

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # 等待键盘事件 如果按倒了q就结束程序

cap.release()
out.release()
cv2.destroyAllWindows()
# 释放视频捕获对象和输出视频对象 并关闭创建的窗口
