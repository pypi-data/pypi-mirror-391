import os
import asyncio
import json
import streamlit as st
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

import nest_asyncio
nest_asyncio.apply()

# UI layout
st.set_page_config(page_title="MCP-Bot", page_icon="🤖", layout="wide")

st.sidebar.title("🤖 MCP-Bot")

# --- Main content ---
st.markdown('<div class="main-content">', unsafe_allow_html=True)

if "agent_ready" not in st.session_state:
    st.session_state.agent_ready = False

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Disable button status
update_disabled = len(st.session_state.chat_history) > 0

if not update_disabled:
    st.markdown("### Start the conversation with your smart assistant below.")

st.sidebar.markdown("---")

# Sidebar for configuration
st.sidebar.header("🔧 Agent Configuration")

# Model selection
selected_model = st.sidebar.text_input(
    "Choose Model",
    value="gemini-2.5-flash",
    help="Currently, only Gemini models are supported."
)
# Model API key input
user_api_key = st.sidebar.text_input(
    "Model API Key",
    type="password",
    help="Provide your model's API key."
)
# MCP endpoint and custom header
mcp_url = st.sidebar.text_input(
    "MCP Endpoint URL",
)
with st.sidebar.expander("🔐 MCP Tools Header (optional)", expanded=False):
    mcp_header_name = st.text_input(
        "Header name",
        value="Authorization",
        help="You can specify a custom request header name if your MCP server requires one."
    )
    mcp_header_value = st.text_input(
        "Header value",
        type="password",
        help="You can specify a custom request header value if your MCP server requires one."
    )
if selected_model and user_api_key and mcp_url:
    update_disabled_agent_button = False
else:
    update_disabled_agent_button = True
# st.sidebar.markdown("---")

col1, col2, col3 = st.sidebar.columns(3)
with col2:
    config_submitted = st.button("Prepare Agent", icon="🚀", disabled=update_disabled_agent_button, use_container_width=True)
    if config_submitted:
        if not user_api_key:
            st.error("Model API key is required.")
        else:
            os.environ["GOOGLE_API_KEY"] = user_api_key
            st.session_state.agent_ready = True

async def prepare_agent(selected_model, mcp_url, mcp_header_name=None, mcp_header_value=None):
    llm = ChatGoogleGenerativeAI(model=selected_model)
    mcp_config = {
        "custom_mcp": {
            "transport": "streamable_http",
            "url": mcp_url,
        }
    }
    if mcp_header_name and mcp_header_value:
        mcp_header_name, mcp_header_value = mcp_header_name.strip(), mcp_header_value.strip()
        mcp_config["custom_mcp"]["headers"] = {
            mcp_header_name: mcp_header_value
        }
    client = MultiServerMCPClient(mcp_config)
    tools = await client.get_tools()
    agent = create_agent(llm, tools)
    return agent

# Async function to get agent response
async def get_agent_response(agent, user_input):
    # Add user message
    st.session_state.chat_history.append(HumanMessage(content=user_input))
    try:
        # Get response
        response = await agent.ainvoke({"messages": st.session_state.chat_history})
        # Append new messages
        new_messages = response["messages"][len(st.session_state.chat_history):]
        st.session_state.chat_history.extend(new_messages)
        return new_messages
    except Exception as e:
        st.error(f"An error occurred during agent execution: {e}")
        # Optionally remove the last HumanMessage if the ainvoke failed before extending
        if st.session_state.chat_history and st.session_state.chat_history[-1].content == user_input:
            st.session_state.chat_history.pop()

def parse_msg(message):
    if isinstance(message, dict):
        st.json(message)
        return
    try:
        # Try parsing the message content as JSON
        parsed_dict = json.loads(message)
        st.json(parsed_dict)
    except:
        if isinstance(message, list):
            try:
                st.markdown(message[0]['text'])
            except:
                st.markdown(message)
        else:
            st.markdown(message)

def render_msg(msg):
    msg_content = msg.content
    if isinstance(msg, ToolMessage):
        tool_name = msg.name
        label = f"{tool_name} Tool Response" if tool_name else "Tool Response"
        with st.expander(label):
            parse_msg(msg_content if msg_content else msg.additional_kwargs)
    else:
        parse_msg(msg_content if msg_content else msg.additional_kwargs)

if selected_model and user_api_key and mcp_url and st.session_state.agent_ready:
    try:
        with st.spinner("Agent is getting ready..."):
            if mcp_header_name and mcp_header_value:
                agent = asyncio.run(prepare_agent(selected_model, mcp_url, mcp_header_name, mcp_header_value))
            else:
                agent = asyncio.run(prepare_agent(selected_model, mcp_url))
    except:
        st.sidebar.error("Provide proper configaration values.")

st.sidebar.markdown("---")
with st.sidebar.form(key="system_msg_form"):
    system_msg = st.text_area("System Message", placeholder="Enter new system message...")
    submitted = st.form_submit_button("Update System Message", disabled=update_disabled)
    if submitted:
        st.session_state.chat_history.append(SystemMessage(content=system_msg.strip()))
        st.success("System message added.")
# New Chat button
col1, col2, col3 = st.sidebar.columns(3)
with col2:
    if st.button("New Chat", icon="🆕", disabled=not update_disabled, use_container_width=True):
        st.session_state.chat_history = []

# Display chat history
for msg in st.session_state.chat_history:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        render_msg(msg)

# Input box
if prompt := st.chat_input("Type your message..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    try:
        if agent:
            with st.spinner("Thinking..."):
                new_msgs = asyncio.run(get_agent_response(agent, prompt))
                for msg in new_msgs:
                    with st.chat_message("assistant"):
                        render_msg(msg)
    except:
        st.warning("Please configure the agent using the sidebar and click 'Prepare Agent' to begin.")