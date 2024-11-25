import cv2
import time
from ultralytics import YOLO
import logging

# Suppress logging below WARNING level
logging.getLogger("ultralytics").setLevel(logging.WARNING)

def detect_objects_yolov8():
    # Load the YOLOv8 model (default is the pretrained COCO model)
    model = YOLO('yolov8n.pt')  # You can use 'yolov8s.pt', 'yolov8m.pt', etc., for larger models
    
    # Open the webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Webcam not found!")
        return

    print("Starting webcam detection. Reading frames every 1 second. Press Ctrl+C to stop.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to capture frame.")
            break

        # Perform detection
        results = model(frame)
        
        # Extract and display detected objects
        detected_objects = []
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls)  # Class ID of the object
                confidence = box.conf  # Confidence score
                class_name = model.names[class_id]  # Class name (e.g., 'person', 'car')
                detected_objects.append(class_name)

        print(f"Detected objects: {', '.join(detected_objects) if detected_objects else 'None'}")
        
        # Annotate frame with detection results (optional, not displayed here)
        annotated_frame = results[0].plot()
        
        # Wait for 1 second
        time.sleep(1)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_objects_yolov8()
