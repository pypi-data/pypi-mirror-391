#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: test_cli.py
Author: Maria Kevin
Created: 2025-11-12
Description: Tests for CLI application
"""

__author__ = "Maria Kevin"
__version__ = "0.1.6"


def test_cli_app():
    from typer.testing import CliRunner
    from player.main import app

    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
