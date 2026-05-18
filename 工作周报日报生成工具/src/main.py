"""一键：判断拉取时间 → 同步 Gitee → 更新 CSV → 生成周报或日报 Markdown。"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
from pathlib import Path


def _load_dotenv(root: Path) -> None:
    env_path = root / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parent.parent
    _load_dotenv(root)

    sys.path.insert(0, str(root))

    from src.config import LAST_PULL_LOG, WORK_CSV, DOCS_DIR, resolve_repos
    from src import gitee_api
    from src import storage
    from src import report_md

    parser = argparse.ArgumentParser(description="Gitee 同步与工作周报/日报生成")
    parser.add_argument(
        "--force-pull",
        action="store_true",
        help="无视当日已拉取记录，强制从 Gitee 拉取最近一周提交",
    )
    parser.add_argument(
        "--skip-report",
        action="store_true",
        help="仅同步 CSV，不生成 docs 下的周报或日报",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="仅从现有 CSV 生成周报或日报（不请求 Gitee；与 --daily 合用时生成日报）",
    )
    parser.add_argument(
        "--since-days",
        type=int,
        default=None,
        metavar="N",
        help="覆盖默认起始时间：从当前本地时刻往前 N 天的 0 点起拉取提交",
    )
    parser.add_argument(
        "--report-days",
        type=int,
        default=14,
        metavar="N",
        help="生成周报时从 CSV 取最近 N 个自然日（含当日）；默认 14 日兼顾交界提交",
    )
    parser.add_argument(
        "--repos-file",
        type=Path,
        default=None,
        metavar="PATH",
        help="JSON 仓库列表，覆盖默认仓库；相对路径相对于项目根目录",
    )
    parser.add_argument(
        "--repo",
        action="append",
        default=None,
        dest="repo_specs",
        metavar="OWNER::REPO::项目展示名",
        help=(
            "覆盖默认仓库，可重复；格式 owner::repo::项目展示名（双冒号分隔）。 "
            "若与 --repos-file 同时存在，以 --repos-file 为准。"
        ),
    )
    parser.add_argument(
        "--daily",
        action="store_true",
        help="生成日报 Markdown（不写周报）；输出 docs/YYYY-MM-DD日报.md",
    )
    parser.add_argument(
        "--daily-date",
        type=str,
        default=None,
        metavar="YYYY-MM-DD",
        help="与 --daily 合用：指定统计日，默认本地今日",
    )
    args = parser.parse_args(argv)

    daily_day: dt.date | None = None
    if args.daily_date and not args.daily:
        print("--daily-date 须与 --daily 同时使用", file=sys.stderr)
        return 5
    if args.daily_date:
        try:
            daily_day = dt.date.fromisoformat(args.daily_date.strip())
        except ValueError:
            print("--daily-date 须为 YYYY-MM-DD", file=sys.stderr)
            return 5

    try:
        repos = resolve_repos(args.repo_specs, args.repos_file, root)
    except (OSError, ValueError) as e:
        print(str(e), file=sys.stderr)
        return 4

    token = (os.environ.get("GITEE_TOKEN") or "").strip()
    today0 = storage.today_midnight_local()
    last = storage.read_last_pull(LAST_PULL_LOG)

    need_pull = args.force_pull or (
        last is None or last < today0
    )

    if args.report_only:
        need_pull = False

    appended = 0
    if need_pull:
        if not token:
            print(
                "需要拉取但未配置 GITEE_TOKEN（环境变量或项目根目录 .env）。",
                file=sys.stderr,
            )
            return 2
        existing = storage.load_existing_shas(WORK_CSV)
        since_dt = storage.pull_since_datetime(since_days=args.since_days)
        new_rows: list[dict[str, str]] = []
        for cfg in repos:
            owner, repo = cfg["owner"], cfg["repo"]
            label = cfg["project_label"]
            try:
                commits = gitee_api.fetch_commits_since(owner, repo, token, since_dt)
            except Exception as e:
                print(f"拉取提交列表失败 {owner}/{repo}: {e}", file=sys.stderr)
                return 3
            for c in commits:
                sha = (c.get("sha") or "").strip()
                if not sha or sha in existing:
                    continue
                commit = c.get("commit") or {}
                msg = (commit.get("message") or "").strip().splitlines()[0].strip()
                if not msg or msg.startswith("```"):
                    msg = "（提交说明为空或不可用作摘要）"
                author = (
                    (commit.get("author") or {}).get("name")
                    or (c.get("committer") or {}).get("name")
                    or ""
                )
                date_str = ((commit.get("author") or {}).get("date") or "").strip()
                try:
                    ad = dt.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    day = ad.astimezone().date().isoformat()
                except ValueError:
                    day = dt.date.today().isoformat()
                module = "综合"
                try:
                    detail = gitee_api.fetch_commit_detail(owner, repo, sha, token)
                    files = detail.get("files") or []
                    paths = [str(f.get("filename") or "") for f in files]
                    module = gitee_api.infer_module_from_files(paths)
                except Exception:
                    pass
                new_rows.append(
                    {
                        "date": day,
                        "project": label,
                        "module": module,
                        "summary": msg,
                        "sha": sha,
                        "author": author,
                    }
                )
                existing.add(sha)
        appended = storage.append_rows(WORK_CSV, new_rows)
        storage.write_last_pull(LAST_PULL_LOG)
        print(f"已从 Gitee 写入 {appended} 条新记录到 {WORK_CSV}")
    else:
        reason = "当日已拉取过" if last and last >= today0 else "用户指定仅生成文档"
        print(f"跳过远程拉取（{reason}），使用本地 CSV：{WORK_CSV}")

    if not args.skip_report:
        if args.daily:
            out = report_md.write_daily_doc(DOCS_DIR, WORK_CSV, day=daily_day)
            print(f"已生成日报：{out}")
        else:
            out = report_md.write_weekly_doc(
                DOCS_DIR, WORK_CSV, report_days=args.report_days
            )
            print(f"已生成周报：{out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
