"""
统一的SKU查询框架
统一不同业务的SKU查询接口，避免重复了解API和逻辑
Unified SKU Query Framework - Unified interface for different business SKU queries
"""
import json
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
from pathlib import Path
import requests
from datetime import datetime, timedelta




def format_time(dt, step=0, level="hourly"):
    """
    计算整分钟，整小时，整天的时间
    :param dt: 时间戳（秒或毫秒），必须是数字类型
    :param step: 往前或往后跳跃取整值，默认为0，即当前所在的时间，正数为往后，负数往前。
                例如：
                step = 0 时 2019-04-11 17:38:21.869993 取整秒后为 2019-04-11 17:38:21
                step = 1 时 2019-04-11 17:38:21.869993 取整秒后为 2019-04-11 17:38:22
                step = -1 时 2019-04-11 17:38:21.869993 取整秒后为 2019-04-11 17:38:20
    :param level: 字符串格式。
                "s": 按秒取整；"min": 按分钟取整；"hour": 按小时取整；"days": 按天取整
    :return: 整理后的时间戳
    """
    # 检查输入类型，必须是数字
    if not isinstance(dt, (int, float)):
        raise TypeError(f"format_time 期望接收数字类型的时间戳，但收到了 {type(dt)}: {dt}")
    
    # 如果是毫秒时间戳（13位），转换为秒时间戳（10位）
    if dt > 1e12:  # 大于 1e12 说明是毫秒时间戳
        dt = dt // 1000
    dt = datetime.fromtimestamp(int(dt))
    if level == "daily":  # 整天
        td = timedelta(days=-step, seconds=dt.second, microseconds=dt.microsecond, milliseconds=0,
                       minutes=dt.minute, hours=dt.hour, weeks=0)
        new_dt = dt - td
    elif level == "hourly":  # 整小时
        td = timedelta(days=0, seconds=dt.second, microseconds=dt.microsecond, milliseconds=0, minutes=dt.minute,
                       hours=-step, weeks=0)
        new_dt = dt - td
    elif level == "minutely":  # 整分钟
        td = timedelta(days=0, seconds=dt.second, microseconds=dt.microsecond, milliseconds=0, minutes=-step,
                       hours=0, weeks=0)
        new_dt = dt - td
    elif level == "secondly":  # 整秒
        td = timedelta(days=0, seconds=-step, microseconds=dt.microsecond, milliseconds=0, minutes=0, hours=0,
                       weeks=0)
        new_dt = dt - td
    else:
        new_dt = dt
    timestamp = new_dt.timestamp()
    return int(timestamp) * 1000



@dataclass
class SkuQueryConfig:
    """SKU查询配置"""
    sku_ids: List[str]  # SKU ID列表
    base_url: str  # 基础URL
    headers: Dict[str, str]  # 请求头
    api_path: str  # API路径
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'SkuQueryConfig':
        """从字典创建配置"""
        api_path = config_dict.get("api_path")
        if not api_path:
            raise ValueError("api_path is required in config")
        
        return cls(
            sku_ids=config_dict.get("sku_ids", []),
            base_url=config_dict.get("base_url", ""),
            headers=config_dict.get("headers", {}),
            api_path=api_path
        )


@dataclass
class DetailQueryConfig:
    """Detail查询配置"""
    base_url: str  # 基础URL
    headers: Dict[str, str]  # 请求头
    api_path: str  # API路径
    date_format: str  # 日期格式
    level: str  # 查询级别
    business: str  # 业务名称
    model: str  # 模型名称
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'DetailQueryConfig':
        """从字典创建配置"""
        # 必需字段检查
        api_path = config_dict.get("api_path")
        if not api_path:
            raise ValueError("api_path is required in detail config")
        
        date_format = config_dict.get("date_format")
        if not date_format:
            raise ValueError("date_format is required in detail config")
        
        level = config_dict.get("level")
        if not level:
            raise ValueError("level is required in detail config")
        
        business = config_dict.get("business")
        if not business:
            raise ValueError("business is required in detail config")
        
        model = config_dict.get("model")
        if not model:
            raise ValueError("model is required in detail config")
        
        return cls(
            base_url=config_dict.get("base_url", ""),
            headers=config_dict.get("headers", {}),
            api_path=api_path,
            date_format=date_format,
            level=level,
            business=business,
            model=model
        )


