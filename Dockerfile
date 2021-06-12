FROM ubuntu:latest
MAINTAINER Daniil Dyryaev <toliman.st4r@gmail.com>


WORKDIR /Projects/Age-of-python

RUN apt update
RUN apt upgrade -y
RUN apt install git -y
RUN apt install python3 -y
RUN apt install python3-pip -y

COPY . .
RUN pip3 install -r requirements.txt

RUN pip3 install Pillow
RUN pip3 install django_hashedfilenamestorage
RUN pip3 install psycopg2-binary

EXPOSE 8000

CMD ["bash"]
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
