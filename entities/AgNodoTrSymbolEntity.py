from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.core import *

from ..entities.AgTramosEntity import AgTramosEntity


class AgNodoTrSymbolEntity():

    def __init__(self):

        self.ag_nodo_tr_symbol = None


    def initialize(self, ag_nodo_tr_symbol):
        self.ag_nodo_tr_symbol = ag_nodo_tr_symbol

    def addNodoSymbol(self, tramo, type_symbol, ini_fin):

        ag_tramos_entity = AgTramosEntity()

        vertices = ag_tramos_entity.getVertexTramoAsPoint(tramo)

        angulo = self.getAngulo(ag_tramos_entity, tramo, ini_fin)

        # consulto acerca del tipo de symbolo para saber la rotacion

        if type_symbol == "TP":

            angulo = self.anguloSum(angulo, type_symbol)

        elif type_symbol == "TE":
            angulo = self.anguloSum(angulo, type_symbol)

        elif type_symbol == "PP" or type_symbol == "DP" or type_symbol == "TS":
            angulo = self.anguloSum(angulo, type_symbol)

        elif type_symbol == "RS":

            if angulo < 0 and ini_fin == True:
                #Compruebo si es de inicio o fin
                angulo = angulo - 90

            elif angulo > 0 and ini_fin == True:
                angulo = angulo - 90

            elif angulo < 0 and ini_fin == False:
                angulo = angulo + 90

            elif angulo > 0 and ini_fin == False:
                angulo = angulo + 90

        attrs = [None] * len(self.ag_nodo_tr_symbol.fields())

        # obtengo el id del tipo de symbol
        idx_type_symbol = self.ag_nodo_tr_symbol.fields().indexFromName("ty_sym")
        idx_type_angulo = self.ag_nodo_tr_symbol.fields().indexFromName("angulo")

        # asigno el tipo de feature
        attrs[idx_type_symbol] = type_symbol
        attrs[idx_type_angulo] = angulo

        self.ag_nodo_tr_symbol.startEditing()
        # creo un feature
        feature = QgsFeature()

        # elijo el 1er vertice como point
        point = None
        if ini_fin == True:
            point = vertices[0]

        else:
            num_ver = len(vertices)
            point = vertices[num_ver - 1]

        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(point.x(), point.y())))
        feature.setAttributes(attrs)
        res = self.ag_nodo_tr_symbol.addFeature(feature)

        if res:

            if self.ag_nodo_tr_symbol.commitChanges():
                return True
            else:
                self.ag_nodo_tr_symbol.rollBack()
                return False
        else:
            return False



    def anguloSum(self, angulo, type_symbol):

        if type_symbol == "TE":

            angulo = angulo - 90

        if type_symbol == "TP":

            angulo = angulo - 180

        if type_symbol == "PP" or type_symbol == "DP" or type_symbol == "TS":

            angulo = angulo - 90

        return angulo


    def changeSymbol(self, idsymbol, new_type_symbol):

        # obtengo el id del tipo de symbol
        idx_type_symbol = self.ag_nodo_tr_symbol.fields().indexFromName("ty_sym")

        attrs = {idx_type_symbol: new_type_symbol}

        # Inicio la edicion y la termino
        self.ag_nodo_tr_symbol.startEditing()

        if self.ag_nodo_tr_symbol.changeAttributeValues(idsymbol, attrs):
            self.ag_nodo_tr_symbol.commitChanges()
            return True
        else:
            self.ag_nodo_tr_symbol.rollBack()
            return False


    def getExistSymbolInicio(self, tramo_select):

        ag_tramos_entity = AgTramosEntity()

        vertice_tramo = ag_tramos_entity.getFirstVertexTramoAsPoint(tramo_select)

        # Consulto la tabla cl_nodo_tr_symbol para saber si hay un punto en esa coordenada
        feats_tr_symbol = self.ag_nodo_tr_symbol.getFeatures()

        for feat in feats_tr_symbol:
            point_symbol = feat.geometry().asPoint()
            # ACA EVALUO SI EL PUNTO ES IGUAL
            if point_symbol == QgsPointXY(vertice_tramo.x(), vertice_tramo.y()):
                return feat

            # Imprimo los datos
        return False

    def deleteSymbol(self, symbol_feat):

        self.ag_nodo_tr_symbol.startEditing()

        res = self.ag_nodo_tr_symbol.deleteFeature(symbol_feat['symbol_tr_symbol'])
        if res:
            if self.ag_nodo_tr_symbol.commitChanges():
                return True
            else:
                self.ag_nodo_tr_symbol.rollBack()
                return False
        return False


    def deleteSymbolByTramo(self, id_tramo, array_tramo_symbol, layer_tramo_symbol):


        existe = False
        for feat in array_tramo_symbol:

            print("Nodo: " + str(feat['symbol_tr_symbol']))

            for feat_actual in layer_tramo_symbol.getFeatures():

                if feat['symbol_tr_symbol'] == feat_actual['symbol_tr_symbol']:
                    print("encontro 1")

                    existe = True

            print("////////////////////////////")


            if existe == False:
                self.deleteSymbol(feat)

            existe = False

    def changeAnguloByTramo(self, tramo_select, symbol, symbol_tramo, ag_tramos_entity):

        if symbol_tramo['tipo'] == "Inicio":

            angulo = self.getAngulo(ag_tramos_entity, tramo_select, True)

            angulo = angulo - 90
            attrs = [None] * len(self.ag_nodo_tr_symbol.fields())

            # obtengo el id del tipo de symbol
            idx_type_angulo = self.ag_nodo_tr_symbol.fields().indexFromName("angulo")
            attrs = {idx_type_angulo: angulo}

            # Inicio la edicion y la termino
            self.ag_nodo_tr_symbol.startEditing()

            if self.ag_nodo_tr_symbol.changeAttributeValues(symbol.id(), attrs):
                self.ag_nodo_tr_symbol.commitChanges()
                return True
            else:
                self.ag_nodo_tr_symbol.rollBack()
                return False


        elif symbol_tramo['tipo'] == "Fin":
            angulo = self.getAngulo(ag_tramos_entity, tramo_select, False)

            angulo = angulo - 180

            attrs = [None] * len(self.ag_nodo_tr_symbol.fields())

            # obtengo el id del tipo de symbol
            idx_type_angulo = self.ag_nodo_tr_symbol.fields().indexFromName("angulo")
            attrs = {idx_type_angulo: angulo}

            # Inicio la edicion y la termino
            self.ag_nodo_tr_symbol.startEditing()

            if self.ag_nodo_tr_symbol.changeAttributeValues(symbol.id(), attrs):

                self.ag_nodo_tr_symbol.commitChanges()
                return True
            else:
                self.ag_nodo_tr_symbol.rollBack()
                return False


    def getExistSymbolFinal(self, tramo_select):

        ag_tramos_entity = AgTramosEntity()

        vertice_tramo = ag_tramos_entity.getLastVertexTramoAsPoint(tramo_select)

        # Consulto la tabla cl_nodo_tr_symbol para saber si hay un punto en esa coordenada
        feats_tr_symbol = self.ag_nodo_tr_symbol.getFeatures()

        for feat in feats_tr_symbol:
            point_symbol = feat.geometry().asPoint()
            # ACA EVALUO SI EL PUNTO ES IGUAL
            if point_symbol == QgsPointXY(vertice_tramo.x(), vertice_tramo.y()):
                return feat

            # Imprimo los datos
        return False


    def getAngulo(self, ag_tramos_entity, tramo_select, ini_fin):

        num_vert = ag_tramos_entity.getNumVertex(tramo_select)

        point_tramo = ag_tramos_entity.getVertexTramoAsPoint(tramo_select)
        angulo = None

        if ini_fin:
            angulo = point_tramo[0].azimuth(point_tramo[1])

        else:
            angulo = point_tramo[num_vert - 2].azimuth(point_tramo[num_vert - 1])

        return angulo

    def getLastPointAdded(self):

        features = self.ag_nodo_tr_symbol.getFeatures()
        last = None
        valor = -1
        for feat in features:
            if feat['gid'] > valor:
                valor = feat['gid']
                last = feat
        return last