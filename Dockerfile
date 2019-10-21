FROM gcr.io/google_appengine/python

RUN virtualenv -p python3 /env
ENV PATH /env/bin:$PATH

COPY hiss /app

RUN /env/bin/pip install --upgrade pip && /env/bin/pip install -r /app/requirements.txt

CMD gunicorn -b :$PORT hiss.wsgi:application --capture-output
