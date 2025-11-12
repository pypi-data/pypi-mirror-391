import click
import datetime
import pathlib
import os
import sqlite_utils
import time
import json
from src import utils
from src import __version__


@click.group()
@click.version_option(version=__version__, prog_name="github-dependents-to-sqlite")
def cli():
    "Save GitHub package dependents data to a SQLite database with support for specific package selection"


@cli.command()
@click.option(
    "-a",
    "--auth",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    default="auth.json",
    help="Path to save tokens to, defaults to auth.json",
)
def auth(auth):
    "Save authentication credentials to a JSON file"
    click.echo("Create a GitHub personal user token and paste it here:")
    click.echo("Visit: https://github.com/settings/tokens")
    click.echo()
    personal_token = click.prompt("Personal token", hide_input=True)
    if pathlib.Path(auth).exists():
        auth_data = json.load(open(auth))
    else:
        auth_data = {}
    auth_data["github_personal_token"] = personal_token
    open(auth, "w").write(json.dumps(auth_data, indent=4) + "\n")
    click.echo(f"✅ Token saved to {auth}")


@cli.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.argument("repos", type=str, nargs=-1, required=True)
@click.option(
    "-a",
    "--auth",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=True),
    default="auth.json",
    help="Path to auth.json token file",
)
@click.option(
    "-p",
    "--package",
    type=str,
    help="Package name or ID to scrape (skips interactive selection)",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Verbose output",
)
def scrape(db_path, repos, auth, package, verbose):
    "Scrape dependents for specified repos"
    try:
        import bs4
    except ImportError:
        raise click.ClickException("Optional dependency bs4 is needed for this command")

    try:
        from tqdm import tqdm
        use_tqdm = True
    except ImportError:
        use_tqdm = False

    db = sqlite_utils.Database(db_path)
    token = load_token(auth)

    for repo in repos:
        click.echo(f"\n📦 Processing repository: {repo}")

        repo_full = utils.fetch_repo(repo, token)
        utils.save_repo(db, repo_full)

        # Get packages for this repository
        packages = utils.get_packages(repo, verbose)

        package_id = None
        if packages:
            click.echo(f"Found {len(packages)} package(s)")

            if package:
                # User specified package via -p option
                # Try to match by name or ID
                matched_package = None
                for pkg in packages:
                    if pkg["name"] == package or pkg["id"] == package:
                        matched_package = pkg
                        break

                if matched_package:
                    package_id = matched_package["id"]
                    click.echo(f"Using package: {matched_package['name']}")
                else:
                    click.echo(f"⚠️  Package '{package}' not found. Available packages:")
                    for i, pkg in enumerate(packages, 1):
                        click.echo(f"  {i}. {pkg['name']}")
                    raise click.ClickException(f"Package '{package}' not found")
            else:
                # Interactive mode: let user choose
                click.echo("\nAvailable packages:")
                for i, pkg in enumerate(packages, 1):
                    click.echo(f"  {i}. {pkg['name']}")
                click.echo(f"  {len(packages) + 1}. All packages (scrape each one)")
                click.echo(f"  {len(packages) + 2}. Skip package selection (may find fewer dependents)")

                choice = click.prompt(
                    "\nSelect a package",
                    type=int,
                    default=len(packages) + 1
                )

                if choice <= len(packages):
                    # User selected a specific package
                    selected_package = packages[choice - 1]
                    package_id = selected_package["id"]
                    click.echo(f"Selected: {selected_package['name']}")
                elif choice == len(packages) + 1:
                    # Scrape all packages
                    click.echo("Scraping all packages...")
                    scrape_all_packages(db, repo, repo_full, packages, token, verbose, use_tqdm)
                    continue
                else:
                    # Skip package selection
                    click.echo("Skipping package selection (using default page)")
                    package_id = None
        else:
            click.echo("No packages found, using default dependents page")

        # Get total count for progress bar
        total_count = utils.get_dependents_count(repo, package_id, verbose)
        if total_count:
            click.echo(f"Total dependents: {total_count:,}")

        # Check if we should resume from last position
        resume_from = utils.get_last_dependent_repo(db, repo)
        existing_count = 0
        if resume_from:
            # Count existing dependents for progress bar
            existing_count = db.execute("""
                SELECT COUNT(*)
                FROM dependents d
                JOIN repos parent ON d.repo = parent.id
                WHERE parent.full_name = ?
            """, [repo]).fetchone()[0]
            click.echo(f"📍 Resuming from last position ({existing_count} already scraped)")
            click.echo(f"   Last scraped: {resume_from['full_name']}")
            if resume_from.get('repo_id'):
                import base64
                cursor = base64.b64encode(str(resume_from['repo_id']).encode()).decode()
                click.echo(f"   Using cursor: {cursor} (repo_id={resume_from['repo_id']})")

        # Scrape dependents for the selected package (or no package)
        dependents_count = 0

        if use_tqdm and total_count:
            # Use generator with tqdm and known total
            pbar = tqdm(total=total_count, desc="Scraping dependents", unit="repo", initial=existing_count)
            dependent_repos_iter = utils.scrape_dependents(repo, package_id, verbose, resume_from)
        else:
            # Collect all first if no total count
            dependent_repos_iter = utils.scrape_dependents(repo, package_id, verbose, resume_from)
            pbar = None

        for dependent_repo in dependent_repos_iter:
            if pbar:
                pbar.update(1)
            # Don't fetch repo details if it's already in our DB
            existing = list(db["repos"].rows_where("full_name = ?", [dependent_repo]))
            dependent_id = None
            if not existing:
                dependent_full = utils.fetch_repo(dependent_repo, token)
                time.sleep(1)
                utils.save_repo(db, dependent_full)
                dependent_id = dependent_full["id"]
            else:
                dependent_id = existing[0]["id"]
            # Only insert if it isn't already there:
            if not db["dependents"].exists() or not list(
                db["dependents"].rows_where(
                    "repo = ? and dependent = ?", [repo_full["id"], dependent_id]
                )
            ):
                db["dependents"].insert(
                    {
                        "repo": repo_full["id"],
                        "dependent": dependent_id,
                        "first_seen_utc": datetime.datetime.utcnow().isoformat(),
                    },
                    pk=("repo", "dependent"),
                    foreign_keys=(
                        ("repo", "repos", "id"),
                        ("dependent", "repos", "id"),
                    ),
                )
                dependents_count += 1

        if pbar:
            pbar.close()

        # Show summary with context
        if existing_count > 0:
            total_now = existing_count + dependents_count
            click.echo(f"✅ Found {dependents_count} new dependent(s) (total: {total_now})")
        else:
            click.echo(f"✅ Found {dependents_count} new dependent(s)")

    utils.ensure_db_shape(db)
    click.echo("\n🎉 Done!")


