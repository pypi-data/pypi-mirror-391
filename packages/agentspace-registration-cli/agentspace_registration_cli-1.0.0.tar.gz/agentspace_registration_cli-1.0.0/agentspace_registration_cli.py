"""Agent registration management script for Gemini Enterprise"""

import asyncio
import json
import os
import subprocess

import httpx
from absl import app, flags

FLAGS = flags.FLAGS

# --- Command-line Flags ---
flags.DEFINE_string("project_id", None, "The ID of your Google Cloud project.")
flags.DEFINE_string(
    "app_id",
    None,
    "The ID of the Gemini Enterprise app. "
    "Retrieve this from the 'ID' column in AI Applications page.",
)
flags.DEFINE_string("display_name", None, "The display name of the agent.")
flags.DEFINE_string(
    "description", None, "The description of the agent, displayed on the frontend."
)
flags.DEFINE_string("agent_id", None, "The ID of the agent to view, update, or delete.")

# Source type flag
flags.DEFINE_enum(
    "source_type",
    "agentengine",
    ["agentengine", "a2a"],
    "The source type of the agent. Use 'agentengine' for ADK agents deployed on Agent Engine, "
    "or 'a2a' for agents using the A2A protocol (can be ADK agents with A2A enabled, Cloud Run, or any A2A-compliant service).",
)

# AgentEngine-specific flags
flags.DEFINE_string(
    "icon_uri",
    None,
    "The public URI of the icon to display near the name of the agent. "
    "Used for agentengine source type only.",
)
flags.DEFINE_string(
    "tool_description",
    None,
    "The description/prompt of the agent used by the LLM to route requests. "
    "Required for agentengine source type.",
)
flags.DEFINE_string(
    "adk_deployment_id",
    None,
    "The ID of the reasoning engine endpoint where the ADK agent is deployed. "
    "Retrieve this from the 'Agent Engine Details' page (format: '5093550707281667376'). "
    "Required for agentengine source type.",
)

# A2A-specific flags
flags.DEFINE_string(
    "agent_card_json",
    None,
    "Path to JSON file or JSON string containing the complete A2A agent card. "
    "Used for a2a source type. If provided, individual A2A fields are ignored.",
)
flags.DEFINE_string(
    "agent_name",
    None,
    "The name of the A2A agent (used in agent card). "
    "Required for a2a source type if agent_card_json is not provided.",
)
flags.DEFINE_string(
    "agent_url",
    None,
    "The endpoint URL of the A2A agent. "
    "Required for a2a source type if agent_card_json is not provided.",
)
flags.DEFINE_string(
    "agent_version",
    None,
    "The version of the A2A agent (e.g., '1.0.0'). "
    "Required for a2a source type if agent_card_json is not provided.",
)
flags.DEFINE_string(
    "protocol_version",
    "v1.0",
    "The A2A protocol version (default: 'v1.0'). Used for a2a source type.",
)
flags.DEFINE_string(
    "capabilities_json",
    None,
    "JSON string or path to file containing A2A capabilities object. "
    "Optional for a2a source type.",
)
flags.DEFINE_string(
    "skills_json",
    None,
    "JSON string or path to file containing A2A skills array. "
    "Required for a2a source type if agent_card_json is not provided.",
)
flags.DEFINE_string(
    "default_input_modes",
    "text/plain",
    "Comma-separated list of default input modes (default: 'text/plain'). "
    "Used for a2a source type.",
)
flags.DEFINE_string(
    "default_output_modes",
    "text/plain",
    "Comma-separated list of default output modes (default: 'text/plain'). "
    "Used for a2a source type.",
)

# Authorization flags
flags.DEFINE_list("auth_ids", [], "Optional: The IDs of the authorization resources.")

# Output format flag
flags.DEFINE_bool(
    "json",
    False,
    "Output raw JSON response instead of formatted output. Useful for debugging or scripting.",
)

# Location flags for different services
flags.DEFINE_string(
    "discovery_location",
    "global",
    "Location where your Gemini Enterprise app is created. "
    "Verify this from the 'Location' column in AI Applications page (e.g., 'us-central1', 'global').",
)
flags.DEFINE_string(
    "reasoning_location",
    "global",
    "Location where your reasoning engine is deployed. "
    "Check the 'Agent Engine Details' page for the correct location.",
)
flags.DEFINE_string(
    "auth_location",
    "global",
    "Location where your authorization resources are created.",
)


