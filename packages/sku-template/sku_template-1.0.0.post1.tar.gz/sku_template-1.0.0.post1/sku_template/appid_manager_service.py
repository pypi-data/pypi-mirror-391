"""
AppID管理HTTP服务
提供AppID的获取、释放和状态查询功能
支持并发获取，解决AppID资源管理问题
"""
import time
import threading
import os
import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, Optional
from flask import Flask, request, jsonify
import argparse


class AppIdManager:
    """AppID管理器"""
    
    def __init__(self):
        """
        初始化AppID管理器
        """
        self.appid_config = {}
        self.appid_status = {}
        self.test_results = {}  # 存储测试用例执行数据 {product_name: {session_id: [test_results]}}
        self.lock = threading.Lock()
    
    def init_product(self, product_name: str, appids: Dict[str, str]) -> Tuple[bool, Dict[str, Any]]:
        """
        初始化或重置产品AppID配置
        
        Args:
            product_name: 产品名称
            appids: AppID配置 {appid: vid}
            
        Returns:
            (success, data): 成功标志和数据
        """
        with self.lock:
            # 更新配置
            self.appid_config[product_name] = appids
            
            # 移除该产品下所有现有的AppID状态
            removed_count = 0
            appids_to_remove = []
            for appid, status in self.appid_status.items():
                if status.get("productName") == product_name:
                    appids_to_remove.append(appid)
                    removed_count += 1
            
            for appid in appids_to_remove:
                del self.appid_status[appid]
            
            # 添加新的AppID状态
            added_count = 0
            for appid, vid in appids.items():
                self.appid_status[appid] = {
                    "starttime": None,
                    "stoptime": None,
                    "productName": product_name,
                    "vid": int(vid)
                }
                added_count += 1
            
            return True, {
                "success": True,
                "productName": product_name,
                "removed_count": removed_count,
                "added_count": added_count,
                "message": f"Product '{product_name}' initialized: removed {removed_count}, added {added_count} appids"
            }
    
    def _is_available(self, appid: str, status: Dict[str, Any]) -> bool:
        """
        判断AppID是否可用
        
        判断规则：
        - starttime=null, stoptime=null → 可用
        - starttime=null, stoptime≠null → 错误状态（不应该存在）
        - starttime≠null, stoptime=null → 使用中，不可用
        - starttime≠null, stoptime≠null → 检查stoptime是否在当前小时内
        """
        starttime = status.get("starttime")
        stoptime = status.get("stoptime")
        
        # 未使用过
        if starttime is None and stoptime is None:
            return True
        
        # 错误状态
        if starttime is None and stoptime is not None:
            return False
        
        # 使用中
        if starttime is not None and stoptime is None:
            return False
        
        # 使用结束，检查是否在当前小时内
        if starttime is not None and stoptime is not None:
            current_hour = self._get_current_hour()
            stoptime_hour = self._get_hour_of_timestamp(stoptime)
            # 严格按小时判断：stoptime所在小时 < 当前小时 → 可用
            # 即：stoptime在之前的小时，现在进入新小时，可以再次使用
            # 如果stoptime所在小时 == 当前小时，说明在当前小时内使用过，不可重复使用
            is_available = stoptime_hour < current_hour
            return is_available
        
        # 理论上不会到达这里，但为了类型检查，返回False
        return False
    
    def _get_current_hour(self) -> int:
        """获取当前小时（时间戳，毫秒）"""
        now = datetime.now()
        # 获取当前小时的开始时间
        hour_start = now.replace(minute=0, second=0, microsecond=0)
        return int(hour_start.timestamp() * 1000)
    
    def _get_hour_of_timestamp(self, timestamp: int) -> int:
        """获取时间戳所在的小时（时间戳，毫秒）"""
        dt = datetime.fromtimestamp(timestamp / 1000)
        hour_start = dt.replace(minute=0, second=0, microsecond=0)
        return int(hour_start.timestamp() * 1000)
    
    def _get_next_hour_start(self) -> int:
        """获取下一个小时的开始时间（时间戳，毫秒）"""
        now = datetime.now()
        next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        return int(next_hour.timestamp() * 1000)
    
    def acquire_appid(self, product_name: str = "default", force_acquire: bool = False) -> Tuple[bool, Dict[str, Any]]:
        """
        获取可用的AppID
        
        Args:
            product_name: 产品名称，用于隔离不同业务的AppID
            force_acquire: 是否强制获取（忽略小时内使用检查），默认为False
                         如果为True，即使AppID在当前小时内使用过，也可以直接获取
                         但starttime和stoptime依旧要填
            
        Returns:
            (success, data): 成功标志和数据
        """
        with self.lock:
            # 遍历找可用AppID（只查找指定产品的AppID）
            for appid, status in self.appid_status.items():
                if status.get("productName") == product_name:
                    # 如果 force_acquire=True，只要AppID不在使用中（stoptime != None），就可以获取
                    # 如果 force_acquire=False，需要检查是否可用（包括小时内使用检查）
                    if force_acquire:
                        # 强制获取：只要不在使用中（stoptime != None），就可以获取
                        # 即使在当前小时内使用过，也可以直接获取
                        if status.get("stoptime") is not None:
                            # 已释放，可以获取（忽略小时内使用检查）
                            current_time = int(time.time() * 1000)
                            vid = status.get("vid")  # 保留vid字段
                            self.appid_status[appid] = {
                                "starttime": current_time,
                                "stoptime": None,
                                "productName": product_name,
                                "vid": vid  # 保留vid字段
                            }
                            
                            return True, {
                                "appid": appid,
                                "vid": vid,
                                "productName": product_name,
                                "starttime": current_time
                            }
                    else:
                        # 正常获取：需要检查是否可用（包括小时内使用检查）
                        if self._is_available(appid, status):
                            # 立即标记为使用中（保留vid字段）
                            current_time = int(time.time() * 1000)
                            vid = status.get("vid")  # 保留vid字段
                            self.appid_status[appid] = {
                                "starttime": current_time,
                                "stoptime": None,
                                "productName": product_name,
                                "vid": vid  # 保留vid字段
                            }
                            
                            return True, {
                                "appid": appid,
                                "vid": vid,
                                "productName": product_name,
                                "starttime": current_time
                            }
            
            # 所有AppID都不可用，检查是否需要等待（只检查指定产品的AppID）
            # 如果 force_acquire=True，但所有AppID都在使用中，返回等待
            current_hour = self._get_current_hour()
            all_in_current_hour = True
            has_released_appid = False  # 是否有已释放的AppID
            
            for status in self.appid_status.values():
                if status.get("productName") == product_name:
                    stoptime = status.get("stoptime")
                    if stoptime is not None:
                        # 有已释放的AppID
                        has_released_appid = True
                        stoptime_hour = self._get_hour_of_timestamp(stoptime)
                        if stoptime_hour < current_hour:
                            # 有AppID的stoptime在之前的小时，应该可用
                            # 但遍历时没找到，可能是判断逻辑有问题，返回waiting让其重试
                            all_in_current_hour = False
                            break
                    elif status.get("starttime") is not None:
                        # 正在使用中的AppID
                        pass
            
            if all_in_current_hour and has_released_appid:
                # 所有已释放AppID的stoptime都在当前小时内，需要等待到下个小时
                next_hour_start = self._get_next_hour_start()
                current_time = int(time.time() * 1000)
                wait_seconds = (next_hour_start - current_time) / 1000
                
                return False, {
                    "error": "no_available",
                    "retry_after": min(int(wait_seconds), 300),  # 最多等待5分钟
                    "message": f"All appids for product '{product_name}' are in use for current hour, wait {wait_seconds:.0f}s until next hour"
                }
            else:
                # 其他情况，短时间重试
                # 包括：1) 所有AppID都在使用中 2) 有AppID应该可用但判断可能有问题
                return False, {
                    "error": "waiting",
                    "retry_after": 60,
                    "message": f"All appids for product '{product_name}' are in use, retry in 60s"
                }
    
    def release_appid(self, appid: str, product_name: str = "default") -> Tuple[bool, Dict[str, Any]]:
        """
        释放AppID
        
        Args:
            appid: 要释放的AppID
            product_name: 产品名称，用于验证AppID归属
            
        Returns:
            (success, data): 成功标志和数据
        """
        with self.lock:
            if appid not in self.appid_status:
                return False, {"error": "appid_not_found", "message": f"AppID {appid} not found"}
            
            status = self.appid_status[appid]
            if status.get("productName") != product_name:
                return False, {"error": "product_mismatch", "message": f"AppID {appid} belongs to product '{status.get('productName')}', not '{product_name}'"}
            
            if status.get("stoptime") is not None:
                return False, {"error": "already_released", "message": f"AppID {appid} already released"}
            
            # 标记为已释放（保留vid字段）
            current_time = int(time.time() * 1000)
            vid = status.get("vid")  # 保留vid字段
            self.appid_status[appid] = {
                "starttime": status.get("starttime"),
                "stoptime": current_time,
                "productName": product_name,
                "vid": vid  # 保留vid字段
            }
            
            return True, {
                "success": True,
                "stoptime": current_time,
                "productName": product_name,
                "message": f"AppID {appid} released successfully"
            }
    
    def get_status(self, product_name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取AppID状态统计和详细信息
        
        Args:
            product_name: 产品名称，如果指定则只统计该产品的AppID
            
        Returns:
            状态统计信息和每个AppID的详细信息
        """
        with self.lock:
            total = 0
            available = 0
            in_use = 0
            appid_details = []  # 存储每个AppID的详细信息
            
            # 获取当前小时，用于判断可用性
            current_hour = self._get_current_hour()
            
            for appid, status in self.appid_status.items():
                # 如果指定了产品名称，只统计该产品的AppID
                if product_name and status.get("productName") != product_name:
                    continue
                
                total += 1
                
                # 判断状态
                is_available = self._is_available(appid, status)
                starttime = status.get("starttime")
                stoptime = status.get("stoptime")
                
                # 计算stoptime所在的小时（如果存在）
                stoptime_hour = None
                if stoptime is not None:
                    stoptime_hour = self._get_hour_of_timestamp(stoptime)
                
                if is_available:
                    status_str = "available"
                    available += 1
                elif stoptime is None:
                    status_str = "in_use"
                    in_use += 1
                else:
                    # 有stoptime，判断是否在当前小时内
                    if stoptime_hour == current_hour:
                        # 在当前小时内使用过，被视为"在当前小时内已使用"
                        status_str = "used_in_current_hour"
                        in_use += 1  # 统计上也算作使用中
                    else:
                        # 在之前的小时使用过，已释放
                        status_str = "released"
                
                # 构建AppID详细信息
                appid_info = {
                    "appid": appid,
                    "vid": status.get("vid"),
                    "productName": status.get("productName"),
                    "starttime": starttime,
                    "stoptime": stoptime,
                    "status": status_str,
                    "is_available": is_available,
                    "stoptime_hour": stoptime_hour,  # stoptime所在的小时（时间戳，毫秒）
                    "current_hour": current_hour  # 当前小时（时间戳，毫秒）
                }
                appid_details.append(appid_info)
            
            result = {
                "total": total,
                "available": available,
                "in_use": in_use,
                "released": total - available - in_use,
                "appids": appid_details  # 所有AppID的详细信息
            }
            
            if product_name:
                result["productName"] = product_name
            
            return result
    
    def store_test_result(self, product_name: str, session_id: str, test_data: Dict[str, Any]) -> None:
        """
        存储测试用例执行数据
        
        Args:
            product_name: 产品名称（业务类型）
            session_id: 测试会话ID（用于区分不同的测试会话，如pytest worker进程）
            test_data: 测试用例数据字典
        """
        with self.lock:
            # 按业务类型组织数据
            if product_name not in self.test_results:
                self.test_results[product_name] = {}
            
            if session_id not in self.test_results[product_name]:
                self.test_results[product_name][session_id] = []
            
            # 添加时间戳（如果test_data中没有）
            if "_stored_at" not in test_data:
                test_data["_stored_at"] = int(time.time() * 1000)  # 毫秒时间戳
            
            self.test_results[product_name][session_id].append(test_data)
    
    def get_test_results(self, product_name: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取测试用例执行数据
        
        Args:
            product_name: 产品名称（业务类型），如果指定则只返回该业务的数据，否则返回所有业务的数据
            session_id: 测试会话ID，如果指定则只返回该会话的数据，否则返回所有会话的数据
            
        Returns:
            测试结果数据字典
        """
        with self.lock:
            if product_name:
                # 返回指定业务的数据
                business_results = self.test_results.get(product_name, {})
                
                if session_id:
                    # 返回指定业务和会话的数据
                    results = business_results.get(session_id, [])
                    return {
                        "product_name": product_name,
                        "session_id": session_id,
                        "results": results
                    }
                else:
                    # 返回指定业务的所有会话数据
                    all_results = []
                    for results in business_results.values():
                        all_results.extend(results)
                    
                    return {
                        "product_name": product_name,
                        "results": all_results
                    }
            else:
                # 返回所有业务的数据
                all_results = []
                for business_results in self.test_results.values():
                    for results in business_results.values():
                        all_results.extend(results)
                
                return {
                    "results": all_results
                }
    
    def clear_test_results(self, product_name: Optional[str] = None, session_id: Optional[str] = None) -> None:
        """
        清除测试用例执行数据
        
        Args:
            product_name: 产品名称（业务类型），如果指定则只清除该业务的数据，否则清除所有业务的数据
            session_id: 测试会话ID，如果指定则只清除该会话的数据，否则清除所有会话的数据
        """
        with self.lock:
            if product_name:
                if product_name not in self.test_results:
                    return
                
                business_results = self.test_results[product_name]
                
                if session_id:
                    # 清除指定业务和会话的数据
                    if session_id in business_results:
                        del business_results[session_id]
                    
                    # 如果该业务下没有会话了，删除业务
                    if not business_results:
                        del self.test_results[product_name]
                else:
                    # 清除指定业务的所有会话数据
                    del self.test_results[product_name]
            else:
                # 清除所有业务的数据
                self.test_results.clear()
    
    def clear_old_test_results(self, days: int = 14) -> Dict[str, Any]:
        """
        清除指定天数前的测试用例执行数据
        
        Args:
            days: 保留最近N天的数据，默认14天（2周）
            
        Returns:
            清理统计信息
        """
        from datetime import datetime, timedelta
        
        with self.lock:
            cutoff_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)  # 毫秒时间戳
            total_removed = 0
            total_kept = 0
            removed_by_product = {}
            
            # 遍历所有业务
            products_to_remove = []
            for product_name, business_results in list(self.test_results.items()):
                sessions_to_remove = []
                product_removed = 0
                product_kept = 0
                
                # 遍历所有会话
                for session_id, results in list(business_results.items()):
                    # 过滤出需要保留的数据（时间戳 >= cutoff_time）
                    kept_results = []
                    for result in results:
                        stored_at = result.get("_stored_at", 0)
                        if stored_at >= cutoff_time:
                            kept_results.append(result)
                            product_kept += 1
                        else:
                            product_removed += 1
                    
                    # 如果该会话还有数据，更新；否则标记为删除
                    if kept_results:
                        business_results[session_id] = kept_results
                    else:
                        sessions_to_remove.append(session_id)
                
                # 删除空的会话
                for session_id in sessions_to_remove:
                    del business_results[session_id]
                
                # 如果该业务下没有会话了，标记为删除
                if not business_results:
                    products_to_remove.append(product_name)
                
                total_removed += product_removed
                total_kept += product_kept
                if product_removed > 0:
                    removed_by_product[product_name] = product_removed
            
            # 删除空的业务
            for product_name in products_to_remove:
                del self.test_results[product_name]
            
            return {
                "cutoff_time": cutoff_time,
                "cutoff_date": datetime.fromtimestamp(cutoff_time / 1000).isoformat(),
                "days": days,
                "total_removed": total_removed,
                "total_kept": total_kept,
                "removed_by_product": removed_by_product
            }
    


