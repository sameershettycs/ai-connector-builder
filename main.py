from dotenv import load_dotenv
load_dotenv()
import os
import pyfiglet
from crewai import Crew , Process
from tools import CustomPromptAnalysisTool, web_base_loader, extract_js_code_and_save
from rich.text import Text
from rich.console import Console
from chromadb import PersistentClient as Client
# from rich.spinner import Spinner


# Define the tool to analyze the user prompt
def main():
    console = Console()
    prompt_analysis_tool = CustomPromptAnalysisTool()
    figlet = pyfiglet.Figlet()
    from tasks import ConnectorTasks
    from agents import ConnectorAgents

    tasks = ConnectorTasks()
    agents = ConnectorAgents()
    # doc_tool = CustomCodeDocsSearchTool()
    # https://developers.google.com/gmail/api/auth/scopes
    client = Client()

    def clear_console():
        # For Windows
        if os.name == 'nt':
            os.system('cls')
        # For Mac and Linux (os.name is 'posix')
        else:
            os.system('clear')

    clear_console()
    ascii_art = figlet.renderText('AI-CONNECTOR BUILDER')
    terminal_width = os.get_terminal_size().columns
    lines = ascii_art.splitlines()
    llm_model="using gpt-4o-mini 🧠\n\n"
    centered_title = "\n".join(line.center(terminal_width) for line in lines)
    model_name = "\n".join(line.center(terminal_width) for line in llm_model.splitlines())
    print(centered_title)
    styled_text = Text(model_name, style="bold magenta")
    console.print(styled_text)





    # Create Agents
    # action_agent = agents.action_agent(tool=doc_tool.CustomCodeDocsSearchTool(url="https://www.contentstack.com/docs/developers/apis/content-management-api#create-an-entry"))
    # lookup_agent = agents.lookup_agent(tool=doc_tool.CustomCodeDocsSearchTool())
    # trigger_agent = agents.trigger_agent(tool=doc_tool.CustomCodeDocsSearchTool())
    # auth_agent = agents.auth_agent(tool=doc_tool.CustomCodeDocsSearchTool())

    def create_agent(agent_type, docLink=None):
        if agent_type == 'action':
            return agents.action_agent()
        elif agent_type == 'lookup':
            return agents.lookup_agent()
        elif agent_type == 'auth':
            return agents.auth_agent()
        elif agent_type == 'trigger':
            return agents.trigger_agent()
        else:
            return None

    # action.context = [loookup, trigger, auth]

    # Define function to route tasks based on the user prompt
    def route_tasks_based_on_prompt(prompt, docLink=None):
        analysis_result = prompt_analysis_tool.analyze(prompt)
        agents_to_initialize = []
        tasks_to_execute = []
        file_names= []
        if(len(analysis_result['action_types']) == 0):
            return None, None, None
        for action_type in analysis_result['action_types']:
            file_names.append(action_type)
            agent = create_agent(action_type, docLink)
            if agent:
                agents_to_initialize.append(agent)
                if action_type == 'action':
                    context = None
                    if docLink != '':
                        vectorstore = web_base_loader(docLink)
                        context = vectorstore.similarity_search(prompt)
                    tasks_to_execute.append(tasks.action_task(agent, prompt, context))
                elif action_type == 'lookup':
                    context = None
                    if docLink != '':
                        vectorstore = web_base_loader(docLink)
                        context = vectorstore.similarity_search(prompt)
                    tasks_to_execute.append(tasks.lookup_task(agent, prompt))
                elif action_type == 'auth':
                    context = None
                    if docLink != '':
                        vectorstore = web_base_loader(docLink)
                        context = vectorstore.similarity_search(prompt)
                    tasks_to_execute.append(tasks.auth_task(agent, prompt))
                elif action_type == 'trigger':
                    context = None
                    if docLink != '':
                        vectorstore = web_base_loader(docLink)
                        context = vectorstore.similarity_search(prompt)
                    tasks_to_execute.append(tasks.trigger_task(agent, prompt))

        return agents_to_initialize, tasks_to_execute, file_names if tasks_to_execute else None




    while True:
        prompt_text = Text()
        prompt_text.append("\n 💡 Enter a prompt to generate one or more of the following: ", style="bold blue")
        prompt_text.append("'action', 'trigger', 'lookup', or 'auth'. ", style="bold green")
        prompt_text.append("Type 'quit' to exit the application:\n", style="bold red")
        prompt_text.append(" >>>", style="bold blue")
        prompt = console.input(prompt_text)
        if prompt.lower() == "quit":
            exit()
        doc_prompt = Text()
        doc_prompt.append("\n 📑 Do you have a link to the documentation? If so, please provide it here, or press Enter if not:\n", style="bold yellow")
        doc_prompt.append(" >>>", style="bold yellow")
        docLink = console.input(doc_prompt)
        if docLink.lower() == "quit":
            exit()
        agentsList, tasks_list, file_names = route_tasks_based_on_prompt(prompt, docLink)
        if tasks_list is None:
                console.print("    Please enter a meaningful prompt", style="bold red")
        else:
            crew = Crew(
                    agents=agentsList,
                    tasks=tasks_list,
                    process=Process.sequential,
                    memory=True,
                    embedder={
                    "provider": "ollama",
                        "config":{
                            "model": "nomic-embed-text",
                            "vector_dimension": 1024
                        }
                    }
                )
            crew.kickoff()
            dirPathText = Text()
            dirPathText.append("\n 📂 Enter the directory path to save the files: ", style="bold blue")
            dirPath = console.input(dirPathText);
            for file in file_names:
                extract_js_code_and_save(file + ".js", dirPath)
