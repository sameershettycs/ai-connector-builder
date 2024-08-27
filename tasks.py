from textwrap import dedent
from crewai import Task

class ConnectorTasks():
	def action_task(self, agent, prompt, context=None,docLink=None):
		return Task(
			description=dedent(f"""\
				Create a new javascript file with action class based on the given prompt and documentation, it should use lookup mechanism to fetch name and use it to fetch field values. Prompt :{prompt} Context:{context} documentation Link :{docLink}"""),
			expected_output="""
				class Action {
                title = "{Add title here}";

                description =
                    "{Add description here}";

                help = "";

                inputSchema = {
                    type: "object",
                    required: [{Add list of required fields here}],
                    properties: {
                {Add required fields here using JSON schema format}
                    },
                };

                async run(event) {
                    const fetch = require("node-fetch");
                    const input = event.input;
                    const auth = event.auth;
                    {Define the run method here and return appropriate response and throw error if any}
                }
            }""",
			agent=agent,
			output_file="action.js"
		)

	def lookup_task(self, agent, prompt , context=None, docLink=None):
		return Task(
			description=dedent(f"""\
				Create a new javascript file with lookup class based on the given prompt and documentation, it should create the lookup and then pass the lookup name to action and trigger to use it to fetch values.
				Prompt :{prompt} Context:{context} documentation Link :{docLink}"""),
			expected_output="""class Lookup {
                title = "{Add title here}";

                description = "{Add description here}";

                name = "{Add appropriate name here}";

                async run(event) {
                    const fetch = require("node-fetch");
                    const auth = event.auth;
                    const input = event.input;
                    {Define the run method here and return appropriate response and throw error if any}
                }
            }""",
			agent=agent,
			output_file="lookup.js"
		)

	def trigger_task(self, agent,prompt, context=None, docLink=None):
		return Task(
			description=dedent(f"""\
				Create a new javascript file with trigger class based on the given prompt and documentation, it should use lookup mechanism to fetch name and use it to fetch field values. Prompt :{prompt} Context:{context} documentation Link :{docLink}"""),
			expected_output="""
				 class Trigger {
                title = {Add title here};
                description =
                    "{Add description here}";
                triggerType = "{Add trigger type here}";
                help = "";

                inputSchema = {
                    type: "object",
                    required: [{Add list of required fields here}],
                    properties: {
                {Add required fields here using JSON schema format}
                    },
                };

                async register(event) {
                    const fetch = require("node-fetch");

                    const auth = event.auth;
                    const input = event.input;
                    const webhookURL = event.options.webhookUrl;

                    {Define the register method here and return appropriate response and throw error if any}
                }

                // incase of instant trigger, unregister method is required
                async unregister(event) {
                    const fetch = require("node-fetch");
                    const webhookId = event.options.getMeta("uid");
                    const auth = event.auth;
                    {Define the unregister method here and return appropriate response and throw error if any}
                }
            }""",
			agent=agent,
			output_file="trigger.js"
			# async_execution=True,
		)

	def auth_task(self, agent, prompt ,context=None, docLink=None):
		return Task(
			description=dedent(f"""\
				Create a new javascript file with auth class based on the given prompt and documentation, it should create either OAuth or Custom type of auth which will be used to pass access_token or api_key for trigger, lookup and action to use. Prompt :{prompt} Context:{context} documentation Link :{docLink}"""),
			expected_output="""
				CustomAuth:
            class Auth {
                title = "{Add title here}";

                description = "{Add description here}";

                authType = "{Add auth type here}";

                help = "";

                inputSchema = {
                    type: "object",
                    required: [{Add list of required fields here}],
                    properties: {
                {Add required fields here using JSON schema format}

                    }
                };

                async validate(event) {
                    const fetch = require('node-fetch');
                    const { api_key, org_id } = event.input

                    {Define the validate method here and return appropriate response and throw error if any}
                }
            }

            OAuth2Auth:
            class Auth {
                // title of auth
                title = "{Add title here}";

                // description of auth
                description = "{Add description here}";

                // type of auth
                authType = "{Add auth type here}";

                // doc url for help
                help = "";

                // oauth 2 client id
                clientId = "";

                // oauth 2 client secret
                clientSecret = "";

                // authorization init url
                authorizeURL = "{Add authorization url here}";

                // access token fetch url
                accessURL = "{Add access token url here}";

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
                    required: [{Add list of required fields here}],
                    properties: {
                    {Add required fields here using JSON schema format}
                    },
                };
            }""",
			agent=agent,
			output_file="auth.js"
		)
