import cv2
from ultralytics import YOLO

# Load the YOLOv8 model trained on Open Images V7
model = YOLO('yolov8n-oiv7.pt')

# Open webcam (0 is usually the default system camera)
cap = cv2.VideoCapture(0)

# Expanded list with various cheating-aid objects and variations.
# Make sure these strings match exactly with the class names from model.names.
TARGET_CLASSES = [
    'Sunglasses',
    'Headphones',
    'Cell phone',
    'Mobile phone',
    'Book',  # Book detection (singular)
    'Books',  # Book detection (plural, if applicable)
    'Laptop',
    'Tablet',
    'iPad',
    'Paper'  # For cheat sheets, printed paper, etc.
]

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO prediction on the current frame
    results = model.predict(source=frame, conf=0.4, verbose=False)

    # Create a copy of the frame for annotations
    annotated_frame = frame.copy()
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id]

            # Check if the detected object's class is in our target list.
            if cls_name in TARGET_CLASSES:
                # Extract coordinates and confidence score
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                label = f"{cls_name} ({conf:.2f})"

                # Draw a rectangle around the object and label it
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(annotated_frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Display the annotated frame
    cv2.imshow('YOLOv8 Live Detection', annotated_frame)

    # Exit on ESC key press
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()