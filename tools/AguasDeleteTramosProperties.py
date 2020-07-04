from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.core import *

import os

try:
    from qgis.PyQt.QtWidgets import *
except:
    pass

from ..Path import PathClass

from ..entities.AgTramosEntity import AgTramosEntity
from ..entities.AgTramoSymbolEntity import AgTramoSymbolEntity
from ..entities.AgNodoTrSymbolEntity import AgNodoTrSymbolEntity
from ..entities.AgVentilacionEntity import AgVentilacionEntity
from ..entities.AgNodoEntity import AgNodoEntity
from ..entities.AgNodosTramos import AgNodosTramosEntity


class AguasDeleteTramoProperties():

    def __init__(self, iface, toolbar):
        self.iface = iface
        self.toolbar = toolbar
        self.canvas = self.iface.mapCanvas()

        dir = PathClass()
        filename = os.path.join(dir.getPath(), 'icons\polilinea_delete.svg')

        # Create actions
        self.tramos_delete = QAction(QIcon(filename),
                                     QCoreApplication.translate("ACAguas", "Eliminar Propieades del Tramo"),
                                     self.iface.mainWindow())

        self.tramos_delete.setCheckable(True)

        # Connect to signals for button behaviour
        self.tramos_delete.triggered.connect(self.action_delete_properties)

        # Add actions to the toolbar
        self.toolbar.addAction(self.tramos_delete)


    def action_delete_properties(self):
        # Accedo si el tool ha sido activado
        if self.tramos_delete.isChecked():

            res_dialog = self.showdialog()

            self.is_proyecto_v = self.is_project()

            if (res_dialog == 1):
                try:

                    if self.is_proyecto_v:

                        self.layer_ag_tramos = QgsProject.instance().mapLayersByName('ag_tramos_p')[0]
                        self.layer_ag_nodos = QgsProject.instance().mapLayersByName('ag_nodos_p')[0]
                        self.layer_ag_nodos_tramos = QgsProject.instance().mapLayersByName('ag_nodos_tramos_p')[0]
                        self.layer_ag_tramo_symbol = QgsProject.instance().mapLayersByName('ag_tramo_symbol_p')[0]
                        self.ag_nodo_tr_symbol = QgsProject.instance().mapLayersByName('ag_nodo_tr_symbol_p')[0]
                        self.layer_ag_ventilacion = QgsProject.instance().mapLayersByName('ag_ventilacion_p')[0]

                    else:
                        self.layer_ag_tramos = QgsProject.instance().mapLayersByName('ag_tramos')[0]
                        self.layer_ag_nodos = QgsProject.instance().mapLayersByName('ag_nodos')[0]
                        self.layer_ag_nodos_tramos = QgsProject.instance().mapLayersByName('ag_nodos_tramos')[0]
                        self.layer_ag_tramo_symbol = QgsProject.instance().mapLayersByName('ag_tramo_symbol')[0]
                        self.ag_nodo_tr_symbol = QgsProject.instance().mapLayersByName('ag_nodo_tr_symbol')[0]
                        self.layer_ag_ventilacion = QgsProject.instance().mapLayersByName('ag_ventilacion')[0]

                    # Instancio las entidades y le paso las capas correspondietes
                    self.ag_tramos_entity = AgTramosEntity()
                    self.ag_tramos_entity.initialize(self.layer_ag_tramos)

                    self.ag_tramo_symbol_entity = AgTramoSymbolEntity()
                    self.ag_tramo_symbol_entity.initialize(self.layer_ag_tramo_symbol)

                    self.ag_nodo_tr_symbol_entity = AgNodoTrSymbolEntity()
                    self.ag_nodo_tr_symbol_entity.initialize(self.ag_nodo_tr_symbol)

                    self.ag_ventilacion_entity = AgVentilacionEntity()
                    self.ag_ventilacion_entity.initialize(self.layer_ag_ventilacion)

                    self.ag_nodos_entity = AgNodoEntity()
                    self.ag_nodos_entity.initialize(self.layer_ag_nodos)

                    self.ag_nodos_tramos_entity = AgNodosTramosEntity()
                    self.ag_nodos_tramos_entity.initialize(self.layer_ag_nodos_tramos)

                    layer_select_tramo = self.layer_ag_tramos.selectedFeatures()

                    if (len(layer_select_tramo) >= 1):
                        # guardo solo el elemento 1 de la seleccion
                        tramo_select = layer_select_tramo[0]

                        #Antes de borrar recupero los id de los nodos
                        nodos_tramos = self.ag_nodos_tramos_entity.getNodosByTramoAdd(tramo_select)
                        array_symbol_tramo = self.ag_tramo_symbol_entity.getArraySymbolByTramo(tramo_select)
                        id_tramo = tramo_select.id()

                        self.ag_nodos_entity.deleteNodoWithoutRef(tramo_select, self.layer_ag_nodos_tramos, nodos_tramos)

                        if self.ag_tramos_entity.deleteTramo(tramo_select):

                            if self.ag_ventilacion_entity.deleteVentilacion(tramo_select):
                                pass

                        #elimino el simbolo
                        self.ag_nodo_tr_symbol_entity.deleteSymbolByTramo(id_tramo, array_symbol_tramo, self.layer_ag_tramo_symbol)

                    else:
                        self.iface.messageBar().pushMessage("Error", "Seleccione un Tramo", Qgis.Warning)

                    self.tramos_delete.setChecked(False)


                except (IndexError, AttributeError):
                    self.iface.messageBar().pushMessage("Error",
                                                        "Debe cargar la capa 'ag_tramos', 'ag_tramos_symbol', 'ag_nodos_tramos', "
                                                        "'ag_nodo_tr_symbol', 'ag_nodos', 'ag_ventilacion'",
                                                        Qgis.Critical)
                    self.tramos_delete.setChecked(False)


    def is_project(self):

        grupos = QgsProject.instance().layerTreeRoot()
        layer = self.iface.activeLayer()

        name_grupo = self.getNameTreeNodo(grupos, layer)
        # ya tengo el grupo donde esta la capa, consulto si tiene el texto proyecto
        if name_grupo.find("proyecto") != -1:
            # encontre la capa en un proyecto hago una cosa
            return True

        else:
            return False

    def getNameTreeNodo(self, tree_groups, layer):

        for nodo in tree_groups.children():
            name_nodo = nodo.name()
            # recorro el child
            for capa in nodo.findLayerIds():

                if capa == layer.id():
                    return name_nodo


    def showdialog(self):

        retval = QMessageBox.question(self.iface.mainWindow(),
                                      "Question", "Borrar Propiedades del Tramo?",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        val = None

        if retval == QMessageBox.Yes:

            val = 1
        else:
            val = 0

        return val
