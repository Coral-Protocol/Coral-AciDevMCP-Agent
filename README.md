## [ACI DEV MCP Agent](https://github.com/Coral-Protocol/firecrawl-coral-agent.git)

ACI Dev agent capable of searching for relevant functions based on user intent and executing those functions with the required parameters.

## Responsibility
ACI.dev is the open-source infrastructure layer for AI-agent tool-use and VibeOps. It gives AI agents intent-aware access to 600+ tools with multi-tenant auth, granular permissions, and dynamic tool discovery—exposed as either direct function calls or through a Unified Model-Context-Protocol (MCP) server.


## Details
- **Framework**: LangChain
- **Tools used**: Firecrawl MCP Server Tools, Coral Server Tools
- **AI model**: OpenAI GPT-4o
- **Date added**: June 4, 2025
- **Reference**: [ACI DEV Repo](https://github.com/aipotheosis-labs/aci)
- **License**: MIT

## Setup the Agent

### 1. Clone & Install Dependencies

<details>

Ensure that the [Coral Server](https://github.com/Coral-Protocol/coral-server) is running on your system. If you are trying to run Open Deep Research agent and require an input, you can either create your agent which communicates on the coral server or run and register the [Interface Agent](https://github.com/Coral-Protocol/Coral-Interface-Agent) on the Coral Server  


```bash
# In a new terminal clone the repository:
git clone https://github.com/Coral-Protocol/Coral-AciDevMCP-Agent

# Navigate to the project directory:
cd Coral-AciDevMCP-Agent

# Download and run the UV installer, setting the installation directory to the current one
curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=$(pwd) sh

# Create a virtual environment named `.venv` using UV
uv venv .venv

# Activate the virtual environment
source .venv/bin/activate

# install uv
pip install uv

# Install dependencies from `pyproject.toml` using `uv`:
uv sync
```

</details>

### 2. Configure Environment Variables

<details>

Get the API Key:
[OpenAI](https://platform.openai.com/api-keys) || 
[Github Token](https://github.com/settings/tokens)

```bash
# Create .env file in project root
cp -r .env_sample .env
```

Check if the .env file has correct URL for Coral Server and adjust the parameters accordingly.

</details>

## Run the Agent

You can run in either of the below modes to get your system running.  

- The Executable Model is part of the Coral Protocol Orchestrator which works with [Coral Studio UI](https://github.com/Coral-Protocol/coral-studio).  
- The Dev Mode allows the Coral Server and all agents to be seperately running on each terminal without UI support.  

### 1. Executable Mode

Checkout: [How to Build a Multi-Agent System with Awesome Open Source Agents using Coral Protocol](https://github.com/Coral-Protocol/existing-agent-sessions-tutorial-private-temp) and update the file: `coral-server/src/main/resources/application.yaml` with the details below, then run the [Coral Server](https://github.com/Coral-Protocol/coral-server) and [Coral Studio UI](https://github.com/Coral-Protocol/coral-studio). You do not need to set up the `.env` in the project directory for running in this mode; it will be captured through the variables below.

<details>

For Linux or MAC:

```bash
# PROJECT_DIR="/PATH/TO/YOUR/PROJECT"

applications:
  - id: "app"
    name: "Default Application"
    description: "Default application for testing"
    privacyKeys:
      - "default-key"
      - "public"
      - "priv"

registry:
  Aacidevmcp_agent:
    options:
      - name: "API_KEY"
        type: "string"
        description: "API key for the service"
      - name: "ACI_OWNER_ID"
        type: "string"
        description: "ACI OWNER IDfor the service"
      - name: "ACI_API_KEY"
        type: "string"
        description: "ACI API KEYfor the service"
    runtime:
      type: "executable"
      command: ["bash", "-c", "${PROJECT_DIR}/run_agent.sh main.py"]
      environment:
        - name: "API_KEY"
          from: "API_KEY"
        - name: "ACI_OWNER_ID"
          from: "ACI_OWNER_ID"
        - name: "ACI_API_KEY"
          from: "ACI_API_KEY"
        - name: "MODEL_NAME"
          value: "gpt-4.1"
        - name: "MODEL_PROVIDER"
          value: "openai"
        - name: "MODEL_TOKEN"
          value: "16000"
        - name: "MODEL_TEMPERATURE"
          value: "0.3"

```
For Windows, create a powershell command (run_agent.ps1) and run:

```bash
command: ["powershell","-ExecutionPolicy", "Bypass", "-File", "${PROJECT_DIR}/run_agent.ps1","main.py"]
```

</details>

### 2. Dev Mode

Ensure that the [Coral Server](https://github.com/Coral-Protocol/coral-server) is running on your system and run below command in a separate terminal.

<details>

```bash
# Run the agent using `uv`:
uv run python main.py
```

You can view the agents running in Dev Mode using the [Coral Studio UI](https://github.com/Coral-Protocol/coral-studio) by running it separately in a new terminal.

</details>


## Example

<details>

```bash
# Input:
can you ask aci dev to check my github- sd2879 and return me recent repository i made

#Output:
The GitHub repositories created by the user sd2879 are:

1. ai-taxi-stand - https://github.com/sd2879/ai-taxi-stand
2. archscan-mistral-ai - https://github.com/sd2879/archscan-mistral-ai
3. cad_pdf_extractror - https://github.com/sd2879/cad_pdf_extractror
4. docker-image-CI-CD - https://github.com/sd2879/docker-image-CI-CD
5. llama_scoutie_ai - https://github.com/sd2879/llama_scoutie_ai
6. mangalX - https://github.com/sd2879/mangalX
7. quant_track_crypto - https://github.com/sd2879/quant_track_crypto
8. rag_pipeline - https://github.com/sd2879/rag_pipeline
9. rooftop_solar_potential - https://github.com/sd2879/rooftop_solar_potential
10. rooftop_solar_potential_using_detectron2 - https://github.com/sd2879/rooftop_solar_potential_using_detectron2
11. sd2879 - https://github.com/sd2879/sd2879
12. test-repo - https://github.com/sd2879/test-repo

```

</details>

### Creator Details
- **Name**: Suman Deb
- **Affiliation**: Coral Protocol
- **Contact**: [Discord](https://discord.com/invite/Xjm892dtt3)

