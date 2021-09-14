FROM python:3.7

ADD . /app
COPY . ./app

WORKDIR /app
RUN pip3 install -r ./requirements.txt

CMD ["python3", "./server.py"]
