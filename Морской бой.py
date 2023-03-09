from random import randint, choice
import string
import time


class Ship:  # Класс корабля
    def __init__(self, length, tp=1, x=None, y=None):
        self._length = length  # длина корабля (число палуб: целое значение: 1, 2, 3 или 4);
        self._tp = tp  # ориентация корабля (1 - горизонтальная; 2 - вертикальная)
        self._x = x  # координаты начала расположения корабля (целые числа);
        self._y = y
        self._is_move = True  # возможно ли перемещение корабля (изначально равно True);
        self._cells = [1] * length  # изначально список длиной length, состоящий из единиц
        self.destroyed = False  # уничтожен ли корабль, изначально False

    def set_start_coords(self, x, y):  # установка начальных координат (запись значений в локальные атрибуты _x, _y)
        self._x = x
        self._y = y

    def get_start_coords(self):  # получение начальных координат корабля в виде кортежа x, y;
        return self._x, self._y

    def ship_coords(self):  # получение кортежа из координат всех точек корабля
        coords = (self._y, self._x),
        for i in range(1, self._length):
            if self._tp == 2:
                coords += (self._y + i, self._x),
            elif self._tp == 1:
                coords += (self._y, self._x + i),
        return coords

    def ship_borders(self):  # получение игровый зоны корабля
        borders = []
        if self._tp == 2:
            borders.extend(Ship(self._length + 2, self._tp, self._x - 1, self._y - 1).ship_coords())
            borders.extend(Ship(self._length + 2, self._tp, self._x, self._y - 1).ship_coords())
            borders.extend(Ship(self._length + 2, self._tp, self._x + 1, self._y - 1).ship_coords())
        elif self._tp == 1:
            borders.extend(Ship(self._length + 2, self._tp, self._x - 1, self._y - 1).ship_coords())
            borders.extend(Ship(self._length + 2, self._tp, self._x - 1, self._y).ship_coords())
            borders.extend(Ship(self._length + 2, self._tp, self._x - 1, self._y + 1).ship_coords())
        borders = tuple(filter(lambda x: x[0] >= 0 and x[1] >= 0, borders))
        return borders

    def move(self, go):
        """перемещение корабля в направлении его ориентации на go клеток (go = 1 - движение в одну сторону на клетку;
        go = -1 - движение в другую сторону на одну клетку); движение возможно только если флаг _is_move = True;"""

        if self._is_move:
            if self._tp == 2:
                self._y += -go
            elif self._tp == 1:
                self._x += go

    def is_collide(self, ship):
        """проверка на столкновение с другим кораблем ship (столкновением считается,
         если другой корабль или пересекается с текущим или просто соприкасается, в том числе и по диагонали);
         метод возвращает True, если столкновение есть и False - в противном случае;"""

        return not set(self.ship_borders()).isdisjoint(ship.ship_coords())

    def is_out_pole(self, size):
        """проверка на выход корабля за пределы игрового поля (size - размер игрового поля, обычно, size = 10);
        возвращается булево значение True, если корабль вышел из игрового поля и False - в противном случае;"""
        coords = [a for b in self.ship_coords() for a in b]
        return not all([0 <= j <= size - 1 for j in coords])

    def __getitem__(self, item):
        return self._cells[item]

    def __setitem__(self, key, value):
        self._cells[key] = value


