FROM python:3.6.8-alpine
WORKDIR repos/fast-api-test
RUN pip install --upgrade pip setuptools wheel pipenv
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN apk add --no-cache --virtual .build-deps \
    build-base \
    ca-certificates
RUN pipenv install --system
COPY main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
