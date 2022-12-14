FROM python:latest

RUN apt-get update
RUN python3 -m pip install --upgrade pip
RUN pip install ecdsa requests click

ADD . .
RUN python3 -m pip install --editable .

CMD python