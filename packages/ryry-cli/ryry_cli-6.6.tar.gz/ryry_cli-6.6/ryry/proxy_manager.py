import os
import sys
import json
import yaml
import subprocess
import threading
import time
import requests
import zipfile
import tarfile
import hashlib
import platform
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse

class ProxyManager:
    """代理管理器，用于管理clashcore代理"""
    
    def __init__(self, config_path: Optional[str] = None):
        return
        self.config_path = config_path or self._get_default_config_path()
        self.clash_process = None
        self.proxy_enabled = False
        self.config_data = None
        self.clash_binary_path = None
        self.clash_dir = self._get_clash_dir()
        self._load_config()
        
    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, "clash_config.yaml")
    
    def _get_clash_dir(self) -> str:
        """获取clash安装目录"""
        base_path = os.path.dirname(os.path.abspath(__file__))
        clash_dir = os.path.join(base_path, "clash_binary")
        os.makedirs(clash_dir, exist_ok=True)
        return clash_dir
    
    def _get_system_info(self) -> Dict[str, str]:
        """获取系统信息"""
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        # 映射系统架构
        arch_map = {
            'x86_64': 'amd64',
            'amd64': 'amd64',
            'i386': '386',
            'i686': '386',
            'arm64': 'arm64',
            'aarch64': 'arm64',
            'armv7l': 'armv7',
            'armv8l': 'arm64'
        }
        
        arch = arch_map.get(machine, machine)
        
        return {
            'system': system,
            'arch': arch,
            'machine': machine
        }
    
    def _get_clash_download_url(self) -> str:
        """获取clash下载URL"""
        system_info = self._get_system_info()
        system = system_info['system']
        arch = system_info['arch']
        
        # Clash Core 下载地址映射
        base_url = "https://github.com/Dreamacro/clash/releases/download"
        version = "v1.18.0"  # 可以更新到最新版本
        
        if system == "windows":
            filename = f"clash-windows-{arch}-{version}.zip"
        elif system == "darwin":
            filename = f"clash-darwin-{arch}-{version}.gz"
        else:  # linux
            filename = f"clash-linux-{arch}-{version}.gz"
        
        return f"{base_url}/{version}/{filename}"
    
    def _download_file(self, url: str, filepath: str) -> bool:
        """下载文件"""
        try:
            print(f"📥 正在下载: {url}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\r📥 下载进度: {percent:.1f}%", end='', flush=True)
            
            print(f"\n✅ 下载完成: {filepath}")
            return True
            
        except Exception as e:
            print(f"\n❌ 下载失败: {e}")
            return False
    
    def _extract_file(self, archive_path: str, extract_dir: str) -> bool:
        """解压文件"""
        try:
            print(f"📦 正在解压: {archive_path}")
            
            if archive_path.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            elif archive_path.endswith('.gz'):
                import gzip
                import shutil
                
                # 对于.gz文件，直接解压为clash可执行文件
                output_path = os.path.join(extract_dir, 'clash')
                with gzip.open(archive_path, 'rb') as f_in:
                    with open(output_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # 设置执行权限
                os.chmod(output_path, 0o755)
            
            print(f"✅ 解压完成: {extract_dir}")
            return True
            
        except Exception as e:
            print(f"❌ 解压失败: {e}")
            return False
    
    def _install_clash(self) -> bool:
        """安装clash"""
        try:
            # 检查是否已安装
            clash_binary = os.path.join(self.clash_dir, 'clash')
            if sys.platform == "win32":
                clash_binary = os.path.join(self.clash_dir, 'clash.exe')
            
            if os.path.exists(clash_binary):
                # 检查版本
                try:
                    result = subprocess.run([clash_binary, "--version"], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        print(f"✅ Clash已安装: {clash_binary}")
                        self.clash_binary_path = clash_binary
                        return True
                except:
                    pass
            
            # 下载并安装
            download_url = self._get_clash_download_url()
            archive_name = os.path.basename(urlparse(download_url).path)
            archive_path = os.path.join(self.clash_dir, archive_name)
            
            # 下载
            if not self._download_file(download_url, archive_path):
                return False
            
            # 解压
            if not self._extract_file(archive_path, self.clash_dir):
                return False
            
            # 清理下载文件
            try:
                os.remove(archive_path)
            except:
                pass
            
            # 验证安装
            if os.path.exists(clash_binary):
                try:
                    result = subprocess.run([clash_binary, "--version"], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        print(f"✅ Clash安装成功: {clash_binary}")
                        self.clash_binary_path = clash_binary
                        return True
                except Exception as e:
                    print(f"❌ Clash验证失败: {e}")
            
            return False
            
        except Exception as e:
            print(f"❌ 安装Clash失败: {e}")
            return False
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config_data = yaml.safe_load(f)
                print(f"✅ 已加载代理配置文件: {self.config_path}")
            else:
                print(f"⚠️  配置文件不存在: {self.config_path}")
                self._create_default_config()
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """创建默认配置文件"""
        default_config = {
            "port": 7890,
            "socks-port": 7891,
            "allow-lan": True,
            "mode": "rule",
            "log-level": "info",
            "external-controller": "127.0.0.1:9090",
            "proxies": [],
            "proxy-groups": [],
            "rules": [
                "DOMAIN-SUFFIX,google.com,Proxy",
                "DOMAIN-SUFFIX,github.com,Proxy",
                "DOMAIN-SUFFIX,githubusercontent.com,Proxy",
                "DOMAIN-SUFFIX,openai.com,Proxy",
                "DOMAIN-SUFFIX,anthropic.com,Proxy",
                "DOMAIN-SUFFIX,claude.ai,Proxy",
                "GEOIP,CN,DIRECT",
                "MATCH,DIRECT"
            ]
        }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
            self.config_data = default_config
            print(f"✅ 已创建默认配置文件: {self.config_path}")
        except Exception as e:
            print(f"❌ 创建默认配置文件失败: {e}")
    
    def start_proxy(self) -> bool:
        """启动代理服务"""
        if self.proxy_enabled:
            print("✅ 代理服务已在运行")
            return True
            
        try:
            # 确保clash已安装
            if not self.clash_binary_path:
                if not self._install_clash():
                    print("❌ Clash安装失败")
                    return False
            
            # 启动clash进程
            cmd = [self.clash_binary_path, "-f", self.config_path]
            self.clash_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待服务启动
            time.sleep(2)
            
            # 检查服务是否正常启动
            if self._check_proxy_status():
                self.proxy_enabled = True
                print("✅ 代理服务启动成功")
                self._set_system_proxy()
                return True
            else:
                print("❌ 代理服务启动失败")
                self.stop_proxy()
                return False
                
        except Exception as e:
            print(f"❌ 启动代理服务失败: {e}")
            return False
    
    def stop_proxy(self):
        """停止代理服务"""
        if self.clash_process:
            try:
                self.clash_process.terminate()
                self.clash_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.clash_process.kill()
            finally:
                self.clash_process = None
        
        self.proxy_enabled = False
        self._unset_system_proxy()
        print("✅ 代理服务已停止")
    

    
    def _check_proxy_status(self) -> bool:
        """检查代理服务状态"""
        try:
            # 检查HTTP代理
            proxies = {
                'http': 'http://127.0.0.1:7890',
                'https': 'http://127.0.0.1:7890'
            }
            response = requests.get('http://httpbin.org/ip', 
                                  proxies=proxies, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _set_system_proxy(self):
        """设置系统代理"""
        try:
            if sys.platform == "win32":
                # Windows系统代理设置
                import winreg
                
                def set_key(name, value):
                    try:
                        winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                                       r"Software\Microsoft\Windows\CurrentVersion\Internet Settings")
                        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                                     r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                                                     0, winreg.KEY_WRITE)
                        winreg.SetValueEx(registry_key, name, 0, winreg.REG_DWORD, value)
                        winreg.CloseKey(registry_key)
                        return True
                    except WindowsError:
                        return False
                
                set_key("ProxyEnable", 1)
                set_key("ProxyServer", "127.0.0.1:7890")
                
            elif sys.platform == "darwin":
                # macOS系统代理设置
                os.system("networksetup -setwebproxy 'Wi-Fi' 127.0.0.1 7890")
                os.system("networksetup -setsecurewebproxy 'Wi-Fi' 127.0.0.1 7890")
                os.system("networksetup -setsocksfirewallproxy 'Wi-Fi' 127.0.0.1 7891")
                
            else:
                # Linux系统代理设置
                os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
                os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
                os.environ['http_proxy'] = 'http://127.0.0.1:7890'
                os.environ['https_proxy'] = 'http://127.0.0.1:7890'
                
        except Exception as e:
            print(f"⚠️  设置系统代理失败: {e}")
    
    def _unset_system_proxy(self):
        """取消系统代理设置"""
        try:
            if sys.platform == "win32":
                import winreg
                
                def set_key(name, value):
                    try:
                        winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                                       r"Software\Microsoft\Windows\CurrentVersion\Internet Settings")
                        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                                     r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                                                     0, winreg.KEY_WRITE)
                        winreg.SetValueEx(registry_key, name, 0, winreg.REG_DWORD, value)
                        winreg.CloseKey(registry_key)
                        return True
                    except WindowsError:
                        return False
                
                set_key("ProxyEnable", 0)
                
            elif sys.platform == "darwin":
                os.system("networksetup -setwebproxystate 'Wi-Fi' off")
                os.system("networksetup -setsecurewebproxystate 'Wi-Fi' off")
                os.system("networksetup -setsocksfirewallproxystate 'Wi-Fi' off")
                
            else:
                # Linux系统代理设置
                if 'HTTP_PROXY' in os.environ:
                    del os.environ['HTTP_PROXY']
                if 'HTTPS_PROXY' in os.environ:
                    del os.environ['HTTPS_PROXY']
                if 'http_proxy' in os.environ:
                    del os.environ['http_proxy']
                if 'https_proxy' in os.environ:
                    del os.environ['https_proxy']
                    
        except Exception as e:
            print(f"⚠️  取消系统代理失败: {e}")
    
    def get_proxy_info(self) -> Dict[str, Any]:
        """获取代理信息"""
        return {
            "enabled": self.proxy_enabled,
            "config_path": self.config_path,
            "clash_binary": self.clash_binary_path,
            "clash_dir": self.clash_dir,
            "http_proxy": "http://127.0.0.1:7890" if self.proxy_enabled else None,
            "socks_proxy": "socks5://127.0.0.1:7891" if self.proxy_enabled else None
        }
    
    def update_config(self, new_config: Dict[str, Any]):
        """更新代理配置"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(new_config, f, default_flow_style=False, allow_unicode=True)
            self.config_data = new_config
            print("✅ 代理配置已更新")
            
            # 如果代理正在运行，重启服务
            if self.proxy_enabled:
                self.stop_proxy()
                time.sleep(1)
                self.start_proxy()
                
        except Exception as e:
            print(f"❌ 更新代理配置失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        self.stop_proxy()
        # 可以选择是否删除clash二进制文件
        # if self.clash_dir and os.path.exists(self.clash_dir):
        #     import shutil
        #     shutil.rmtree(self.clash_dir)

# # 全局代理管理器实例
proxy_manager = ProxyManager()

def init_proxy():
    """初始化代理服务"""
    return proxy_manager.start_proxy()

def stop_proxy():
    """停止代理服务"""
    proxy_manager.stop_proxy()

def get_proxy_status():
    """获取代理状态"""
    return proxy_manager.get_proxy_info()

def cleanup_proxy():
    """清理代理资源"""
    proxy_manager.cleanup() 