import sys
import psycopg2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextEdit, QHBoxLayout
from PyQt5.QtCore import Qt
from playwright.sync_api import sync_playwright
from main_selectors import Selectors
import time


# Функция-декоратор для засечения времени выполнения функции
def timer(func):
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        result = func(self, *args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time of {func.__name__}: {execution_time} seconds")
        return result

    return wrapper

class SQLQueryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STATIX")
        self.init_ui()
        self.browser = None
        self.context = None
        self.page = None
        self.empty_page = None
        self.team1 = None
        self.team2 = None


    def create_browser(self, playwright):
        browser_type = playwright.chromium
        self.browser = browser_type.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.empty_page = self.context.new_page()

    def init_ui(self):
        layout = QVBoxLayout()

        # Создаем горизонтальный контейнер для полей ввода и кнопки
        input_layout = QHBoxLayout()

        self.entry_fields = []
        self.entry_adv = []
        self.teams = []
        self.accurate = []

        signs = ['Home Q1', 'Away Q1', 'Home Q2', 'Away Q2']
        for i in range(4):
            label = QLabel(signs[i])
            input_layout.addWidget(label)
            entry = QLineEdit()
            entry.setFixedWidth(25)
            input_layout.addWidget(entry)
            self.entry_fields.append(entry)

        layout.addLayout(input_layout)  # Добавляем горизонтальный контейнер в вертикальный

        # Создаем второй горизонтальный контейнер для расширенных значений
        input_advance = QHBoxLayout()
        signs_advance = ["Plus", "Minus", "Total", "HC"]
        for i in range(4):
            label = QLabel(signs_advance[i])
            input_advance.addWidget(label)
            entry_adv = QLineEdit()
            entry_adv.setFixedWidth(35)
            input_advance.addWidget(entry_adv)
            self.entry_adv.append(entry_adv)

        layout.addLayout(input_advance)  # Добавляем второй горизонтальный контейнер в вертикальный

        # Создаем четвертый горизонтальный контейнер для точных значений
        input_accurate = QHBoxLayout()
        signs_accurate = ["Acc. Total", "Acc. Hc"]
        for i, default_value in enumerate([2.5, 1.5]):
            label2 = QLabel(signs_accurate[i])
            input_accurate.addWidget(label2)
            entry_accurate = QLineEdit()
            entry_accurate.setFixedWidth(25)
            entry_accurate.setText(str(default_value))  # Устанавливаем значение по умолчанию
            input_accurate.addWidget(entry_accurate)
            self.accurate.append(entry_accurate)

            # Создаем кнопки "+" и "-"
            btn_plus = QPushButton("+")
            btn_plus.setFixedSize(25, 25)  # Устанавливаем размер кнопок
            btn_plus.clicked.connect(lambda _, index=i: self.change_accurate_value(index, 0.5))
            input_accurate.addWidget(btn_plus)

            btn_minus = QPushButton("-")
            btn_minus.setFixedSize(25, 25)  # Устанавливаем размер кнопок
            btn_minus.clicked.connect(lambda _, index=i: self.change_accurate_value(index, -0.5))
            input_accurate.addWidget(btn_minus)

        layout.addLayout(input_accurate)  # Добавляем четвертый горизонтальный контейнер в вертикальный

        # Создаем третий горизонтальный контейнер для команд
        input_teams = QHBoxLayout()
        signs_teams = ["Home", "Away"]
        for i in range(2):
            label1 = QLabel(signs_teams[i])
            input_teams.addWidget(label1)
            entry_teams = QLineEdit()
            entry_teams.setFixedWidth(120)
            input_teams.addWidget(entry_teams)
            self.teams.append(entry_teams)

        layout.addLayout(input_teams)  # Добавляем третий горизонтальный контейнер в вертикальный

        # Добавляем поле для ввода ссылки и кнопку для ее обработки
        link_layout = QHBoxLayout()
        link_label = QLabel("Ссылка:")
        self.link_entry = QLineEdit()
        link_layout.addWidget(link_label)
        link_layout.addWidget(self.link_entry)
        process_button = QPushButton("Обработать ссылку")
        process_button.clicked.connect(
            self.process_link_button_clicked)  # Связываем событие нажатия на кнопку с методом
        link_layout.addWidget(process_button)
        layout.addLayout(link_layout)

        execute_button = QPushButton("Выполнить запрос")
        execute_button.clicked.connect(self.execute_query)
        layout.addWidget(execute_button)

        self.result_textedit = QTextEdit()
        layout.addWidget(self.result_textedit)

        self.setLayout(layout)

        # Устанавливаем соединение для обработки событий клавиатуры для кнопки
        execute_button.setAutoDefault(True)
        execute_button.setDefault(True)
        execute_button.setFocus()

    def change_accurate_value(self, index, increment):
        try:
            current_value = float(self.accurate[index].text())
            new_value = current_value + increment
            if new_value >= 0:  # Убедитесь, что значение не станет отрицательным
                self.accurate[index].setText(str(new_value))
        except ValueError:
            pass  # Обработка некорректных значений, например, если поле не содержит число

    def process_link_button_clicked(self):
        # Получаем ссылку из поля ввода
        url = self.link_entry.text()
        # Вызываем функцию process_link с полученной ссылкой
        self.process_link(url)
    @timer
    def process_link(self, url):

        def find_average_value(coefline):
            k = None
            value = None
            min_diff = 100
            for case in coefline:
                current_total = case.split()[0]
                k1, k2 = list(map(float, case.split()[1:3]))
                diff = abs(k1 - k2)
                if diff < min_diff:
                    min_diff = diff
                    value = current_total
            print(f"The total/handicap with the smallest diff is: {value}")
            return float(value)




        try:

            page = self.page
            page.goto(url)

            team_home_element = page.query_selector(Selectors.team_home).text_content()
            team_away_element = page.query_selector(Selectors.team_away).text_content()
            league_element = page.query_selector(Selectors.tournament)
            league = league_element.text_content()
            t1_q1 = int(page.query_selector_all(Selectors.home_part[1])[0].inner_text())
            t2_q1 = int(page.query_selector_all(Selectors.away_part[1])[0].inner_text())
            t1_q2 = int(page.query_selector_all(Selectors.home_part[2])[0].inner_text())
            t2_q2 = int(page.query_selector_all(Selectors.away_part[2])[0].inner_text())
            try:
                t1_q3 = int(page.query_selector_all(Selectors.home_part[3])[0].inner_text())
                t2_q3 = int(page.query_selector_all(Selectors.away_part[3])[0].inner_text())
            except:
                t1_q3, t2_q3 = 0, 0
            print(team_home_element)
            print(team_away_element)
            print(league)
            print(t1_q1, t2_q1, t1_q2, t2_q2, t1_q3, t2_q3)

            self.team1 = team_home_element
            self.team2 = team_away_element

            page.click(Selectors.odds_on_bar)
            page.click(Selectors.total_button)

            aqurate_total = page.query_selector_all('.ui-table__row')

            ave_tot = []
            for element in aqurate_total:
                inner_text = element.inner_text()
                # Проверяем наличие элемента с атрибутом title, содержащим слово "removed"
                removed_element = element.query_selector('[title*="removed"]')
                if removed_element:
                    inner_text += " (removed)"
                    continue
                ave_tot.append(inner_text)

            avg_total_value = find_average_value(ave_tot)

            page.click(Selectors.handicap_button)

            aqurate_handicap = page.query_selector_all('.ui-table__row')

            ave_hand = []
            for element in aqurate_handicap:
                inner_text = element.inner_text()
                # Проверяем наличие элемента с атрибутом title, содержащим слово "removed"
                removed_element = element.query_selector('[title*="removed"]')
                if removed_element:
                    continue
                ave_hand.append(inner_text)
            avg_handicap_value = find_average_value(ave_hand)

            print(avg_total_value, avg_handicap_value)

            params = (t1_q1, t2_q1, t1_q2, t2_q2, avg_total_value, avg_handicap_value, team_home_element, team_away_element)
            self.execute_query(params)

        except Exception as e:
            print("Произошла ошибка при открытии страницы:", e)




    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.execute_query()
        elif event.key() == Qt.Key_Down:
            self.focus_next_field(1)
        elif event.key() == Qt.Key_Up:
            self.focus_next_field(-1)
        elif event.key() == Qt.Key_Right:
            self.focus_next_field(1)
        elif event.key() == Qt.Key_Left:
            self.focus_next_field(-1)
        else:
            super().keyPressEvent(event)  # Передаем остальные события базовому классу

    def focus_next_field(self, direction):
        current_widget = self.focusWidget()

        if current_widget in self.entry_fields:
            current_index = self.entry_fields.index(current_widget)
            next_index = (current_index + direction) % len(self.entry_fields)
            self.entry_fields[next_index].setFocus()
        elif current_widget in self.entry_adv:
            current_index = self.entry_adv.index(current_widget)
            next_index = (current_index + direction) % len(self.entry_adv)
            self.entry_adv[next_index].setFocus()

    def execute_query(self, params):

        try:
            t1q1, t2q1, t1q2, t2q2, total, hc, team1, team2 = params
            self.entry_fields[0].setText(str(t1q1))
            self.entry_fields[1].setText(str(t2q1))
            self.entry_fields[2].setText(str(t1q2))
            self.entry_fields[3].setText(str(t2q2))

            self.entry_adv[2].setText(str(total))
            self.entry_adv[3].setText(str(hc))

            self.teams[0].setText(team1)
            self.teams[1].setText(team2)
        except:
            pass


        values = [entry.text() for entry in self.entry_fields[:4]]
        print('Values:', values)



        try:
            plus, minus, total, handicap = [entry_adv.text() for entry_adv in self.entry_adv[:4]]
            acc_total, acc_hc = [entry_acc.text() for entry_acc in self.accurate]
            team1, team2 = [entry_team.text() for entry_team in self.teams]
        except:
            plus, minus, total, handicap, acc_total, acc_hc = 0, 0, None, None, 0, 0
        plus = int(plus) if plus.isdigit() else 0
        minus = int(minus) if minus.isdigit() else 0
        acc_total = float(acc_total) if acc_total else 0
        acc_hc = float(acc_hc) if acc_hc else 0

        print('Adv:', plus, minus, total, handicap, acc_total, acc_hc)
        self.team1 = team1
        self.team2 = team2

        try:
            conn = psycopg2.connect(
                host="127.0.0.1",
                user="postgres",
                password="123456er",
                port="5432"
            )
            cursor = conn.cursor()

            query = """
                SELECT total_ft, home_score_ft, away_score_ft, home_score_ft - away_score_ft AS handicap
                FROM matches
                JOIN details ON matches.match_id = details.match_id
                WHERE home_q1 >= %s - %s AND home_q1 <= %s + %s
                  AND away_q1 >= %s - %s AND away_q1 <= %s + %s
                  AND home_q2 >= %s - %s AND home_q2 <= %s + %s
                  AND away_q2 >= %s - %s AND away_q2 <= %s + %s
            """
            params = [values[0], minus, values[0], plus, values[1], minus, values[1], plus,
                      values[2], minus, values[2], plus, values[3], minus, values[3], plus]

            # Если введено значение Total, добавляем условие
            if total:
                total = float(total)
                query += " AND total >= %s - %s AND total <= %s + %s"
                # Добавляем значения для сравнения
                params.extend([total, acc_total, total, acc_total])

            # Если введено значение Handicap, добавляем условие
            if handicap:
                handicap = float(handicap)
                query += " AND handicap >= %s - %s AND handicap <= %s + %s"
                # Добавляем значения для сравнения
                params.extend([handicap, acc_hc, handicap, acc_hc])

            query += " ORDER BY total_ft ASC;"
            cursor.execute(query, params)

            results = cursor.fetchall()


            # Создаем списки для каждого поля
            total_ft_list = []
            home_score_ft_list = []
            away_score_ft_list = []
            handicap_list_ft = []

            # Добавляем значения из результатов запроса в соответствующие списки
            for result in results:
                total_ft_list.append(str(result[0]))
                home_score_ft_list.append(int(result[1]))
                away_score_ft_list.append(int(result[2]))
                handicap_list_ft.append(int(result[3]))

            # Формируем строки для каждого поля, разделяя значения пробелами
            formatted_total_ft = ' '.join(total_ft_list)
            formatted_home_score_ft = ' '.join(map(str,sorted(home_score_ft_list)))
            formatted_away_score_ft = ' '.join(map(str,sorted(away_score_ft_list)))
            formatted_handicap_ft = ' '.join(map(str, sorted(handicap_list_ft)))

            # Объединяем строки в одну с разделением по строкам
            formatted_results = (f"WITH CURRENT CONDITION ->\n{team1} - {team2}\n\nTotal: {formatted_total_ft}\n\nTeam1: "
                                 f"{formatted_home_score_ft}\n\nTeam2: {formatted_away_score_ft}\n\n"
                                 f"Handicap: {formatted_handicap_ft}\n---------------------------------------->\n")

            self.result_textedit.setText(formatted_results)
            print(formatted_results)
            cursor.close()
            conn.close()
        except psycopg2.Error as e:
            print("Ошибка при выполнении запроса:", e)


if __name__ == "__main__":
    with sync_playwright() as playwright:
        app = QApplication(sys.argv)
        window = SQLQueryApp()
        window.create_browser(playwright)  # Передача объекта playwright в метод create_browser
        window.show()
        sys.exit(app.exec_())