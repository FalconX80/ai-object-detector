FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 && \
    pip install torch torchvision flask numpy opencv-python pillow

COPY . /app
WORKDIR /app

EXPOSE 5000
CMD ["python", "app.py"]