# Flask应用
app = Flask(__name__)

# 全局AppID管理器实例
appid_manager = None

# 全局认证Token
AUTH_TOKEN = "npYXxclHVCN2wvRWJeW57fTsCXz0r2GnFvxdS5ve5eJxrqFYTCQw03uFKwC-T7n0"

# 定时清理任务
cleanup_thread = None
cleanup_running = False


def generate_auth_token(length: int = 64) -> str:
    """
    生成安全的认证token
    
    Args:
        length: token长度（默认64字符，推荐32-128）
        
    Returns:
        随机生成的token字符串
    """
    # 使用大小写字母、数字和部分特殊字符
    alphabet = string.ascii_letters + string.digits + "-_"
    token = ''.join(secrets.choice(alphabet) for _ in range(length))
    return token


def cleanup_old_test_results():
    """清理2周前的测试结果数据"""
    global appid_manager
    if appid_manager is None:
        return
    
    try:
        result = appid_manager.clear_old_test_results(days=14)
        if result["total_removed"] > 0:
            print(f"[Cleanup] 清理了 {result['total_removed']} 条2周前的测试数据，保留了 {result['total_kept']} 条")
            if result["removed_by_product"]:
                for product, count in result["removed_by_product"].items():
                    print(f"  - {product}: {count} 条")
    except Exception as e:
        print(f"[Cleanup Error] 清理测试数据时出错: {str(e)}")


