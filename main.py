import logging
import os

if os.getenv('API_ENV') != 'production':
    from dotenv import load_dotenv

    load_dotenv()

from fastapi import FastAPI, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
import openai
import uvicorn
import re

logging.basicConfig(level=os.getenv('LOG', 'WARNING'))
logger = logging.getLogger(__file__)

app = FastAPI()
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
openai.api_key = os.getenv('OPENAI_API_KEY')


def is_url_valid(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        # domain...
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None


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
    # Use OpenAI API to process the text
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"""
          Source 你會幫我把內容都轉換為 google calendar 的邀請網址。
          Message 我會給你任何格式的訊息，需要整理裡面的內容並對應上google calendar 的渲染方式。
          Channel 將內容整理成 google calendar 邀請網址，並且要能整理出對應標題、行事曆時間、地點，其餘內容整理完後放在描述裡面。
          Receiver 收到連結需要點選放進 google calendar 的民眾。
          Effect 最後不論怎麼樣，一定要回傳只能給我網址，其他內容都不要給我。
          請參考以上的格式，只需要將下列的文字轉換成 google calendar URL回傳給我即可，不要有其他的敘述以及空白鍵。
          
          {text}
          """}])
    print(response.choices[0].message)
    processed_text: str = response.choices[0].message.content
    if is_url_valid(processed_text):
        response: FlexSendMessage = FlexSendMessage(alt_text='行事曆網址', contents={
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
                            "uri": processed_text
                        }
                    }
                ],
                "flex": 0
            }
        })
    else:
        response: TextSendMessage = TextSendMessage(text=str(processed_text))
    # Send the processed text back to the user through LINE Bot
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text="請確認以下網址"),
            response
        ]
    )


if __name__ == "__main__":
    port = int(os.environ.get('PORT', default=8080))
    debug = True if os.environ.get(
        'API_ENV', default='develop') == 'develop' else False
    logging.info('Application will start...')
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=debug)