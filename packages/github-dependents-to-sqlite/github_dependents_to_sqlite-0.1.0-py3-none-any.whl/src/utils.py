import requests
import time

# FTS configuration for full-text search
FTS_CONFIG = {
    "repos": ["name", "description"],
    "users": ["login", "name"],
}

# Views for the database
VIEWS = {
    # Name: (required_tables, SQL)
    "dependent_repos": (
        {"repos", "dependents"},
        """select
  repos.full_name as repo,
  'https://github.com/' || dependent_repos.full_name as dependent,
  dependent_repos.created_at as dependent_created,
  dependent_repos.updated_at as dependent_updated,
  dependent_repos.stargazers_count as dependent_stars,
  dependent_repos.watchers_count as dependent_watchers
from
  dependents
  join repos as dependent_repos on dependents.dependent = dependent_repos.id
  join repos on dependents.repo = repos.id
order by
  dependent_repos.created_at desc""",
    ),
}

# Foreign keys
FOREIGN_KEYS = [
    ("repos", "license", "licenses", "key"),
]


class GitHubError(Exception):
    def __init__(self, message, status_code, headers=None):
        self.message = message
        self.status_code = status_code
        self.headers = headers

    @classmethod
    def from_response(cls, response):
        message = response.json()["message"]
        if "git repository is empty" in message.lower():
            cls = GitHubRepositoryEmpty
        return cls(message, response.status_code, response.headers)


class GitHubRepositoryEmpty(GitHubError):
    pass


def save_user(db, user):
    # Under some conditions, GitHub caches removed repositories with
    # stars and ends up leaving dangling `None` user references.
    if user is None:
        return None

    # Remove all url fields except avatar_url and html_url
    to_save = {
        key: value
        for key, value in user.items()
        if (key in ("avatar_url", "html_url") or not key.endswith("url"))
    }
    # If this user was nested in repo they will be missing several fields
    # so fill in 'name' from 'login' so Datasette foreign keys display
    if to_save.get("name") is None:
        to_save["name"] = to_save["login"]
    return db["users"].upsert(to_save, pk="id", alter=True).last_pk


def fetch_repo(full_name=None, token=None, url=None):
    headers = make_headers(token)
    # Get topics:
    headers["Accept"] = "application/vnd.github.mercy-preview+json"
    if url is None:
        owner, slug = full_name.split("/")
        url = "https://api.github.com/repos/{}/{}".format(owner, slug)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def save_repo(db, repo):
    assert isinstance(repo, dict), "Repo should be a dict: {}".format(repr(repo))
    # Remove all url fields except html_url
    to_save = {
        key: value
        for key, value in repo.items()
        if (key == "html_url") or not key.endswith("url")
    }
    to_save["owner"] = save_user(db, to_save["owner"])
    to_save["license"] = save_license(db, to_save["license"])
    if "organization" in to_save:
        to_save["organization"] = save_user(db, to_save["organization"])
    else:
        to_save["organization"] = None
    repo_id = (
        db["repos"]
        .insert(
            to_save,
            pk="id",
            foreign_keys=(("owner", "users", "id"), ("organization", "users", "id")),
            alter=True,
            replace=True,
            columns={
                "organization": int,
                "topics": str,
                "name": str,
                "description": str,
            },
        )
        .last_pk
    )
    return repo_id


def save_license(db, license):
    if license is None:
        return None
    return db["licenses"].insert(license, pk="key", replace=True).last_pk


def make_headers(token=None):
    headers = {}
    if token is not None:
        headers["Authorization"] = "token {}".format(token)
    return headers


def ensure_foreign_keys(db):
    for expected_foreign_key in FOREIGN_KEYS:
        table, column, table2, column2 = expected_foreign_key
        if (
            expected_foreign_key not in db[table].foreign_keys
            and
            # Ensure all tables and columns exist
            db[table].exists()
            and db[table2].exists()
            and column in db[table].columns_dict
            and column2 in db[table2].columns_dict
        ):
            db[table].add_foreign_key(column, table2, column2)


def ensure_db_shape(db):
    "Ensure FTS is configured and expected FKS, views and (soon) indexes are present"
    # Foreign keys:
    ensure_foreign_keys(db)
    db.index_foreign_keys()

    # FTS:
    existing_tables = set(db.table_names())
    for table, columns in FTS_CONFIG.items():
        if "{}_fts".format(table) in existing_tables:
            continue
        if table not in existing_tables:
            continue
        db[table].enable_fts(columns, create_triggers=True)

    # Views:
    existing_views = set(db.view_names())
    existing_tables = set(db.table_names())
    for view, (tables, sql) in VIEWS.items():
        # Do all of the tables exist?
        if not tables.issubset(existing_tables):
            continue
        db.create_view(view, sql, replace=True)


def get_packages(repo, verbose=False):
    "Get list of packages for a GitHub repository"
    from bs4 import BeautifulSoup

    url = "https://github.com/{}/network/dependents".format(repo)
    if verbose:
        print(f"Fetching packages from: {url}")

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    packages = []
    for item in soup.select(".select-menu-item"):
        package_name = item.get_text(strip=True)
        package_url = item.get("href", "")

        # Extract package_id from URL
        package_id = None
        if "package_id=" in package_url:
            package_id = package_url.split("package_id=")[1].split("&")[0]

        packages.append({
            "name": package_name,
            "id": package_id,
            "url": package_url
        })

    if verbose:
        print(f"Found {len(packages)} packages")

    return packages


