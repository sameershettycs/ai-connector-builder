from main import main
import os
from rich.text import Text
from rich.console import Console
from tools import clear_console

def init():
    clear_console()
    console = Console()
    if os.getenv("API_KEY") == None and os.getenv("ORG_ID") == None:
            prompt_env_api = Text()
            prompt_env_org_id = Text()
            prompt_env_api.append("\n    Enter OPENAI-API-KEY : ", style="bold yellow")
            prompt_env_org_id.append("\n    Enter OPENAI-ORG-ID : ", style="bold yellow")
            API_KEY = console.input(prompt_env_api)
            ORG_ID = console.input(prompt_env_org_id)
            with open("./.env", 'w') as file:
                file.write(f"API_KEY='{API_KEY}'\nORG_ID='{ORG_ID}'")
            console.print("\n    Environment variables set successfully ✅\n\n    Restart the application!", style="bold green")
            exit()
    main()


init()
