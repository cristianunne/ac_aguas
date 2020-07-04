from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.core import *


class AgTramosEntity():

    def __init__(self):

        self.ag_tramo = None


    def initialize(self, ag_tramo):
        self.ag_tramo = ag_tramo


    def addAttributes(self, feat_linea, tipo, longitud, diametro, material, conforme, is_project):

        #La variable que viene como conforme tmb es proyecto
        # obtengo el id del tramo
        id_tramo = feat_linea["gid"]

        if diametro == "":
            diametro = None

        # obtengo los indices de los atributos
        idx_tipo = self.ag_tramo.fields().indexFromName("tipo")
        idx_longitud = self.ag_tramo.fields().indexFromName("longitud")
        idx_diametro = self.ag_tramo.fields().indexFromName("diametro")
        idx_material = self.ag_tramo.fields().indexFromName("material")
        idx_conforme = self.ag_tramo.fields().indexFromName("conforme")
        idx_proyecto = self.ag_tramo.fields().indexFromName("proyecto")
        idx_sentido = self.ag_tramo.fields().indexFromName("sentido")

        sentido = "ft"
        attrs = None

        #Compruebo si es un proyecto
        if is_project:
            attrs = {idx_tipo: tipo, idx_longitud: longitud, idx_diametro: diametro, idx_material: material,
                     idx_proyecto: conforme, idx_sentido: sentido}

        else:

            attrs = {idx_tipo: tipo, idx_longitud: longitud, idx_diametro: diametro, idx_material: material,
                 idx_conforme: conforme, idx_sentido: sentido}

        # Inicio la edicion y la termino
        self.ag_tramo.startEditing()

        if self.ag_tramo.changeAttributeValues(id_tramo, attrs):
            self.ag_tramo.commitChanges()
            return True
        else:

            self.ag_tramo.rollBack()
            return False

    def addVertexToLine(self, tramo):
        # distancia ocupada para interpolar el punto
        distance = 10

        geom_line = tramo.geometry()

        # inicio la edicion del layer
        self.ag_tramo.startEditing()

        # Obtengo el punto de la interpolacion
        point = geom_line.interpolate(distance)

        # inseto el vertice
        res = geom_line.insertVertex(point.asPoint().x(), point.asPoint().y(), 1)

        if res:
            self.ag_tramo.changeGeometry(tramo.id(), geom_line)
            self.ag_tramo.commitChanges()
            return True

        self.ag_tramo.rollBack()
        return False

    def deleteTramo(self, tramo_feat):

        self.ag_tramo.startEditing()

        res = self.ag_tramo.deleteFeature(tramo_feat.id())
        if res:
            if self.ag_tramo.commitChanges():
                return True
            else:
                self.ag_tramo.rollBack()
                return False
        return False

    def getLongitudTramo(self, tramo):

        long = tramo.geometry().length()

        return long

    def getVertexTramoAsPoint(self, tramo):

        # Arreglo de puntos a devolver
        points = []
        geom = tramo.geometry()
        n = 0
        # ingresa por el primer vertice
        ver = geom.vertexAt(0)
        # count vertex and extract nodes
        while (ver != QgsPoint(0, 0)):
            n += 1
            points.append(ver)
            ver = geom.vertexAt(n)

        return points

    def getFirstVertexTramoAsPoint(self, tramo):

        # Arreglo de puntos a devolver
        points = []
        geom = tramo.geometry()
        n = 0
        # ingresa por el primer vertice
        ver = geom.vertexAt(0)
        # count vertex and extract nodes
        while (ver != QgsPoint(0, 0)):
            n += 1
            points.append(ver)
            ver = geom.vertexAt(n)

        return points[0]

    def getLastVertexTramoAsPoint(self, tramo):

        # Arreglo de puntos a devolver
        points = []
        geom = tramo.geometry()
        n = 0
        # ingresa por el primer vertice
        ver = geom.vertexAt(0)
        # count vertex and extract nodes
        while (ver != QgsPoint(0, 0)):
            n += 1
            points.append(ver)
            ver = geom.vertexAt(n)

        return points[self.getNumVertex(tramo) - 1]



    def getNumVertex(self, tramo):
        geom = tramo.geometry()
        n = 0
        # ingresa por el primer vertice
        ver = geom.vertexAt(0)
        # count vertex and extract nodes
        while (ver != QgsPoint(0, 0)):
            n += 1
            ver = geom.vertexAt(n)

        return n

    def setNullData(self, tramo):

        num_attr = 8
        # modificar los atributos del 1 al 7
        self.ag_tramo.startEditing()

        for i in range(num_attr):

            if i >= 1 and i <= 7:
                self.ag_tramo.changeAttributeValue(tramo.id(), i, None)

        if self.ag_tramo.commitChanges():

            return True

        else:
            self.ag_tramo.rollBack()
            return False

    def verifiedTramo(self, tramo_select, ag_tramo_symbol_entity):
        #deberia verificar que no tenga asociaciones con los simbolos

        if ag_tramo_symbol_entity.verifiedTramoInTable(tramo_select.id()):

            return True
        else :
            return False


