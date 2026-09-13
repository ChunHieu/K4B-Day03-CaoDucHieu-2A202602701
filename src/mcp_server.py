"""
🔌 MODEL CONTEXT PROTOCOL (MCP) SERVER MODULE
Mô phỏng kiến trúc MCP Server (Client-Server Architecture) cung cấp công cụ chuẩn hóa.
"""

import json
import sys
from typing import Dict, Any, List
from tools import TOOLS_SCHEMA, dispatch_tool_call

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class MCPVinBusServer:
    def __init__(self, server_name: str = "vinbus-service-mcp-server"):
        self.server_name = server_name
        self.version = "2026.1.0"

    def list_tools(self) -> List[Dict[str, Any]]:
        """Công bố danh sách công cụ cho Agent."""
        return TOOLS_SCHEMA

    def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gọi công cụ và đóng gói kết quả theo khung bài lab."""
        raw_result = dispatch_tool_call(tool_name, arguments)
        content = json.loads(raw_result)

        return {
            "jsonrpc": "2.0",
            "server": self.server_name,
            "tool": tool_name,
            "result": content
        }


if __name__ == "__main__":
    server = MCPVinBusServer()

    print(f"✅ Khởi tạo MCP Server: {server.server_name}")
    print(f"Version: {server.version}")
    print(f"📦 Số lượng công cụ: {len(server.list_tools())}")

    for tool in server.list_tools():
        print(f"  - {tool['name']}")

    checks = [
        (
            "Tra cứu tuyến tồn tại",
            "lookup_bus_route",
            {"route_id": "E01"},
            "SUCCESS"
        ),
        (
            "Tra cứu tuyến không tồn tại",
            "lookup_bus_route",
            {"route_id": "UNKNOWN"},
            "NOT_FOUND"
        ),
        (
            "Đăng ký vé tháng",
            "register_monthly_pass",
            {
                "passenger_name": "Khách Thử Nghiệm",
                "phone": "0900000000",
                "route_id": "E01",
                "month": "2026-10"
            },
            "SUCCESS"
        ),
        (
            "Gọi công cụ không tồn tại",
            "unknown_tool",
            {},
            "UNKNOWN_TOOL"
        )
    ]

    for title, tool_name, arguments, expected_status in checks:
        response = server.call_tool(tool_name, arguments)

        assert response["jsonrpc"] == "2.0"
        actual_status = response["result"].get("status")
        assert actual_status == expected_status, (
            f"{title}: kỳ vọng {expected_status}, nhận {actual_status}"
        )

        print(f"\n✅ PASS: {title}")
        print(json.dumps(response, ensure_ascii=False, indent=2))