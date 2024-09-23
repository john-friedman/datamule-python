import openai
import json

from datamule.helper import identifier_to_cik
from .tools import tools, select_table_tool
from .helper import get_company_concept, select_table
from .search import fuzzy_search


class MuleBot:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)
        self.messages = [
            {"role": "system", "content": "You are a helpful, but concise, assistant to assist with questions related to the Securities and Exchanges Commission. You are allowed to guess tickers."}
        ]
        self.total_tokens = 0

    def process_message(self, user_input):
        self.messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.messages,
                tools=tools,
                tool_choice="auto"
            )

            #print(f"Response: {response}\n")

            self.total_tokens += response.usage.total_tokens
            assistant_message = response.choices[0].message

            if assistant_message.content is None:
                assistant_message.content = "I'm processing your request."

            self.messages.append({"role": "assistant", "content": assistant_message.content})

            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    print(f"Tool call: {tool_call.function.name}")
                    if tool_call.function.name == "identifier_to_cik":
                        function_args = json.loads(tool_call.function.arguments)
                        print(f"Function args: {function_args}")
                        
                        cik = identifier_to_cik(function_args["ticker"])
                        return {'key':'text','value':cik}
                    elif tool_call.function.name == "get_company_concept":
                        function_args = json.loads(tool_call.function.arguments)
                        print(f"Function args: {function_args}")
                        table_dict_list = get_company_concept(function_args["ticker"], function_args["search_term"])
                        
                        # now we narrow down the table choices to reduce token usagge
                        labels = [table['label'] for table in table_dict_list]
                        matched_labels = fuzzy_search(query=function_args["search_term"], labels = labels)
                        matched_labels_str = ", ".join(matched_labels)
                        print(f"Matched labels: {matched_labels_str}")

                         # Have the LLM choose the best matching label
                        label_selection_messages = [
                            {"role": "assistant", "content": f"I've found the following matching labels: {matched_labels_str}."},
                            {"role": "user", "content": f"Please choose the best matching label for '{function_args['search_term']}' from these options: {matched_labels_str}"}
                        ]
                        
                        label_selection_response = self.client.chat.completions.create(
                            model="gpt-4o",
                            messages=label_selection_messages,
                            tools = [select_table_tool],
                            tool_choice={"type": "function", "function": {"name": "select_table"}}
                        )
                        self.total_tokens += label_selection_response.usage.total_tokens
                        
                        label = json.loads(label_selection_response.choices[0].message.tool_calls[0].function.arguments)['label']
                        print(f"Selected label: {label}")

                        # use the selected label to get the table
                        selected_table = select_table(table_dict_list, label)
                        print(f"Selected table: {selected_table}")

                        return {'key':'table','value':selected_table}

            return {'key':'text','value':'No tool call was made.'}

        except Exception as e:
            return f"An error occurred: {str(e)}"

    def get_total_tokens(self):
        return self.total_tokens
    
    def run(self):
        """Basic chatbot loop"""
        print("MuleBot: Hello! I'm here to assist you with questions related to the Securities and Exchange Commission. Type 'quit', 'exit', or 'bye' to end the conversation.")
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("MuleBot: Goodbye!")
                break
            
            response = self.process_message(user_input)
            response_type = response['key']

            if response_type == 'text':
                values = response['value']
                print(values[0])
            elif response_type == 'table':
                values = response['value']
                print(values)