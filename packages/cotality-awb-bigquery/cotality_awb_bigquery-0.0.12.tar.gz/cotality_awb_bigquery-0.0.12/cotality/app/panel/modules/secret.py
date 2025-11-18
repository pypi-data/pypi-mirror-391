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
"""Secret Module"""

from __future__ import annotations

import panel as pn

from ....core.locales import keys
from ...base.base_app import BaseApp


def display(app: BaseApp) -> pn.Column:
    """Edit API credentials."""

    if app.api_credential_is_valid:
        return __display_update_secrets(app)
    else:
        return __display_create_secrets(app)


def __display_create_secrets(app: BaseApp):
    username = pn.widgets.TextInput(
        name=app._(keys.TEXT_SECRET_USERNAME), sizing_mode="stretch_width"
    )
    password = pn.widgets.PasswordInput(
        name=app._(keys.TEXT_SECRET_PASSWORD), sizing_mode="stretch_width"
    )
    save_button = pn.widgets.Button(
        name=app._(keys.BUTTON_SAVE_SECRET),
        button_type="primary",
        sizing_mode="stretch_width",
    )

    save_output = pn.Column(sizing_mode="stretch_width")

    def _save(event):
        if not (username.value and password.value):
            save_output.objects = [
                pn.pane.Alert(app._(keys.TEXT_SECRET_INTRODUCTION), alert_type="danger")
            ]
            return

        app.toggle_loading()
        secret_client = app.platform.secret_client

        try:
            secret_client.save_digital_gateway_credential(
                username.value, password.value
            )
            save_output.objects = [
                pn.pane.Alert(
                    app._(keys.TEXT_SECRET_SAVED_CORRECTLY), alert_type="success"
                )
            ]
        except Exception:
            save_output.objects = [
                pn.pane.Alert(app._(keys.SYS_ERROR_SAVE_SECRETS), alert_type="danger")
            ]
        finally:
            app.toggle_loading()

    save_button.on_click(_save)

    return pn.Column(
        pn.pane.Markdown(
            f"# {app._(keys.TEXT_NO_SECRET_CREATED)}", sizing_mode="stretch_width"
        ),
        pn.pane.Markdown(
            f"### {app._(keys.TEXT_NO_SECRET_CREATED_INTRO)}",
            sizing_mode="stretch_width",
        ),
        username,
        password,
        save_button,
        save_output,
        sizing_mode="stretch_width",
        css_classes=["center-wrapper"],
    )


def __display_update_secrets(app: BaseApp) -> pn.Column:
    username = pn.widgets.TextInput(
        name=app._(keys.TEXT_SECRET_USERNAME), sizing_mode="stretch_width"
    )
    password = pn.widgets.PasswordInput(
        name=app._(keys.TEXT_SECRET_PASSWORD), sizing_mode="stretch_width"
    )

    save_button = pn.widgets.Button(
        name=app._(keys.BUTTON_SAVE_SECRET),
        button_type="primary",
        sizing_mode="stretch_width",
    )

    save_output = pn.Column(sizing_mode="stretch_width")

    def _save(event):
        if not (username.value and password.value):
            save_output.objects = [
                pn.pane.Alert(app._(keys.TEXT_SECRET_INTRODUCTION), alert_type="danger")
            ]
            return

        app.toggle_loading()
        secret_client = app.platform.secret_client

        try:
            secret_client.save_digital_gateway_credential(
                username.value, password.value
            )
            save_output.objects = [
                pn.pane.Alert(
                    app._(keys.TEXT_SECRET_SAVED_CORRECTLY), alert_type="success"
                )
            ]
        except Exception:
            save_output.objects = [
                pn.pane.Alert(app._(keys.SYS_ERROR_SAVE_SECRETS), alert_type="danger")
            ]
        finally:
            app.toggle_loading()

    save_button.on_click(_save)

    return pn.Column(
        pn.pane.Markdown(
            f"# {app._(keys.TEXT_UPDATE_SECRET)}", sizing_mode="stretch_width"
        ),
        pn.pane.Markdown(
            f"### {app._(keys.TEXT_UPDATE_SECRET_INTRO)}", sizing_mode="stretch_width"
        ),
        username,
        password,
        save_button,
        save_output,
        sizing_mode="stretch_width",
        css_classes=["center-wrapper"],
    )
