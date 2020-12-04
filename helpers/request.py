import logging
import time
from functools import wraps
from flask import jsonify, request
from helpers import VERSION

logger = logging.getLogger(__name__)


def _error_results(message, start_time=None, status_code=400):
    response = jsonify({
        'status': 'error',
        'statusCode': status_code,
        'duration': int(round((time.time() - start_time) * 1000)) if start_time else 0,
        'message': message,
    })
    response.status_code = status_code
    return response


def validate_params_exist(form, params):
    for param in params:
        if param not in form:
            raise ValueError('Missing required value for '+param)


def arguments_required(*expected_args):
    """
    Handy decorator for ensuring that request params exist
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.debug(request.args)
                validate_params_exist(request.args, expected_args)
                return func(*args, **kwargs)
            except ValueError as e:
                logger.exception("Missing a required arg")
                return _error_results(e.args[0])
        return wrapper
    return decorator


def argument_is_valid(argument, valid_values):
    """
    Handy decorator for ensuring that the parameter is one of the valid values
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(request.args)
            is_valid = request.args[argument] in valid_values
            if not is_valid:
                return _error_results('"{}" is not in {}'.format(argument, valid_values))
            return func(*args, **kwargs)
        return wrapper
    return decorator


def form_fields_required(*expected_form_fields):
    """
    Handy decorator for ensuring that the form has the fields you need
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.debug(request.form)
                validate_params_exist(request.form, expected_form_fields)
                return func(*args, **kwargs)
            except ValueError as e:
                logger.exception("Missing a required form field")
                return _error_results(e.args[0])
        return wrapper
    return decorator


def _results_with_metadata(results, start_time):
    wrapped_results = {
        'version': VERSION,
        'status': 'ok',
        'duration': int(round((time.time()-start_time) * 1000)),
        'results': results
    }
    return wrapped_results


def api_method(func):
    """
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            results = func(*args, **kwargs)
            return _results_with_metadata(results, start)
        except Exception as e:
            logger.exception(e)
            return _error_results(str(e), start)
    return wrapper
