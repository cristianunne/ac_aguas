# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WhereAmIDialog
                                 A QGIS plugin
 Localiza las coordenadas de un punto
                             -------------------
        begin                : 2018-01-03
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Cristian
        email                : cristian297@hotmail.com
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

from qgis.PyQt import QtGui, uic
from qgis.PyQt.QtGui import QPixmap
from ..Path import PathClass

try:
    from qgis.PyQt.QtWidgets import *
except:
    pass

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Add_Ventilacion_Form_base.ui'))


class AddVentilacionDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(AddVentilacionDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs_-with-auto-connect
        self.setupUi(self)
        self.initUI()
        
        #self.n_nodo_final.setValidator(QtGui.QIntValidator())
        #self.ztn_final.setValidator(QtGui.QDoubleValidator())

    def initUI(self):
        dir = PathClass()


        pixmap_ve = QPixmap(os.path.join(dir.getPath(), 'icons\VE.svg'))
        self.ve_inicio_8.setPixmap(pixmap_ve)

        pixmap_vm = QPixmap(os.path.join(dir.getPath(), 'icons\VM.png'))
        self.vm_inicio_9.setPixmap(pixmap_vm)

        pixmap_vr = QPixmap(os.path.join(dir.getPath(), 'icons\VR.png'))
        self.vr_inicio_10.setPixmap(pixmap_vr)

        pixmap_vg = QPixmap(os.path.join(dir.getPath(), 'icons\VG.svg'))
        self.vg_inicio_11.setPixmap(pixmap_vg)
