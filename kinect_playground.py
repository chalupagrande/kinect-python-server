from freenect2 import Device, FrameType
import numpy as np
import json
import cv2
import time
import threading  # Import the threading module
import asyncio
import zlib
# import asyncio
# from websockets.client import connect

websocket_address = 'ws://192.168.86.159:8080'

device = Device()
frames = {}
i = 0

undistorted_depth = []
registered_color = []


def map_and_round_2d(arr):
    return [[round(value) for value in row] for row in arr]


def compress_data(data):
    # Convert data to JSON string
    json_str = json.dumps(data)

    # Convert the JSON string to bytes and compress
    compressed = zlib.compress(json_str.encode('utf-8'))

    return compressed


with device.running():
    for type_, frame in device:
        frames[type_] = frame
        if FrameType.Color in frames and FrameType.Depth in frames:
            break


rgb, depth = frames[FrameType.Color], frames[FrameType.Depth]
undistorted, registered = device.registration.apply(
    rgb, depth, with_big_depth=False)
undistorted_depth = map_and_round_2d(depth.to_array().tolist())
registered_color = registered.to_array().tolist()

# # Open the default device and capture a color and depth frame.


# async def capture_frames():
#     global undistorted_depth
#     global payload
#     with device.running():
#         for type_, frame in device:
#             frames[type_] = frame
#             # Capture undistorted_depth and registered_color frames
#             if FrameType.Depth in frames and FrameType.Color in frames:
#                 # Process and store the frames as needed
#                 undistorted_depth = frames[FrameType.Depth].to_array(
#                 ).tolist()
#                 payload = undistorted_depth[::2]
#                 # registered_color = frames[FrameType.Color].to_array().tolist()
#                 # rgb = frames[FrameType.Color]
#                 # registered_color = rgb.to_array().tolist()
#                 # logging.info(f"{rgb.to_array().shape}")


# def capture_frames_thread():
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(capture_frames())


# capture_thread = threading.Thread(target=capture_frames_thread)
# # Allow the thread to be terminated when the main program exits
# capture_thread.daemon = True
# capture_thread.start()

# time.sleep(20)
# for i in range(1, 100):
#     file.write(json.dumps(payload))

# file.close()


# # Use the factory calibration to undistort the depth frame and register the RGB
# # frame onto it.

# rgb, depth = frames[FrameType.Color], frames[FrameType.Depth]
# undistorted, registered = device.registration.apply(
#     rgb, depth, with_big_depth=False)

# cv2.imshow("image", rgb.to_array())
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# # print(registered.to_array().shape)
# # print(depth.to_array().shape)


# # # SAVES REGISTERED IMAGE AND DEPTH DATA
# with open('output/registered4.json', 'w') as outfile:
#     outfile.write(json.dumps(registered.to_array().tolist()))

# # with open('output/big_depth3.json', 'w') as outfile:
# #     outfile.write(json.dumps(big_depth.to_array().tolist()))

compressed = compress_data(undistorted_depth)
with open('output/depth_rounded.json', 'w') as outfile:
    outfile.write(json.dumps(undistorted_depth))


with open('output/depth_compressed.zlib', 'wb') as outfile:
    outfile.write(compressed)


# with open('output/registered.json', 'w') as outfile:
#     outfile.write(json.dumps(registered_color))


# def quantize(value):
#     # Subtract the minimum
#     value = value - 0.5  # Assuming values start from 0.5m
#     # Scale by the precision
#     value = value * 100  # Convert meters to centimeters
#     # Return the integer value
#     return int(value)
