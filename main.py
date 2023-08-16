"""
Данная программа решает игры Одномастка Дурак и Д-Дурак, модификации с и без весов.
Она по начальному распределению карт и тому, какой игрок ходит первым определяет кто выиграет и с каким счетом,
а также оптимальные и "хитрые" ходы.
В конце файла есть пример использования класссов.
"""


class Position:
    """
    Вспомогательный класс, содержащий инофрмацию о результате игры, при заданном начальном распределении карт между игроками
    """

    def __init__(self, who_wins=-1, winning_score=0):
        """
        Конструктор класса
        :param who_wins: кто выиграет, может быть номером игрока - 0 или 1, и 2 - если ничья, по умолчанию -1, то есть неизвестно
        :param winning_score: с каким счетом будет выигрыш, по умолчанию 0
        """
        self.who_wins = who_wins  # -1 - неизвестно, 0 и 1 - номер выигравшего игрока, 2 - ничья
        self.winning_score = winning_score  # счет, с которым игрок выигрывает, то есть количество оставшихся у противника карт с учетом весов
        self.good_moves = []  # оптимальные ходы текущего игрока
        self.catching_the_take = -1  # "хитрый" ход: номер минимальной карту, которую противник должен принять, а побить которую — это ошибка, или -1 если не задано
        self.catching_the_transmission = -1  # "хитрый" ход: номер  максимальной карты, которую противник должен побить, а принять - ошибка, или -1 если не задано
        self.opponents_moves = {}  # оптимальный ответный ход ходящего вторым игрока для любого варианта хода текущего игрока


