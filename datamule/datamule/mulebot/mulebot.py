import openai
import json

from datamule.parsers import get_all_facts_for_company
from datamule.helper import identifier_to_cik
from .tools import tools

class MuleBot:
    def __init__(self):
        self.client = None
        self.messages = [
            {"role": "system", "content": "You are a helpful assistant to assist with questions related to the Securities and Exchanges Commission."}
        ]
        self.total_tokens = 0
        self.client = openai.OpenAI()

    def set_api_key(self, api_key):
        openai.api_key = api_key

    def chat(self):
        if not self.client:
            print("Error: API key not set. Please call set_api_key() first.")
            return

        print('------------------------------------\n\n')
        print("Chatbot: Hello! What would you like to know?\n")

        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Chatbot: Goodbye!")
                break

            print("Processing user input...\n")
            self.messages.append({"role": "user", "content": user_input})

            try:
                print("Sending request to OpenAI API...")
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=self.messages,
                    tools=tools,
                    tool_choice="auto"
                )

                self.total_tokens += response.usage.total_tokens
                print(f"Response received. Total tokens used: {self.total_tokens}\n")

                assistant_message = response.choices[0].message

                if assistant_message.content is None:
                    assistant_message.content = "I'm processing your request."

                self.messages.append({"role": "assistant", "content": assistant_message.content})

                if assistant_message.tool_calls:
                    print("Function call detected. Processing...\n")
                    for tool_call in assistant_message.tool_calls:
                        if tool_call.function.name == "identifier_to_cik":
                            function_args = json.loads(tool_call.function.arguments)

                            print(f"Calling identifier_to_cik({function_args['ticker']})\n")
                            result = identifier_to_cik(function_args["ticker"])
                            function_response = f"The CIK for {function_args['ticker']} is {result}"
                            self.messages.append({"role": "function", "name": "identifier_to_cik", "content": function_response})

                    print("Getting final response from assistant...\n")
                    final_response = self.client.chat.completions.create(
                        model="gpt-4",
                        messages=self.messages
                    )
                    self.total_tokens += final_response.usage.total_tokens
                    print(f"Final response received. Total tokens used: {self.total_tokens}")

                    assistant_message = final_response.choices[0].message
                    self.messages.append({"role": "assistant", "content": assistant_message.content})

                print("Chatbot:", assistant_message.content, "\n")

            except openai.BadRequestError as e:
                print(f"An error occurred: {e}")
                print("Chatbot: I'm sorry, I encountered an error. Could you please rephrase your question?")