class GamePole:  # Класс игрового пол
    def __init__(self, size):
        self._size = size
        self._ships = []
        self._gamepole = [[0 for j in range(size)] for i in range(size)]

    def chek_ship(self, ship):
        """Проверка нахождения корабля в игровой зоне и что он не пересекается с другими короблями.
        Возврощает True, если условия выполнены"""
        if not ship.is_out_pole(self._size):
            return all([not ship.is_collide(i) for i in self._ships if i != ship]) or not self._ships
        return False

    def filling_gamepole(self):  # Заполнение игрового поля значениями добавленных кораблей
        self._gamepole = [[0 for j in range(self._size)] for i in range(self._size)]
        for ship in self.get_ships():
            for coords, cell in zip(ship.ship_coords(), ship._cells):
                self._gamepole[coords[0]][coords[1]] = cell

    def init(self):
        """начальная инициализация игрового поля; здесь создается список из кораблей (объектов класса Ship):
        однопалубных - 4; двухпалубных - 3; трехпалубных - 2; четырехпалубный - 1. Ориентация случайная"""
        free_cells = [(i, j) for j in range(self._size) for i in range(self._size)]
        size_ships = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        for size in size_ships:
            ship = Ship(size, randint(1, 2))
            while True:
                ship.set_start_coords(*choice(free_cells))
                if self.chek_ship(ship):
                    self._ships.append(ship)
                    break
        self.filling_gamepole()

    def get_ships(self):  # возвращает коллекцию _ships;
        return self._ships

    def move_ships(self):
        """ перемещает каждый корабль из коллекции _ships на одну клетку (случайным образом вперед или назад)
        в направлении ориентации корабля; если перемещение в выбранную сторону
        невозможно (другой корабль или пределы игрового поля), то попытаться переместиться в противоположную сторону,
        иначе (если перемещения невозможны), оставаться на месте;"""
        for ship in self._ships:  # Проходим циклом по кораблям
            go = choice([1, -1])  # Рандомный выбор стороны перемещения
            ship.move(go)  # Двигаем карабль
            if not self.chek_ship(ship):  # Проверка,после перемещения на возможность расположения там корабля
                ship.move(-go * 2)  # Если нет, то двигаем на 2 клетки в противоположную сторону
                if not self.chek_ship(ship):  # Снова проверям
                    ship.move(go)  # Если опять невозможно, двигаем корабль на исходную точку
            self.filling_gamepole()  # Перезаполняем игровое поле

    def show(self):
        """отображение игрового поля в консоли
        (корабли должны отображаться значениями из коллекции _cells каждого корабля, вода - значением 0);"""
        print("     " + " ".join(list(string.ascii_letters[:self._size])))
        for numb, i in enumerate(self._gamepole):
            print(str(numb + 1).rjust(2, " ") + ' |', *i)

    def get_pole(self):
        """получение текущего игрового поля в виде двумерного (вложенного) кортежа размерами size x size элементов."""
        return tuple(tuple(i) for i in self._gamepole)


