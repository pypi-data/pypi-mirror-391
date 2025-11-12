# Agentspace / Gemini Enterprise Agent Registration CLI

A command-line interface for managing agents in Google Cloud Gemini Enterprise (formerly known as Agentspace). This CLI tool allows you to easily register, view, list, update, and delete agents from your terminal, supporting both ADK agents running on Agent Engine and any A2A agents running anywhere else (e.g. Cloud Run).

## Overview

This script provides a convenient wrapper around the Google Discovery Engine API, simplifying the registration and management of agents within a Gemini Enterprise application. It was created because there is currently no `gcloud` CLI support for registering and managing agents in Gemini Enterprise. The tool handles authentication, request formatting, and provides clear feedback for all operations.

## What's New in Version 1.0.0

🎉 **Major Update**: A2A Protocol Support
- Register and manage A2A (Agent-to-Agent) protocol agents
- Support for agents running anywhere: Cloud Run, external services, or ADK agents with A2A enabled
- Flexible input options: JSON file or individual fields

🏷️ **Rebranding**: Agentspace is now **Gemini Enterprise**

## Agent Types

This tool supports two types of agents:

### 1. Agent Engine (AgentEngine)
ADK agents deployed on Google's Reasoning Engine (aka. Agent Engine). This is the traditional deployment method.

**Use when:**
- Your agent is built with ADK and deployed on Agent Engine

### 2. A2A Protocol (a2a)
Agents supporting the Agent-to-Agent (A2A) protocol.

**Use when:**
- Your agent runs on Cloud Run, Cloud Functions, or anywhere with an external endpoint
- Your agent is built with any agentic framework that supports A2A

## Prerequisites

*   Python 3.9+
*   Google Cloud SDK installed and authenticated. Run `gcloud auth login` and `gcloud auth application-default login` to set up your credentials.

## Installation

There are two recommended ways to use this tool:

### 1. Via Pip (Recommended)

For easy, system-wide access, you can install this tool from PyPI:

```bash
pip install agentspace-registration-cli
```

*(Note: The package name on PyPI is `agentspace-registration-cli`, but the command to run it is `agentspace-reg`)*

### 2. Direct Download

Alternatively, you can download the script and run it directly:

```bash
curl -O https://raw.githubusercontent.com/0nri/agentspace-registration-cli/main/agentspace_registration_cli.py
chmod +x agentspace_registration_cli.py
```

## Usage

After installation via pip, the tool is available as `agentspace-reg`.

If you downloaded the script directly, you will invoke it with `python agentspace_registration_cli.py`. All examples below use the `agentspace-reg` command.

---

## Agent Engine (AgentEngine) Examples

These examples show how to manage ADK agents deployed on Reasoning Engine.

### Register an Agent Engine Agent

```bash
agentspace-reg register \
  --source_type agentengine \
  --project_id "my-ai-project-12345" \
  --app_id "customer-support-app" \
  --display_name "TechSupportBot" \
  --description "Provides technical support and troubleshooting assistance." \
  --tool_description "An AI agent that helps users with technical issues and product questions." \
  --adk_deployment_id "7845692103458921067" \
  --icon_uri "https://example.com/icon.png"
```

### Update an Agent Engine Agent

```bash
agentspace-reg update \
  --source_type agentengine \
  --project_id "my-project-id" \
  --app_id "my-app-id" \
  --agent_id "existing-agent-id" \
  --display_name "Updated Support Bot" \
  --description "Updated description" \
  --tool_description "Updated tool description" \
  --adk_deployment_id "7845692103458921067"
```

---

## A2A Protocol Agent Examples

These examples show how to manage A2A protocol agents (Cloud Run, external services, or ADK with A2A enabled).

### Register an A2A Agent (Using Agent Card URL)

The tool can automatically fetch agent cards from URLs (following the A2A standard of hosting at `.well-known/agent-card.json`):

```bash
agentspace-reg register \
  --source_type a2a \
  --project_id "my-ai-project-12345" \
  --app_id "my-app" \
  --display_name "Cloud Run Agent" \
  --description "Agent hosted on Cloud Run" \
  --agent_card_json "https://my-agent.run.app/.well-known/agent-card.json"
```

### Register an A2A Agent (Using JSON File)

Alternatively, create a local agent card JSON file (`my-agent-card.json`):

```json
{
  "protocolVersion": "v1.0",
  "name": "Cloud Run Data Agent",
  "description": "Analyzes data from BigQuery",
  "url": "https://my-agent-xyz.run.app",
  "iconUrl": "https://example.com/icon.png",
  "version": "1.0.0",
  "capabilities": {
    "streaming": true
  },
  "skills": [
    {
      "id": "data-analysis",
      "name": "Data Analysis",
      "description": "Analyze data and provide insights",
      "tags": ["analytics", "bigquery"],
      "examples": ["Analyze sales data", "Show revenue trends"]
    }
  ],
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain", "application/json"]
}
```

Then register the agent:

