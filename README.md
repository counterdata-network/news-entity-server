News Entity Server
==================

A small API server to return entities and other metadata for online news articles. Originally built to support the 
[Data Against Feminicide](https://datoscontrafeminicidio.net/) project. Technically, this exposes
API endpoints that accepts URLs and returns entities in JSON. Uses spaCy under the hood for entity extraction.


**Install from Docker**: The easiest approach to just start using this is to install the pre-built image from 
DockerHub. Set a `WEB_CONCURRENCY` env var if you want more than one worker.

```
docker pull rahulbot/news-entity-server:latest
docker run -p 8000:8000 -e MODEL_MODE=small -m 8G news-entity-server:latest
```

Developing
----------

### Installation

```
pip install -r requirements.txt
./install.sh
```

### Running Locally

Run locally with Gunicorn: `./run.sh`

Or via docker:
```
docker image build -t news-entity-server .
docker container run --rm -it -p 8000:8000 -e MODEL_MODE=small news-entity-server
```


### Testing

Just run *pytest* to run a small set of test on the API endpoints.


Usage
-----

API documentation is available at http://localhost:5000/redoc. See the code in `test/test_server.py` for examples.

### API Endpoints

Every endpoint returns a dict like this:

```json
{
  "duration": 123,
  "status": "ok",
  "version": "0.0.1", 
  "results": { ... }  
}
```

 * **duration**: the number of milliseconds the request too to complete on the server
 * **status**: "ok" if it worked, "error" if it did not work
 * **version**: a semantically versioned number indicating the server version
 * **results**: a dict of the results you requested (potentially different for different endpoints)


#### /entities/from-url

POST a `url` and `language` to this endpoint and it returns JSON with all the entities it finds. 
Add a `title` argument, set to 1 or 0, to optionally include the article title in the entity extraction.  

#### /entities/from-content

POST `text` and `language` content to this endpoint and it returns JSON with all the entities it finds.

#### /content/from-url

POST a `url` to this endpoint and it returns just the extracted content from the HTML.


Releasing to DockerHub
----------------------

I build and release this to DockerHub for easier deployment on your server. To release the latest code:

```
docker build -t rahulbot/news-entity-server .
docker push rahulbot/news-entity-server
```

To release a tagged version:

```
docker build -t rahulbot/news-entity-server:2.0.0 .
docker push rahulbot/news-entity-server:2.0.0
```
