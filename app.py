"""Lightweight Streamlit demo for YOLOv8 single-image detection."""

from html import escape
import os
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from ultralytics import YOLO


DEFAULT_MODEL_PATH = os.environ.get("MODEL_PATH", "local_weights/yolov8n_640_50epochs/best.pt")
SAMPLE_IMAGE_DIR = Path("docs/error_case_gallery/images")
MODEL_MISSING_MESSAGE = (
    "未找到模型权重。请检查侧边栏中的模型路径。"
    "模型权重应保存在本地，不要提交到 Git。"
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


def apply_page_style() -> None:
    st.markdown(
        """
        <style>
        :root {
          --yolo-blue: #2563eb;
          --yolo-cyan: #06b6d4;
          --yolo-border: #d7e7f4;
          --yolo-muted: #667085;
          --yolo-text: #172033;
          --yolo-surface: rgba(255, 255, 255, 0.92);
          --yolo-shadow: 0 10px 24px rgba(59, 130, 246, 0.1);
        }
        .stApp {
          background:
            radial-gradient(circle at top left, rgba(14, 165, 233, 0.16), transparent 34rem),
            linear-gradient(135deg, #eef8ff 0%, #f5fbff 45%, #f8fdff 100%);
          color: var(--yolo-text);
        }
        header[data-testid="stHeader"] {
          background: transparent;
        }
        section[data-testid="stSidebar"] {
          background: linear-gradient(180deg, rgba(255,255,255,0.97), rgba(238,248,255,0.94));
          border-right: 1px solid var(--yolo-border);
        }
        section[data-testid="stSidebar"] > div {
          padding: 1.2rem 1.15rem 1.6rem;
        }
        @media (min-width: 901px) {
          section[data-testid="stSidebar"] {
            width: 300px !important;
            min-width: 300px !important;
          }
          section[data-testid="stSidebar"] > div {
            width: 300px !important;
          }
        }
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
          gap: 0.9rem;
        }
        section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
          color: #334155;
          font-weight: 750;
        }
        section[data-testid="stSidebar"] input {
          border: 1px solid var(--yolo-border);
          border-radius: 14px;
          background: rgba(248, 253, 255, 0.95);
          color: var(--yolo-text);
          font-size: 0.94rem;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] {
          display: grid;
          gap: 0.45rem;
        }
        section[data-testid="stSidebar"] label[data-baseweb="radio"] {
          border: 1px solid rgba(215, 231, 244, 0.72);
          border-radius: 14px;
          background: rgba(255, 255, 255, 0.66);
          padding: 0.28rem 0.55rem;
        }
        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
          color: var(--yolo-muted);
          font-size: 0.82rem;
        }
        .yolo-sidebar-brand {
          border: 1px solid var(--yolo-border);
          border-radius: 16px;
          background: rgba(255, 255, 255, 0.72);
          box-shadow: 0 8px 18px rgba(59, 130, 246, 0.08);
          margin-bottom: 0.2rem;
          padding: 0.95rem 1rem;
        }
        .yolo-sidebar-brand strong {
          display: block;
          color: var(--yolo-text);
          font-size: 1.18rem;
          line-height: 1.2;
        }
        .yolo-sidebar-brand span {
          display: block;
          color: var(--yolo-muted);
          font-size: 0.84rem;
          margin-top: 0.25rem;
        }
        .block-container {
          max-width: 1200px;
          padding-top: 2.1rem;
          padding-left: 2.4rem;
          padding-right: 2.4rem;
          padding-bottom: 2.5rem;
        }
        .yolo-hero,
        .yolo-capability,
        .yolo-summary {
          background: var(--yolo-surface);
          border: 1px solid var(--yolo-border);
          border-radius: 16px;
          box-shadow: var(--yolo-shadow);
        }
        .yolo-hero {
          background: linear-gradient(135deg, rgba(255,255,255,0.97), rgba(231,251,255,0.92));
          margin-bottom: 1.3rem;
          padding: 2rem 2.25rem;
        }
        .yolo-hero h1 {
          margin: 0 0 0.55rem;
          font-size: 2.28rem;
          line-height: 1.2;
        }
        .yolo-hero p,
        .yolo-capability p,
        .yolo-summary p {
          color: var(--yolo-muted);
          margin: 0;
          font-size: 1.03rem;
        }
        .yolo-capabilities {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 1rem;
          margin: 0 0 1.45rem;
        }
        .yolo-capability {
          min-height: 116px;
          padding: 1.15rem 1.25rem;
        }
        .yolo-capability strong {
          display: block;
          margin-bottom: 0.35rem;
          font-size: 1.08rem;
        }
        .yolo-section-title {
          margin: 0 0 0.8rem;
          font-size: 1.38rem;
          font-weight: 800;
        }
        .yolo-summary {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 0.8rem;
          margin: 0.5rem 0 1.2rem;
          padding: 1rem;
        }
        .yolo-summary div {
          border-radius: 16px;
          background: #f8fdff;
          padding: 0.85rem;
        }
        .yolo-summary strong {
          display: block;
          color: var(--yolo-text);
          font-size: 1.35rem;
          line-height: 1.2;
        }
        .yolo-summary span {
          color: var(--yolo-muted);
          font-size: 0.84rem;
          font-weight: 700;
        }
        .yolo-result-title {
          margin: 1.45rem 0 0.6rem;
          font-size: 1.4rem;
          font-weight: 850;
        }
        .yolo-prompt {
          border: 1px solid #cfeeff;
          border-radius: 16px;
          background: rgba(228, 251, 255, 0.78);
          color: #36556a;
          font-weight: 700;
          margin-top: 1.25rem;
          padding: 1rem 1.15rem;
        }
        .block-container [data-testid="stVerticalBlockBorderWrapper"] {
          background: var(--yolo-surface);
          border: 1px solid var(--yolo-border);
          border-radius: 16px;
          box-shadow: var(--yolo-shadow);
          padding: 1.35rem 1.45rem;
        }
        .yolo-note {
          border: 1px solid #cfeeff;
          border-radius: 16px;
          background: rgba(228, 251, 255, 0.58);
          color: var(--yolo-muted);
          min-height: 128px;
          padding: 1.1rem 1.15rem;
          font-size: 0.98rem;
          line-height: 1.65;
        }
        .yolo-note strong {
          display: block;
          color: var(--yolo-text);
          margin-bottom: 0.35rem;
        }
        div[data-testid="stFileUploader"] {
          border: 1px dashed #9bdcf0;
          border-radius: 16px;
          background: rgba(248, 253, 255, 0.82);
          padding: 1rem;
        }
        div[data-testid="stHorizontalBlock"] {
          gap: 2rem;
        }
        div.stButton > button,
        div.stDownloadButton > button {
          border: 0;
          border-radius: 16px;
          background: linear-gradient(135deg, var(--yolo-blue), var(--yolo-cyan));
          color: white;
          font-weight: 700;
        }
        div[data-testid="stDataFrame"] {
          border: 1px solid var(--yolo-border);
          border-radius: 16px;
          overflow: hidden;
        }
        div[data-testid="stMetric"] {
          background: rgba(255, 255, 255, 0.88);
          border: 1px solid var(--yolo-border);
          border-radius: 14px;
          padding: 0.8rem 0.9rem;
        }
        div[data-testid="stImage"] {
          background: rgba(255, 255, 255, 0.86);
          border: 1px solid var(--yolo-border);
          border-radius: 16px;
          box-shadow: var(--yolo-shadow);
          overflow: hidden;
          padding: 0.75rem;
        }
        .stAlert {
          border-radius: 14px;
        }
        .element-container {
          margin-bottom: 0.35rem;
        }
        @page {
          size: 1440px 900px;
          margin: 0;
        }
        @media print {
          * {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
          }
          html,
          body,
          .stApp,
          [data-testid="stAppViewContainer"],
          [data-testid="stMain"],
          .main,
          .block-container {
            width: auto !important;
            height: 900px !important;
            min-height: 900px !important;
            overflow: hidden !important;
          }
          html,
          body,
          .stApp,
          [data-testid="stAppViewContainer"] {
            width: 1440px !important;
          }
          body,
          .stApp,
          [data-testid="stAppViewContainer"] {
            background:
              radial-gradient(circle at top left, rgba(14, 165, 233, 0.16), transparent 34rem),
              linear-gradient(135deg, #eef8ff 0%, #f5fbff 45%, #f8fdff 100%) !important;
          }
          body {
            margin: 0 !important;
          }
          header[data-testid="stHeader"],
          [data-testid="stToolbar"],
          [data-testid="stDecoration"],
          [style*="cursor: col-resize"][style*="right: -6px"],
          #MainMenu,
          footer {
            display: none !important;
          }
          section[data-testid="stSidebar"] {
            position: static !important;
            width: 300px !important;
            min-width: 300px !important;
            height: 900px !important;
            min-height: 900px !important;
            overflow: hidden !important;
            background: linear-gradient(180deg, rgba(255,255,255,0.97), rgba(238,248,255,0.94)) !important;
            border-right: 1px solid var(--yolo-border) !important;
          }
          section[data-testid="stSidebar"] > div {
            width: 300px !important;
            padding: 1.2rem 1.15rem 1.6rem !important;
          }
          .block-container {
            max-width: 1200px !important;
            padding: 2.1rem 2.4rem 2.5rem !important;
          }
          .yolo-hero,
          .yolo-capability,
          .yolo-summary,
          .yolo-note,
          .yolo-prompt,
          .block-container [data-testid="stVerticalBlockBorderWrapper"],
          div[data-testid="stDataFrame"],
          div[data-testid="stImage"],
          div[data-testid="stFileUploader"] {
            break-inside: avoid !important;
            page-break-inside: avoid !important;
          }
          .yolo-hero {
            margin-bottom: 1.3rem !important;
            padding: 2rem 2.25rem !important;
            box-shadow: var(--yolo-shadow) !important;
          }
          .yolo-hero h1 {
            font-size: 2.28rem !important;
          }
          .yolo-hero p {
            font-size: 1.03rem !important;
          }
          .yolo-capabilities {
            grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
            gap: 1rem !important;
            margin-bottom: 1.45rem !important;
          }
          .yolo-capability {
            min-height: 116px !important;
            padding: 1.15rem 1.25rem !important;
            box-shadow: var(--yolo-shadow) !important;
          }
          .block-container [data-testid="stVerticalBlockBorderWrapper"] {
            padding: 1.35rem 1.45rem !important;
            box-shadow: var(--yolo-shadow) !important;
          }
          .yolo-note {
            min-height: 128px !important;
            padding: 1.1rem 1.15rem !important;
          }
          .yolo-prompt {
            margin-top: 1.25rem !important;
            padding: 1rem 1.15rem !important;
          }
          div[data-testid="stHorizontalBlock"] {
            gap: 2rem !important;
            overflow: visible !important;
          }
          div[data-testid="column"] {
            min-width: 0 !important;
          }
          div.stButton > button,
          div.stDownloadButton > button {
            display: none !important;
          }
          div[data-testid="stFileUploader"] {
            padding: 0.75rem !important;
            overflow: visible !important;
          }
          div[data-testid="stDataFrame"],
          div[data-testid="stDataFrame"] * {
            overflow: visible !important;
          }
        }
        @media (max-width: 900px) {
          .block-container {
            max-width: 100% !important;
            padding-top: 1.1rem;
            padding-left: 1rem;
            padding-right: 1rem;
            padding-bottom: 2rem;
          }
          section[data-testid="stSidebar"] {
            width: auto !important;
            min-width: 0 !important;
          }
          section[data-testid="stSidebar"] > div {
            width: auto !important;
            padding: 1rem;
          }
          .yolo-capabilities,
          .yolo-summary { grid-template-columns: 1fr; }
          .yolo-hero { padding: 1.4rem; }
          .yolo-hero h1 { font-size: 1.75rem; }
          .yolo-note { min-height: auto; }
          div[data-testid="stHorizontalBlock"] { gap: 1rem; }
          div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
          }
          div[data-testid="stFileUploader"] {
            padding: 0.85rem;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <div class="yolo-hero">
          <h1>YOLOv8 车辆与行人检测系统</h1>
          <p>上传本地图片或选择样例图片，运行 YOLOv8 单图检测，并查看可检查的检测结果。</p>
        </div>
        <div class="yolo-capabilities">
          <div class="yolo-capability"><strong>图片检测</strong><p>单张图片推理</p></div>
          <div class="yolo-capability"><strong>检测结果</strong><p>类别、置信度、bbox 表格</p></div>
          <div class="yolo-capability"><strong>本地输出</strong><p>CSV 下载，不写入仓库</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_project_note() -> None:
    st.markdown(
        """
        <div class="yolo-note">
          <strong>项目边界</strong>
          <span>本页面用于课程演示与本机功能验证，不作为生产级安全系统或公共安全决策依据。</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_detection_summary(detection_table: pd.DataFrame) -> None:
    if detection_table.empty:
        target_count = 0
        primary_class = "无"
        average_confidence = "—"
    else:
        target_count = len(detection_table)
        primary_class = str(detection_table["class_name"].mode().iloc[0])
        average_confidence = f"{float(detection_table['confidence'].mean()):.3f}"

    st.markdown(
        f"""
        <div class="yolo-summary">
          <div><span>检测目标数</span><strong>{target_count}</strong></div>
          <div><span>主要类别</span><strong>{escape(primary_class)}</strong></div>
          <div><span>平均置信度</span><strong>{average_confidence}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="YOLOv8 车辆与行人检测系统", layout="wide")
    apply_page_style()
    render_hero()

    with st.sidebar:
        st.markdown(
            """
            <div class="yolo-sidebar-brand">
              <strong>YOLOV8</strong>
              <span>车辆与行人检测系统</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        model_path = st.text_input("模型路径", value=DEFAULT_MODEL_PATH)
        confidence = st.slider(
            "置信度阈值",
            min_value=0.05,
            max_value=0.95,
            value=0.25,
            step=0.05,
        )
        input_mode = st.radio(
            "输入方式",
            options=["上传图片", "使用样例图片"],
        )
        st.caption("FastAPI: 8010 · React: 5178 · Streamlit: 8511")

    image_source = None
    image_name = None

    with st.container(border=True):
        st.markdown('<div class="yolo-section-title">图片输入</div>', unsafe_allow_html=True)
        input_col, note_col = st.columns([1.45, 0.95], gap="large")
        with input_col:
            if input_mode == "上传图片":
                uploaded_file = st.file_uploader(
                    "上传一张图片",
                    type=["jpg", "jpeg", "png", "bmp", "webp"],
                )
                if uploaded_file is not None:
                    image_source = uploaded_file
                    image_name = uploaded_file.name
            else:
                sample_images = get_sample_images()
                if sample_images:
                    selected_sample = st.selectbox(
                        "选择样例图片",
                        options=sample_images,
                        format_func=lambda path: path.name,
                    )
                    image_source = selected_sample
                    image_name = selected_sample.name
                else:
                    st.info("没有找到样例图片，请改用上传图片。")

            st.caption("样例图片来自 docs/error_case_gallery/images/。")

        with note_col:
            render_project_note()

    if not Path(model_path).is_file():
        st.warning(MODEL_MISSING_MESSAGE)
        return

    if image_source is None:
        st.markdown(
            '<div class="yolo-prompt">请上传图片或选择样例图片后开始检测。</div>',
            unsafe_allow_html=True,
        )
        return

    try:
        image = Image.open(image_source).convert("RGB")
    except Exception as exc:
        st.error(f"无法读取图片：格式不支持或文件损坏。{short_error(exc)}")
        return

    image_array = np.array(image)

    try:
        with st.spinner("正在加载模型..."):
            model = load_model(model_path)
    except Exception as exc:
        st.error(f"模型加载失败：{short_error(exc)}")
        return

    try:
        with st.spinner("正在运行检测..."):
            results = model.predict(
                source=image_array,
                conf=confidence,
                save=False,
                verbose=False,
            )
    except Exception as exc:
        st.error(f"检测失败：{short_error(exc)}")
        return

    result = results[0]
    detection_table = build_detection_table(result)
    annotated_image = result.plot()

    st.markdown('<div class="yolo-result-title">检测结果</div>', unsafe_allow_html=True)
    render_detection_summary(detection_table)

    col_original, col_result = st.columns(2, gap="large")
    with col_original:
        st.markdown("##### 原始图片")
        st.image(image, use_container_width=True)
    with col_result:
        st.markdown("##### 检测预览")
        st.image(annotated_image, channels="RGB", use_container_width=True)

    st.markdown('<div class="yolo-result-title">结果表格</div>', unsafe_allow_html=True)
    if detection_table.empty:
        st.info("当前置信度阈值下没有检测框。")
        st.info("暂无可下载的检测 CSV。")
    else:
        st.dataframe(detection_table, use_container_width=True)
        image_stem = Path(image_name or "image").stem
        csv_data = detection_table.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="下载检测 CSV",
            data=csv_data,
            file_name=f"detections_{image_stem}.csv",
            mime="text/csv",
        )

    st.caption("预测图片仅在页面中渲染，检测 CSV 由用户手动下载。")


if __name__ == "__main__":
    main()
