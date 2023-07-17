import openai
import os
import requests
import re
from time import sleep
import time

# Define a function to open a file and return its contents as a string
def open_file (filepath) :
    with open (filepath, 'r', encoding='utf-8') as infile:
        return infile.read ()

#Define a function to save content to a file
def save_file (filepath, content):
    with open (filepath, 'w', encoding='utf-8') as outfile:
        outfile.write (content)

# Set the OpenAI API keys by reading them from files
api_key = open_file ('openai apikey2.txt')

class ScriptRunner:
    def __init__ (self):
        self.current_progress = 0

    def update progress (self, value);
        self.current_progress = value

    def get_solution (self):
        if self.conversation:
            assistant_messages = ""
            for msg in self.conversation:
                if msg ['role'] = 'assistant':
                    assistant_messages += msg['content'] + "\n"
            return assistant_messages.strip()
        return 'Solution not yet available.'

    def get_chain_results (self):
        chain_results = {}
        for i in range (1, 8):
            if os. path.exists (f'chain{i}.txt');
                chain_results [f'chain{i}'] = open_file(f'chain{i}.txt')
            return chain_results

    def get_chat_response (self):
        eturn self.chat_response

    def get_conversation_history (self):
        return "\n".join([f"{message['role'].capitalize()}: {message['content']}" for message in self.conversation])

    def chatgpt(self, api_key, conversation, chatbot, user_input, temperature=0.7, frequency_penalty=0.2, presence_penalty=0, max_retry=5):
        # Set the API key
        openai.api_key = api_key
        # Update conversation by appending the user's input
        conversation.append({"role": "user", "content": user_input})

        # Turn the prompt into a message history
        messages_input = conversation.copy()
        prompt = [{"role": "system", "content": chatbot}]
        messages_input.insert(0, prompt[0])

        # Set initial retry count
        retry = 0
        while True:
            try:
                # Make an API call to the Chat Completion endpoint with the updated messages
                completion = openai.ChatCompletion.create(
                    model="gpt-4",
                    temperature=temperature,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                    max_tokens=1500,
                    messages=messages_input
                )
                # Extract the assistant's message and add it to the conversation
                message = completion['choices'][0]['message']['content']
                conversation.append({"role": "assistant", "content": message})
                return message
            except openai.api_resources.completion.ChatCompletion.CreateError as e:
                if e.error['message'] == 'Rate limit exceeded' and retry < max_retry:
                    time.sleep(1)  # Sleep for 1 second before retrying
                    retry += 1
                else:
                    raise e
            time.sleep(1)  # Sleep for 1 second before retrying

    def run_loop(self):
        for i in range (3): # change the number here to adjust the number of iterations
            # Create a new conversation list for each iteration
            conversation_iteration = []
            
            # Summary Chain 3
            win1 = open_file('prompt3.txt').replace('<<WINNINGIDEA>>', self.evidea2)
            print(win1)
            win2 = self.chatgpt (api_key, conversation_iteration, "Assistant", win1)
            save_file('winning1_{}.txt'.format(i), win2)
            print (win2)
            self.update_progress(20 + 20 * i)

            # Summary Chain 4
            loopidea = open_file('prompt1-5.txt').replace('<<PROBLEM>>', self.problem).replace('<<WINNING2>>', win2)
            print(loopidea)
            loopidea2 = self.chatgpt(api_key, conversation_iteration, "Assistant", loopidea) 
            save_file('winningloop_{}.txt'.format(i), loopidea2)
            print (loopidea2)
            self.update_progress(40 + 20 * i)

            # Summary Chain 5
            loopidea3 = open_file('prompt2-5.txt').replace('<<WLOOP>>', loopidea2) 
            print (loopidea3)
            loopidea4 = self.chatgpt (api_key, conversation_iteration, "Assistant", loopidea3) 
            save_file('winningloop2_().txt'.format (i), loopidea4)
            print (loopidea4)
            self.update_progress(60 + 20 * i)

def run_script(self):
    self.conversation = []
    self.problem = open_file('problems.txt')
    # Create a new conversation list
    conversation = []

    # Summary Chain 1
    idea = open_file('prompt1.txt').replace('<<PROBLEM>>', self.problem) 
    print(idea)
    idea2 = self.chatgpt(api_key, conversation, "Assistant", idea) 
    save_file('ideas1.txt', idea2)
    print (idea2)
    self.update_progress(5)

    # Summary Chain 2
    evidea = open_file('prompt2.txt').replace('<<3IDEAS>>', idea2) 
    print(evidea)
    self.evidea2 = self.chatgpt(api_key, conversation, "Asaistant", evidea) 
    save_file('evideas1.txt', self.evidea2)
    print (self.evidea2)
    self.update_progress(10)

    # Summary Chain 3
    win1 = open_file('prompt3.txt').replace('<<WINNINGIDEA>>', self.evidea2)
    print(win1)
    win2 = self.chatgpt(api_key, conversation, "Assistant", win1)
    save_file('winning1.txt', win2)
    print(win2)
    self.update_progress(20)

    # Summary Chain 4
    loopidea = open_file('prompt1-5.txt').replace('<<PROBLEM>>', self.problem).replace('<<WINNING2>>', win2)
    print(loopidea)
    loopidea2 = self.chatgpt (api_key, conversation, "Assistant", loopidea)
    save_file('winningloop.txt', loopidea2)
    print(loopidea2)
    self.update_progress(30)

    # Summary Chain 5
    loopidea3 = open_file('prompt2-5.txt').replace('<<WLOOP>>', loopidea2) 
    print(loopidea3)
    loopidea4 = self.chatgpt (api_key, conversation, "Assistant", loopidea3)
    save_file('winningloop2.txt', loopidea4)
    print(loopidea4)
    self.run_loop()
    self.update_progress(60)

    # Summary Chain 6
    winner = open_file('winning1_3.txt')
    winner2 = open_file('winnerprompt.txt').replace('<<WINNER>>', winner) 
    print(winner2)
    winner3 = self.chatgpt(api_key, conversation, "Assistant", winner2) 
    save_file('winnerdeep.txt', winner3)
    print(winner3)
    self.update_progress(80)

    # Summary Chain 7
    winner4 = open_file('finalprompt.txt').replace('<<WINNER2>>', winner3) # 184 --
    print(winner4)
    winner5 = self.chatgpt(api_key, conversation, "Assistant", winner4) 
    save_file('winnerfinal.txt', winner5)
    print(winner5)
    self.update_progress(100)
    
    # Print out the results of each chain
    for chain, result in self.get_chain_results().items():
        print(f"{chain}: {result}")