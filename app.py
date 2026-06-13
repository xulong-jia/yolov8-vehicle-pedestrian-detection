"""Lightweight Streamlit demo for YOLOv8 single-image detection."""

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from ultralytics import YOLO


DEFAULT_MODEL_PATH = "local_weights/yolov8n_640_50epochs/best.pt"
MODEL_MISSING_MESSAGE = (
    "Model weight not found. Please place best.pt at "
    "local_weights/yolov8n_640_50epochs/best.pt"
)


@st.cache_resource(show_spinner=False)
def load_model(model_path: str) -> YOLO:
    return YOLO(model_path)


def build_detection_table(result) -> pd.DataFrame:
    names = result.names
    rows = []

    if result.boxes is None or len(result.boxes) == 0:
        return pd.DataFrame(
            columns=["class_name", "confidence", "xmin", "ymin", "xmax", "ymax"]
        )

    boxes = result.boxes.xyxy.cpu().numpy()
    confidences = result.boxes.conf.cpu().numpy()
    class_ids = result.boxes.cls.cpu().numpy().astype(int)

    for box, confidence, class_id in zip(boxes, confidences, class_ids):
        xmin, ymin, xmax, ymax = box.tolist()
        rows.append(
            {
                "class_name": names.get(class_id, str(class_id)),
                "confidence": round(float(confidence), 4),
                "xmin": round(float(xmin), 2),
                "ymin": round(float(ymin), 2),
                "xmax": round(float(xmax), 2),
                "ymax": round(float(ymax), 2),
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    st.set_page_config(page_title="YOLOv8 Image Detection Demo", layout="wide")
    st.title("YOLOv8 Vehicle and Pedestrian Detection")

    model_path = st.text_input("Model path", value=DEFAULT_MODEL_PATH)
    confidence = st.slider(
        "Confidence threshold",
        min_value=0.05,
        max_value=0.95,
        value=0.25,
        step=0.05,
    )

    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png", "bmp", "webp"],
    )

    if not Path(model_path).is_file():
        st.warning(MODEL_MISSING_MESSAGE)
        return

    if uploaded_file is None:
        st.info("Upload an image to run detection.")
        return

    try:
        image = Image.open(uploaded_file).convert("RGB")
    except Exception as exc:
        st.error(f"Could not read the uploaded image: {exc}")
        return

    image_array = np.array(image)

    try:
        with st.spinner("Loading model and running detection..."):
            model = load_model(model_path)
            results = model.predict(
                source=image_array,
                conf=confidence,
                save=False,
                verbose=False,
            )
    except Exception as exc:
        st.error(f"Detection failed: {exc}")
        return

    result = results[0]
    detection_table = build_detection_table(result)
    annotated_image = result.plot()

    col_original, col_result = st.columns(2)
    with col_original:
        st.subheader("Original Image")
        st.image(image, use_container_width=True)
    with col_result:
        st.subheader("Detection Result")
        st.image(annotated_image, channels="RGB", use_container_width=True)

    st.subheader("Detection Table")
    if detection_table.empty:
        st.info("No detections above the selected confidence threshold.")
    else:
        st.dataframe(detection_table, use_container_width=True)


if __name__ == "__main__":
    main()
