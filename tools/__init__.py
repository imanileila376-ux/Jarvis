from tools.basic_tools import TOOLS, TOOL_FUNCTIONS
from tools.web_tools import WEB_TOOLS, WEB_TOOL_FUNCTIONS

# Combine all tools
ALL_TOOLS = TOOLS + WEB_TOOLS
ALL_FUNCTIONS = {**TOOL_FUNCTIONS, **WEB_TOOL_FUNCTIONS}