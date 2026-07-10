Step 1: Start Kestra
This module includes a docker-compose.yml with Kestra pre-configured:

cd 03-orchestration
docker compose up -d
Once the container starts, access the Kestra UI at http://localhost:8080.

To shut down Kestra:

docker compose down
Step 2: Obtain API Keys
Gemini API Key (Required)

Visit Google AI Studio
Sign in with your Google account
Click "Create API Key" and copy your key
The free tier is sufficient for light use, but rate limits are relatively low — you may hit quota quickly if you run the agent and multi-agent flows repeatedly. If you run into 429 Resource Exhausted errors, wait a minute before retrying, or consider upgrading to a paid tier.

OpenAI API Key (Required for flow 3)

Visit platform.openai.com and sign in or create an account
Go to API keys and create a new key
Tavily API Key (Required for web search: flows 3, 5, and 6)

Visit Tavily
Sign up for the free tier
Get your API key from the dashboard
The free tier includes 1,000 searches/month.

Step 3: Configure API Keys in Kestra  
Kestra reads secrets from environment variables prefixed with SECRET_ where the value is base64-encoded. Export your keys before starting Kestra:

export GEMINI_API_KEY="your-gemini-api-key-here" # required
export SECRET_GEMINI_API_KEY=$(echo -n $GEMINI_API_KEY | base64) # required
export SECRET_OPENAI_API_KEY=$(echo -n "your-openai-api-key-here" | base64)   # required for flow 3
export SECRET_TAVILY_API_KEY=$(echo -n "your-tavily-api-key-here" | base64)   # optional
Then start (or restart) Kestra:

docker compose up -d
In flows, reference secrets with {{ secret('GEMINI_API_KEY') }} — omit the SECRET_ prefix when calling secret().

Warning

Never commit API keys to Git!

Step 4: Import Example Flows
cd 03-orchestration

# Adjust username and password to match your Kestra setup
curl -X POST -u 'admin@kestra.io:Admin1234!' http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/1_chat_without_rag.yaml
curl -X POST -u 'admin@kestra.io:Admin1234!' http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/2_chat_with_rag.yaml
curl -X POST -u 'admin@kestra.io:Admin1234!' http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/3_rag_with_websearch.yaml
curl -X POST -u 'admin@kestra.io:Admin1234!' http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/4_simple_agent.yaml
curl -X POST -u 'admin@kestra.io:Admin1234!' http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/5_web_research_agent.yaml
curl -X POST -u 'admin@kestra.io:Admin1234!' http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/6_multi_agent_research.yaml
Alternatively, copy-paste the flow YAML directly into Kestra's UI.

Step 5: Run Your First Agent
Open Kestra UI at http://localhost:8080
Navigate to the zoomcamp namespace
Find the 4_simple_agent flow and click "Execute"
Leave default inputs or customize them
Watch the execution and review the outputs
Then run 5_web_research_agent and 6_multi_agent_research and analyze the logs and outputs