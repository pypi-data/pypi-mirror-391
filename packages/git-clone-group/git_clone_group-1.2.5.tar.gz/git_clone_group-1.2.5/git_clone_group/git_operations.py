"""
Git operations for cloning and pulling repositories.

This module handles all Git-related operations including cloning repositories,
pulling updates, and managing different branches.
"""

import asyncio
from pathlib import Path
from typing import Dict, List

from .config import GitLabConfig, ProjectStats
from .exceptions import GitLabPermissionError


async def clone_or_pull_project(
    config: GitLabConfig, project: Dict, stats: ProjectStats
) -> None:
    """Clone or pull a single project asynchronously."""
    project_url = project["ssh_url_to_repo"]
    project_path = project["path_with_namespace"]
    full_path = config.dest_dir / project_path

    async def run_git_command(command: List[str]) -> str:
        """Execute a git command asynchronously."""
        try:
            proc = await asyncio.create_subprocess_exec(
                *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            stderr_text = stderr.decode()
            stdout_text = stdout.decode().strip()

            if proc.returncode != 0:
                if "Permission denied" in stderr_text:
                    raise GitLabPermissionError(f"Permission denied for {project_path}")
                raise RuntimeError(f"Git command failed: {stderr_text}")
            return stdout_text
        except GitLabPermissionError:
            raise
        except Exception as e:
            raise RuntimeError(f"Git operation failed: {str(e)}")

    async def safe_pull(path: Path) -> None:
        """Fetch all remote refs and update current branch without switching.

        行为变更：
        - 不强制切换到远端默认分支或指定分支；优先保持当前本地分支。
        - 拉取远程仓库的全部引用信息（所有远端、标签，自动清理已删除的远端分支）。
        - 如果当前分支已设置 upstream，则执行 fast-forward 的 pull；否则仅 fetch。
        """
        try:
            # Fetch origin with all refs and tags (不使用 --prune，保留已删除远程分支的本地引用)
            await run_git_command(["git", "-C", str(path), "fetch", "origin", "--tags"])

            # Determine current branch; if detached HEAD, skip pull and only fetch
            current_branch = await run_git_command(
                ["git", "-C", str(path), "rev-parse", "--abbrev-ref", "HEAD"]
            )

            if current_branch != "HEAD":
                # Check whether current branch has an upstream tracking branch
                has_upstream = False
                try:
                    await run_git_command(
                        [
                            "git",
                            "-C",
                            str(path),
                            "rev-parse",
                            "--abbrev-ref",
                            "--symbolic-full-name",
                            "@{u}",
                        ]
                    )
                    has_upstream = True
                except RuntimeError:
                    # No upstream configured; we won't switch or create one automatically
                    has_upstream = False

                if has_upstream:
                    # Fast-forward only to avoid unintended merges
                    await run_git_command(["git", "-C", str(path), "pull", "--ff-only"])

            # Count as updated if fetch succeeded regardless of pull
            stats.updated += 1
        except Exception as e:
            raise RuntimeError(f"Pull failed: {str(e)}")

    async def init_repo(path: Path) -> None:
        """Initialize new repository"""
        try:
            clone_cmd = ["git", "clone", project_url, str(path)]
            if config.branch:
                clone_cmd.extend(["-b", config.branch])
            await run_git_command(clone_cmd)

            if not path.exists():
                raise RuntimeError("Clone completed but directory not found")

            # 检查是否为空仓库
            try:
                await run_git_command(["git", "-C", str(path), "rev-parse", "HEAD"])
                stats.cloned += 1
            except RuntimeError:
                stats.empty += 1
                stats.empty_repos.append(project_path)
        except Exception as e:
            raise RuntimeError(f"Clone failed: {str(e)}")

    # Main operation with retries
    for attempt in range(config.max_retries):
        try:
            if full_path.exists():
                await safe_pull(full_path)
            else:
                await init_repo(full_path)
            return
        except GitLabPermissionError:
            raise
        except Exception as e:
            if attempt == config.max_retries - 1:
                print(
                    f"Failed after {config.max_retries} attempts for {project_path}: {e}"
                )
                stats.failed += 1
                raise
            await asyncio.sleep(1 * (attempt + 1))
