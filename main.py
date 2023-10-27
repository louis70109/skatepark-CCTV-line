import json
import logging
import os
import tempfile

if os.getenv('API_ENV') != 'production':
    from dotenv import load_dotenv

    load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))


def arrange_flex_message(gcal_url: str, action: dict) -> FlexSendMessage:
    return FlexSendMessage(alt_text='行事曆網址', contents={
        "type": "bubble",
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
                            "uri": gcal_url
                        }
                    },
                    action
                ],
            "flex": 0
        }
    })


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
        print(doc)
        return doc.__dict__['_data']
    return None


@app.post("/api/user", status_code=201)
async def add_user(request: Request):
    body = await request.body()
    body = body.decode()
    response = json.loads(body)
    doc = read_doc('user', response['userId'])
    data = doc.__dict__['_data']
    if data is not None and data['mobile'] is not None:
        update_doc('user', response['userId'], dict(response))
        print('updated')
    else:
        create_doc('user', response['userId'], dict(response))
    return True


@app.get("/api/liff")
async def add_user():
    return {'liffId': os.environ['LIFF_ID']}


@app.post("/webhooks/line")
async def callback(request: Request):
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = await request.body()
    body = body.decode('utf-8')

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        return 'Invalid signature. Please check your channel access token/channel secret.'

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text

    line_bot_api.reply_message(
        event.reply_token,
        [TextSendMessage(text=text)]
    )


if __name__ == "__main__":
    port = int(os.environ.get('PORT', default=8000))
    debug = True if os.environ.get(
        'API_ENV', default='develop') == 'develop' else False
    logging.info('Application will start...')
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=debug)
