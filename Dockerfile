FROM gcr.io/google_appengine/python

RUN virtualenv -p python3 /env
ENV PATH /env/bin:$PATH

COPY hiss /app/hiss

RUN /env/bin/pip install --upgrade pip && /env/bin/pip install -r /app/hiss/requirements.txt

CMD gunicorn -b :$PORT hiss.hiss.wsgi:application
