#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2018 Andy Stewart
#
# Author:     MacKong <mackonghp@gmail.com>
# Maintainer: MacKong <mackonghp@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json

from core.buffer import Buffer
from core.utils import *
from PyQt6.QtCore import QTimer
from qtconsole import styles
from qtconsole.manager import QtKernelManager
from qtconsole.rich_jupyter_widget import RichJupyterWidget

import os
import sys
sys.path.append(os.path.dirname(__file__))

from kill_ring import EafKillRing


class AppBuffer(Buffer):
    def __init__(self, buffer_id, url, arguments):
        Buffer.__init__(self, buffer_id, url, arguments, False)

        arguments_dict = json.loads(arguments)
        self.kernel = arguments_dict["kernel"]

        (font_size, font_family) = get_emacs_vars(["eaf-jupyter-font-size", "eaf-jupyter-font-family"])

        self.add_widget(EafJupyterWidget(self.kernel,
                                         self.theme_background_color, self.theme_foreground_color,
                                         font_size=font_size, font_family=font_family))

        QTimer.singleShot(500, self.focus_widget)

        self.build_all_methods(self.buffer_widget)

    def get_key_event_widgets(self):
        ''' Send key event to RichJupyterWidget's focusProxy widget.'''
        # We need send key event to RichJupyterWidget's focusProxy widget, not RichJupyterWidget.
        widget = self.buffer_widget.focusProxy()
        return [widget] if widget else []

    def destroy_buffer(self):
        print('Shutdown jupyter kernel {}'.format(self.kernel))
        self.buffer_widget.destroy()

        super().destroy_buffer()

    @interactive
    def update_theme(self):
        super().update_theme()
        dark_mode = get_app_dark_mode("eaf-jupyter-dark-mode")
        self.buffer_widget._init_style(self.theme_background_color, self.theme_foreground_color, dark_mode)

class EafJupyterWidget(RichJupyterWidget):
    def __init__(self, kernel, theme_background_color, theme_foreground_color, *args, **kwargs):
        dark_mode = get_app_dark_mode("eaf-jupyter-dark-mode")
        self._init_style(theme_background_color, theme_foreground_color, dark_mode)

        self.scrollbar_visibility = False

        super(EafJupyterWidget, self).__init__(*args, **kwargs)

        kernel_manager = QtKernelManager(kernel_name=kernel)
        kernel_manager.start_kernel()

        kernel_client = kernel_manager.client()
        kernel_client.start_channels()

        self.kernel_manager = kernel_manager
        self.kernel_client = kernel_client

        self._control.setStyleSheet("border: none;")
        self._page_control.setStyleSheet("border: none;")

        self._kill_ring = EafKillRing(self._control)

    @interactive
    def zoom_in(self):
        self.change_font_size(1)

    @interactive
    def zoom_out(self):
        self.change_font_size(-1)

    @interactive
    def zoom_reset(self):
        self.reset_font()

    def focusProxy(self):
        if self._control.isVisible():
            return self._control
        elif self._page_control.isVisible():
            return self._page_control
        else:
            return None

    def _init_style(self, bg_color, fg_color, dark_mode):
        if dark_mode:
            self.style_sheet = styles.default_dark_style_template % dict(bgcolor=bg_color, fgcolor=fg_color, select="#555")
            self.syntax_style = styles.default_dark_syntax_style
        else:
            self.style_sheet = styles.default_light_style_template % dict(bgcolor=bg_color, fgcolor=fg_color, select="#ccc")
            self.syntax_style = styles.default_light_syntax_style
        self._syntax_style_changed()
        self._style_sheet_changed()

    def destroy(self):
        self.kernel_client.stop_channels()
        self.kernel_manager.shutdown_kernel()
