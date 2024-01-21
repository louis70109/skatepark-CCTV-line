from linebot.v3.messaging import (
    FlexMessage,
    FlexContainer
)

def flex_container(flex_dict: dict):
  # bubble_string = """{ type:"bubble", ... }"""
  return FlexMessage(alt_text="滑板場入口", contents=FlexContainer.from_dict(flex_dict))

def entrance(locations: list):
  contents = []
  for idx in range(len(locations)):
    contents.append({
        "type": "button",
        "style": "primary",
        "height": "md",
        "action": {
          "type": "message",
          "label": locations[idx],
          "text": locations[idx]
        },
        "margin": "5px"
      })
  flex_dict = {
    "type": "bubble",
    "footer": {
      "type": "box",
      "layout": "vertical",
      "spacing": "sm",
      "contents": contents,
      "flex": 0
    }
  }
  return flex_container(flex_dict=flex_dict)
  


