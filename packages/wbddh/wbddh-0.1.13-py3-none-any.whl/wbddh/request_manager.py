import requests
import re
import time
from wbddh.ddh_exceptions import *

# default API host
API_host = "https://datacatalogapi.worldbank.org/ddhxext"

def get(endpoint, params=None, headers=None, session=None):
    '''Send a GET request

    Arguments:
        endpoint:		the endpoint (e.g., "datasets")
        params:			parameters
        headers:		additional headers

    Returns:
        a Response object (from the requests package)
    '''
    def has_special_character(input_string):
        special_char_pattern = re.compile(r'[^a-zA-Z0-9\s]')
        if special_char_pattern.search(input_string):
            return True
        else:
            return False
        
    special_query_string = ''
    regular_params = None
    if params is not None:
        special_params = {key: value for key, value in params.items() if has_special_character(key)}
        regular_params = {key: value for key, value in params.items() if not has_special_character(key)}
        if special_params:
            special_query_string = "?" + "&".join([f"{key}={value}" for key, value in special_params.items()])

    if session:
        session.check_tokens()
        print()
        return requests.get(get_request_url(endpoint) + special_query_string, params=regular_params, verify=session.verify, headers=session.get_headers(headers))
    else:
        return requests.get(get_request_url(endpoint) + special_query_string, params=regular_params)


def try_get(endpoint, params=None, headers=None, session=None, num_try=3, interval=10):
    '''Repeat sending a GET request until it succeeds or it tries {num_try} times

    Additional arguments:
        num_try:        number of tries
        interval:       interval between tries in seconds
    '''
    count = 0
    while True:
        try:
            count = count + 1
            if session:
                session.check_tokens()
                response = requests.get(get_request_url(endpoint), params=params, verify=session.verify, headers=session.get_headers(headers))
            else:
                response = requests.get(get_request_url(endpoint), params=params)
            if response.status_code in DDH_RUNTIME_ERRORS and count < num_try:
                time.sleep(interval)
                continue
            else:
                return response
        except requests.exceptions.RequestException as e:
            print (f"[{count} try] Error: ", e)
            if count > num_try:
                raise Exception(f"Request failed after {count} tries.")
            time.sleep(interval)
            continue


def get_all_in_generator(endpoint, params=None, top_key="top", skip_key="skip", headers=None, session=None):
    if params == None:
        params = {}
    if skip_key in params or top_key in params:
        raise Exception(f"get_all function cannot be used with '{skip_key}' or '{top_key}' parameter.")
    
    pageSize = 50
    def fetch(page):
        params[skip_key] = page * pageSize
        params[top_key] = pageSize
        response = get(endpoint, params=params, headers=headers, session=session)
        if response.status_code != 200:
            raise DDHRequestException(response)
        return response.json()
    
    count = None
    pageNum = 0
    while count is None or pageNum * pageSize <= count:
        batch = fetch(pageNum)
        # type 1
        if type(batch) == list:
            for row in batch:
                yield row
        elif type(batch) == dict:
            if set(batch.keys()).issuperset({'Response'}) or set(batch.keys()).issuperset({'response'}):
                batch = list(batch.values())[0]
            # type 2
            if set(batch.keys()).issuperset({'count', 'data'}):
                count = batch['count']
                for row in batch['data']:
                    yield row
            # type 3
            elif set(batch.keys()).issuperset({'@odata.count', 'value'}):
                count = batch['@odata.count']
                for row in batch['value']:
                    yield row       
            else: 
                raise Exception(f"This function does not support {set(batch.keys())} response.")
        else:
            raise Exception(f"This function does not support {type(batch)} type response.")
        pageNum += 1


def get_all_in_list(endpoint, params=None, top_key="top", skip_key="skip", headers=None, session=None):
    if params == None:
        params = {}
    if skip_key in params or top_key in params:
        raise Exception(f"get_all function cannot be used with '{skip_key}' or '{top_key}' parameter.")
    
    pageSize = 50
    def fetch(page):
        params[skip_key] = page * pageSize
        params[top_key] = pageSize
        response = get(endpoint, params=params, headers=headers, session=session)
        if response.status_code != 200:
            raise DDHRequestException(response)
        return response.json()
    
    return_list = []
    count = None
    pageNum = 0
    while count is None or pageNum * pageSize <= count:
        batch = fetch(pageNum)
        # type 1
        if type(batch) == list:
            for row in batch:
                return_list.append(row)
        elif type(batch) == dict:
            if set(batch.keys()).issuperset({'Response'}) or set(batch.keys()).issuperset({'response'}):
                batch = list(batch.values())[0]
            # type 2
            if set(batch.keys()).issuperset({'count', 'data'}):
                count = batch['count']
                for row in batch['data']:
                    return_list.append(row)
            # type 3
            elif set(batch.keys()).issuperset({'@odata.count', 'value'}):
                count = batch['@odata.count']
                for row in batch['value']:
                    return_list.append(row)        
            else: 
                raise Exception(f"This function does not support {set(batch.keys())} response.")
        else:
            raise Exception(f"This function does not support {type(batch)} type response.")
        pageNum += 1
    return return_list


    
