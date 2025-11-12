"""
配置初始化模块
Configuration Initialization Module

提供配置文件的初始化功能，在项目目录创建配置目录结构
Provides configuration file initialization, creating config directory structure in project directory
"""
import json
from pathlib import Path
from typing import Optional, List


def get_config_locations() -> List[Path]:
    """
    获取配置文件的查找路径（按优先级排序）
    Get configuration file search paths (ordered by priority)
    
    只返回已存在的目录路径，不会自动创建目录。
    Only returns existing directory paths, does not create directories automatically.
    
    Returns:
        配置路径列表，优先级从高到低
        List of config paths, ordered by priority (highest first)
    """
    locations = []
    
    # 当前工作目录下的 sku-config 目录
    # Current working directory sku-config folder
    cwd_sku_config_base = Path.cwd() / "sku-config"
    if cwd_sku_config_base.exists():
        locations.append(cwd_sku_config_base)
    
    return locations


def get_config_dir() -> Optional[Path]:
    """
    获取实际使用的配置目录（查找已存在的配置）
    Get the actual config directory (find existing config)
    
    Returns:
        配置目录路径，如果不存在则返回 None
        Config directory path, or None if not found
    """
    locations = get_config_locations()
    
    for config_dir in locations:
        common_config = config_dir / "common.json"
        if common_config.exists():
            return config_dir
    
    return None


def init_config(
    force: bool = False
) -> Path:
    """
    初始化配置目录结构
    
    自动创建 sku-config 目录和配置文件结构。
    
    Args:
        force: 如果为 True，即使配置文件已存在也会覆盖
    
    Returns:
        创建的配置目录路径
        Created config directory path
    
    Raises:
        ValueError: 如果配置文件已存在且 force=False
    """
    # 使用当前目录下的 sku-config
    config_dir = Path.cwd() / "sku-config"
    
    # 自动创建 sku-config 目录（如果不存在）
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建配置子目录
    businesses_dir = config_dir / "businesses"
    businesses_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建空的 common.json 文件（如果不存在）
    common_config = config_dir / "common.json"
    if not common_config.exists():
        # 只创建空文件，不填充内容
        common_config.touch()
    elif force:
        # 如果 force=True，清空文件内容
        common_config.write_text("", encoding='utf-8')
    
    # 创建 README.md 说明文件（如果不存在）
    readme_file = config_dir / "README.md"
    if not readme_file.exists() or force:
        readme_content = """# SKU Template 配置文件说明

本目录包含 SKU Template 模块的配置文件。

## 文件说明

- `common.json`: 通用配置，包含环境设置、API 路径等（已自动创建空文件，需要填写内容）
- `businesses/`: 业务特定配置目录
  - 每个业务一个 JSON 文件
  - 文件名对应业务名称

## 配置优先级

配置文件按以下优先级查找：
1. 项目目录 (`./sku-config/`) - 中等优先级

## 创建配置文件

1. 创建 `common.json` 文件，设置 API 地址和认证信息
2. 在 `businesses/` 目录下创建业务配置文件
3. 配置修改后，`SkuQueryFactory` 会在下次使用时自动重新加载

## 使用示例

```python
from pathlib import Path
from sku_template import SkuQueryFactory

# 方式1: 自动查找配置
client = SkuQueryFactory.get_client("speech-to-text", environment="staging")

# 方式2: 指定配置目录
config_dir = Path("/path/to/your/config")
client = SkuQueryFactory.get_client("speech-to-text", environment="staging", config_dir=config_dir)
```

## 更多信息

详细配置说明请参考 sku-config 模块文档。
"""
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    print(f"✅ 配置目录已创建: {config_dir}")
    print(f"✅ 通用配置文件已创建: {common_config}")
    print(f"📝 请根据实际需求填写配置文件内容：")
    print(f"   - 通用配置: {common_config}")
    print(f"   - 业务配置目录: {businesses_dir}")
    print(f"   - 参考文档了解配置文件格式")
    
    return config_dir


def check_config() -> tuple[bool, Optional[Path], str]:
    """
    检查配置文件是否存在
    
    Returns:
        (是否存在, 配置目录路径, 消息)
        (exists, config_dir, message)
    """
    config_dir = get_config_dir()
    
    if config_dir is None:
        return False, None, "未找到配置文件，请运行初始化命令"
    
    return True, config_dir, f"找到配置文件: {config_dir}"


def main():
    """CLI 入口函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SKU Template 配置初始化工具")
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制覆盖已存在的配置文件"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="检查配置文件是否存在"
    )
    
    args = parser.parse_args()
    
    if args.check:
        exists, config_dir, message = check_config()
        if exists:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            print(f"💡 运行 'sku-config-init' 进行初始化")
    else:
        try:
            config_dir = init_config(force=args.force)
            print(f"\n📖 配置文件位置: {config_dir}")
            print(f"📖 通用配置: {config_dir / 'common.json'}")
            print(f"📖 业务配置: {config_dir / 'businesses'}")
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            exit(1)


if __name__ == "__main__":
    main()