def get_access_token() -> str:
    """Gets the gcloud access token."""
    return subprocess.check_output(
        ["gcloud", "auth", "print-access-token"], text=True
    ).strip()


def get_discovery_engine_base_url() -> str:
    """Gets the correct Discovery Engine base URL based on location."""
    if FLAGS.discovery_location == "us":
        return "https://us-discoveryengine.googleapis.com/v1alpha"
    elif FLAGS.discovery_location == "eu":
        return "https://eu-discoveryengine.googleapis.com/v1alpha"
    else:
        # For global or any other location, use the standard endpoint
        return "https://discoveryengine.googleapis.com/v1alpha"


def load_json_input(json_input: str) -> dict:
    """Load JSON from URL, file path, or parse JSON string."""
    # Check if it's a URL
    if json_input.startswith(("http://", "https://")):
        try:
            response = httpx.get(json_input, timeout=30.0, follow_redirects=True)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise ValueError(f"Failed to fetch agent card from URL: {e}")
    # Check if it's a file
    elif os.path.isfile(json_input):
        with open(json_input, "r") as f:
            return json.load(f)
    # Otherwise, parse as JSON string
    else:
        return json.loads(json_input)


def build_a2a_agent_card() -> dict:
    """Build A2A agent card from individual flags."""
    if FLAGS.agent_card_json:
        return load_json_input(FLAGS.agent_card_json)

    # Validate required fields
    if not all(
        [FLAGS.agent_name, FLAGS.agent_url, FLAGS.agent_version, FLAGS.skills_json]
    ):
        raise ValueError(
            "For A2A agents, you must provide either --agent_card_json or all of: "
            "--agent_name, --agent_url, --agent_version, --skills_json"
        )

    # Build agent card from individual fields
    card = {
        "protocolVersion": FLAGS.protocol_version,
        "name": FLAGS.agent_name,
        "description": FLAGS.description,
        "url": FLAGS.agent_url,
        "version": FLAGS.agent_version,
        "capabilities": load_json_input(FLAGS.capabilities_json)
        if FLAGS.capabilities_json
        else {},
        "skills": load_json_input(FLAGS.skills_json),
        "defaultInputModes": [
            mode.strip() for mode in FLAGS.default_input_modes.split(",")
        ],
        "defaultOutputModes": [
            mode.strip() for mode in FLAGS.default_output_modes.split(",")
        ],
    }

    return card


def format_timestamp(timestamp_str: str) -> str:
    """Format ISO timestamp to a more readable format."""
    if not timestamp_str:
        return "N/A"
    try:
        # Just return the date and time part, removing microseconds
        return timestamp_str.replace("T", " ").split(".")[0] + " UTC"
    except Exception:
        return timestamp_str


def get_agent_type(agent_data: dict) -> str:
    """Determine the agent type from response data."""
    if "a2aAgentDefinition" in agent_data:
        return "A2A"
    elif "adkAgentDefinition" in agent_data:
        return "AgentEngine"
    return "Unknown"


def format_agent_summary(response_data: dict) -> str:
    """Format agent data for register/update operations."""
    agent_name = response_data.get("name", "")
    agent_id = agent_name.split("/")[-1] if agent_name else "N/A"
    display_name = response_data.get("displayName", "N/A")
    status = response_data.get("state", "N/A")
    agent_type = get_agent_type(response_data)
    created = format_timestamp(response_data.get("createTime", ""))

    output = []
    output.append(f"Agent ID: {agent_id}")
    output.append(f"Display Name: {display_name}")
    output.append(f"Status: {status}")
    output.append(f"Type: {agent_type}")
    output.append(f"Created: {created}")

    return "\n".join(output)


