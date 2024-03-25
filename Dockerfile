FROM python:3.9

ENV HOME /root
WORKDIR /root

COPY . .

# Download Dependencies
RUN pip3 install -r requirements.txt

EXPOSE 5000

ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /wait
RUN chmod +x /wait

# Command to run the Flask app
CMD ["sh", "-c", "/wait mongo:27017 -- python -m flask run --host=0.0.0.0"]
