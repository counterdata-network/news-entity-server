# using alpine as base for smaller image size
FROM python:3.10

# move options to try and reduce image size
ENV \
    # Allow statements and log messages to immediately appear
    PYTHONUNBUFFERED=1 \
    # disable a pip version check to reduce run-time & log-spam
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # cache is useless in docker image, so disable to reduce image size
    PIP_NO_CACHE_DIR=1


WORKDIR /news-entity-server

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY install.sh /
RUN chmod +x /install.sh && /install.sh

COPY . ./

EXPOSE 8000

CMD ["./run.sh"]
