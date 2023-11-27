import json
import logging
import os
import sys
import tempfile

import requests
from utils.github import Github

from utils.image import SkateParkImage

if os.getenv('API_ENV') != 'production':
    from dotenv import load_dotenv

    load_dotenv()


from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    PushMessageRequest,
    TextMessage,
    ImageMessage
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent
)

import uvicorn
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


# Read Firebase cert from env variable JSON string
firebase_cred = tempfile.NamedTemporaryFile(suffix='.json')
try:
    GOOGLE_KEY = os.environ.get('FIREBASE_CRED', '{}')
    firebase_cred.write(GOOGLE_KEY.encode())
    firebase_cred.seek(0)
    os.environ['FIREBASE_CREDENTIALS'] = firebase_cred.name
except Exception as e:
    firebase_cred.close()

if not firebase_admin._apps:
    cred = credentials.Certificate(os.environ['FIREBASE_CREDENTIALS'])
    firebase_admin.initialize_app(cred)

db = firestore.client()


def create_doc(collection_name, doc_name, data):
    doc_ref = db.collection(collection_name).document(doc_name)
    doc_ref.set(data)
    logger.debug(f"{data} created successfully")


def read_doc(collection_name, doc_name):
    doc_ref = db.collection(collection_name).document(doc_name)
    doc = doc_ref.get()
    if doc.exists:
        logger.debug(f"Document data: {doc.to_dict()}")
        return doc
    else:
        logger.info("No such document!")
        return None


def update_doc(collection_name, doc_name, data):
    doc_ref = db.collection(collection_name).document(doc_name)
    doc_ref.update(data)
    logger.debug(f"{collection_name}'s {doc_name} deleted successfully")


logging.basicConfig(level=os.getenv('LOG', 'WARNING'))
logger = logging.getLogger(__file__)

app = FastAPI()

# TODO: check CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


def order_flex(
    title,
    place,
    time,
    website,
    image_url="https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png",
):
    return {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": image_url,
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover",
            "action": {
                "type": "uri",
                "uri": "http://linecorp.com/"
            }
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": title,
                    "weight": "bold",
                    "size": "xl"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "Place",
                                    "color": "#aaaaaa",
                                    "size": "sm",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": place,
                                    "wrap": True,
                                    "color": "#666666",
                                    "size": "sm",
                                    "flex": 5
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "Time",
                                    "color": "#aaaaaa",
                                    "size": "sm",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": time,
                                    "wrap": True,
                                    "color": "#666666",
                                    "size": "sm",
                                    "flex": 5
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": "WEBSITE",
                        "uri": website
                    }
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [],
                    "margin": "sm"
                }
            ],
            "flex": 0
        }
    }


@app.post("/order/consume")
async def order(request: Request):
    order_json = order_flex(
        title="Brown Coffee",
        place="JCConf",
        time="10:00~11:00",
        website="https://jcconf.tw/2023/"
    )
    line_bot_api.push_message(
        'LINE User ID',
        FlexSendMessage(alt_text="訂餐資訊", contents=order_json)
    )


@app.get("/api/user")
async def get_user(q: str = ''):
    if q != '':
        doc = read_doc('user', q)
        logging.info(f'Firebase data is: {doc}')
        return doc.__dict__['_data']
    return None


@app.post("/api/user")
async def add_user(request: Request):
    body = await request.body()
    body = body.decode()
    response = json.loads(body)
    doc = read_doc('user', response['userId'])
    data = doc.__dict__['_data']
    try:
        if data is not None and data.get('mobile') is not None:
            update_doc('user', response['userId'], dict(response))
        else:
            create_doc('user', response['userId'], dict(response))
        logging.info(f'Create success, data is: {data}')
        return ''
    except Exception as e:
        logging.info(f'Create error, error is: e')
        return {'status': 'Post got some error'}


@app.get("/api/liff")
async def add_user():
    return {'liffId': os.environ['LIFF_ID']}


@app.get("/capture")
async def capture():
    pass
    image_b64 = get_neihu_meiti_image()
    return {'image': image_b64}


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

        if text == "入口":
            await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=SkatePark.get_name(),)]
            )
        )
        else:    
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text=f'請稍候...查詢「{text}」中',
                        quoteToken=event.message.quote_token)]
                )
            )
            
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
            await line_bot_api.push_message(push_message_request=PushMessageRequest(
                to=event.source.user_id,
                messages=[
                    ImageMessage(
                        originalContentUrl=url,
                        previewImageUrl=url)],
            ))
    return 'OK'


if __name__ == "__main__":
    port = int(os.getenv"PORT") or 8080
    debug = True if os.environ.get(
        'API_ENV', default='develop') == 'develop' else False
    logging.info('Application will start...')
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=debug)
