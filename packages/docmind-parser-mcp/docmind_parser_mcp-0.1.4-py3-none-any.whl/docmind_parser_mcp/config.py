import yaml
from pathlib import Path
import shutil
import os

def load_config():
    # 首先尝试加载用户目录下的配置文件
    user_config_dir = Path.home() / ".docmind"
    user_config_path = user_config_dir / "docmind_config.yaml"
    
    # 如果用户配置文件不存在，则复制默认配置文件到用户目录
    if not user_config_path.exists():
        default_config_path = Path(__file__).parent / "docmind_config.yaml"
        # 确保用户配置目录存在
        user_config_dir.mkdir(parents=True, exist_ok=True)
        # 复制默认配置文件到用户目录
        shutil.copy(default_config_path, user_config_path)
    
    # 加载用户配置文件
    with open(user_config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # 从环境变量中读取配置值，如果存在则覆盖配置文件中的值
    # 解析相关配置
    parse_config = config.get("parse", {})
    
    # 检查环境变量并更新配置
    structure_type = os.getenv("DOC_MIND_STRUCTURE_TYPE")
    if structure_type is not None:
        parse_config["structure_type"] = structure_type
    
    formula_enhancement = os.getenv("DOC_MIND_FORMULA_ENHANCEMENT")
    if formula_enhancement is not None:
        # 将字符串转换为布尔值
        parse_config["formula_enhancement"] = formula_enhancement.lower() in ("true", "1", "yes", "on")
    
    llm_enhancement = os.getenv("DOC_MIND_LLM_ENHANCEMENT")
    if llm_enhancement is not None:
        # 将字符串转换为布尔值
        parse_config["llm_enhancement"] = llm_enhancement.lower() in ("true", "1", "yes", "on")
    
    enhancement_mode = os.getenv("DOC_MIND_ENHANCEMENT_MODE")
    if enhancement_mode is not None:
        parse_config["enhancement_mode"] = enhancement_mode
    
    # 服务器相关配置
    server_config = config.get("server", {})
    
    protocol_mode = os.getenv("SERVER_PROTOCOL_MODE")
    if protocol_mode is not None:
        server_config["protocol_mode"] = protocol_mode
    
    bind_host = os.getenv("SERVER_BIND_HOST")
    if bind_host is not None:
        server_config["bind_host"] = bind_host
    
    listen_port = os.getenv("SERVER_LISTEN_PORT")
    if listen_port is not None:
        # 将字符串转换为整数
        try:
            server_config["listen_port"] = int(listen_port)
        except ValueError:
            pass  # 如果转换失败，保持原配置
    
    # 更新配置字典
    config["parse"] = parse_config
    config["server"] = server_config
    
    return config

config = load_config()