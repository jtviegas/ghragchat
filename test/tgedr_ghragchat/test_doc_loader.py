"""Tests for document loading utilities."""

from types import SimpleNamespace
from unittest.mock import Mock

from tgedr_ghragchat import doc_loader


def test_load_lists_and_gets_documents_from_configured_source(monkeypatch) -> None:
    """Pass the requested source context and target to the configured source."""
    source = Mock()
    source.list.return_value = ["document.md"]
    settings = SimpleNamespace(source_impl="tests.fake_source.FakeSource")
    monkeypatch.setattr(doc_loader, "Settings", lambda: settings)
    load_source = Mock(return_value=lambda: source)
    monkeypatch.setattr(doc_loader.UtilsReflection, "load_subclass_from_module", load_source)
    loader = doc_loader.DocLoader()

    loader.load("input", "output")

    load_source.assert_called_once_with("tests.fake_source", "FakeSource", doc_loader.Source)
    source.list.assert_called_once_with(context={"source": "input", "suffix": ".md"})
    source.get.assert_called_once_with({"files": ["document.md"], "target": "output"})


def test_load_uses_requested_suffix(monkeypatch) -> None:
    """Pass a non-default suffix to source listing."""
    source = Mock()
    settings = SimpleNamespace(source_impl="tests.fake_source.FakeSource")
    monkeypatch.setattr(doc_loader, "Settings", lambda: settings)
    monkeypatch.setattr(
        doc_loader.UtilsReflection,
        "load_subclass_from_module",
        Mock(return_value=lambda: source),
    )
    loader = doc_loader.DocLoader()

    loader.load("input", "output", suffix=".pdf")

    source.list.assert_called_once_with(context={"source": "input", "suffix": ".pdf"})
    source.get.assert_called_once_with({"files": source.list.return_value, "target": "output"})
