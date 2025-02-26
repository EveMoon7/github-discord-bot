#!/bin/bash

# 切换到 Git 仓库目录
cd /home/ec2-user/github-discord-bot || exit

# 确保 Git 远程仓库是正确的
git remote -v

# 添加 user_affection.db
git add user_affection.db

# 检查是否有更改
if ! git diff --cached --quiet; then
    # 提交更改
    git commit -m "定时更新 user_affection.db $(date '+%Y-%m-%d %H:%M:%S')"

    # 推送到 GitHub
    git push origin main
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 没有变化，不推送。" >> /home/ec2-user/push_log.txt
fi