class OdnomastkaDurak:
    """
    Класс, решающий игру Одноматска Дурак
    """

    def __init__(self, cards, player):
        """
        Конструктор класса
        :param cards: текущие карты в формате массива содержащего 0 и 1 вектор (если на i-ой позиции стоит k, значит
        i-ая карта принадлежит игроку k)
        :param player: игрок, который начинает игру
        """
        self.moves_tree = {}  # уже просчитанные позиции
        self.pole = -1  # карта лежащая на столе
        self.cards = 0  # текущие карты в формате числа. То есть если i-ый бит в двоичном счислении равен k, то i-ая карта принадлежит игроку k
        self.max_size = len(cards)  # максимальное количество карт
        self.size = len(cards)  # текущее количество карт у обоих игроков
        self.reverse = 0  # является ли текущая позиция реверсной.
        self.now_player = player  # текущий игрок
        self.names_of_cards = [i for i in range(1, self.size + 1)]  # названия карт
        self.degrees = [2 ** i for i in range(self.size + 2)]  # степени двой для быстрого подсчета
        # переводим формат массива в формат числа
        for i in range(self.size):
            self.cards += cards[i] * self.degrees[i]
        self.cards += self.degrees[self.size]  # обозначает общее число карт
        if player == 1:
            self.change_player()  # теперь считаем, что первый ходит игрок 0
        self.build_moves_tree()

    def who_wins(self):
        """
        :return: номер выигрывающего игрока
        """
        return (self.moves_tree[self.cards].who_wins + self.reverse) % 2

    def winning_score(self):
        """
        :return: с каким счетом выиграет победивший игрок, то есть сколько у его противника останется карт
        """
        return self.moves_tree[self.cards].winning_score

    def good_moves(self):
        """
        :return: оптимальные ходы от текущей позиции. Индексы считаются с 1.
        """
        return [x + 1 for x in self.moves_tree[self.cards].good_moves]

    def catching_the_transmission(self):
        """
        :return: ловля пропускание от текущей позиции (None если не определено). Индекс считается с 1.
        """
        if self.moves_tree[self.cards].catching_the_transmission == -1:
            return None
        return self.moves_tree[self.cards].catching_the_transmission + 1

    def catching_the_take(self):
        """
        :return: ловля взятие от текущей позиции (None если не определено). Индекс считается с 1.
        """
        if self.moves_tree[self.cards].catching_the_take == -1:
            return None
        return self.moves_tree[self.cards].catching_the_take + 1

    def has_player_position(self, pos, player):
        """

        :param pos: позиция карты
        :param player: номер игрока
        :return: принажлежит ли карта pos игроку player
        """
        return self.degrees[pos] & self.cards == player * self.degrees[pos]

    def change_player(self):
        """
        Меняет текущего игрока. То есть меняет переменную self.reverse, а также в переменной self.cards все значащие
        биты меняются на противоположные, то есть если карта принадлежала игроку 1, то теперь принадлежит игроку 0
        и наоборот.
        """
        self.cards = (self.degrees[self.size] - 1) ^ self.cards
        self.reverse = (self.reverse + 1) % 2

    def remove(self, pos1, pos2):
        """
        Удаляет из self.cards использованные карты pos1 и pos2
        :param pos1: позиция карты
        :param pos2: позиция карты
        """
        if pos1 < pos2:
            pos1, pos2 = pos2, pos1
        self.cards = self.cards % self.degrees[pos1] + ((self.cards // self.degrees[pos1 + 1]) << pos1)
        self.cards = self.cards % self.degrees[pos2] + ((self.cards // self.degrees[pos2 + 1]) << pos2)
        self.size -= 2

    def add(self, pos1, player1, pos2, player2):
        """
        Добавляет карту pos1 игроку player1 в self.cards и карту pos2 игроку player2 в self.cards
        :param pos1: позиция карты
        :param player1: номер игрока
        :param pos2: позиция карты
        :param player2: номер игрока
        """
        if pos1 > pos2:
            pos1, pos2 = pos2, pos1
            player1, player2 = player2, player1
        self.cards = self.cards % self.degrees[pos1] + player1 * self.degrees[pos1] + (
                (self.cards // self.degrees[pos1]) << (pos1 + 1))
        self.cards = self.cards % self.degrees[pos2] + player2 * self.degrees[pos2] + (
                (self.cards // self.degrees[pos2]) << (pos2 + 1))
        self.size += 2

    def change_position(self, pos):
        """
        Поменять владельца карты pos.
        :param pos: позиция карты
        """
        if self.degrees[pos] & self.cards == 0:
            self.cards += self.degrees[pos]
        else:
            self.cards -= self.degrees[pos]

    def is_end(self):
        """
        :return: закончина ли игра. То есть правда ли, что все карты принадлежат одному игроку.
        """
        return self.cards == self.degrees[self.size] or self.cards == (self.degrees[self.size + 1] - 1)

    def move_by_computer(self):
        """
        Сделать ход компьютером
        :return: -1, если игра окончена, иначе номер карты - если компьютер решил принят карты.ю лежашую на чтоле, то
        он вернет ее номер, иначе это номер карты, которую от кладет на стол.
        """
        if self.is_end():  # окончена ли игра
            return -1
        if self.pole == -1:  # если на столе нет карты
            self.now_player = (self.now_player + 1) % 2
            if self.moves_tree[self.cards].catching_the_take != -1:  # проверяем определена ли ловля взятие
                self.pole = self.moves_tree[self.cards].catching_the_take
                return self.names_of_cards[self.moves_tree[self.cards].catching_the_take]
            elif self.moves_tree[
                self.cards].catching_the_transmission != -1:  # проверяем определена ли ловля пропускание
                self.pole = self.moves_tree[self.cards].catching_the_transmission
                return self.names_of_cards[self.moves_tree[self.cards].catching_the_transmission]
            else:  # если хитрых ходов нет, то просто берем какой-то оптимальный ход
                self.pole = self.moves_tree[self.cards].good_moves[0]
                return self.names_of_cards[self.moves_tree[self.cards].good_moves[0]]
        else:  # на столе есть карта
            t = self.pole
            self.pole = -1  # очищаем карту со стола
            res = self.moves_tree[self.cards].opponents_moves[t]  # оптимальный ход для этой карты на столе и позиции
            if res == t:  # Если оптимальный ход - принять карту
                self.now_player = (self.now_player + 1) % 2
                self.change_position(res)
                return self.names_of_cards[res]
            # если оптимально - побить карту
            self.remove(res, t)
            res = self.names_of_cards[res]
            # Удаляем использованные карты из self.names_of_cards, чтобы потом выдавать верные названия карт
            self.names_of_cards.remove(res)
            self.names_of_cards.remove(self.names_of_cards[t])
            # Мы только здесь вызываем эту функцию, так как только здесь возникает ситуации, где на столе нет карты, а ходить игроку 1
            self.change_player()
            return res

    def move_by_player(self, pos):  # код ошибки -1, pos=-1 значит принять карт
        """
        Делает ход игрока
        :param pos: номер карты или -1 если карту надо принять
        :return: 0, если все верно, -1 при ошибке
        """
        if self.is_end():  # Проверяем, если игра окончена
            return -1
        if pos == -1:  # если надо принять
            if self.pole == -1:  # на поле должна быть карта
                return -1
            else:
                self.now_player = (self.now_player + 1) % 2
                self.change_position(self.pole)
                self.pole = -1
        else:  # если надо побить или выложить карту на стол
            # ищем переданную карту в self.names_of_cards, то есть переводим номер карты в позицию карты в self.cards
            is_finded = False
            for i in range(self.size):
                if self.names_of_cards[i] == pos:
                    pos = i
                    is_finded = True
                    break
            if not is_finded:  # карта не найдена
                return -1
            if self.pole == -1:  # поле пустое
                if not self.has_player_position(pos, 0):  # карта не принадлежит игроку
                    return -1
                self.pole = pos
                self.now_player = (self.now_player + 1) % 2
            else:  # на поле есть карта
                if (not self.has_player_position(pos,
                                                 1)) or pos <= self.pole:  # карта не принадлежит игроку или ей нельзя побить лежащую на поле карту
                    return -1
                self.remove(self.pole, pos)
                self.names_of_cards.remove(self.names_of_cards[pos])
                self.names_of_cards.remove(self.names_of_cards[self.pole])
                self.pole = -1
                self.change_player()
        return 0

    def write_position(self, p, pole, is_catching):
        """
        Записывает в self.moves_tree[self.cards] позицию p
        :param p: позиция, которую надо записать в self.moves_tree[self.cards]
        :param pole: карта на столе
        :param is_catching: является ли хитрым ходом
        """
        self.moves_tree[self.cards].who_wins = p.who_wins
        self.moves_tree[self.cards].winning_score = p.winning_score
        self.moves_tree[self.cards].catching_the_transmission = -1
        self.moves_tree[self.cards].catching_the_take = -1
        self.moves_tree[self.cards].good_moves = [pole]
        if is_catching and self.moves_tree[self.cards].opponents_moves[pole] != pole:
            self.moves_tree[self.cards].catching_the_transmission = pole
        elif is_catching and self.moves_tree[self.cards].opponents_moves[pole] == pole:
            self.moves_tree[self.cards].catching_the_take = pole

    def build_moves_tree_opponent(self):
        """
        Построить дерево решений с для игрока 1 от текущей позиции, то есть на поле должна лежать карта
        """
        pole = self.pole
        # пробуем принять карту на поле
        self.change_position(pole)
        self.pole = -1
        self.build_moves_tree()
        take = self.cards  # распределение карт если принять
        who_wins_take = self.moves_tree[take].who_wins
        self.change_position(pole)
        # пробуем побить карту на поле
        protection = pole  # карта защиты
        while protection < self.size and self.has_player_position(protection, 0):
            protection += 1
        p = Position(who_wins_take,
                     self.moves_tree[take].winning_score)  # что получится после этого хода в лучшем случае
        self.moves_tree[self.cards].opponents_moves[pole] = pole  # изначачльно считаем, что выгоднее принять карту
        is_catching = False  # является ли карта на поле хитрым ходом
        if protection != self.size:  # нашлась карта, которая может побить карту на поле
            self.remove(pole, protection)  # удаляем ненужные карты
            self.change_player()  # так как по идее следующий должен ходить 1, а у нас все счиатется для 0
            transmission = self.cards
            self.build_moves_tree()
            # возвращаем карты как были
            self.change_player()
            self.add(pole, 0, protection, 1)
            # смотрим лучший результат, если побить или принять, кто в лучшем случае выиграет и с каким счетом.
            # Здесь игрок 1 выбирает самый выгодный для себя вариант.
            is_catching = True
            who_wins_transmission = (self.moves_tree[transmission].who_wins + 1) % 2
            if who_wins_take == 0 and who_wins_transmission == 1:
                p = Position(1, self.moves_tree[transmission].winning_score)
                self.moves_tree[self.cards].opponents_moves[pole] = protection
            elif who_wins_take == 1 and who_wins_transmission == 1:
                p.who_wins = 1
                if self.moves_tree[take].winning_score < self.moves_tree[transmission].winning_score:
                    p.winning_score = self.moves_tree[transmission].winning_score
                    self.moves_tree[self.cards].opponents_moves[pole] = protection
                elif self.moves_tree[take].winning_score == self.moves_tree[transmission].winning_score:
                    p.winning_score = self.moves_tree[transmission].winning_score
                    self.moves_tree[self.cards].opponents_moves[pole] = pole
                    is_catching = False
            elif who_wins_take == 0 and who_wins_transmission == 0:
                p.who_wins = 0
                if self.moves_tree[take].winning_score > self.moves_tree[transmission].winning_score:
                    p.winning_score = self.moves_tree[transmission].winning_score
                    self.moves_tree[self.cards].opponents_moves[pole] = protection
                elif self.moves_tree[take].winning_score == self.moves_tree[transmission].winning_score:
                    p.winning_score = self.moves_tree[transmission].winning_score
                    self.moves_tree[self.cards].opponents_moves[pole] = pole
                    is_catching = False
        # сравниваем текущий просчитанный результат и тот, который мы посчитали только что и правим позицию в
        # соответствии с новой информацией. Здесь самый выгодный для себя вариант выбирает игрок 0
        if self.moves_tree[self.cards].who_wins == -1 or (
                self.moves_tree[self.cards].who_wins == 1 and p.who_wins == 0):
            self.write_position(p, pole, is_catching)
        elif self.moves_tree[self.cards].who_wins == 0 and p.who_wins == 0:
            if self.moves_tree[self.cards].winning_score < p.winning_score:
                self.write_position(p, pole, is_catching)
            elif self.moves_tree[self.cards].winning_score == p.winning_score:
                self.moves_tree[self.cards].good_moves.append(pole)
                if is_catching and self.moves_tree[self.cards].opponents_moves[pole] == protection:
                    self.moves_tree[self.cards].catching_the_transmission = pole
                elif is_catching and self.moves_tree[self.cards].opponents_moves[pole] == pole and \
                        self.moves_tree[self.cards].catching_the_take == -1:
                    self.moves_tree[self.cards].catching_the_take = pole
        elif self.moves_tree[self.cards].who_wins == 1 and p.who_wins == 1:
            if self.moves_tree[self.cards].winning_score > p.winning_score:
                self.write_position(p, pole, is_catching)
            elif self.moves_tree[self.cards].winning_score == p.winning_score:
                self.moves_tree[self.cards].good_moves.append(pole)
                if is_catching and self.moves_tree[self.cards].opponents_moves[pole] == protection:
                    self.moves_tree[self.cards].catching_the_transmission = pole
                elif is_catching and self.moves_tree[self.cards].opponents_moves[pole] == pole and \
                        self.moves_tree[self.cards].catching_the_take == -1:
                    self.moves_tree[self.cards].catching_the_take = pole

    def build_moves_tree(self):
        """
        Построить дерево решений для игрока 0 от текущей позиции, то есть на столе нет карты
        """
        if not self.moves_tree.get(self.cards) is None:  # позиция уже посчитана
            return
        if self.cards == self.degrees[self.size]:  # все карты у игрока 0
            self.moves_tree[self.cards] = Position(1, self.size)
            return
        if self.cards == (self.degrees[self.size + 1] - 1):  # все карты у игрока 1
            self.moves_tree[self.cards] = Position(0, self.size)
            return
        self.moves_tree[self.cards] = Position()
        # пробуем положить на стол все карты, принадлежащие игроку 0 и проверяем, какая даст лучший результат
        for i in range(self.size):
            if self.has_player_position(i, 0):
                self.pole = i
                self.build_moves_tree_opponent()
        self.pole = -1

    def print(self):
        """
        Печатает номер карты на поле, если есть и текущее распределение карт
        """
        copy_cards = self.cards
        cards = [0] * self.size
        # перевести формат распределения карт из числа в формат массива
        i = 0
        while copy_cards != 0 and i < self.size:
            cards[i] = (copy_cards % 2 + self.reverse) % 2
            copy_cards //= 2
            i += 1
        # добавить пробелы туда, где карты были удалены, так как не влияли на игру
        ind = 0
        j = 0
        for i in range(self.size):
            kol = 0
            while self.names_of_cards[i] != j + 1:
                kol += 1
                j += 1
            j += 1
            if i == 0:
                cards = [' '] * kol + cards
            else:
                cards = cards[:ind] + [' '] * kol + cards[ind:]
            ind += kol + 1
        kol = 0
        while self.max_size >= j + 1:
            kol += 1
            j += 1
        cards = cards + [' '] * kol
        if self.pole == -1:
            print("Карты:", cards)
        else:
            print("Карты: ", cards, ". На поле: ", self.pole + 1, sep='')


class OdnomastkaD_Durak(OdnomastkaDurak):
    """
    Класс, решающий игру Одноматска Д-Дурак (то есть существует ничья, в отличии от Одномастки Дурак)
    """

    def who_wins(self):
        """
        :return: номер выигрывающего игрока или 2, если ничья
        """
        if self.winning_score() == 0:  # у обоих игроков в конце кончились карты
            return 2
        return (self.moves_tree[self.cards].who_wins + self.reverse) % 2


class OdnomastkaDurakWithWeights(OdnomastkaDurak):
    """
    Класс, решающий игру Одноматска Дурак с весами. Веса могут быть отрицательными. Если у игрока закончились карты,
    но сумма весов карт противника отрицательная, то он проиграл.
    """

    def __init__(self, cards, player, weights):
        """
        Конструктор класса
        :param cards: текущие карты в формате массива содержащего 0 и 1 вектор (если на i-ой позиции стоит k, значит
        i-ая карта принадлежит игроку k)
        :param player: игрок, который начинает игру
        :param weights: массив весов карт
        """
        self.moves_tree = {}  # уже просчитанные позиции
        self.pole = -1  # карта лежащая на столе
        self.cards = 0  # текущие карты в формате числа. То есть если i-ый бит в двоичном счислении равен k, то i-ая карта принадлежит игроку k
        self.max_size = len(cards)  # максимальное количество карт
        self.size = len(cards)  # текущее количество карт у обоих игроков
        self.reverse = 0  # является ли текущая позиция реверсной.
        self.now_player = player  # текущий игрок
        self.weights = tuple(weights)  # массив весов
        self.names_of_cards = [i for i in range(1, self.size + 1)]  # названия карт
        self.degrees = [2 ** i for i in range(self.size + 2)]  # степени двой для быстрого подсчета
        # переводим формат массива в формат числа
        for i in range(self.size):
            self.cards += cards[i] * (2 ** i)
        self.cards += self.degrees[self.size]  # обозначает общее число карт
        if player == 1:
            self.change_player()  # теперь считаем, что первый ходит игрок 0
        self.build_moves_tree()

    def who_wins(self):
        """
        :return: номер выигрывающего игрока
        """
        return (self.moves_tree[(self.cards, self.weights)].who_wins + self.reverse) % 2

    def winning_score(self):
        """
        :return: с каким счетом выиграет победивший игрок, то есть сколько у его противника останется карт с учетом весов
        """
        return self.moves_tree[(self.cards, self.weights)].winning_score

    def good_moves(self):
        """
        :return: оптимальные ходы от текущей позиции. Индексы считаются с 1.
        """
        return [x + 1 for x in self.moves_tree[(self.cards, self.weights)].good_moves]

    def catching_the_transmission(self):
        """
        :return: ловля пропускание от текущей позиции (None если не определено) Индекс считается с 1.
        """
        if self.moves_tree[(self.cards, self.weights)].catching_the_transmission == -1:
            return None
        return self.moves_tree[(self.cards, self.weights)].catching_the_transmission + 1

    def catching_the_take(self):
        """
        :return: ловля взятие от текущей позиции (None если не определено). Индекс считается с 1.
        """
        if self.moves_tree[(self.cards, self.weights)].catching_the_take == -1:
            return None
        return self.moves_tree[(self.cards, self.weights)].catching_the_take + 1

    def remove(self, pos1, pos2):
        """
        Удаляет из self.cards и self.weights использованные карты pos1 и pos2
        :param pos1: позиция карты
        :param pos2: позиция карты
        """
        if pos1 < pos2:
            pos1, pos2 = pos2, pos1
        self.cards = self.cards % self.degrees[pos1] + ((self.cards // self.degrees[pos1 + 1]) << pos1)
        self.cards = self.cards % self.degrees[pos2] + ((self.cards // self.degrees[pos2 + 1]) << pos2)
        self.weights = self.weights[:pos2] + self.weights[pos2 + 1:pos1] + self.weights[pos1 + 1:]
        self.size -= 2

    def add(self, pos1, player1, weight1, pos2, player2, weight2):
        """
        Добавляет карту pos1 игроку player1 в self.cards и ее вес weight1 в self.weights, а также карту pos2 игроку
        player2 в self.cards и ее вес weight2 в self.weights
        :param pos1: позиция карты
        :param player1: номер игрока
        :param weight1: вес карты
        :param pos2: позиция карты
        :param player2: номер игрока
        :param weight2: вес карты
        """
        if pos1 > pos2:
            pos1, pos2 = pos2, pos1
            player1, player2 = player2, player1
            weight1, weight2 = weight2, weight1
        self.cards = self.cards % self.degrees[pos1] + player1 * self.degrees[pos1] + (
                (self.cards // self.degrees[pos1]) << (pos1 + 1))
        self.cards = self.cards % self.degrees[pos2] + player2 * self.degrees[pos2] + (
                (self.cards // self.degrees[pos2]) << (pos2 + 1))
        self.weights = self.weights[:pos1] + (weight1,) + self.weights[pos1:]
        self.weights = self.weights[:pos2] + (weight2,) + self.weights[pos2:]
        self.size += 2

    def move_by_computer(self):
        """
        Сделать ход компьютером
        :return: -1, если игра окончена, иначе номер карты - если компьютер решил принят карты.ю лежашую на чтоле, то
        он вернет ее номер, иначе это номер карты, которую от кладет на стол.
        """
        if self.is_end():  # окончена ли игра
            return -1
        now = (self.cards, self.weights)
        if self.pole == -1:  # если на столе нет карты
            self.now_player = (self.now_player + 1) % 2
            if self.moves_tree[now].catching_the_take != -1:  # проверяем определена ли ловля взятие
                self.pole = self.moves_tree[now].catching_the_take
                return self.names_of_cards[self.moves_tree[now].catching_the_take]
            elif self.moves_tree[now].catching_the_transmission != -1:  # проверяем определена ли ловля пропускание
                self.pole = self.moves_tree[now].catching_the_transmission
                return self.names_of_cards[self.moves_tree[now].catching_the_transmission]
            else:  # если хитрых ходов нет, то просто берем какой-то оптимальный ход
                self.pole = self.moves_tree[now].good_moves[0]
                return self.names_of_cards[self.moves_tree[now].good_moves[0]]
        else:  # на столе есть карта
            t = self.pole
            self.pole = -1  # очищаем карту со стола
            res = self.moves_tree[now].opponents_moves[t]  # оптимальный ход для этой карты на столе и позиции
            if res == t:  # Если оптимальный ход - принять карту
                self.now_player = (self.now_player + 1) % 2
                self.change_position(res)
                return self.names_of_cards[res]
            # если оптимально - побить карту
            self.remove(res, t)
            res = self.names_of_cards[res]
            # Удаляем использованные карты из self.names_of_cards, чтобы потом выдавать верные названия карт
            self.names_of_cards.remove(res)
            self.names_of_cards.remove(self.names_of_cards[t])
            # Мы только здесь вызываем эту функцию, так как только здесь возникает ситуации, где на столе нет карты, а ходить игроку 1
            self.change_player()
            return res

    def write_position(self, p, pole, is_catching):
        """
        Записывает в self.moves_tree[self.cards] позицию p
        :param p: позиция, которую надо записать в self.moves_tree[self.cards]
        :param pole: карта на столе
        :param is_catching: является ли хитрым ходом
        """
        now = (self.cards, self.weights)
        self.moves_tree[now].who_wins = p.who_wins
        self.moves_tree[now].winning_score = p.winning_score
        self.moves_tree[now].catching_the_transmission = -1
        self.moves_tree[now].catching_the_take = -1
        self.moves_tree[now].good_moves = [pole]
        if is_catching and self.moves_tree[now].opponents_moves[pole] != pole:
            self.moves_tree[now].catching_the_transmission = pole
        elif is_catching and self.moves_tree[now].opponents_moves[pole] == pole:
            self.moves_tree[now].catching_the_take = pole

    def build_moves_tree_opponent(self):
        """
        Построить дерево решений с для игрока 1 от текущей позиции, то есть на поле должна лежать карта
        """
        now = (self.cards, self.weights)
        # пробуем принять карту на поле
        pole = self.pole
        self.change_position(pole)
        self.pole = -1
        self.build_moves_tree()
        take = (self.cards, self.weights)  # распределение карт и весов если принять
        self.change_position(pole)
        # пробуем побить карту на поле
        protection = pole  # карта защиты
        p = Position(self.moves_tree[take].who_wins,
                     self.moves_tree[take].winning_score)  # что получится после этого хода в лучшем случае
        self.moves_tree[now].opponents_moves[pole] = pole  # изначачльно считаем, что выгоднее принять карту
        is_catching = False  # является ли карта на поле хитрым ходом
        has_equal = False
        while protection + 1 < self.size:
            protection += 1
            if self.has_player_position(protection,
                                        1):  # нашлась карта, которая принадлежит игроку 1 и может побить карту на поле
                # Так как в этой версии игры есть веса, то мы пытаемся побить карту на полу всеми возможными картами
                w1, w2 = self.weights[pole], self.weights[protection]
                self.remove(pole, protection)  # удаляем ненужные карты
                self.change_player()  # так как по идее следующий должен ходить 1, а у нас все счиатется для 0
                transmission = (self.cards, self.weights)
                self.build_moves_tree()
                # возвращаем карты как были
                self.change_player()
                self.add(pole, 0, w1, protection, 1, w2)
                who_wins_transmission = (self.moves_tree[transmission].who_wins + 1) % 2
                # смотрим лучший результат, если побить или принять, кто в лучшем случае выиграет и с каким счетом.
                # Здесь игрок 1 выбирает самый выгодный для себя вариант.
                if self.moves_tree[take].who_wins == who_wins_transmission and \
                        self.moves_tree[take].winning_score == self.moves_tree[transmission].winning_score:
                    has_equal = True
                if p.who_wins == 0 and who_wins_transmission == 1:
                    p = Position(1, self.moves_tree[transmission].winning_score)
                    self.moves_tree[now].opponents_moves[pole] = protection
                elif p.who_wins == 1 and who_wins_transmission == 1 and \
                        abs(p.winning_score) < abs(self.moves_tree[transmission].winning_score):
                    p.winning_score = self.moves_tree[transmission].winning_score
                    self.moves_tree[now].opponents_moves[pole] = protection
                elif p.who_wins == 0 and who_wins_transmission == 0 and \
                        abs(p.winning_score) > abs(self.moves_tree[transmission].winning_score):
                    p.winning_score = self.moves_tree[transmission].winning_score
                    self.moves_tree[now].opponents_moves[pole] = protection
                if p.who_wins != self.moves_tree[take].who_wins or \
                        p.winning_score != self.moves_tree[take].winning_score or not has_equal:
                    is_catching = True
        # сравниваем текущий просчитанный результат и тот, который мы посчитали только что и правим позицию в
        # соответствии с новой информацией. Здесь самый выгодный для себя вариант выбирает игрок 0
        if self.moves_tree[now].who_wins == -1 or (
                self.moves_tree[now].who_wins == 1 and p.who_wins == 0):
            self.write_position(p, pole, is_catching)
        elif self.moves_tree[now].who_wins == 0 and p.who_wins == 0:
            if self.moves_tree[now].winning_score < p.winning_score:
                self.write_position(p, pole, is_catching)
            elif self.moves_tree[now].winning_score == p.winning_score:
                self.moves_tree[now].good_moves.append(pole)
                if is_catching and self.moves_tree[now].opponents_moves[pole] != pole:
                    self.moves_tree[now].catching_the_transmission = pole
                elif is_catching and self.moves_tree[now].opponents_moves[pole] == pole and \
                        self.moves_tree[now].catching_the_take == -1:
                    self.moves_tree[now].catching_the_take = pole
        elif self.moves_tree[now].who_wins == 1 and p.who_wins == 1:
            if self.moves_tree[now].winning_score > p.winning_score:
                self.write_position(p, pole, is_catching)
            elif self.moves_tree[now].winning_score == p.winning_score:
                self.moves_tree[now].good_moves.append(pole)
                if is_catching and self.moves_tree[now].opponents_moves[pole] != pole:
                    self.moves_tree[now].catching_the_transmission = pole
                elif is_catching and self.moves_tree[now].opponents_moves[pole] == pole and \
                        self.moves_tree[now].catching_the_take == -1:
                    self.moves_tree[now].catching_the_take = pole

    def build_moves_tree(self):
        """
        Построить дерево решений для игрока 0 от текущей позиции, то есть на столе нет карты
        """
        now = (self.cards, self.weights)
        if not self.moves_tree.get(now) is None:  # позиция уже посчитана
            return
        if self.cards == self.degrees[self.size]:  # все карты у игрока 0
            if sum(self.weights) < 0:
                self.moves_tree[now] = Position(0, sum(self.weights))
                return
            self.moves_tree[now] = Position(1, sum(self.weights))
            return
        if self.cards == (self.degrees[self.size + 1] - 1):  # все карты у игрока 1
            if sum(self.weights) < 0:
                self.moves_tree[now] = Position(1, sum(self.weights))
                return
            self.moves_tree[now] = Position(0, sum(self.weights))
            return
        # пробуем положить на стол все карты, принадлежащие игроку 0 и проверяем, какая даст лучший результат
        self.moves_tree[now] = Position()
        for i in range(self.size):
            if self.has_player_position(i, 0):
                self.pole = i
                self.build_moves_tree_opponent()
        self.pole = -1


class OdnomastkaD_DurakWithWeights(OdnomastkaDurakWithWeights):
    """
    Класс, решающий игру Одноматска Д-Дурак с весами (то есть существует ничья). Веса могут быть отрицательными. Если у
    игрока закончились карты, но сумма весов карт противника отрицательная, то он проиграл.
    """

    def who_wins(self):
        """
        :return: номер выигрывающего игрока или 2, если ничья
        """
        if self.winning_score() == 0:  # итоговый счет = 0
            return 2
        return (self.moves_tree[(self.cards, self.weights)].who_wins + self.reverse) % 2


def example():
    cards = [1, 0, 0, 1]
    weights = [-1, -1, -1, -1]
    first = 1
    game = OdnomastkaDurakWithWeights(cards, first, weights)
    print("Выиграет игрок:", game.who_wins(), "\nС счетом:", game.winning_score(),
          "\nОптимальные ходы:", game.good_moves(), "\nЛовля взятие:", game.catching_the_take(),
          "\nЛовля пропускание:", game.catching_the_transmission())
    while not game.is_end():
        t = game.move_by_computer()
        print("Ход:", t)
        game.print()


