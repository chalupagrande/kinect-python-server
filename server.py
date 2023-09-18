import json
import asyncio
import threading  # Import the threading module
import logging  # Import the logging module

import zlib
import base64
import pickle
import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from freenect2 import Device, FrameType

frames = {}
undistorted_depth = []
registered_color = []
payload = []

logging.basicConfig(filename="server.log", level=logging.INFO)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

device = Device()


async def capture_frames():
    global registered_color
    global undistorted_depth
    global payload
    with device.running():
        for type_, frame in device:

            frames[type_] = frame
            # Capture undistorted_depth and registered_color frames
            if FrameType.Depth in frames and FrameType.Color in frames:
                # Process and store the frames as needed
                undistorted_depth = frames[FrameType.Depth].to_array(
                ).tolist()
                payload = undistorted_depth[::2]
                # registered_color = frames[FrameType.Color].to_array().tolist()
                # rgb = frames[FrameType.Color]
                # registered_color = rgb.to_array().tolist()
                # logging.info(f"{rgb.to_array().shape}")


def capture_frames_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(capture_frames())


# Start the frame capture loop in a separate thread
capture_thread = threading.Thread(target=capture_frames_thread)
# Allow the thread to be terminated when the main program exits
capture_thread.daemon = True
capture_thread.start()


@app.get("/")
async def read_root():
    # Return the HTML file
    return FileResponse("static/index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:

            # serialized_object = pickle.dumps(
            #     [1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 2, 4, 123])
            json_string = json.dumps(payload)

            # Encode the compressed object as a Base64 string
            # base64_encoded_object = base64.b64encode(
            #     serialized_object).decode('utf-8')
            base64_encoded_object = base64.b64encode(
                json_string).decode('utf-8')
            await websocket.send_json(base64_encoded_object)
            # await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    print("starting server")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
