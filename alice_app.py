from __future__ import unicode_literals

import logging
from alice_sdk import AliceRequest, AliceResponse

from english_bot import handle_dialog

from flask import Flask, request
app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

import pylibmc
import os

servers = os.environ.get('MEMCACHIER_SERVERS', '').split(',')
user = os.environ.get('MEMCACHIER_USERNAME', '')
passw = os.environ.get('MEMCACHIER_PASSWORD', '')

mc = pylibmc.Client(servers, binary=True,
                    username=user, password=passw,
                    behaviors={
                      # Faster IO
                      'tcp_nodelay': True,

                      # Keep connection alive
                      'tcp_keepalive': True,

                      # Timeout for set/get requests
                      'connect_timeout': 2000, # ms
                      'send_timeout': 750 * 1000, # us
                      'receive_timeout': 750 * 1000, # us
                      '_poll_timeout': 2000, # ms

                      # Better failover
                      'ketama': True,
                      'remove_failed': 1,
                      'retry_timeout': 2,
                      'dead_timeout': 30,
                    })


mc.set("session_storage", {})


@app.route("/", methods=['POST'])
def main():
    alice_request = AliceRequest(request.json)
    logging.info('Request: {}'.format(alice_request))

    alice_response = AliceResponse(alice_request)

    user_id = alice_request.user_id

    alice_response, storage = handle_dialog(
        alice_request, alice_response, mc.get("session_storage").get(user_id)
    )

    sessions = mc.get("session_storage")
    sessions[user_id] = storage
    mc.set("session_storage", sessions)

    logging.info('Response: {}'.format(alice_response))

    return alice_response.dumps()


if __name__ == '__main__':
    app.run()