def get_dependents_count(repo, package_id=None, verbose=False):
    "Get the total count of dependents for a repository/package"
    from bs4 import BeautifulSoup
    import re

    if package_id:
        url = "https://github.com/{}/network/dependents?package_id={}".format(repo, package_id)
    else:
        url = "https://github.com/{}/network/dependents".format(repo)

    if verbose:
        print(f"Fetching count from: {url}")

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Look for the count in the format "23,089 Repositories"
    # It's in an <a> element with class "btn-link selected"
    count_elem = soup.select_one("a.btn-link.selected")
    if count_elem:
        text = count_elem.get_text(strip=True)
        # Extract number with commas (e.g., "23,089")
        match = re.search(r'([\d,]+)\s*Repositories', text)
        if match:
            count_str = match.group(1).replace(',', '')
            count = int(count_str)
            if verbose:
                print(f"Found {count:,} total dependents")
            return count

    if verbose:
        print("Could not find dependent count")
    return None


def get_last_dependent_repo(db, repo_full_name):
    """Get the last scraped dependent repo for resume functionality

    Returns a dict with 'full_name' and 'id' (repo ID) of the last dependent
    that was scraped for this repo, which can be used for resume.
    GitHub's cursor format is base64-encoded repo ID.
    """
    if not db["dependents"].exists():
        return None

    result = db.execute("""
        SELECT r.full_name, r.id
        FROM repos r
        JOIN dependents d ON r.id = d.dependent
        JOIN repos parent ON d.repo = parent.id
        WHERE parent.full_name = ?
        ORDER BY d.first_seen_utc DESC
        LIMIT 1
    """, [repo_full_name]).fetchone()

    if result:
        return {"full_name": result[0], "repo_id": result[1]}
    return None


def scrape_dependents(repo, package_id=None, verbose=False, resume_from=None):
    """Scrape dependents for a GitHub repository from the dependency graph page

    Args:
        repo: Repository name (e.g., 'owner/repo')
        package_id: Package ID to filter by (optional)
        verbose: Print verbose output
        resume_from: Dict with 'full_name' and 'repo_id', or just a string full_name
                    Will try to use repo_id for direct pagination (cursor = base64(repo_id))
    """
    # Optional dependency:
    from bs4 import BeautifulSoup
    import base64

    # Build initial URL
    if package_id:
        url = "https://github.com/{}/network/dependents?package_id={}".format(repo, package_id)
    else:
        url = "https://github.com/{}/network/dependents".format(repo)

    # Handle resume_from - can be dict with repo_id or string
    resume_repo_id = None
    resume_full_name = None
    if resume_from:
        if isinstance(resume_from, dict):
            resume_full_name = resume_from.get("full_name")
            resume_repo_id = resume_from.get("repo_id")
        else:
            resume_full_name = resume_from

        # Try to use repo_id for direct cursor-based pagination
        if resume_repo_id:
            # GitHub's cursor format: base64-encoded repo ID (as string)
            cursor = base64.b64encode(str(resume_repo_id).encode()).decode()
            url += f"&dependents_after={cursor}"
            if verbose:
                print(f"📍 Resuming with cursor: {cursor} (repo_id={resume_repo_id}, {resume_full_name})")
            # When using cursor, we can start immediately
            found_resume_point = True
            skipped_pages = 0
        else:
            # Fall back to page-skipping method
            if verbose:
                print(f"📍 Resuming from: {resume_full_name}")
                print(f"   Will skip pages until finding repos after this point...")
            found_resume_point = False
            skipped_pages = 0
    else:
        found_resume_point = True
        skipped_pages = 0

    page_num = 0

    while url:
        page_num += 1
        if verbose:
            print(f"Page {page_num}: {url}")
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        repos = [
            a["href"].lstrip("/")
            for a in soup.select("a[data-hovercard-type=repository]")
        ]

        # If we're in resume mode and haven't found the resume point yet
        if not found_resume_point:
            # Check if resume_full_name is on this page
            if resume_full_name in repos:
                found_resume_point = True
                skipped_pages = page_num - 1
                # Yield only repos after the resume point on this page
                resume_index = repos.index(resume_full_name)
                repos_to_yield = repos[resume_index + 1:]
                if verbose:
                    print(f"  ✓ Found resume point! Skipping first {resume_index + 1} repos on this page")
                    print(f"  Yielding {len(repos_to_yield)} repos from this page")
                yield from repos_to_yield
            else:
                # Haven't found resume point yet, skip this entire page
                if verbose:
                    print(f"  ⏭️  Skipping page (before resume point)")
        else:
            # Normal operation: yield all repos (including cursor-based resume)
            if verbose:
                print(f"  Found {len(repos)} repos on this page")
            yield from repos

        # next page?
        try:
            next_link = soup.select(".paginate-container")[0].find("a", string="Next")
        except IndexError:
            break
        if next_link is not None:
            url = next_link["href"]
            time.sleep(1)
        else:
            url = None

    if resume_from and verbose and found_resume_point:
        print(f"✓ Resume completed. Skipped {skipped_pages} page(s)")
