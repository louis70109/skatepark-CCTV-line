import logging
import os
import sys

import requests
from utils.flex import entrance
from utils.github import Github

from utils.image import SkateParkImage

if os.getenv('API_ENV') != 'production':
    from dotenv import load_dotenv

    load_dotenv()


from fastapi import FastAPI, HTTPException, Request

from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    TextMessage,
    ImageMessage
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
)

import uvicorn

logging.basicConfig(level=os.getenv('LOG', 'WARNING'))
logger = logging.getLogger(__file__)

app = FastAPI()

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

configuration = Configuration(
    access_token=channel_access_token
)

async_api_client = AsyncApiClient(configuration)
line_bot_api = AsyncMessagingApi(async_api_client)
parser = WebhookParser(channel_secret)


@app.get("/health")
async def health():
    return 'ok'


@app.post("/webhooks/line")
async def handle_callback(request: Request):
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = await request.body()
    body = body.decode()

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        logging.info(event)
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessageContent):
            continue
        text = event.message.text
        SkatePark = SkateParkImage()
        park_list = SkatePark.get_name_list()
        print(text in park_list)
        if text == "入口":
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[entrance(park_list)]
                )
            )
        elif text in park_list:
            b64_file = SkatePark.get_image(event.message.text)
            try:
                github = Github()
                res = requests.put(
                    headers={
                        "Accept": "application/vnd.github+json",
                        "Authorization": f"Bearer {os.getenv('GITHUB')}"
                    },
                    json={
                        "message": f"✨ Commit",
                        "committer": {"name": "NiJia Lin", "email": "louis70109@gmail.com"},
                        "content": b64_file,
                        "branch": "master"},
                    url=f"https://api.github.com/repos/{github.repo_name}/contents/images/{event.message.id}.png"
                )
                # response_msg = res.json()
                url = f"https://raw.githubusercontent.com/{github.repo_name}/master/images/{event.message.id}.png"
            except Exception as e:
                logging.warning(f'Image upload to GitHub error, Error is: {e}')

            logger.info('Ready to push data...')
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(
                            text=f'「{text}」...圖片如下'),
                        ImageMessage(
                            originalContentUrl=url,
                            previewImageUrl=url)
                    ]
                )
            )
        else:
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=text)]
                )
            )
    return 'OK'


if __name__ == "__main__":
    port = int(os.environ.get('PORT', default=8000))
    debug = True if os.environ.get(
        'API_ENV', default='develop') == 'develop' else False
    logging.info('Application will start...')
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=debug)
