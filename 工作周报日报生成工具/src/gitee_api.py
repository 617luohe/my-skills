"""Gitee OpenAPI：提交列表与详情。"""
from __future__ import annotations

import datetime as dt
from typing import Any

import requests

COMMITS_URL = "https://gitee.com/api/v5/repos/{owner}/{repo}/commits"
COMMIT_DETAIL_URL = "https://gitee.com/api/v5/repos/{owner}/{repo}/commits/{sha}"


def fetch_commits_since(
    owner: str,
    repo: str,
    token: str,
    since: dt.datetime,
    per_page: int = 100,
) -> list[dict[str, Any]]:
    params = {
        "access_token": token,
        "since": since.isoformat(timespec="seconds"),
        "per_page": per_page,
    }
    out: list[dict[str, Any]] = []
    page = 1
    while True:
        r = requests.get(
            COMMITS_URL.format(owner=owner, repo=repo),
            params={**params, "page": page},
            timeout=60,
        )
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        out.extend(batch)
        if len(batch) < per_page:
            break
        page += 1
    return out


def fetch_commit_detail(owner: str, repo: str, sha: str, token: str) -> dict[str, Any]:
    r = requests.get(
        COMMIT_DETAIL_URL.format(owner=owner, repo=repo, sha=sha),
        params={"access_token": token},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def infer_module_from_files(paths: list[str]) -> str:
    tops: list[str] = []
    for p in paths:
        p = p.strip().strip("/")
        if not p or p.startswith("."):
            continue
        tops.append(p.split("/")[0])
    if not tops:
        return "综合"
    return max(set(tops), key=tops.count)
