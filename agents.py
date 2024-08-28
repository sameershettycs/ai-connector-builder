from textwrap import dedent
from crewai import Agent
from langchain_openai import ChatOpenAI
import os
# from langchain_ollama.chat_models import ChatOllama

# llm = ChatGoogleGenerativeAI(
#     model="gemini-1.5-pro",
#     temperature=1,
#     max_tokens=None,
#     timeout=None,
#     max_retries=2,
# )

# llm = ChatOllama(
#     model= 'codeqwen',
#     base_url="http://localhost:11434",
# 	temperature=0.9,
# )

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=.2,
    max_tokens=None,
    timeout=None,
    max_retries=2,
	api_key=os.getenv("API_KEY"),
    organization=os.getenv("ORG_ID")
)
class ConnectorAgents():
	def action_agent(self,tool=None):
		return Agent(
			role='You are a Senior Software Developer with expertise in JavaScript and Node.js.',
			goal="""Creates a JavaScript file with an Action class based on the given prompts and documentation. The file should contain only the JavaScript code for the Action class without any explanatory text or comments. The generated code uses lookup names created by the lookup agent as input to automatically fill options for action fields. The file should include the class definition and it uses JSON Schema for inputs and must have a run method required for execution.
        Example:
        class Action {
            title = "Create Record";

            description = "This action adds a record(s) in Airtable.";

            help = "https://www.contentstack.com/docs/developers/automation-hub-connectors/airtable/#create-record";

            inputSchema = {
                type: "object",
                required: ["base_id", "table_id", "body"],
                properties: {
                base_id: {
                    type: "string",
                    title: "Database Name/ID",
                    description: "Select a database created in your Airtable account.",
                    minLength: 3,
                    lookup: {
                    id: "get_bases"
                    }
                },
                table_id: {
                    type: "string",
                    title: "Table Name/ID",
                    description: "Select a table to create a new record(s).",
                    minLength: 3,
                    lookup: {
                    id: "get_tables",
                    deps: ["base_id"]
                    }
                },
                body: {
                    type: "string",
                    title: "Record Data",
                    format: "textarea",
                    description: "Enter the data in the key-value pair in JSON format.",
                    default: `{
                    "records": [
                        {
                        "fields": {

                        }
                        }
                    ]
                    }`,
                    minLength: 5
                }
                }
            };

            async run(event) {
                const fetch = require("node-fetch");
                const input = event.input;
                const auth = event.auth;

                const headers = {
                Authorization: `Bearer ${auth.access_token}`,
                "Content-Type": "application/json"
                };
                const url = `https://api.airtable.com/v0/${input.base_id}/${input.table_id}`;

                let body = input.body;

                if (typeof input.body === "string") {
                try {
                    body = JSON.parse(input.body);
                } catch (e) {
                    throw new Error("Invalid record, must be a json object");
                }
                }

                if (!body || typeof body !== "object") {
                throw new Error("Invalid record, must be a json object");
                }

                const requestOptions = {
                method: "POST",
                headers,
                body: JSON.stringify(body)
                };

                const response = await fetch(url, requestOptions);

                const res = await response.json();

                if (response.ok) {
                return res;
                } else {
                throw new Error(res.error.message ? res.error.message : res.error);
                }
            }
        }""",
			backstory=dedent("""\
					 An expert in javascript language and designing and implementing new actions.
        Used name of lookup created by the lookup agent to create automatic filling options for action field."""),
			verbose=False,
			llm=llm,
		    allow_delegation=False,
			# tools=[tool]
		)

	def lookup_agent(self,tool=None):
		return Agent(
			role='You are a Senior Software Developer with expertise in JavaScript and Node.js.',
			goal="""Creates a new JavaScript file with a Lookup class based on the given prompts and documentation. The file should contain only the JavaScript code for the Lookup class without any explanatory text or comments. The generated code should create an array of objects formatted as [{value: "", title: ""}, {value: "", title: ""}]. These lookup name values will be used by the action agent to create automatic filling options for action fields. The file should include the class definition and a `run` method required for execution.
            Example:
            class Lookup {
                title = "Get Bases";

                description = "Get list of bases from an account.";

                name = "get_bases";

                async run(event) {
                    const fetch = require("node-fetch");
                    const auth = event.auth;

                    const headers = {
                    Authorization: `Bearer ${auth.access_token}`
                    };
                    const url = `https://api.airtable.com/v0/meta/bases`;

                    const response = await fetch(url, { method: "GET", headers }).catch((e) => {
                    let err = {
                        error_name: e.name,
                        message: e.message,
                        status: e?.status
                    };
                    throw err;
                    });
                    const res = await response.json();

                    if (response.ok) {
                    const result = {
                        values: []
                    };

                    result.values = res.bases.map((entry) => {
                        return {
                        title: entry.name,
                        value: entry.id
                        };
                    });

                    return result;
                    }

                    throw res.error.message ? res.error.message : res.error;
                }
            }""",
			backstory=dedent("""\
					An expert in javascript language and designing and implementing new lookup.
        Used name of lookup created here will be passed to action agent and then that agent will use it to create automatic filling options for action field."""),
			verbose=False,
			llm=llm,
        allow_delegation=False,
        # tools=[tool]
		)

	def trigger_agent(self,tool=None):
		return Agent(
			role='You are a Senior Software Developer with expertise in JavaScript and Node.js.',
			goal="""Creates a new JavaScript file with a Trigger class based on the given prompts and documentation. The file should contain only the JavaScript code for the Trigger class without any explanatory text or comments. The generated code should primarily work with webhooks to create and manage triggers. It should include `register` and `unregister` methods for creating and deleting webhooks. The class may use the docs search tool to search for documentation and create a trigger based on that documentation. The file should include the class definition and the `register` and `unregister` methods required for execution.
        Example:
        class Trigger {
            title = "Box";
            description =
                "This event is triggered when a file is uploaded in your Box cloud drive.";
            triggerType = "instant";
            help = "";

            inputSchema = {
                type: "object",
                required: ["event", "folder_id"],
                properties: {
                event: {
                    type: "string",
                    title: "Select an Event",
                    description: "Select an event to invoke the trigger",
                    default: "FILE.UPLOADED",
                    enum: ["FILE.UPLOADED"],
                    enumNames: ["File Uploaded"],
                },
                folder_id: {
                    type: "string",
                    title: "Select Folder Name",
                    description:
                    "Select a folder to invoke the trigger. Please make sure to create new folder in your Box cloud drive since the #root folder cannot be chosen. Configuring a trigger anywhere with the same folder will result in an error, as only one trigger can be assigned to a single folder.",
                    minLength: 1,
                    lookup: {
                    id: "get_folders_v2",
                    edit: true,
                    nested: true
                    },
                },
                },
                prefetch: {
                lookup: "prefetch_box_trigger",
                },
            };

            async register(event) {
                const fetch = require("node-fetch");

                const auth = event.auth;
                const input = event.input;
                const webhookURL = event.options.webhookUrl;

                let body = {
                triggers: [input.event],
                address: webhookURL,
                target: {
                    id: input.folder_id,
                    type: "folder",
                },
                };

                const res = await fetch(`https://api.box.com/2.0/webhooks`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    authorization: `Bearer ${auth.access_token}`,
                },
                body: JSON.stringify(body),
                });

                if (res.ok) {
                const data = await res.json();
                event.options.setMeta("uid", data.id);
                return data;
                }
                throw res.statusText;
            }

            // incase of instant trigger, unregister method is required
            async unregister(event) {
                const fetch = require("node-fetch");
                const webhookId = event.options.getMeta("uid");
                const auth = event.auth;
                const res = await fetch(`https://api.box.com/2.0/webhooks/${webhookId}`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                    authorization: `Bearer ${auth.access_token}`,
                },
                });
                if (res.ok) {
                return res.statusText;
                }
                throw res.statusText;
            }
        }
""",
			backstory=dedent("""\
		An expert in javascript language and designing and implementing new trigger.
        It mainly works on webhooks to create an triggers and has a register and unregister function where webhooks are created and deleted. Is uses the docs search tool to search for documentation and create a trigger based on the documentation.
        And also uses the lookup name values created by lookup agent as input to automatic filling options for trigger field."""),
			verbose=False,
			llm=llm,
        allow_delegation=False,
            # tools=[tool]

		)

	def auth_agent(self,tool=None):
		return Agent(
			role='You are a Senior Software Developer with expertise in JavaScript and Node.js.',
			goal="""Creates a new JavaScript file with an Auth class based on the given prompts and documentation. The class supports two types of authentication: custom and OAuth. For custom auth, it handles fields such as `api_key` and `secrets` to be used directly during the execution of actions, lookups, and triggers. For OAuth, it manages `client_id` and `client_secret` and uses the OAuth2.0 protocol to obtain bearer access and refresh tokens. The class may use the docs search tool to search for documentation and create an auth implementation based on that documentation. The file should include the class definition and a `validate` method required for execution.
        Example OAuth:
        class Auth {
            // title of auth
            title = "Box";

            // description of auth
            description = "Box auth";

            // type of auth
            authType = "oauth2";

            // doc url for help
            help = "";

            // oauth 2 client id
            clientId = "";

            // oauth 2 client secret
            clientSecret = "";

            // authorization init url
            authorizeURL = "https://account.box.com/api/oauth2/authorize";

            // access token fetch url
            accessURL = "https://api.box.com/oauth2/token";

            // url to refresh the token when current access token expired
            refreshURL = this.accessURL;

            // body content type for all calls
            contentType = "application/x-www-form-urlencoded";

            scopeJoinChar = " ";

            // authorization init call options
            authorizeURLOptions = {
                state: "{{state}}",
                client_id: "{{client_id}}",
                scope: "{{scope}}",
                redirect_uri: "{{redirect_uri}}",
                response_type: "code",
            };

            // access token fetch url call options
            accessURLOptions = {
                grant_type: "authorization_code",
                client_id: "{{client_id}}",
                client_secret: "{{client_secret}}",
                code: "{{code}}",
                // scope: "{{scope}}",
                // redirect_uri: "{{redirect_uri}}",
            };

            // options to refresh token call when current access token expired
            refreshURLOptions = {
                refresh_token: "{{refresh_token}}",
                client_id: "{{client_id}}",
                client_secret: "{{client_secret}}",
                grant_type: "refresh_token",
                // redirect_uri: "{{redirect_url}}",
            };

            // json schema to get oauth scopes from user
            inputSchema = {
                type: "object",
                required: ["scope"],
                properties: {
                scope: {
                    title: ".scope",
                    type: "object",
                    properties: {
                    root_readwrite: {
                        type: "boolean",
                        title: "Read and write all files and folders stored in Box.",
                        default: true,
                    },
                    manage_webhook: {
                        type: "boolean",
                        title: "Manage webhooks.",
                        default: true,
                    },
                    },
                },
                },
            };
        }

        Example Custom:
        class Auth {
            title = "ChatGPT";

            description = "chatGPT auth";

            authType = "custom";

            help = "";

            inputSchema = {
                type: "object",
                required: ["api_key","org_id"],
                properties: {
                api_key: {
                    type: "string",
                    title: "API Key",
                    description:
                    "Enter your OpenAI API Key. You can get it or generate a new key from https://platform.openai.com/account/api-keys",
                    minLength: 6
                },
                org_id: {
                    type: "string",
                    title: "Organization ID",
                    description:
                    "Enter your OpenAI Organization ID. You can get it from https://platform.openai.com/account/org-settings",
                    minLength: 6
                }
                }
            };

            async validate(event) {
                const fetch = require('node-fetch');
                const { api_key, org_id } = event.input

                const response = await fetch("https://api.openai.com/v1/models", {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${api_key}`,
                    'OpenAI-Organization':  `${org_id}`
                },
                })

                if (response.status === 200) {
                return await response.json();
                }
                throw await response.statusText;
            }
        }""",
			backstory=dedent("""\
					An expert in javascript language and designing and implementing new authentication mechanisms.
        Used docs search tool to search for documentation and create an auth based on the documentation. It can either be custom or oauth."""),
			verbose=False,
			llm=llm,
            allow_delegation=False,
            # tools=[tool]
		)