def cleanup_task_worker():
    """定时清理任务的工作线程"""
    global cleanup_running
    while cleanup_running:
        try:
            # 每天凌晨2点执行清理（避免影响正常使用）
            # 这里简化为每24小时执行一次
            time.sleep(24 * 3600)  # 24小时
            if cleanup_running:
                cleanup_old_test_results()
        except Exception as e:
            print(f"[Cleanup Task Error] {str(e)}")
            # 出错后等待1小时再重试
            time.sleep(3600)


def start_cleanup_task():
    """启动定时清理任务"""
    global cleanup_thread, cleanup_running
    
    if cleanup_thread is not None and cleanup_thread.is_alive():
        return  # 任务已在运行
    
    cleanup_running = True
    cleanup_thread = threading.Thread(target=cleanup_task_worker, daemon=True)
    cleanup_thread.start()
    print("✓ 定时清理任务已启动（每24小时清理一次2周前的测试数据）")


def stop_cleanup_task():
    """停止定时清理任务"""
    global cleanup_running, cleanup_thread
    
    cleanup_running = False
    if cleanup_thread is not None:
        cleanup_thread.join(timeout=5)
    print("定时清理任务已停止")


def init_appid_manager():
    """初始化AppID管理器"""
    global appid_manager
    
    appid_manager = AppIdManager()
    print("AppID Manager initialized (empty)")
    
    # 启动定时清理任务
    start_cleanup_task()


