import pelican_katex.rendering as rendering
import pytest
from pelican_katex.rendering import KaTeXError, RenderServer


def test_raises_on_missing_nodejs_binary(tmp_path, monkeypatch):
    missing_bin = tmp_path / "nonexistent_binary_xyz"
    monkeypatch.setattr(rendering, "KATEX_NODEJS_BINARY", str(missing_bin))

    with pytest.raises(KaTeXError, match=str(missing_bin)):
        RenderServer.build_command()


def test_build_command_uses_explicit_katex_path(monkeypatch):
    monkeypatch.setattr(rendering, "KATEX_PATH", "/custom/katex.js")

    cmd = RenderServer.build_command()

    assert "--katex" in cmd
    idx = cmd.index("--katex")
    assert cmd[idx + 1] == "/custom/katex.js"


def test_build_command_resolves_bundled_katex_when_unset(monkeypatch):
    monkeypatch.setattr(rendering, "KATEX_PATH", None)
    monkeypatch.setattr(
        rendering.glob,
        "glob",
        lambda _pattern: ["/pkg/pelican_katex/katex.0.16.9.js"],
    )

    cmd = RenderServer.build_command()

    assert "--katex" in cmd
    idx = cmd.index("--katex")
    assert cmd[idx + 1] == "/pkg/pelican_katex/katex.0.16.9.js"
