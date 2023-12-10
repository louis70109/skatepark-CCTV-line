# SkatePark 滑板場地查詢機器人

這個專案是一個使用 FastAPI 建立的 LINE Bot，提供使用者查詢滑板場地資訊，並且將資訊以圖片的方式儲存至 Github，提供給 LINE Bot 所需輸出的網址，詳細流程請參考下圖

![](https://raw.githubusercontent.com/louis70109/skatepark-CCTV-line/main/user-flow.png)

## 功能

- 使用者可以透過 LINE Bot 查詢滑板場地資訊
- 機器人會將查詢結果以圖片的方式儲存至 Github
- 使用者可以透過 API 拿取 CCTV 的截圖

## 開發

這個專案使用了以下的主要技術：

FastAPI：建立 API
LINE Messaging API：與使用者進行互動
Github API：將查詢結果儲存至 Github

## 安裝需求

你需要 Python 3.7 或以上版本的環境來運行此應用程式，並確保安裝以下的 Python 套件：

Clone 這個專案到你的本地環境：

```
git clone https://github.com/louis70109/skatepark-CCTV-line.git
cd notifier-line/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

```
export LINE_CHANNEL_SECRET=your_line_channel_secret
export LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
export GITHUB=your_github_token
```

透過 ngrok 建立暫時含有 https 的網址，並設定在 [LINE Developer Console](https://developers.line.biz/console) Webhook 欄位當中

```
ngrok http 8080
```

將 Domain 設定於 [LINE Developer Console](https://developers.line.biz/console)

1. 前往 LINE Developer Console 網站：https://developers.line.biz/console/
2. 點選右上角的「Log in」按鈕，登入您的 LINE 帳號。如果您還沒有 LINE 帳號，您需要先建立一個。
3. 在網頁上方的選單中，選擇「Provider」，然後選擇「Create」。
4. 在彈出的視窗中，輸入一個 Provider 名稱，然後點擊「Create」。
5. 建立之後，您將被導向該 Provider 的頁面。在這裡，選擇「Create Channel」。
6. 您需要選擇您要創建的 Channel 類型，對於 bot，請選擇「Messaging API」。
7. 填寫 Channel 的資訊，包括 Channel 名稱、Channel 說明、區域、大頭貼等等，然後點選「Create」。
8. Channel 建立後，您將被導向 Channel 的設定頁面。在這裡，您可以看到您的 Channel ID、Channel Secret、以及 Channel Access Token，這些資訊將被用於設定 bot。
9. 還有一個重要的設定是「Use webhooks」。如果您希望您的 bot 可以接收來自 LINE 的訊息，您需要打開這個設定，並輸入您的 webhook URL。您的 webhook URL 是一個可以接收 POST 請求的伺服器網址。
10. 之後，您可以在 LINE app 中加入您剛剛建立的 bot 為好友，並開始測試。

## Google Cloud Platform 部署

[![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run)

Clone 此專案

```
git clone git@github.com:gcp-serverless-workshop/notifier-line.git
cd notifier-line/
```

### gcloud 基礎設定

- `gcloud init`：初始化 gcloud CLI，該指令會提示登錄 Google 帳戶，並選擇您要使用的 GCP 項目。
- `gcloud config set project PROJECT_ID`：設定 GCP Project ID，以便 gcloud CLI 與該項目交互使用。
- `gcloud auth login`：登錄 Google 帳戶。

透過 [gcloud](https://cloud.google.com/sdk/docs/install?hl=zh-cn) 指令佈署

```
gcloud run deploy notifier-line-1 --source .
```

> 佈署參考: [【GCP】將 FastAPI 佈署上 Cloud Run](https://nijialin.com/2023/03/19/gcp-why-need-cloudrun-as-serverless/#5-%E4%BD%88%E7%BD%B2%E5%88%B0-Google-Cloud-Run)

## 參與貢獻

如果你有任何問題或建議，歡迎開 issue 或 pull request。

## LICENSE

請見 LICENSE 文件
