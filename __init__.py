# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RepairLinesConncetions
                                 A QGIS plugin
 Repair Lines Connections
                             -------------------
        begin                : 2018-05-16
        copyright            : (C) 2018 by carlos eduardo cagna / IBGE
        email                : carlos.cagna@ibge.gov.br
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load RepairLinesConncetions class from file RepairLinesConncetions.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .repair_Lines_connections import RepairLinesConncetions
    return RepairLinesConncetions(iface)
