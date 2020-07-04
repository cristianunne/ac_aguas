from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.core import *



class AgTrdomEntity():
    
    def __init__(self, ag_trdom_layer):
        
        self.layer_ag_trdom = ag_trdom_layer
        
        
    def addSegment(self, feat_parcela, cl_tramo, linea, last_point):
        #Inicio la edicion de cl_trdom
        self.layer_ag_trdom.startEditing()
        gid_parcela = feat_parcela['gid']
        gid_ag_infotd_last = last_point['gid']
        gid_ag_tramo = cl_tramo['gid']

        fields = self.layer_ag_trdom.fields()
        #Obtengo los indice de cada uno de las gid foraneas
        idx_gid_parc =  fields.indexFromName("parcelas_idparcelas")
        idx_gid_ag_infotd =  fields.indexFromName("infotd_aginfotd")
        idx_gid_ag_tramo =  fields.indexFromName("tramos_agtramos")
        idx_length =  fields.indexFromName("longitud")
        
         #creo el arreglo vacion con la dimension de los atributos
        attrs = [None] * len( self.layer_ag_trdom.fields())
        
        #Asigno los valores al arreglo
        attrs[idx_gid_parc] = gid_parcela
        attrs[idx_gid_ag_infotd] = gid_ag_infotd_last
        attrs[idx_gid_ag_tramo] = gid_ag_tramo
        attrs[idx_length] = QgsGeometry.fromPolylineXY(linea).length()
        
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPolylineXY(linea))
        feature.setAttributes(attrs)
        
        res = self.layer_ag_trdom.addFeature(feature)
        
        if self.layer_ag_trdom.commitChanges():
            return res
        else:
            self.layer_ag_trdom.rollBack()
            return False
        
    def getLastLineAdded(self):
        
        features = self.layer_ag_trdom.getFeatures()
        last = features.next()
        
        for feat in features:
            last = feat
            
        return last
