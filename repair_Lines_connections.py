# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RepairLinesConncetions
                                 A QGIS plugin
 Repair Lines Connections
                              -------------------
        begin                : 2018-05-16
        git sha              : $Format:%H$
        copyright            : (C) 2018 by carlos eduardo cagna / IBGE
        email                : carlos.cagna@ibge.gov.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from repair_Lines_connections_dialog import RepairLinesConncetionsDialog

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from qgis.core import *
from qgis.utils import *
from qgis.gui import *
from mostra_erros import MostraErros

import processing
import os.path


class RepairLinesConncetions:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'RepairLinesConncetions_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Repair Lines Connections')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'RepairLinesConncetions')
        self.toolbar.setObjectName(u'RepairLinesConncetions')
        
        self.painel_camadas = iface.legendInterface()
        self.layer = None
        self.unidade = 0
        
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('RepairLinesConncetions', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = RepairLinesConncetionsDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/RepairLinesConncetions/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Repair Lines Connections'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Repair Lines Connections'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def setar_variaveis(self):
        for layer in self.painel_camadas.layers():
            if layer.type() == QgsMapLayer.VectorLayer:
                if layer.geometryType() == QGis.Line:           
                    self.dlg.comboBox.addItem(layer.name())

    def acha_erros(self):

        outputs_QGISEXPLODELINES_1=processing.runalg('qgis:explodelines', self.layer,None)
        explode = QgsVectorLayer(outputs_QGISEXPLODELINES_1['OUTPUT'], ("final"), "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(explode, False)
        consulta_sql=('''
            select ST_Expand(geometry, %f) as geometry, conta
            from 
            (
            select geometry, count(ST_AsText(geometry)) as conta  
            from
            (Select ST_StartPoint(geometry) as geometry
            from input1
                             UNION ALL
             Select ST_EndPoint(geometry) as geometry
            from input1) as a
            group by ST_AsText(geometry)) as a
            where conta = 1'''%(self.dlg.doubleSpinBox.value()*self.unidade))
        
        outputs_QGISEXECUTESQL_1=processing.runalg('qgis:executesql', [outputs_QGISEXPLODELINES_1['OUTPUT'],], consulta_sql,None,None,0,'',None)
        QgsMapLayerRegistry.instance().removeMapLayer(explode)
            
        
        outputs_QGISJOINATTRIBUTESBYLOCATION_1=processing.runalg('qgis:joinattributesbylocation', outputs_QGISEXECUTESQL_1['OUTPUT_LAYER'],self.layer,['intersects','contains'],0.0,1,'',1,None)
        outputs_QGISEXTRACTBYATTRIBUTE_1=processing.runalg('qgis:extractbyattribute', outputs_QGISJOINATTRIBUTESBYLOCATION_1['OUTPUT'],'count',2,'1',None)    

        self.camada_erros = QgsVectorLayer(outputs_QGISEXTRACTBYATTRIBUTE_1['OUTPUT'], ("Connections Errors"), "ogr")  
        if self.camada_erros.featureCount() <> 0:
            QgsMapLayerRegistry.instance().addMapLayer(self.camada_erros)      

            renderizacao_da_consulta  = self.camada_erros.rendererV2()
            estilo_consulta = QgsFillSymbolV2.createSimple({'color':'0,0,0,0', 'color_border': '0,0,255','width_border':'1.5'})
            renderizacao_da_consulta.setSymbol(estilo_consulta)

            self.camada_erros = iface.activeLayer()


            self.camada_erros.startEditing()
            for feat in self.camada_erros.getFeatures():
                box = feat.geometry().boundingBox()
                id = feat.id()
                
                for feat in self.camada_erros.getFeatures():
                    if feat.id() == id+1:
                        index = QgsSpatialIndex()
                        index.insertFeature(feat)
                        if (index.intersects(box)) <> []:
                            self.camada_erros.deleteFeature(feat.id())
                
            self.camada_erros.commitChanges()     
            
    def corrigi_erros(self):
                                  
        xmin= self.layer.extent().xMinimum()
        xmax=self.layer.extent().xMaximum()
        ymin=self.layer.extent().yMinimum()
        ymax=self.layer.extent().yMaximum()

        extend =  str(float(xmin)) + ", " +  str(float(xmax))+", " + str(float(ymin))+ ", " +str(float(ymax))
        

        SELECTBYLOCATION_1=processing.runalg('qgis:selectbylocation', self.layer, self.camada_erros,['intersects','within'],0.0,0)
        SAVESELECTEDFEATURES_1=processing.runalg('qgis:saveselectedfeatures', SELECTBYLOCATION_1['OUTPUT'],None)
        autoincremental_1= processing.runalg('qgis:addautoincrementalfield',SAVESELECTEDFEATURES_1['OUTPUT_LAYER'],None)    
        CLEAN_1=processing.runalg('grass7:v.clean', autoincremental_1['OUTPUT'],1,3*self.unidade,extend,0.00001,0.0001,None,None)
        CLEAN_2=processing.runalg('grass7:v.clean', CLEAN_1['output'] ,2,3*self.unidade,extend,0.0001,0.0001,None,None)
        CLEAN_3=processing.runalg('grass7:v.clean', CLEAN_2['output'],0,3*self.unidade,extend,-1.0,0.0001,None,None)  
        dissolve_1= processing.runalg('qgis:dissolve',CLEAN_3['output'],False,'AUTO',None) 
        remove_field_1 = processing.runalg('qgis:deletecolumn', dissolve_1['OUTPUT'], "AUTO", None)        
 
 
        self.camada_corrigida = QgsVectorLayer(remove_field_1['OUTPUT'], "clean", "ogr") 
        QgsMapLayerRegistry.instance().addMapLayer(self.camada_corrigida)   

    def configura_camada_corrigida(self):        
        symbolList = self.camada_corrigida.rendererV2().symbols()
        symbol = symbolList[0]
        symLyrReg = QgsSymbolLayerV2Registry
        lineStyle = {'width':'0.50', 'color':'255,0,0'}
        symLyr1Meta = symLyrReg.instance().symbolLayerMetadata('SimpleLine')
        symLyr1 = symLyr1Meta.createSymbolLayer(lineStyle)
        symbol.appendSymbolLayer(symLyr1)
        markerStyle = {}
        markerStyle['width'] = '0.2'
        markerStyle['color'] = '0,0,0'
        markerStyle['placement'] = 'vertex'
        markerStyle['rotate'] = '1'
        symLyr2Meta = symLyrReg.instance().symbolLayerMetadata('MarkerLine')
        symLyr2 = symLyr2Meta.createSymbolLayer(markerStyle)
        sybSym = symLyr2.subSymbol()
        sybSym.deleteSymbolLayer(0)
        railStyle = {'size':'0,000005', 'size_unit':'MapUnit', 'color':'0,0,0,0', 'name':'circle', 'angle':'0', 'color_border':'255,0,0', 'width_border':'1.5', 'outline_width':'0.5' }
        railMeta = symLyrReg.instance().symbolLayerMetadata('SimpleMarker')
        rail = railMeta.createSymbolLayer(railStyle)
        sybSym.appendSymbolLayer(rail)
        symbol.appendSymbolLayer(symLyr2)            
        self.camada_corrigida.triggerRepaint()
        self.iface.legendInterface().refreshLayerSymbology(self.camada_corrigida)
        
    def print_a(self):
        print 'a'
 
    def run(self):
        """Run method that performs all the real work"""
        self.setar_variaveis()
        # show the dialog     
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.            
 
            self.ifaceCanvas =  iface.mapCanvas()
            self.ifaceCanvas.setDestinationCrs(QgsCoordinateReferenceSystem(4326))
            for layer in self.painel_camadas.layers():
                if  layer.name() == self.dlg.comboBox.currentText():
                    self.layer = layer 
                    
            if self.layer.crs().mapUnits() == 0:
                self.unidade = 1

            if self.layer.crs().mapUnits() == 2:
                self.unidade = 1e-05
            
            self.acha_erros()
            if self.camada_erros.featureCount() <> 0:
                self.corrigi_erros()   
                self.configura_camada_corrigida() 
                janela_erros = MostraErros(self.camada_erros, self.layer, self.camada_corrigida)       
                janela_erros.show() 
                            
            else: 
                mostra_mensagem = iface.messageBar().pushMessage("No Error Found", level=QgsMessageBar.INFO, duration =  10)            
                    
                    
            pass
