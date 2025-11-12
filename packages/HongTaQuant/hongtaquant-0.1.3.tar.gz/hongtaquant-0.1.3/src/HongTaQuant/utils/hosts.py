"""Hosts 文件管理工具类

提供跨平台的 hosts 文件读取、修改、备份和恢复功能。
支持 Windows、Linux 和 macOS 系统。

Example:
    >>> from HongTaQuant.utils import HostsManager
    >>> 
    >>> # 添加 hosts 映射
    >>> HostsManager.add_host("120.253.157.163", "api.hongtaquant.com")
    >>> 
    >>> # 移除 hosts 映射
    >>> HostsManager.remove_host("api.hongtaquant.com")
    >>> 
    >>> # 备份 hosts 文件
    >>> HostsManager.backup()
    >>> 
    >>> # 恢复 hosts 文件
    >>> HostsManager.restore()
"""

from __future__ import annotations

import os
import platform
import shutil
from pathlib import Path
from typing import Any


class HostsManager:
    """Hosts 文件管理器
    
    提供跨平台的 hosts 文件操作功能，包括添加、删除、备份和恢复。
    """
    
    # 标记注释，用于识别由本工具添加的条目
    MARKER = "# Added by HongTaQuant"
    
    @staticmethod
    def _get_hosts_path() -> Path:
        """获取 hosts 文件路径
        
        Returns:
            hosts 文件的 Path 对象
        """
        system = platform.system()
        if system == "Windows":
            return Path(r"C:\Windows\System32\drivers\etc\hosts")
        else:  # Linux, macOS, etc.
            return Path("/etc/hosts")
    
    @staticmethod
    def _get_backup_path() -> Path:
        """获取备份文件路径
        
        Returns:
            备份文件的 Path 对象
        """
        hosts_path = HostsManager._get_hosts_path()
        return hosts_path.with_suffix(".backup")
    
    @staticmethod
    def _check_permission() -> None:
        """检查是否有修改 hosts 文件的权限
        
        Raises:
            PermissionError: 如果没有足够的权限
        """
        hosts_path = HostsManager._get_hosts_path()
        if not os.access(hosts_path, os.W_OK):
            system = platform.system()
            if system == "Windows":
                msg = "需要管理员权限。请以管理员身份运行程序。"
            else:
                msg = "需要 root 权限。请使用 sudo 运行程序。"
            raise PermissionError(msg)
    
    @staticmethod
    def backup() -> Path:
        """备份当前的 hosts 文件
        
        Returns:
            备份文件的路径
            
        Raises:
            PermissionError: 如果没有足够的权限
            IOError: 如果备份失败
        """
        HostsManager._check_permission()
        
        hosts_path = HostsManager._get_hosts_path()
        backup_path = HostsManager._get_backup_path()
        
        try:
            shutil.copy2(hosts_path, backup_path)
            return backup_path
        except Exception as e:
            raise OSError(f"备份 hosts 文件失败: {e}") from e
    
    @staticmethod
    def restore() -> None:
        """从备份恢复 hosts 文件
        
        Raises:
            FileNotFoundError: 如果备份文件不存在
            PermissionError: 如果没有足够的权限
            IOError: 如果恢复失败
        """
        HostsManager._check_permission()
        
        hosts_path = HostsManager._get_hosts_path()
        backup_path = HostsManager._get_backup_path()
        
        if not backup_path.exists():
            raise FileNotFoundError(f"备份文件不存在: {backup_path}")
        
        try:
            shutil.copy2(backup_path, hosts_path)
        except Exception as e:
            raise OSError(f"恢复 hosts 文件失败: {e}") from e
    
    @staticmethod
    def read() -> list[str]:
        """读取 hosts 文件内容
        
        Returns:
            hosts 文件的所有行（包含换行符）
            
        Raises:
            IOError: 如果读取失败
        """
        hosts_path = HostsManager._get_hosts_path()
        
        try:
            with open(hosts_path, encoding="utf-8") as f:
                return f.readlines()
        except Exception as e:
            raise OSError(f"读取 hosts 文件失败: {e}") from e
    
    @staticmethod
    def add_host(ip: str, hostname: str, comment: str = "") -> None:
        """添加或更新 hosts 映射
        
        如果主机名已存在，则更新其 IP 地址。
        
        Args:
            ip: IP 地址
            hostname: 主机名
            comment: 可选的注释说明
            
        Raises:
            PermissionError: 如果没有足够的权限
            IOError: 如果操作失败
            ValueError: 如果参数无效
        """
        if not ip or not hostname:
            raise ValueError("IP 地址和主机名不能为空")
        
        HostsManager._check_permission()
        
        # 先移除已存在的条目
        HostsManager.remove_host(hostname, silent=True)
        
        # 添加新条目
        hosts_path = HostsManager._get_hosts_path()
        try:
            with open(hosts_path, "a", encoding="utf-8") as f:
                entry = f"{ip}\t{hostname}"
                if comment:
                    entry += f"  # {comment}"
                entry += f"  {HostsManager.MARKER}\n"
                f.write(entry)
        except Exception as e:
            raise OSError(f"添加 hosts 条目失败: {e}") from e
    
    @staticmethod
    def remove_host(hostname: str, silent: bool = False) -> bool:
        """移除指定主机名的 hosts 映射
        
        Args:
            hostname: 要移除的主机名
            silent: 如果为 True，主机名不存在时不抛出异常
            
        Returns:
            是否成功移除（True）或主机名不存在（False）
            
        Raises:
            PermissionError: 如果没有足够的权限
            ValueError: 如果主机名不存在且 silent=False
            IOError: 如果操作失败
        """
        if not hostname:
            raise ValueError("主机名不能为空")
        
        HostsManager._check_permission()
        
        hosts_path = HostsManager._get_hosts_path()
        
        try:
            lines = HostsManager.read()
            new_lines = []
            found = False
            
            for line in lines:
                # 跳过空行和注释行
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    new_lines.append(line)
                    continue
                
                # 检查是否包含要删除的主机名
                parts = stripped.split()
                if len(parts) >= 2 and parts[1] == hostname:
                    found = True
                    continue  # 跳过此行
                
                new_lines.append(line)
            
            if not found and not silent:
                raise ValueError(f"主机名 '{hostname}' 在 hosts 文件中不存在")
            
            # 写回文件
            with open(hosts_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            
            return found
        except ValueError:
            raise
        except Exception as e:
            raise OSError(f"移除 hosts 条目失败: {e}") from e
    
    @staticmethod
    def list_custom_hosts() -> list[dict[str, str]]:
        """列出所有由本工具添加的 hosts 映射
        
        Returns:
            包含 IP、主机名和注释的字典列表
            
        Raises:
            IOError: 如果读取失败
        """
        try:
            lines = HostsManager.read()
            custom_hosts = []
            
            for line in lines:
                if HostsManager.MARKER in line:
                    stripped = line.strip()
                    # 移除标记注释
                    stripped = stripped.replace(HostsManager.MARKER, "").strip()
                    
                    # 分离 IP、主机名和可选注释
                    parts = stripped.split(None, 2)
                    if len(parts) >= 2:
                        entry: dict[str, Any] = {
                            "ip": parts[0],
                            "hostname": parts[1],
                        }
                        if len(parts) > 2 and parts[2].startswith("#"):
                            entry["comment"] = parts[2][1:].strip()
                        custom_hosts.append(entry)
            
            return custom_hosts
        except Exception as e:
            raise OSError(f"列出自定义 hosts 失败: {e}") from e
    
    @staticmethod
    def clear_custom_hosts() -> int:
        """清除所有由本工具添加的 hosts 映射
        
        Returns:
            清除的条目数量
            
        Raises:
            PermissionError: 如果没有足够的权限
            IOError: 如果操作失败
        """
        HostsManager._check_permission()
        
        hosts_path = HostsManager._get_hosts_path()
        
        try:
            lines = HostsManager.read()
            new_lines = []
            count = 0
            
            for line in lines:
                if HostsManager.MARKER in line:
                    count += 1
                    continue  # 跳过由本工具添加的行
                new_lines.append(line)
            
            # 写回文件
            with open(hosts_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            
            return count
        except Exception as e:
            raise OSError(f"清除自定义 hosts 失败: {e}") from e
