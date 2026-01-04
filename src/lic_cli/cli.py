import sys
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
        result = subprocess.run(
            ["git", "config", "--global", "--get", "user.name"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except:
        return None


def fetch_licenses():
    response = httpx.get("https://api.github.com/licenses", timeout=10.0)
    response.raise_for_status()
    return {lic["key"]: lic for lic in response.json()}


def get_license(key):
    response = httpx.get(f"https://api.github.com/licenses/{key}", timeout=10.0)
    response.raise_for_status()
    return response.json().get("body", "")


def render_license(content, author, year):
    replacements = {
        "[year]": year,
        "[fullname]": author,
        "[yyyy]": year,
        "[name of copyright owner]": author,
        "[NAME OF COPYRIGHT OWNER]": author,
    }
    for old, new in replacements.items():
        content = content.replace(old, new)  ## Goated Dic Play from StackOverflow
    return content


def main():
    # console.print(Panel("[bold cyan]License Generator[/bold cyan]\n[dim]Generate licenses from GitHub[/dim]",
    #                     border_style="cyan", expand=False))
    # console.print()

    try:
        console.print("[bold]Loading licenses...[/bold]")
        with console.status("[bold cyan]Fetching from GitHub...", spinner="dots"):
            licenses = fetch_licenses()

        console.print(f"[dim]Found {len(licenses)} licenses[/dim]\n")

        keys = list(licenses.keys())
        selected = questionary.select(
            "Choose a license:",
            choices=[licenses[k]["name"] for k in keys],
            use_arrow_keys=True,
            style=questionary.Style(
                [
                    ("qmark", "fg:#673ab7 bold"),
                    ("question", "bold"),
                    ("answer", "fg:#00ff00 bold"),
                    ("pointer", "fg:#673ab7 bold"),
                    ("highlighted", "fg:#00ff00 bold"),
                ]
            ),
        ).ask()

        if not selected:
            return console.print("\n[yellow]Cancelled[/yellow]")

        key = keys[[licenses[k]["name"] for k in keys].index(selected)]
        console.print(f"[green]✓ {selected}[/green]")

        git_name = get_git_name()
        author = questionary.text(
            "Author:",
            default=git_name if git_name else "",
            instruction="",
            style=questionary.Style(
                [
                    ("qmark", "fg:#673ab7 bold"),
                    ("question", "bold"),
                    ("answer", "fg:#00ff00 bold"),
                ]
            ),
        ).ask()

        # Move cursor up and print checkmark
        print("\033[A\033[K", end="")
        console.print(f"[green]✓ Author: {author}[/green]")

        year = questionary.text(
            "Year:",
            default=str(datetime.now().year),
            instruction="",
            style=questionary.Style(
                [
                    ("qmark", "fg:#673ab7 bold"),
                    ("question", "bold"),
                    ("answer", "fg:#00ff00 bold"),
                ]
            ),
        ).ask()

        # Move cursor up and print checkmark
        print("\033[A\033[K", end="")
        console.print(f"[green]✓ Year: {year}[/green]")

        with console.status("[bold cyan]Generating license..."):
            content = render_license(get_license(key), author, year)
            Path("LICENSE").write_text(content)

        console.print("[green]✔ License created successfully[/green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/yellow]")
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]✗ Error:[/bold red]\n{e}", border_style="red", expand=False
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
