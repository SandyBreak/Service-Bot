# -*- coding: UTF-8 -*-
    
FROM python:3.10.12-alpine

WORKDIR /src/

COPY requirements.txt /tmp/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt

RUN mkdir /src/downloads
RUN mkdir /src/downloads/photos
RUN mkdir /src/downloads/video

COPY . .

CMD ["python", "/src/main.py"]
