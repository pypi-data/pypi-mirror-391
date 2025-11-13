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
"""Header"""
from __future__ import annotations

from datetime import datetime as dt

import panel as pn

from ....core.locales import keys
from ...base.base_app import BaseApp
from .dashboard import display as dashboard_display
from .input import display as input_display
from .secret import display as secret_display


def display(app: BaseApp) -> pn.Column:
    """Displays the main app"""
    pages = {
        app._(keys.NAVIGATION_TEXT_SECRET): secret_display,
        app._(keys.NAVIGATION_TEXT_DASHBOARD): dashboard_display,
        app._(keys.NAVIGATION_CREATE_TABLE): input_display,
    }

    nav = pn.widgets.RadioButtonGroup(
        options=list(pages.keys()),
        orientation="horizontal",
        css_classes=["my-nav-buttons"],
    )

    nav.value = app._(keys.NAVIGATION_TEXT_DASHBOARD)

    main_area = pn.bind(lambda page: pages[page](app), nav)

    dashboard = pn.Column(
        pn.Row(__header(app, nav), sizing_mode="stretch_width"),
        pn.Row(main_area, sizing_mode="stretch_width"),
        pn.Spacer(height=20),
        pn.Row(__footer(), sizing_mode="stretch_width"),
        sizing_mode="stretch_width",
    )

    return dashboard


def __header(app: BaseApp, nav) -> pn.Row:
    return pn.Row(
        pn.pane.HTML(
            app.logo_content, sizing_mode="fixed", css_classes=["logo-wrapper"]
        ),
        pn.Spacer(width=20),
        nav,
        sizing_mode="stretch_width",
        css_classes=["my-nav"],
    )


def __footer() -> pn.Row:
    """Display the app footer."""
    return pn.Row(
        pn.pane.HTML(
            f"&copy; {dt.now().year} Cotality. All rights reserved.",
            sizing_mode="fixed",
            css_classes=["my-footer"],
        ),
        sizing_mode="stretch_width",
        css_classes=["my-footer-wrapper"],
    )
