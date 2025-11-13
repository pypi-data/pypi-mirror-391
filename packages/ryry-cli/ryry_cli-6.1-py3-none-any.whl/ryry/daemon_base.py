import sys
import os
import json
import time
import signal
import threading
from typing import Optional, Dict, Any
from ryry import ryry_webapi
import platform

class SimpleDaemonBase:
    """
    简化的Daemon基类
    
    用户需要实现的方法：
    - initialize(): 初始化资源
    - loop_function(): 循环执行的任务（可选）
    - on_stop(): 清理资源（可选）
    """
    
    def __init__(self, widget_id: str):
        # 基础配置
        self.widget_id = widget_id
        self.widget_name = "???"
        self.running = False
        
        # 配置加载
        self._load_config()
        
        print(f"【{self.widget_name}】Daemon实例创建完成", file=sys.stderr)

    def _load_config(self):
        """加载配置文件"""
        try:
            self._script_path = os.path.abspath(sys.modules[self.__class__.__module__].__file__)
            self.base_path = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser("~/.ryry")
            config_path = os.path.join(os.path.dirname(self._script_path), "config.json")
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.timeout = config.get("timeout", 600)
                    self.widget_name = config.get("name", self.widget_name)
            else:
                self.timeout = 600
        except Exception as e:
            print(f"配置加载失败: {e}", file=sys.stderr)
            self.timeout = 600

    # ==================== 生命周期方法 ====================
    
    def initialize(self):
        """
        初始化方法 - 子类可选实现
        在这里进行资源初始化，如数据库连接、模型加载等
        """
        pass

    def loop_function(self):
        """
        循环执行的方法 - 子类可选实现
        每秒调用一次，用于定时任务、心跳等
        """
        pass

    def on_stop(self):
        """
        停止时的清理方法 - 子类可选实现
        在这里进行资源清理，如关闭连接、保存状态等
        """
        pass

    def wait_for_tasks_completion(self, timeout: int = 30) -> bool:
        """
        等待任务完成的方法 - 子类可选实现
        返回True表示所有任务已完成，False表示超时
        """
        return True

    # ==================== 通信方法 ====================
    
    def send_ready_signal(self):
        """发送就绪信号"""
        try:
            ready_file = os.path.join(self.base_path, f"daemon_ready_{self.widget_id}.json")
            ready_data = {
                "accept_tasks": False,
                "timestamp": time.time(),
                "pid": os.getpid()
            }
            with open(ready_file, 'w', encoding='utf-8') as f:
                json.dump(ready_data, f)
            print(f"【{self.widget_name}】就绪信号已发送", file=sys.stderr)
        except Exception as e:
            print(f"发送就绪信号失败: {e}", file=sys.stderr)

    def send_stop_signal(self):
        """发送停止信号"""
        try:
            stop_file = os.path.join(self.base_path, f"daemon_stopped_{self.widget_id}.json")
            with open(stop_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "widget_id": self.widget_id,
                    "stopped_at": time.time(),
                    "pid": os.getpid()
                }, f)
        except Exception as e:
            print(f"发送停止信号失败: {e}", file=sys.stderr)

    def process_command(self):
        """处理命令文件"""
        cmd_file = os.path.join(self.base_path, f"daemon_cmd_{self.widget_id}.json")
        if not os.path.exists(cmd_file):
            return
        
        try:
            with open(cmd_file, 'r', encoding='utf-8') as f:
                command = json.load(f)
            os.remove(cmd_file)
            
            cmd_type = command.get("type")
            if cmd_type == "task":
                self._handle_task_command(command)
            elif cmd_type == "health":
                self._handle_health_command(command)
            elif cmd_type == "stop":
                self._handle_stop_command(command)
                
        except Exception as e:
            print(f"处理命令失败: {e}", file=sys.stderr)

    def _handle_task_command(self, command: Dict[str, Any]):
        """处理任务命令"""
        task_data = command.get("data", {})
        timeout = command.get("timeout", self.timeout)
        
        try:
            result = self.process_task(task_data, timeout)
            self._send_response({
                "type": "task_result",
                "task_id": command.get("task_id"),
                "success": True,
                "data": result
            })
        except Exception as e:
            self._send_response({
                "type": "task_result", 
                "task_id": command.get("task_id"),
                "success": False,
                "error": str(e),
                "data": {"result": [], "status": 1, "message": str(e)}
            })

    def _handle_health_command(self, command: Dict[str, Any]):
        """处理健康检查命令"""
        health = self.health_check()
        self._send_response({
            "type": "health_result",
            "data": health
        })

    def _handle_stop_command(self, command: Dict[str, Any]):
        """处理停止命令"""
        self.running = False
        self._send_response({
            "type": "stop_result",
            "success": True
        })

    def _send_response(self, response: Dict[str, Any]):
        """发送响应"""
        try:
            result_file = os.path.join(self.base_path, f"daemon_result_{self.widget_id}.json")
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(response, f)
        except Exception as e:
            print(f"发送响应失败: {e}", file=sys.stderr)

    # ==================== 子类可选重写的方法 ====================
    
    def process_task(self, task_data: Dict[str, Any], timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        处理短链任务 - 子类可选实现
        默认返回空结果
        """
        return {
            "result": [{"type": "text", "content": [f"Processed: {task_data}"]}],
            "status": 0,
            "message": "Success"
        }

    def health_check(self) -> Dict[str, Any]:
        """
        健康检查 - 子类可选重写
        """
        return {
            "healthy": True,
            "state": "running" if self.running else "stopped",
            "accept_tasks": False,
            "timestamp": time.time()
        }

    # ==================== 控制方法 ====================
    
    def run(self):
        """
        运行daemon的主入口方法
        """
        try:
            # 初始化
            self.initialize()
            
            # 发送就绪信号
            self.send_ready_signal()
            
            # 主循环
            self.running = True
            last_status_report_time = 0  # 上次状态上报时间
            status_report_interval = 60  # 状态上报间隔（秒）
            
            while self.running:
                try:
                    # 处理命令
                    self.process_command()
                    
                    # 执行循环函数
                    self.loop_function()
                    
                    # 每分钟报告一次状态
                    current_time = time.time()
                    if current_time - last_status_report_time >= status_report_interval:
                        ryry_webapi.widgetStatusReport(self.widget_id, self.health_check())
                        last_status_report_time = current_time
                    
                    time.sleep(1)
                except KeyboardInterrupt:
                    print(f"【{self.widget_name}】收到KeyboardInterrupt", file=sys.stderr)
                    break
                except Exception as e:
                    print(f"主循环异常: {e}", file=sys.stderr)
                    time.sleep(5)  # 异常后等待5秒再继续
            
            # 等待任务完成
            print(f"【{self.widget_name}】等待任务完成...", file=sys.stderr)
            tasks_completed = self.wait_for_tasks_completion(timeout=60)
            if not tasks_completed:
                print(f"【{self.widget_name}】任务等待超时，强制停止", file=sys.stderr)
            
            # 清理
            self.on_stop()
            
        except Exception as e:
            print(f"运行异常: {e}", file=sys.stderr)
        finally:
            # 发送停止信号
            self.send_stop_signal()
            print(f"【{self.widget_name}】进程终止", file=sys.stderr) 