import importlib
import logging
import subprocess
import sys
import time
from pathlib import Path

from thkit.markup import TextDecor


#####ANCHOR: Customize Logger with colors
class ColorLogger(logging.Logger):
    """Logger subclass that supports `color` argument for console output."""

    def _log_with_color(self, level, msg, *args, color=None, **kwargs):
        ### Log plain text (for file handler only)
        super().log(level, msg, *args, **kwargs)

        ### Print Colored message to console
        theme = {
            "info": "white",
            "warning": "yellow",
            "error": "red",
            "critical": "red",
            "debug": "green",
        }
        if color:
            colored_msg = TextDecor(msg).mkcolor(color)
        elif level >= logging.ERROR:
            colored_msg = TextDecor(msg).mkcolor(theme["error"])
        elif level >= logging.WARNING:
            colored_msg = TextDecor(msg).mkcolor(theme["warning"])
        elif level >= logging.INFO:
            colored_msg = TextDecor(msg).mkcolor(theme["info"])
        else:
            colored_msg = msg  # no color

        time_str = TextDecor(time.strftime("%b%d %H:%M")).mkcolor("bright_black")

        for key, color in zip(theme.keys(), ["green", "yellow", "red", "red", "green"]):
            if level == getattr(logging, key.upper()):
                level_str = TextDecor(f"{key.upper()}").mkcolor(color)
                break
        print(f"{time_str} {level_str}: {colored_msg}")
        return

    def info(self, msg, *args, color=None, **kwargs):
        self._log_with_color(logging.INFO, msg, *args, color=color, **kwargs)

    def warning(self, msg, *args, color=None, **kwargs):
        self._log_with_color(logging.WARNING, msg, *args, color=color, **kwargs)

    def error(self, msg, *args, color=None, **kwargs):
        self._log_with_color(logging.ERROR, msg, *args, color=color, **kwargs)


def create_logger(
    name: str = None,
    log_file: str = None,
    level: str = "INFO",
    level_logfile: str = None,
) -> logging.Logger:
    """Create a logger that supports `color` argument per message, to colorize console output and plain-text logfile."""
    logging.setLoggerClass(ColorLogger)
    logger = logging.getLogger(name or __name__)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.hasHandlers():
        ### File handler only (no console handler, as ColorLogger prints to console directly)
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            fh = logging.FileHandler(log_file, mode="a")
            fh.setLevel(getattr(logging, (level_logfile or level).upper(), logging.INFO))
            fmt = logging.Formatter("%(asctime)s | %(levelname)s: %(message)s", "%Y%b%d %H:%M:%S")
            fh.setFormatter(fmt)
            logger.addHandler(fh)
    return logger


def write_to_logfile(logger: object, text: str):
    """Retrieve logfile name from logger and write text to it. Useful when want to write unformat text to the same logfile used by logger."""
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            logfile = handler.baseFilename
            with open(logfile, "a") as f:
                f.write(text)
    return


#####ANCHOR: Packages tools
def check_package(
    package_name: str,
    auto_install: bool = False,
    git_repo: str = None,
    conda_channel: str = None,
):
    """Check if the required packages are installed"""
    try:
        importlib.import_module(package_name)
    except ImportError:
        if auto_install:
            install_package(package_name, git_repo, conda_channel)
        else:
            raise ImportError(
                f"Required package `{package_name}` is not installed. Please install it.",
            )
    return


def install_package(
    package_name: str,
    git_repo: str | None = None,
    conda_channel: str | None = None,
) -> None:
    """Install the required package:
        - Default using: `pip install -U {package_name}`
        - If `git_repo` is provided: `pip install -U git+{git_repo}`
        - If `conda_channel` is provided: `conda install -c {conda_channel} {package_name}`

    Args:
        package_name (str): package name
        git_repo (str): git path for the package. Default: None. E.g., http://somthing.git
        conda_channel (str): conda channel for the package. Default: None. E.g., conda-forge
    """
    if git_repo:
        cmd = ["pip", "install", "-U", f"git+{git_repo}"]
    elif conda_channel:
        cmd = ["conda", "install", "-c", conda_channel, package_name, "-y"]
    else:
        cmd = ["pip", "install", "-U", package_name]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to install `{package_name}`: {e}")
    return


def dependency_info(packages=["numpy", "polars", "thkit", "ase"]) -> str:
    """Get the dependency information

    Note:
        Use `importlib` instead of `__import__` for clarity.
    """
    lines = [TextDecor(" Dependencies ").fill_center(fill="-", length=70)]
    for pkg in packages:
        try:
            mm = importlib.import_module(pkg)
            ver = getattr(mm, "__version__", "unknown").split("+")[0]
            path = getattr(mm, "__path__", ["unknown path"])[0]
            lines.append(f"{pkg:>12}  {ver:<12} {Path(path).as_posix()}")
        except ImportError:
            lines.append(f"{pkg:>12}  {'unknown':<12} ")
        except Exception:
            lines.append(f"{pkg:>12}  {'':<12} unknown version or path")
    ### Python version
    lines.append(
        f"{'python':>12}  {sys.version.split(' ')[0]:<12} {Path(sys.executable).as_posix()}"
    )
    return "\n".join(lines) + "\n"
