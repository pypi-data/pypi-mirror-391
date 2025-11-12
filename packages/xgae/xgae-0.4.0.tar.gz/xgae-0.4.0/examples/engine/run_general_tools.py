import asyncio

from xgae.engine.task_engine import XGATaskEngine
from xgae.utils.setup_env import setup_logging
from xgae.engine.mcp_tool_box import XGAMcpToolBox

setup_logging()

async def main() -> None:
    tool_box = XGAMcpToolBox(custom_mcp_server_file="xga_mcp_servers.json")
    engine = XGATaskEngine(tool_box=tool_box, general_tools=["*"])

    user_input =  "This week's gold price"
    final_result = await engine.run_task_with_final_answer(task_input={"role": "user", "content": user_input})
    print("FINAL RESULT:", final_result)

asyncio.run(main())