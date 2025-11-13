# AxeProfiler is a program designed to make saving/switching configurations for
# bitcoin miner devices simpler and more efficient.

# Copyright (C) 2025 [DC] Celshade <ggcelshade@gmail.com>

# This file is part of AxeProfiler.

# AxeProfiler is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.

# AxeProfiler is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# AxeProfiler. If not, see <https://www.gnu.org/licenses/>.

from os import system

from rich.panel import Panel
from rich.prompt import Confirm
from rich import print as rprint

from .cli import Cli


def show_notice() -> bool:
    try:
        root = __file__.split('src')[0]
        notice = f"{root}.notice"
        copying = f"{root}COPYING"

        with open(notice, 'r') as f:
            notice = f.read()

        system("clear")  # NOTE @Linux; handle MAC/Windows
        rprint(Panel(f"{notice}[bold magenta]{copying}.",
                     title="[bold bright_cyan]Copyright Notice",
                     width=80))
        return Confirm.ask("Do you want to start the program?", default='y')
    except FileNotFoundError:
        msg = ''.join(("Could not render the [red]copyright[/] notice.\n",
                        "Please see line 4 of any source file or ",
                        f"[red]{copying}[/] for more details."))
        rprint(Panel(msg, title="[bold bright_cyan]Copyright Notice",
                        width=80))
        return Confirm.ask("Do you want to start the program?", default='y')


def main() -> None:  # NOTE Program entry point
    # TODO add title screen?
    if show_notice():
        cli = Cli()
        cli.session()


if __name__ == "__main__":
    main()
