import cv2
import torch
import easyocr
from datetime import datetime

stolen_vehicles = ['GX15 OGJ', 'AP05 JEO', 'NA54 ABG']
suspected_stolen_vehicles = []
# Create lists for stolen vehicles and detected suspected stolen vehicles

model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5/runs/train/exp/weights/last.pt').cuda()
# Load the model and use CUDA for processing

video_path = '../demo.mp4'
# Set video file path

cap = cv2.VideoCapture(video_path)
# Open the video file using VideoCapture

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
# Get the width, height, and frame rate of the video

window_width = 1920
window_height = 1080
# Set the window size

reader = easyocr.Reader(['en'])
# Initialize EasyOCR reader and set it to English

def correct_recognition(text):

    corrections = {
        'S': '5', 'O': '0', 'I': '1', 'B': '8', 'G': '6', 'Q': '0', 'Z': '2',
        '5': 'S', '0': 'O', '1': 'I', '8': 'B', '6': 'G', '2': 'Z'
    }
    # Define replacements for common recognition errors

    if len(text) >= 4:
        if text[2].isalpha():
            text = text[:2] + corrections.get(text[2], text[2]) + text[3:]
        if text[3].isalpha():
            text = text[:3] + corrections.get(text[3], text[3]) + text[4:]
        # According to the UK license plate pattern, if the third and fourth characters are letters,
        # check the dictionary for replacements. If a replacement is found, replace and output;
        # otherwise, output directly

    if len(text) == 7:
        for i in range(4, 7):
            if text[i].isdigit():
                text = text[:i] + corrections.get(text[i], text[i]) + text[i + 1:]
                # The last three characters of UK license plates are letters, so if a digit is detected,
                # check for replacements

    return text

output_path = '../out_demo.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
# Set the output file path, define the codec, frame rate, and frame size


with open('../stolen_vehicles.txt','w') as f:
    # Open the file to record suspected stolen vehicle information

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # Open video capture and read each frame
        # ret is a boolean indicating if a frame was successfully read; frame contains the frame information
        # If ret is false, it means reading failed or the video ended, so break the loop

        results = model(frame)
        # Get prediction results

        for pred in results.pred[0].cpu().numpy():
            # Transfer all results to the CPU for numpy processing
            # Use pred to iterate over each detected bounding box

            x1, y1, x2, y2, conf, cls = pred
            # Extract the coordinates of the bounding box, confidence, and class

            if int(cls) == 0:
                # This if is redundant, but for code readability, it's written here

                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                # Draw a green rectangle on the image with a thickness of 2 pixels

                plate_img = frame[int(y1):int(y2), int(x1):int(x2)]
                result = reader.readtext(plate_img)
                # Crop the predicted license plate position and use EasyOCR's readtext method for character recognition

                if result:

                    text = result[0][-2]
                    # Here, explain why choose 0 and -2
                    # EasyOCR returns results in the following format
                    # [[1, 2], [3, 4], [5, 6], [7, 8], 'ABC123', 0.88]
                    # These are the four coordinates (top-left, top-right, bottom-right, bottom-left)
                    # of the detected text
                    # Followed by the recognized text (-2) and the confidence
                    # The result is a 2D list, with each element being a 1D list containing the above information
                    # 0 is chosen because, when processing a single license plate image,
                    # the license plate is usually the most prominent feature
                    # So it is reasonable to believe the first detected result is the license plate

                    cleaned_text = ''.join(filter(str.isalnum, text))
                    # Keep only letters and numbers from the recognized result using the isalnum method

                    if len(cleaned_text) == 7:

                        corrected_text = correct_recognition(cleaned_text.upper())
                        corrected_text = corrected_text[:4] + ' ' + corrected_text[4:]
                        # After the correct_recognition function processes it,
                        # add a space between the first four and the last three characters
                        # To match the license plate standard format

                        if corrected_text in stolen_vehicles and corrected_text not in suspected_stolen_vehicles:
                            suspected_stolen_vehicles.append(corrected_text)
                            # If the license plate belongs to a stolen vehicle and hasn't been recognized before,
                            # add it to the suspected list

                            text = f'Suspected stolen vehicle: {corrected_text}'
                            # current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            # Record the current time; this is mainly for real-time recognition.
                            # For video recognition, it's not necessary
                            print(text)
                            f.write(text + ' at ' + '''current_time''' + '\n')
                            # Write the recognition information to the file

                        font_scale = 0.6
                        font_thickness = 1
                        # Set font scale and thickness
                        text_size, _ = cv2.getTextSize(corrected_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
                        # Calculate the width and height the text should be displayed at with the specified font,
                        # scale, and thickness

                        text_w, text_h = text_size
                        cv2.putText(frame, corrected_text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), font_thickness)
                        # Extract the text height and width,
                        # move it up by ten pixels to avoid overlapping with the bounding box,
                        # and set it to green

        out.write(frame)
        # Write the processed image to the video file

        resized_frame = cv2.resize(frame, (window_width, window_height))
        cv2.imshow('License Plate Detection', resized_frame)
        # Resize the frame to fit the window and set the window name for display

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # Wait for a keyboard event; if 'q' is pressed, end the program

cap.release()
out.release()
cv2.destroyAllWindows()
# Release the video capture object and output video object, and close the created windows
