from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

client = MongoClient('mongodb://localhost:27017/')
db = client.chatbot_db

@app.route('/message', methods=['POST'])
def receive_message():
    data = request.json
    user_message = data['message']
    session_id = data.get('session_id')

    if not session_id:
        session_id = str(ObjectId())
        conversation = {
            'session_id': session_id,
            'exchanges': []
        }
        insert_result = db.conversations.insert_one(conversation)
        print(f"Inserted new conversation with ID: {insert_result.inserted_id}")

    print(f"Session ID: {session_id}")
    existing_convo = db.conversations.find_one({'session_id': session_id})
    print(f"Existing conversation: {existing_convo}")

    rasa_response = requests.post('http://localhost:5005/webhooks/rest/webhook', json={"sender": session_id, "message": user_message})
    bot_message = "I didn't understand that." if rasa_response.status_code != 200 else rasa_response.json()[0]['text']

    exchange = {'user': user_message, 'bot': bot_message}
    session_name = data.get('name', 'Default Chat')
    db.conversations.update_one(
        {'session_id': session_id},
        {'$set': {'name': session_name, 'date': datetime.now()}},
        upsert=True
    )

    return jsonify({'reply': bot_message, 'session_id': session_id})
    
@app.route('/chat-history', methods=['GET'])
def get_chat_history():
    chat_sessions = db.conversations.find().sort("date", -1)
    all_chats = []

    for session in chat_sessions:
        session_name = session.get('name', 'Default Chat')
        session_date = session.get('date', '')
        exchanges = session.get('exchanges', [])
        all_chats.append({
            'name': session_name,
            'date': session_date,
            'exchanges': exchanges
        })

    return jsonify(all_chats)

if __name__ == '__main__':
    app.run(debug=True)
