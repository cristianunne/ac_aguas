from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.core import *


import os
import string

try:
    from qgis.PyQt.QtWidgets import *
except:
    pass

from ..Path import PathClass

from ..dialogs.Ag_FormInicio import AgFormInicioDialog
from ..dialogs.Nodo_Inicio_Tramo import NodoInicioTramosDialog
from ..dialogs.Ag_FormFinal import AgFormFinalDialog
from ..dialogs.Nodo_Final_Tramo import NodoFinalTramosDialog
from ..dialogs.Resumen_base import ResumenBaseDialog

from ..entities.AgTramosEntity import AgTramosEntity
from ..entities.AgTramoSymbolEntity import AgTramoSymbolEntity
from ..entities.AgNodoTrSymbolEntity import AgNodoTrSymbolEntity
from ..entities.AgVentilacionEntity import AgVentilacionEntity
from ..entities.AgNodoEntity import AgNodoEntity
from ..entities.AgNodosTramos import AgNodosTramosEntity

class AguasTramosAction():

    def __init__(self, iface, toolbar):
        self.iface = iface
        self.toolbar = toolbar
        self.canvas = self.iface.mapCanvas()

        # Cargo el Dialog
        self.dlg_ag_tramos = AgFormInicioDialog()
        self.dlg_ag_tramos_final = AgFormFinalDialog()
        self.dlg_nodo_inicio = NodoInicioTramosDialog()
        self.dlg_nodo_final = NodoFinalTramosDialog()
        self.dlg_resumen_tramo = ResumenBaseDialog()

        dir = PathClass()
        filename = os.path.join(dir.getPath(), 'icons\polilinea.png')

        # Create actions
        self.tramos = QAction(QIcon(filename),
                              QCoreApplication.translate("ACAguas", "Agregar Propieades al Tramo"),
                              self.iface.mainWindow())

        self.tramos.setCheckable(True)

        # Connect to signals for button behaviour
        self.tramos.triggered.connect(self.action_tramos)

        # Add actions to the toolbar
        self.toolbar.addAction(self.tramos)


    def action_tramos(self):

        #Defino si es un proyecto o no y realizo el cambio en el FORM para que el texto se nromalice
        #Utilizo el nombre del Esquema o del Grupo para determinar

        self.is_proyecto = self.is_project()

        # Accedo si el tool ha sido activado
        if self.tramos.isChecked():
            try:

                #aca debo controlar si es proyecto o no
                if self.is_proyecto:
                    self.layer_ag_tramos = QgsProject.instance().mapLayersByName('ag_tramos_p')[0]
                    self.layer_ag_nodos = QgsProject.instance().mapLayersByName('ag_nodos_p')[0]
                    self.layer_ag_nodos_tramos = QgsProject.instance().mapLayersByName('ag_nodos_tramos_p')[0]
                    layer_ag_tramo_symbol = QgsProject.instance().mapLayersByName('ag_tramo_symbol_p')[0]
                    self.ag_nodo_tr_symbol = QgsProject.instance().mapLayersByName('ag_nodo_tr_symbol_p')[0]
                    self.layer_ag_ventilacion = QgsProject.instance().mapLayersByName('ag_ventilacion_p')[0]

                else :
                    self.layer_ag_tramos = QgsProject.instance().mapLayersByName('ag_tramos')[0]
                    self.layer_ag_nodos = QgsProject.instance().mapLayersByName('ag_nodos')[0]
                    self.layer_ag_nodos_tramos = QgsProject.instance().mapLayersByName('ag_nodos_tramos')[0]
                    layer_ag_tramo_symbol = QgsProject.instance().mapLayersByName('ag_tramo_symbol')[0]
                    self.ag_nodo_tr_symbol = QgsProject.instance().mapLayersByName('ag_nodo_tr_symbol')[0]
                    self.layer_ag_ventilacion = QgsProject.instance().mapLayersByName('ag_ventilacion')[0]


                # Instancio las entidades y le paso las capas correspondietes
                self.ag_tramos_entity = AgTramosEntity()
                self.ag_tramos_entity.initialize(self.layer_ag_tramos)

                self.ag_tramo_symbol_entity = AgTramoSymbolEntity()
                self.ag_tramo_symbol_entity.initialize(layer_ag_tramo_symbol)

                self.ag_nodo_tr_symbol_entity = AgNodoTrSymbolEntity()
                self.ag_nodo_tr_symbol_entity.initialize(self.ag_nodo_tr_symbol)

                self.ag_ventilacion_entity = AgVentilacionEntity()
                self.ag_ventilacion_entity.initialize(self.layer_ag_ventilacion)

                self.ag_nodos_entity = AgNodoEntity()
                self.ag_nodos_entity.initialize(self.layer_ag_nodos)

                self.ag_nodos_tramos_entity = AgNodosTramosEntity()
                self.ag_nodos_tramos_entity.initialize(self.layer_ag_nodos_tramos)


                # verifico que haya al menos un elemento seleccionado
                layer_select_tramo = self.layer_ag_tramos.selectedFeatures()

                if (len(layer_select_tramo) >= 1):
                    # guardo solo el elemento 1 de la seleccion
                    tramo_select = layer_select_tramo[0]

                    # Controlo que haya guardado del Tramo
                    if tramo_select.id() < 0:
                        self.iface.messageBar().pushMessage("Error", "Por favor Guarde el tramo para proceder",
                                                            Qgis.Warning)

                    else:

                        # PRIMERO VERIFICO QUE NO HAYA NINGUN TIPO DE DATOS CARGADOS EN EL TRAMO
                        #Verificar de otra forma porque va a entrar igual
                        if self.ag_tramos_entity.verifiedTramo(tramo_select, self.ag_tramo_symbol_entity) == False:

                            # evaluo si hay un simbolo al inicio y al Final y proceso segun ello
                            res_exists_symbol_inicio = self.ag_nodo_tr_symbol_entity.getExistSymbolInicio(tramo_select)
                            res_exists_symbol_final = self.ag_nodo_tr_symbol_entity.getExistSymbolFinal(tramo_select)

                            if res_exists_symbol_inicio == False and res_exists_symbol_final == False:

                                self.resetAllDialogs()
                                self.showBoxsCompleted(tramo_select)


                            elif res_exists_symbol_inicio != False and res_exists_symbol_final == False:

                                self.resetAllDialogs()
                                self.showBoxWithInitialData(tramo_select)


                            elif res_exists_symbol_inicio == False and res_exists_symbol_final != False:
                                self.resetAllDialogs()
                                self.showBoxWithFinalData(tramo_select)

                            elif res_exists_symbol_inicio != False and res_exists_symbol_final != False:
                                self.resetAllDialogs()
                                self.showBoxWithInitialAndFinalData(tramo_select)


                else:
                    self.iface.messageBar().pushMessage("Error", "Seleccione un Tramo", Qgis.Warning)

                self.tramos.setChecked(False)


            except (IndexError, AttributeError):
                self.iface.messageBar().pushMessage("Error", "Debe cargar la capa Todas las capas", Qgis.Critical)
                self.tramos.setChecked(False)





    def is_project(self):


        grupos = QgsProject.instance().layerTreeRoot()
        layer = self.iface.activeLayer()

        name_grupo = self.getNameTreeNodo(grupos, layer)

        #ya tengo el grupo donde esta la capa, consulto si tiene el texto proyecto
        if name_grupo.find("proyecto") != -1:
            #encontre la capa en un proyecto hago una cosa
            self.dlg_resumen_tramo.label_res_ch.setText("Proyecto:")
            return True

        else:
            #no es un proyecto
            self.dlg_resumen_tramo.label_res_ch.setText("Conforme:")
            return False


    def getNameTreeNodo(self, tree_groups, layer):

        for nodo in tree_groups.children():
            name_nodo = nodo.name()
            # recorro el child
            for capa in nodo.findLayerIds():

                if capa == layer.id():
                    return name_nodo




    def tramosActionProcess(self, tramo_select):

        res_exists_symbol_inicio = self.ag_nodo_tr_symbol_entity.getExistSymbolInicio(tramo_select)
        res_exists_symbol_final = self.ag_nodo_tr_symbol_entity.getExistSymbolFinal(tramo_select)
        tipo_canieria_aux = None

        if res_exists_symbol_inicio == False:

            # Agrego la ventilacion con cualquiera de los 2 inicios de ramales
            if self.tipo_canieria_symbol == "RS" or self.tipo_canieria_symbol == "RD":

                # agrego el symbolo al inicio
                if self.ag_nodo_tr_symbol_entity.addNodoSymbol(tramo_select, self.tipo_canieria_symbol, True):
                    last_point_sym_add_ini = self.ag_nodo_tr_symbol_entity.getLastPointAdded()
                    # Agrego la referencia a la tabla que relaciona ambas
                    if self.ag_tramo_symbol_entity.addTramoSymbol(tramo_select.id(), last_point_sym_add_ini.id(),
                                                                  "Inicio"):
                        # Cargo los atributos del tramo
                        if self.ag_tramos_entity.addAttributes(tramo_select, self.tipo, self.longitud, self.diametro,
                                                               self.material, self.conforme, self.is_proyecto):

                            # Agrego los nodos
                            if self.ag_nodos_entity.addNodoByTramo(tramo_select, self.layer_ag_nodos_tramos,
                                                                       self.tipo_cota, self.cota_ini, False):
                                pass

            elif self.tipo_canieria_symbol == "VE" or self.tipo_canieria_symbol == "VM" or self.tipo_canieria_symbol == "VR" or self.tipo_canieria_symbol == "VG":
                tipo_canieria_aux = "Nada"
                # agrego el symbolo al inicio
                if self.ag_nodo_tr_symbol_entity.addNodoSymbol(tramo_select, tipo_canieria_aux, True):
                    last_point_sym_add_ini = self.ag_nodo_tr_symbol_entity.getLastPointAdded()
                    # Agrego la referencia a la tabla que relaciona ambas
                    if self.ag_tramo_symbol_entity.addTramoSymbol(tramo_select.id(), last_point_sym_add_ini.id(),
                                                                      "Inicio"):
                        # Cargo los atributos del tramo
                        if self.ag_tramos_entity.addAttributes(tramo_select, self.tipo, self.longitud,
                                                                   self.diametro,
                                                                   self.material, self.conforme, self.is_proyecto):


                            if self.ag_ventilacion_entity.addVentilacion(tramo_select, self.tipo_canieria_symbol):

                                    # Agrego los nodos
                                if self.ag_nodos_entity.addNodoByTramo(tramo_select, self.layer_ag_nodos_tramos,
                                                                           self.tipo_cota, self.cota_ini, True):
                                    pass

            elif self.tipo_canieria_symbol == "Nada":

                # agrego el symbolo al inicio
                if self.ag_nodo_tr_symbol_entity.addNodoSymbol(tramo_select, self.tipo_canieria_symbol, True):
                    last_point_sym_add_ini = self.ag_nodo_tr_symbol_entity.getLastPointAdded()
                    # Agrego la referencia a la tabla que relaciona ambas
                    if self.ag_tramo_symbol_entity.addTramoSymbol(tramo_select.id(), last_point_sym_add_ini.id(),
                                                                      "Inicio"):
                        # Cargo los atributos del tramo
                        if self.ag_tramos_entity.addAttributes(tramo_select, self.tipo, self.longitud,
                                                                   self.diametro,
                                                                   self.material, self.conforme, self.is_proyecto):
                            # Agrego los nodos
                            if self.ag_nodos_entity.addNodoByTramo(tramo_select, self.layer_ag_nodos_tramos,
                                                                       self.tipo_cota, self.cota_ini, False):
                                pass

        else:
            # existe un simbolo, solo agrego la referencia
            # guardo el tipo de simbolo que tengo al inicio
            tipo_symbol_inicio = str(res_exists_symbol_inicio['ty_sym'])
            res_symbol_inicio = False
            is_add_nodos = False

            # compruebo si la opcion inicial es RS y la nueva RD
            if self.tipo_canieria_symbol == "RD" and tipo_symbol_inicio == "RS":
                # realizo el cambio de simbolo
                self.ag_nodo_tr_symbol_entity.changeSymbol(res_exists_symbol_inicio.id(), "RD")

                #Agrego la referencia
                if self.ag_tramo_symbol_entity.addTramoSymbol(tramo_select.id(), res_exists_symbol_inicio.id(),
                                                              "Inicio"):
                    # Tegno que agregar la ventilacion tmb
                    if self.ag_nodos_entity.addNodoByTramo(tramo_select, self.layer_ag_nodos_tramos, self.tipo_cota_fin,
                                                               self.cota_fin, False):
                        is_add_nodos = True

                        # Evaluo que hacer segun la opcion de inicio
            elif (tipo_symbol_inicio == "Nada" and self.tipo_canieria_symbol == "RD") or (tipo_symbol_inicio == "Nada" and self.tipo_canieria_symbol == "RS"):
                # realizo el cambio de simbolo
                self.ag_nodo_tr_symbol_entity.changeSymbol(res_exists_symbol_inicio.id(),
                                                                   self.tipo_canieria_symbol)

                # Agrego la referencia
                if self.ag_tramo_symbol_entity.addTramoSymbol(tramo_select.id(), res_exists_symbol_inicio.id(),
                                                              "Inicio"):
                    # tengo que agregar la ventilacion
                    #if self.ag_ventilacion_entity.addVentilacion(tramo_select, "VE"):
                        if self.ag_nodos_entity.addNodoByTramo(tramo_select, self.layer_ag_nodos_tramos, self.tipo_cota_fin,
                                                               self.cota_fin, False):
                            is_add_nodos = True

            elif tipo_symbol_inicio == "Nada" and (self.tipo_canieria_symbol == "VE" or self.tipo_canieria_symbol == "VM" or
                                                   self.tipo_canieria_symbol == "VR" or self.tipo_canieria_symbol == "VG"):

                # Agrego la referencia
                if self.ag_tramo_symbol_entity.addTramoSymbol(tramo_select.id(), res_exists_symbol_inicio.id(),
                                                              "Inicio"):
                    # Tegno que agregar la ventilacion tmb
                    if self.ag_ventilacion_entity.addVentilacion(tramo_select, self.tipo_canieria_symbol):
                        if self.ag_nodos_entity.addNodoByTramo(tramo_select, self.layer_ag_nodos_tramos, self.tipo_cota_fin,
                                                               self.cota_fin, True):
                            is_add_nodos = True

            elif tipo_symbol_inicio == "Nada" and self.tipo_canieria_symbol == "Nada":

                # Cargo los atributos del tramo
                # Agrego la referencia
                if self.ag_tramo_symbol_entity.addTramoSymbol(tramo_select.id(), res_exists_symbol_inicio.id(),
                                                              "Inicio"):

                    if self.ag_nodos_entity.addNodoByTramo(tramo_select, self.layer_ag_nodos_tramos, self.tipo_cota_fin,
                                                           self.cota_fin, False):
                        pass

            elif tipo_symbol_inicio == "RS" or tipo_symbol_inicio == "RD":

                # Agrego la referencia
                if self.ag_tramo_symbol_entity.addTramoSymbol(tramo_select.id(), res_exists_symbol_inicio.id(),
                                                              "Inicio"):

                    if self.tipo_canieria_symbol == "Nada":

                        if self.ag_nodos_entity.addNodoByTramo(tramo_select, self.layer_ag_nodos_tramos, self.tipo_cota_fin,
                                                               self.cota_fin, False):
                            pass
                    elif self.tipo_canieria_symbol == "VE" or self.tipo_canieria_symbol == "VM" or \
                            self.tipo_canieria_symbol == "VR" or self.tipo_canieria_symbol == "VG":
                        # Tegno que agregar la ventilacion tmb
                        if self.ag_ventilacion_entity.addVentilacion(tramo_select, self.tipo_canieria_symbol):
                            if self.ag_nodos_entity.addNodoByTramo(tramo_select, self.layer_ag_nodos_tramos, self.tipo_cota_fin,
                                                                   self.cota_fin, True):
                                is_add_nodos = True


            #este metodo se ejectua independientemente del tipo de condicion anterior
            if self.ag_tramos_entity.addAttributes(tramo_select, self.tipo, self.longitud, self.diametro,
                                                   self.material, self.conforme, self.is_proyecto):
               pass



        if res_exists_symbol_final == False:
            # si elije ventilacion cargo a nada
            if self.tipo_canieria_final_symbol == "VE" or self.tipo_canieria_final_symbol == "VM" or self.tipo_canieria_final_symbol == "VR" or self.tipo_canieria_final_symbol == "VG":
                # Agrego el icono al Final con su referencia// False refiere a que es al Final
                if self.ag_nodo_tr_symbol_entity.addNodoSymbol(tramo_select, "Nada", False):
                    last_point_sym_add_fin = self.ag_nodo_tr_symbol_entity.getLastPointAdded()
                    # Agrega a la tabla que los referencia
                    if self.ag_tramo_symbol_entity.addTramoSymbol(tramo_select.id(), last_point_sym_add_fin.id(),
                                                                  "Fin"):
                        if self.ag_ventilacion_entity.addVentilacionToFinal(tramo_select, self.tipo_canieria_final_symbol):

                            if self.ag_nodos_entity.addNodoToFinal(tramo_select, self.layer_ag_nodos_tramos):
                                pass
            else:
                if self.ag_nodo_tr_symbol_entity.addNodoSymbol(tramo_select, self.tipo_canieria_final_symbol, False):
                    last_point_sym_add_fin = self.ag_nodo_tr_symbol_entity.getLastPointAdded()
                    # Agrega a la tabla que los referencia
                    if self.ag_tramo_symbol_entity.addTramoSymbol(tramo_select.id(), last_point_sym_add_fin.id(),
                                                                  "Fin"):
                        pass
        else:
            # Agrega a la tabla que los referencia
            if self.ag_tramo_symbol_entity.addTramoSymbol(tramo_select.id(), res_exists_symbol_final.id(),
                                                          "Fin"):
                # Verifico si esta cargando una ventilacion
                if self.tipo_canieria_final_symbol == "VE" or self.tipo_canieria_final_symbol == "VM" or \
                        self.tipo_canieria_final_symbol == "VR" or self.tipo_canieria_final_symbol == "VG":
                    # agrego la caneria al final
                    if self.ag_ventilacion_entity.addVentilacionToFinal(tramo_select, self.tipo_canieria_final_symbol):

                        if self.ag_nodos_entity.addNodoToFinal(tramo_select, self.layer_ag_nodos_tramos):
                            pass


    def showBoxsCompleted(self, tramo_select):

        #Abro la ventana del Nodo Incial
        res = self.dlg_nodo_inicio.exec_()

        if res == 1:
            # Guardo las Variables del nodo inicial
            self.tipo_cota = self.optionInicioNodoChecked()
            self.cota_ini = self.dlg_nodo_inicio.cota_ini.text()

            res2 = self.dlg_ag_tramos.exec_()

            if res2 == 1:
                #obtengo los Atributos del la Caneria
                self.tipo_canieria_symbol = self.optionInicioCanieriaChecked()
                #Reseteo el formulario de simbolo
                self.resetFormsInicioCanieriaChecked()

                res3 = self.dlg_nodo_final.exec_()

                if res3 == 1:
                    # Guardo las Variables del nodo inicial
                    self.tipo_cota_fin = self.optionFinNodoChecked()
                    self.cota_fin = self.dlg_nodo_final.cota_final.text()

                    #Cargo el Dialog del Final
                    res4 = self.dlg_ag_tramos_final.exec_()

                    if res4 == 1:
                        # obtengo los Atributos del la Caneria
                        self.tipo_canieria_final_symbol = self.optionFinalCanieriaChecked()

                        #Completo los campos de la ventana resumen
                        self.dlg_resumen_tramo.res_long_lbl.setText(str(self.ag_tramos_entity.getLongitudTramo(tramo_select)))
                        self.dlg_resumen_tramo.res_sent_lbl.setText("DS")

                        res5 = self.dlg_resumen_tramo.exec_()

                        if res5 == 1:
                            #Guardo todas las variables
                            self.longitud = self.dlg_resumen_tramo.res_long_lbl.text()
                            self.diametro = self.dlg_resumen_tramo.res_diam_txt.text()
                            self.material = self.dlg_resumen_tramo.res_cb_material.currentText()
                            self.tipo = self.dlg_resumen_tramo.res_cb_tipo.currentText()
                            self.sentido = self.dlg_resumen_tramo.res_sent_lbl.text()
                            self.conforme = self.dlg_resumen_tramo.res_conf_txt.text()

                            self.tramosActionProcess(tramo_select)

    def showBoxWithInitialData(self, tramo_select):

        #No reemplazo los datos del Nodo solo los del tramo
        #reviso cual fue la situacion y en base a eso completo lso campos
        symbol = self.ag_nodo_tr_symbol_entity.getExistSymbolInicio(tramo_select)

        if symbol != False:
            self.evalButtonSymbolInicio(str(symbol['ty_sym']))
        # Abro la ventana del Nodo Incial
        res2 = self.dlg_ag_tramos.exec_()

        if res2:
            # obtengo los Atributos del la Caneria
            self.tipo_canieria_symbol = self.optionInicioCanieriaChecked()
            # Reseteo el formulario de simbolo
            self.resetFormsInicioCanieriaChecked()

            res3 = self.dlg_nodo_final.exec_()

            if res3 == 1:
                # Guardo las Variables del nodo inicial
                self.tipo_cota_fin = self.optionFinNodoChecked()
                self.cota_fin = self.dlg_nodo_final.cota_final.text()

                # Cargo el Dialog del Final
                res4 = self.dlg_ag_tramos_final.exec_()

                if res4 == 1:
                    # obtengo los Atributos del la Caneria
                    self.tipo_canieria_final_symbol = self.optionFinalCanieriaChecked()

                    # Completo los campos de la ventana resumen
                    self.dlg_resumen_tramo.res_long_lbl.setText(
                        str(self.ag_tramos_entity.getLongitudTramo(tramo_select)))
                    self.dlg_resumen_tramo.res_sent_lbl.setText("DS")

                    res5 = self.dlg_resumen_tramo.exec_()

                    if res5 == 1:
                        # Guardo todas las variables
                        self.longitud = self.dlg_resumen_tramo.res_long_lbl.text()
                        self.diametro = self.dlg_resumen_tramo.res_diam_txt.text()
                        self.material = self.dlg_resumen_tramo.res_cb_material.currentText()
                        self.tipo = self.dlg_resumen_tramo.res_cb_tipo.currentText()
                        self.sentido = self.dlg_resumen_tramo.res_sent_lbl.text()
                        self.conforme = self.dlg_resumen_tramo.res_conf_txt.text()

                        self.tramosActionProcess(tramo_select)


    def showBoxWithFinalData(self, tramo_select):
        # No reemplazo los datos del Nodo solo los del tramo
        # reviso cual fue la situacion y en base a eso completo lso campos
        symbol = self.ag_nodo_tr_symbol_entity.getExistSymbolFinal(tramo_select)

        if symbol != False:

            self.evalButtonSymbolFinal(str(symbol['ty_sym']))

        # Abro la ventana del Nodo Incial
        res = self.dlg_nodo_inicio.exec_()

        if res == 1:
            # Guardo las Variables del nodo inicial
            self.tipo_cota = self.optionInicioNodoChecked()
            self.cota_ini = self.dlg_nodo_inicio.cota_ini.text()

            res2 = self.dlg_ag_tramos.exec_()

            if res2 == 1:
                # obtengo los Atributos del la Caneria
                self.tipo_canieria_symbol = self.optionInicioCanieriaChecked()
                # Reseteo el formulario de simbolo
                self.resetFormsInicioCanieriaChecked()

                # Cargo el Dialog del Final
                res4 = self.dlg_ag_tramos_final.exec_()

                if res4 == 1:

                    # obtengo los Atributos del la Caneria
                    self.tipo_canieria_final_symbol = self.optionFinalCanieriaChecked()

                    # Completo los campos de la ventana resumen
                    self.dlg_resumen_tramo.res_long_lbl.setText(
                        str(self.ag_tramos_entity.getLongitudTramo(tramo_select)))
                    self.dlg_resumen_tramo.res_sent_lbl.setText("DS")

                    res5 = self.dlg_resumen_tramo.exec_()

                    if res5 == 1:
                        # Guardo todas las variables
                        self.longitud = self.dlg_resumen_tramo.res_long_lbl.text()
                        self.diametro = self.dlg_resumen_tramo.res_diam_txt.text()
                        self.material = self.dlg_resumen_tramo.res_cb_material.currentText()
                        self.tipo = self.dlg_resumen_tramo.res_cb_tipo.currentText()
                        self.sentido = self.dlg_resumen_tramo.res_sent_lbl.text()
                        self.conforme = self.dlg_resumen_tramo.res_conf_txt.text()



                        self.tramosActionProcess(tramo_select)



    def showBoxWithInitialAndFinalData(self, tramo_select):
        # No reemplazo los datos del Nodo solo los del tramo
        # reviso cual fue la situacion y en base a eso completo lso campos
        symbol_inicio = self.ag_nodo_tr_symbol_entity.getExistSymbolInicio(tramo_select)
        symbol_final = self.ag_nodo_tr_symbol_entity.getExistSymbolFinal(tramo_select)

        if symbol_inicio != False:
            self.evalButtonSymbolInicio(str(symbol_inicio['ty_sym']))

        if symbol_final != False:

            self.evalButtonSymbolFinal(str(symbol_final['ty_sym']))

        res2 = self.dlg_ag_tramos.exec_()

        if res2:
            # obtengo los Atributos del la Caneria
            self.tipo_canieria_symbol = self.optionInicioCanieriaChecked()
            # Reseteo el formulario de simbolo
            self.resetFormsInicioCanieriaChecked()

            # Cargo el Dialog del Final
            res4 = self.dlg_ag_tramos_final.exec_()

            if res4 == 1:
                # obtengo los Atributos del la Caneria
                self.tipo_canieria_final_symbol = self.optionFinalCanieriaChecked()

                # Completo los campos de la ventana resumen
                self.dlg_resumen_tramo.res_long_lbl.setText(
                    str(self.ag_tramos_entity.getLongitudTramo(tramo_select)))
                self.dlg_resumen_tramo.res_sent_lbl.setText("DS")

                res5 = self.dlg_resumen_tramo.exec_()

                if res5 == 1:
                    # Guardo todas las variables
                    self.longitud = self.dlg_resumen_tramo.res_long_lbl.text()
                    self.diametro = self.dlg_resumen_tramo.res_diam_txt.text()
                    self.material = self.dlg_resumen_tramo.res_cb_material.currentText()
                    self.tipo = self.dlg_resumen_tramo.res_cb_tipo.currentText()
                    self.sentido = self.dlg_resumen_tramo.res_sent_lbl.text()
                    self.conforme = self.dlg_resumen_tramo.res_conf_txt.text()

                    self.tipo_cota_fin = ""
                    self.cota_fin = ""

                    self.tramosActionProcess(tramo_select)




    def evalButtonSymbolInicio(self, symbol):


        if symbol == 'RD':
            #bloqueo todos los forms

            self.dlg_ag_tramos.rb_inicio_dp.setEnabled(False)
            self.dlg_ag_tramos.rb_inicio_pp.setEnabled(False)
            self.dlg_ag_tramos.rb_inicio_te.setEnabled(False)
            self.dlg_ag_tramos.rb_inicio_ts.setEnabled(False)
            self.dlg_ag_tramos.rb_inicio_tp.setEnabled(False)

            self.dlg_ag_tramos.rb_inicio_rs.setEnabled(False)
            self.dlg_ag_tramos.rb_inicio_rd.setEnabled(False)

            #pongo en default a la ventilacion
            self.dlg_ag_tramos.rb_inicio_ve.setChecked(True)

        elif symbol == 'RS':

            self.dlg_ag_tramos.rb_inicio_dp.setEnabled(False)
            self.dlg_ag_tramos.rb_inicio_pp.setEnabled(False)
            self.dlg_ag_tramos.rb_inicio_te.setEnabled(False)
            self.dlg_ag_tramos.rb_inicio_ts.setEnabled(False)
            self.dlg_ag_tramos.rb_inicio_tp.setEnabled(False)


            self.dlg_ag_tramos.rb_inicio_rs.setEnabled(False)


        else:

            self.dlg_ag_tramos.rb_inicio_nada.setChecked(True)


    def evalButtonSymbolFinal(self, symbol):

        if symbol == 'RD' or symbol == 'RS':
            # bloqueo todos los forms

            self.dlg_ag_tramos_final.rb_inicio_dp.setEnabled(False)
            self.dlg_ag_tramos_final.rb_inicio_pp.setEnabled(False)
            self.dlg_ag_tramos_final.rb_inicio_te.setEnabled(False)
            self.dlg_ag_tramos_final.rb_inicio_ts.setEnabled(False)
            self.dlg_ag_tramos_final.rb_inicio_tp.setEnabled(False)

            self.dlg_ag_tramos_final.rb_inicio_rs.setEnabled(False)
            self.dlg_ag_tramos_final.rb_inicio_rd.setEnabled(False)

        elif symbol == 'TP':
            self.dlg_ag_tramos_final.rb_inicio_tp.setChecked(True)

        elif symbol == 'TS':
            self.dlg_ag_tramos_final.rb_inicio_ts.setChecked(True)

        elif symbol == 'TE':
            self.dlg_ag_tramos_final.rb_inicio_te.setChecked(True)

        elif symbol == 'DP':
            self.dlg_ag_tramos_final.rb_inicio_dp.setChecked(True)

        elif symbol == 'PP':
            self.dlg_ag_tramos_final.rb_inicio_pp.setChecked(True)

        else:
            self.dlg_ag_tramos_final.rb_inicio_nada.setChecked(True)




    def optionInicioNodoChecked(self):

        if self.dlg_nodo_inicio.rb_foto_ini.isChecked():

            return self.dlg_nodo_inicio.rb_foto_ini.text()

        elif self.dlg_nodo_inicio.rb_relev_ini.isChecked():

            return self.dlg_nodo_inicio.rb_relev_ini.text()

        elif self.dlg_nodo_inicio.rb_plano_ini.isChecked():

            return self.dlg_nodo_inicio.rb_plano_ini.text()


    def optionFinNodoChecked(self):

        if self.dlg_nodo_final.rb_foto_final.isChecked():

            return self.dlg_nodo_final.rb_foto_final.text()

        elif self.dlg_nodo_final.rb_relev_final.isChecked():

            return self.dlg_nodo_final.rb_relev_final.text()

        elif self.dlg_nodo_final.rb_plano_final.isChecked():

            return self.dlg_nodo_final.rb_plano_final.text()


    def optionInicioCanieriaChecked(self):

        if self.dlg_ag_tramos.rb_inicio_dp.isChecked():
            return self.dlg_ag_tramos.rb_inicio_dp.text()
        elif self.dlg_ag_tramos.rb_inicio_pp.isChecked():
            return self.dlg_ag_tramos.rb_inicio_pp.text()
        elif self.dlg_ag_tramos.rb_inicio_te.isChecked():
            return self.dlg_ag_tramos.rb_inicio_te.text()
        elif self.dlg_ag_tramos.rb_inicio_ts.isChecked():
            return self.dlg_ag_tramos.rb_inicio_ts.text()
        elif self.dlg_ag_tramos.rb_inicio_tp.isChecked():
            return self.dlg_ag_tramos.rb_inicio_tp.text()

        elif self.dlg_ag_tramos.rb_inicio_rs.isChecked():
            return self.dlg_ag_tramos.rb_inicio_rs.text()
        elif self.dlg_ag_tramos.rb_inicio_rd.isChecked():
            return self.dlg_ag_tramos.rb_inicio_rd.text()

        elif self.dlg_ag_tramos.rb_inicio_ve.isChecked():
            return self.dlg_ag_tramos.rb_inicio_ve.text()
        elif self.dlg_ag_tramos.rb_inicio_vm.isChecked():
            return self.dlg_ag_tramos.rb_inicio_vm.text()
        elif self.dlg_ag_tramos.rb_inicio_vr.isChecked():
            return self.dlg_ag_tramos.rb_inicio_vr.text()
        elif self.dlg_ag_tramos.rb_inicio_vg.isChecked():
            return self.dlg_ag_tramos.rb_inicio_vg.text()

        elif self.dlg_ag_tramos.rb_inicio_nada.isChecked():
            return self.dlg_ag_tramos.rb_inicio_nada.text()


    def optionFinalCanieriaChecked(self):

        if self.dlg_ag_tramos_final.rb_inicio_dp.isChecked():
            return self.dlg_ag_tramos_final.rb_inicio_dp.text()
        elif self.dlg_ag_tramos_final.rb_inicio_pp.isChecked():
            return self.dlg_ag_tramos_final.rb_inicio_pp.text()
        elif self.dlg_ag_tramos_final.rb_inicio_te.isChecked():
            return self.dlg_ag_tramos_final.rb_inicio_te.text()
        elif self.dlg_ag_tramos_final.rb_inicio_ts.isChecked():
            return self.dlg_ag_tramos_final.rb_inicio_ts.text()
        elif self.dlg_ag_tramos_final.rb_inicio_tp.isChecked():
            return self.dlg_ag_tramos_final.rb_inicio_tp.text()

        elif self.dlg_ag_tramos_final.rb_inicio_rs.isChecked():
            return self.dlg_ag_tramos_final.rb_inicio_rs.text()
        elif self.dlg_ag_tramos_final.rb_inicio_rd.isChecked():
            return self.dlg_ag_tramos_final.rb_inicio_rd.text()

        elif self.dlg_ag_tramos_final.rb_inicio_ve.isChecked():
            return self.dlg_ag_tramos_final.rb_inicio_ve.text()
        elif self.dlg_ag_tramos_final.rb_inicio_vm.isChecked():
            return self.dlg_ag_tramos_final.rb_inicio_vm.text()
        elif self.dlg_ag_tramos_final.rb_inicio_vr.isChecked():
            return self.dlg_ag_tramos_final.rb_inicio_vr.text()
        elif self.dlg_ag_tramos_final.rb_inicio_vg.isChecked():
            return self.dlg_ag_tramos_final.rb_inicio_vg.text()

        elif self.dlg_ag_tramos_final.rb_inicio_nada.isChecked():
            return self.dlg_ag_tramos_final.rb_inicio_nada.text()

    def resetAllDialogs(self):

        #self.dlg_ag_tramos.rb_inicio_dp.setEnabled(True)
        #self.dlg_ag_tramos.rb_inicio_pp.setEnabled(True)
        #self.dlg_ag_tramos.rb_inicio_te.setEnabled(True)
        #self.dlg_ag_tramos.rb_inicio_ts.setEnabled(True)
        #self.dlg_ag_tramos.rb_inicio_tp.setEnabled(True)

        self.dlg_ag_tramos.rb_inicio_rs.setEnabled(True)
        self.dlg_ag_tramos.rb_inicio_rd.setEnabled(True)

        self.dlg_ag_tramos_final.rb_inicio_dp.setEnabled(True)
        self.dlg_ag_tramos_final.rb_inicio_pp.setEnabled(True)
        self.dlg_ag_tramos_final.rb_inicio_te.setEnabled(True)
        self.dlg_ag_tramos_final.rb_inicio_ts.setEnabled(True)
        self.dlg_ag_tramos_final.rb_inicio_tp.setEnabled(True)

        self.dlg_ag_tramos_final.rb_inicio_rs.setEnabled(True)
        self.dlg_ag_tramos_final.rb_inicio_rd.setEnabled(True)

        self.diametro = self.dlg_resumen_tramo.res_diam_txt.clear()
        self.material = self.dlg_resumen_tramo.res_cb_material.setCurrentIndex(0)
        self.tipo = self.dlg_resumen_tramo.res_cb_tipo.setCurrentIndex(0)
        self.conforme = self.dlg_resumen_tramo.res_conf_txt.clear()


    def resetFormsInicioCanieriaChecked(self):
        self.dlg_ag_tramos.rb_inicio_nada.setChecked(True)
