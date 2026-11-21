"""Tests for application settings."""

from tgedr_ghragchat.settings import Settings


def test_environment_overrides_dotenv_values(monkeypatch, tmp_path) -> None:
    """Read a setting from dotenv and prefer an environment variable when present."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "SOURCE_IMPL=example.source.DotenvSource\nSECRET_KEY=dotenv-secret\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("SOURCE_IMPL", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setenv("SECRET_KEY", "environment-secret")

    settings = Settings(_env_file=env_file)
    assert settings.source_impl == "example.source.DotenvSource"
    assert settings.secret_key == "environment-secret"
