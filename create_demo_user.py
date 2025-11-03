# ============================================================================
# 创建演示用户脚本
# ============================================================================

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import db

print("\n" + "="*60)
print("创建 AgentForge 演示账号")
print("="*60 + "\n")

try:
    with db.session_scope() as session:
        # 检查演示账号是否已存在
        from backend.models import User
        existing = session.query(User).filter_by(username='demo').first()
        
        if existing:
            print("⚠️  演示账号已存在")
            print(f"   用户名: {existing.username}")
            print(f"   邮箱: {existing.email}")
            print(f"   角色: {existing.role}")
        else:
            # 创建演示账号
            demo_user = User(
                username='demo',
                email='demo@agentforge.com',
                role='admin'
            )
            demo_user.password = 'demo123'
            session.add(demo_user)
            
            print("✓ 演示账号创建成功！")
            print("\n登录信息：")
            print("─" * 40)
            print(f"  用户名：demo")
            print(f"  密码：  demo123")
            print(f"  角色：  admin")
            print("─" * 40)
        
        # 创建普通用户账号
        existing_user = session.query(User).filter_by(username='user').first()
        if not existing_user:
            normal_user = User(
                username='user',
                email='user@agentforge.com',
                role='user'
            )
            normal_user.password = 'user123'
            session.add(normal_user)
            
            print("\n✓ 普通用户账号创建成功！")
            print("\n登录信息：")
            print("─" * 40)
            print(f"  用户名：user")
            print(f"  密码：  user123")
            print(f"  角色：  user")
            print("─" * 40)

except Exception as e:
    print(f"✗ 错误：{e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("完成！")
print("="*60)
print("\n现在可以运行 python app.py 启动服务器")
print("然后访问 http://localhost:5000/login 登录\n")

