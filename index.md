# create index.md in the portfolio repo
$index = @"
---
layout: home
title: Dan Boles — AI & Systems
---

{% capture readme %}{% include_relative README.md %}{% endcapture %}
{{ readme | markdownify }}
"@

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText("$HOME\dev\dboles99.github.io\index.md", $index, $utf8NoBom)

git -C "$HOME\dev\dboles99.github.io" add index.md
git -C "$HOME\dev\dboles99.github.io" commit -m "site: add index.md homepage (renders README)" 2>$null
git -C "$HOME\dev\dboles99.github.io" push

# (optional) trigger a build and open the site)
gh api repos/dboles99/dboles99.github.io/pages/builds -X POST | Out-Null
Start-Process "https://dboles99.github.io/"
