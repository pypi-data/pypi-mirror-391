import re
import subprocess
from pathlib import Path


def build():
    """自动递增版本号并构建 wheel 包"""
    try:
        pyproject_path = Path("pyproject.toml")
        content = pyproject_path.read_text(encoding="utf-8")
        
        # 匹配版本号
        match = re.search(r'version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', content)
        if not match:
            raise ValueError("无法找到版本号")
        
        major, minor, patch = map(int, match.groups())
        old_version = f"{major}.{minor}.{patch}"
        new_version = f"{major}.{minor}.{patch + 1}"
        
        # 更新版本号
        new_content = re.sub(
            r'version\s*=\s*"[\d\.]+"',
            f'version = "{new_version}"',
            content
        )
        pyproject_path.write_text(new_content, encoding="utf-8")
        print(f"✓ 版本号已更新: {old_version} → {new_version}")
        
        # 执行构建
        result = subprocess.run(
            ["uv", "build", "--wheel"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("构建成功!")
            print(result.stdout)
        else:
            print("构建失败!")
            print(result.stderr)
            raise RuntimeError(f"构建失败: {result.stderr}")
            
    except FileNotFoundError:
        print("错误: 找不到 pyproject.toml 文件")
        raise
    except Exception as e:
        print(f"发生错误: {e}")
        raise 