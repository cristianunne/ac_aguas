from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.core import *


import os

try:
    from qgis.PyQt.QtWidgets import *
except:
    pass

from ..Path import PathClass
from .HidranteMouseEffect import HidranteMouseEffect


class HidrantesTool():


    def __init__(self, iface, toolbar):
        self.iface = iface
        self.toolbar = toolbar
        self.canvas = self.iface.mapCanvas()
        self.result = False
        dir = PathClass()
        filename = os.path.join(dir.getPath(), 'icons\hidrantes.svg')

        # Create actions
        self.hidrantes = QAction(QIcon(filename),
                              QCoreApplication.translate("ACAguas", "Agregar Symbolos Especiales"),
                              self.iface.mainWindow())

        self.hidrantes.setCheckable(True)

        # Connect to signals for button behaviour
        self.hidrantes.triggered.connect(self.addHidrante)

        # Add actions to the toolbar
        self.toolbar.addAction(self.hidrantes)

        self.tool = HidranteMouseEffect(self.iface)



    def addHidrante(self):

        if self.hidrantes.isChecked():

            self.is_proyecto_v = self.is_project()

            try:

                if self.is_proyecto_v:
                    self.layer_ag_tramos = QgsProject.instance().mapLayersByName('ag_tramos_p')[0]
                    self.layer_ag_hidrantes = QgsProject.instance().mapLayersByName('ag_hidrantes_p')[0]

                else:

                    self.layer_ag_tramos = QgsProject.instance().mapLayersByName('ag_tramos')[0]
                    self.layer_ag_hidrantes = QgsProject.instance().mapLayersByName('ag_hidrantes')[0]


                self.tool.initialize(self.layer_ag_hidrantes)
                self.canvas.setMapTool(self.tool)
                self.tool.select_.connect(self.alm_res)
                self.activate()

                if self.result != False:
                    print(self.result)
                else:
                    pass


            except (IndexError, AttributeError):
                self.deactivate()
                self.unsetTool()
                self.iface.messageBar().pushMessage("Error", "Debe cargar la capa Todas las capas", Qgis.Critical)
                self.hidrantes.setChecked(False)

        else:
            self.deactivate()
            self.unsetTool()


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


    def alm_res(self, result):
        self.result = result

    def unsetTool(self):
        mc = self.canvas
        mc.unsetMapTool(self.tool)

    def activate(self):
        print("Activo la herramienta de Agregar Hidrante")

    def deactivate(self):

        mc = self.canvas

        layer = self.canvas.currentLayer()

        self.iface.actionPan().trigger()

        for la in mc.layers():
            if layer.type() == layer.VectorLayer:
                layer.removeSelection()
            mc.refresh()
        print("Desactivo la Herramienta de Agregar Hidrante")


