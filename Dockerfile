FROM python:slim
WORKDIR /usr/src/app
COPY . .
RUN pip install -r requirements.txt --disable-pip-version-check --no-cache-dir

ENTRYPOINT ["python", "py/correlation.py"]
