#!/bin/bash
# 切換到專案目錄
cd /home/ec2-user/github-discord-bot || exit

# 檢查 user_affection.db 是否有變更
if ! git diff --quiet HEAD -- user_affection.db; then
    # 新增 user_affection.db 的變更
    git add user_affection.db

    # 使用當前日期作為 commit 訊息
    git commit -m "自動更新 user_affection.db $(date +"%Y-%m-%d %H:%M:%S")"

    # 推送到 GitHub，這裡假設分支名稱為 main
    git push origin main
fi