def verify_auth():
    """
    验证请求的认证信息
    支持两种方式：
    1. Authorization: Bearer <token>
    2. X-API-Key: <token>
    
    Returns:
        None if auth valid, Response object if auth invalid
    """
    if AUTH_TOKEN is None:
        # 如果没有配置token，不需要认证
        return None
    
    # 从请求头获取token
    auth_header = request.headers.get('Authorization', '')
    api_key = request.headers.get('X-API-Key', '')
    
    token = None
    
    # 尝试从 Authorization header 获取 Bearer token
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]  # 去掉 'Bearer ' 前缀
    
    # 或者从 X-API-Key header 获取
    if not token and api_key:
        token = api_key
    
    # 验证token
    if not token:
        return jsonify({
            "error": "unauthorized",
            "message": "Authentication required. Please provide token via 'Authorization: Bearer <token>' or 'X-API-Key: <token>' header"
        }), 401
    
    if token != AUTH_TOKEN:
        return jsonify({
            "error": "unauthorized",
            "message": "Invalid authentication token"
        }), 401
    
    return None


@app.before_request
def check_auth():
    """请求前检查认证（health接口除外）"""
    # health接口不需要认证
    if request.path == '/health':
        return None
    
    # 其他所有接口都需要认证
    return verify_auth()


