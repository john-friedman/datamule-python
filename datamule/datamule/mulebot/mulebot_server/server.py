# File: datamule/mulebot_server.py

from flask import Flask, request, jsonify, render_template
from datamule.mulebot import MuleBot

class MuleBotServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.mulebot = MuleBot()
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def home():
            return render_template('chat.html')

        @self.app.route('/chat', methods=['POST'])
        def chat():
            user_input = request.json['message']
            
            # Add user message to MuleBot's messages
            self.mulebot.messages.append({"role": "user", "content": user_input})
            
            # Process the message using MuleBot's chat method
            self.mulebot.chat()
            
            # Get the latest assistant message
            assistant_message = next(msg for msg in reversed(self.mulebot.messages) if msg['role'] == 'assistant')
            
            return jsonify({'response': assistant_message['content']})

    def set_api_key(self, api_key):
        self.mulebot.set_api_key(api_key)

    def run(self, debug=False, host='0.0.0.0', port=5000):
        self.app.run(debug=debug, host=host, port=port)

# Create a single instance of MuleBotServer
server = MuleBotServer()

if __name__ == '__main__':
    # This allows running the server directly if needed
    with open("apikey.txt", "r") as f:
        api_key = f.read().strip()
    server.set_api_key(api_key)
    server.run(debug=True)