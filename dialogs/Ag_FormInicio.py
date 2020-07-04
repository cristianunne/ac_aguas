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
    os.path.dirname(__file__), 'Ag_FormInicio_base.ui'))


class AgFormInicioDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(AgFormInicioDialog, self).__init__(parent)
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

        pixmap = QPixmap(os.path.join(dir.getPath(), 'icons\DP.svg'))
        self.dp_inicio_1.setPixmap(pixmap)

        pixmap_pp = QPixmap(os.path.join(dir.getPath(), 'icons\PP.svg'))
        self.pp_inicio_2.setPixmap(pixmap_pp)

        pixmap_te = QPixmap(os.path.join(dir.getPath(), 'icons\TE.svg'))
        self.te_inicio_3.setPixmap(pixmap_te)

        pixmap_ts = QPixmap(os.path.join(dir.getPath(), 'icons\TS.svg'))
        self.ts_inicio_4.setPixmap(pixmap_ts)

        pixmap_tp = QPixmap(os.path.join(dir.getPath(), 'icons\TP.svg'))
        self.tp_inicio_5.setPixmap(pixmap_tp)

        pixmap_rs = QPixmap(os.path.join(dir.getPath(), 'icons\RS.svg'))
        self.rs_inicio_6.setPixmap(pixmap_rs)

        pixmap_rd = QPixmap(os.path.join(dir.getPath(), 'icons\RD.svg'))
        self.rd_inicio_7.setPixmap(pixmap_rd)

        pixmap_ve = QPixmap(os.path.join(dir.getPath(), 'icons\VE.svg'))
        self.ve_inicio_8.setPixmap(pixmap_ve)

        pixmap_vm = QPixmap(os.path.join(dir.getPath(), 'icons\VM.png'))
        self.vm_inicio_9.setPixmap(pixmap_vm)

        pixmap_vr = QPixmap(os.path.join(dir.getPath(), 'icons\VR.png'))
        self.vr_inicio_10.setPixmap(pixmap_vr)

        pixmap_vg = QPixmap(os.path.join(dir.getPath(), 'icons\VG.svg'))
        self.vg_inicio_11.setPixmap(pixmap_vg)
