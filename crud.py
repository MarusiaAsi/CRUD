
import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox

DB_NAME = "groups.db"


class AddFilmWidget(QMainWindow):
    def __init__(self, parent=None, student_id=None) :
        super().__init__(parent)
        self.con = sqlite3.connect(DB_NAME)
        self.params = {}
        uic.loadUi('addStudent.ui', self)
        self.selectGroups()
        self.student_id = student_id
        if student_id is not None :
            self.pushButton.clicked.connect(self.edit_elem)
            self.pushButton.setText('Отредактировать')
            self.setWindowTitle('Редактирование записи')
            self.get_elem()
        else :
            self.pushButton.clicked.connect(self.add_elem)

    def get_elem(self) :
        cur = self.con.cursor()
        item = cur.execute(
            f'SELECT groups.id, grouplist.groupselect, groups.name, groups.appraisals FROM groups JOIN grouplist ON grouplist.id = groups."group" WHERE groups.id = {self.student_id}').fetchone()
        self.comboBox.setCurrentText(item[1])
        self.name.setPlainText(str(item[2]))
        self.appraisals.setPlainText(str(item[3]))

    def selectGroups(self) :
        req = "SELECT * from grouplist"
        cur = self.con.cursor()
        for value, key in cur.execute(req).fetchall() :
            self.params[key] = value
        self.comboBox.addItems(list(self.params.keys()))

    def add_elem(self) :
        cur = self.con.cursor()
        try :
            id_off = cur.execute("SELECT max(id) FROM groups").fetchone()[0]
            new_data = (id_off + 1, self.params.get(self.comboBox.currentText()), self.name.toPlainText(),
                        int(self.appraisals.toPlainText()))
            cur.execute("INSERT INTO groups VALUES (?,?,?,?)", new_data)
        except ValueError as ve :
            self.statusBar().showMessage("Неверно заполнена форма")
            print(ve)
        else :
            self.con.commit()
            self.parent().update_films()
            self.close()

    def edit_elem(self) :
        cur = self.con.cursor()
        try :
            new_data = (self.params.get(self.comboBox.currentText()), self.name.toPlainText(),
                        int(self.appraisals.toPlainText()), self.student_id)
            cur.execute('UPDATE groups SET "group"=?, name=?, appraisals=? WHERE id=?', new_data)
        except ValueError as ve :
            self.statusBar().showMessage("Неверно заполнена форма")
            print(ve)
        else :
            self.con.commit()
            self.parent().update_films()
            self.close()

class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.con = sqlite3.connect(DB_NAME)
        self.update_films()
        self.pushButton.clicked.connect(self.update_films)
        self.addFilmButton.clicked.connect(self.add_film)
        self.editFilmButton.clicked.connect(self.edit_film)
        self.deleteFilmButton.clicked.connect(self.delete_film)
        self.dialogs = list()
        self.exitAction.triggered.connect(self.close_app)
        # self.tabWidget.currentChanged.connect(self.tab_changed)
        self.tableWidget.currentChanged.connect(self.update_films)

    def update_films(self):
        cur = self.con.cursor()
        # Получили результат запроса, который ввели в текстовое поле+
        que = 'SELECT groups.id, grouplist.groupselect, groups.name, groups.appraisals FROM groups JOIN grouplist ON grouplist.id = groups."group"'
        result = cur.execute(que).fetchall()

        # Заполнили размеры таблицы
        self.filmsTable.setRowCount(len(result))
        self.filmsTable.setColumnCount(len(result[0]))
        self.filmsTable.setHorizontalHeaderLabels(
            ['ID', 'Группа', 'Имя', 'Оценка'])
        # Заполнили таблицу полученными элементами
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.filmsTable.setItem(i, j, QTableWidgetItem(str(val)))

    # def update_genres(self):
    #     cur = self.con.cursor()
    #     # Получили результат запроса, который ввели в текстовое поле
    #     que = "SELECT id, groupselect FROM grouplist"
    #     result = cur.execute(que).fetchall()
    #
    #     # Заполнили размеры таблицы
    #     self.genresTable.setRowCount(len(result))
    #     self.genresTable.setColumnCount(len(result[0]))
    #     self.genresTable.setHorizontalHeaderLabels(
    #         ['ИД', 'Название жанра'])
    #
    #     # Заполнили таблицу полученными элементами
    #     for i, elem in enumerate(result):
    #         for j, val in enumerate(elem):
    #             self.genresTable.setItem(i, j, QTableWidgetItem(str(val)))

    def add_film(self):
        dialog = AddFilmWidget(self)
        dialog.show()

    # def add_genre(self):
    #     dialog = AddGenreWidget(self)
    #     dialog.show()

    def edit_film(self):
        rows = list(set([i.row() for i in self.filmsTable.selectedItems()]))
        ids = [self.filmsTable.item(i, 0).text() for i in rows]
        if not ids:
            self.statusBar().showMessage('Ничего не выбрано')
            return
        else:
            self.statusBar().showMessage('')
        dialog = AddFilmWidget(self, student_id=ids[0])
        dialog.show()

    # def edit_genre(self):
    #     rows = list(set([i.row() for i in self.genresTable.selectedItems()]))
    #     ids = [self.genresTable.item(i, 0).text() for i in rows]
    #     if not ids:
    #         self.statusBar().showMessage('Ничего не выбрано')
    #         return
    #     else:
    #         self.statusBar().showMessage('')
    #     dialog = AddGenreWidget(self, genre_id=ids[0])
    #     dialog.show()

    def delete_film(self):
        rows = list(set([i.row() for i in self.filmsTable.selectedItems()]))
        ids = [self.filmsTable.item(i, 0).text() for i in rows]
        if not ids:
            self.statusBar().showMessage('Ничего не выбрано')
            return
        else:
            self.statusBar().showMessage('')
        valid = QMessageBox.question(self, '', "Действительно удалить элементы с id " + ",".join(ids),
                                     QMessageBox.Yes,
                                     QMessageBox.No)
        # Если пользователь ответил утвердительно, удаляем элементы. Не забываем зафиксировать изменения
        if valid == QMessageBox.Yes:
            cur = self.con.cursor()
            cur.execute("DELETE from groups WHERE ID in (" + ", ".join('?' * len(ids)) + ")", ids)
            self.con.commit()
            self.update_films()

    # def delete_genre(self):
    #     rows = list(set([i.row() for i in self.genresTable.selectedItems()]))
    #     ids = [self.genresTable.item(i, 0).text() for i in rows]
    #     if not ids:
    #         self.statusBar().showMessage('Ничего не выбрано')
    #         return
    #     else:
    #         self.statusBar().showMessage('')
    #     valid = QMessageBox.question(self, '', "Действительно удалить элементы с id " + ",".join(ids),
    #                                  QMessageBox.Yes,
    #                                  QMessageBox.No)
    #     # Если пользователь ответил утвердительно, удаляем элементы. Не забываем зафиксировать изменения
    #     if valid == QMessageBox.Yes:
    #         cur = self.con.cursor()
    #         cur.execute("DELETE from groups WHERE id in (" + ", ".join('?' * len(ids)) + ")", ids)
    #         self.con.commit()
    #         self.update_genres()

    def close_app(self):
        self.close()

    def tab_changed(self, index):
        if index == 0:
            self.update_films()
        # else:
        #     self.update_genres()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MyWidget()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
