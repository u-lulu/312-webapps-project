FROM python:3.9

ENV HOME /root
WORKDIR /root

COPY . .

# Download Dependencies
RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]