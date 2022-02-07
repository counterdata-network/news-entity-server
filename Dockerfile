FROM python:3

WORKDIR /news-entity-server
EXPOSE 8000

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY install.sh /
RUN chmod +x /install.sh && /install.sh

COPY . ./

CMD ["./run.sh"]
