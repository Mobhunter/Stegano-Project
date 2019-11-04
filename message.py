# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'message.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 132)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(16, 12, 361, 111))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "РАБОТАЕМ"))
        self.label.setText(_translate("Form", "Пожалуйста подождите.\n"
                                              "Процесс может занять некоторое время. \n"
                                              "При закрытии этого окна\n"
                                              "процесс завершится."))
