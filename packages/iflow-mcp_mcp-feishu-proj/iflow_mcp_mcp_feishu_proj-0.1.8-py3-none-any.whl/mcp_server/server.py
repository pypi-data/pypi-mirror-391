from mcp.server.fastmcp import FastMCP
from .fsprojclient import FSProjClient, WorkItemType
from typing import Literal
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 检查必需的环境变量
required_env_vars = [
    "FS_PROJ_PROJECT_KEY",
    "FS_PROJ_USER_KEY",
    "FS_PROJ_PLUGIN_ID",
    "FS_PROJ_PLUGIN_SECRET"
]

missing_vars = []
for var in required_env_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f"错误: 缺少以下必需的环境变量: {', '.join(missing_vars)}")
    print("请确保这些环境变量已在.env文件中设置或已在系统环境中定义")
    sys.exit(1)

host = os.getenv("SSE_SERVER_HOST", "0.0.0.0")
port = int(os.getenv("SSE_SERVER_PORT", "8000"))
mcp = FastMCP("feishuproj-mcp-server", host=host, port=port)

client = FSProjClient(
    os.getenv("FS_PROJ_BASE_URL", "https://project.feishu.cn/"),
    project_key=os.getenv("FS_PROJ_PROJECT_KEY"),
    user_key=os.getenv("FS_PROJ_USER_KEY"),
    plugin_id=os.getenv("FS_PROJ_PLUGIN_ID"),
    plugin_secret=os.getenv("FS_PROJ_PLUGIN_SECRET"),
)

@mcp.tool("get_view_list")
def get_view_list(work_item_type_key: WorkItemType):
    """获取当前飞书项目下的某一类型工作项的所有视图列表
    Args:
        work_item_type_key: 工作项类型，可选值为"story"、"version"、"issue", 分别对应需求、版本、缺陷。
    """    
    client.get_plugin_token()
    return client.get_view_list(work_item_type_key)

@mcp.tool("get_view_detail")
def get_view_detail(view_id: str, page_num: int = 1, page_size: int = 20):
    """根据视图id获取指定视图下的工作项列表
    Args:
        view_id: 视图标识id
        page_num: 页码，默认为1
        page_size: 每页数量，默认为20
    """
    client.get_plugin_token()
    return client.get_view_detail(view_id, page_num, page_size)

@mcp.tool("get_view_detail_by_name")
def get_view_detail_by_name(view_name: str, work_item_type_key: WorkItemType, page_num: int = 1, page_size: int = 20):
    """根据视图名称获取指定视图下的工作项列表
    Args:
        view_name: 视图名称
        work_item_type_key: 工作项类型，可选值为"story"、"version"、"issue", 分别对应需求、版本、缺陷。
        page_num: 页码，默认为1
        page_size: 每页数量，默认为20
    """
    client.get_plugin_token()
    # 获取所有视图列表
    view_list = client.get_view_list(work_item_type_key)
    # 查找指定名称的视图
    view = next((v for v in view_list if v["name"] == view_name), None)
    if view:
        # 如果找到视图，获取其ID
        view_id = view["view_id"]
        return client.get_view_detail(view_id, page_num, page_size)
    else:
        return {}

@mcp.tool("get_work_item_detail")
def get_work_item_detail(work_item_type_key: WorkItemType, work_item_ids: str):
    """获取指定工作项的详情信息
    Args:
        work_item_type_key: 工作项类型，可选值为"story"、"version"、"issue", 分别对应需求、版本、缺陷。
        work_item_ids: 工作项ID，多个ID之间用逗号分隔
    """
    client.get_plugin_token()
    id_list = [int(id.strip()) for id in work_item_ids.split(",")]
    return client.get_workitem_detail(work_item_type_key, id_list)

@mcp.tool("get_work_item_type_meta")
def get_work_item_type_meta(work_item_type_key: WorkItemType):
    """获取工作项类型元数据
    - 在工作项详情的"fields"字段中各个字段的具体意义及信息可以在工作项类型元数据中获取
    Args:
        work_item_type_key: 工作项类型，可选值为"story"、"version"、"issue", 分别对应需求、版本、缺陷。
    """
    client.get_plugin_token()
    return client.get_work_item_type_meta(work_item_type_key)

@mcp.tool("get_flow_roles")
def get_flow_roles(work_item_type_key: WorkItemType):
    """获取流程角色配置详情
    Args:
        work_item_type_key: 工作项类型，可选值为"story"、"version"、"issue", 分别对应需求、版本、缺陷。
    """
    client.get_plugin_token()
    return client.get_flow_roles(work_item_type_key)
