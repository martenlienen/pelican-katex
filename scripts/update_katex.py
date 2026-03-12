#!/usr/bin/env python3
"""Update the bundled KaTeX file to the latest upstream release."""

import glob
import io
import json
import os
import re
import sys
import urllib.request
import zipfile


def set_output(name, value):
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"{name}={value}\n")
    else:
        print(f"  {name}={value}")


def find_current_version():
    files = glob.glob("pelican_katex/katex.*.js")
    if len(files) != 1:
        print(
            f"Expected exactly one file matching pelican_katex/katex.*.js, "
            f"found {len(files)}"
        )
        for f in files:
            print(f"  {f}")
        sys.exit(1)

    file_path = files[0]
    file_name = os.path.basename(file_path)
    m = re.match(r"^katex\.(\d+\.\d+\.\d+)\.js$", file_name)
    if not m:
        print(f"Could not parse version from file name: {file_name}")
        sys.exit(1)

    return file_path, m.group(1)


def fetch_latest_release():
    url = "https://api.github.com/repos/KaTeX/KaTeX/releases/latest"
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req) as response:
        data = json.load(response)

    version = data["tag_name"].lstrip("v")
    zip_url = None
    for asset in data.get("assets", []):
        if asset.get("name") == "katex.zip":
            zip_url = asset.get("browser_download_url")
            break

    if not zip_url:
        raise SystemExit("katex.zip asset was not found in latest release")

    return version, zip_url


def is_newer(current_version, latest_version):
    current = tuple(int(x) for x in current_version.split("."))
    latest = tuple(int(x) for x in latest_version.split("."))
    return latest > current


def download_and_replace(zip_url, old_file, new_version):
    print(f"Downloading {zip_url} ...")
    with urllib.request.urlopen(zip_url) as response:
        zip_data = response.read()

    with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
        katex_js = zf.read("katex/katex.js")

    new_file = f"pelican_katex/katex.{new_version}.js"
    with open(new_file, "wb") as f:
        f.write(katex_js)
    print(f"Written {new_file}")

    os.remove(old_file)
    print(f"Removed {old_file}")


def main():
    old_file, current_version = find_current_version()
    print(f"Current bundled KaTeX: {current_version} ({old_file})")

    latest_version, zip_url = fetch_latest_release()
    print(f"Latest KaTeX release:  {latest_version}")

    if is_newer(current_version, latest_version):
        print("Newer version available, updating ...")
        download_and_replace(zip_url, old_file, latest_version)
        set_output("newer", "true")
        set_output("new_version", latest_version)
    else:
        print("Bundled KaTeX is already up to date.")
        set_output("newer", "false")
        set_output("new_version", current_version)


if __name__ == "__main__":
    main()
