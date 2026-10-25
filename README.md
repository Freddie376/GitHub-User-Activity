# GitHub User Activity CLI

A simple command line tool, written in Python, that fetches the recent public activity of any GitHub user using the GitHub API and shows it in the terminal. It uses only Python's built-in modules (no external libraries).

Project from roadmap.sh: https://roadmap.sh/projects/github-user-activity

## Features

- Takes the GitHub username as an argument
- Fetches recent public events from the GitHub API
- Shows each event as a short, readable line with the time it happened
- Handles errors clearly: invalid usernames, users that do not exist, rate limits, no internet connection, slow replies and broken replies

## Requirements

- Python 3.9 or newer
- An internet connection

Check your Python version with:
```bash
python --3.9
```
On some systems the command is `python3` instead of `python`.

## How to run

1. Clone the repository:
   ```bash
   git clone https://github.com/Freddie376/github-user-activity.git
   cd github-user-activity
   ```
2. Run the script with a GitHub username:
   ```bash
   python github_activity.py <username>
   ```

Example:
```bash
python github_activity.py kamranahmedse
```

## Example output

```
Recent public activity for user 'kamranahmedse':

- Pushed 3 commits to kamranahmedse/developer-roadmap at 2026-10-24 10:30 UTC
- Opened issue #7 in kamranahmedse/developer-roadmap at 2026-10-24 09:12 UTC
- Starred kamranahmedse/developer-roadmap at 2026-10-23 18:45 UTC
```

The lines you see depend on what the user did recently.

## Optional: run it as `github-activity`

To type `github-activity <username>` instead of the full command, add an alias to your shell:
```bash
echo 'alias github-activity="python /full/path/to/github_activity.py"' >> ~/.bashrc
source ~/.bashrc
github-activity <username>
```
Replace `/full/path/to/` with the real folder path.

## Events it understands

| GitHub event | What is shown |
|--------------|---------------|
| `PushEvent` | Pushed N commits to repo |
| `IssuesEvent` | Opened / Closed / Reopened issue #N in repo |
| `IssueCommentEvent` | Commented on issue (or pull request) #N in repo |
| `PullRequestEvent` | Opened / Closed / Merged pull request #N in repo |
| `PullRequestReviewEvent`, `PullRequestReviewCommentEvent` | Reviewed pull request #N in repo |
| `CommitCommentEvent` | Commented on a commit in repo |
| `WatchEvent` | Starred repo |
| `ForkEvent` | Forked repo to owner/new-repo |
| `CreateEvent` | Created repository, branch or tag |
| `DeleteEvent` | Deleted branch or tag |
| `ReleaseEvent` | Published release in repo |
| `PublicEvent` | Made repo public |
| `MemberEvent` | Added member to repo |
| `GollumEvent` | Edited the wiki of repo |
| Any other event | Shows the event name and the repo |

## How it works

1. `main()` reads the username from `sys.argv`.
2. `is_valid_username()` checks that the name follows GitHub's rules before anything is sent.
3. `fetch_github_activity()` sends a request to `https://api.github.com/users/<username>/events/public` using `urllib.request` and turns the JSON reply into a Python list.
4. `describe_event()` turns each event into a short sentence, and `format_time()` makes the time easier to read.
5. `main()` prints one line for each event.

A line-by-line explanation of the code is in `GitHub_Activity_Code_Explained.pdf`.

## Error handling

| Problem | Message |
|---------|---------|
| No username given | Shows the usage and an example |
| Username has invalid characters | `'name' is not a valid GitHub username.` |
| User does not exist (404) | `User 'name' not found.` |
| Too many requests (403 / 429) | `Rate limit exceeded. Please try again later.` |
| Other GitHub errors | `HTTP Error: <status> - <reason>` |
| No internet or connection failure | `Could not connect to GitHub (...). Check your internet connection.` |
| Slow reply | `Request timed out` or `GitHub took too long to respond` |
| Broken reply | `Failed to read the response from GitHub.` |
| User with no recent activity | `No recent public activity found for user 'name'.` |

GitHub allows a limited number of requests per hour without logging in. If you see the rate limit message, wait and try again.

## Project structure

```
github-user-activity/
├── github_activity.py                  # the application
├── GitHub_Activity_Code_Explained.pdf  # line-by-line explanation (optional)
└── README.md
```

## What I learned

This project has helped me learn how to work with APIs, read JSON data, writing and building reliable python tools and organizing my code making it easy for anyone to read.
