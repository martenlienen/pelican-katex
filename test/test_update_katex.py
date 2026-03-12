import io
import json
import zipfile

import pytest

from scripts import update_katex


class DummyResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None


def test_find_current_version_success(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pkg_dir = tmp_path / "pelican_katex"
    pkg_dir.mkdir()
    bundled = pkg_dir / "katex.0.16.9.js"
    bundled.write_text("// old")

    file_path, version = update_katex.find_current_version()

    assert file_path == "pelican_katex/katex.0.16.9.js"
    assert version == "0.16.9"


def test_find_current_version_fails_with_multiple_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pkg_dir = tmp_path / "pelican_katex"
    pkg_dir.mkdir()
    (pkg_dir / "katex.0.16.8.js").write_text("// old")
    (pkg_dir / "katex.0.16.9.js").write_text("// new")

    with pytest.raises(SystemExit):
        update_katex.find_current_version()


def test_fetch_latest_release_parses_version_and_asset(monkeypatch):
    payload = {
        "tag_name": "v0.16.11",
        "assets": [
            {"name": "other.txt", "browser_download_url": "https://example.invalid/other"},
            {"name": "katex.zip", "browser_download_url": "https://example.invalid/katex.zip"},
        ],
    }

    def fake_urlopen(request):
        assert request.full_url == "https://api.github.com/repos/KaTeX/KaTeX/releases/latest"
        return DummyResponse(json.dumps(payload).encode("utf-8"))

    monkeypatch.setattr(update_katex.urllib.request, "urlopen", fake_urlopen)

    version, zip_url = update_katex.fetch_latest_release()

    assert version == "0.16.11"
    assert zip_url == "https://example.invalid/katex.zip"


def test_download_and_replace_writes_new_file_and_removes_old(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    pkg_dir = tmp_path / "pelican_katex"
    pkg_dir.mkdir()
    old_file = pkg_dir / "katex.0.16.9.js"
    old_file.write_text("old")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zf:
        zf.writestr("katex/katex.js", "new bundled content")

    def fake_urlopen(_url):
        return DummyResponse(zip_buffer.getvalue())

    monkeypatch.setattr(update_katex.urllib.request, "urlopen", fake_urlopen)

    update_katex.download_and_replace("https://example.invalid/katex.zip", str(old_file), "0.16.11")

    new_file = pkg_dir / "katex.0.16.11.js"
    assert new_file.read_text() == "new bundled content"
    assert not old_file.exists()


@pytest.mark.parametrize(
    "current,latest,expected",
    [
        ("0.16.9", "0.16.10", True),
        ("0.16.10", "0.16.10", False),
        ("0.16.11", "0.16.10", False),
    ],
)
def test_is_newer(current, latest, expected):
    assert update_katex.is_newer(current, latest) is expected


def test_main_sets_outputs_for_no_update(monkeypatch, tmp_path):
    output_file = tmp_path / "gh_output.txt"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output_file))

    monkeypatch.setattr(update_katex, "find_current_version", lambda: ("pelican_katex/katex.0.16.11.js", "0.16.11"))
    monkeypatch.setattr(update_katex, "fetch_latest_release", lambda: ("0.16.11", "https://example.invalid/katex.zip"))

    called = {"download": False}

    def fake_download(_zip_url, _old_file, _new_version):
        called["download"] = True

    monkeypatch.setattr(update_katex, "download_and_replace", fake_download)

    update_katex.main()

    assert called["download"] is False
    assert output_file.read_text() == "newer=false\nnew_version=0.16.11\n"


def test_main_sets_outputs_for_update(monkeypatch, tmp_path):
    output_file = tmp_path / "gh_output.txt"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output_file))

    monkeypatch.setattr(update_katex, "find_current_version", lambda: ("pelican_katex/katex.0.16.9.js", "0.16.9"))
    monkeypatch.setattr(update_katex, "fetch_latest_release", lambda: ("0.16.11", "https://example.invalid/katex.zip"))

    calls = []

    def fake_download(zip_url, old_file, new_version):
        calls.append((zip_url, old_file, new_version))

    monkeypatch.setattr(update_katex, "download_and_replace", fake_download)

    update_katex.main()

    assert calls == [("https://example.invalid/katex.zip", "pelican_katex/katex.0.16.9.js", "0.16.11")]
    assert output_file.read_text() == "newer=true\nnew_version=0.16.11\n"
