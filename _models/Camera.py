import pyrealsense2 as rs
from sympy import Quaternion
import numpy as np
import math


# This camera matrix was generated using opencv's tutorial
# https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
CAMERA_MATRIX = np.array(
    [[608.38952271, 0.0, 332.60130193], [0.0, 610.59807426, 236.58507294], [0.0, 0.0, 1.0]]
)

CAMERA_MATRIX_INV = np.linalg.inv(CAMERA_MATRIX)

class Camera:
    def __init__(self, camera_pitch):
        print("Initializing camera")
        self.camera_pitch = camera_pitch
        # Create a pipeline
        self.pipeline = rs.pipeline()

        # Create a config and configure the pipeline to stream
        # different resolutions of color and depth streams
        config = rs.config()

        # Get device product line for setting a supporting resolution
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()
        device_product_line = str(device.get_info(rs.camera_info.product_line))

        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

        if device_product_line == "L500":
            config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
        else:
            config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

        # Start streaming
        profile = self.pipeline.start(config)

    def get_image(self):
        # Capture frame from camera
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        frame_image = np.asanyarray(frames.get_color_frame().get_data())

        return frame_image, depth_frame

    def get_relative_ring_position(self, x, y, depth):
        """
        Args:
            x - horizontal distance form the top left pixel of image
            y - vertical distance from the top pixel
            depth - pure depth from the camera

        Return:
            pair of values, with x and y estimate values
        """
        
        # https://homepages.inf.ed.ac.uk/rbf/CVonline/LOCAL_COPIES/EPSRC_SSAZ/node3.html
        # This takes the camera matrix and projects the ring to the camera space, then 
        # performs a rotation about the camera pitch to get the position of the ring from 
        # camera space to the real space.

        # Calculate rotation needed to convert camera space to real space, based on 
        # the camera's pitch to the ground
        camera_quaternion = Quaternion.from_axis_angle((1.0, 0, 0), float(self.camera_pitch))
        camera_rot_mtx: np.ndarray = np.array(camera_quaternion.to_rotation_matrix()).astype('float32')
        camera_rot_mtx_inv = np.linalg.inv(camera_rot_mtx)

        # Multiply the pixel's location on the image by the depth
        pixel_location = np.array([x, y, 1])
        pixel_location *= depth

        # Get the camera space location of that pixel
        camera_space_location = np.dot(CAMERA_MATRIX_INV, pixel_location)

        # Get the real space location of the pixel by rotating the camera space
        real_space_location = np.dot(camera_rot_mtx_inv, camera_space_location)

        # Return the x and z coordinates of the pixel, giving the real position of
        # the ring detected with respect to the robot
        return [real_space_location[0], real_space_location[2]]

