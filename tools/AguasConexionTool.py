
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.core import *
from qgis.gui import QgsMessageBar
from qgis.utils import *
from ..Path import PathClass
import os

try:
    from qgis.PyQt.QtWidgets import *
except:
    pass

from ac_aguas.entities.AgTrdomEntity import AgTrdomEntity
from ac_aguas.entities.Ag_InfotdEntity import Ag_InfotdEntity



class AguasConexionTool():
    
    def __init__(self, iface, toolbar):
        
        self.iface = iface
        self.toolbar = toolbar
        self.canvas = self.iface.mapCanvas()
        
        self.result = False
        #Clase que maneja el trdom
        self.cl_trdom = None
        self.info_td = None

        dir = PathClass()
        filename = os.path.join(dir.getPath(), 'icons\conexion.png')
        # Create actions 
        self.nodos = QAction(QIcon(filename),  QCoreApplication.translate("ACAguas", "Crear Conexion Domiciliaria"),  self.iface.mainWindow())
        self.nodos.setCheckable(True)
        self.nodos.triggered.connect(self.conexionCloacas)
        
        # Add actions to the toolbar
        self.toolbar.addAction(self.nodos)

        
    def conexionCloacas(self):
        #evaluo que el currentlayer sea cl_tramos

        self.is_proyecto_c = self.is_project()
        if self.nodos.isChecked():
             #Verifico que las tablas esten cargadas
            try:

                if self.is_proyecto_c:
                    #Verifico que las tablas esten cargadas
                    layer_parcelas = QgsProject.instance().mapLayersByName('parcelas')[0]
                    layer_ag_tramos = QgsProject.instance().mapLayersByName('ag_tramos_p')[0]
                    layer_ag_infotd = QgsProject.instance().mapLayersByName('ag_infotd_p')[0]
                    layer_ag_trdom = QgsProject.instance().mapLayersByName('ag_trdom_p')[0]

                else:
                    layer_parcelas = QgsProject.instance().mapLayersByName('parcelas')[0]
                    layer_ag_tramos = QgsProject.instance().mapLayersByName('ag_tramos')[0]
                    layer_ag_infotd = QgsProject.instance().mapLayersByName('ag_infotd')[0]
                    layer_ag_trdom = QgsProject.instance().mapLayersByName('ag_trdom')[0]

                #Instancio la clase que maneja TRDOM
                self.ag_trdom = AgTrdomEntity(layer_ag_trdom)
                self.info_td = Ag_InfotdEntity(layer_ag_infotd)
                
                res_dialog = self.showdialog()
                if(res_dialog == 1):
                    self.processConexion(layer_parcelas, layer_ag_tramos)
                
                self.nodos.setChecked(False)
                
            except (IndexError, AttributeError):
                self.iface.messageBar().pushMessage("Error", "Debe cargar la capa 'ag_tramos', 'parcelas', 'ag_infotd' y 'ag_trdom'"  , Qgis.Critical)
                self.nodos.setChecked(False)
            


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



    def processConexion(self, layer_parcelas, layer_ag_tramos):
        #Obtengo las parcelas seleccionadas
        feat_parcelas = layer_parcelas.selectedFeatures()
        num_parc_sel = len(feat_parcelas)
        feat_agtramos = None
        num_agtramos_sel = 0

        
        try: 
            feat_agtramos = layer_ag_tramos.selectedFeatures()
            num_agtramos_sel = len(feat_agtramos)

            if num_agtramos_sel >= 1:
                feat_agtramos = layer_ag_tramos.selectedFeatures()[0]
                num_agtramos_sel = 1
                
            if(num_parc_sel == 0 or num_agtramos_sel == 0):
                self.iface.messageBar().pushMessage("Error", "Debe seleccionar al menos 1 parcela y 1 ag_tramo", Qgis.Warning)
            
            else:
                #Recorro cada uno de los features seleccionados
                for feat in feat_parcelas:
                    #Obtengo el Polygono convertido en linea
                    pol_line = self.polygonToLine(feat, layer_parcelas)
                    #Procedo a crear los centroides de las lineas
                    #Mando el layer_parcelas solo para obtener el sistema de coordenadas
                    centroid_layer = self.createPointMemLayer(layer_parcelas, 'centroides')
                    #creo los centroides de las lineas
                    centroids = self.createCentroidPoints(pol_line, centroid_layer)
                    vector_centroid_point = self.createPointCentroidsLayer(centroids, centroid_layer)
                    #creo la conexion
                    self.createConexion(feat_agtramos, vector_centroid_point, feat)
                    self.canvas.refresh()
            
        except (IndexError):
            num_cltramos_sel = 0
            self.iface.messageBar().pushMessage("Error", "Debe cargar la capa 'ag_tramos' y 'parcelas'", Qgis.Critical)
    
    def polygonToLine(self, feat_parc, layer_parcelas):
       
        #Me devuelve los puntos del poligono
        points_poly = self.getVertexAsPoint(feat_parc)
                #AHORA CONVIERTO A LINEA
        mem_layer = self.createMemLayer(layer_parcelas, "perimeto_pol")
        #QgsMapLayerRegistry.instance().addMapLayer(mem_layer)
        #Obtengo el numero de vertices
        num_point_poly = len(points_poly)
        array_line = []
        for i in range(num_point_poly - 1):
            #accedo al primer punto
            segmento = []
            segmento.append(points_poly[i])
            segmento.append(points_poly[i + 1])
            array_line.append(segmento)
    
        #Guarda el vector de linea creado
        vector_line = self.createVectorLayer(array_line, mem_layer)
        #QgsMapLayerRegistry.instance().addMapLayer(vector_line)
        return vector_line
    
    def getVertexAsPoint(self, feat):
        #Arreglo de puntos a devolver
        points = []
        geom = feat.geometry()
        n=0
        #ingresa por el primer vertice
        ver = geom.vertexAt(0)
        #count vertex and extract nodes
        while(ver != QgsPoint(0,0)):
          
            n +=1
            points.append(ver)
            ver=geom.vertexAt(n)
        return points
    
    def createMemLayer(self, layer, name):

        CRS = layer.crs().postgisSrid()
 
        URI = "MultiLineString?crs=epsg:"+str(CRS)+"&field=id:integer""&index=yes"
        #create memory layer
        mem_layer = QgsVectorLayer(URI,
                            name,
                            "memory")
        return mem_layer
    
    def createMemLayerLine(self, layer, name):

        CRS = layer.crs().postgisSrid()
 
        URI = "LineString?crs=epsg:"+str(CRS)+"&field=id:integer""&index=yes"
        #create memory layer
        mem_layer = QgsVectorLayer(URI,
                            name,
                            "memory")
        return mem_layer
    
    def createVectorLayer(self, array_line, mem_layer):
        #Arrayline contiene los puntos de las lineas
        #Prepare mem_layer for editing
        mem_layer.startEditing()
        n_seg = len(array_line)
        feature = QgsFeature()
        feature = []
        
        for i in range(n_seg):
            feat =QgsFeature()
            feature.append(feat)
            
        for i in range(n_seg):
            feature[i].setGeometry(QgsGeometry.fromPolyline(array_line[i]))
            feature[i].setAttributes([i])
        mem_layer.addFeatures(feature)
        mem_layer.commitChanges()
        return mem_layer
    
    def createPointMemLayer(self, layer, name):
        CRS = layer.crs().postgisSrid()
 
        URI = "Point?crs=epsg:"+str(CRS)+"&field=id:integer""&index=yes"
        #create memory layer
        mem_layer = QgsVectorLayer(URI,
                            name,
                            "memory")
        return mem_layer
    
    def createCentroidPoints(self, vector_line, mem_layer):
        feat_point = vector_line.getFeatures()
        centroids = []
        for feature in feat_point:
            centroids.append(feature.geometry().centroid().asPoint())
        return centroids
    
    def createPointCentroidsLayer(self, centroids, mem_layer):
        mem_layer.startEditing()
        num_cen = len(centroids)
        feature_cen = QgsFeature()
        feature_cen = []
        for i in range(num_cen):
            feat =QgsFeature()
            feature_cen.append(feat)
            
        for i in range(num_cen):
            feature_cen[i].setGeometry(QgsGeometry.fromPointXY(centroids[i]))
            feature_cen[i].setAttributes([i])
            
        mem_layer.addFeatures(feature_cen)
        mem_layer.commitChanges()
        #QgsMapLayerRegistry.instance().addMapLayer(mem_layer)
        return mem_layer
    
    def createConexion(self, feat_agtramos, layer_centroids, feat_parcela):

        #Obtengo la gemoetria del tramo
        geom_ag_tramos = feat_agtramos.geometry()
        #obtengo los features de los centroides
        feat_centroids  = layer_centroids.getFeatures()
        
        features = QgsFeature()
        features = []
        i = 0
        res = None
        for feat in feat_centroids:
            feat_ = QgsFeature()
            #print feat.geometry().asPoint().x()
            #print feat.geometry().asPoint().y()
            res = geom_ag_tramos.closestSegmentWithContext(feat.geometry().asPoint())[1]
            #agrego el closest segment
            #Evaluo si esta a la derecha o arriba y abajo
            x_cen = feat.geometry().asPoint().x()
            y_cen = feat.geometry().asPoint().y()
            x_colseg = res.x()
            y_colseg = res.y()
            
            #POINT AUX ES EL QUE LE DEBO ASIGNAR A CL_INFOTD

            poly = QgsGeometry.fromPolylineXY([feat.geometry().asPoint(), res])

            feat_.setGeometry(poly)
            feat_.setAttributes([i, feat_.geometry().length()])
            i= i+ 1
            features.append(feat_)
            
    
        feat_aux = None
        length = 0
        
        #closest.addFeatures(features)
       
        #QgsMapLayerRegistry.instance().addMapLayer(closest)
            
        #Evaluo el Tramo mas chico y ese es el closest segment que necesito tambien necesito evaluar que el punto sea mas cercano al centroide
        for feat in features:
            tam = feat.geometry().length()
                
            if(length == 0):
                length = tam
                feat_aux = feat
            elif (tam < length):
                length = tam
                feat_aux = feat
        
        #lA LINEA DEBE AGREGARSE A CL_TRDOM
        #Obtengo las coordenadas del punto del feat_aux
        
        linea_ = feat_aux.geometry().asPolyline()
        p1 = linea_[0]
        p2 = linea_[1]  

        point_aux = self.evaluatedPosicionPoint(p1.x(), p1.y(), p2.x(), p2.y())

        #vuelvo a crear la linea con los nuevos datos
        linea_feat = QgsFeature()
        
        poly = QgsGeometry.fromPolylineXY([point_aux, p2])

        linea_feat.setGeometry(poly)
        linea_feat.setAttributes([i, linea_feat.geometry().length()])
        
        linea_ = linea_feat.geometry().asPolyline()
        p1 = linea_[0]
        
        if self.info_td.addPoint(p1, feat_parcela, feat_agtramos):
            #Obtengo el ultimo point agregado
            last_p = self.info_td.getLastPointAdded()
    
            if self.ag_trdom.addSegment(feat_parcela, feat_agtramos, linea_, last_p):
                pass

                 
        else:
            self.iface.messageBar().pushMessage("Error", "Problema al crear las conexiones, verifique los datos e intente nuevamente", Qgis.Critical)
        
    def evaluatedPosicionPoint(self, x_cen, y_cen, x_colseg, y_colseg):
        
        point_aux = None
        
        #RESUELTO NO TOCARRRRR----------------------------------  
        if(x_colseg < x_cen and y_colseg == y_cen):
            point_aux = QgsPointXY(x_cen + 3.5, y_cen)

        #-------------------------------------------------------
        #RESUELTO NO TOCARRRRR----------------------------------  
        elif (x_colseg > x_cen and y_colseg == y_cen):
            
            point_aux = QgsPointXY(x_cen - 3.5, y_cen)
        
        #-------------------------------------------------------   
        elif (x_colseg == x_cen and y_colseg > y_cen):
            
            
            point_aux = QgsPointXY(x_cen, y_cen - 3.5)
            
        #RESUELTO NO TOCARRRRR----------------------------------  
        elif (x_colseg == x_cen and y_colseg < y_cen):
            
            point_aux = QgsPointXY(x_cen, y_cen + 3.5)
            
        #-------------------------------------------------------  
        
            
        elif (x_colseg < x_cen and y_colseg < y_cen):

            
            if (x_cen - x_colseg) > 2.5:
            
            
            
                point_aux = QgsPointXY(x_cen + 2.5, y_cen + 2.5)
                
                
            else:
                
                point_aux = QgsPointXY(x_cen, y_cen + 3.5)
            
            
        
        
        #RESUELTO NO TOCARRRRR----------------------------------    
        elif (x_colseg > x_cen and y_colseg > y_cen):
            
   
            if (x_colseg - x_cen) > 2.5:
                
                if (y_colseg - y_cen) > 2.5:
                    
                    point_aux = QgsPointXY(x_cen - 2.5, y_cen - 2.5)
                   
                else:
                 
                    point_aux = QgsPointXY(x_cen - 3.5, y_cen)
                    
                
            #consulto si es mayor a 2,5
            else:
                
                y_ = y_colseg - y_cen
                point_aux = QgsPointXY(x_cen, y_cen - 3.5)
               
                
        #RESUELTO NO TOCARRRRR----------------------------------    
        elif (x_colseg < x_cen and y_colseg > y_cen):

            
            if (x_cen - x_colseg) > 2.5:
                
                if (y_colseg - y_cen) > 2.5:
                   

                    point_aux = QgsPointXY(x_cen + 2.5, y_cen - 2.5)
                else:
                    
                    point_aux = QgsPointXY(x_cen + 3.5, y_cen)

                            
            else:
                if (y_colseg - y_cen) > 2.5:
                    
                    x_ = x_cen - x_colseg
                    point_aux = QgsPointXY(x_cen + x_, y_cen - 3.5)
                
                else:
                    y_ = y_colseg - y_cen
               
                    point_aux = QgsPointXY(x_cen + 3.5, y_cen + y_)
                
        #----------------------------------
        
        elif (x_colseg > x_cen and y_colseg < y_cen):
            if (x_colseg - x_cen) > 2.5:
                

                point_aux = QgsPointXY(x_cen - 2.5, y_cen + 2.5)
               
            else:
                
                point_aux = QgsPointXY(x_cen, y_cen + 2.5)
               
        
        return point_aux

    def createMemLayerSegment(self, layer, name):
        CRS = layer.crs().postgisSrid()
 
        URI = "MultiLineString?crs=epsg:"+str(CRS)+"&field=id:integer&field=length:float""&index=yes"
        #create memory layer
        mem_layer = QgsVectorLayer(URI,
                            name,
                            "memory")
        return mem_laye   

    def showdialog(self):
        
        retval = QMessageBox.question(self.iface.mainWindow(),
                "Question", "Crear Conexiones Domiciliarias?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        val = None
        
        if retval == QMessageBox.Yes:
            
            val = 1
        else:
            val = 0
        
        
        return val        
            
            