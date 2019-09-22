FROM python:3.7.4-buster

WORKDIR /opt
COPY ./requirements.txt ./
RUN pip3 install --upgrade git+https://github.com/arthaud/python3-pwntools.git && pip install -r requirements.txt && rm requirements.txt

COPY ./solve.py ./runner.py ./

CMD ["python", "runner.py"]