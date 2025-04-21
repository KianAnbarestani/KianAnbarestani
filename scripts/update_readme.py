import requests
import os

USERNAME = "KianAnbarestani"
TOKEN = os.getenv("GITHUB_TOKEN")  # Automatically provided in GitHub Actions
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

GRAPHQL_QUERY = """
{
  user(login: "%s") {
    repositoriesContributedTo(first: 5, contributionTypes: [COMMIT], includeUserRepositories: false, orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes {
        name
        description
        url
        updatedAt
        stargazerCount
        owner {
          login
        }
      }
    }
  }
}
""" % USERNAME

def fetch_contributions():
    res = requests.post(
        "https://api.github.com/graphql",
        json={"query": GRAPHQL_QUERY},
        headers=HEADERS
    )
    if res.status_code != 200:
        raise Exception(f"GitHub API error: {res.status_code}\n{res.text}")
    return res.json()["data"]["user"]["repositoriesContributedTo"]["nodes"]

def build_markdown(repos):
    lines = ["<!--START:projects-->"]
    lines.append("## 🔥 Latest Repositories I Contributed To\n")
    for repo in repos:
        lines.append(f"* [{repo['owner']['login']}/{repo['name']}]({repo['url']}) – {repo['description'] or 'No description'}  ")
        lines.append(f"  ⭐ {repo['stargazerCount']} | 🕒 Updated: {repo['updatedAt'][:10]}\n")
    lines.append("<!--END:projects-->")
    return "\n".join(lines)

def update_readme(new_section):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    start_marker = "<!--START:projects-->"
    end_marker = "<!--END:projects-->"
    start = content.find(start_marker)
    end = content.find(end_marker) + len(end_marker)

    if start == -1 or end == -1:
        raise Exception("Markers <!--START:projects--> or <!--END:projects--> not found in README.md")

    updated = content[:start] + new_section + content[end:]

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)

def main():
    repos = fetch_contributions()
    new_md = build_markdown(repos)
    update_readme(new_md)

if __name__ == "__main__":
    main()
