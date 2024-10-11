set -e

function commit_git() {
  if [ -z "$1" ]; then
    echo "请输入提交信息"
    read -r commit_msg
    git add .
    git commit -m "$commit_msg"
    git push
  else
    git add .
    git commit -m "$1"
    git push
  fi
}

commit_git "$1"