@app.route('/api/appid/acquire', methods=['POST'])
def acquire_appid():
    """获取可用的AppID"""
    if appid_manager is None:
        return jsonify({"error": "service_unavailable", "message": "AppID Manager not initialized"}), 500
    
    try:
        data = request.get_json() or {}
        product_name = data.get('productName')
        force_acquire = data.get('forceAcquire', False)  # 默认为False，保持向后兼容
        
        if not product_name:
            return jsonify({"error": "missing_product_name", "message": "productName is required"}), 400
        
        success, result = appid_manager.acquire_appid(product_name, force_acquire=force_acquire)
        if success:
            return jsonify(result), 200
        else:
            return jsonify(result), 202  # Accepted but waiting
    except Exception as e:
        return jsonify({"error": "internal_error", "message": str(e)}), 500


@app.route('/api/appid/release', methods=['POST'])
def release_appid():
    """释放AppID"""
    if appid_manager is None:
        return jsonify({"error": "service_unavailable", "message": "AppID Manager not initialized"}), 500
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "missing_data", "message": "Request body is required"}), 400
        
        appid = data.get('appid')
        product_name = data.get('productName')
        
        if not appid:
            return jsonify({"error": "missing_appid", "message": "appid is required"}), 400
        
        if not product_name:
            return jsonify({"error": "missing_product_name", "message": "productName is required"}), 400
        
        success, result = appid_manager.release_appid(appid, product_name)
        
        if success:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({"error": "internal_error", "message": str(e)}), 500


