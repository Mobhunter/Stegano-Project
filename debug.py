from PIL import Image


def func(fname, res_fname, txt):
    # img = Image.open(self.fname)
    img = Image.open(fname)
    img = img.convert("RGB")
    pixels = img.load()
    x, y = img.size

    # text = iter(self.textEdit.toPlainText().encode("KOI8-R"))  # Текстовое сообщение
    text = iter(txt.encode("KOI8-R"))
    end_flag = False  # Нужен, чтобы вставлять нули, когда кончится текст

    # Вставляем биты в пиксели
    for i in range(x):
        for j in range(0, y, 3):
            if not end_flag:
                try:
                    lttr = bin(next(text))[2:].zfill(8)  # Буква из textEdit в бинарном виде
                except StopIteration:
                    end_flag = True
            else:
                print("Yay")
                lttr = "0" * 8
            # Так как в 3 пикселях 9 бит, а нам нужно восемь
            # Длинная проверка в range, чтобы записывалось сообщение, если пикселей меньше
            for k in range(j, (j + 3 if j + 3 <= y - 1 else j)):
                pixel = []
                for color in range(3):
                    if (k - j) * 3 + color != 8:
                        # Запись бита в пиксели
                        byte = int(lttr[(k - j) * 3 + color])
                        pixels_byte = int(bin(pixels[i, (k - j)][color])[-1])
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
    """m.close()
    res_fname = QFileDialog.getSaveFileName(
        self, "Результат", self.fname,
        f"Картинка (*.{self.fname.split('/')[-1].split('.')[-1]})"
    )"""
    img.save(res_fname)


func("фото.jpg", "res.jpg", """Для вас, души моей царицы,Красавицы, д шепот старины болтливой,Рукою верной я писал;Примите ж""")
