from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from qgis.core import *
from qgis.utils import *
from qgis.gui import *
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
from os.path import expanduser
import processing
from    pyspatialite  import dbapi2 as sqlite
import  subprocess
import os

result = False

class MostraErros(QMainWindow):

 closed = pyqtSignal( int )

 def __init__(self, camada_erros, camada_base, camada_corrigida):
    
   QMainWindow.__init__(self)
   self.camada_erros = camada_erros
   self.camada_base = camada_base
   self.camada_corrigida = camada_corrigida
   self.canvas = QgsMapCanvas()
   self.canvas.setCanvasColor(Qt.white)
   self.canvas.setDestinationCrs(iface.mapCanvas().mapSettings().destinationCrs())
   self.ifaceCanvas =  iface.mapCanvas()

   self.x = 0
   
   self.selecionadas = []
   
   for feat in self.camada_base.selectedFeatures():
        self.selecionadas.append(feat.geometry().asPolyline())
        
   for feat in self.camada_erros.getFeatures():
            if feat.id() == self.x:
                self.canvas.setExtent(feat.geometry().boundingBox())
                self.canvas.refresh()
                self.ifaceCanvas.setExtent((feat.geometry().boundingBox()))
                self.ifaceCanvas.refresh()   
   
   self.canvas.setLayerSet([QgsMapCanvasLayer(self.camada_erros), QgsMapCanvasLayer(self.camada_corrigida)])

   self.setCentralWidget(self.canvas)

   actionZoomIn = QAction("Zoom in", self)
   actionZoomOut = QAction("Zoom out", self)
   actionPan = QAction("Pan", self)
   actionRepair = QAction("Repair", self)
   actionNext = QAction("Next Error", self)
   actionPrevious = QAction("Previous Error", self)

   
   actionZoomIn.setCheckable(True) 
   actionZoomOut.setCheckable(True)
   actionPan.setCheckable(True)

    

   self.connect(actionZoomIn, SIGNAL("triggered()"), self.zoomIn)
   self.connect(actionZoomOut, SIGNAL("triggered()"), self.zoomOut)
   self.connect(actionPan, SIGNAL("triggered()"), self.pan)
   self.connect(actionRepair, SIGNAL("triggered()"), self.repair)
   self.connect(actionNext, SIGNAL("triggered()"), self.next)
   self.connect(actionPrevious, SIGNAL("triggered()"), self.previous)
   
   self.toolbar = self.addToolBar("Canvas actions")
   self.toolbar.addAction(actionZoomIn)
   self.toolbar.addAction(actionZoomOut)
   self.toolbar.addAction(actionPan)
   self.toolbar.addAction(actionRepair)
   self.toolbar.addAction(actionPrevious)     
   self.toolbar.addAction(actionNext)
 

   # create the map tools
   self.toolPan = QgsMapToolPan(self.canvas)
   self.toolPan.setAction(actionPan)
   self.toolZoomIn = QgsMapToolZoom(self.canvas, False) # false = in
   self.toolZoomIn.setAction(actionZoomIn)
   self.toolZoomOut = QgsMapToolZoom(self.canvas, True) # true = out
   self.toolZoomOut.setAction(actionZoomOut)
   self.toolZoomOut = QgsMapToolZoom(self.canvas, True) # true = out
   self.toolZoomOut.setAction(actionZoomOut)
   

   self.ifaceCanvas.extentsChanged.connect(lambda:self.sync())
   self.canvas.extentsChanged.connect(lambda:self.sync2())

 def closeEvent(self, event):
    QgsMapLayerRegistry.instance().removeMapLayer(self.camada_erros)
    QgsMapLayerRegistry.instance().removeMapLayer(self.camada_corrigida)
  
 def zoomIn(self):
   self.canvas.setMapTool(self.toolZoomIn)

 def zoomOut(self):
   self.canvas.setMapTool(self.toolZoomOut)

 def pan(self):
   self.canvas.setMapTool(self.toolPan)
   
 def repair(self):
    for feat in self.camada_erros.getFeatures():
        if feat.id() == self.x:      
            geom_1 = feat.geometry()
            box_1 = geom_1.boundingBox()
          
    index_1 = QgsSpatialIndex()        
          
    for feat in self.camada_base.getFeatures():
        index_1.insertFeature(feat)

    deletar = index_1.intersects(box_1)
    
    index_2 = QgsSpatialIndex()        
          
    for feat in self.camada_corrigida.getFeatures():
        index_2.insertFeature(feat)

    adiconar = index_2.intersects(box_1)
    self.camada_base.startEditing()

    
    for feat in self.camada_base.getFeatures():
        if feat.id() in deletar and feat.geometry().asPolyline() in self.selecionadas:     
            self.camada_base.deleteFeature(feat.id())

        
    for feat in self.camada_corrigida.getFeatures():
        if feat.id() in adiconar:
            self.camada_base.addFeature(feat)
    self.ifaceCanvas.refresh()
    
 def next(self):
   if self.x < max(self.camada_erros.allFeatureIds()): 
    self.x = self.x+1
   else:  
    mostra_mensagem = iface.messageBar().pushMessage("last error was found", level=QgsMessageBar.INFO, duration =  10)    
                   
   for feat in self.camada_erros.getFeatures():
            if feat.id() == self.x:
                self.canvas.setExtent(feat.geometry().boundingBox())
                self.canvas.refresh()
                self.ifaceCanvas.setExtent((feat.geometry().boundingBox()))
                self.ifaceCanvas.refresh()
            feat            

 def previous(self):
    if self.x > 0:
       self.x = self.x-1 
       for feat in self.camada_erros.getFeatures():
                if feat.id() == self.x:
                    self.canvas.setExtent(feat.geometry().boundingBox())
                    self.canvas.refresh()
                    self.ifaceCanvas.setExtent((feat.geometry().boundingBox()))
                    self.ifaceCanvas.refresh()    
       
 def sync(self):
    if self.canvas.extent().center() <> self.ifaceCanvas.extent().center():
        self.canvas.setExtent(self.ifaceCanvas.extent())
        self.canvas.refresh()
    
 def sync2(self):
    if self.canvas.extent().center() <> self.ifaceCanvas.extent().center():
        self.ifaceCanvas.setExtent(self.canvas.extent())
        self.ifaceCanvas.refresh()