@app.route('/api/appid/status', methods=['GET'])
def get_status():
    """获取AppID状态统计"""
    if appid_manager is None:
        return jsonify({"error": "service_unavailable", "message": "AppID Manager not initialized"}), 500
    
    try:
        product_name = request.args.get('productName')
        status = appid_manager.get_status(product_name)
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"error": "internal_error", "message": str(e)}), 500


@app.route('/api/appid/init', methods=['POST'])
def init_product():
    """初始化或重置产品AppID配置"""
    if appid_manager is None:
        return jsonify({"error": "service_unavailable", "message": "AppID Manager not initialized"}), 500
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "missing_data", "message": "Request body is required"}), 400
        
        product_name = data.get('productName')
        appids = data.get('appids')
        
        if not product_name:
            return jsonify({"error": "missing_product_name", "message": "productName is required"}), 400
        
        if not appids:
            return jsonify({"error": "missing_appids", "message": "appids is required"}), 400
        
        success, result = appid_manager.init_product(product_name, appids)
        if success:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({"error": "internal_error", "message": str(e)}), 500


@app.route('/api/test/result', methods=['POST'])
def store_test_result():
    """存储测试用例执行数据"""
    if appid_manager is None:
        return jsonify({"error": "service_unavailable"}), 500
    
    data = request.get_json() or {}
    product_name = data.get('product_name') or data.get('productName')
    session_id = data.get('session_id')
    test_data = data.get('test_data')
    
    if not product_name or not session_id or test_data is None:
        return jsonify({"error": "missing_required_fields"}), 400
    
    appid_manager.store_test_result(product_name, session_id, test_data)
    return jsonify({"success": True}), 200


