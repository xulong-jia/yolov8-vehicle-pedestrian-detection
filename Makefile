.PHONY: check api-check test streamlit status danger-check list-large-docs

check:
	python3 -m py_compile app.py src/train.py src/evaluate.py src/predict_image.py src/predict_video.py src/visualize_dataset.py src/analyze_dataset.py

api-check:
	python3 -m py_compile src/api.py

test:
	python3 -m pytest tests

streamlit:
	streamlit run app.py

status:
	git status --short

danger-check:
	git diff --cached --name-only | grep -E '\.pt$$|\.pth$$|\.onnx$$|\.mp4$$|\.avi$$|\.mov$$|\.mkv$$|^local_weights/|^local_videos/source/|^dataset/train/|^dataset/valid/|^dataset/test/|^runs/|^\.venv/' || true

list-large-docs:
	find docs -type f -size +5M
