# syntax=docker/dockerfile:1
# slim and alpine can't install sklearn because of wheel problems
FROM python
WORKDIR /usr/src/app
COPY . .
RUN pip install -r requirements.txt --disable-pip-version-check --no-cache-dir

ENTRYPOINT ["python", "py/correlation.py"]
