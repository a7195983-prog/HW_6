FROM python:3.14.7-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app


COPY requirements.txt /app/


RUN pip install -r requirements.txt \
    && chmod +x start.sh

ENTRYPOINT [ "/bin/sh", "/app/start.sh" ]