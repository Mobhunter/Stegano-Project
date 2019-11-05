import sys
import os
import zipfile

from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QWidget, QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtCore
from PIL import Image
from message import Ui_Form as message
from crypter import Ui_MainWindow as crypter
from decrypter import Ui_MainWindow as decrypter


class Crypter(QMainWindow, crypter):
    """Окно шифрования"""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.show()

    def initUI(self):
        self.fname = ""
        self.pushButton.clicked.connect(self.picture)
        self.pushButton_2.clicked.connect(self.crypt)
        self.buttonGroup.buttonClicked.connect(self.radioButtonClicked)

    def radioButtonClicked(self, button):
        """Включает или выключает textEdit"""
        if button.text().startswith("Текст"):
            self.textEdit.setEnabled(True)
        else:
            self.textEdit.setEnabled(False)

    def picture(self):
        """Выбор картинки для шифрования"""
        file, ok = QFileDialog.getOpenFileName(self, "Выберете картинку", "",
                                               "Картинка (*.png *.jpg *.bmp)")
        if ok:
            self.pushButton.setText(file.split("/")[-1])
            self.fname = file

    def crypt(self):
        """Функция шифрования
Вызывается при нашатии на кнопку 'Зашифровать'"""
        try:
            if self.buttonGroup.checkedButton().text().startswith("Текст"):
                self.text_crypt()
            else:
                self.files_crypt()
        except:
            # Вывод ошибки
            QMessageBox.critical(self, "Ошибка", "\n".join(map(repr, sys.exc_info())),
                                 QMessageBox.Ok)
            self.show()

    def text_crypt(self):
        """Шифрует текстовое сообщение в коддировке 'KOI8-R' картинку"""
        # Проверка на то, что картинка существует
        try:
            img = Image.open(self.fname)
            img = img.convert("RGB")
        except (FileNotFoundError, AttributeError):
            QMessageBox.critical(self, "Ошибка", "Вы не выбрали картинку!", QMessageBox.Ok)
        else:
            # Отображение окошка загрузки
            m = Message()
            m.show()
            self.hide()
            # Работа с картинкой
            pixels = img.load()
            x, y = img.size

            text = iter(self.textEdit.toPlainText().encode("KOI8-R"))  # Текстовое сообщение
            end_flag = False  # Нужен, чтобы вставлять нули, когда кончится текст

            # Вставляем биты в пиксели
            for i in range(x):

                m.change_val(i, x)  # Изменить значение PROGRESS BAR
                QApplication.processEvents()

                for j in range(0, y, 3):
                    if not end_flag:
                        # Проверка на конец заданной строки
                        try:
                            lttr = bin(next(text))[2:].zfill(8)  # Буква из textEdit в бинарном виде
                        except StopIteration:
                            end_flag = True
                            lttr = "0" * 8
                    else:  # Если кончилась строка, то заполняем пиксели нулями
                        lttr = "0" * 8
                    # Так как в 3 пикселях 9 бит, а нам нужно восемь
                    # Длинная проверка в range, чтобы записывалось сообщение, если пикселей меньше
                    # (Исправлю на предупреждение о сокращении количества символов заранее)
                    for k in range(j, (j + 3 if j + 3 <= y - 1 else j)):
                        pixel = []
                        for color in range(3):
                            if (k - j) * 3 + color != 8:
                                # Запись бита в пиксели
                                byte = int(lttr[(k - j) * 3 + color])
                                pixels_byte = int(bin(pixels[i, k][color])[-1])
                                if byte == 1 and pixels_byte == 0:
                                    pixel.append(pixels[i, k][color] + 1)
                                elif byte == 0 and pixels_byte == 1:
                                    pixel.append(pixels[i, k][color] - 1)
                                else:
                                    pixel.append(pixels[i, k][color])
                            else:
                                pixel.append(pixels[i, k][2])
                        pixels[i, k] = tuple(pixel)
            # Выбор результирующей картинки
            self.show()
            m.close()
            res_fname = QFileDialog.getSaveFileName(
                self, "Результат", self.fname,
                f"Картинка (*.{self.fname[-3:]})"
            )[0]
            if res_fname:
                img.save(res_fname)

    def files_crypt(self):
        if self.fname[-3:] not in ("png", "jpg", "bmp"):
            QMessageBox.critical(self, "Ошибка", "Вы не выбрали картинку!", QMessageBox.Ok)
        elif self.fname.endswith("bmp"):
            QMessageBox.critical(self, "Ошибка",
                                 "Для данного вида шифрования нельзя использовать .bmp",
                                 QMessageBox.Ok)
        else:
            direc = \
                QFileDialog.getExistingDirectory(self, "Выберете папку с файлами", "")
            m = Message()
            m.show()
            self.hide()
            zf = zipfile.ZipFile("data.zip", "w", compression=zipfile.ZIP_DEFLATED)
            for dirname, subdirs, files in os.walk(direc):
                zf.write(dirname)
                for filename in files:
                    zf.write(os.path.join(dirname, filename))
            zf.close()

            m.change_val(1, 2)  # Изменить значение PROGRESS BAR
            QApplication.processEvents()

            with open("data.zip", "rb") as zip_:
                with open(self.fname, "rb") as img:
                    res_img = img.read() + zip_.read()
            os.remove("data.zip")

            m.change_val(2, 2)  # Изменить значение PROGRESS BAR
            QApplication.processEvents()

            res_fname = QFileDialog.getSaveFileName(
                self, "Результат", self.fname,
                f"Картинка (*.{self.fname[-3:]})"
            )[0]
            if res_fname:
                with open(res_fname, "wb") as file:
                    file.write(res_img)


class Decrypter(QMainWindow, decrypter):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.show()

    def initUI(self):
        pass


class Message(QWidget, message):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

    def change_val(self, x, x_size):
        self.progressBar.setValue(int(x / x_size * 100))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Выбор программмы
    item, ok = QInputDialog.getItem(QWidget(), "Выберете программу", "Запустить",
                                    ("Шифровальщик", "Дешифровальщик"), 1, False)
    if ok:
        if item == "Дешифровальщик":
            w = Decrypter()
        elif item == "Шифровальщик":
            w = Crypter()
    else:
        sys.exit(0)
    sys.exit(app.exec())
