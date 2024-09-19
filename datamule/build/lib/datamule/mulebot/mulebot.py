import openai
import json
from datamule.parsers import get_all_facts_for_company
from datamule.helper import identifier_to_cik
from .tools import tools

class MuleBot:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)
        self.messages = [
            {"role": "system", "content": "You are a helpful assistant to assist with questions related to the Securities and Exchanges Commission."}
        ]
        self.total_tokens = 0

    def process_message(self, user_input):
        self.messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-0613",
                messages=self.messages,
                tools=tools,
                tool_choice="auto"
            )

            self.total_tokens += response.usage.total_tokens
            assistant_message = response.choices[0].message

            if assistant_message.content is None:
                assistant_message.content = "I'm processing your request."

            self.messages.append({"role": "assistant", "content": assistant_message.content})

            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    if tool_call.function.name == "identifier_to_cik":
                        function_args = json.loads(tool_call.function.arguments)
                        result = identifier_to_cik(function_args["ticker"])
                        function_response = f"The CIK for {function_args['ticker']} is {result}"
                        self.messages.append({"role": "function", "name": "identifier_to_cik", "content": function_response})

                final_response = self.client.chat.completions.create(
                    model="gpt-4-0613",
                    messages=self.messages
                )
                self.total_tokens += final_response.usage.total_tokens
                assistant_message = final_response.choices[0].message
                self.messages.append({"role": "assistant", "content": assistant_message.content})

            return assistant_message.content

        except openai.BadRequestError as e:
            return f"An error occurred: {str(e)}"

    def get_total_tokens(self):
        return self.total_tokens