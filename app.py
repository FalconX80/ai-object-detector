import torch
import torchvision
from torchvision.transforms import functional as F
from torchvision.models.detection.faster_rcnn import FasterRCNN
from torch.serialization import add_safe_globals
from flask import Flask, render_template, request
import numpy as np
import cv2
from PIL import Image
import io

# VOC class names
VOC_CLASSES = [
    "__background__", "aeroplane", "bicycle", "bird", "boat",
    "bottle", "bus", "car", "cat", "chair", "cow",
    "diningtable", "dog", "horse", "motorbike", "person",
    "pottedplant", "sheep", "sofa", "train", "tvmonitor"
]

# Setup device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# ✅ Add model class to safe globals
add_safe_globals([FasterRCNN])

# ✅ Load model safely with full object
model = torch.load("trained_model.pth", map_location=device, weights_only=False)
model.to(device)
model.eval()

# Flask app
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            img_bytes = file.read()
            pil_image = Image.open(io.BytesIO(img_bytes)).convert("RGB")

            # Convert to numpy for OpenCV and display
            np_image = np.array(pil_image)
            image_tensor = F.to_tensor(np_image).to(device)

            with torch.no_grad():
                prediction = model([image_tensor])[0]

            # Draw boxes
            for box, label, score in zip(prediction['boxes'], prediction['labels'], prediction['scores']):
                if score > 0.5:
                    x1, y1, x2, y2 = map(int, box)
                    class_name = VOC_CLASSES[label]
                    cv2.rectangle(np_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    # Prepare label text
                    label_text = f"{class_name} {score:.2f}"

                    # Calculate text size to draw background
                    (text_width, text_height), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)

                    # Draw filled rectangle background for text
                    cv2.rectangle(np_image, (x1, y1), (x1 + text_width + 10, y1 + text_height + 10), (0, 255, 0), -1)

                    # Put the label text on top of that rectangle
                    cv2.putText(np_image, label_text, (x1 + 5, y1 + text_height + 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
            # Save and send output
            output_path = "static/output.jpg"
            cv2.imwrite(output_path, cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR))
            return render_template('index.html', output_image=output_path)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
