from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.core import *

from ..entities.AgNodosTramos import AgNodosTramosEntity
from ..entities.AgTramosEntity import AgTramosEntity


class AgNodoEntity():

    def __init__(self):
        self.ag_nodo_layer = None


    def initialize(self, ag_nodo):
        self.ag_nodo_layer = ag_nodo


    def addNodo(self, point, ty_z, cota):

        if ty_z == None or ty_z == "":
            ty_z = None

        if cota == None or cota == "":
            cota = None

        # creo el arreglo vacion con la dimension de los atributos
        attrs = [None] * len(self.ag_nodo_layer.fields())
        idx_ty_z = self.ag_nodo_layer.fields().indexFromName("ty_z")
        idx_cota = self.ag_nodo_layer.fields().indexFromName("cota")

        attrs[idx_ty_z] = ty_z
        attrs[idx_cota] = cota

        feature = QgsFeature()
        self.ag_nodo_layer.startEditing()

        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(point.x(), point.y())))
        feature.setAttributes(attrs)
        res = self.ag_nodo_layer.addFeature(feature)

        if res:

            if self.ag_nodo_layer.commitChanges():
                return True
            else:
                self.ag_nodo_layer.rollBack()
                return False
        else:
            return False


    def addNodoByTramo(self, tramo_select, ag_nodos_tramos_layer, ty_z, cota, with_nodo_middle):
        #with_nodo_middle sirve para saber si se agrega un nodo o no
        #si es TRUE agrego el vertice al tramo para tener la referencia del punto
        point = None
        vertices = None

        if with_nodo_middle:
            geom_line = tramo_select.geometry()
            # Obtengo el punto de la interpolacion
            point = geom_line.interpolate(10)
            # inseto el vertice
            res = geom_line.insertVertex(point.asPoint().x(), point.asPoint().y(), 1)

            if res:
                vertices = geom_line.asMultiPolyline()[0]

        else:
            vertices = tramo_select.geometry().asMultiPolyline()[0]


        num_vert = len(vertices)
        i = 0

        ag_nodos_tramos_entity = AgNodosTramosEntity()
        ag_nodos_tramos_entity.initialize(ag_nodos_tramos_layer)

        for ver in vertices:
            feat = QgsFeature()
            # consulto si existe un nodo en la posicion del vertice
            feat_return = self.getExistNodo(ver)

            #si no encuentra ninun nodo en la lista
            if feat_return == False:

                if i == 0:
                    #estoy en el primer nodo, entonces hago el add del nodo
                    if self.addNodo(ver, ty_z, cota):
                        #si me agrego la cota, agrego la referencia en la tabla
                        #Traigo el ultimo nodo agregado
                        last_nodo = self.getLastPointAdded()
                        ag_nodos_tramos_entity.addNodoTramo(tramo_select.id(), last_nodo.id())



                elif i == (num_vert - 1):

                    if self.addNodo(ver, ty_z, cota):
                        #si me agrego la cota, agrego la referencia en la tabla
                        last_nodo = self.getLastPointAdded()
                        ag_nodos_tramos_entity.addNodoTramo(tramo_select.id(), last_nodo.id())

                else:
                    ty_z_ = ""
                    cota_ = ""
                    if self.addNodo(ver, ty_z_, cota_):
                        #si me agrego la cota, agrego la referencia en la tabla
                        last_nodo = self.getLastPointAdded()
                        ag_nodos_tramos_entity.addNodoTramo(tramo_select.id(), last_nodo.id())

            #aca encontro un nodo
            else:
                #como el nodo ya existe, lo unico que hago es agregar en la tabla referencia
                ag_nodos_tramos_entity.addNodoTramo(tramo_select.id(), feat_return.id())

            i = i + 1


    #agrega el 2do nodo al inicio.. Metodo usado cuando agrega la ventilacion individualmente
    def addNodoIntermedio(self, tramo_select, ag_nodos_tramos_layer, ini_fin):
        #si ini_fin es TRUE, es en el inicio, si es FALSE es al final

        point = None
        vertices = None
        geom_line = tramo_select.geometry()

        if ini_fin:
            point = geom_line.interpolate(10)

        else:
            # Obtengo el punto de la interpolacion
            point = geom_line.interpolate(geom_line.length() - 10)

        if self.addNodo(point.asPoint(), "", ""):

            last_nodo = self.getLastPointAdded()
            ag_nodos_tramos_entity = AgNodosTramosEntity()
            ag_nodos_tramos_entity.initialize(ag_nodos_tramos_layer)
            if ag_nodos_tramos_entity.addNodoTramo(tramo_select.id(), last_nodo.id()):
                return True
            else:
                return False

        else:
            return False



    def addNodoToFinal(self, tramo_select, ag_nodos_tramos_layer):
        point = None
        vertices = None
        geom_line = tramo_select.geometry()
        # Obtengo el punto de la interpolacion
        point = geom_line.interpolate(geom_line.length() - 10)

        if self.addNodo(point.asPoint(), "", ""):

            last_nodo = self.getLastPointAdded()
            ag_nodos_tramos_entity = AgNodosTramosEntity()
            ag_nodos_tramos_entity.initialize(ag_nodos_tramos_layer)
            if ag_nodos_tramos_entity.addNodoTramo(tramo_select.id(), last_nodo.id()):
                return True
            else:
                return False

        else:
            return False

    def deleteNodo(self, feat_delete):

        self.ag_nodo_layer.startEditing()
        res = self.ag_nodo_layer.deleteFeature(feat_delete.id())

        if res:

            if self.ag_nodo_layer.commitChanges():
                return True
            else:
                self.ag_nodo_layer.rollBack()
                return False
        else:
            return False

    def deleteNodoWithoutRef(self, tramo_select, ag_nodos_tramos_layer, nodos_ref):


         for nodos in self.ag_nodo_layer.getFeatures():

            #recorro la lista de referencias
            for feat in ag_nodos_tramos_layer.getFeatures():
                print(str(nodos.id()) + str(" : ") + str(feat['ag_nodos_id_ag_nodos']))
                if nodos.id() == feat['ag_nodos_id_ag_nodos'] and tramo_select.id() == feat['tramo_idtramo']:

                    #Vuelvo a reccrrer los nodos para eliminar
                    cant = 0

                    for nod in ag_nodos_tramos_layer.getFeatures():

                        if nodos.id() == nod['ag_nodos_id_ag_nodos']:
                            cant = cant + 1

                    if cant <= 1:

                        self.deleteNodo(nodos)







    def getLastPointAdded(self):

        features = self.ag_nodo_layer.getFeatures()
        last = None
        valor = -1
        for feat in features:
            if feat['gid'] > valor:
                valor = feat['gid']
                last = feat
        return last

    def getExistNodo(self, point):
        # recorro la capa de cl_nodos
        for feat in self.ag_nodo_layer.getFeatures():

            p = feat.geometry().asPoint()

            if p == point:
                return feat

        return False