```bash
agentspace-reg register \
  --source_type a2a \
  --project_id "my-ai-project-12345" \
  --app_id "my-app" \
  --display_name "Cloud Run Data Agent" \
  --description "Analyzes data from BigQuery" \
  --agent_card_json "./my-agent-card.json"
```

### Register an A2A Agent (Using Individual Fields)

```bash
agentspace-reg register \
  --source_type a2a \
  --project_id "my-ai-project-12345" \
  --app_id "my-app" \
  --display_name "Simple Chat Agent" \
  --description "A simple chatbot agent" \
  --agent_name "Simple Chat Agent" \
  --agent_url "https://my-chatbot.run.app" \
  --agent_version "1.0.0" \
  --protocol_version "v1.0" \
  --skills_json '[{"id":"chat","name":"Chat","description":"Chat with users","tags":["conversation"],"examples":["Hello","How are you?"]}]' \
  --default_input_modes "text/plain" \
  --default_output_modes "text/plain"
```

### Register an A2A Agent with Authorization

For agents that need to access Google Cloud resources on behalf of users:

```bash
agentspace-reg register \
  --source_type a2a \
  --project_id "my-project" \
  --app_id "my-app" \
  --display_name "BigQuery Agent" \
  --description "Queries BigQuery on behalf of users" \
  --agent_card_json "./bigquery-agent-card.json" \
  --auth_ids "my-oauth-config"
```

### Update an A2A Agent

```bash
agentspace-reg update \
  --source_type a2a \
  --project_id "my-project-id" \
  --app_id "my-app-id" \
  --agent_id "existing-agent-id" \
  --display_name "Updated Cloud Run Agent" \
  --description "Updated description" \
  --agent_card_json "./updated-agent-card.json"
```

---

## Common Operations

These operations work for both agent types.

### View an Agent

```bash
agentspace-reg view \
  --project_id "your-gcp-project-id" \
  --app_id "your-app-id" \
  --agent_id "the-id-of-the-agent-to-view"
```

### List All Agents

```bash
agentspace-reg list \
  --project_id "your-gcp-project-id" \
  --app_id "your-app-id"
```

### Delete an Agent

**This action cannot be undone.**

```bash
agentspace-reg delete \
  --project_id "your-gcp-project-id" \
  --app_id "your-app-id" \
  --agent_id "the-id-of-the-agent-to-delete"
```

---

## Command-Line Flags Reference

### Common Flags (All Agent Types)

| Flag                | Description                                                                 | Required For                  |
| ------------------- | --------------------------------------------------------------------------- | ----------------------------- |
| `--project_id`      | The ID of your Google Cloud project.                                        | All actions                   |
| `--app_id`          | The ID of the Gemini Enterprise app.                                        | All actions                   |
| `--display_name`    | The display name of the agent.                                              | `register`, `update`          |
| `--description`     | The user-facing description of the agent.                                   | `register`, `update`          |
| `--agent_id`        | The ID of the agent to view, update, or delete.                             | `view`, `update`, `delete`    |
| `--source_type`     | Agent source type: `agentengine` or `a2a` (default: `agentengine`)          | `register`, `update`          |

### Agent Engine Specific Flags

| Flag                | Description                                                                 | Required For                  |
| ------------------- | --------------------------------------------------------------------------- | ----------------------------- |
| `--tool_description`| The LLM-facing prompt that describes the agent's capabilities.              | `register`, `update` (agentengine) |
| `--adk_deployment_id`| The ID of the reasoning engine where the ADK agent is deployed.             | `register`, `update` (agentengine) |
| `--icon_uri`        | A public URI for the agent's icon.                                          | Optional (agentengine only)   |
| `--auth_ids`        | Comma-separated list of authorization resource IDs (supports multiple).     | Optional (agentengine)        |

### A2A Protocol Specific Flags

| Flag                | Description                                                                 | Required For                  |
| ------------------- | --------------------------------------------------------------------------- | ----------------------------- |
| `--agent_card_json` | Path to JSON file or JSON string with complete agent card.                  | `register`, `update` (a2a) OR use individual fields |
| `--agent_name`      | The name of the A2A agent (in agent card).                                  | `register`, `update` (a2a, if no card JSON) |
| `--agent_url`       | The endpoint URL of the A2A agent.                                          | `register`, `update` (a2a, if no card JSON) |
| `--agent_version`   | The version of the agent (e.g., "1.0.0").                                   | `register`, `update` (a2a, if no card JSON) |
| `--skills_json`     | JSON string or file path with skills array.                                 | `register`, `update` (a2a, if no card JSON) |
| `--protocol_version`| A2A protocol version (default: "v1.0").                                     | Optional (a2a)                |
| `--capabilities_json`| JSON string or file path with capabilities object.                         | Optional (a2a)                |
| `--default_input_modes` | Comma-separated input modes (default: "text/plain").                    | Optional (a2a)                |
| `--default_output_modes` | Comma-separated output modes (default: "text/plain").                  | Optional (a2a)                |
| `--auth_ids`        | Authorization resource ID (only first one used for A2A).                    | Optional (a2a)                |

