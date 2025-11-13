# Copyright 2025 Cotality
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Cotality Panel Application"""
from __future__ import annotations

import panel as pn

from ...core.clgxtyping import LogLevel
from ...core.platform import Platform
from ..base.base_app import BaseApp, UIFramework
from .modules import layout as app_layout


class ClipApp(BaseApp):
    """Panel Workbench Application Client."""

    def __init__(self, platform: Platform):
        """Initialize the Workbench Application Client.

        Args:
            platform (Platform): The platform instance to use.
        """
        super().__init__(
            platform=platform,
            ui_framework=UIFramework.PANEL,
        )

        pn.config.raw_css.append(self.style)
        pn.config.loading_spinner = "petal"
        pn.config.loading_color = "black"

    def toggle_loading(self):
        """Toggles the loading screen on and off"""
        if not hasattr(self, "_dashboard"):
            return
        self._dashboard.loading = not self._dashboard.loading

    def display(self):
        """Display the application UI."""

        pn.extension("plotly", "tabulator")

        self._dashboard = app_layout.display(self)
        self._dashboard.servable()

        return self._dashboard
