import cv2
from .filters import cartoon_filter, edge_paint_filter, oil_paint_filter, sepia_filter

def run_webcam(filter_name="cartoon"):
    filters = {
        "cartoon": cartoon_filter,
        "edge": edge_paint_filter,
        "oil": oil_paint_filter,
        "sepia": sepia_filter
    }

    if filter_name not in filters:
        raise ValueError(f"Unknown filter: {filter_name}")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open webcam")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        filtered = filters[filter_name](frame)
        cv2.imshow("Easy Filters", filtered)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
