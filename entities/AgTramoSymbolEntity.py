from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.core import *


from ..entities.AgNodoTrSymbolEntity import AgNodoTrSymbolEntity


class AgTramoSymbolEntity():

    def __init__(self):

        self.ag_tramo_symbol = None


    def initialize(self, ag_tramo_symbol):
        self.ag_tramo_symbol = ag_tramo_symbol



    def addTramoSymbol(self, id_tramo, id_symbol, tipo):

        attr = [None] * len(self.ag_tramo_symbol.fields())

        idx_id_tramo = self.ag_tramo_symbol.fields().indexFromName("tramo_idtramo")
        idx_id_symbol = self.ag_tramo_symbol.fields().indexFromName("symbol_tr_symbol")
        idx_id_tipo = self.ag_tramo_symbol.fields().indexFromName("tipo")

        attr[idx_id_tramo] = id_tramo
        attr[idx_id_symbol] = id_symbol
        attr[idx_id_tipo] = tipo

        # inicio la edicion
        self.ag_tramo_symbol.startEditing()

        feat = QgsFeature()
        feat.setAttributes(attr)

        if self.ag_tramo_symbol.addFeature(feat):

            if self.ag_tramo_symbol.commitChanges():

                return True
            else:
                self.ag_tramo_symbol.rollBack()

                return False
        else:
            return False


    def verifiedTramoInTable(self, id_tramo):

        for feat in self.ag_tramo_symbol.getFeatures():

            if feat['tramo_idtramo'] == id_tramo:
                return True
            else:
                return False


    def verifiedSymbolInTable(self, id_symbol):

        for feat in self.ag_tramo_symbol.getFeatures():

            if feat['symbol_tr_symbol'] == id_symbol.id():
                return True
            else:
                return False


    def verifiedSymbolByTramo(self, id_symbol, id_tramo):


        for feat in self.ag_tramo_symbol.getFeatures():
            if feat['symbol_tr_symbol'] == id_symbol and feat['tramo_idtramo'] == id_tramo:

                return feat

        return False

    def getExistSymbolInicio(self, tramo_select):

        #Se evalua por posicion dado que el nuevo Tramo no tiene relacionado todavia el simbolo


        return False



    def getExistSymbolFin(self, id_tramo):

        """for feat in self.ag_tramo_symbol.getFeatures():

            if feat['tramo_idtramo'] == id_tramo and feat['tipo'] == "Fin":
                return True"""

        return False

    def getArraySymbolByTramo(self, tramo_select):
        # recorro la tabla de relacion primero
        nodos_tramos_ref = []

        for feat in self.ag_tramo_symbol.getFeatures():

            if feat['tramo_idtramo'] == tramo_select.id():
                nodos_tramos_ref.append(feat)

        if len(nodos_tramos_ref) > 0:
            return nodos_tramos_ref

        else:
            return False


    def getSymbolInicio(self, tramo_select, ag_nodo_tr_symbol):


        return None


    def getSymbolFin(self, tramo_select, ag_nodo_tr_symbol):
        return None

