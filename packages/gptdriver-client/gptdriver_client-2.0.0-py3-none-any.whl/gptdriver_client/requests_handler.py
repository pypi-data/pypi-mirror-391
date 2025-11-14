import requests


def check_request_wrapper(func):
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)

        try:
            response.raise_for_status()
            return response
        except Exception as e:
            raise Exception(f"Request failed: {e}.\n {response.content}")

    return wrapper


class MiddleLayerRequestsHandler:
    base_url = f"https://api.mobileboost.io/sessions"

    @check_request_wrapper
    def post(self, endpoint, json, headers=None):
        response = requests.post(f"{self.base_url}/{endpoint}", json=json, headers=headers)
        return response

    @check_request_wrapper
    def get(self, endpoint, headers=None):
        response = requests.get(f"{self.base_url}/{endpoint}", headers=headers)
        return response
