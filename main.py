# backend/main.py

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN
import io
import torch

# Setup
device = 'cuda' if torch.cuda.is_available() else 'cpu'
mtcnn = MTCNN(keep_all=True, device=device)

app = FastAPI()

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def blur_faces_opencv(image_np):
    img_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)

    boxes, _ = mtcnn.detect(pil_img)

    if boxes is not None:
        for box in boxes:
            x1, y1, x2, y2 = [int(b) for b in box]
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(image_np.shape[1], x2)
            y2 = min(image_np.shape[0], y2)

            face = image_np[y1:y2, x1:x2]
            blurred_face = cv2.GaussianBlur(face, (99, 99), 30)
            image_np[y1:y2, x1:x2] = blurred_face

    return image_np

@app.post("/blur/")
async def blur_image(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    result_img = blur_faces_opencv(image_np)

    # Encode image back to jpg
    _, img_encoded = cv2.imencode('.jpg', result_img)
    return StreamingResponse(io.BytesIO(img_encoded.tobytes()), media_type="image/jpeg")
