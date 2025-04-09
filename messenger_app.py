# sys.path.insert(0, os.path.dirname(__file__))
# App chatbot phản hồi với người dùng qua Facebook Messenger
# Sử dụng Flask để thực hiện xử lý webhook
# Sử dụng pymessenger để gửi tin nhắn đến người dùng
# Sử dụng LightRAG để tạo phản hồi từ mô hình Gemini 2.0

import os, sys
from flask import Flask, request
from pymessenger import Bot
from generate_response import generate_response

PAGE_ACCESS_TOKEN = "EsAATadLAyZAmekABO40cX6GKn6J0tPQEILZCjguk7eDZAacqDn6k4aekq5npqGbTXCUwfBoG4IlsZC4nS8o2cZCs57ZCziAgRlVl5KtK98t6o28UyhTFZAZA1gER2m1waLvEBxa8IyZCRYlve6HOD0vlZA3Lk1q9VC3HSwjdcMtwsDfX3gMI8AJVCxbawqacYFdqEaoFL3wZDZD"
bot = Bot(PAGE_ACCESS_TOKEN)

app = Flask(__name__)
@app.route('/', methods=['GET'])
def verify():
    #Webhook verification 
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "hello":
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200 
    return "Successfull webhook", 200

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    log(data)
    sender_id, messaging_text = get_senderid_message(data)
    
    if messaging_text == 0:
        messaging_text = "Bạn muốn hỏi gì?"
        response = messaging_text
    else:
        response = generate_response(messaging_text)
                        
    #Send message
    bot.send_text_message(sender_id, response)
    return "ok", 200

def get_senderid_message(data):
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                #id
                sender_id = messaging_event['sender']['id']
                recipient_id = messaging_event['recipient']['id']

                if messaging_event.get('message'):
                    if 'text' in messaging_event['message']:
                        messaging_text = messaging_event['message']['text']
                        return sender_id, messaging_text
    return 0,0

# def generate_response(input_text):
#     model = ChatOllama(model="llama3.2:1b", base_url="http://localhost:11434/")

#     response = model.invoke(input_text)

#     return response.content
                    
def log(message):
    print(message)
    sys.stdout.flush()
    

if __name__ == "__main__":
    # print(generate_response("Bạn là gì?"))
    app.run(debug = True, port = 80)