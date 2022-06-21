FROM python:3.7

WORKDIR /app

COPY . /app

# COPY requirements.txt .
# RUN cat requirements.txt | xargs -n1 pip install

RUN pip install -r requirements.txt --no-cache-dir
# RUN pip install flask moviepy passlib pydub requests moviepy PyMySQL Flask-MySQL SpeechRecognition 

ENV PYTHONUNBUFFERED 1
ENV FLASK_APP app.py
ENV FLASK_ENV development
ENV FLASK_DEBUG 1

EXPOSE 5000
EXPOSE 5001

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]


