FROM python:3

COPY . /corkboardit
WORKDIR /corkboardit
RUN pip install -r requirements.txt

ENV FLASK_APP corkboardit.py

CMD flask run --host=0.0.0.0
