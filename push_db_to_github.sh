#!/bin/bash

# 切换到 Git 仓库目录
cd /home/ec2-user/github-discord-bot || exit

# 强制追踪 user_affection.db（即使 .gitignore 忽略）
git add -f user_affection.db

# 确保 Git 远程仓库配置正确
git remote -v

# 添加所有更改
git add .

# 检查是否有未提交的更改
if ! git diff --cached --quiet; then
    # 提交更改（即使没有文件变更，也允许提交）
    git commit -m "定时更新 user_affection.db $(date '+%Y-%m-%d %H:%M:%S')" --allow-empty

    # 推送到 GitHub
    git push origin main
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 没有变化，不推送。" >> /home/ec2-user/push_log.txt
fi

