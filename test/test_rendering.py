import pelican_katex.rendering as rendering
import pytest
from pelican_katex.rendering import KaTeXError, RenderServer


def test_raises_on_missing_nodejs_binary(tmp_path, monkeypatch):
    missing_bin = tmp_path / "nonexistent_binary_xyz"
    monkeypatch.setattr(rendering, "KATEX_NODEJS_BINARY", str(missing_bin))

    with pytest.raises(KaTeXError, match=str(missing_bin)):
        RenderServer.build_command()
