# .github/scripts/generate_activity.py
import os
import requests
import datetime
import re

# 設定要抓取的 username（可以改成想抓的使用者）
USERNAME = os.getenv("ACTIVITY_USER", os.getenv("GITHUB_ACTOR", "octocat"))

# GitHub API
API_URL = f"https://api.github.com/users/{USERNAME}/events/public"

headers = {}
token = os.getenv("GITHUB_TOKEN")  # 我們在 workflow 用 secret TOKEN 傳入到 GITHUB_TOKEN
if token:
    headers["Authorization"] = f"token {token}"

resp = requests.get(API_URL, headers=headers)
events = resp.json() if resp.status_code == 200 else []

# 取最近 5 件活動（視情況改）
entries = []
for ev in events[:5]:
    t = ev.get("type", "Event")
    repo = ev.get("repo", {}).get("name", "")
    created = ev.get("created_at", "")
    # 簡單格式化
    created_fmt = ""
    if created:
        try:
            created_fmt = datetime.datetime.fromisoformat(
                created.replace("Z", "+00:00")
            ).strftime("%Y-%m-%d %H:%M")
        except:
            created_fmt = created
    entries.append(f"- **{t}** on `{repo}` — {created_fmt}")

if not entries:
    new_block = "*（自動產生中 — 無最近活動）*"
else:
    new_block = "\n".join(entries)

# 讀 README.md，替換 ACTIVITY 區塊
with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

pattern = re.compile(r"(<!-- ACTIVITY_START -->)(.*?)(<!-- ACTIVITY_END -->)", re.S)
replacement = r"\1\n" + new_block + r"\n\3"

if pattern.search(readme):
    new_readme = pattern.sub(replacement, readme)
else:
    # 如果找不到標記，則把區塊插到檔案末尾
    new_readme = (
        readme
        + "\n\n<!-- ACTIVITY_START -->\n"
        + new_block
        + "\n<!-- ACTIVITY_END -->\n"
    )

# 只有在不同時才寫檔
if new_readme != readme:
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_readme)
    print("README updated")
else:
    print("No update needed")
