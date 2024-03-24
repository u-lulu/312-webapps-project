FROM python:3.9

ENV HOME /root
WORKDIR /root

COPY . .

# Download Dependencies
RUN pip3 install -r requirements.txt

EXPOSE 8000
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait 
CMD /wait && python app.py