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
    os.path.dirname(__file__), 'Ag_Hidrantes.ui'))


class AgHidrantesDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(AgHidrantesDialog, self).__init__(parent)
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

        pixmap = QPixmap(os.path.join(dir.getPath(), 'icons\hidrantes.svg'))
        self.dp_hid_1.setPixmap(pixmap)

        pixmap_2 = QPixmap(os.path.join(dir.getPath(), 'icons\hidrante_vista.svg'))
        self.dp_hid_2.setPixmap(pixmap_2)

        pixmap_3 = QPixmap(os.path.join(dir.getPath(), 'icons\camara_limpieza.svg'))
        self.dp_hid_3.setPixmap(pixmap_3)

        pixmap_4 = QPixmap(os.path.join(dir.getPath(), 'icons\grifo_publico.svg'))
        self.dp_hid_4.setPixmap(pixmap_4)

        pixmap_5 = QPixmap(os.path.join(dir.getPath(), 'icons/valvula_aire.svg'))
        self.dp_hid_5.setPixmap(pixmap_5)

        pixmap_6 = QPixmap(os.path.join(dir.getPath(), 'icons/boca_riego.svg'))
        self.dp_hid_6.setPixmap(pixmap_6)

        pixmap_7 = QPixmap(os.path.join(dir.getPath(), 'icons/valvula_seg.svg'))
        self.dp_hid_7.setPixmap(pixmap_7)

        pixmap_8 = QPixmap(os.path.join(dir.getPath(), 'icons/val_con_golpe.svg'))
        self.dp_hid_8.setPixmap(pixmap_8)

        pixmap_9 = QPixmap(os.path.join(dir.getPath(), 'icons/tanque_hidron.svg'))
        self.dp_hid_9.setPixmap(pixmap_9)

        pixmap_10 = QPixmap(os.path.join(dir.getPath(), 'icons\camara_rompec.svg'))
        self.dp_hid_10.setPixmap(pixmap_10)

        pixmap_11 = QPixmap(os.path.join(dir.getPath(), 'icons/valv_reg_presion.svg'))
        self.dp_hid_11.setPixmap(pixmap_11)

        pixmap_12 = QPixmap(os.path.join(dir.getPath(), 'icons/valv_reg_caudal.svg'))
        self.dp_hid_12.setPixmap(pixmap_12)

        pixmap_13 = QPixmap(os.path.join(dir.getPath(), 'icons/medidor_caudal.svg'))
        self.dp_hid_13.setPixmap(pixmap_13)
