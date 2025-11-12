import asyncio
import os
import sys
from typing import Any, Iterable

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from dotenv import load_dotenv 
load_dotenv()

def _blocks_to_text(blocks: Iterable[Any]) -> str:
    parts: list[str] = []
    for b in blocks or []:
        text = getattr(b, "text", None)
        if isinstance(text, str):
            parts.append(text)
        else:
            # fallback
            parts.append(str(b))
    return "".join(parts)


async def main() -> None:
    # 要求在环境中设置 BB_USERNAME 与 BB_PASSWORD（以及可选的 BB_BASE_URL）
    if not os.getenv("BB_USERNAME") or not os.getenv("BB_PASSWORD"):
        print("缺少环境变量：请设置 BB_USERNAME 与 BB_PASSWORD 后再运行本测试。")
        return

    # 在 src 布局下运行模块，设置 cwd 指向 src 以便 `python -m bb_mcp` 能找到包
    project_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "bb_mcp"],
        cwd=project_src,
        env=os.environ.copy(),
    )

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # 1) 列出工具，确认 fetch_content 与 search_file_info 存在
            tools_result = await session.list_tools()
            tool_names = [t.name for t in tools_result.tools]
            print("已发现工具:", tool_names)

            # 2) 调用 fetch_content（分页非 verbose），用于对比目录树中是否包含 Assignment1
            fc_args = {"code": "STA4001", "verbose": False, "page": 1}
            fc_result = await session.call_tool("fetch_content", fc_args)
            fc_text = _blocks_to_text(fc_result.content)
            print("\n===== fetch_content 结果（页1，截断预览） =====")
            print(fc_text[:2000])

            # 3) 在正确文件夹内搜索 Assignment1（应命中）
            s1_args = {"course_code": "STA4001", "folder": "Assignment", "keyword": "Assignment1"}
            s1_result = await session.call_tool("search_content_info", s1_args)
            s1_text = _blocks_to_text(s1_result.content)
            print("\n===== search_file_info 结果（folder=Assignment, keyword=Assignment1） =====")
            print(s1_text)

            # 4) 故意在错误文件夹内搜索，用于对比（多半不命中）
            s2_args = {"course_code": "STA4001", "folder": "Assessment Scheme", "keyword": "Assignment1"}
            s2_result = await session.call_tool("search_content_info", s2_args)
            s2_text = _blocks_to_text(s2_result.content)
            print("\n===== search_file_info 结果（folder=Assessment Scheme, keyword=Assignment1） =====")
            print(s2_text)

            # 5) 不指定文件夹，验证回退到整棵树搜索（应命中）
            s3_args = {"course_code": "STA4001", "folder": "", "keyword": "Assignment1"}
            s3_result = await session.call_tool("search_content_info", s3_args)
            s3_text = _blocks_to_text(s3_result.content)
            print("\n===== search_file_info 结果（folder=空, keyword=Assignment1） =====")
            print(s3_text)


if __name__ == "__main__":
    asyncio.run(main())


