FROM python:3.12

WORKDIR /usr/src/app

COPY weather_requester.py mqtt_sender.py html_sender.py requirements.txt /usr/src/app/
COPY templates /usr/src/app/templates

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
EXPOSE 1883

VOLUME ["/data"]

CMD [ "python","weather_requester.py" ]
