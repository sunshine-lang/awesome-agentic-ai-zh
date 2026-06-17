import requests
import os

# 显示 GitHub 用户信息 函数
def show_github_user(username):

    url = f"https://api.github.com/users/{username}"
    token = os.getenv('GITHUB_TOKEN')
    headers = {'Authorization': f'token {token}'} if token else {}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        if e.response is not None:
            print(f"请求失败: {e.response.status_code}")
        else:
            print(f"请求失败: {e}")
        return
    data = response.json()
    print(f"用户名: {data['login']}")
    print(f"粉丝数: {data['followers']}")
    print(f"公开仓库数: {data['public_repos']}")

show_github_user("sunshine908686")
show_github_user("sunshine-lang")
