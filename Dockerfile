FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV MODEL_PATH=/models/best.pt

WORKDIR /app

COPY requirements.txt requirements-api.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-api.txt

COPY app.py ./app.py
COPY src ./src
COPY configs ./configs
COPY docs/error_case_gallery ./docs/error_case_gallery
COPY docs/streamlit_demo.md ./docs/streamlit_demo.md
COPY docs/model_loading_strategy.md ./docs/model_loading_strategy.md
COPY docs/deployment_guide.md ./docs/deployment_guide.md

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
