CVAT video to YOLO image annotation converter 

A script that takes a directory of videos and their accompanying CVAT video annotation files and converts the annotations to YOLO format and splits the videos into frames. For each video, annotation file pair, a directory is created with the video name and contains image and annotation subdirectories that contain a frame and annotation for each frame. 

This script is built to convert CVAT annotations constructed with CVAT's track feature. The label mapping is specific to BOSL SharkEye project.