@app.route('/api/test/results', methods=['GET'])
def get_test_results():
    """获取测试用例执行数据"""
    if appid_manager is None:
        return jsonify({"error": "service_unavailable"}), 500
    
    product_name = request.args.get('product_name') or request.args.get('productName')
    session_id = request.args.get('session_id')
    results = appid_manager.get_test_results(product_name, session_id)
    return jsonify(results), 200


@app.route('/api/test/results/clear', methods=['POST'])
def clear_test_results():
    """清除测试用例执行数据"""
    if appid_manager is None:
        return jsonify({"error": "service_unavailable"}), 500
    
    data = request.get_json() or {}
    product_name = data.get('product_name') or data.get('productName')
    session_id = data.get('session_id')
    
    appid_manager.clear_test_results(product_name, session_id)
    return jsonify({"success": True}), 200


@app.route('/api/test/results/cleanup', methods=['POST'])
def cleanup_old_results():
    """手动触发清理2周前的测试数据"""
    if appid_manager is None:
        return jsonify({"error": "service_unavailable"}), 500
    
    try:
        data = request.get_json() or {}
        days = data.get('days', 14)  # 默认14天（2周）
        
        result = appid_manager.clear_old_test_results(days=days)
        return jsonify({
            "success": True,
            "result": result
        }), 200
    except Exception as e:
        return jsonify({"error": "internal_error", "message": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({"status": "healthy", "timestamp": int(time.time() * 1000)}), 200


def main():
    """主函数"""
    global AUTH_TOKEN
    
    parser = argparse.ArgumentParser(description='AppID Manager Service')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0 for external access, use 127.0.0.1 for localhost only)')
    parser.add_argument('--port', type=int, default=8888, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--auth-token', default=None, 
                       help='Authentication token (or set APPID_AUTH_TOKEN env var). If not set, authentication is disabled.')
    parser.add_argument('--generate-token', action='store_true',
                       help='Generate a secure authentication token and exit')
    parser.add_argument('--token-length', type=int, default=64,
                       help='Token length when using --generate-token (default: 64, recommended: 32-128)')
    
    args = parser.parse_args()
    
    # 如果只是生成token，生成后退出
    if args.generate_token:
        token = generate_auth_token(args.token_length)
        print("\n" + "="*70)
        print("Generated Authentication Token:")
        print("="*70)
        print(token)
        print("="*70)
        print("\nUsage examples:")
        print(f"  # Start service with this token:")
        print(f"  python3.11 appid_manager_service.py --auth-token \"{token}\"")
        print(f"\n  # Or set environment variable:")
        print(f"  export APPID_AUTH_TOKEN=\"{token}\"")
        print(f"  python3.11 appid_manager_service.py")
        print("\n" + "="*70)
        return
    
    # 设置认证token（优先使用命令行参数，其次使用环境变量）
    AUTH_TOKEN = args.auth_token or os.environ.get('APPID_AUTH_TOKEN')
    
    # 初始化AppID管理器
    init_appid_manager()
    
    print(f"Starting AppID Manager Service on {args.host}:{args.port}")
    
    if AUTH_TOKEN:
        print(f"✓ Authentication enabled (token configured)")
        print("  All API requests require authentication via:")
        print("    - Authorization: Bearer <token>")
        print("    - or X-API-Key: <token>")
    else:
        print("⚠ Authentication disabled (no token configured)")
        print("  WARNING: Service is accessible without authentication!")
    
    print("\nAvailable endpoints:")
    print("  【AppID管理接口】")
    print("  POST /api/appid/acquire - Get available appid (requires auth)")
    print("  POST /api/appid/release - Release appid (requires auth)")
    print("  GET  /api/appid/status  - Get status (requires auth)")
    print("  POST /api/appid/init    - Initialize product (requires auth)")
    print("  【测试结果存储接口】")
    print("  POST /api/test/result   - Store test result (requires auth)")
    print("  GET  /api/test/results   - Get test results (JSON, requires auth)")
    print("  POST /api/test/results/clear - Clear test results (requires auth)")
    print("  【通用接口】")
    print("  GET  /health            - Health check (no auth required)")
    
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
