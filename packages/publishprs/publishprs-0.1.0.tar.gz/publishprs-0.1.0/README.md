# publishprs: Publish pull requests from a private repo to a public repo

Install:

```bash
pip install publishprs
```

Publish a PR:

```python
from publishprs import Publisher
publisher = Publisher(
    source_repo="https://github.com/laminlabs/laminhub",
    target_repo="https://github.com/laminlabs/laminhub-public",
    db="laminlabs/lamin-site-assets"
)
url = publisher.publish(pull_id=3820)
print(f"Published to: {url}")
```

Note that downloading assets from GitHub URLs of the form `https://github.com/user-attachments/assets/47729149-22a5-481b-beb4-69bb609ae054` neither works with the auto-generated `GITHUB_TOKEN` within GitHub Actions nor the fine-grained modern access tokens. A classic token is needed.
