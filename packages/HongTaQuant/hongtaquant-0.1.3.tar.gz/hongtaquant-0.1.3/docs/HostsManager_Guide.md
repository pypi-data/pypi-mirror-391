# HostsManager 使用指南

## 简介

`HostsManager` 是一个跨平台的 hosts 文件管理工具类，提供了便捷的 hosts 文件操作功能。

## 功能特性

- ✅ 跨平台支持（Windows、Linux、macOS）
- ✅ 添加/更新 hosts 映射
- ✅ 删除 hosts 映射
- ✅ 备份和恢复 hosts 文件
- ✅ 列出自定义的 hosts 条目
- ✅ 批量清除自定义条目
- ✅ 自动权限检查

## 安装

```python
pip install HongTaQuant
```

## 基本使用

### 导入模块

```python
from HongTaQuant.utils import HostsManager
# 或者
from HongTaQuant import HostsManager
```

### 添加 hosts 映射

```python
# 添加简单的 IP 到主机名映射
HostsManager.add_host("120.253.157.163", "api.hongtaquant.com")

# 添加带注释的映射
HostsManager.add_host(
    "120.253.157.163", 
    "api.hongtaquant.com", 
    comment="红塔量化API服务器"
)
```

### 移除 hosts 映射

```python
# 移除指定主机名的映射
HostsManager.remove_host("api.hongtaquant.com")

# 静默模式（主机名不存在时不抛出异常）
HostsManager.remove_host("api.hongtaquant.com", silent=True)
```

### 列出自定义的 hosts

```python
# 获取所有由 HostsManager 添加的 hosts 条目
custom_hosts = HostsManager.list_custom_hosts()

for host in custom_hosts:
    print(f"{host['ip']} -> {host['hostname']}")
    if 'comment' in host:
        print(f"  注释: {host['comment']}")
```

### 备份和恢复

```python
# 备份当前 hosts 文件
backup_path = HostsManager.backup()
print(f"已备份到: {backup_path}")

# 恢复 hosts 文件
HostsManager.restore()
```

### 清除所有自定义条目

```python
# 清除所有由 HostsManager 添加的条目
count = HostsManager.clear_custom_hosts()
print(f"已清除 {count} 个自定义条目")
```

### 读取 hosts 文件

```python
# 读取完整的 hosts 文件内容
lines = HostsManager.read()
for line in lines:
    print(line, end='')
```

## 权限要求

修改 hosts 文件需要管理员/root 权限：

### Windows

以**管理员身份**运行 PowerShell 或 CMD：

```powershell
# 右键点击 PowerShell，选择"以管理员身份运行"
python your_script.py
```

### Linux/macOS

使用 `sudo` 运行：

```bash
sudo python your_script.py
```

## 完整示例

```python
from HongTaQuant.utils import HostsManager

def setup_hongtaquant_hosts():
    """配置红塔量化所需的 hosts 映射"""
    try:
        # 先备份
        print("备份 hosts 文件...")
        backup_path = HostsManager.backup()
        print(f"✓ 已备份到: {backup_path}")
        
        # 添加映射
        print("添加 hosts 映射...")
        HostsManager.add_host(
            "120.253.157.163",
            "api.hongtaquant.com",
            "红塔量化API服务器"
        )
        print("✓ 已添加 api.hongtaquant.com")
        
        # 验证
        custom_hosts = HostsManager.list_custom_hosts()
        print(f"\n当前自定义 hosts 条目: {len(custom_hosts)} 个")
        for host in custom_hosts:
            print(f"  {host['ip']} -> {host['hostname']}")
        
        print("\n✓ 配置完成！")
        
    except PermissionError as e:
        print(f"✗ 权限错误: {e}")
        print("请以管理员/root 权限运行此脚本")
    except Exception as e:
        print(f"✗ 错误: {e}")

def cleanup_hongtaquant_hosts():
    """清理红塔量化的 hosts 映射"""
    try:
        count = HostsManager.clear_custom_hosts()
        print(f"✓ 已清除 {count} 个自定义 hosts 条目")
    except PermissionError as e:
        print(f"✗ 权限错误: {e}")
    except Exception as e:
        print(f"✗ 错误: {e}")

if __name__ == "__main__":
    # 设置
    setup_hongtaquant_hosts()
    
    # 如需清理，取消下行注释
    # cleanup_hongtaquant_hosts()
```

## 异常处理

```python
from HongTaQuant.utils import HostsManager

try:
    HostsManager.add_host("127.0.0.1", "test.local")
except PermissionError as e:
    print(f"权限不足: {e}")
except ValueError as e:
    print(f"参数错误: {e}")
except OSError as e:
    print(f"IO错误: {e}")
```

## 注意事项

1. **权限要求**：修改 hosts 文件需要管理员/root 权限
2. **备份建议**：修改前建议先备份 hosts 文件
3. **条目标记**：所有通过 HostsManager 添加的条目会带有特殊标记 `# Added by HongTaQuant`
4. **自动更新**：如果主机名已存在，`add_host` 会自动更新其 IP 地址
5. **跨平台**：自动检测操作系统并使用正确的 hosts 文件路径

## API 参考

### HostsManager 类方法

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `add_host(ip, hostname, comment="")` | 添加或更新 hosts 映射 | None |
| `remove_host(hostname, silent=False)` | 移除 hosts 映射 | bool |
| `list_custom_hosts()` | 列出自定义的 hosts 条目 | list[dict] |
| `clear_custom_hosts()` | 清除所有自定义条目 | int |
| `backup()` | 备份 hosts 文件 | Path |
| `restore()` | 恢复 hosts 文件 | None |
| `read()` | 读取 hosts 文件内容 | list[str] |

## 常见问题

### Q: 提示权限错误怎么办？

**A:** 需要以管理员/root 权限运行程序。

- Windows: 右键"以管理员身份运行"
- Linux/macOS: 使用 `sudo` 命令

### Q: 如何恢复原始的 hosts 文件？

**A:** 使用 `restore()` 方法恢复之前的备份：

```python
HostsManager.restore()
```

### Q: 能否添加多个 IP 对应同一个主机名？

**A:** 不能。同一个主机名只能对应一个 IP。如果再次添加，会更新为新的 IP。

### Q: 如何查看哪些条目是由 HostsManager 添加的？

**A:** 使用 `list_custom_hosts()` 方法查看：

```python
custom_hosts = HostsManager.list_custom_hosts()
```

所有通过 HostsManager 添加的条目都会带有 `# Added by HongTaQuant` 标记。
