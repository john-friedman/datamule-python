# File: datamule/mulebot_server.py

from flask import Flask, request, jsonify, render_template
from datamule.mulebot import MuleBot

class MuleBotServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.mulebot = None  # We'll initialize this when we have the API key
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def home():
            return render_template('chat.html')

        @self.app.route('/chat', methods=['POST'])
        def chat():
            if not self.mulebot:
                return jsonify({'error': 'MuleBot not initialized. Please set API key.'}), 500

            user_input = request.json['message']
            
            # Process the message using MuleBot's process_message method
            response = self.mulebot.process_message(user_input)
            
            return jsonify({
                'response': response,
                'total_tokens': self.mulebot.get_total_tokens()
            })

    def set_api_key(self, api_key):
        self.mulebot = MuleBot(api_key)

    def run(self, debug=False, host='0.0.0.0', port=5000):
        if not self.mulebot:
            raise ValueError("API key not set. Please call set_api_key() before running the server.")
        self.app.run(debug=debug, host=host, port=port)

# Create a single instance of MuleBotServer
server = MuleBotServer()
