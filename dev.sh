#!/bin/bash
set -e
# 检查是否提供了提交信息
if [ "$#" -eq 0 ]; then
    # 如果没有提供提交信息，提示用户输入
    read -p "请输入提交信息: " commit_msg
else
    # 如果提供了提交信息，使用第一个参数作为提交信息
    commit_msg="$1"
fi

# 执行git提交命令
git add .
git commit -m "$commit_msg"
# 提示提交结果
echo "提交成功: $commit_msg"
git push githubware main
echo "推送成功"
