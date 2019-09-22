FROM python:3.7.4-buster

WORKDIR /opt
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY ./reporter.py ./

CMD ["python", "reporter.py"]