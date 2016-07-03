"""Generic RESTful API interface class."""


import requests
from urlparse import urlparse, urljoin


# Helper functions
def merge_args(args1, args2):
    assert isinstance(args1, dict) and isinstance(args2, dict)
    result = args1.copy()
    for arg, value2 in args2.items():
        value1 = result.get(arg, None)
        if isinstance(value1, dict):
            assert isinstance(value2, dict)
            result[arg] = value1.update(value2)
        result[arg] = value2
    return result


class RESTfulAPI(object):
    def __init__(self, api_url, **request_args):
        self.api_url = api_url
        self.request_args = request_args

    def absolute_url(self, url):
        parsed_url = urlparse(url)
        if parsed_url.scheme and parsed_url.netloc:
            return url
        else:
            base_path = urlparse(self.api_url).path
            return urljoin(self.api_url, base_path + url)

    def get(self, url, **request_args):
        url = self.absolute_url(url)
        request_args = merge_args(self.request_args, request_args)
        response = requests.get(url, **request_args)
        return response

    def get_iter(self, url, **request_args):
        url = self.absolute_url(url)
        request_args = merge_args(self.request_args, request_args)
        response = requests.get(url, **request_args)
        while True:
            # Yield response content
            yield response
            # Get next page
            if response.links.get('next'):
                next_url = response.links.get('next').get('url')
                # Remove args that mutate next_url
                if request_args.get('params'):
                    request_args.pop('params')
                response = requests.get(next_url, **request_args)
            else:
                raise StopIteration

    def post(self, url, **request_args):
        url = self.absolute_url(url)
        request_args = merge_args(self.request_args, request_args)
        response = requests.post(url, **request_args)
        return response

    def put(self, url, **request_args):
        url = self.absolute_url(url)
        request_args = merge_args(self.request_args, request_args)
        response = requests.put(url, **request_args)
        return response

    def delete(self, url, **request_args):
        url = self.absolute_url(url)
        request_args = merge_args(self.request_args, request_args)
        response = requests.delete(url, **request_args)
        return response
