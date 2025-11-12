import subprocess
import os
from typing import Dict, Optional

def get_user_info(cwd: Optional[str] = None) -> Dict[str, str]:
    """
    获取 Git 用户信息
    
    Args:
        cwd: 工作目录，默认为当前目录
        
    Returns:
        包含用户名、邮箱和工作目录的字典
    """
    if cwd is None:
        cwd = os.getcwd()
    
    try:
        # 获取用户名
        try:
            name_result = subprocess.run(
                ['git', 'config', 'user.name'], 
                cwd=cwd, 
                capture_output=True, 
                text=True, 
                check=True
            )
            name = name_result.stdout.strip()
        except subprocess.CalledProcessError:
            name = 'unknown'
        
        # 获取邮箱
        try:
            email_result = subprocess.run(
                ['git', 'config', 'user.email'], 
                cwd=cwd, 
                capture_output=True, 
                text=True, 
                check=True
            )
            email = email_result.stdout.strip()
        except subprocess.CalledProcessError:
            email = 'unknown'
        
        print(f"[DataStatistics] 解析用户信息: name={name}, email={email}, cwd={cwd}")
        return {'name': name, 'email': email, 'cwd': cwd}
    
    except Exception as error:
        print(f"获取用户信息失败: {error}")
        return {'name': 'unknown', 'email': 'unknown', 'cwd': cwd}

# 使用示例
if __name__ == "__main__":
    user_info = get_user_info()
    print(f"用户名: {user_info['name']}")
    print(f"邮箱: {user_info['email']}")
    print(f"工作目录: {user_info['cwd']}")