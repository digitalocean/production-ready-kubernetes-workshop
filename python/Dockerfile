FROM python

ENV DB_HOST="localhost"
ENV DB_PORT=6379
ENV DB_PASSWORD=None
ENV DB_SSL=True

RUN mkdir /app
WORKDIR /app
ADD . /app/
RUN pip install -r requirements.txt


EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]