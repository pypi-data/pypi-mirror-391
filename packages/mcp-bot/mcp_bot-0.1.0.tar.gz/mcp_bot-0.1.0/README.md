# 🤖 MCP Bot

An interactive chat UI for interacting with your MCP Tools using Language models.
MCP Bot makes it simple to connect to an MCP endpoint, configure your model, and start chatting with intelligent agent tools — all from a friendly, browser-based interface.

## ✨ Features

* **Model Integration:** Seamlessly connect model of your choice to power your agent responses (currently supports Gemini models).
* **Connect to any MCP Server:** Easily connect to any MCP server by simply entering its URL.
* **Custom Headers Support:** You can add custom request headers (like API tokens, authorization keys, or metadata) when connecting to an MCP server.
This makes it easy to test protected or authenticated MCP tools directly from the interface.
* **System Message Support:** Dynamically update the system prompt to guide your agent’s behavior.
* **Chat with MCP Agents:** Interactively communicate with tools served through MCP using a conversational interface.

---

### 🚀 Installation

You can install `mcp-bot` directly from PyPI.

```bash
pip install mcp-bot
```

---

### 💻 How to Run

After installation, you can launch the application from your terminal with a single command:

```bash
mcp-bot
```
This will automatically start a local server and open the app in your default web browser.

---

### 🛠️ Usage

1.  **Enter Model Name & Key:** On the left sidebar, enter the model name you want to use in this agent (currently supports Gemini models) and model api key.
2.  **Enter Server URL:** Enter the URL of the MCP server you want to connect with the agent.
3.  **Optional Headers:** Expand **"🔐 MCP Tools Header (optional)"** below the URL input if your MCP tools requires custom headers and header-based access is already configured in your MCP server.
    - Enter the header name (e.g., Authorization)
    - Enter the header value (e.g., Bearer your_api_token)
4.  **Prepare Agent:** Click **"🚀 Prepare Agent"** button.
4.  **System Message:** Use the sidebar to add a custom System Message to shape your agent’s behavior.
5.  **New Chat:** Start a fresh session anytime with the **"🆕 New Chat"** button.

---

### 📄 Requirements

* Python 3.11+

---

## 🔗 Project Links

- 📂 [Source Code](https://github.com/NilavoBoral/mcp-bot)
