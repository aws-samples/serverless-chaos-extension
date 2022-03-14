#!/usr/bin/env python3

import json
import os
import time
import random
import requests
import threading
from flask import Flask, request

app = Flask('lambda-chaos-extension')
AWS_LAMBDA_RUNTIME_API = os.getenv('AWS_LAMBDA_RUNTIME_API')
EXTENSION_NEXT_URL = f"http://{AWS_LAMBDA_RUNTIME_API}/2020-01-01/extension/event/next"
EXTENSION_REGISTER_URL = f"http://{AWS_LAMBDA_RUNTIME_API}/2020-01-01/extension/register"


def register_extension():
    register_res = requests.post(EXTENSION_REGISTER_URL,
                                 headers={'Lambda-Extension-Name': 'lambda_chaos_extension'},
                                 json={'events': []})
    extension_id = register_res.headers['Lambda-Extension-Identifier']
    print(f"[extension] extension '{extension_id}' registered.")
    print(f"[extension] enter event loop for extension id: '{extension_id}'")
    requests.get(EXTENSION_NEXT_URL, headers={'Lambda-Extension-Identifier': extension_id})


@app.route("/2018-06-01/runtime/invocation/next", methods=['GET'])
def get_next_invocation():
    resp = requests.get(f"http://{AWS_LAMBDA_RUNTIME_API}{request.full_path}")
    # Chaos!!!
    if random.random() > 0.9:
        time.sleep(300) # sleep 5 minutes, causing the function to timeout.

    resp.headers['Transfer-Encoding'] = None
    return resp.json(), resp.status_code, resp.headers.items()


@app.route("/2018-06-01/runtime/invocation/<path:request_id>/response", methods=['post'])
def post_invoke_response(request_id):
    # Chaos!!!
    if random.random() > 0.5:
        data = request.get_json()
    else:
        # modify the response data
        data = {
            "statusCode": 500,
            "body": json.dumps({
                "message": "hello, Chaos!!!",
            }),
        }

    resp = requests.post(f"http://{AWS_LAMBDA_RUNTIME_API}{request.full_path}",
                         headers=request.headers,
                         json=data)

    return resp.json(), resp.status_code, resp.headers.items()


@app.route("/2018-06-01/runtime/init/error", methods=['post'])
def post_initialization_error():
    resp = requests.post(f"http://{AWS_LAMBDA_RUNTIME_API}{request.full_path}",
                         headers=request.headers,
                         json=request.get_json())
    return resp.json(), resp.status_code, resp.headers.items()


@app.route("/2018-06-01/runtime/invocation/<path:request_id>/error", methods=['post'])
def post_invoke_error(request_id):
    resp = requests.post(f"http://{AWS_LAMBDA_RUNTIME_API}{request.full_path}",
                         headers=request.headers,
                         json=request.get_json())
    return resp.json(), resp.status_code, resp.headers.items()


def main():
    # start rapid proxy
    threading.Thread(target=app.run, args=('127.0.0.1', 9100, False)).start()
    # start extension
    register_extension()


if __name__ == "__main__":
    main()
