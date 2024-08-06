import os
import xml.etree.ElementTree as ET
import cv2

def convert(size, box):
    dw = 1./size[0]
    dh = 1./size[1]
    # size0 is width, size1 is height, reciprocal for normalized coordinates

    x = (box[0] + box[1])/2.
    y = (box[2] + box[3])/2.
    # The center coordinates of the bounding box are obtained by dividing xmin+xmax by 2
    # Same for y

    w = box[1] - box[0]
    h = box[3] - box[2]
    # Get the width and height of the bounding box

    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)
    # Calculate normalized coordinates acceptable by YOLO

def convert_annotation(image_id):
    in_file = open(f'../annotations/{image_id}')
    out_file = open(f'../label/{image_id}.txt', 'w')
    # Define input and output files for annotation processing

    tree = ET.parse(in_file)
    root = tree.getroot()
    # Get the root element of the XML

    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
    # Find the size tag and extract the width and height text content
    # Convert them to integers

    for obj in root.iter('object'):
        # Iterate over all object tags in the XML file

        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        # Get the detection difficulty and class name of the object

        if cls not in classes or int(difficult) == 1:
            continue
        # Skip if the object is not a license plate and is difficult to detect
        # Difficult objects increase training complexity and reduce model accuracy, so it's best to skip them

        cls_id = classes.index(cls)
        # Extract the index
        # Since the training data only has license plates, you can just write 0 here
        # The classes list is actually unnecessary
        # But for code readability, it's better to write it out

        xmlbox = obj.find('bndbox')
        box = (
            float(xmlbox.find('xmin').text),
            float(xmlbox.find('xmax').text),
            float(xmlbox.find('ymin').text),
            float(xmlbox.find('ymax').text)
        )
        # Extract bounding box coordinates and convert them to a tuple of floats

        convert_box = convert((w, h), box)
        # Pass into the convert function for normalization

        out_file.write(f"{cls_id} "+ " ".join([str(a) for a in convert_box]) + "\n")
        # Write the class index and bounding box coordinates to the file

if __name__ == '__main__':

    classes = ["licence"]

    if not os.path.exists('../label'):
        os.mkdir('../label')

    for image_id in os.listdir('../annotations'):
        convert_annotation(image_id)
        # Loop through XML files for processing