def format_agent_details(response_data: dict) -> str:
    """Format detailed agent information for view operation."""
    agent_name = response_data.get("name", "")
    agent_id = agent_name.split("/")[-1] if agent_name else "N/A"
    display_name = response_data.get("displayName", "N/A")
    description = response_data.get("description", "N/A")
    status = response_data.get("state", "N/A")
    agent_type = get_agent_type(response_data)
    created = format_timestamp(response_data.get("createTime", ""))
    updated = format_timestamp(response_data.get("updateTime", ""))

    output = []
    output.append("=" * 60)
    output.append("AGENT DETAILS")
    output.append("=" * 60)
    output.append(f"Agent ID: {agent_id}")
    output.append(f"Display Name: {display_name}")
    output.append(f"Description: {description}")
    output.append(f"Type: {agent_type}")
    output.append(f"Status: {status}")
    output.append(f"Created: {created}")
    output.append(f"Updated: {updated}")
    output.append("")

    # Add type-specific details
    if agent_type == "A2A":
        a2a_def = response_data.get("a2aAgentDefinition", {})
        card_json = a2a_def.get("jsonAgentCard", "{}")
        try:
            card = json.loads(card_json)
            output.append("A2A Agent Details:")
            output.append(f"  Agent URL: {card.get('url', 'N/A')}")
            output.append(f"  Protocol Version: {card.get('protocolVersion', 'N/A')}")
            output.append(f"  Version: {card.get('version', 'N/A')}")
            skills = card.get("skills", [])
            output.append(f"  Skills: {len(skills)} skill(s) available")
            if skills:
                output.append("  Skill List:")
                for skill in skills[:5]:  # Show first 5 skills
                    skill_name = skill.get("name", "Unknown")
                    skill_desc = skill.get("description", "")
                    # Truncate description
                    if len(skill_desc) > 60:
                        skill_desc = skill_desc[:57] + "..."
                    output.append(f"    - {skill_name}: {skill_desc}")
                if len(skills) > 5:
                    output.append(f"    ... and {len(skills) - 5} more")
        except json.JSONDecodeError:
            output.append("A2A Agent Details: (Unable to parse agent card)")

    elif agent_type == "AgentEngine":
        adk_def = response_data.get("adkAgentDefinition", {})
        tool_settings = adk_def.get("toolSettings", {})
        reasoning_engine = adk_def.get("provisionedReasoningEngine", {})

        output.append("Agent Engine Details:")
        tool_desc = tool_settings.get("toolDescription", "N/A")
        if len(tool_desc) > 100:
            tool_desc = tool_desc[:97] + "..."
        output.append(f"  Tool Description: {tool_desc}")

        re_path = reasoning_engine.get("reasoningEngine", "N/A")
        if re_path != "N/A":
            re_id = re_path.split("/")[-1]
            output.append(f"  Reasoning Engine ID: {re_id}")

    output.append("")
    output.append("=" * 60)
    output.append("Use --json flag to see the complete raw response")
    output.append("=" * 60)

    return "\n".join(output)


def format_agents_table(response_data: dict) -> str:
    """Format agents list as a table."""
    agents = response_data.get("agents", [])

    if not agents:
        return "No agents found in this app."

    output = []
    output.append("")
    output.append(f"Found {len(agents)} agent(s) in this app:")
    output.append("")

    # Table header
    header = f"{'Agent ID':<22} | {'Display Name':<30} | {'Type':<12} | {'Status':<8} | {'Created':<20}"
    output.append(header)
    output.append("-" * len(header))

    # Table rows
    for agent in agents:
        agent_name = agent.get("name", "")
        agent_id = agent_name.split("/")[-1] if agent_name else "N/A"
        # Truncate if too long
        if len(agent_id) > 20:
            agent_id = agent_id[:17] + "..."

        display_name = agent.get("displayName", "N/A")
        if len(display_name) > 28:
            display_name = display_name[:25] + "..."

        agent_type = get_agent_type(agent)
        status = agent.get("state", "N/A")
        created = format_timestamp(agent.get("createTime", ""))

        row = f"{agent_id:<22} | {display_name:<30} | {agent_type:<12} | {status:<8} | {created:<20}"
        output.append(row)

    output.append("")
    output.append("Use --json flag to see the complete raw response")
    output.append("")

    return "\n".join(output)


