# coding=utf-8
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.core import *


import os

try:
    from qgis.PyQt.QtWidgets import *
except:
    pass

from ..Path import PathClass

from ..dialogs.Questions_ini_fin_vent import QuestionIniFinVentilacion
from ..dialogs.Add_Ventilacion_Form import AddVentilacionDialog

from ..entities.AgVentilacionEntity import AgVentilacionEntity
from ..entities.AgNodoEntity import AgNodoEntity


class VentilacionTool():

    def __init__(self, iface, toolbar):
        self.iface = iface
        self.toolbar = toolbar
        self.canvas = self.iface.mapCanvas()
        self.result = False
        dir = PathClass()
        filename = os.path.join(dir.getPath(), 'icons\VE_add.svg')

        # Cargo el Dialog
        self.dlg_question_ini_fin_vent = QuestionIniFinVentilacion()
        self.dlg_add_ventilacion = AddVentilacionDialog()

        # Create actions
        self.venti = QAction(QIcon(filename),
                                 QCoreApplication.translate("ACAguas", "Agregar Ventilacion"),
                                 self.iface.mainWindow())

        self.venti.setCheckable(True)

        # Connect to signals for button behaviour
        self.venti.triggered.connect(self.addVentilacion)

        # Add actions to the toolbar
        self.toolbar.addAction(self.venti)





    def addVentilacion(self):

        self.is_proyecto_v = self.is_project()

        if self.venti.isChecked():

            try:

                #Compruebo si se trata de un proyecto
                if self.is_proyecto_v:
                    self.layer_ag_tramos = QgsProject.instance().mapLayersByName('ag_tramos_p')[0]
                    self.layer_ag_ventilacion = QgsProject.instance().mapLayersByName('ag_ventilacion_p')[0]
                    self.layer_ag_nodos = QgsProject.instance().mapLayersByName('ag_nodos_p')[0]
                    self.layer_ag_nodos_tramos = QgsProject.instance().mapLayersByName('ag_nodos_tramos_p')[0]

                else:
                    self.layer_ag_tramos = QgsProject.instance().mapLayersByName('ag_tramos')[0]
                    self.layer_ag_ventilacion = QgsProject.instance().mapLayersByName('ag_ventilacion')[0]
                    self.layer_ag_nodos = QgsProject.instance().mapLayersByName('ag_nodos')[0]
                    self.layer_ag_nodos_tramos = QgsProject.instance().mapLayersByName('ag_nodos_tramos')[0]


                #creo la entidad de la ventilacion
                self.ag_ventilacion_entity = AgVentilacionEntity()
                self.ag_ventilacion_entity.initialize(self.layer_ag_ventilacion)

                self.ag_nodos_entity = AgNodoEntity()
                self.ag_nodos_entity.initialize(self.layer_ag_nodos)

                # verifico que haya al menos un elemento seleccionado
                layer_select_tramo = self.layer_ag_tramos.selectedFeatures()

                if (len(layer_select_tramo) >= 1):
                    # guardo solo el elemento 1 de la seleccion
                    tramo_select = layer_select_tramo[0]

                    res = self.showdialog()

                    if res == 1:
                        res2 = self.dlg_question_ini_fin_vent.exec_()

                        inicio = False
                        fin = False

                        if self.dlg_question_ini_fin_vent.rb_vent_ini.isChecked():
                            inicio = True

                        elif self.dlg_question_ini_fin_vent.rb_vent_fin.isChecked():
                            fin = True


                        if res2:

                            res3 = self.dlg_add_ventilacion.exec_()

                            tipo_ventilacion = ""

                            if self.dlg_add_ventilacion.rb_inicio_ve.isChecked():
                                tipo_ventilacion = "VE"

                            elif self.dlg_add_ventilacion.rb_inicio_vm.isChecked():
                                tipo_ventilacion = "VM"

                            elif self.dlg_add_ventilacion.rb_inicio_vr.isChecked():
                                tipo_ventilacion = "VR"

                            elif self.dlg_add_ventilacion.rb_inicio_vg.isChecked():
                                tipo_ventilacion = "VG"

                            if res3:
                                res_4 = self.addNodoDialog()
                                is_nodos = False

                                if res_4 == 1:
                                    is_nodos = True

                                #agrego la ventilacion
                                if inicio == True:
                                    self.ag_ventilacion_entity.addVentilacion(tramo_select, tipo_ventilacion)
                                    if is_nodos:
                                        self.ag_nodos_entity.addNodoIntermedio(tramo_select, self.layer_ag_nodos_tramos,
                                                                               True)

                                elif fin == True:
                                    self.ag_ventilacion_entity.addVentilacionToFinal(tramo_select, tipo_ventilacion)
                                    if is_nodos:
                                        self.ag_nodos_entity.addNodoIntermedio(tramo_select, self.layer_ag_nodos_tramos,
                                                                               False)

                else:
                    self.iface.messageBar().pushMessage("Error", "Seleccione un Tramo", Qgis.Warning)

                self.venti.setChecked(False)

            except (IndexError, AttributeError):

                self.iface.messageBar().pushMessage("Error", "Debe cargar la capa Todas las capas", Qgis.Critical)
                self.venti.setChecked(False)


    def is_project(self):

        grupos = QgsProject.instance().layerTreeRoot()
        layer = self.iface.activeLayer()

        name_grupo = self.getNameTreeNodo(grupos, layer)
        #ya tengo el grupo donde esta la capa, consulto si tiene el texto proyecto
        if name_grupo.find("proyecto") != -1:
            #encontre la capa en un proyecto hago una cosa
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
                                      "Question", "Agregar Simbolo de Vetilacion u Otro?",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)


        val = None

        if retval == QMessageBox.Yes:

            val = 1
        else:
            val = 0

        return val


    def sb(self):

        box = QMessageBox()
        box.setIcon(QMessageBox.Question)
        box.setStyleSheet("background-color: rgb(85, 170, 255);")
        box.setWindowTitle("Consulta")
        box.setText("¿Desea Agregar la Ventilacion?")
        box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        box.setDefaultButton(QMessageBox.No)
        buttonYes = box.button(QMessageBox.Yes)
        buttonYes.setText("Aceptar")
        buttonNo = box.button(QMessageBox.No)
        buttonNo.setText("Cancelar")
        box.exec_()

    def addNodoDialog(self):

        retval = QMessageBox.question(self.iface.mainWindow(),
                                      "Question", "Desea agregar los Nodos?",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        val = None

        if retval == QMessageBox.Yes:

            val = 1
        else:
            val = 0

        return val