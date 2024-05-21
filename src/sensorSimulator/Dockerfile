FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 1883

ENV BROKER_ADDRESS=localhost
ENV BROKER_PORT=1883
ENV TOPIC=sensor_data

CMD ["python", "sensorSim.py"]
