FROM python:3.11-alpine

WORKDIR /Download/

VOLUME [ "/app/data" ]

COPY . /app/

COPY "database.db" /app/data/

RUN pip install -r requirements.txt

EXPOSE 5000

CMD [ "python", "app_fast.py" ]
