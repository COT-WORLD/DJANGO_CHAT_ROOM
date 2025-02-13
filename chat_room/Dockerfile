FROM python:3.12
 
WORKDIR /chat_room
 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 
 
EXPOSE 8000 
 
COPY . /chat_room/

RUN pip install --no-cache-dir -r requirements.txt

RUN python manage.py collectstatic --noinput

CMD ["/bin/bash", "-c", "python manage.py migrate;python manage.py runserver 0.0.0.0:8000"]


