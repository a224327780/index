FROM python:3.7

COPY ./run.sh /run.sh
COPY . /data/python

WORKDIR /data/python

RUN chmod +x /run.sh && pip install --no-cache-dir gunicorn && pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["/run.sh"]