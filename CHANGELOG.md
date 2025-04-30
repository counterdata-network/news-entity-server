Version History
===============

### v2.5.1

* Automated build tweaks for DockerHub release

### v2.5.0

* Add Swahili support
* Update dependencies

### v2.4.3

* Docker build tweaks to try to reduce image size so it builds and releases via GH Actions

### v2.4.2

* Update spacey models and other libraries to latest versions

### v2.4.1

* Update spacey models and other libraries to latest versions

### v2.4.0

* Added Korean language model support

### v2.3.6

* More CI work

### v2.3.5

* Continuous integration updates (built and pushed via GitHub Actions to DockerHub)

### v2.3.4

* Force python 3.10 to fix cchardet build error on deployment (was defaulting to 3.11)

### v2.3.3

* Update dependencies

### v2.3.2

* Add new `/entities/from-html` endpoint

### v2.3.1

* Update dependencies (including spacy models)

### v2.3.0

* Update dependencies (including spacy models)
* Catch and ignore more expected "webpage didn't respond" errors

### v2.2.1

* Remove language param from `entities/from-url`; we guess it from the text
* Tweaks for production server horizontal scaling

### v2.2.0

* Switch some underlying dependencies to centralize our news article metadata code

### v2.1.0

* Update underlying libraries to the latest versions

### v2.0.2

* Fix bugs in entity-from-content endpoint

### v2.0.1

* More consistent models (small vs. large)

### v2.0.0

* Refactored to include canonical_domain_name. If you are using entities endpoints, the entities themselves are 
  now under `results.entities`.
* Added official docker release docker 

### v1.6.0

Better guessing for publish_date via `htmldate` module.

### v1.5.3

Fix english large model mode box.

### v1.5.2

More work on large model bug fixes.

### v1.5.1

Add model mode to returned results.

### v1.5.0

Add new MODEL_MODE to pick between models for each language: "small" (default) or "large".

### v1.4.6

Update dependencies.

### v1.4.5

Protect against missing content-type in fetched response.

### v1.4.4

Ignore some more can't-fetch-webpage errors.

### v1.4.3

Ignore some more can't-fetch-webpage errors.

### v1.4.2

Add back in suppression of error messages we don't care about logging (ie. ones like timeouts that are expected errors).

### v1.4.1

Add custom PT date/age entity recognition code.

### v1.4.0

Switch from Flask/gunicorn to FastAPI/uvicorn for speed and documentation.

### v1.3.3

Tell Sentry to ignore some more low-level logging so it doesn't relay noisy erorrs to the server.

### v1.3.2

Reduce errors sent to central Sentry logging, because we don't care about ones we expect to happen.

### v1.3.1

Fetch HTML once *before* running extractors to save time.

### v1.3.0

Add support for Portuguese parsing. Standardize request headers and timeouts.

### v1.2.1

More check to make sure we don't parse non-html content. 

### v1.2.0

Switch default extraction to readability, with a more robust set of fallback libraries. Clean up test code too. 

### v1.1.2

Fixed spanish date regex

### v1.1.1

Fix bugs in integration of new date and age extraction code, add more test cases for those too

### v1.1.0

Added custom age and date extraction code to support story clustering experiments

### v1.0.0

First release, works for english and spanish
