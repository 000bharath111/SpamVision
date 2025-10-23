# services/worker/Dockerfile
# CPU-first worker image. If you need GPU support, use a CUDA base image and install the appropriate torch wheel.
FROM python:3.10-slim

WORKDIR /worker

# install system deps for sentence-transformers (and optional mkdocs etc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl libsndfile1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# copy requirements
COPY requirements.txt /worker/requirements.txt
RUN pip install --no-cache-dir -r /worker/requirements.txt

# copy worker code (this file) and set PYTHONPATH so it can import app package from host
COPY . /worker

# default workdir: the container will still need access to the app package; mount it or set PYTHONPATH at runtime.
ENV PYTHONPATH=/app:.

CMD ["bash", "-lc", "echo 'Start RQ worker: rq worker --with-scheduler spampipeline'; rq worker --with-scheduler spampipeline"]
