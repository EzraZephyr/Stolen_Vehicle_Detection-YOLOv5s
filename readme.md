# YOLOv5s Stolen Vehicle Detection System

English /  [中文](readme_zh.md)

↑ 点击切换语言

This project trains a license plate dataset using a pretrained YOLOv5s model, extracts license plates using EasyOCR, and formats them to match the UK license plate style. It then compares them against the license plates in the "database" of stolen vehicles to identify if a stolen vehicle appears.

Below are screenshots from the out_demo video.

![Demo](demo.png)

Because only a 20-second video was used for demonstration, a list of "stolen vehicles" was directly defined in the code. For real-time monitoring, you can use Tkinter to update the data in real time.

After video processing is complete, the following results can be obtained, including the suspected stolen vehicles and the times they appeared.

| Suspected Stolen Vehicle | Time                |
|--------------------------|---------------------|
| GX15 OGJ                 | 2024-08-05 21:25:15 |
| AP05 JEO                 | 2024-08-05 21:25:21 |

## Table of Contents

- [Multilingual Annotations](#multilingual-annotations)
- [Dataset](#dataset)
- [File Structure](#file-structure)
- [Contributions](#contributions)

## Multilingual Annotations

To make the code easier to understand for developers from different language backgrounds, the annotations in this project are provided in both English and Chinese.

## Dataset

The license plate dataset used in this project is sourced from [Kaggle](https://www.kaggle.com/datasets/andrewmvd/car-plate-detection)

Since the license plate dataset is pretty large, please download is yourself.

The YOLOv5 model is sourced from [Github](https://github.com/ultralytics/yolov5)

The demo video is sourced from [Pexels](https://www.pexels.com/video/traffic-flow-in-the-highway-2103099/)

Please download the dataset directly from the provided links.

## File Structure

The file structure of the project is as follows:

```c++
Stolen_Vehicle_Detection 
│
├── annotations/
│   └── *.xml
│
├── images/
│   └── *.png
│
├── label/
│   └── *.txt
│
├── utils(en/zh)/
│   ├── yolov5
│   ├── __init__.py
│   ├── data_process.py
│   ├── test.py
│   ├── train.ipynb
│   └── yolov5s.pt
│
└── main.py 
```

## Contributions

All forms of contributions are welcome! Whether it's reporting errors or making suggestions, your input is greatly appreciated!