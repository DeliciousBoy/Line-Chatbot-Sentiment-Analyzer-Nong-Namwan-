import sys
sys.path.append('C:\chatbot')
from flask import Flask,request,abort
import requests
from app.Config import *
import json
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer
import sklearn
import numpy as np
from pythainlp.tokenize import word_tokenize
import dill

Introduce = ['สวัสดี','หวัดดี','สวัสดีครับ','สวัสดีค่ะ']
app=Flask(__name__)
@app.route('/webhook',methods=['POST','GET'])
def webhook():
    if request.method=='POST':
        payload =request.json
        Reply_token=payload['events'][0]['replyToken']
        message=payload['events'][0]['message']['text'] #ข้อความที่เราพิมพ์ไป
        
        if message in Introduce:
            Reply_text = "สวัสดีค่ะ น้องน้ำหวานยินดีช่วยเหลือเต็มที่ค่ะ\nน้ำหวานสามารถวิเคราะห์ความรู้สึกผ่านข้อความได้นะ"
            # sticker_package_id = 1  
            # sticker_id = 1          
            # send_sticker(Reply_token, sticker_package_id, sticker_id)
        else:
            Reply_text = prediction(sentiment(message))
            
        print(Reply_text,flush=True)
        ReplyMessage(Reply_token,Reply_text,Channel_access_token)
        return request.json,200
    elif request.method=='GET':
        return "this is method GET!!!",200
    else:
        abort(400)
        
def sentiment(message):
    
    with open('Naivebay_Ads.hd5', 'rb') as model_file:
        nb = pickle.load(model_file)
            
    with open('vectorizer.pkl', 'rb') as model_file:
        vectorizer = dill.load(model_file)
            
    new_text_tokenized = word_tokenize(message, keep_whitespace=False)
    new_text_bow = vectorizer.transform([new_text_tokenized])
    y_pred = nb.predict(new_text_bow)
    return y_pred[0]

def prediction(y_pred):
    if y_pred == [0]:
        Reply_text  = 'ข้อความของคุณเป็นกลาง'
    elif y_pred == [1]:
        Reply_text  = 'ข้อความของคุณเป็นเชิงลบ'
    elif y_pred == [2]:
        Reply_text  = 'ข้อความของคุณป็นเชิงบวก'
    return Reply_text 

def ReplyMessage(Reply_token,TextMessage,Line_Acees_Token):
    LINE_API='https://api.line.me/v2/bot/message/reply/'
    
    Authorization='Bearer {}'.format(Line_Acees_Token)
    print(Authorization)
    headers={
        'Content-Type':'application/json; char=UTF-8',
        'Authorization':Authorization
    }

    data={
        "replyToken":Reply_token,
        "messages":[{
            "type":"text",
            "text":TextMessage
        }
        ]
    }
    data=json.dumps(data) # ทำเป็น json
    r=requests.post(LINE_API,headers=headers,data=data)
    return 200

def send_sticker(Reply_token, sticker_package_id, sticker_id):
    LINE_API = 'https://api.line.me/v2/bot/message/reply/'
    Authorization = 'Bearer {}'.format(Channel_access_token)
    headers = {
        'Content-Type': 'application/json; char=UTF-8',
        'Authorization': Authorization
    }
    data = {
        "replyToken": Reply_token,
        "messages": [
            {
                "type": "sticker",
                "packageId": sticker_package_id,
                "stickerId": sticker_id
            }
        ]
    }
    data = json.dumps(data)
    r = requests.post(LINE_API, headers=headers, data=data)
    return 200