def scrape_all_packages(db, repo, repo_full, packages, token, verbose, use_tqdm):
    "Helper function to scrape dependents for all packages"
    from tqdm import tqdm as tqdm_func

    package_iterator = tqdm_func(packages, desc="Processing packages", unit="pkg") if use_tqdm else packages

    for pkg in package_iterator:
        pkg_name_short = pkg['name'][:30] if len(pkg['name']) > 30 else pkg['name']

        if use_tqdm:
            package_iterator.set_description(f"Package: {pkg_name_short}")
        else:
            click.echo(f"\nProcessing package: {pkg['name']}")

        # Get total count for this package
        total_count = utils.get_dependents_count(repo, pkg["id"], verbose)
        if total_count and not use_tqdm:
            click.echo(f"  Total dependents: {total_count:,}")

        # Check for resume point for this package
        resume_from = utils.get_last_dependent_repo(db, repo)
        existing_count = 0
        if resume_from:
            existing_count = db.execute("""
                SELECT COUNT(*)
                FROM dependents d
                JOIN repos parent ON d.repo = parent.id
                WHERE parent.full_name = ?
            """, [repo]).fetchone()[0]

        # Create progress bar for dependents if we have a count
        if use_tqdm and total_count:
            dep_pbar = tqdm_func(total=total_count, desc=f"  └─ {pkg_name_short}", unit="repo", leave=False, initial=existing_count)
        else:
            dep_pbar = None

        dependents_count = 0
        for dependent_repo in utils.scrape_dependents(repo, pkg["id"], verbose, resume_from):
            if dep_pbar:
                dep_pbar.update(1)
            existing = list(db["repos"].rows_where("full_name = ?", [dependent_repo]))
            dependent_id = None
            if not existing:
                try:
                    dependent_full = utils.fetch_repo(dependent_repo, token)
                    time.sleep(1)
                    utils.save_repo(db, dependent_full)
                    dependent_id = dependent_full["id"]
                except Exception as e:
                    if verbose:
                        click.echo(f"⚠️  Error fetching {dependent_repo}: {e}")
                    continue
            else:
                dependent_id = existing[0]["id"]

            if not db["dependents"].exists() or not list(
                db["dependents"].rows_where(
                    "repo = ? and dependent = ?", [repo_full["id"], dependent_id]
                )
            ):
                db["dependents"].insert(
                    {
                        "repo": repo_full["id"],
                        "dependent": dependent_id,
                        "first_seen_utc": datetime.datetime.utcnow().isoformat(),
                    },
                    pk=("repo", "dependent"),
                    foreign_keys=(
                        ("repo", "repos", "id"),
                        ("dependent", "repos", "id"),
                    ),
                )
                dependents_count += 1

        if dep_pbar:
            dep_pbar.close()

        if not use_tqdm:
            click.echo(f"  Found {dependents_count} dependent(s) for {pkg['name']}")


def load_token(auth):
    try:
        token = json.load(open(auth))["github_personal_token"]
    except (KeyError, FileNotFoundError):
        token = None
    if token is None:
        # Fallback to GITHUB_TOKEN environment variable
        token = os.environ.get("GITHUB_TOKEN") or None
    return token
