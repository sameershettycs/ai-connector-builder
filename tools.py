import re
import os
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rich.text import Text
from rich.console import Console

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
)

console = Console()
class CustomPromptAnalysisTool:
    def __init__(self):
        self.keywords = {
            'action': ['action', 'run'],
            'lookup': ['lookup'],
            'auth': ['auth', 'authenticate', 'authorize'],
            'trigger': ['trigger', 'activate', 'start', 'initiate', 'webhook']
        }

    def analyze(self, prompt):
        prompt_lower = prompt.lower()
        matched_action_types = set()
        for action_type, keywords in self.keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                matched_action_types.add(action_type)
        return {'action_types': list(matched_action_types)}

def web_base_loader(url):
    loader = WebBaseLoader(url)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    all_splits = text_splitter.split_documents(data)
    vectorstore = Chroma.from_documents(documents=all_splits, embedding=embeddings)
    return vectorstore;

def extract_js_code_and_save(file_path, file_destination_path="./"):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        code_block_regex = r'```javascript([\s\S]*?)```'
        code_blocks = re.findall(code_block_regex, content)
        code_blocks = [code_block.strip() for code_block in code_blocks]
        formatted_code = "\n\n".join(code_blocks)
        file_name_text = Text()
        file_name_text.append(f"\n 📝 Enter file name (e.g., getAllRecords.js) for {file_path}: ", style="bold Orange");
        file_name = console.input(file_name_text)
        if not file_name:
            console.print("    Error: File name cannot be empty.")
            return
        if not file_destination_path.endswith(os.path.sep):
            file_destination_path += os.path.sep
        full_destination_path = os.path.join(file_destination_path, file_name)
        os.makedirs(file_destination_path, exist_ok=True)
        with open(full_destination_path, 'w') as file:
            file.write(formatted_code)
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"    Warning: Original file {file_path} does not exist.")
        console.print(f"\n ✅ Formatted code has been saved to {full_destination_path}",style="bold green")
    except Exception as e:
        print(f"    An error occurred: {e}")

def clear_console():
        # For Windows
    if os.name == 'nt':
        os.system('cls')
        # For Mac and Linux (os.name is 'posix')
    else:
        os.system('clear')
