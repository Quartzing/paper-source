import openai
import os


class GeneralAgent(object):

    role_ = ""

    def __init__(self, model: str='gpt-3.5-turbo'):
        self.system_message_ = {"role": "system", "content": self.role_} # system prompt
        self.model_ = model # use different model

    def query(self, user_query: str):
        print(f'Sending request to OpenAI: {user_query}')
        messages = [self.system_message_,
                    {"role": "user", "content": user_query}] # messages include system prompt and user prompt
        response = openai.ChatCompletion.create(model=self.model_, messages=messages) # use openai to creat the answer
        answer = response.choices[0]["message"]["content"]  # choose the first return as answer
        print(f'Response from OpenAI: {answer}')
        return answer


class Researcher(GeneralAgent):
    # system prompt
    role_ = "You are a professional researcher, you had PhD and is a professor of Stanford University. \
        Your expertise is reading and summarizing scientific papers. When you are given a query, \
        a series of paper content as context and the title of the paper, you always return a very detailed answer to the query."
