import requests
import os


API_KEY = os.environ["API Translator"]
OED_APP_ID = os.environ["OED_APP_ID"]
OED_KEY = os.environ["OED_KEY"]


def translator(text, lang):
    accompanying_text = "Переведено сервисом «Яндекс.Переводчик» http://translate.yandex.ru/."
    translator_url = "https://translate.yandex.net/api/v1.5/tr.json/translate"
    response = requests.get(
        translator_url,
        params={
            "key": API_KEY,
            "lang": lang,
            "text": text
        })
    return "\n\n".join([response.json()["text"][0], accompanying_text])


def detect_lang(text):
    detector_url = "https://translate.yandex.net/api/v1.5/tr.json/detect"
    response = requests.get(
        detector_url,
        params={
            "key": API_KEY,
            "text": text,
            "hint": "ru,en"
        })
    result = response.json()["lang"]
    return result + "-ru" if result == "en" else result + "-en"


def get_definition(word, lang):
    try:
        oxford_template = 'https://od-api.oxforddictionaries.com/api/v2/entries/{}/{}'.format(lang, word)
        headers = {
            "Accept": "application/json",
            "app_id": OED_APP_ID,
            "app_key": OED_KEY
        }
        res = requests.get(oxford_template, headers=headers)
        res = res.json()
        return res['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['definitions'][0]
    except:
        return None
