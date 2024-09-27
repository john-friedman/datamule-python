import openai
import json

from datamule.helper import identifier_to_cik
from datamule import Downloader, Parser
from .search import search_filing
from .tools import tools, return_title_tool
from .helper import get_company_concept, select_dict_by_title

downloader = Downloader()
parser = Parser()


class MuleBot:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)
        self.messages = [
            {"role": "system", "content": "You are a helpful, but concise, assistant to assist with questions related to the Securities and Exchanges Commission. You are allowed to guess tickers."}
        ]
        self.total_tokens = 0

    def process_message(self, user_input):

        new_message_chain = self.messages
        new_message_chain.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=new_message_chain,
                tools=tools,
                tool_choice="auto"
            )

            self.total_tokens += response.usage.total_tokens
            assistant_message = response.choices[0].message

            if assistant_message.content is None:
                assistant_message.content = "I'm processing your request."

            new_message_chain.append({"role": "assistant", "content": assistant_message.content})
            
            tool_calls = assistant_message.tool_calls
            if tool_calls is None:
                return {'key':'text','value':assistant_message.content}
            else:
                for tool_call in tool_calls:
                    print(f"Tool call: {tool_call.function.name}")
                    if tool_call.function.name == "identifier_to_cik":
                        function_args = json.loads(tool_call.function.arguments)
                        print(f"Function args: {function_args}")
                        
                        cik = identifier_to_cik(function_args["ticker"])
                        return {'key':'text','value':cik}
                    elif tool_call.function.name == "get_company_concept":
                        function_args = json.loads(tool_call.function.arguments)
                        print(f"Function args: {function_args}")
                        table_dict_list = get_company_concept(function_args["ticker"])
                        return {'key':'table','value':table_dict_list}
                    elif tool_call.function.name == "get_filing_urls":
                        function_args = json.loads(tool_call.function.arguments)
                        print(f"Function args: {function_args}")
                        result = downloader.download(**function_args,return_urls=True)
                        return {'key':'list','value':result}
                    elif tool_call.function.name == "find_filing_section_by_title":
                        function_args = json.loads(tool_call.function.arguments)
                        print(f"Function args: {function_args}")
                        # Parse the filing
                        data = parser.parse_filing(function_args["url"])

                        # find possible matches
                        section_dicts = search_filing(query = function_args["title"], nested_dict =data, score_cutoff=0.3)

                        # feed titles back to assistant
                        titles = [section['title'] for section in section_dicts]
                        new_message_chain.append({"role": "assistant", "content": f"Which of these titles is closest: {','.join(titles)}"})

                        title_response = self.client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=new_message_chain,
                            tools=[return_title_tool],
                            tool_choice="required"
                        )

                        title_tool_call = title_response.choices[0].message.tool_calls[0]
                        title = json.loads(title_tool_call.function.arguments)['title']
                        print(f"Selected title: {title}")
                        #print(f"Possible titles: {titles}")

                        # select the section
                        #section_dict = select_dict_by_title(data, title)
                        
                        # probably want to return full dict, and section label
                        return {'key':'filing','value':{'data':data,'title':title}}

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
                value = response['value']
                print(value)
            elif response_type == 'table':
                value = response['value']
                print(value)
            elif response_type == 'list':
                value = response['value']
                print(value)
            elif response_type == 'filing':
                value = response['value']
                print(value)
            else:
                value = response['value']
                print(value)