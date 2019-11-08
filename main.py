import sys
import os
import zipfile

from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QWidget, QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QImage, QIcon
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
        self.setWindowIcon(QIcon("./icons/icon.ico"))
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
        """Шифрует текстовое сообщение в коддировке 'koi8-r' картинку"""
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

            text = iter(self.textEdit.toPlainText().encode("koi8-r"))
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
                            lttr = bin(" ".encode("koi8-r")[0])[2:].zfill(8)
                    else:  # Если кончилась строка, то заполняем пиксели Пробелами
                        lttr = bin(" ".encode("koi8-r")[0])[2:].zfill(8)
                    # Так как в 3 пикселях 9 бит, а нам нужно восемь
                    # Длинная проверка в range, чтобы записывалось сообщение, если пикселей меньше
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
                self, "Результат", "",
                f"Картинка (*.png)"
            )[0]
            if res_fname:
                img.save(res_fname, "PNG")

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
                for filename in files:
                    if filename.endswith("data.zip"):
                        continue
                    zf.write(os.path.join(dirname, filename),
                             arcname=os.path.join(dirname, filename).split("/")[-1].replace('\\',
                                                                                            '/'))
            img = QImage(self.fname)
            x, y = img.width(), img.height()

            zf.setpassword(f"{x}{self.fname.split('/')[-1]}{y}".encode("utf-8"))
            zf.close()

            m.change_val(1, 2)  # Изменить значение PROGRESS BAR
            QApplication.processEvents()

            with open("data.zip", "rb") as zip_:
                with open(self.fname, "rb") as img:
                    res_img = img.read() + zip_.read()
            os.remove("data.zip")

            m.change_val(2, 2)  # Изменить значение PROGRESS BAR
            QApplication.processEvents()
            m.close()

            res_fname = QFileDialog.getSaveFileName(
                self, "Результат", self.fname,
                f"Картинка (*.{self.fname[-3:]})"
            )[0]
            if res_fname:
                with open(res_fname, "wb") as file:
                    file.write(res_img)
            self.show()


class Decrypter(QMainWindow, decrypter):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.show()

    def initUI(self):
        self.setWindowIcon(QIcon("./icons/icon.ico"))
        self.pushButton.clicked.connect(self.decrypt_image)

    def decrypt_image(self):
        """Вызывается при нажатии кнопки расшифровать"""
        try:
            self.imgname = QFileDialog.getOpenFileName(self, "Выберете картинку", "",
                                                       "Картинка (*.png *.jpg *.bmp)")[0]
            if not self.imgname:
                QMessageBox.critical(self, "Ошибка",
                                     "Вы не выбрали картинку",
                                     QMessageBox.Ok)
            else:
                # Если можно распаковать - распаковывем, иначе LSBшим
                try:
                    zf = zipfile.ZipFile(self.imgname)
                    zf.close()
                except zipfile.BadZipFile:
                    self.do_lsb()
                else:
                    self.do_zip()
        except:
            # Вывод ошибки
            QMessageBox.critical(self, "Ошибка", "\n".join(map(repr, sys.exc_info())),
                                 QMessageBox.Ok)

    def do_lsb(self):
        """Расшифровывает текстовое сообщение в формате koi8-r"""
        img = None
        try:
            img = Image.open(self.imgname)
        except (FileNotFoundError, AttributeError):
            if not self.imgname:
                QMessageBox.critical(self, "Ошибка",
                                     "Файл выбранный вами не является картинкой.",
                                     QMessageBox.Ok)
        if img:
            m = Message()
            m.show()
            self.hide()

            array = bytearray()
            x, y = img.size
            pixels = img.load()
            for i in range(x):

                m.change_val(i, x)  # Изменить значение PROGRESS BAR
                QApplication.processEvents()

                for j in range(0, y, 3):
                    num = 0
                    for k in range(j, (j + 3 if j + 3 <= y - 1 else j)):
                        for color in range(3):
                            if (k - j) * 3 + color != 8:
                                bn = bin(pixels[i, k][color])
                                n = 8 - (3 * (k - j) + color)
                                num += int('0b' +
                                           bn[-1].ljust(n, "0"),
                                           base=2)
                    array.append(num)

            self.show()
            m.close()
            self.textBrowser.setPlainText(array.decode("koi8-r", 'ignore').rstrip())

    def do_zip(self):
        """Распаковать из картинки-архива"""
        img = QImage(self.imgname)
        x, y = img.width(), img.height()

        direc = QFileDialog.getExistingDirectory(self, "Выберете папку для выгрузки", "")
        if direc:
            # Работа с окошками
            m = Message()
            m.show()
            self.hide()
            m.change_val(1, 2)
            # Распаковываем архив
            with zipfile.ZipFile(self.imgname) as zf:
                zf.extractall(path=direc, pwd=f"{x}{self.imgname.split('/')[-1]}{y}".encode("utf-8"))
            self.show()



class Message(QWidget, message):
    """Окно загрузки"""
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.setWindowIcon(QIcon("./icons/icon.ico"))

    def change_val(self, x, x_size):
        self.progressBar.setValue(int(x / x_size * 100))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Выбор программмы
    w = QWidget()
    w.setWindowIcon(QIcon("./icons/icon.ico"))
    item, ok = QInputDialog.getItem(w, "Выберете программу", "Запустить",
                                    ("Шифровальщик", "Дешифровальщик"), 1, False)
    if ok:
        if item == "Дешифровальщик":
            w = Decrypter()
        elif item == "Шифровальщик":
            w = Crypter()
    else:
        sys.exit(0)
    sys.exit(app.exec())