async def register_agent():
    """Registers an agent in Gemini Enterprise."""
    # Validate common required fields
    if not all([FLAGS.project_id, FLAGS.app_id, FLAGS.display_name, FLAGS.description]):
        print("Error: Missing one or more required flags for registration.")
        print("Required: --project_id, --app_id, --display_name, --description")
        return

    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": FLAGS.project_id,
    }

    base_url = get_discovery_engine_base_url()
    url = f"{base_url}/projects/{FLAGS.project_id}/locations/{FLAGS.discovery_location}/collections/default_collection/engines/{FLAGS.app_id}/assistants/default_assistant/agents"

    # Build request data based on source type
    if FLAGS.source_type == "agentengine":
        # Validate AgentEngine-specific required fields
        if not all([FLAGS.tool_description, FLAGS.adk_deployment_id]):
            print("Error: Missing required flags for agentengine source type.")
            print("Required: --tool_description, --adk_deployment_id")
            return

        data = {
            "displayName": FLAGS.display_name,
            "description": FLAGS.description,
            "adk_agent_definition": {
                "tool_settings": {
                    "tool_description": FLAGS.tool_description,
                },
                "provisioned_reasoning_engine": {
                    "reasoning_engine": f"projects/{FLAGS.project_id}/locations/{FLAGS.reasoning_location}/reasoningEngines/{FLAGS.adk_deployment_id}",
                },
            },
        }

        if FLAGS.icon_uri:
            data["icon"] = {"uri": FLAGS.icon_uri}

        if FLAGS.auth_ids:
            data["adk_agent_definition"]["authorizations"] = [
                f"projects/{FLAGS.project_id}/locations/{FLAGS.auth_location}/authorizations/{auth_id}"
                for auth_id in FLAGS.auth_ids
            ]

    elif FLAGS.source_type == "a2a":
        try:
            agent_card = build_a2a_agent_card()
        except ValueError as e:
            print(f"Error: {e}")
            return
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error parsing JSON input: {e}")
            return

        data = {
            "displayName": FLAGS.display_name,
            "description": FLAGS.description,
            "a2aAgentDefinition": {"jsonAgentCard": json.dumps(agent_card)},
        }

        # Add authorization if provided
        if FLAGS.auth_ids:
            auth_id = FLAGS.auth_ids[0]
            data["authorizationConfig"] = {
                "agentAuthorization": f"projects/{FLAGS.project_id}/locations/{FLAGS.auth_location}/authorizations/{auth_id}"
            }
            if len(FLAGS.auth_ids) > 1:
                print(
                    "Warning: A2A agents support only one authorization resource. Using the first one."
                )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data, timeout=30.0)
            response.raise_for_status()
            response_data = response.json()

            print("✓ Agent registered successfully!")
            print("")
            if FLAGS.json:
                print(json.dumps(response_data, indent=2))
            else:
                print(format_agent_summary(response_data))
                print("")
                print("Use --json flag to see the complete raw response")
        except httpx.HTTPStatusError as e:
            print(f"Error registering agent: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


async def view_agent():
    """Views a specific agent in Gemini Enterprise."""
    if not all([FLAGS.project_id, FLAGS.app_id, FLAGS.agent_id]):
        print("Error: Missing one or more required flags for viewing.")
        print("Required: --project_id, --app_id, --agent_id")
        return

    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": FLAGS.project_id,
    }

    base_url = get_discovery_engine_base_url()
    url = f"{base_url}/projects/{FLAGS.project_id}/locations/{FLAGS.discovery_location}/collections/default_collection/engines/{FLAGS.app_id}/assistants/default_assistant/agents/{FLAGS.agent_id}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            response_data = response.json()

            if FLAGS.json:
                print(json.dumps(response_data, indent=2))
            else:
                print(format_agent_details(response_data))
        except httpx.HTTPStatusError as e:
            print(f"Error retrieving agent: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


async def list_agents():
    """Lists all agents in a Gemini Enterprise app."""
    if not all([FLAGS.project_id, FLAGS.app_id]):
        print("Error: Missing one or more required flags for listing.")
        print("Required: --project_id, --app_id")
        return

    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": FLAGS.project_id,
    }

    base_url = get_discovery_engine_base_url()
    url = f"{base_url}/projects/{FLAGS.project_id}/locations/{FLAGS.discovery_location}/collections/default_collection/engines/{FLAGS.app_id}/assistants/default_assistant/agents"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            response_data = response.json()

            if FLAGS.json:
                print(json.dumps(response_data, indent=2))
            else:
                print(format_agents_table(response_data))
        except httpx.HTTPStatusError as e:
            print(f"Error retrieving agents: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


async def update_agent():
    """Updates an existing agent in Gemini Enterprise."""
    # Validate common required fields
    if not all(
        [
            FLAGS.project_id,
            FLAGS.app_id,
            FLAGS.agent_id,
            FLAGS.display_name,
            FLAGS.description,
        ]
    ):
        print("Error: Missing one or more required flags for updating.")
        print(
            "Required: --project_id, --app_id, --agent_id, --display_name, --description"
        )
        return

    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": FLAGS.project_id,
    }

    base_url = get_discovery_engine_base_url()
    url = f"{base_url}/projects/{FLAGS.project_id}/locations/{FLAGS.discovery_location}/collections/default_collection/engines/{FLAGS.app_id}/assistants/default_assistant/agents/{FLAGS.agent_id}"

    # Build request data based on source type
    if FLAGS.source_type == "agentengine":
        # Validate AgentEngine-specific required fields
        if not all([FLAGS.tool_description, FLAGS.adk_deployment_id]):
            print("Error: Missing required flags for agentengine source type.")
            print("Required: --tool_description, --adk_deployment_id")
            return

        data = {
            "displayName": FLAGS.display_name,
            "description": FLAGS.description,
            "adk_agent_definition": {
                "tool_settings": {
                    "tool_description": FLAGS.tool_description,
                },
                "provisioned_reasoning_engine": {
                    "reasoning_engine": f"projects/{FLAGS.project_id}/locations/{FLAGS.reasoning_location}/reasoningEngines/{FLAGS.adk_deployment_id}",
                },
            },
        }

        if FLAGS.icon_uri:
            data["icon"] = {"uri": FLAGS.icon_uri}

        if FLAGS.auth_ids:
            data["adk_agent_definition"]["authorizations"] = [
                f"projects/{FLAGS.project_id}/locations/{FLAGS.auth_location}/authorizations/{auth_id}"
                for auth_id in FLAGS.auth_ids
            ]

    elif FLAGS.source_type == "a2a":
        try:
            agent_card = build_a2a_agent_card()
        except ValueError as e:
            print(f"Error: {e}")
            return
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error parsing JSON input: {e}")
            return

        data = {
            "displayName": FLAGS.display_name,
            "description": FLAGS.description,
            "a2aAgentDefinition": {"jsonAgentCard": json.dumps(agent_card)},
        }

        # Add authorization if provided
        if FLAGS.auth_ids:
            auth_id = FLAGS.auth_ids[0]
            data["authorizationConfig"] = {
                "agentAuthorization": f"projects/{FLAGS.project_id}/locations/{FLAGS.auth_location}/authorizations/{auth_id}"
            }
            if len(FLAGS.auth_ids) > 1:
                print(
                    "Warning: A2A agents support only one authorization resource. Using the first one."
                )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(url, headers=headers, json=data, timeout=30.0)
            response.raise_for_status()
            response_data = response.json()

            print("✓ Agent updated successfully!")
            print("")
            if FLAGS.json:
                print(json.dumps(response_data, indent=2))
            else:
                print(format_agent_summary(response_data))
                print("")
                print("Use --json flag to see the complete raw response")
        except httpx.HTTPStatusError as e:
            print(f"Error updating agent: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


async def delete_agent():
    """Deletes a specific agent from Gemini Enterprise."""
    if not all([FLAGS.project_id, FLAGS.app_id, FLAGS.agent_id]):
        print("Error: Missing one or more required flags for deletion.")
        print("Required: --project_id, --app_id, --agent_id")
        return

    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": FLAGS.project_id,
    }

    base_url = get_discovery_engine_base_url()
    url = f"{base_url}/projects/{FLAGS.project_id}/locations/{FLAGS.discovery_location}/collections/default_collection/engines/{FLAGS.app_id}/assistants/default_assistant/agents/{FLAGS.agent_id}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            print(f"Agent with ID '{FLAGS.agent_id}' deleted successfully.")
        except httpx.HTTPStatusError as e:
            print(f"Error deleting agent: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


def main_cli() -> None:
    """Main entry point for the CLI script."""

    # absl.app.run() expects to be called with a main function,
    # so we wrap our logic in a little helper.
    def run_action(argv):
        if len(argv) < 2:
            print(
                "Error: No action specified. Please specify 'register', 'view', 'list', 'update', or 'delete'."
            )
            return

        action = argv[1]

        if action == "register":
            asyncio.run(register_agent())
        elif action == "view":
            asyncio.run(view_agent())
        elif action == "list":
            asyncio.run(list_agents())
        elif action == "update":
            asyncio.run(update_agent())
        elif action == "delete":
            asyncio.run(delete_agent())
        else:
            print(f"Unknown action: {action}")

    app.run(run_action)


if __name__ == "__main__":
    main_cli()