class SeaBattle:  # Класс для управления игровым процессом в целом
    def __init__(self):
        self.gamepole_player = GamePole(10)  # Игровое поле игрока
        self.gamepole_player_attack = GamePole(10)  # Инфополе для отоброжения поподаний игрока
        self.gamepole_player.init()  # Заполнение поля корабялми
        self.gamepole_ii = GamePole(10)  # Игровое поле ИИ
        self.gamepole_ii.init()  # Заполнение поля корабялми
        self.latters = {latters: numb for numb, latters in enumerate(string.ascii_letters[:self.gamepole_player._size])}
        self.game_over = False
        self.coords = [(i, j) for j in range(self.gamepole_player._size) for i in range(self.gamepole_player._size)]

    def chek_coords(self, coords):  # Проверка существования игровой координаты
        try:
            coords_attack = int(coords[1:]) - 1, self.latters[coords[0]]
            chek = self.gamepole_player._gamepole[coords_attack[0]][coords_attack[1]]
        except (IndexError, ValueError, KeyError):
            raise Exception("Несуществующая координата")

        return coords_attack

    def hit(self, gamepole, ship, coords_attack, hod):  # Реализация попадания по кораблю
        ship._is_move = False  # Запрещаем передвижения корабля после попадания
        ship[ship.ship_coords().index(coords_attack)] = 2  # Отмечаем палубу в которую попали
        gamepole.filling_gamepole()  # Перезаполняем поле новыми значениями
        if hod == 'player':  # Обозначаем клетку поподания на инфополе
            print("Есть попадание")
            self.gamepole_player_attack._gamepole[coords_attack[0]][coords_attack[1]] = 2
        if self.ship_destruction(ship):  # Проверка уничтожения корабля
            ship.destroyed = True  # Отмечаем что корабль уничтожен
            if hod == 'player':  # Если корабль уничтожен, отмечаем всю игрувую зону на инфополе
                print("Корабль уничтожен")
                for coords in filter(lambda x: x[0] < gamepole._size and x[1] < gamepole._size, ship.ship_borders()):
                    self.gamepole_player_attack._gamepole[coords[0]][coords[1]] = "*"
                for coords in ship.ship_coords():
                    self.gamepole_player_attack._gamepole[coords[0]][coords[1]] = 2
            if hod == "ii":  # Убираем всю зону корабля из доступных вариантов выстрела для ИИ
                self.coords = [coords for coords in self.coords if coords not in ship.ship_borders()]
            self.chek_game_over(gamepole)  # Проверка конца игры, если был уничтожен последний корабль

    def ship_destruction(self, ship):  # Проверка на уничтожение корабля
        return all([i == 2 for i in ship._cells])

    def chek_game_over(self, gamepole):  # Проверка конца игры
        if all(ship.destroyed for ship in gamepole.get_ships()):
            self.game_over = True

    def print_game_pole(self):
        print("Игровое поле игрока:")
        self.gamepole_player.show()
        print()
        print("Игровое поле ИИ(отоброжаются только поподания по кораблям):")
        self.gamepole_player_attack.show()
        print()

    def chek_hit(self, gamepole, coords_attack, hod):
        for ship in gamepole.get_ships():  # Проверка поподания в корабль
            # print(ship.ship_coords())
            if coords_attack in ship.ship_coords():
                self.hit(gamepole, ship, coords_attack, hod)
                return True
        return False

    def move_player(self):
        """ Функция для реализации хода игрока, запрашиваем координаты, если попали по кораблю повторяем ход"""
        print("hod player")
        while not self.game_over:
            self.gamepole_ii.move_ships()
            self.print_game_pole()
            self.gamepole_ii.show()
            coords_attack = input("Введите координаты для стрельбы пример('g3'):")
            try:
                coords_attack = self.chek_coords(coords_attack)
            except Exception:
                print("Неверно введены координаты")
                continue
            if self.chek_hit(self.gamepole_ii, coords_attack, hod='player'):
                self.coords = [coords for coords in self.coords if coords != coords_attack]
                time.sleep(2)
            else:
                print("Промах")
                break

    def move_ii(self):
        """Функция для реализации хода ИИ, берем рандомную координату и убираем ее из списка,
        что бы повторно не поподались,каждые 10 ходов, возврощаем координаты в общий список"""
        print("Hod ii")
        time.sleep(2)
        count = 0
        shooting_miss = []
        while not self.game_over:
            self.gamepole_player.move_ships()  # Перемещение кораблей
            if count == 10:  # Каждые 10 ходов, добовляем обратно кординаты промоха ИИ
                count = 0
                self.coords.extend(shooting_miss)
            coords_attack = choice(self.coords)
            self.coords = [i for i in self.coords if i != coords_attack]  #Убираем координату из доступных для выбора ИИ
            print(coords_attack)
            if self.chek_hit(self.gamepole_player, coords_attack, hod='ii'):
                print("Попадание")
                count += 1
                time.sleep(2)
            else:
                print("Промах, переход хода игроку")
                time.sleep(2)
                shooting_miss.append(coords_attack)
                count += 1
                break

    def game(self):
        hod = 0
        while not self.game_over:
            hod += 1
            if hod % 2 != 0:
                self.move_player()
            else:
                self.move_ii()

        print("Конец игры")
        if hod % 2 != 0:
            print("Победил игрок")
        else:
            print("Победил компьютер")


game = SeaBattle()
game.game()
