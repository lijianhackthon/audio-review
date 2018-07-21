FROM python:3.5
LABEL maintainer="Binbin Zhang"

WORKDIR /app

ADD . /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 80

CMD ["python", "main.py", "config/config.json"]

