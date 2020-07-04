from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.core import *


class AgNodosTramosEntity():

    def __init__(self):
        self.ag_nodos_tramos_layer = None

    def initialize(self, ag_nodos_tramos_layer):
        self.ag_nodos_tramos_layer = ag_nodos_tramos_layer


    def addNodoTramo(self, id_tramo, id_cl_nodo):

        attr = [None] * len(self.ag_nodos_tramos_layer.fields())

        idx_id_tramo = self.ag_nodos_tramos_layer.fields().indexFromName("tramo_idtramo")
        idx_cl_nodo = self.ag_nodos_tramos_layer.fields().indexFromName("ag_nodos_id_ag_nodos")

        attr[idx_id_tramo] = id_tramo
        attr[idx_cl_nodo] = id_cl_nodo

        # inicio la edicion
        self.ag_nodos_tramos_layer.startEditing()

        feat = QgsFeature()
        feat.setAttributes(attr)

        if self.ag_nodos_tramos_layer.addFeature(feat):

            if self.ag_nodos_tramos_layer.commitChanges():

                return True
            else:
                self.ag_nodos_tramos_layer.rollBack()

                return False
        else:
            return False


    def deleteNodosTramos(self, feat_delete):

        self.ag_nodos_tramos_layer.startEditing()
        res = self.ag_nodos_tramos_layer.deleteFeature(feat_delete.id())

        if res:

            if self.ag_nodos_tramos_layer.commitChanges():
                return True
            else:
                self.ag_nodos_tramos_layer.rollBack()
                return False
        else:
            return False


    def getNodosByTramoAdd(self, tramo_select):

        #recorro la tabla de relacion primero
        nodos_tramos_ref =  []

        for feat in self.ag_nodos_tramos_layer.getFeatures():

            if feat['tramo_idtramo'] == tramo_select.id():
                nodos_tramos_ref.append(feat)

        if len(nodos_tramos_ref) > 0:
            return nodos_tramos_ref

        else:
            return False