class SkuQueryClient(ABC):
    """SKU查询客户端抽象基类"""
    
    @abstractmethod
    def query_sku(self, vid: int, from_ts: int, sku_ids: List[str], 
                  level: str = "HOURLY", to_ts: Optional[int] = None) -> Dict[str, Any]:
        """查询SKU数据"""
        pass
    
    @abstractmethod
    def query_detail(self, vid: int, from_ts: int, 
                    to_ts: Optional[int] = None) -> Dict[str, Any]:
        """查询Detail数据"""
        pass
    
    def query_sku_across_hours(self, vid: int, start_time: int, end_time: int, 
                               sku_ids: List[str], level: str = "HOURLY") -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        跨小时查询SKU数据（累加多个小时的数据）
        
        该方法会从start_time到end_time，每小时查询一次SKU数据，并累加所有小时的usageValue。
        如果start_time或end_time不是整小时，会自动转换为整小时（向下取整到小时开始）。
        适用于跨小时的计费数据查询场景。
        
        Args:
            vid: 供应商ID
            start_time: 开始时间（时间戳，毫秒），如果不是整小时会自动转换为整小时
            end_time: 结束时间（时间戳，毫秒），如果不是整小时会自动转换为整小时
            sku_ids: SKU ID列表
            level: 时间间隔，默认HOURLY
            
        Returns:
            查询结果字典，包含累加后的数据和每个小时的原始数据
            格式：{
                "aggregated": {
                    "30331": 累加值,  # 简单的数值
                    "30332": 累加值,
                    ...
                },
                "hourly_details": [
                    {
                        "hour": 1699002000000,  # 小时时间戳
                        "data": {
                            "30331": [...],  # 该小时的原始数据
                            "30332": [...],
                            ...
                        }
                    },
                    ...
                ]
            }
        """
        from datetime import datetime

        if start_time is None or end_time is None:
            return {}, []
        
        # 将时间转换为整小时（向下取整到小时开始）
        def to_hour_start(timestamp_ms: int) -> int:
            """将时间戳转换为整小时开始（向下取整）"""
            dt = datetime.fromtimestamp(timestamp_ms / 1000)
            hour_start = dt.replace(minute=0, second=0, microsecond=0)
            return int(hour_start.timestamp() * 1000)
        
        # 判断是否为整小时
        def is_hour_start(timestamp_ms: int) -> bool:
            """判断时间戳是否为整小时开始"""
            dt = datetime.fromtimestamp(timestamp_ms / 1000)
            return dt.minute == 0 and dt.second == 0 and dt.microsecond == 0
        
        # 转换开始时间和结束时间为整小时
        start_hour = to_hour_start(start_time)
        end_hour = to_hour_start(end_time)
        
        # 如果时间被转换了，给出提示
        if not is_hour_start(start_time):
            print(f"⚠️  开始时间 {start_time} 不是整小时，已转换为 {start_hour}")
        if not is_hour_start(end_time):
            print(f"⚠️  结束时间 {end_time} 不是整小时，已转换为 {end_hour}")
        
        # 初始化结果字典，不预设值（如果查询失败，值会是None）
        aggregated_results = {}
        for sku_id in sku_ids:
            aggregated_results[sku_id] = None
        
        # 存储每个小时的原始数据
        hourly_details = []
        
        # 处理每个小时的计费数据
        current_hour = start_hour
        
        print(f"[跨小时查询] 开始查询 - vid={vid}, start_hour={start_hour}, end_hour={end_hour}, sku_ids={sku_ids}, level={level}")
        print(f"[跨小时查询] 时间范围: {datetime.fromtimestamp(start_hour/1000)} 到 {datetime.fromtimestamp(end_hour/1000)}")
        
        while current_hour <= end_hour:
            hour_str = datetime.fromtimestamp(current_hour / 1000).strftime("%Y-%m-%d %H:00:00")
            print(f"\n[跨小时查询] ========== 查询小时: {hour_str} (timestamp: {current_hour}) ==========")
            
            # 查询当前小时的SKU数据
            try:
                hour_results = self.query_sku(vid, current_hour, sku_ids, level)
                query_success = True
                error_message = None
                print(f"[跨小时查询] 查询成功 - hour={current_hour}")
            except Exception as e:
                # 查询失败（抛出异常），记录错误信息
                hour_results = {}
                query_success = False
                error_message = f"查询异常: {str(e)}"
                print(f"⚠️  [跨小时查询] 查询失败 (hour={current_hour}): {error_message}")
            
            # 保存当前小时的原始数据
            hour_detail = {
                "hour": current_hour,
                "data": {},
                "query_success": query_success
            }
            
            if not query_success:
                # 查询失败，记录错误信息
                hour_detail["error"] = error_message
                # 所有SKU在当前小时都没有数据（查询失败）
                for sku_id in sku_ids:
                    hour_detail["data"][sku_id] = []
                    # 如果之前没有成功查询过，保持None（表示查询失败）
                    # 如果之前已经成功查询过，保持当前值（不覆盖）
                    if aggregated_results[sku_id] is None:
                        aggregated_results[sku_id] = None
                print(f"[跨小时查询] ⚠️  查询失败，所有SKU数据为空")
            else:
                # 查询成功，处理数据
                # 检查是否有任何SKU返回了数据（用于判断是否真的查询成功）
                has_any_data = False
                for sku_id in sku_ids:
                    if sku_id in hour_results and hour_results[sku_id]:
                        has_any_data = True
                        break
                
                print(f"[跨小时查询] hour_results keys: {list(hour_results.keys())}")
                print(f"[跨小时查询] 是否有数据: {has_any_data}")
                
                # 如果所有SKU都返回空列表，可能是查询失败（比如500错误但被捕获了）
                # 但query_sku内部已经处理了异常，所以这里假设查询成功
                for sku_id in sku_ids:
                    if sku_id in hour_results and hour_results[sku_id]:
                        # 保存该小时的原始数据
                        hour_detail["data"][sku_id] = hour_results[sku_id].copy()
                        
                        # 计算当前小时的usageValue总和（可能有多条数据）
                        hour_total = sum(item.get("usageValue", 0) for item in hour_results[sku_id])
                        print(f"[跨小时查询] ✅ sku_id={sku_id} 当前小时数据: {len(hour_results[sku_id])}条, usageValue总和={hour_total}")
                        
                        # 累加usageValue（如果之前是None，初始化为0）
                        if aggregated_results[sku_id] is None:
                            aggregated_results[sku_id] = 0
                            print(f"[跨小时查询] sku_id={sku_id} 初始化aggregated_results为0")
                        old_value = aggregated_results[sku_id]
                        aggregated_results[sku_id] += hour_total
                        print(f"[跨小时查询] sku_id={sku_id} 累加: {old_value} + {hour_total} = {aggregated_results[sku_id]}")
                    else:
                        # 该SKU在当前小时没有数据（查询成功但没有该SKU的数据）
                        hour_detail["data"][sku_id] = []
                        print(f"[跨小时查询] ⚠️  sku_id={sku_id} 当前小时无数据（查询成功但返回空）")
                        # 如果之前没有成功查询过，保持None；如果已经查询过，保持当前值
                        # 注意：这里不改变 aggregated_results[sku_id]，因为可能是真的没有数据
            
            # 保存当前小时的详细信息
            hourly_details.append(hour_detail)
            
            # 移动到下一个小时（增加1小时 = 3600000毫秒）
            current_hour += 3600000
        
        print(f"\n[跨小时查询] ========== 查询完成 ==========")
        print(f"[跨小时查询] 最终aggregated_results: {aggregated_results}")
        print(f"[跨小时查询] 查询了 {len(hourly_details)} 个小时")
        
        # 返回累加结果和每个小时的原始数据
        return aggregated_results,hourly_details
    
    def query_detail_across_hours(self, vid: int, start_time: int, end_time: int,level="hourly") -> List[Any]:
        """
        跨小时查询Detail数据（合并多个小时的数据）
        
        该方法会从start_time到end_time，每小时查询一次Detail数据，并合并所有小时的数据。
        如果start_time或end_time不是整小时，会自动转换为整小时（向下取整到小时开始）。
        适用于跨小时的计费数据查询场景。
        
        Args:
            vid: 供应商ID
            start_time: 开始时间（时间戳，毫秒），如果不是整小时会自动转换为整小时
            end_time: 结束时间（时间戳，毫秒），如果不是整小时会自动转换为整小时
            
        Returns:
            合并后的查询结果，包含所有小时的detail数据
            格式：{
                "status_code": 200,
                "data": [...],  # 所有小时的detail数据列表
            }
        """
        from datetime import datetime
        if start_time is None or end_time is None or start_time == "" or end_time == "":
            return []
        # 将时间转换为整小时（向下取整到小时开始）
        def to_hour_start(timestamp_ms: int) -> int:
            """将时间戳转换为整小时开始（向下取整）"""
            dt = datetime.fromtimestamp(timestamp_ms / 1000)
            hour_start = dt.replace(minute=0, second=0, microsecond=0)
            return int(hour_start.timestamp() * 1000)
        
        # 判断是否为整小时
        def is_hour_start(timestamp_ms: int) -> bool:
            """判断时间戳是否为整小时开始"""
            dt = datetime.fromtimestamp(timestamp_ms / 1000)
            return dt.minute == 0 and dt.second == 0 and dt.microsecond == 0
        
        # 转换开始时间和结束时间为整小时
        start_hour = format_time(start_time,0,level)
        end_hour = format_time(end_time,0,level)
        
        # 如果时间被转换了，给出提示
        if not is_hour_start(start_time):
            print(f"⚠️  开始时间 {start_time} 不是整小时，已转换为 {start_hour}")
        if not is_hour_start(end_time):
            print(f"⚠️  结束时间 {end_time} 不是整小时，已转换为 {end_hour}")
        
        # 初始化结果
        all_detail_data = []
        
        # 处理每个小时的计费数据
        current_hour = start_hour
        
        while current_hour <= end_hour:
            # 查询当前小时的Detail数据
            hour_result = self.query_detail(vid, current_hour)
            
            # 如果查询成功，合并数据
            if hour_result.get("status_code") == 200:
                hour_data = hour_result.get("data", [])
                if isinstance(hour_data, list):
                    all_detail_data.extend(hour_data)
            
            # 移动到下一个小时（增加1小时 = 3600000毫秒）
            current_hour += 3600000
        
        # 返回合并后的结果
        return all_detail_data


class StagingSkuQueryClient(SkuQueryClient):
    """Staging环境的SKU查询客户端"""
    
    def __init__(self, sku_config: SkuQueryConfig, detail_config: DetailQueryConfig):
        """
        初始化查询客户端
        
        Args:
            sku_config: SKU查询配置
            detail_config: Detail查询配置
        """
        self.sku_config = sku_config
        self.detail_config = detail_config
    
    def query_sku(self, vid: int, from_ts: int, sku_ids: List[str], 
                  interval: str = "HOURLY", to_ts: Optional[int] = None) -> Dict[str, Any]:
        """
        查询SKU数据
        
        Args:
            vid: 供应商ID
            from_ts: 开始时间戳（毫秒），内部会自动转换为毫秒级时间戳
            sku_ids: SKU ID列表
            interval: 时间间隔，默认HOURLY
            to_ts: 结束时间戳（可选，毫秒），内部会自动转换为毫秒级时间戳
            
        Returns:
            查询结果字典，key为sku_id，value为查询结果
        """
        results = {}
        
        # API需要毫秒级时间戳，将秒转换为毫秒
        from_ts_seconds = from_ts * 1000 if from_ts <= 10000000000 else from_ts  # 如果小于10位数，认为是秒
        to_ts_seconds = None
        if to_ts:
            to_ts_seconds = to_ts * 1000 if to_ts <= 10000000000 else to_ts
        
        for sku_id in sku_ids:
            url = f"{self.sku_config.base_url}{self.sku_config.api_path}"
            params = {
                "interval": interval.upper(),
                "vid": vid,
                "fromTs": from_ts_seconds,
                "skuIdSet": sku_id
            }
            
            if to_ts_seconds and from_ts_seconds < to_ts_seconds:
                params["toTs"] = to_ts_seconds
            
            # 构建 curl 命令
            import urllib.parse
            curl_parts = ["curl", "-X", "GET"]
            
            # 添加 URL 和参数（使用 urllib.parse.urlencode 进行 URL 编码）
            param_str = urllib.parse.urlencode(params)
            full_url = f"{url}?{param_str}"
            curl_parts.append(f'"{full_url}"')
            
            # 添加 headers
            if self.sku_config.headers:
                for key, value in self.sku_config.headers.items():
                    curl_parts.append("-H")
                    curl_parts.append(f'"{key}: {value}"')
            
            curl_cmd = " \\\n  ".join(curl_parts)
            if to_ts:
                print(f"[SKU Query] sku_id={sku_id}, vid={vid}, from_ts={from_ts}ms (转换为 {from_ts_seconds}s), to_ts={to_ts}ms (转换为 {to_ts_seconds}s)")
            else:
                print(f"[SKU Query] sku_id={sku_id}, vid={vid}, from_ts={from_ts}ms (转换为 {from_ts_seconds}s)")
            print(f"[SKU Query] curl 命令:\n{curl_cmd}")
            
            try:
                response = requests.get(url, params=params, headers=self.sku_config.headers, timeout=30)
                print(f"[SKU Query] Response Status: {response.status_code}")
                response.raise_for_status()
                
                data = response.json()
                results[sku_id] = data if isinstance(data, list) else [data]
                
                print(f"[SKU Query] ✅ 查询成功 - sku_id={sku_id}, 返回数据条数: {len(results[sku_id])}")
                if results[sku_id]:
                    print(f"[SKU Query] 数据示例: {results[sku_id][0] if isinstance(results[sku_id], list) else results[sku_id]}")
                    # 打印usageValue总和
                    if isinstance(results[sku_id], list):
                        total_usage = sum(item.get("usageValue", 0) for item in results[sku_id])
                        print(f"[SKU Query] sku_id={sku_id} 总usageValue: {total_usage}")
                else:
                    print(f"[SKU Query] ⚠️  sku_id={sku_id} 返回空数据")
                
            except Exception as e:
                print(f"[SKU Query Error] sku_id={sku_id}, vid={vid}, error={str(e)}")
                # 检查是否是requests异常，包含response信息
                if hasattr(e, 'response') and getattr(e, 'response', None) is not None:
                    try:
                        response = getattr(e, 'response')
                        print(f"[SKU Query Error] Response Status: {response.status_code}")
                        print(f"[SKU Query Error] Response Text: {response.text[:500]}")
                    except (AttributeError, TypeError):
                        pass
                results[sku_id] = []
        
        return results
    
    def query_detail(self, vid: int, from_ts: int, 
                    to_ts: Optional[int] = None) -> Dict[str, Any]:
        """
        查询Detail数据
        
        Args:
            vid: 供应商ID
            from_ts: 开始时间戳（毫秒）
            to_ts: 结束时间戳（可选）
            
        Returns:
            查询结果（JSON格式）
        """
        from datetime import datetime
        
        # 格式化日期
        date_obj = datetime.fromtimestamp(from_ts / 1000)
        formatted_date = date_obj.strftime(self.detail_config.date_format)
        
        url = f"{self.detail_config.base_url}{self.detail_config.api_path}"
        params = {
            "date_time": formatted_date,
            "vid": vid,
            "level": self.detail_config.level.lower(),
            "business": self.detail_config.business,
            "model": self.detail_config.model
        }
        
        # 构建 curl 命令
        import urllib.parse
        curl_parts = ["curl", "-X", "GET"]
        
        # 添加 URL 和参数（使用 urllib.parse.urlencode 进行 URL 编码）
        param_str = urllib.parse.urlencode(params)
        full_url = f"{url}?{param_str}"
        curl_parts.append(f'"{full_url}"')
        
        # 添加 headers
        if self.detail_config.headers:
            for key, value in self.detail_config.headers.items():
                curl_parts.append("-H")
                curl_parts.append(f'"{key}: {value}"')
        
        curl_cmd = " \\\n  ".join(curl_parts)
        print(f"[Detail Query] vid={vid}, from_ts={from_ts}, formatted_date={formatted_date}")
        print(f"[Detail Query] curl 命令:\n{curl_cmd}")
        
        try:
            response = requests.get(url, params=params, headers=self.detail_config.headers, timeout=30)
            print(f"[Detail Query] Response Status: {response.status_code}")
            response.raise_for_status()
            
            # 返回JSON格式的数据
            result = {
                "status_code": response.status_code,
                "data": response.json() if response.text else [],
                "raw_text": response.text
            }
            
            print(f"[Detail Query] ✅ 查询成功 - 返回数据条数: {len(result.get('data', [])) if isinstance(result.get('data'), list) else 'N/A'}")
            return result
            
        except Exception as e:
            print(f"[Detail Query Error] vid={vid}, error={str(e)}")
            if hasattr(e, 'response') and getattr(e, 'response', None) is not None:
                try:
                    response = getattr(e, 'response')
                    print(f"[Detail Query Error] Response Status: {response.status_code}")
                    print(f"[Detail Query Error] Response Text: {response.text[:500]}")
                except (AttributeError, TypeError):
                    pass
            return {
                "status_code": 500,
                "data": [],
                "raw_text": "",
                "error": str(e)
            }


class SkuQueryFactory:
    """SKU查询工厂类 - 统一管理不同业务的查询配置"""
    
    # 配置目录（动态查找，支持多实例）
    _CONFIG_DIR: Optional[Path] = None
    _BUSINESS_CONFIG_DIR: Optional[Path] = None
    _COMMON_CONFIG_FILE: Optional[Path] = None
    
    # 配置缓存
    _COMMON_CONFIG: Optional[Dict[str, Any]] = None
    _BUSINESS_CONFIGS: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def _find_config_dir(cls) -> Optional[Path]:
        """
        查找配置目录（按优先级）
        Find config directory (by priority)
        
        Returns:
            配置目录路径，如果未找到则返回 None
        """
        from .config_init import get_config_dir
        return get_config_dir()
    
    @classmethod
    def _get_config_dir(cls) -> Path:
        """
        获取配置目录，如果不存在则抛出异常
        """
        if cls._CONFIG_DIR is None:
            found_config_dir = cls._find_config_dir()
            if found_config_dir is None:
                raise FileNotFoundError(
                    "未找到配置文件。请运行以下命令初始化配置：\n"
                    "  python -m sku_template.config_init\n"
                    "或查看文档了解配置初始化方法。"
                )
            cls._CONFIG_DIR = found_config_dir
            cls._BUSINESS_CONFIG_DIR = cls._CONFIG_DIR / "businesses"
            cls._COMMON_CONFIG_FILE = cls._CONFIG_DIR / "common.json"
        
        return cls._CONFIG_DIR
    
    @classmethod
    def _load_common_config(cls) -> Dict[str, Any]:
        """加载通用配置"""
        if cls._COMMON_CONFIG is not None:
            return cls._COMMON_CONFIG
        
        try:
            config_dir = cls._get_config_dir()
            common_config_file = config_dir / "common.json"
            
            if not common_config_file.exists():
                print(f"警告: 通用配置文件不存在 {common_config_file}")
                config = {}
            else:
                with open(common_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    config = config if isinstance(config, dict) else {}
            
            cls._COMMON_CONFIG = config
            
        except FileNotFoundError as e:
            print(f"错误: {e}")
            config = {}
        except Exception as e:
            print(f"警告: 加载通用配置文件失败: {e}")
            config = {}
        
        return config or {}
    
    @classmethod
    def _load_business_configs(cls) -> Dict[str, Dict[str, Any]]:
        """从配置文件加载业务配置并合并通用配置"""
        if cls._BUSINESS_CONFIGS:
            return cls._BUSINESS_CONFIGS
        
        # 加载通用配置
        common_config = cls._load_common_config()
        
        try:
            config_dir = cls._get_config_dir()
            business_config_dir = config_dir / "businesses"
            
            if not business_config_dir.exists():
                return {}
            
            # 加载所有业务配置文件并合并通用配置
            for config_file in business_config_dir.glob("*.json"):
                business_name = config_file.stem
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        business_config = json.load(f)
                    
                    # 合并通用配置和业务配置
                    merged_config = cls._merge_configs(common_config, business_config)
                    cls._BUSINESS_CONFIGS[business_name] = merged_config
                except Exception as e:
                    print(f"警告: 加载配置文件失败 {config_file}: {e}")
        except FileNotFoundError as e:
            print(f"错误: {e}")
            return {}
        except Exception as e:
            print(f"警告: 加载业务配置失败: {e}")
            return {}
        
        return cls._BUSINESS_CONFIGS
    
    @classmethod
    def _merge_configs(cls, common: Dict[str, Any], business: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并通用配置和业务配置
        业务配置会覆盖通用配置中的相同字段
        """
        merged = {}
        
        # 合并 environments
        if "environments" in common:
            merged["environments"] = common["environments"].copy()
        else:
            merged["environments"] = {}
        
        if "environments" in business:
            # 如果业务配置中有environments，合并它们
            for env_name, env_config in business["environments"].items():
                if env_name in merged["environments"]:
                    # 合并环境配置（业务配置会覆盖通用配置）
                    merged["environments"][env_name] = {
                        **merged["environments"][env_name],
                        **env_config
                    }
                else:
                    merged["environments"][env_name] = env_config
        
        # 合并 sku 配置
        merged["sku"] = {}
        if "sku" in common:
            merged["sku"].update(common["sku"])
        if "sku" in business:
            merged["sku"].update(business["sku"])
        
        # 合并 detail 配置
        merged["detail"] = {}
        if "detail" in common:
            merged["detail"].update(common["detail"])
        if "detail" in business:
            merged["detail"].update(business["detail"])
        
        # 合并 appIds 配置（业务特定，不包含在通用配置中）
        if "appIds" in business:
            merged["appIds"] = business["appIds"]
        
        return merged
    
    @classmethod
    def _get_business_configs(cls) -> Dict[str, Dict[str, Any]]:
        """获取业务配置（带缓存）"""
        return cls._load_business_configs()
    
    @classmethod
    def get_client(cls, business: str, environment: str = "staging") -> SkuQueryClient:
        """
        获取查询客户端
        
        Args:
            business: 业务名称（如 "speech-to-text"）
            environment: 环境名称（"staging" 或 "prod"），默认为 "staging"
            
        Returns:
            SkuQueryClient实例
            
        Raises:
            ValueError: 业务配置不存在或环境配置不存在
        """
        configs = cls._get_business_configs()
        
        if business not in configs:
            raise ValueError(f"Unknown business: {business}. Available: {list(configs.keys())}")
        
        config = configs[business]
        
        # 检查环境配置
        if "environments" not in config:
            raise ValueError(f"Business '{business}' has no environments configuration")
        
        if environment not in config["environments"]:
            raise ValueError(f"Environment '{environment}' not found for business '{business}'. Available: {list(config['environments'].keys())}")
        
        env_config = config["environments"][environment]
        sku_config_dict = config["sku"]
        detail_config_dict = config["detail"]
        
        # 合并环境配置和业务配置
        sku_config_dict = {
            **sku_config_dict,
            "base_url": env_config["base_url"],
            "headers": env_config["headers"]
        }
        
        detail_config_dict = {
            **detail_config_dict,
            "base_url": env_config["base_url"],
            "headers": env_config["headers"]
        }
        
        sku_config = SkuQueryConfig.from_dict(sku_config_dict)
        detail_config = DetailQueryConfig.from_dict(detail_config_dict)
        
        return StagingSkuQueryClient(sku_config, detail_config)
    
    @classmethod
    def register_business(cls, name: str, environments: Dict[str, Dict[str, Any]], 
                          sku_config: Dict[str, Any], detail_config: Dict[str, Any]):
        """
        注册新业务配置
        
        Args:
            name: 业务名称
            environments: 环境配置字典，格式: {"staging": {"base_url": "...", "headers": {...}}, "prod": {...}}
            sku_config: SKU查询配置（包含 sku_ids 和 api_path）
            detail_config: Detail查询配置（包含 business、model、level等）
        """
        # 更新内存缓存
        cls._BUSINESS_CONFIGS[name] = {
            "environments": environments,
            "sku": sku_config,
            "detail": detail_config
        }
        
        # 保存到配置文件（只保存业务特定配置，不包含通用配置）
        try:
            config_dir = cls._get_config_dir()
            business_config_dir = config_dir / "businesses"
            config_file = business_config_dir / f"{name}.json"
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 提取业务特定配置（去除通用配置）
            business_only_config = {
                "sku": {
                    "sku_ids": sku_config.get("sku_ids", [])
                },
                "detail": {
                    "business": detail_config.get("business", ""),
                    "model": detail_config.get("model", "")
                }
            }
            
            # 如果业务配置中有自定义的level，也保存
            if "level" in detail_config:
                business_only_config["detail"]["level"] = detail_config["level"]
            
            # 如果业务配置中有 appIds，也保存
            if "appIds" in cls._BUSINESS_CONFIGS[name]:
                business_only_config["appIds"] = cls._BUSINESS_CONFIGS[name]["appIds"]
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(business_only_config, f, indent=2, ensure_ascii=False)
        except FileNotFoundError:
            # 如果配置目录不存在，只更新内存缓存，不保存到文件
            print(f"警告: 配置目录不存在，业务配置 '{name}' 仅保存在内存中")
            print(f"提示: 运行 'sku-config-init' 初始化配置文件")
    
    @classmethod
    def list_businesses(cls) -> List[str]:
        """列出所有已注册的业务"""
        configs = cls._get_business_configs()
        return list(configs.keys())
    
    @classmethod
    def get_sku_ids(cls, business: str) -> List[str]:
        """
        获取业务的SKU ID列表
        
        Args:
            business: 业务名称
            
        Returns:
            SKU ID列表
            
        Raises:
            ValueError: 业务配置不存在
        """
        configs = cls._get_business_configs()
        
        if business not in configs:
            raise ValueError(f"Unknown business: {business}. Available: {list(configs.keys())}")
        
        return configs[business]["sku"].get("sku_ids", [])
    
    @classmethod
    def get_appids(cls, business: str) -> Dict[str, str]:
        """
        获取业务的AppID配置
        
        Args:
            business: 业务名称
            
        Returns:
            AppID字典 {appid: vid}
            
        Raises:
            ValueError: 业务配置不存在
        """
        configs = cls._get_business_configs()
        
        if business not in configs:
            raise ValueError(f"Unknown business: {business}. Available: {list(configs.keys())}")
        
        # 支持 appIds 和 appids 两种字段名（兼容性）
        return configs[business].get("appIds", {})


# 使用示例
if __name__ == "__main__":
    # 获取staging环境的客户端
    client = SkuQueryFactory.get_client("speech-to-text", environment="staging")
    
    # 查询SKU数据（使用配置中的sku_ids）
    vid = 1057686
    from_ts = 1699000000000  # 示例时间戳
    
    # 注意：sku_ids 应该从配置中获取，这里仅作示例
    sku_results = client.query_sku(
        vid=vid,
        from_ts=from_ts,
        sku_ids=["30331", "30332"]
    )
    
    print("SKU Results:", json.dumps(sku_results, indent=2, ensure_ascii=False))
    
    # 查询Detail数据
    detail_results = client.query_detail(vid=vid, from_ts=from_ts)
    print("Detail Results:", json.dumps(detail_results, indent=2, ensure_ascii=False))
    
