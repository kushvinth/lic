import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
import httpx
from rich.console import Console
from rich.panel import Panel
import questionary

console = Console()


def get_git_name():
    try:
        result = subprocess.run(["git", "config", "--global", "--get", "user.name"],
                              capture_output=True, text=True, timeout=2)
        return result.stdout.strip() if result.returncode == 0 else None
    except:
        return None


def fetch_licenses():
    response = httpx.get("https://api.github.com/licenses", timeout=10.0)
    response.raise_for_status()
    return {lic["key"]: lic for lic in response.json()}

# Fetching only the required license (if provided as an arg) to enhance speed
def get_license(key):
    response = httpx.get(f"https://api.github.com/licenses/{key}", timeout=10.0)
    response.raise_for_status()
    return response.json().get("body", "")


def render_license(content, author, year):
    replacements = {"[year]": year, "[fullname]": author, "[yyyy]": year,
                   "[name of copyright owner]": author, "[NAME OF COPYRIGHT OWNER]": author}
    for old, new in replacements.items():
        content = content.replace(old, new) ## Goated Dic Play from StackOverflow 
    return content


def get_license_key_interactive(licenses):
    """Interactive selection of license key from available licenses."""
    keys = list(licenses.keys())
    selected = questionary.select(
        "Choose a license:",
        choices=[licenses[k]["name"] for k in keys],
        use_arrow_keys=True,
        style=questionary.Style([
            ('qmark', 'fg:#673ab7 bold'), ('question', 'bold'),
            ('answer', 'fg:#00ff00 bold'), ('pointer', 'fg:#673ab7 bold'),
            ('highlighted', 'fg:#00ff00 bold')
        ])
    ).ask()
    
    if not selected:
        return None
    
    return keys[[licenses[k]["name"] for k in keys].index(selected)]


def get_author_input(provided_author=None, non_interactive=False):
    """Get author from arguments, git config, or interactive prompt."""
    if provided_author:
        console.print(f"[green]✓ Author: {provided_author}[/green]")
        return provided_author
    
    if non_interactive:
        git_name = get_git_name()
        if git_name:
            console.print(f"[green]✓ Author: {git_name} (from git config)[/green]")
            return git_name
        raise ValueError("Author required in non-interactive mode (use --author or set git user.name)")
    
    git_name = get_git_name()
    author = questionary.text(
        "Author:",
        default=git_name if git_name else "",
        instruction="",
        style=questionary.Style([
            ('qmark', 'fg:#673ab7 bold'), ('question', 'bold'),
            ('answer', 'fg:#00ff00 bold')
        ])
    ).ask()
    
    print("\033[A\033[K", end="")
    console.print(f"[green]✓ Author: {author}[/green]")
    return author


def get_year_input(provided_year=None, non_interactive=False):
    """Get year from arguments or interactive prompt."""
    if provided_year:
        console.print(f"[green]✓ Year: {provided_year}[/green]")
        return provided_year
    
    if non_interactive:
        current_year = str(datetime.now().year)
        console.print(f"[green]✓ Year: {current_year} (current year)[/green]")
        return current_year
    
    year = questionary.text(
        "Year:",
        default=str(datetime.now().year),
        instruction="",
        style=questionary.Style([
            ('qmark', 'fg:#673ab7 bold'), ('question', 'bold'),
            ('answer', 'fg:#00ff00 bold')
        ])
    ).ask()
    
    print("\033[A\033[K", end="")
    console.print(f"[green]✓ Year: {year}[/green]")
    return year


def save_license(content):
    """Save license content to LICENSE file."""
    Path("LICENSE").write_text(content)


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Generate licenses from GitHub",
        prog="lic"
    )
    parser.add_argument(
        "-l", "--license",
        help="License key (e.g., mit, apache-2.0, gpl-3.0)",
        metavar="LICENSE"
    )
    parser.add_argument(
        "-a", "--author",
        help="Author/copyright holder name",
        metavar="AUTHOR"
    )
    parser.add_argument(
        "-y", "--year",
        help="Year for the license",
        metavar="YEAR"
    )
    parser.add_argument(
        "-n", "--non-interactive",
        action="store_true",
        help="Disable interactive prompts; --license required; --author optional (uses git config if available); --year defaults to current year"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite LICENSE file if it exists"
    )
    args = parser.parse_args()
    
    try:
        # Check for existing LICENSE file
        license_path = Path("LICENSE")
        if license_path.exists() and not args.force:
            if args.non_interactive:
                raise FileExistsError("LICENSE already exists. Use --force to overwrite.")
            else:
                overwrite = questionary.confirm(
                    "LICENSE file already exists. Overwrite?",
                    default=False
                ).ask()
                print("\033[A\033[K", end="")
                if not overwrite:
                    console.print("[yellow]Cancelled[/yellow]")
                    return
        
        # Get license key
        if args.license:
            key = args.license
            console.print(f"[green]✓ {key}[/green]")
        else:
            if args.non_interactive:
                raise ValueError("License required in non-interactive mode (use --license)")
            console.print("[bold]Loading licenses...[/bold]")
            with console.status("[bold cyan]Fetching from GitHub...", spinner="dots"):
                licenses = fetch_licenses()
            console.print(f"[dim]Found {len(licenses)} licenses[/dim]\n")
            
            key = get_license_key_interactive(licenses)
            if not key:
                return console.print("\n[yellow]Cancelled[/yellow]")
            console.print(f"[green]✓ {licenses[key]['name']}[/green]")
        
        # Get author and year
        author = get_author_input(args.author, args.non_interactive)
        year = get_year_input(args.year, args.non_interactive)
        
        # Generate and save license
        with console.status("[bold cyan]Generating license..."):
            content = render_license(get_license(key), author, year)
            save_license(content)
        
        console.print("[green]✔ License created successfully[/green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/yellow]")
    except Exception as e:
        console.print(Panel(f"[bold red]✗ Error:[/bold red]\n{e}", border_style="red", expand=False))
        sys.exit(1)


if __name__ == "__main__":
    main()