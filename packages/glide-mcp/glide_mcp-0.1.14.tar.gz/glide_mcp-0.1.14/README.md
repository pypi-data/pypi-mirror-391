
#  Glide MCP

> Note: **we're currently recording a demo video and features for this mcp. Stay tuned and thank you for your patience :)**



### Configure MCP Client of your chosse to use Glide

1. **Add to Cursor (Preferred):**

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en-US/install-mcp?name=glide-mcp&config=eyJlbnYiOnsiVk9ZQUdFQUlfQVBJX0tFWSI6InBhLXQ5MGptcVlmZ1pQYzBXMDBfMW1MMmEwZjBCbjRrOG9sX25kRVkydEl2OEMiLCJIRUxJWF9BUElfRU5EUE9JTlQiOiJodHRwczovL2hlbGl4LWdsaWRlLXByb2R1Y3Rpb24uZmx5LmRldiIsIkNFUkVCUkFTX0FQSV9LRVkiOiJjc2std3ZrM2p3bmo1NXgzdzhtZXByZXRya2Y4azMydHhucGQ4dnJueTRldG1rdGtkY2U4IiwiQ0VSRUJSQVNfTU9ERUxfSUQiOiJxd2VuLTMtMzJiIiwiTU9SUEhMTE1fQVBJX0tFWSI6InNrLU1TemIzYVlyWDBjb1F1WWFQT1haMmpJOFFzY3JRYnR0UVdvTUY2Y3MtdmJtSkdHSSIsIkhFTElYX0xPQ0FMIjoiRmFsc2UifSwiY29tbWFuZCI6InV2eCAtLWZyb20gZ2xpZGUtbWNwIGdsaWRlICJ9)


2. **Add to Claude Code:**
make sure to fill in the api keys correctly, no quotes needed
```zsh
claude mcp add --transport stdio glide-mcp --env VOYAGEAI_API_KEY= --env HELIX_API_ENDPOINT= --env CEREBRAS_API_KEY= --env CEREBRAS_MODEL_ID=qwen-3-32b --env HELIX_LOCAL= --env MORPHLLM_API_KEY= -- uvx --from glide-mcp glide
```


3. **Add to VSCode**: 

[![Install MCP Server](https://img.shields.io/badge/add_to_VSCode-blue)](vscode:mcp/install?{\"name\":\"glide-mcp\",\"command\":\"uvx\",\"args\":[\"--from\",\"glide-mcp\",\"glide\"],\"env\":{\"VOYAGEAI_API_KEY\":\"\",\"HELIX_API_ENDPOINT\":\"\",\"CEREBRAS_API_KEY\":\"\",\"CEREBRAS_MODEL_ID\":\"qwen-3-32b\",\"HELIX_LOCAL\":\"\"}})


You can add the API keys needed by opening the command palette (Cmd+Shift+P) and searching for `"MCP: List MCP Servers"`. Make sure to fill in the API keys correctly.


**Manual Installation:**

Add the following to your `mcp.json` configuration in your preferred editor / IDE:

```json
{
  "mcpServers": {
    "glide-mcp": {
      "command": "uvx",
      "args": ["--from", "glide-mcp", "glide"],
      "env": {
        "VOYAGEAI_API_KEY": "",
        "HELIX_API_ENDPOINT": "",
        "CEREBRAS_API_KEY": "",
        "CEREBRAS_MODEL_ID": "qwen-3-32b",
        "HELIX_LOCAL": "",
        "MORPHLLM_API_KEY": ""
      }
    }
  }
}
```



## Working with the source: 

### 1. You can also clone the source
```bash
git clone https://github.com/SoarAILabs/glide.git
```

### 2. Navigate to the project directory

```bash
cd glide
```

### 3. Start the server

```bash
uv run python -m src.mcp.app
```

