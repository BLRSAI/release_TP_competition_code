import cv2
from Camera import Camera
from math import radians
import torch
from grip.detectorfour import GripPipeline


class RingDetector:
    def __init__(self, file="./weights/best.pt", camera_pitch=30, grip=False):
        self.file = file
        self.model = self.load_model()
        self.camera = Camera(camera_pitch=-radians(camera_pitch))
        self.gripDetector = GripPipeline()
        self.grip = grip

    def load_model(self):
        model = torch.hub.load('ultralytics/yolov5', 'custom', path=self.file, force_reload=False, skip_validation=True)
        return model

    def inference(self, n):
        # This function call is intended to be made by the comeptition code.
        # It will return the nearest detected rings padded with zeros to size n.
        # It uses the CNN above to detect all the rings in the image,
        # then it uses the Realsense for localization.

        # This code can be refactored for better performance, probably

        img, depth_map = self.camera.get_image()

        if self.grip:
            # Toggles if it should get ran through the grip pipeline (classical cv) or not 
            self.gripDetector.process(img)
            img = self.gripDetector.mask_output

        rings = []

        pred = self.model(img)

        color = (0, 0, 255)
        # label 0 is a ring
        for row in pred.pandas().xyxy[0].iterrows():
            p1 = (int(row[1]["xmin"]), int(row[1]["ymin"]))
            p2 = (int(row[1]["xmax"]), int(row[1]["ymax"]))
            img = cv2.rectangle(img, p1, p2, color, 1)
                       
            xmax = row[1]["xmax"]
            xmin = row[1]["xmin"]
            ymin = row[1]["ymin"]
            ymax = row[1]["ymax"]  
            x = (((xmax - xmin)//2)+xmin)
            y = (((ymax - ymin)//2)+ymin)    

            # Get the depth at pixel (x, y)
            depth = depth_map.get_distance(int(x), int(y))

            # Gets the relative ring positions to the robot
            distance = self.camera.get_relative_ring_position(x, y, depth)

            if depth != 0: rings.append([depth, distance])

        # Sorts by distance to robot
        rings.sort(key=lambda x: x[0])

        # Returns only relative ring positions
        ret = [item for sublist in rings for item in sublist[1]]
        
        # Either pad the return list with 0s or take first n*2 values
        if len(ret) > n*2: ret = ret[:n*2]
        else: ret += [0] * (n*2 - len(ret))

        return ret


