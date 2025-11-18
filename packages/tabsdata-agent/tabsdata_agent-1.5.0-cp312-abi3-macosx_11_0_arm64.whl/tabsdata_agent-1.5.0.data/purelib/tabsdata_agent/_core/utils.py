#
# Copyright 2025 Tabs Data Inc.
#

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

from tabsdata.api.tabsdata_server import TabsdataServer


def get_client(config: RunnableConfig) -> TabsdataServer:
    """
    Get a TabsdataServer client from a RunnableConfig.
    """
    client = config["configurable"].get("tabsdata", None)
    if client and isinstance(client, TabsdataServer):
        return client
    else:
        raise ValueError("TabsdataServer client not found in config.")


def extract_tools(chat_response: dict) -> list[dict]:
    """
    Extract tool names called (tool_calls) in a LangChain chat response.
    Returns a list of dicts: {"name": tool_name, "args": arguments_dict}.
    """
    tools_used_with_args = []

    for msg in reversed(chat_response.get("messages", [])):
        if isinstance(msg, AIMessage):
            # New format: tool_calls is a top-level attribute
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for call in msg.tool_calls:
                    tool_name = call.get("name")
                    arguments = call.get("args", {})
                    tools_used_with_args.append({"name": tool_name, "args": arguments})
    return tools_used_with_args


def extract_final_answer(chat_response: dict) -> str:
    """
    Extract the final answer from a LangChain chat response.
    Returns the content of the last AIMessage.
    """
    for msg in reversed(chat_response.get("messages", [])):
        if isinstance(msg, AIMessage):
            return msg.content
    if "error" in chat_response:
        return chat_response["error"]
    return ""


def count_tokens(chat_response: dict) -> int:
    """
    Extract the token count from a LangChain response.
    """
    for msg in reversed(chat_response.get("messages", [])):
        if isinstance(msg, AIMessage):
            total_tokens = msg.usage_metadata.get("total_tokens")
            if total_tokens is None:
                raise ValueError("Token usage metadata not found in chat response.")
            return total_tokens
    raise ValueError("Token usage metadata not found in chat response.")
