
import os
import cv2
import sys
sys.path.append('/home/slishy/Code/ACT/pyorbbecsdk/install/lib')
# from pyorbbecsdk import *
from or_utils import frame_to_bgr_image
def initialize_pipeline(device):
    """
    Initialize the Orbbec SDK pipeline and configuration.

    :return: Initialized pipeline and configuration.
    """
    device.set_bool_property(OBPropertyID.OB_PROP_COLOR_AUTO_EXPOSURE_BOOL, auto_exposure)
    pipeline = Pipeline(device)
    config = Config()
    profile_list = pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
    color_profile: VideoStreamProfile = profile_list.get_default_video_stream_profile()
    config.enable_stream(color_profile)

    # Start the pipeline
    pipeline.start(config)
    return pipeline

def capture_color_image(pipeline):
    try:
        while True:
            frames = pipeline.wait_for_frames(100)  # Wait for frames
            if frames is None:
                continue

            color_frame = frames.get_color_frame()  # Get the color frame
            if color_frame is not None:
                image = frame_to_bgr_image(color_frame)
                image = cv2.resize(image, (640, 480), interpolation=cv2.INTER_AREA)
                if image is None:
                    print("Failed to convert frame to image")
                    return None
                return image
    except KeyboardInterrupt:
        print("Process interrupted by user")
        return None
    # finally:
    #     pipeline.stop()

# Example usage
if __name__ == "__main__":
    ctx = Context()
    device_list = ctx.query_devices()
    print('######################',device_list.get_count())
    device1 = device_list.get_device_by_index(2)
    device2 = device_list.get_device_by_index(1)
    device3 = device_list.get_device_by_index(0)
    pipeline1 = initialize_pipeline(device1)
    pipeline2 = initialize_pipeline(device2)
    pipeline3 = initialize_pipeline(device3)
    pipelines = [pipeline1, pipeline2, pipeline3]
    image1 = capture_color_image(pipeline1)
    image2 = capture_color_image(pipeline2)
    image3 = capture_color_image(pipeline3)
    if image1 is not None:
        for i in range(10000):
            cv2.imshow('left',capture_color_image(pipeline1))
            cv2.imshow('middle', capture_color_image(pipeline2))
            cv2.imshow('right', capture_color_image(pipeline3))
            cv2.waitKey(10)
            print("Image captured successfully.")
    else:
        print("Failed to capture image.")
