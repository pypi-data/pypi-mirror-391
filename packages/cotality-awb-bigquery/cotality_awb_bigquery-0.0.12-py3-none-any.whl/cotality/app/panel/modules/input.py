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
from __future__ import annotations

import re

import panel as pn

from ....core.locales import keys
from ...base.base_app import BaseApp


def display(
    app: BaseApp,
    title_key: str = keys.TEXT_ADD_INPUT_TABLE_DIALOG,
    subtitle_key: str = keys.TEXT_ADD_INPUT_TABLE_EXPLANATION,
) -> pn.Column:
    """Select the input table for the Clip Lookup Panel app.
    Args:
        platform (Platform): The platform instance.
    """

    main_title = pn.pane.Markdown(f"# {app._(title_key)}", sizing_mode="stretch_width")
    subtitle = pn.pane.Markdown(
        f"### {app._(subtitle_key)}", sizing_mode="stretch_width"
    )
    table_name = pn.widgets.TextInput(
        name=app._(keys.TEXT_ADD_INPUT_TABLE_DIALOG), sizing_mode="stretch_width"
    )

    create_button = pn.widgets.Button(
        name=app._(keys.BUTTON_CREATE_TABLE_DIALOG),
        button_type="primary",
        sizing_mode="stretch_width",
    )

    create_output = pn.Column(sizing_mode="stretch_width")

    def _create(event):
        validation, info = validate_input_table_name(app, table_name.value)
        if not validation:
            create_output.objects = [pn.pane.Alert(info, alert_type="danger")]
            return

        tables = []
        try:
            tables = app.clip_client.get_clip_input_tables()
        except Exception:
            create_output.objects = [
                pn.pane.Alert(app._(keys.SYS_ERROR_GET_TABLES), alert_type="danger")
            ]
            return

        if table_name.value in tables:
            create_output.objects = [
                pn.pane.Alert(
                    app._(keys.ERROR_INPUT_TABLE_ALREADY_EXISTS), alert_type="danger"
                )
            ]
            return

        try:
            app.clip_client.create_clip_input_table(table_name.value)
        except Exception:
            create_output.objects = [
                pn.pane.Alert(app._(keys.SYS_ERROR_CREATE_TABLE), alert_type="danger")
            ]
            return

        create_output.objects = [
            pn.pane.Alert(
                app._(keys.SUCCESS_INPUT_TABLE_CREATION), alert_type="success"
            )
        ]

    # wrapper for loading screen
    def _create_loading(event):
        app.toggle_loading()
        _create(event)
        app.toggle_loading()

    create_button.on_click(_create_loading)

    return pn.Column(
        main_title,
        subtitle,
        table_name,
        create_button,
        create_output,
        sizing_mode="stretch_width",
        css_classes=["center-wrapper"],
    )


def validate_input_table_name(app: BaseApp, table_name: str) -> (bool, str):
    """Validate the input table name.

    Args:
        table_name (str): The name of the input table.

    Returns:
        bool: True if valid, False otherwise.
    """

    table_name = table_name.strip().lower()
    if len(table_name.strip()) == 0:
        return False, app._(keys.ERROR_INPUT_TABLE_REQUIRED)

    if len(table_name.split(" ")) > 1:
        return False, app._(keys.ERROR_INPUT_TABLE_HAS_SPACES)

    if not re.match("^[a-zA-Z]$", table_name[0]):
        return False, app._(keys.ERROR_INPUT_TABLE_FIRST_CHAR)

    if len(table_name) < 4:
        return False, app._(keys.ERROR_INPUT_TABLE_MIN_LENGHT)

    if not re.match(r"^[a-zA-Z][\w_]{3,}$", table_name):
        return False, app._(keys.ERROR_INPUT_TABLE_INVALID_CHARS)

    return True, "placeholder-for-successful-validation"
