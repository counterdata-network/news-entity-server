Version History
===============

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
