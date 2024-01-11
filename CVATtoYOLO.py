
import xml.etree.ElementTree as ET
import os
import cv2

### CANNOT CURRENTLY HANDLE VIDEO INPUTS WITH AND WITHOUT ACOMPANYING ANNOTATION FILES SIMULANEOUSLY ###

try:
    if not os.path.exists('data'):
        os.makedirs('data')
except OSError:
    print ('Error: Creating directory of data')


label_mapping = {
    "small_shark": 0,
    # mapping both small and large shark labels to 0 and we will only hvae one class, "gws", from here on
    "large_shark": 0,
    # Add more labels and indices as needed
    "gws": 0,
}


def extract_and_save_frames(video_folder_path, video_filename, video_data_filename):
    vid_file_path = os.path.join(video_folder_path, video_filename)
    cap = cv2.VideoCapture(vid_file_path)
    if cap.isOpened():
        current_frame = 0
        while(cap.isOpened()):
            # Capture frame-by-frame
            ret, frame = cap.read()
            if ret:
                # naming each image file frameX.jpg
                frame_filename = os.path.join("data", video_data_filename, "images") + "/frame" + str(current_frame) + '.jpg'
                print(f'Creating: {frame_filename}')
                cv2.imwrite(frame_filename, frame)
                current_frame += 1
            else:
                break
        cap.release()
    cv2.destroyAllWindows()


def extract_and_save_annotations(annotations_folder_path, annotation_filename, video_name):
    cvat_xml_path = os.path.join(annotations_folder_path, annotation_filename)
    tree = ET.parse(cvat_xml_path)
    root = tree.getroot()
    
    # Get the width and height values
    original_size_element = root.find('.//original_size')
    image_width = float(original_size_element.find('width').text)
    image_height = float(original_size_element.find('height').text)

    path_to_output_dir = os.path.join("data", video_name, "annotations")

    # CVAT format organizes annotations by tracks, each track is a unique shark in a video - we will iterate through each 
    # track rather than each frame and update output annotation files as needed
    for track in root.findall('.//track'):
        # track_id = track.get('id')  # Get the 'id' attribute value
        label = track.get('label')  # Get the 'label' attribute value

        for box in track.findall('box'):
            xtl = float(box.get('xtl'))
            ytl = float(box.get('ytl'))
            xbr = float(box.get('xbr'))
            ybr = float(box.get('ybr'))

            # convert from x and y of the top left corner and bottom right corner to x cneter, y center, width and height
            x_center = round((xtl + xbr) / 2.0 / image_width, 7)
            y_center = round((ytl + ybr) / 2.0 / image_height, 7)
            width = round((xbr - xtl) / image_width, 7)
            height = round((ybr - ytl) / image_height, 7)

            # maps all labels to class id 0
            if label in label_mapping:
                class_id = label_mapping[label]
                yolo_line = f"{class_id} {x_center} {y_center} {width} {height}"

            # annotation filename must be same as image filename for same frame 
            frame_number = box.get('frame')
            frame_file_path = path_to_output_dir + "/frame" + str(frame_number) + ".txt"
            # If the file exists, open it in append mode and write a new line
            if os.path.exists(frame_file_path):
                with open(frame_file_path, "a") as file:
                    file.write(yolo_line + "\n")
            # if it does not exist write a new annotation file for the frame
            else:
                with open(frame_file_path, "w") as file:
                    file.write(yolo_line + "\n")
            file.close()


def convert(vid_subdirectory_name, an_subdirectory_name):
    # Get the paths to the subdirectories
    vid_folder_path = os.path.join(os.getcwd(), vid_subdirectory_name)
    an_folder_path = os.path.join(os.getcwd(), an_subdirectory_name)

    # eliminate hidden files and sort alphabetically
    videos = [x for x in os.listdir(vid_folder_path) if not x.startswith(".")]
    annotations = [x for x in os.listdir(an_folder_path) if not x.startswith(".")]
    videos.sort()
    annotations.sort()

    if len(annotations) > 0 and len(annotations) != len(videos):
        print("CANNOT CURRENTLY HANDLE VIDEO INPUTS WITH AND WITHOUT ACOMPANYING ANNOTATION FILES SIMULANEOUSLY ie. a >1 uneven number of annotation and video file")

    # just splitting video without a shark into frames
    elif len(annotations) == 0:
        for vid_filename in videos:
            # get video name
            video_name = vid_filename.split(".")[0]
            # make video  directory and subdirectories in the data folder 
            os.makedirs(os.path.join("data", video_name))
            os.makedirs(os.path.join("data", video_name, "images"))
            os.makedirs(os.path.join("data", video_name, "annotations"))

            extract_and_save_frames(vid_folder_path, vid_filename, video_name)   
    else:
        for vid_filename, an_filename in zip(videos, annotations):
            # get video name
            video_name = vid_filename.split(".")[0]
            # make video data directory and subdirectories in the data folder
            os.makedirs(os.path.join("data", video_name))
            os.makedirs(os.path.join("data", video_name, "images"))
            os.makedirs(os.path.join("data", video_name, "annotations"))
        
            extract_and_save_frames(vid_folder_path, vid_filename, video_name)
            # extract annotations 
            extract_and_save_annotations(an_folder_path, an_filename, video_name)


if __name__ == '__main__':
    convert("videos", "annotations")







