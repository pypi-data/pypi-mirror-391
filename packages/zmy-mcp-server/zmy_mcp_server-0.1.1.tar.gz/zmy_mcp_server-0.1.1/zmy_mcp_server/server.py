import asyncio
from mcp.server import Server, Tool
import subprocess
import json

class UvxTool(Tool):
    """
    允许 LLM 执行 uvx 命令的工具。
    """
    def __init__(self):
        super().__init__("run_uvx_command", "Run a specific uvx command in an isolated environment.")

    async def apply(self, command: str, arguments: list[str]) -> str:
        """
        执行指定的 uvx 命令并返回结果。
        """
        try:
            # 使用 subprocess 运行命令
            result = subprocess.run(
                ["uvx", command] + arguments,
                capture_output=True,
                text=True,
                check=True
            )
            return json.dumps({"output": result.stdout})
        except subprocess.CalledProcessError as e:
            return json.dumps({"error": e.stderr})
        except FileNotFoundError:
            return json.dumps({"error": "`uvx` command not found. Ensure `uv` is installed and in PATH."})

def main():
    # 创建 MCP 服务器实例并添加工具
    server = Server(
        "my-mcp-server",
        "A server exposing uvx functionality to LLMs.",
        [UvxTool()],
    )
    # 运行服务器 (通常以 stdio 模式运行，以便与 LLM 客户端通信)
    asyncio.run(server.run_stdio())

if __name__ == "__main__":
    main()
