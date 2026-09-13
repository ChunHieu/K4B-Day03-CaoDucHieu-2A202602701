"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
"""

import json
from pathlib import Path
import re
import unicodedata
from typing import Dict, Any
from uuid import uuid4

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    # Tool 1: Đã được định nghĩa mẫu sẵn cho Học viên tham khảo
    {
        "name": "lookup_bus_route",
        "description": (
            "Tra cứu tuyến xe trong bản lưu dữ liệu Hà Nội bằng mã tuyến "
            "hoặc cả điểm đi và điểm đến. "
            "Nếu có nhiều tuyến phù hợp, cần hỏi người dùng chọn tuyến."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "route_id": {
                    "type": "string",
                    "description": "Mã tuyến, ví dụ E01."
                },
                "origin": {
                    "type": "string",
                    "description": "Tên điểm đi."
                },
                "destination": {
                    "type": "string",
                    "description": "Tên điểm đến."
                }
            },
            "required": []
        }
    },
    
    # --------------------------------------------------------------------------
    # TODO 1.2: HỌC VIÊN HOÀN THIỆN TOOL SCHEMA CHO 'schedule_appointment'
    # 🎯 YÊU CẦU THIẾT KẾ SCHEMA (JSON SCHEMA STANDARD):
    # 1. Tool dùng để đặt lịch hẹn tư vấn học vụ với Cố vấn học tập VinUni.
    # 2. Thiết kế các tham số (properties) để LLM trích xuất:
    #    - student_id (string): Mã sinh viên cần đặt lịch (ví dụ: 'SV2026001')
    #    - datetime_str (string): Thời gian hẹn (ví dụ: '14:00 15/09/2026')
    #    - advisor_name (string): Tên cố vấn học tập
    # 3. Khai báo danh sách các trường bắt buộc (required).
    # --------------------------------------------------------------------------
    {
        "name": "register_monthly_pass",
        "description": (
            "Đăng ký vé tháng mô phỏng khi người dùng yêu cầu đăng ký "
            "và đã cung cấp đủ thông tin. Không phát hành vé VinBus thật."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "passenger_name": {
                    "type": "string",
                    "description": "Họ tên hành khách."
                },
                "phone": {
                    "type": "string",
                    "description": "Số điện thoại gồm 10 chữ số, bắt đầu bằng 0."
                },
                "route_id": {
                    "type": "string",
                    "description": "Mã tuyến cần đăng ký."
                },
                "month": {
                    "type": "string",
                    "description": "Tháng sử dụng vé theo định dạng YYYY-MM."
                }
            },
            "required": [
                "passenger_name", "phone", "route_id", "month"
            ]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================
# Dữ liệu tuyến từ nguồn chính thức; đăng ký vẫn mô phỏng.

_DATA = json.loads((Path(__file__).resolve().parents[1] / "config/hanoi_routes.json").read_text(encoding="utf-8"))
ROUTES = {r["route_id"]: {**r, **{k: v for k, v in _DATA.items() if k != "routes"}} for r in _DATA["routes"]}
for route in ROUTES.values():
    route["city"] = "hanoi"
_HCM = json.loads((Path(__file__).resolve().parents[1] / "config/hcm_routes.json").read_text(encoding="utf-8"))
for route in _HCM["routes"]:
    ROUTES[route["route_id"]] = {**route, **{k: v for k, v in _HCM.items() if k != "routes"}, "city": "hcm"}
for schema in TOOLS_SCHEMA:
    schema["parameters"]["properties"]["city"] = {"type": "string", "enum": ["hanoi", "hcm"], "description": "Thành phố: hanoi là Hà Nội, hcm là TP.HCM."}
TOOLS_SCHEMA[0]["description"] = "Tra cứu tuyến theo thành phố và mã tuyến hoặc điểm đi–đến. Chỉ cung cấp city để liệt kê các tuyến đã lưu."
REGISTRATIONS = {}

def json_result(data):
    return json.dumps(data, ensure_ascii=False)


def normalize(text):
    """Chuẩn hóa để tìm kiếm không phân biệt dấu và chữ hoa."""
    text = unicodedata.normalize("NFD", text.strip().lower())
    text = "".join(
        char for char in text
        if unicodedata.category(char) != "Mn"
    )
    return " ".join(text.replace("đ", "d").split())


def execute_lookup_bus_route(
    route_id: str = "",
    origin: str = "",
    destination: str = "",
    city: str = "hanoi"
) -> str:
    if city not in ("hanoi", "hcm"):
        return json_result({"status": "INVALID_ARGUMENTS", "message": "Chọn hanoi hoặc hcm."})
    local_routes = {key: route for key, route in ROUTES.items() if route["city"] == city}
    if not all(isinstance(v, str) for v in [route_id, origin, destination]):
        return json_result({
            "status": "INVALID_ARGUMENTS",
            "message": "Các tham số tra cứu phải là chuỗi."
        })

    if route_id.strip():
        route = local_routes.get(route_id.strip().upper())
        matches = [route] if route else []
    elif origin.strip() and destination.strip():
        matches = []

        for route in local_routes.values():
            stops = [normalize(stop) for stop in route["waypoints"]]

            # Chỉ tìm theo chiều các điểm dừng được liệt kê.
            if any(
                normalize(origin) == stops[i]
                and normalize(destination) == stops[j]
                for i in range(len(stops))
                for j in range(i + 1, len(stops))
            ):
                matches.append(route)
    elif not origin.strip() and not destination.strip():
        matches = list(local_routes.values())
    else:
        return json_result({
            "status": "INVALID_ARGUMENTS",
            "message": "Cần cung cấp mã tuyến hoặc cả điểm đi và điểm đến."
        })

    if not matches:
        return json_result({
            "status": "NOT_FOUND",
            "message": "Không tìm thấy tuyến trong bản lưu của thành phố đã chọn."
        })

    return json_result({
        "status": "SUCCESS",
        "data_mode": "official_source_snapshot",
        "count": len(matches),
        "routes": matches,
        "requires_selection": len(matches) > 1
    })


def execute_register_monthly_pass(
    passenger_name: str,
    phone: str,
    route_id: str,
    month: str,
    city: str = "hanoi"
) -> str:
    values = [passenger_name, phone, route_id, month]

    if not all(isinstance(value, str) and value.strip() for value in values):
        return json_result({
            "status": "INVALID_ARGUMENTS",
            "message": "Thông tin đăng ký phải là chuỗi và không được để trống."
        })

    passenger_name = passenger_name.strip()
    phone = phone.strip()
    route_id = route_id.strip().upper()
    month = month.strip()

    if not re.fullmatch(r"0[0-9]{9}", phone):
        return json_result({
            "status": "INVALID_ARGUMENTS",
            "message": "Số điện thoại phải có 10 chữ số và bắt đầu bằng 0."
        })

    if not re.fullmatch(r"[0-9]{4}-(0[1-9]|1[0-2])", month):
        return json_result({
            "status": "INVALID_ARGUMENTS",
            "message": "Tháng đăng ký phải theo định dạng YYYY-MM."
        })

    route = ROUTES.get(route_id)
    if not route or route["city"] != city:
        return json_result({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy tuyến {route_id} trong thành phố đã chọn."
        })
    if route.get("monthly_pass_price_vnd") is None:
        return json_result({"status": "UNSUPPORTED", "message": "Chưa xác minh chính sách vé tháng tuyến này nên chưa hỗ trợ đăng ký; không áp dụng giá Hà Nội.", "source_url": route["source_url"]})

    # Tránh tạo trùng khi Agent gọi lại trong cùng phiên chạy.
    registration_key = (phone, route_id, month)
    if registration_key in REGISTRATIONS:
        return json_result({
            "status": "ALREADY_REGISTERED",
            "simulation": True,
            "registration": REGISTRATIONS[registration_key],
            "message": "Đã có đăng ký cho số điện thoại, tuyến và tháng này."
        })

    registration = {
        "registration_id": f"VB-DEMO-{uuid4().hex[:10].upper()}",
        "passenger_name": passenger_name,
        "phone": phone,
        "route_id": route_id,
        "month": month,
        "price_vnd": route["monthly_pass_price_vnd"],
        "fare_note": route["data_note"],
        "fare_source_url": route["fare_source_url"]
    }
    REGISTRATIONS[registration_key] = registration

    return json_result({
        "status": "SUCCESS",
        "simulation": True,
        "registration": registration,
        "message": "Đăng ký vé tháng mô phỏng thành công. Đây không phải vé thật."
    })


# Router gọi tool thực tế
TOOL_ROUTER = {
    "lookup_bus_route": execute_lookup_bus_route,
    "register_monthly_pass": execute_register_monthly_pass
}


def dispatch_tool_call(tool_name: str, arguments: dict) -> str:
    if not isinstance(tool_name, str) or tool_name not in TOOL_ROUTER:
        return json_result({
            "status": "UNKNOWN_TOOL",
            "message": f"Công cụ không tồn tại: {tool_name}"
        })

    if not isinstance(arguments, dict):
        return json_result({
            "status": "INVALID_ARGUMENTS",
            "message": "Tham số công cụ phải là một object."
        })

    try:
        return TOOL_ROUTER[tool_name](**arguments)
    except TypeError as error:
        return json_result({
            "status": "INVALID_ARGUMENTS",
            "message": str(error)
        })
    except Exception as error:
        return json_result({
            "status": "EXECUTION_ERROR",
            "message": str(error)
        })
