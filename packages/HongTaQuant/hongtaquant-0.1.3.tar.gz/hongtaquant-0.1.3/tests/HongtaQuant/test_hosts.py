"""测试 HostsManager 工具类"""

import pytest

from HongTaQuant.utils import HostsManager


def test_hosts_manager_import() -> None:
    """测试 HostsManager 可以正确导入."""
    assert HostsManager is not None


def test_get_hosts_path() -> None:
    """测试获取 hosts 文件路径."""
    path = HostsManager._get_hosts_path()
    assert path is not None
    assert path.exists()


def test_read_hosts() -> None:
    """测试读取 hosts 文件."""
    lines = HostsManager.read()
    assert isinstance(lines, list)
    assert len(lines) > 0


def test_list_custom_hosts() -> None:
    """测试列出自定义 hosts."""
    custom_hosts = HostsManager.list_custom_hosts()
    assert isinstance(custom_hosts, list)


# 注意：以下测试需要管理员权限，默认跳过
@pytest.mark.skip(reason="需要管理员/root权限")
def test_add_and_remove_host() -> None:
    """测试添加和移除 hosts 映射."""
    test_ip = "127.0.0.1"
    test_hostname = "test.hongtaquant.local"
    
    # 添加映射
    HostsManager.add_host(test_ip, test_hostname, "测试用例")
    
    # 验证添加成功
    custom_hosts = HostsManager.list_custom_hosts()
    assert any(h["hostname"] == test_hostname for h in custom_hosts)
    
    # 移除映射
    result = HostsManager.remove_host(test_hostname)
    assert result is True
    
    # 验证移除成功
    custom_hosts = HostsManager.list_custom_hosts()
    assert not any(h["hostname"] == test_hostname for h in custom_hosts)


@pytest.mark.skip(reason="需要管理员/root权限")
def test_backup_and_restore() -> None:
    """测试备份和恢复 hosts 文件."""
    # 备份
    backup_path = HostsManager.backup()
    assert backup_path.exists()
    
    # 恢复
    HostsManager.restore()


def test_invalid_parameters() -> None:
    """测试无效参数处理."""
    with pytest.raises(ValueError):
        HostsManager.add_host("", "test.com")
    
    with pytest.raises(ValueError):
        HostsManager.add_host("127.0.0.1", "")
    
    with pytest.raises(ValueError):
        HostsManager.remove_host("")
