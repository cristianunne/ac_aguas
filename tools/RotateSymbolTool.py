from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.core import *

import os

try:
    from qgis.PyQt.QtWidgets import *
except:
    pass

from ..Path import PathClass

from ..entities.AgTramoSymbolEntity import AgTramoSymbolEntity
from ..entities.AgTramosEntity import AgTramosEntity
from ..entities.AgNodoTrSymbolEntity import AgNodoTrSymbolEntity



class RotateSymbolTool():

    def __init__(self, iface, toolbar):
        self.iface = iface
        self.toolbar = toolbar
        self.canvas = self.iface.mapCanvas()

        dir = PathClass()
        filename = os.path.join(dir.getPath(), 'icons/rotar.svg')

        # Create actions
        self.rotate = QAction(QIcon(filename),
                              QCoreApplication.translate("ACAguas", "Rotar Simbolo a partir de un Tramo"),
                              self.iface.mainWindow())

        self.rotate.setCheckable(True)

        # Connect to signals for button behaviour
        self.rotate.triggered.connect(self.rotateSymbol)

        # Add actions to the toolbar
        self.toolbar.addAction(self.rotate)



    def rotateSymbol(self):

        if self.rotate.isChecked():

            try:
                self.layer_ag_tramos = QgsProject.instance().mapLayersByName('ag_tramos')[0]
                self.layer_ag_nodo_tr_symbol = QgsProject.instance().mapLayersByName('ag_nodo_tr_symbol')[0]
                self.layer_ag_tramo_symbol = QgsProject.instance().mapLayersByName('ag_tramo_symbol')[0]

                self.ag_tramo_symbol_entity = AgTramoSymbolEntity()
                self.ag_tramo_symbol_entity.initialize(self.layer_ag_tramo_symbol)

                self.ag_tramos_entity = AgTramosEntity()
                self.ag_tramos_entity.initialize(self.layer_ag_tramos)

                self.ag_nodo_tr_symbol_entity = AgNodoTrSymbolEntity()
                self.ag_nodo_tr_symbol_entity.initialize(self.layer_ag_nodo_tr_symbol)

                # verifico que haya al menos un elemento seleccionado
                layer_select_tramo = self.layer_ag_tramos.selectedFeatures()
                layer_select_symbol = self.layer_ag_nodo_tr_symbol.selectedFeatures()

                if len(layer_select_tramo) >= 1 and len(layer_select_symbol) >= 1:
                    tramo_select = layer_select_tramo[0]
                    symbol_select = layer_select_symbol[0]

                    symbol_tramo = self.ag_tramo_symbol_entity.verifiedSymbolByTramo(symbol_select.id(), tramo_select.id())
                    #primero verifico que el simbolo que estoy seleccionado este relacionado con el tramo
                    if  symbol_tramo != False:

                       self.ag_nodo_tr_symbol_entity.changeAnguloByTramo(tramo_select, symbol_select, symbol_tramo, self.ag_tramos_entity)



                    else:
                        self.iface.messageBar().pushMessage("Error", "Seleccione un Tramo y un Simbolo que esten relacionados", Qgis.Warning)


                else:
                    self.iface.messageBar().pushMessage("Error", "Seleccione un Tramo y un Simbolo", Qgis.Warning)

                self.rotate.setChecked(False)




            except (IndexError):

                self.iface.messageBar().pushMessage("Error", "Debe cargar la capa Todas las capas", Qgis.Critical)
                self.rotate.setChecked(False)