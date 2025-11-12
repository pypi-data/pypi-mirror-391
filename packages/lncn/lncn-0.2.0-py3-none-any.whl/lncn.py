import argparse
import os
import re
import fnmatch

from pathlib import Path

USE_COLOR: bool = not os.system("color")

def throw(process: str = "argparse") -> None:
    err: str

    if process == "argparse":
        err = f"ERROR: Could not parse the given arguments, check the syntax of your command"
    else:
        pass
    
    if USE_COLOR:
        err = "\033[91m {}\033[00m".format(err)
    
    print(err)

def list_files_recursive(base_dir: str, include: list[str] | None = None) -> list[Path]:
    base_path = Path(base_dir)
    results = []

    if include is None:
        results = [p for p in base_path.rglob('*') if p.is_file()]
    else:
        for name in include:
            if any(ch in name for ch in ['*', '?', '[', ']']):
                results.extend(p for p in base_path.rglob(name) if p.is_file())
            else:
                for path in base_path.rglob(name):
                    if path.is_file():
                        results.append(path)
                    elif path.is_dir():
                        results.extend(p for p in path.rglob('*') if p.is_file())

    return results

def file_count(path: str,
               ignore_empty_line: bool = True,
               ignore_multi_line_comments: bool = True,
               ignore_single_line_comments: bool = True,
               ignore_bracket_only_lines: bool = True) -> int:
    
    c_style_avoid_python = path.endswith((".c",".h",".cpp","hpp",".cc",".hh",".c++",".h++",".m",".mm",".C",".M"))

    if "_KEEPB" in globals():
        ignore_bracket_only_lines = False

    try:
        with open(path, "r", encoding="utf-8") as file:
            count = 0
            
            content = file.read()

            if ignore_multi_line_comments:
                content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL) # C-style multi line
                content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL) # HTML-style multi line
                content = re.sub(r'^""".*?"""', '', content, flags=re.DOTALL) # Python-style multi line
                content = re.sub(r'^@doc raw""".*?"""', '', content, flags=re.DOTALL) # Julia version of Python-style

            for line in content.splitlines():
                if ignore_single_line_comments:
                    line = line.strip()

                    # if the file possibly has preprocessor commands, don't check python-style comments to avoid false positives
                    if not c_style_avoid_python: 
                        line = re.sub(r'^#.*$', '', line) # Python-style single line

                    line = re.sub(r'^//.*$', '', line) # C-style single line
                    line = re.sub(r'^!.*$', '', line) # Fortran-style single line
                    line = re.sub(r'^;.*$', '', line) # Assembly-style single line

                if ignore_bracket_only_lines:
                    line = re.sub("|".join([r'\{', r'\}', r'\[', r'\]', r'\(', r'\)', r';']), '', line)

                if ignore_empty_line and not line:
                    continue

                count += 1

        return count
    except UnicodeDecodeError:
        return 0

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="lncn",
        description="Simple Python CLI to count SLOC in a codebase"
    )

    parser.add_argument(
        "path",
        type=str,
        default=None,
        help="Path to the directory or file that will be counted"
    )

    parser.add_argument(
        "-i", "--ignore",
        nargs="+",
        default=[],
        help="File/directory paths to ignore in the count."
    )

    parser.add_argument(
        "-k", "--keep",
        action="store_true",
        help="Don't use the default list of files to ignore (this will include README, .git/, etc in the count)"
    )

    parser.add_argument(
        "-b", "--braces",
        action="store_true",
        help="Keep lines with only braces and/or brackets as part of the count"
    )

    args = parser.parse_args()

    path = args.path
    
    if args.keep:
        ignore = []
    else:
        ignore = [
            ".git",
            ".gitignore",
            ".gitattributes",
            ".gitmodules",
            ".vscode",
            ".vs",
            ".editorconfig",
            ".prettierrc",
            ".eslintrc",
            "Jenkinsfile",
            ".travis.yml",
            ".DS_Store",
            "build",
            "dist",
            "target",
            "*.class",
            "*.o",
            "*.obj",
            "*.exe",
            "*.dll",
            "*.zip",
            "*.tar.gz",
            "*.whl",
            "*.jar",
            "*.war",
            "*.jpg",
            "*.jpeg",
            "*.png",
            "*.gif",
            "*.svg",
            "*.ico",
            "*.mp3",
            "*.flac",
            "*.wav",
            "*.mp4",
            "*.mov",
            "*.ttf",
            "*.woff",
            "*.eot",
            "*.json",
            "*.xml",
            "*.csv",
            "*.yaml",
            "*.yml",
            "*.ini",
            "*.properties",
            "*.sqlite",
            "*.db",
            "*.log"
            "*/README*",
            "LICENSE*",
            "UNLICENSE*",
            "COPYING*",
            "CHANGELOG*",
            "NEWS*",
            "HISTORY*",
            "CONTRIBUTING*",
            "AUTHORS*",
            "SOURCES*",
            "PKG-INFO",
            "*.txt",
            "*.md",
        ]

    for r in args.ignore:
        ignore.append(r)

    ignore = list_files_recursive(path, include=ignore)

    if args.braces:
        global _KEEPB
        _KEEPB = True

    if path is None:
        throw()
        return 1
    else:
        if os.path.isfile(path):
            count = file_count(path)
        else:
            files = [str(f.resolve()) for f in list_files_recursive(path) if f not in ignore]
            count = sum(map(file_count, files))
        
    print(count)
    return 0

if __name__ == "__main__":
    main()