def post(endpoint, params=None, json=None, headers=None, session=None):
    '''Send a POST request

    Arguments:
        endpoint:		the endpoint (e.g., "dataset/listpage")
        json:			data object
        params:			query parameters
        headers:		additional headers

    Returns:
        a Response object (from the requests package)
    '''
    if session:
        session.check_tokens()
        return requests.post(get_request_url(endpoint), params=params, json=json, verify=session.verify, headers=session.get_headers(headers))
    else:
        raise DDHSessionException("DDH POST request requires a session")

def try_post(endpoint, params=None, json=None, headers=None, session=None, num_try=3, interval=10):
    '''Repeat sending a POST request until it succeeds or it tries {num_try} times

    Additional arguments:
        num_try:        number of tries
        interval:       interval between tries in seconds
    '''
    if session:
        count = 0
        while True:
            try:
                count = count + 1
                session.check_tokens()
                response = requests.post(get_request_url(endpoint), params=params, json=json, verify=session.verify, headers=session.get_headers(headers))
                if response.status_code in DDH_RUNTIME_ERRORS and count < num_try:
                    time.sleep(interval)
                    continue
                else:
                    return response
            except requests.exceptions.RequestException as e:
                print (f"[{count} try] Error: ", e)
                if count >= num_try:
                    raise Exception(f"Request failed after {count} tries.")
                time.sleep(interval)
                continue
                        
    else:
        raise DDHSessionException("DDH POST request requires a session")


def post_file(endpoint, files=None, headers=None, session=None):
    '''Send a POST request with file

    Arguments:
        endpoint:		the endpoint (e.g., "dataset/listpage")
        files:			multi-part form object
        headers:		additional headers

    Returns:
        a Response object (from the requests package)
    '''
    if session:
        session.check_tokens()
        return requests.post(get_request_url(endpoint), files=files, verify=session.verify, headers=session.get_headers(headers))
    else:
        raise DDHSessionException("DDH POST request requires a session")


def put(endpoint, data=None, headers=None, session=None):
    '''Send a PUT request

    Arguments:
        endpoint:		the endpoint
        data:			file content
        headers:		additional headers

    Returns:
        a Response object (from the requests package)
    '''
    if session:
        session.check_tokens()
        return requests.put(get_request_url(endpoint), data=data, verify=session.verify, headers=session.get_headers(headers))
    else:
        raise DDHSessionException("DDH PUT request requires a session")


def patch(endpoint, data=None, json=None, headers=None, session=None):
    '''Send a PATCH request

    Arguments:
        endpoint:		the endpoint
        data:			Dictionary, list of tuples, bytes, or file-like object to send in the body of the Request
        json:           A JSON serializable Python object to send in the body of the Request
        headers:		additional headers

    Returns:
        a Response object (from the requests package)
    '''
    if session:
        session.check_tokens()
        return requests.patch(get_request_url(endpoint), data=data, json=json, verify=session.verify, headers=session.get_headers(headers))
    else:
        raise DDHSessionException("DDH PATCH request requires a session")
    

def delete(endpoint, headers=None, session=None):
    '''Send a DELETE request

    Arguments:
        endpoint:		the endpoint
        headers:		additional headers

    Returns:
        a Response object (from the requests package)
    '''
    if session:
        session.check_tokens()
        return requests.delete(get_request_url(endpoint), verify=session.verify, headers=session.get_headers(headers))
    else:
        raise DDHSessionException("DDH DELETE request requires a session")
    

def get_request_url(endpoint):
    return '/'.join([get_api_host(), endpoint.strip()])
    

def get_api_host():
    return API_host
    

def set_api_host(url):
    global API_host
    API_host = url
