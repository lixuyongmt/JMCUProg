#coding: utf-8

import os
import sys
import ConfigParser

import jlink
import device

import sip
sip.setapi('QString', 2)
from PyQt4 import QtCore, QtGui, uic

'''
from MCUProg_UI import Ui_MCUProg
class MCUProg(QtGui.QWidget, Ui_MCUProg):
    def __init__(self, parent=None):
        super(MCUProg, self).__init__(parent)
        
        self.setupUi(self)
'''
class MCUProg(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MCUProg, self).__init__(parent)
        
        uic.loadUi('MCUProg.ui', self)

        self.initSetting()

        for dev in device.Devices:
            self.cmbMCU.addItem(dev)

    def initSetting(self):
        if not os.path.exists('setting.ini'):
            open('setting.ini', 'w')
        
        self.conf = ConfigParser.ConfigParser()
        self.conf.read('setting.ini')
        
        if not self.conf.has_section('globals'):
            self.conf.add_section('globals')
            self.conf.set('globals', 'mcutype', self.cmbMCU.itemText(0))
            self.conf.set('globals', 'dllpath', '')
            self.conf.set('globals', 'hexpath', '[]')
        self.cmbMCU.setCurrentIndex(self.cmbMCU.findText(self.conf.get('globals', 'mcutype')))
        self.linDLL.setText(self.conf.get('globals', 'dllpath'))
        for hexpath in eval(self.conf.get('globals', 'hexpath').decode('gbk')): self.cmbHEX.insertItem(10, hexpath)

    @QtCore.pyqtSlot()
    def on_btnDLL_clicked(self):
        dllpath = QtGui.QFileDialog.getOpenFileName(caption=u'JLinkARM.dll路径', filter=u'动态链接库 (*.dll)')
        if dllpath:
            self.linDLL.setText(dllpath)

    @QtCore.pyqtSlot()
    def on_btnHEX_clicked(self):
        hexpath = QtGui.QFileDialog.getOpenFileName(caption=u'程序文件路径', filter=u'程序文件 (*.bin)',
                                                    directory=self.cmbHEX.currentText(),)
        if hexpath:
            self.cmbHEX.insertItem(0, hexpath)
            self.cmbHEX.setCurrentIndex(0)

    @QtCore.pyqtSlot()
    def on_btnErase_clicked(self):
        self.lblInfo.setText(u'    开始擦除 ... ...')
        jlk = jlink.JLink(self.linDLL.text())
        dev = device.Devices[self.cmbMCU.currentText()](jlk)
        dev.chip_erase()
        self.lblInfo.setText(u'    擦除完成')

    @QtCore.pyqtSlot()
    def on_btnWrite_clicked(self):
        data = open(self.cmbHEX.currentText(), 'rb').read()
        data = [ord(x) for x in data]
        self.lblInfo.setText(u'    开始编程 ... ...')
        jlk = jlink.JLink(self.linDLL.text())
        dev = device.Devices[self.cmbMCU.currentText()](jlk)
        dev.chip_write(data)
        self.lblInfo.setText(u'    编程完成')
        jlk.reset()
        jlk.go()
    
    def closeEvent(self, evt):
        self.closed = True
        
        self.conf.set('globals', 'mcutype', self.cmbMCU.currentText())
        self.conf.set('globals', 'dllpath', self.linDLL.text())
        paths = []
        for i in range(min(10, self.cmbHEX.count())):
            paths.append(self.cmbHEX.itemText(i))
        self.conf.set('globals', 'hexpath', repr(paths))
        self.conf.write(open('setting.ini', 'w'))


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mcu = MCUProg()
    mcu.show()
    app.exec_()