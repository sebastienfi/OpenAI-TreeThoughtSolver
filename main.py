import openai
import os
import time
import logging
import argparse
import streamlit as st

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define a function to open a file and return its contents as a string
def open_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as infile:
            return infile.read()
    except IOError as e:
        logging.error(f'Error opening file {filepath}: {e}')
        raise e

# Define a function to save content to a file
def save_file(filepath, content, mode='w'):
    try:
        with open(filepath, mode, encoding='utf-8') as outfile:
            outfile.write(content)
    except IOError as e:
        logging.error(f'Error writing to file {filepath}: {e}')

def save_debug(content):
    try:
        save_file('debug.txt', content, 'a')
    except IOError as e:
        logging.error(f'Error writing to file {filepath}: {e}')


# Set the OpenAI API keys by reading them from files
api_key = open_file('openai_apikey.md')

page_title = '# Chain Prompt + Tree of Thoughts 🎈'

st.set_page_config(page_title=page_title, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

st.markdown(page_title)

col1, col2 = st.columns([1, 4])
col1.subheader("Auto")
col2.subheader("Result")
bar = col2.progress(0)

class ScriptRunner:
    def __init__(self, loop_count):
        self.current_progress = 0
        self.loop_count = loop_count
        self.conversation = []
        self.problem = ""
        self.evidea2 = ""

    def update_progress(self, value):
        self.current_progress = value
        bar.progress(value)

    def get_solution(self):
        if self.conversation:
            assistant_messages = ""
            for msg in self.conversation:
                if msg['role'] == 'assistant':
                    assistant_messages += msg['content'] + "\n"
            return assistant_messages.strip()
        return 'Solution not yet available.'

    def get_chain_results(self):
        chain_results = {}
        for i in range(1, 8):
            if os.path.exists(f'chain{i}.md'):
                chain_results[f'chain{i}'] = open_file(f'chain{i}.md')
        return chain_results

    def get_chat_response (self):
        return self.chat_response

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
                save_debug(f'retry: {retry}\n')
                save_debug(f'messages_input: {messages_input}\n')

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
                save_debug(f'message: {message}\n')
                save_debug('----\n')
                return message

            except openai.error.RateLimitError as e:
                if e.error['message'] == 'Rate limit exceeded' and retry < max_retry:
                    retry_time = e.retry_after if hasattr(e, 'retry_after') else 3
                    print(f'Rate limit exceeded. Sleeping for {retry_time} seconds...')
                    time.sleep(retry_time)
                    retry += 1
                else:
                    raise e

            except openai.error.ServiceUnavailableError as e:
                retry_time = 10  # Adjust the retry time as needed
                print(f'Service is unavailable. Retrying in {retry_time} seconds...')
                time.sleep(retry_time)
                retry += 1

            except openai.error.APIError as e:
                retry_time = e.retry_after if hasattr(e, 'retry_after') else 10
                print(f'API error occurred. Retrying in {retry_time} seconds...')
                time.sleep(retry_time)
                retry += 1

            except OSError as e:
                retry_time = 5  # Adjust the retry time as needed
                print(f'Connection error occurred: {e}. Retrying in {retry_time} seconds...')
                time.sleep(retry_time)
                retry += 1

    def chain_process(self, prompt_file, save_file_name, replacements, api_key, conversation, chatbot):
        prompt = open_file(prompt_file)
        for placeholder, value in replacements.items():
            prompt = prompt.replace(placeholder, value)

        col1.markdown(f'- {prompt_file}')

        result = self.chatgpt(api_key, conversation, chatbot, prompt)
        save_file(save_file_name, result)

        with col2.expander(save_file_name):
            st.markdown(f'Prompt: {prompt_file}')
            st.markdown(f'File: {save_file_name}')
            st.markdown(result)

        return result

    def run_loop(self):
        for i in range(self.loop_count):
            # Create a new conversation list for each iteration
            conversation_iteration = []

            # Summary Chain 3
            replacements = {'<<WINNINGIDEA>>': self.evidea2}
            win2 = self.chain_process('prompts/discriminate.md', f'results/loop_{i}_discriminated.md', replacements, api_key, conversation_iteration, "Assistant")
            self.update_progress(20 + 20 * i)

            # Summary Chain 4
            replacements = {'<<PROBLEM>>': self.problem, '<<WINNING2>>': win2}
            loopidea2 = self.chain_process('prompts/brainstorm.md', f'results/loop_{i}_brained.md', replacements, api_key, conversation_iteration, "Assistant")
            self.update_progress(40 + 20 * i)

            # Summary Chain 5
            replacements = {'<<WLOOP>>': loopidea2}
            loopidea4 = self.chain_process('prompts/evaluate.md', f'results/loop_{i}_evaluated.md', replacements, api_key, conversation_iteration, "Assistant")
            self.update_progress(60 + 20 * i)

    def run_script(self):
        self.problem = open_file('problems.md')

        col2.markdown("Problems")
        col2.markdown(self.problem)

        conversation = []

        # Summary Chain 1
        replacements = {'<<PROBLEM>>': self.problem}
        idea2 = self.chain_process('prompts/brainstorm-initial.md', 'results/brainstormed.md', replacements, api_key, conversation, "Assistant")
        self.update_progress(5)

        # Summary Chain 2
        replacements = {'<<3IDEAS>>': idea2}
        self.evidea2 = self.chain_process('prompts/evaluate-initial.md', 'results/evaluated.md', replacements, api_key, conversation, "Assistant")
        self.update_progress(10)

        # Summary Chain 3
        replacements = {'<<WINNINGIDEA>>': self.evidea2}
        win2 = self.chain_process('prompts/discriminate.md', 'results/discriminated.md', replacements, api_key, conversation, "Assistant")
        self.update_progress(20)

        # Summary Chain 4
        replacements = {'<<PROBLEM>>': self.problem, '<<WINNING2>>': win2}
        loopidea2 = self.chain_process('prompts/brainstorm.md', 'results/brainstormed-2.md', replacements, api_key, conversation, "Assistant")
        self.update_progress(30)

        # Summary Chain 5
        replacements = {'<<WLOOP>>': loopidea2}
        loopidea4 = self.chain_process('prompts/evaluate.md', 'results/evaluated-2.md', replacements, api_key, conversation, "Assistant")
        self.update_progress(60)

        self.run_loop()

        # Summary Chain 6
        winner = open_file(f'results/loop_{self.loop_count - 1}_evaluated.md')
        replacements = {'<<WINNER>>': winner}
        winner3 = self.chain_process('prompts/deepen-win.md', 'results/win-deepened.md', replacements, api_key, conversation, "Assistant")
        self.update_progress(80)

        # Summary Chain 7
        replacements = {'<<WINNER2>>': winner3}
        winner5 = self.chain_process('prompts/justify-win.md', 'results/win-justified.md', replacements, api_key, conversation, "Assistant")
        self.update_progress(95)

        # Create a solution.md
        timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
        solution_file_name = f'solution_{timestr}.md'
        save_file(solution_file_name, '# SOLUTIONS\n\n', 'w')
        save_file(solution_file_name, '## Stated problems\n\n', 'a')
        save_file(solution_file_name, self.problem, 'a')
        save_file(solution_file_name, '\n\n', 'a')
        save_file(solution_file_name, '## Initial brainstorm\n\n', 'a')
        save_file(solution_file_name, self.evidea2, 'a')
        save_file(solution_file_name, '\n\n', 'a')
        save_file(solution_file_name, '## Second brainstorm\n\n', 'a')
        save_file(solution_file_name, loopidea2, 'a')
        save_file(solution_file_name, '\n\n', 'a')
        save_file(solution_file_name, '## Second brainstorm\n\n', 'a')
        save_file(solution_file_name, loopidea2, 'a')
        save_file(solution_file_name, '\n\n', 'a')
        save_file(solution_file_name, f'## Solution\n', 'a')
        save_file(solution_file_name, f'After {self.loop_count} iterations, we deepened the thoughts on the solution.\n\n', 'a')
        save_file(solution_file_name, winner3, 'a')
        save_file(solution_file_name, '\n\n', 'a')
        save_file(solution_file_name, f'## Final thoughts on the solution\n\n', 'a')
        save_file(solution_file_name, winner5, 'a')
        self.update_progress(100)

        # Print out the results of each chain
        for chain, result in self.get_chain_results().items():
            logging.info(f'{chain}: {result}')
            with st.sidebar:
                st.divider()
                st.markdown(chain)
                st.divider()
                st.markdown(result)
                st.divider()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the script with a specific number of loops.')
    parser.add_argument('--loops', type=int, default=3, help='The number of loops to run.')
    args = parser.parse_args()

    runner = ScriptRunner(loop_count=args.loops)
    runner.run_script()
