# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ACAguas
                                 A QGIS plugin
 Plugin para el manejo de las aguas
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-11-10
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Aguas de Corrientes
        email                : cristain297@hotmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

try:
    from qgis.PyQt.QtWidgets import *
except:
    pass
# Import the code for the dialog
from .ac_aguas_dialog import ACAguasDialog
import os.path
from .tools.AguasConexionTool import AguasConexionTool
from .tools.AguasTramosActionTool import AguasTramosAction
from .tools.AguasDeleteTramosProperties import AguasDeleteTramoProperties
from .tools.HidrantesTool import HidrantesTool
from .tools.VentilacionTool import VentilacionTool
from .tools.RotateSymbolTool import RotateSymbolTool


class ACAguas:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ACAguas_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []

        self.toolbar = self.iface.addToolBar(u'ACAguas')
        self.toolbar.setObjectName(u'ACAguas')


    def tr(self, message):

        return QCoreApplication.translate('ACAguas', message)


    def initGui(self):

        self.conexion_tool = AguasConexionTool(self.iface, self.toolbar)
        self.toolbar.addSeparator()

        self.ag_tramos_action_tool = AguasTramosAction(self.iface, self.toolbar)
        self.ag_tramos_delete = AguasDeleteTramoProperties(self.iface, self.toolbar)

        self.toolbar.addSeparator()

        self.hidrandtes_tool = HidrantesTool(self.iface, self.toolbar)

        self.toolbar.addSeparator()

        self.ventilacion_tool = VentilacionTool(self.iface, self.toolbar)

        self.toolbar.addSeparator()

        self.rotate_symbol_tool = RotateSymbolTool(self.iface, self.toolbar)







    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&ACAguas'),
                action)
            self.iface.removeToolBarIcon(action)


