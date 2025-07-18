import urllib.parse
from dotenv import load_dotenv
import os
import asyncio
import logging
import traceback
import json
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE, MCPServerStdio
import logfire
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logfire.configure()  
logfire.instrument_pydantic_ai() 

# Load environment variables
load_dotenv(override=True)

# Get environment variables
base_url = os.getenv("CORAL_SSE_URL")
agentID = os.getenv("CORAL_AGENT_ID")

# Debug environment variables
logger.info(f"CORAL_SSE_URL: {base_url}")
logger.info(f"CORAL_AGENT_ID: {agentID}")

coral_params = {
    "agentId": agentID,
    "agentDescription": "ACI Dev agent capable of searching for relevant functions based on user intent and executing those functions with the required parameters."
}

query_string = urllib.parse.urlencode(coral_params)

async def get_mcp_tools(server):
    """Get tools from an MCP server and return formatted tool descriptions."""
    try:
        async with server:
            logger.info(f"Attempting to list tools from server: {server}")
            tools_result = await server.list_tools()
            logger.info(f"Tools result: {tools_result}")
            # Check if tools_result is a list; if so, use it directly
            tools = tools_result if isinstance(tools_result, list) else (tools_result.tools if hasattr(tools_result, 'tools') else [])
            logger.info(f"Retrieved tools: {tools}")
            
            # Format tools like get_tools_description
            def serialize_schema(tool):
                # Use parameters_json_schema for ToolDefinition objects
                if hasattr(tool, 'parameters_json_schema'):
                    return json.dumps(tool.parameters_json_schema).replace('{', '{{').replace('}', '}}')
                return "{}"
            
            formatted_tools = "\n".join(
                f"Tool: {tool.name}, Schema: {serialize_schema(tool)}"
                for tool in tools
            )
            return formatted_tools or "No tools available"
            
    except Exception as e:
        logger.error(f"Error retrieving tools from server {server}: {str(e)}")
        logger.error(traceback.format_exc())
        return "Error retrieving tools"


async def main():
    try:
        # Setup MCP servers
        CORAL_SERVER_URL = f"{base_url}?{query_string}"
        logger.info(f"Connecting to Coral Server: {CORAL_SERVER_URL}")
        
        # Initialize Coral MCP server (SSE)
        coral_server = MCPServerSSE(
            url=CORAL_SERVER_URL,
            sse_read_timeout=600,
            timeout=600,
        )
        
        # Initialize ACI MCP server (stdio)
        aci_server = MCPServerStdio(
            command='uvx',
            args=[
                'aci-mcp', 
                'unified-server', 
                '--linked-account-owner-id', os.getenv("ACI_OWNER_ID"), 
                '--port', '8000', 
                '--allowed-apps-only'
            ],
            env={"ACI_API_KEY": os.getenv("ACI_API_KEY")},
            timeout=600,
        )
        
        # Get tools from MCP servers before creating agent
        logger.info("Getting tools from MCP servers...")
        coral_tools = await get_mcp_tools(coral_server)
        aci_tools = await get_mcp_tools(aci_server)
        
        # Print tools for debugging
        print(coral_tools)
        print("=== ACI TOOLS ===")
        print(aci_tools)
        
        # Create system prompt with tool descriptions
        system_prompt = """You are an agent interacting with the tools from Coral Server and having your own tools. Your task is to perform any instructions coming from any agent. 
                            Follow these steps in order:
                            1. Call wait_for_mentions from coral tools (timeoutMs: 30000) to receive mentions from other agents.
                            2. When you receive a mention, keep the thread ID and the sender ID.
                            3. Think about the content (instruction) of the message and check only from the list of your tools available for you to action.
                            4. Check the tool schema and make a plan in steps for the task you want to perform.
                            5. Only call the tools you need to perform for each step of the plan to complete the instruction in the content.
                            6. Think about the content and see if you have executed the instruction to the best of your ability and the tools. Make this your response as "answer".
                            7. Use `send_message` from coral tools to send a message in the same thread ID to the sender Id you received the mention from, with content: "answer".
                            8. If any error occurs, use `send_message` to send a message in the same thread ID to the sender Id you received the mention from, with content: "error".
                            9. Always respond back to the sender agent even if you have no answer or error.
                            10. Repeat the process from step 1.
                            These are the list of coral tools: {coral_tools_description}
                            These are the list of your tools: {agent_tools_description}
                            """
        
        # Initialize agent with complete system prompt including tool descriptions
        agent = Agent(
            model=f"{os.getenv('MODEL_PROVIDER', 'openai')}:{os.getenv('MODEL_NAME', 'gpt-4o-mini')}",
            system_prompt=system_prompt,
            mcp_servers=[coral_server, aci_server]
        )

        logger.info("Multi Server Connection Established")
        
        # Initialize message history
        message_history = []

        # Run the agent with MCP servers
        async with agent.run_mcp_servers():
            logger.info("=== CONNECTION ESTABLISHED ===")
            
            while True:
                try:
                    logger.info("Starting new agent invocation")
                    
                    # Run the agent to wait for mentions and process them
                    result = await agent.run(
                        "Call wait for mentions to wait for instructions from other agents",
                        message_history=message_history
                    )
                    
                    logger.info(f"Agent result: {result.output}")
                    
                    # Update message history with new messages
                    message_history.extend(result.new_messages())
                    
                    # Log the current message history size
                    logger.debug(f"Current message history size: {len(message_history)}")
                    
                    logger.info("Completed agent invocation, restarting loop")
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error in agent loop: {str(e)}")
                    logger.error(traceback.format_exc())
                    await asyncio.sleep(5)

    except Exception as e:
        logger.error(f"Error in main setup: {str(e)}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    asyncio.run(main())