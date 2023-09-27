#====================================#
# Date: 2023.8.19
#====================================#
import os
import cv2
from base_camera import BaseCamera
import time

#====================================#
# Camera
#====================================#
class Camera(BaseCamera):
    video_source = 0 #select camera, 0 for default camera

    def __init__(self):
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()

            # get local time
            timeArray = time.localtime()
            otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            cv2.putText(img, str(otherStyleTime), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()