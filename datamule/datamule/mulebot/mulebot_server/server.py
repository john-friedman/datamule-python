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
            user_input = request.json['message']
            
            # Process the message using MuleBot's process_message method
            response = self.mulebot.process_message(user_input)
            response_type = response['key']

            # Prepare the response based on the type
            if response_type == 'text':
                # If response type is text, add it to the chat
                chat_response = {
                    'type': 'text',
                    'content': response['value']
                }
            elif response_type == 'table':
                # If response type is table, prepare it for the artifact window
                chat_response = {
                    'type': 'artifact',
                    'content': response['value'],
                    'artifact_type': 'artifact-table'
                }
            elif response_type == 'list':
                chat_response = {
                    'type': 'artifact',
                    'content': response['value'],
                    'artifact_type': 'artifact-list'
                }

            else:
                # Handle other types of responses if needed
                chat_response = {
                    'type': 'unknown',
                    'content': 'Unsupported response type'
                }
            
            return jsonify({
                'response': chat_response,
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
