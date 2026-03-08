import os
from ultralytics import YOLO

DEBRIS_LABEL_MAP = {
    "bus": "rocket_body",
    "truck": "rocket_body",
    "airplane": "rocket_body",
    "boat": "defunct_satellite",
    "person": "fragment",
    "car": "defunct_satellite",
}

# load model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
model = YOLO(os.path.join(BASE_DIR, "models", "yolov8n.pt"))

def detect_debris(image_path: str) -> dict:
    results = model(image_path)
    boxes = results[0].boxes

    if len(boxes) == 0:
        return {"label": "unknown", "debris_category": "unknown", "confidence": 0.0}
    
    top_class_id = int(boxes.cls[0].item())
    top_label = model.names[top_class_id]
    top_confidence = float(boxes.conf[0].item())
    debris_category = DEBRIS_LABEL_MAP.get(top_label, "unknown")
    return {"label": top_label, "debris_category": debris_category, "confidence": round(top_confidence, 4)}

if __name__ == "__main__":
    result = detect_debris("https://ultralytics.com/images/bus.jpg")
    print(result)