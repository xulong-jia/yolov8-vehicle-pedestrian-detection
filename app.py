"""Lightweight Streamlit demo for YOLOv8 single-image detection."""

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from ultralytics import YOLO


DEFAULT_MODEL_PATH = "local_weights/yolov8n_640_50epochs/best.pt"
SAMPLE_IMAGE_DIR = Path("docs/error_case_gallery/images")
MODEL_MISSING_MESSAGE = (
    "Model weight not found. Expected local path: "
    "local_weights/yolov8n_640_50epochs/best.pt. "
    "Keep model weights local and do not commit them to Git."
)
DETECTION_COLUMNS = [
    "class_id",
    "class_name",
    "confidence",
    "xmin",
    "ymin",
    "xmax",
    "ymax",
]


@st.cache_resource(show_spinner=False)
def load_model(model_path: str) -> YOLO:
    return YOLO(model_path)


def get_sample_images(sample_dir: Path = SAMPLE_IMAGE_DIR) -> list[Path]:
    if not sample_dir.is_dir():
        return []

    image_extensions = {".jpg", ".jpeg", ".png"}
    return sorted(
        path
        for path in sample_dir.iterdir()
        if path.is_file() and path.suffix.lower() in image_extensions
    )


def short_error(exc: Exception, max_length: int = 180) -> str:
    message = str(exc).strip() or exc.__class__.__name__
    return message if len(message) <= max_length else f"{message[:max_length]}..."


def build_detection_table(result) -> pd.DataFrame:
    names = result.names
    rows = []

    if result.boxes is None or len(result.boxes) == 0:
        return pd.DataFrame(columns=DETECTION_COLUMNS)

    boxes = result.boxes.xyxy.cpu().numpy()
    confidences = result.boxes.conf.cpu().numpy()
    class_ids = result.boxes.cls.cpu().numpy().astype(int)

    for box, confidence, class_id in zip(boxes, confidences, class_ids):
        xmin, ymin, xmax, ymax = box.tolist()
        rows.append(
            {
                "class_id": class_id,
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

    with st.sidebar:
        model_path = st.text_input("Model path", value=DEFAULT_MODEL_PATH)
        confidence = st.slider(
            "Confidence threshold",
            min_value=0.05,
            max_value=0.95,
            value=0.25,
            step=0.05,
        )
        input_mode = st.radio(
            "Input mode",
            options=["Upload image", "Use sample image"],
        )

    image_source = None
    image_name = None

    if input_mode == "Upload image":
        uploaded_file = st.file_uploader(
            "Upload an image",
            type=["jpg", "jpeg", "png", "bmp", "webp"],
        )
        if uploaded_file is not None:
            image_source = uploaded_file
            image_name = uploaded_file.name
    else:
        sample_images = get_sample_images()
        if sample_images:
            selected_sample = st.selectbox(
                "Select a sample image",
                options=sample_images,
                format_func=lambda path: path.name,
            )
            image_source = selected_sample
            image_name = selected_sample.name
        else:
            st.info("No sample images found. Please use image upload instead.")

    st.caption(
        "Sample images are loaded from docs/error_case_gallery/images/ when available."
    )

    if not Path(model_path).is_file():
        st.warning(MODEL_MISSING_MESSAGE)
        return

    if image_source is None:
        st.info("Choose or upload an image to run detection.")
        return

    try:
        image = Image.open(image_source).convert("RGB")
    except Exception as exc:
        st.error(f"Could not read image: unsupported or corrupted image. {short_error(exc)}")
        return

    image_array = np.array(image)

    try:
        with st.spinner("Loading model..."):
            model = load_model(model_path)
    except Exception as exc:
        st.error(f"Model loading failed: {short_error(exc)}")
        return

    try:
        with st.spinner("Running detection..."):
            results = model.predict(
                source=image_array,
                conf=confidence,
                save=False,
                verbose=False,
            )
    except Exception as exc:
        st.error(f"Inference failed: {short_error(exc)}")
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
        st.info("No detections available for CSV download.")
    else:
        st.dataframe(detection_table, use_container_width=True)
        image_stem = Path(image_name or "image").stem
        csv_data = detection_table.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download detection CSV",
            data=csv_data,
            file_name=f"detections_{image_stem}.csv",
            mime="text/csv",
        )

    st.caption("Prediction images are rendered in memory and are not saved to disk.")


if __name__ == "__main__":
    main()
