import os
import csv


class PriceMachine():
    """
    Класс для обработки и анализа файлов с ценами на продукцию.

    Сканирует каталог на наличие файлов с информацией о товарах,
    извлекает данные и позволяет выполнять поиск по наименованию товара,
    включая его частичное название, а также экспортировать результаты в HTML-формат.
    """

    def __init__(self):

        self.data = []
        self.result = []

    def load_prices(self, file_path='.'):  
        # - file_path (str): путь к каталогу, где находятся файлы (по умолчанию текущий каталог).
        """
        Загружает данные из CSV-файлов, содержащих информацию о товарах, ценах и весе.

        Ищет файлы с "price" в названии в указанном каталоге.
        Поддерживаются следующие наименования столбцов:

        - Для товара: "товар", "название", "наименование", "продукт".
        - Для цены: "розница", "цена".
        - Для веса: "вес", "масса", "фасовка".

        Если файл не содержит всех необходимых столбцов, он пропускается.
        Если строка содержит ошибки в формате данных, она также пропускается.
        Данные сортируются по цене за килограмм.

       
        
        """
        files = [file_name for file_name in os.listdir(file_path) if "price" in file_name]
        if not files:
            print(f"ОШИБКА: отсутствуют файлы прайс-листов в данном каталоге: "\
                  f"имя файла должно содержать слово 'price'.")
            exit(0)
        for file_name in files:
            with (open(file_name, mode='r', newline='', encoding='utf-8') as file):
                reader = csv.DictReader(file)  # загружаем csv-файл

                # находим требуемые столбцы
                headers = dict()
                headers["file"] = file_name
                for field in reader.fieldnames:
                    if field.lower() in ["название", "продукт", "товар", "наименование"]:
                        headers["name"] = field
                    elif field.lower() in ["цена", "розница"]:
                        headers["price"] = field
                    elif field.lower() in ["фасовка", "масса", "вес"]:
                        headers["weight"] = field

                # файл без нужных столбцов - пропускается
                if len(headers) != 4:
                    print(f"ВНИМАНИЕ: пропуск файла '{file_name}' не верные данные "
                          f"имен заголовков: {reader.fieldnames}")
                    continue

                # чтение данных из файла
                count = 1  # текущая сторка данных в файле
                for row in reader:
                    count += 1
                    row_d = dict()
                    row_d['name'] = row[headers['name']].lower()  # название товара
                    row_d['price'] = row[headers['price']]  # цена
                    row_d['weight'] = row[headers['weight']]  # вес в кг
                    row_d['file'] = headers["file"]  # файл .csv
                    try:
                        # рассчитываем цену за килограмм
                        row_d['price_for_kg'] = round(float(row_d['price']) / float(row_d['weight']), 2)  # цена за кг
                    except ValueError as ex:
                        # строка с ошибкой - пропускается
                        print(f"ВНИМАНИЕ: строка пропущена из-за ошибки формата, файл '{file_name}', "
                              f"строка {count}, данные: price = {row_d['price']}, weight = {row_d['weight']}.")
                        continue
                    self.data.append(row_d)

        # данные по цене за килограмм
        self.data = sorted(self.data, key=lambda x: x['price_for_kg'])

    def show_found_result(self):
        """
        Выводит на экран результаты поиска.

        Если результаты отсутствуют, ничего не выводится.
        """
        if self.result:
            print(f'{"№":5} {"Наименование":40} {"сумма, руб.":>7} {"вес, кг":>10} '
                  f'{"файл":>8} {"цена руб/кг.":>22}')
            count = 1
            for i in self.result:
                print(f'{count:<5} '
                      f'{self.data[i]["name"]:40} '
                      f'{self.data[i]["price"]:>7} '
                      f'{self.data[i]["weight"]:>12} '
                      f'{self.data[i]["file"]:>15}  '
                      f'{self.data[i]["price_for_kg"]:>11}')
                count += 1

    def export_to_html(self, fname='output.html'):
        """
        Экспортирует результаты поиска в HTML-файл.


        """
        result = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
        </head>
        <body>
            <table>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        """
        count = 1
        for i in self.result:
            result += "<tr>"
            result += f"<td>{count}</td>"
            result += f"<td>{self.data[i]['name']}</td>"
            result += f"<td>{self.data[i]['price']}</td>"
            result += f"<td>{self.data[i]['weight']}</td>"
            result += f"<td>{self.data[i]['file']}</td>"
            result += f"<td>{self.data[i]['price_for_kg']}</td>"
            result += "</tr>\n"
            count += 1
        result += "</tbody></table></body></html>"

        # сохранение HTML в файл
        with open(fname, mode="w", encoding="utf-8") as file:
            file.write(result)

    def find_text(self, text):
        """
        Выполняет поиск товаров, содержащих указанный текст в названии, и сохраняет их индексы в self.result.


        """
        self.result = []
        index = 0
        for row in self.data:
            if text in row["name"]:
                self.result.append(index)
            index += 1


if __name__ == "__main__":
    pm = PriceMachine()
    # загружаем данные из файлов
    pm.load_prices()
    prompt = "Введите название интересующего Вас товара (введите exit для выхода): "
    command = input(prompt).lower()
    while command != 'exit':
        # поиск товара по введенному названию
        pm.find_text(command)
        if not pm.result:
            print(f"Данные по запросу '{command}' отсутствуют.")
        else:
            print()
            pm.show_found_result()  # отображение результатов поиска

            print()
            print('анализ завершен')
            print()

            answer = input("Сохранить результаты в HTML-формате (д/н)? ")
            if answer.lower() == "д":
                while True:
                    filename = input("Введите имя HTML-файла для сохранения (введите exit для выхода): ").strip()
                    # проверка на ввод имени файла
                    if not filename:
                        print("ОШИБКА: введите имя файла.")
                        continue
                    elif filename == "exit":
                        exit(0)
                    # проверка существования файла
                    if os.path.isfile(filename):
                        answer = input(f"Файл '{filename}' существует. Перезаписать (д/н)? ")
                        if answer.lower() == "д":
                            break
                    else:
                        break
                # сохранение в HTML-файл
                pm.export_to_html(fname=filename)
                print(f"Файл '{filename}' СОХРАНЁН.")
        command = input(prompt).lower()
