import sys
import os

from dotenv import load_dotenv

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI

from langchain.tools import BaseTool, StructuredTool, tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import mailtrap as mt

load_dotenv('.env')

# your mailtrap token
token = os.environ.get("MAILTAP_TOKEN")

# define your sender email address
sender: str = os.environ.get("MAILTAP_SENDER")

@tool
def send_email(to: str, subject: str, text: str):
    """send email via MailtrapClient"""
    
    # create mail object
    mail = mt.Mail(
        sender=mt.Address(email="mailtrap@herzens.app", name="Mailtrap Test"),
        to=[mt.Address(email=to)],
        subject=subject,
        text=text,
    )

    # create client and send
    client = mt.MailtrapClient(token=token)
    client.send(mail)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """You are an email delivery platform. Use your tool to send emails.
         If you do not have a tool to answer the question, say i can't process your question. 
         You have to get three parameters from human: 
         to, subject, text:
         - to: the recipient email address
         - subject: the email subject
         - text: the email body
         
        Only do your tasks. Do not ask for help.
        """),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

# Choose the LLM that will drive the agent
llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)

# Setup the toolkit
toolkit = [send_email]

# Construct the OpenAI Tools agent
agent = create_openai_tools_agent(llm, toolkit, prompt)

# Create an agent executor by passing in the agent and tools
agent_executor = AgentExecutor(agent=agent, tools=toolkit, verbose=True)

yellow = "\033[0;33m"
green = "\033[0;32m"
white = "\033[0;39m"

chat_history = []
print(f"{yellow}---------------------------------------------------------------------------------")
print('I am an email delivery platform. How can I help you?')
print('---------------------------------------------------------------------------------')

# example input: 
'''
Please send an email to taherfattahi11@gmail.com with the subject "You are awesome!" 
and the body of the email should be: "Congratulations on successfully sending a test email with Mailtrap!"
'''

while True:
    query = input(f"{green}Prompt: ")
    if query == "exit" or query == "quit" or query == "q" or query == "f":
        print('Exiting')
        sys.exit()
    if query == '':
        continue
    result = agent_executor.invoke({"input": query})
    print(f"\n{white}Answer: " + result["output"] + "\n")
    chat_history.append((query, result["output"]))