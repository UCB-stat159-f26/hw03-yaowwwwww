"""Automated tests must never access a live server."""

import socket

import pytest
import requests


def _no_network(*args, **kwargs):
    raise AssertionError("Network access is forbidden in automated tests.")


@pytest.fixture(autouse=True)
def block_network(monkeypatch):
    monkeypatch.setattr(requests.sessions.Session, "request", _no_network)
    monkeypatch.setattr(socket.socket, "connect", _no_network)
    monkeypatch.setattr(socket.socket, "connect_ex", _no_network)
    monkeypatch.setattr(socket, "getaddrinfo", _no_network)
