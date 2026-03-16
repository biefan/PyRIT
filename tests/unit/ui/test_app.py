# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from pyrit.ui import app as ui_app


def test_is_app_running_returns_false_on_non_windows(monkeypatch):
    monkeypatch.setattr(ui_app.sys, "platform", "linux")

    assert ui_app.is_app_running() is False


def test_create_mutex_returns_true_on_non_windows(monkeypatch):
    monkeypatch.setattr(ui_app.sys, "platform", "linux")

    assert ui_app.create_mutex() is True
