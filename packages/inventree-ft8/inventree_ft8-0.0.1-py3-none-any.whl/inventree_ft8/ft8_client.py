"""FT8 client plugin definition."""

from __future__ import annotations

import structlog
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path
from django.utils.translation import gettext_lazy as _

from plugin import InvenTreePlugin
from plugin.mixins import (
    NavigationMixin,
    SettingsMixin,
    UrlsMixin,
    UserInterfaceMixin,
)

from .version import PLUGIN_VERSION

logger = structlog.get_logger('inventree.ft8')


class FT8Client(
    SettingsMixin, UserInterfaceMixin, NavigationMixin, UrlsMixin, InvenTreePlugin
):
    """Expose the browser FT8 client via the InvenTree UI."""

    NAME = 'FT8Client'
    SLUG = 'ft8'
    TITLE = _('FT8 Ham Radio Client')
    AUTHOR = 'MrARM'
    PUBLISH_DATE = '2025-11-13'
    DESCRIPTION = _('Operate an ft8js-based FT8 terminal from inside InvenTree.')
    VERSION = PLUGIN_VERSION

    PANEL_ENTRYPOINT = 'FT8Panel.js:renderFT8Panel'
    PANEL_TARGETS = {'usersettings'}

    NAVIGATION = [{'name': _('FT8 Client'), 'link': 'plugin:ft8:console', 'icon': 'ti ti-radio'}]
    NAVIGATION_TAB_NAME = _('FT8')
    NAVIGATION_TAB_ICON = 'ti ti-radio'

    SETTINGS = {
        'ENABLE_PANEL': {
            'name': _('Enable FT8 Panel'),
            'description': _(
                'Expose the FT8 browser client as a plugin panel for eligible pages.'
            ),
            'default': True,
            'validator': bool,
        },
        'OPERATOR_CALLSIGN': {
            'name': _('Default Callsign'),
            'description': _('Optional callsign to pre-fill in the FT8 client.'),
        },
        'OPERATOR_GRID': {
            'name': _('Default Grid Square'),
            'description': _(
                'Optional Maidenhead grid to provide as the initial location.'
            ),
        },
    }

    def get_plugin_context(self, user):
        """Build a consistent context dict for the React entry-point."""

        return {
            'callsign': (self.get_setting('OPERATOR_CALLSIGN') or user.username or 'N0CALL').upper(),
            'grid': (self.get_setting('OPERATOR_GRID') or 'EM28').upper(),
            'plugin_base_url': self.base_url,
        }

    def console_view(self, request):
        """Render the standalone FT8 console page."""

        if not request.user.is_authenticated:
            return HttpResponse(_('You must be logged in to use the FT8 console.'), status=403)

        context = {'plugin_context': self.get_plugin_context(request.user)}
        return render(request, 'plugin/ft8/console.html', context)

    def setup_urls(self):
        """Expose the FT8 console route."""

        return [
            path('console/', self.console_view, name='console'),
        ]

    def get_ui_panels(self, request, context=None, **kwargs):
        """Return the FT8 client as a plugin panel where appropriate."""

        panels: list[dict] = []
        context = context or {}

        if not self.get_setting('ENABLE_PANEL', True):
            return panels

        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return panels

        target_model = context.get('target_model')
        if target_model not in self.PANEL_TARGETS:
            return panels

        panel_context = self.get_plugin_context(user)

        logger.debug(
            'Providing FT8 panel',
            target_model=target_model,
            user_id=getattr(user, 'pk', None),
        )

        panels.append(
            {
                'key': 'ft8-web-client',
                'title': _('FT8 Client'),
                'description': _(
                    'powered by ft8js.'
                ),
                'icon': 'ti ti-radio',
                'source': self.plugin_static_file(self.PANEL_ENTRYPOINT),
                'context': panel_context,
            }
        )

        return panels
