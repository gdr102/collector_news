import requests


async def translate_yandex(FOLDER_ID, KEY_SECRET, texts):
    body = {
        "targetLanguageCode": 'ru',
        "texts": texts,
        "folderId": FOLDER_ID,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f'Api-key {KEY_SECRET}'   
    }

    response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
        json = body,
        headers = headers
    )

    return response.text