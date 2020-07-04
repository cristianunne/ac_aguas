# coding=utf-8
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.core import *
from qgis.gui import *

try:
    from qgis.PyQt.QtWidgets import *
except:
    pass

import operator


from ..entities.AgTramosEntity import AgTramosEntity

from ..dialogs.Ag_Hidrantes import AgHidrantesDialog



class HidranteMouseEffect(QgsMapTool):
    select_ = pyqtSignal(object)

    def __init__(self, iface):
        QgsMapTool.__init__(self, iface.mapCanvas())
        self.iface = iface
        self.qpoint = None
        self.geom_Sel = None
        self.canvas = iface.mapCanvas()
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                       "      c None",
                                       ".     c #FF0000",
                                       "+     c #FFFFFF",
                                       "                ",
                                       "       +.+      ",
                                       "      ++.++     ",
                                       "     +.....+    ",
                                       "    +.     .+   ",
                                       "   +.   .   .+  ",
                                       "  +.    .    .+ ",
                                       " ++.    .    .++",
                                       " ... ...+... ...",
                                       " ++.    .    .++",
                                       "  +.    .    .+ ",
                                       "   +.   .   .+  ",
                                       "   ++.     .+   ",
                                       "    ++.....+    ",
                                       "      ++.++     ",
                                       "       +.+      "]))

        self.dlg_ag_hidrantes = AgHidrantesDialog()

        self.ag_tramo_entity = AgTramosEntity()

    def initialize(self, ag_hidrantes_layer):

        self.ag_hidrantes_layer = ag_hidrantes_layer

    def canvasPressEvent(self, e):
        self.qpoint = self.toMapCoordinates(e.pos())

    def canvasMoveEvent(self, event):
        pass

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        pass

    def canvasReleaseEvent(self, event):

        res = self.selecciona(self.qpoint)

        if res == True:
            #tengo que hacer el closest y tomar el punto final
            res_clos = self.geom_Sel.geometry().closestSegmentWithContext(self.qpoint)[1]
            layer = self.canvas.currentLayer()

            # Cargo el Dialog del Final
            res_ = self.dlg_ag_hidrantes.exec_()

            if res_ == 1:

                hid_sel = self.getButtonSelect()
                angulo = self.getAngulo(self.geom_Sel, res_clos)

                #Deberia agregar el Hidrante y Rotar Luego
                self.addHidranteTemp(hid_sel, angulo, res_clos)
                self.canvas.refresh()

                #consulto si va a rotar y cambios el atributo angulo
                res_rotar = self.showdialog()

                if res_rotar == 1:
                    angulo = angulo + 180
                    self.addHidrante(angulo, res, hid_sel, res_clos)

                else:
                    self.addHidrante(angulo, res, hid_sel, res_clos)


        else:
            self.select_.emit(False)


    def addHidranteTemp(self, hid_sel, angulo, res_clos):
        # Inicio la edicion de la capa hidrantes
        # creo el arreglo vacion con la dimension de los atributos
        attrs = [None] * len(self.ag_hidrantes_layer.fields())
        idx_ty_hid = self.ag_hidrantes_layer.fields().indexFromName("ty_hid")
        idx_angulo = self.ag_hidrantes_layer.fields().indexFromName("angulo")
        idx_id_tramo = self.ag_hidrantes_layer.fields().indexFromName("tramo_idtramo")

        attrs[idx_ty_hid] = hid_sel
        attrs[idx_angulo] = angulo
        attrs[idx_id_tramo] = self.geom_Sel.id()

        self.ag_hidrantes_layer.startEditing()

        self.feature = QgsFeature()
        self.feature.setGeometry(QgsGeometry.fromPointXY(res_clos))
        self.feature.setAttributes(attrs)

        res = self.ag_hidrantes_layer.addFeature(self.feature)

        return res



    def addHidrante(self, angulo, res, hid_sel, res_clos):

        #Elimino el feature y lo agrego unuevamente
        if res:
            self.ag_hidrantes_layer.rollBack()

        attrs = [None] * len(self.ag_hidrantes_layer.fields())
        idx_ty_hid = self.ag_hidrantes_layer.fields().indexFromName("ty_hid")
        idx_angulo = self.ag_hidrantes_layer.fields().indexFromName("angulo")
        idx_id_tramo = self.ag_hidrantes_layer.fields().indexFromName("tramo_idtramo")

        attrs[idx_ty_hid] = hid_sel
        attrs[idx_angulo] = angulo
        attrs[idx_id_tramo] = self.geom_Sel.id()

        self.ag_hidrantes_layer.startEditing()

        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPointXY(res_clos))
        feature.setAttributes(attrs)

        res = self.ag_hidrantes_layer.addFeature(feature)

        if res:

            if self.ag_hidrantes_layer.commitChanges():
                pass
            else:
                self.ag_hidrantes_layer.rollBack()

    def selecciona(self, point):

        # Borro la seleccion actual
        mc = self.iface.mapCanvas()

        for layer in mc.layers():
            if layer.type() == layer.VectorLayer:
                layer.removeSelection()
            mc.refresh()

        pntGeom = QgsGeometry.fromPointXY(self.qpoint)
        pntBuffer = pntGeom.buffer((mc.mapUnitsPerPixel() * 2), 0)
        rectan = pntBuffer.boundingBox()
        cLayer = mc.currentLayer()
        cLayer.selectByRect(rectan, False)

        feats = cLayer.selectedFeatures()
        n = len(feats)

        # si n es mayor a1 deselecciono, los demas a expecion del primer elemento
        if n >= 1:
            if n > 1:
                i = 1
                while (i < n):
                    cLayer.deselect(feats[i].id())
                    i = i + 1
                self.geom_Sel = cLayer.selectedFeatures()[0]
            else:
                self.geom_Sel = cLayer.selectedFeatures()[0]

            mc.refresh()
            return True
        else:
            return False

    def getAngulo(self, tramo_select, point_closest):

        # Obtengo los puntos del tramo seleccionado
        array_point_tramo = self.ag_tramo_entity.getVertexTramoAsPoint(tramo_select)

        #EL POINT CENTROIDE SERIA EL PUNTO QUE OBTENGO DEL CLOSEST
        # obtengo el numero de vertices
        num_ver = self.ag_tramo_entity.getNumVertex(tramo_select)
        diccionario = {}
        if num_ver > 2:
            i = 0
            for point in array_point_tramo:
                diccionario[i] = point_closest.distance(QgsPointXY(point.x(), point.y()))
                i = i + 1

        resultado = sorted(diccionario.items(), key=operator.itemgetter(1))

        mem_line_segment = self.segmentLineToLine(tramo_select)

        linea_target = None

        for linea in mem_line_segment.getFeatures():
            buffer = QgsGeometry.fromPointXY(QgsPointXY(point_closest.x(), point_closest.y())).buffer(0.2, 1)

            if linea.geometry().intersects(buffer):
                linea_target = linea

            # obtengo los vertices de la linea target como point
        linea_target_point = self.ag_tramo_entity.getVertexTramoAsPoint(linea_target)

        point_select = linea_target_point[1]

        # calculo el angulo de orientacion del icono
        angulo = point_closest.azimuth(QgsPointXY(point_select.x(), point_select.y())) + 2

        return angulo - 90


    def segmentLineToLine(self, tramo_select):
        # Obtengo los puntos del tramo seleccionado
        array_point_tramo = self.ag_tramo_entity.getVertexTramoAsPoint(tramo_select)
        num_point_poly = len(array_point_tramo)
        mem_layer = self.createMemLayer(self.ag_hidrantes_layer, "segment_line")
        array_line = []
        for i in range(num_point_poly - 1):
            # accedo al primer punto
            segmento = []
            segmento.append(array_point_tramo[i])
            segmento.append(array_point_tramo[i + 1])
            array_line.append(segmento)
        # Guarda el vector de linea creado
        vector_line = self.loadVectorLayer(array_line, mem_layer)
        return vector_line

    def loadVectorLayer(self, array_line, mem_layer):
        # Arrayline contiene los puntos de las lineas
        # Prepare mem_layer for editing
        mem_layer.startEditing()
        n_seg = len(array_line)
        feature = QgsFeature()
        feature = []
        for i in range(n_seg):
            feat = QgsFeature()
            feature.append(feat)

        for i in range(n_seg):
            feature[i].setGeometry(QgsGeometry.fromPolyline(array_line[i]))
            feature[i].setAttributes([i])
        mem_layer.addFeatures(feature)
        mem_layer.commitChanges()
        return mem_layer

    def createMemLayer(self, vector_layer, name):

        CRS = vector_layer.crs().postgisSrid()

        URI = "MultiLineString?crs=epsg:" + str(CRS) + "&field=id:integer""&index=yes"
        # create memory layer
        mem_layer = QgsVectorLayer(URI,
                                   name,
                                   "memory")
        return mem_layer

    def getButtonSelect(self):

        if self.dlg_ag_hidrantes.rb_hid_1.isChecked():
            return self.dlg_ag_hidrantes.rb_hid_1.text()

        elif self.dlg_ag_hidrantes.rb_hid_2.isChecked():

            return self.dlg_ag_hidrantes.rb_hid_2.text()

        elif self.dlg_ag_hidrantes.rb_hid_3.isChecked():

            return self.dlg_ag_hidrantes.rb_hid_3.text()

        elif self.dlg_ag_hidrantes.rb_hid_4.isChecked():

            return self.dlg_ag_hidrantes.rb_hid_4.text()

        elif self.dlg_ag_hidrantes.rb_hid_5.isChecked():

            return self.dlg_ag_hidrantes.rb_hid_5.text()

        elif self.dlg_ag_hidrantes.rb_hid_6.isChecked():

            return self.dlg_ag_hidrantes.rb_hid_6.text()

        elif self.dlg_ag_hidrantes.rb_hid_7.isChecked():

            return self.dlg_ag_hidrantes.rb_hid_7.text()

        elif self.dlg_ag_hidrantes.rb_hid_8.isChecked():

            return self.dlg_ag_hidrantes.rb_hid_8.text()

        elif self.dlg_ag_hidrantes.rb_hid_9.isChecked():

            return self.dlg_ag_hidrantes.rb_hid_9.text()

        elif self.dlg_ag_hidrantes.rb_hid_10.isChecked():

            return self.dlg_ag_hidrantes.rb_hid_10.text()

        elif self.dlg_ag_hidrantes.rb_hid_11.isChecked():

            return self.dlg_ag_hidrantes.rb_hid_11.text()

        elif self.dlg_ag_hidrantes.rb_hid_12.isChecked():

            return self.dlg_ag_hidrantes.rb_hid_12.text()

        elif self.dlg_ag_hidrantes.rb_hid_13.isChecked():

            return self.dlg_ag_hidrantes.rb_hid_13.text()



    def createMemLayerPoint(self, layer, name):

        CRS = layer.crs().postgisSrid()
        URI = "Point?crs=epsg:" + str(CRS) + "&field=id:integer""&index=yes"
        # create memory layer
        mem_layer = QgsVectorLayer(URI,
                                   name,
                                   "memory")
        return mem_layer


    def showdialog(self):

        retval = QMessageBox.question(self.iface.mainWindow(),
                                      "Question", "Rotar 180° el simbolo?",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        val = None

        if retval == QMessageBox.Yes:

            val = 1
        else:
            val = 0

        return val