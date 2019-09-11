from __future__ import unicode_literals

import logging
from alice_sdk import AliceRequest, AliceResponse

from english_bot import handle_dialog
from memory_cache import mc

from flask import Flask, request
app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
mc.set("session_storage", {})  # кэшируем данные о сессиях


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
