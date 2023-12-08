FROM python:3.10-alpine

ENV PYTHONBUFFERED 1

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r ./requirements.txt

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN adduser -D user
USER user

CMD ["/entrypoint.sh"]