### Location Flags

| Flag                | Description                                                                 | Default    |
| ------------------- | --------------------------------------------------------------------------- | ---------- |
| `--discovery_location` | Location where your Gemini Enterprise app is created.                    | `global`   |
| `--reasoning_location` | Location where your reasoning engine is deployed (agentengine only).     | `global`   |
| `--auth_location`   | Location where your authorization resources are created.                    | `global`   |

---

## Multi-Region Support

This tool supports multi-region deployments where your Discovery Engine (i.e. Gemini Enterprise), Reasoning Engine (i.e. Agent Engine), and Authorization resources can be deployed in different Google Cloud regions.

### Finding Your Resource Locations

You can find the correct location values in the Google Cloud Console:

- **`--discovery_location`**: Check the "Location" column in the AI Applications page
- **`--reasoning_location`**: Find this in the "Agent Engine Details" page  
- **`--auth_location`**: Check where your authorization resources are created
- **`--adk_deployment_id`**: Located in the "Agent Engine Details" page (format: "1234567890123456789")
- **`--app_id`**: Found in the "ID" column of the AI Applications page

### Multi-Region Example

```bash
agentspace-reg register \
  --source_type agentengine \
  --project_id "my-ai-project-12345" \
  --app_id "customer-support-app" \
  --display_name "DataAnalysisBot" \
  --description "Analyzes customer data and provides insights." \
  --tool_description "An AI agent specialized in data analysis and reporting." \
  --adk_deployment_id "3721958460127834952" \
  --discovery_location "us" \
  --reasoning_location "us-central1" \
  --auth_location "us-east1"
```

---

## A2A Agent Card Schema

For A2A agents, the agent card must include these fields:

### Required Fields
- `protocolVersion`: A2A protocol version (e.g., "v1.0")
- `name`: Agent name
- `description`: Agent description
- `url`: Agent endpoint URL
- `version`: Agent version
- `skills`: Array of skill objects
- `defaultInputModes`: Array of input MIME types
- `defaultOutputModes`: Array of output MIME types

### Optional Fields
- `iconUrl`: URL or data URI for agent icon
- `capabilities`: Object with capability flags (e.g., `{"streaming": true}`)

### Skills Object
Each skill must include:
- `id`: Unique skill identifier
- `name`: Skill name
- `description`: Skill description
- `tags`: Array of tags (optional)
- `examples`: Array of example queries (optional)

For the complete A2A protocol specification, see the [Agent2Agent (A2A) Protocol Official Specification](https://github.com/google/generative-ai-docs/blob/main/site/en/gemini-api/docs/a2a/a2a-spec.md).

---

## Authorization for Agents

Both agent types can use OAuth 2.0 authorization to access Google Cloud resources on behalf of users.

### Creating Authorization Resources

First, create OAuth 2.0 credentials and register them as an authorization resource:

```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: PROJECT_ID" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/PROJECT_ID/locations/global/authorizations?authorizationId=my-oauth-config" \
  -d '{
    "serverSideOauth2": {
      "clientId": "YOUR_OAUTH_CLIENT_ID",
      "clientSecret": "YOUR_OAUTH_CLIENT_SECRET",
      "authorizationUri": "YOUR_AUTH_URI",
      "tokenUri": "YOUR_TOKEN_URI"
    }
  }'
```

Then reference it when registering your agent with `--auth_ids "my-oauth-config"`.

### Differences Between Agent Types

- **Agent Engine**: Supports multiple authorization resources via comma-separated list
- **A2A**: Supports only one authorization resource (first one used if multiple provided)

---

## Troubleshooting

### Common Issues

**Issue**: `Error: Missing required flags`
- **Solution**: Ensure you've provided all required flags for your agent type. Use `--source_type agentengine` or `--source_type a2a` and check the required flags table above.

**Issue**: `Error parsing JSON input`
- **Solution**: Validate your JSON syntax. For `--skills_json` and `--capabilities_json`, ensure the JSON is properly formatted and quoted in your shell.

**Issue**: `HTTP 404: Agent not found`
- **Solution**: Verify the `--agent_id` is correct. Use the `list` command to see all available agents.

**Issue**: `HTTP 403: Permission denied`
- **Solution**: Ensure your Google Cloud credentials have the Discovery Engine Admin role.

**Issue**: A2A agent icon not displaying
- **Solution**: Make sure the `iconUrl` in your agent card is either a publicly accessible URL or a valid data URI.

---

## More Information

- [Gemini Enterprise Documentation](https://cloud.google.com/generative-ai-app-builder/docs)
- [A2A Protocol Specification](https://github.com/google/generative-ai-docs/blob/main/site/en/gemini-api/docs/a2a/a2a-spec.md)
- [Google Cloud AI Applications](https://cloud.google.com/generative-ai-app-builder/docs/locations)
- [ADK (Agent Development Kit) Documentation](https://google.github.io/adk-docs/)

