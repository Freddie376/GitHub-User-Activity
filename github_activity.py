"""GitHub User Activity CLI
Fetches the recent public activity of a GitHub user with the GitHub API
and shows it in the terminal. Uses only Python's built-in modules.

Usage: python github_activity.py <username>"""

from __future__ import annotations

import json
import re
import socket
import sys
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any, Final, cast

API_URL: Final[str] = "https://api.github.com/users/{username}/events/public"
TIMEOUT: Final[int] = 10  # seconds to wait for GitHub before giving up


def is_valid_username(username: str) -> bool:
    """Checks a username against GitHub's rules: letters, numbers and hyphens,
    1 to 39 characters, and it cannot start or end with a hyphen."""
    return re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", username) is not None


def fetch_github_activity(username: str) -> list[dict[str, Any]]:
    """Gets the recent public events of a user from the GitHub API.
    Stops the program with a clear message if anything goes wrong."""
    url = API_URL.format(username=username)
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "GitHub Activity CLI",  # GitHub rejects requests without one
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: User '{username}' not found.")
        elif e.code in (403, 429):
            print("Error: Rate limit exceeded. Please try again later.")
        else:
            print(f"HTTP Error: {e.code} - {e.reason}")
        sys.exit(1)
    except urllib.error.URLError as e:
        if isinstance(e.reason, socket.timeout):
            print("Error: Request timed out. Please try again.")
        else:
            print(f"Error: Could not connect to GitHub ({e.reason}). Check your internet connection.")
        sys.exit(1)
    except (TimeoutError, socket.timeout):
        print("Error: GitHub took too long to respond. Please try again.")
        sys.exit(1)
    except ValueError:
        print("Error: Failed to read the response from GitHub.")
        sys.exit(1)

    if not isinstance(data, list):
        print("Error: Unexpected data format received from GitHub API.")
        sys.exit(1)
    return cast(list[dict[str, Any]], data)


def plural(count: int, singular: str, plural_form: str) -> str:
    """Returns the singular or plural form based on the count."""
    return f"{count} {singular}" if count == 1 else f"{count} {plural_form}"


def format_time(created_at: str) -> str:
    """Turns GitHub's time (2026-10-24T10:30:00Z) into a shorter form (2026-10-24 10:30 UTC)."""
    try:
        moment = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    except (TypeError, ValueError):
        return str(created_at)
    return moment.strftime("%Y-%m-%d %H:%M UTC")


def describe_event(event: dict[str, Any]) -> str:
    """Turns one GitHub event into a short sentence."""
    event_type = event.get("type", "UnknownEvent")
    repo_name = event.get("repo", {}).get("name", "an unknown repository")
    payload = event.get("payload", {})
    action = payload.get("action", "")

    if event_type == "PushEvent":
        commits = payload.get("size")
        if commits is None:
            commits = len(payload.get("commits", []))
        if commits:
            return f"Pushed {plural(commits, 'commit', 'commits')} to {repo_name}"
        return f"Pushed to {repo_name}"

    if event_type == "IssuesEvent":
        issue = payload.get("issue", {})
        return f"{action.capitalize() or 'Updated'} issue #{issue.get('number', 'Unknown')} in {repo_name}"

    if event_type == "IssueCommentEvent":
        issue = payload.get("issue", {})
        kind = "pull request" if "pull_request" in issue else "issue"
        return f"Commented on {kind} #{issue.get('number', 'Unknown')} in {repo_name}"

    if event_type == "PullRequestEvent":
        pull_request = payload.get("pull_request", {})
        if action == "closed" and pull_request.get("merged", False):
            action = "merged"
        return f"{action.capitalize() or 'Updated'} pull request #{pull_request.get('number', 'Unknown')} in {repo_name}"

    if event_type in ("PullRequestReviewEvent", "PullRequestReviewCommentEvent"):
        number = payload.get("pull_request", {}).get("number", "Unknown")
        return f"Reviewed pull request #{number} in {repo_name}"

    if event_type == "CommitCommentEvent":
        return f"Commented on a commit in {repo_name}"

    if event_type == "WatchEvent":
        return f"Starred {repo_name}"

    if event_type == "ForkEvent":
        return f"Forked {repo_name} to {payload.get('forkee', {}).get('full_name', 'Unknown')}"

    if event_type == "CreateEvent":
        ref_type = payload.get("ref_type", "Unknown")
        if ref_type == "repository":
            return f"Created repository {repo_name}"
        return f"Created {ref_type} {payload.get('ref', 'Unknown')} in {repo_name}"

    if event_type == "DeleteEvent":
        ref_type = payload.get("ref_type", "Unknown")
        return f"Deleted {ref_type} {payload.get('ref', 'Unknown')} in {repo_name}"

    if event_type == "ReleaseEvent":
        tag = payload.get("release", {}).get("tag_name", "Unknown")
        return f"{action.capitalize() or 'Published'} release {tag} in {repo_name}"

    if event_type == "PublicEvent":
        return f"Made {repo_name} public"

    if event_type == "MemberEvent":
        member = payload.get("member", {}).get("login", "Unknown")
        return f"{action.capitalize() or 'Updated'} member {member} in {repo_name}"

    if event_type == "GollumEvent":
        return f"Edited the wiki of {repo_name}"

    # Any other event type: show its name instead of failing
    return f"{event_type.removesuffix('Event')} activity in {repo_name}"


def main() -> None:
    """Reads the username from the command line and shows the activity."""
    if len(sys.argv) != 2:
        print("Usage: python github_activity.py <username>")
        print("Example: python github_activity.py octocat")
        sys.exit(1)

    username = sys.argv[1].strip()

    if not is_valid_username(username):
        print(f"Error: '{username}' is not a valid GitHub username.")
        sys.exit(1)

    events = fetch_github_activity(username)

    if not events:
        print(f"No recent public activity found for user '{username}'.")
        return

    print(f"Recent public activity for user '{username}':\n")

    for event in events:
        description = describe_event(event)
        created_at = format_time(event.get("created_at", "Unknown time"))
        print(f"- {description} at {created_at}")


if __name__ == "__main__":
    main()
