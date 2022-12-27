import os
import sys
from random import randrange
from random import choice

# try:
#     color = sys.stdout.shell
# except AttributeError:
#     raise RuntimeError("Use IDLE")

#=============================
#*****************************
#CLASSES & FUNCTIONS
#*****************************
#=============================

class FieldPart(object):
    main = 'map'
    radar = 'radar'
    weight = 'weight'

#decided to introduce these cell names for better code readability:
class Cell(object):
    empty_cell = '□'
    ship_cell = '■'
    # miss_cell = '0'
    miss_cell = '•'
    damaged_ship = '!'
    destroyed_ship = 'X'

class Field(object):

    def __init__(self, size):
        self.size = size
        #self.map = [[Cell.empty_cell for _ in range(size)] for _ in range(size)]
        self.map =  [[Cell.empty_cell for _ in range(size)] for _ in range(size)]
        self.radar = [[Cell.empty_cell for _ in range(size)] for _ in range(size)]
        self.weight = [[1 for _ in range(size)] for _ in range(size)]

    def get_field_part(self, element):
        if element == FieldPart.main:
            return self.map
        if element == FieldPart.radar:
            return self.radar
        if element == FieldPart.weight:
            return self.weight

    def print_cell(self, elem):
        print(elem, end="")
        #destroyed
        # if(elem == 'X'):
        #     print(elem, end="")
        # #empty (also miss) - for the computer's board
        # elif(elem == '0'):
        #     print(elem, end="")
        # #shot
        # elif(elem == '!'):
        #     print(elem, end="")
        # #empty or occupied - for player's map/radar
        # else: print(elem, end="")

        
    
        

    def draw_field(self, element):
        size = self.size
        field = self.get_field_part(element) #fetches a link to a field part; most of the times it's either
                                            #a player's filed (with filled cells) or an opp's
        weights = self.get_max_weight_cells() #uncomment when defined

        #for debug purposes only (outputs weights):
        if element == FieldPart.weight:
            for x in range(self.size):
                for y in range(self.size):
                    if field[x][y] == 0:
                        print(str("" + ". " + ""), end='')
                    else:
                        print(str("" + str(field[x][y]) + " "), end='')
                print()
        #for actual gameplay (outputs map or radar):                
        else:
            for x in range(-1, self.size):
                for y in range(-1, self.size):
                    if x == -1 and y == -1:
                        print("  ", end="")
                        continue
                    if x == -1 and y >= 0:
                        print(y + 1, end=" ")
                        continue
                    if x >= 0 and y == -1:
                        print(Game.letters[x], end='')
                        continue
                    print(" ", end='')
                    elem = str(field[x][y])
                    self.print_cell(elem)
                print('')

    #for AI aiming algorithm: checking if a ship can be present at a given cell
    def check_ship_fits(self, ship, element):

        field = self.get_field_part(element)

        if ship.x + ship.height - 1 >= self.size or ship.x < 0 or \
                ship.y + ship.width - 1 >= self.size or ship.y < 0:
            return False

        x = ship.x
        y = ship.y
        width = ship.width
        height = ship.height

        for p_x in range(x, x + height):
            for p_y in range(y, y + width):
                if str(field[p_x][p_y]) == Cell.miss_cell:
                    return False

        for p_x in range(x - 1, x + height + 1):
            for p_y in range(y - 1, y + width + 1):
                if p_x < 0 or p_x >= len(field) or p_y < 0 or p_y >= len(field):
                    continue
                if str(field[p_x][p_y]) in (Cell.ship_cell, Cell.destroyed_ship):
                    return False
        return True


    def mark_destroyed_ship(self, ship, element):

        field = self.get_field_part(element)

        x, y = ship.x, ship.y
        width, height = ship.width, ship.height

        for p_x in range(x - 1, x + height + 1):
            for p_y in range(y - 1, y + width + 1):
                if p_x < 0 or p_x >= len(field) or p_y < 0 or p_y >= len(field):
                    continue
                field[p_x][p_y] = Cell.miss_cell

        for p_x in range(x, x + height):
            for p_y in range(y, y + width):
                field[p_x][p_y] = Cell.destroyed_ship


    def add_ship_to_field(self, ship, element):

        field = self.get_field_part(element)

        x, y = ship.x, ship.y
        width, height = ship.width, ship.height

        for p_x in range(x, x + height):
            for p_y in range(y, y + width):
                field[p_x][p_y] = ship #we assign the link to a ship to a cell, so that by addressing
                                        #this cell we could get
                                        #the ship's hp count

    def get_max_weight_cells(self):
        weights = {}
        max_weight = 0
        for x in range(self.size):
            for y in range(self.size):
                if self.weight[x][y] > max_weight:
                    max_weight = self.weight[x][y]
                weights.setdefault(self.weight[x][y], []).append((x, y))
        return weights[max_weight]

    

    def recalculate_weight_map(self, available_ships):
        self.weight = [[1 for _ in range(self.size)] for _ in range(self.size)]
        for x in range(self.size):
                for y in range(self.size):
                    if self.radar[x][y] == Cell.damaged_ship:

                        self.weight[x][y] = 0

                        if x - 1 >= 0:
                            if y - 1 >= 0:
                                self.weight[x - 1][y - 1] = 0
                            self.weight[x - 1][y] *= 50
                            if y + 1 < self.size:
                                self.weight[x - 1][y + 1] = 0

                        if y - 1 >= 0:
                            self.weight[x][y - 1] *= 50
                        if y + 1 < self.size:
                            self.weight[x][y + 1] *= 50

                        if x + 1 < self.size:
                            if y - 1 >= 0:
                                self.weight[x + 1][y - 1] = 0
                            self.weight[x + 1][y] *= 50
                            if y + 1 < self.size:
                                self.weight[x + 1][y + 1] = 0

        for ship_size in available_ships:
            ship = Ship(ship_size, 1, 1, 0)
            for x in range(self.size):
                for y in range(self.size):
                    if self.radar[x][y] in (Cell.destroyed_ship, Cell.damaged_ship, Cell.miss_cell) \
                            or self.weight[x][y] == 0:
                        self.weight[x][y] = 0
                        continue
                    for rotation in range(0, 4):
                        ship.set_position(x, y, rotation)
                        if self.check_ship_fits(ship, FieldPart.radar):
                            self.weight[x][y] += 1

                            

class Game(object):
    letters = tuple(chr(i) for i in range(65, 75))
    #print(letters)
    #ships_rules = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
    ships_rules = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
    field_size = len(letters)

    def __init__(self):

        self.players = []
        self.current_player = None
        self.next_player = None
        self.status = 'prepare'

    def start_game(self):
        self.current_player = self.players[0]
        self.next_player = self.players[1]

    def status_check(self):
        if self.status == 'prepare' and len(self.players) >= 2:
            self.status = 'in game'
            self.start_game()
            return True
        if self.status == 'in game' and len(self.next_player.ships) == 0:
            self.status = 'game over'
            return True
        
    def add_player(self, player):
        player.field = Field(Game.field_size)
        player.enemy_ships = list(Game.ships_rules)
        self.ships_setup(player)
        player.field.recalculate_weight_map(player.enemy_ships)
        self.players.append(player)

    def ships_setup(self, player):
        for ship_size in Game.ships_rules:
            retry_count = 60
            ship = Ship(ship_size, 0, 0, 0)
            while True:
                Game.clear_screen()
                if player.auto_ship_setup is not True:
                    player.field.draw_field(FieldPart.main)
                    player.message.append('Куда поставить {} корабль (формат ввода: [буква][цифра][H или\
                        V - hrizontal/vertical], например a1v): '.format(ship_size))
                    for _ in player.message:
                        print(_)
                else:
                    print('{}. Расставляем корабли...'.format(player.name))
                player.message.clear()
                x, y, r = player.get_input('ship_setup')
                if x + y + r == 0:
                    continue
                
                ship.set_position(x, y, r)                
                if player.field.check_ship_fits(ship, FieldPart.main):
                    player.field.add_ship_to_field(ship, FieldPart.main)
                    player.ships.append(ship)
                    break
                player.message.append('Неправильная позиция!')
                retry_count -= 1
                if retry_count < 0:
                    player.field.map = [[Cell.empty_cell for _ in range(Game.field_size)] for _ in\
                                        range(Game.field_size)]
                    player.ships = []
                    self.ships_setup(player)
                    return True

    def draw(self):
        if not self.current_player.is_ai:
            print('\n●●●● Ваша эскадра ●●●●\n')
            self.current_player.field.draw_field(FieldPart.main)
            print('\n●●●●●●● Радар ●●●●●●●\n')
            self.current_player.field.draw_field(FieldPart.radar) #regular mode
            #self.next_player.field.draw_field(FieldPart.main) #developpers cheat mode: shows enemy's ships
            #self.current_player.field.draw_field(FieldPart.weight) #for debugging purposes
            print('')

    def switch_players(self):
        self.current_player, self.next_player = self.next_player, self.current_player

    #can be called without an object of the Game class:
    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
    #doesn't work with IDLE though :( only with the terminal






class Player(object):
    #def __init__(self, name, is_ai, skill, auto_ship):
    def __init__(self, name, is_ai, auto_ship):
        self.name = name
        self.is_ai = is_ai
        self.auto_ship_setup = auto_ship
        #self.skill = skill
        self.message = []
        self.ships = []
        self.enemy_ships = []
        self.field = None
        self.hit_count = 0 #for combo announcements
        
    def get_input(self, input_type, inputStr = ''):

        if input_type == "ship_setup":

            if self.is_ai or self.auto_ship_setup:
                user_input = str(choice(Game.letters)) +\
                             str(randrange(0, self.field.size)) + choice(["H", "V"])
            else:
                user_input = input().upper().replace(" ", "")

            if len(user_input) < 3:
                return 0, 0, 0

            x, y, r = user_input[0], user_input[1:-1], user_input[-1]

            if x not in Game.letters or not y.isdigit() or int(y) not in range(1, Game.field_size + 1) or \
                    r not in ("H", "V"):
                self.message.append('Приказ непонятен, ошибка формата данных')
                return 0, 0, 0

            return Game.letters.index(x), int(y) - 1, 0 if r == 'H' else 1

        if(input_type == 'action'):
            if (): return 0
        
        
        
        if input_type == "shot":

            if self.is_ai:
                """
                if self.is_ai:
                if self.skill == 1:
                    x, y = choice(self.field.get_max_weight_cells())
                if self.skill == 0:
                    x, y = randrange(0, self.field.size), randrange(0, self.field.size)
                """
                x, y = choice(self.field.get_max_weight_cells())
           
            else:
                if(inputStr == ''): user_input = input().upper().replace(" ", "")
                else: user_input = inputStr.upper().replace(" ", "")


                x, y = user_input[0].upper(), user_input[1:]
                if x not in Game.letters or not y.isdigit() or int(y) not in range(1, Game.field_size + 1):
                    self.message.append('Приказ непонятен, ошибка формата данных')
                    return 500, 0
                x = Game.letters.index(x)
                y = int(y) - 1
            return x, y
        


    def make_shot(self, target_player, inputStr = ''):

        sx, sy = self.get_input('shot', inputStr)

        if sx + sy == 500 or self.field.radar[sx][sy] != Cell.empty_cell:
            return 'retry'
        shot_res = target_player.receive_shot((sx, sy))

        if shot_res == 'miss':
            self.field.radar[sx][sy] = Cell.miss_cell

        if shot_res == 'get':
            self.field.radar[sx][sy] = Cell.damaged_ship

        if type(shot_res) == Ship:
            destroyed_ship = shot_res
            self.field.mark_destroyed_ship(destroyed_ship, FieldPart.radar)
            self.enemy_ships.remove(destroyed_ship.size)
            shot_res = 'kill'
        self.field.recalculate_weight_map(self.enemy_ships)

        return shot_res

    
    def receive_shot(self, shot):

        sx, sy = shot

        if type(self.field.map[sx][sy]) == Ship:
            ship = self.field.map[sx][sy]
            ship.hp -= 1

            if ship.hp <= 0:
                self.field.mark_destroyed_ship(ship, FieldPart.main)
                self.ships.remove(ship)
                return ship

            self.field.map[sx][sy] = Cell.damaged_ship
            return 'get'

        else:
            self.field.map[sx][sy] = Cell.miss_cell
            return 'miss'

    def get_hit_counter(self):
        return self.hit_count    

    def set_hit_counter(self, hits):
        self.hit_count = hits

    def announce_combo(self, hit_count):
        #print(str(hit_count), "COMMENT")
        if(shot_result != 'retry'):
            if(hit_count == 2):
                print('Высокая меткость! ', end="")
            elif(hit_count == 3):
                print('Превосходно! ', end="")
            elif(hit_count >= 4):
                print('РЕЗНЯ!!! ', end="")
        


class Ship:
    def __init__(self, size, x, y, rotation):
        self.size = size
        self.hp = size
        self.x = x
        self.y = y
        self.rotation = rotation
        self.set_rotation(rotation)

    def __str__(self):
        return Cell.ship_cell

    def set_position(self, x, y, r):
        self.x = x
        self.y = y
        self.set_rotation(r)

    def set_rotation(self, r):
        self.rotation = r

        if self.rotation == 0:
            self.width = self.size
            self.height = 1
        elif self.rotation == 1:
            self.width = 1
            self.height = self.size
        elif self.rotation == 2:
            self.y = self.y - self.size + 1
            self.width = self.size
            self.height = 1
        elif self.rotation == 3:
            self.x = self.x - self.size + 1
            self.width = 1
            self.height = self.size
    

#=============================
#*****************************
#MAIN PART
#*****************************
#=============================

#DEBUGGING
"""
print_caption()
print('')
str_matrix = draw_field(10)
length = len(str_matrix)
print(str_matrix)
print(length)
print_field(str_matrix, 10)

field1 = Field(10)
#field1.draw_field('map')
#field1.draw_field('radar')

battleship = Ship(4, 5, 5, 3)
field1.add_ship_to_field(battleship, 'map')
field1.draw_field('map')
"""

if __name__ == '__main__':

    #creating a list of two players and initializing their
    #basic props
    players = []
    print('Как вас зовут, адмирал?', '\nИмя: ', end='')
    first_name = input()
    print('Фамилия: ', end='')
    last_name = input()
    username = first_name + ' ' + last_name
    print(f'Намечается славная заварушка, сэр {last_name}!')
    players.append(Player(name=username, is_ai=False, auto_ship=True))
    players.append(Player(name='IQ180', is_ai=True, auto_ship=True))

    #creating the game itself, then running the infinite cycle
    game = Game()

    print('Желаете ходить первым?'.format(username))
    print('ДА или НЕТ\n')
    # print(' или ')
    # print('НЕТ\n')
    print('Ваш ввод: ')
    wants_to_play_first = input()
    wants_to_play_first.lower()
    while (wants_to_play_first == False or (wants_to_play_first != 'да'\
                                                      and wants_to_play_first != 'нет')):
        print('Приказ не ясен, повторите ответ')
        wants_to_play_first = input()
    print('Принято!')

    print('Хотите расставить свои корабли вручную?'.format(username))
    print('ДА или НЕТ\n')
    # print(' или ')
    # print('НЕТ\n')
    print('Ваш ввод: ')
    wishes_manual_setup = input()
    wishes_manual_setup.lower()
    while (wishes_manual_setup == False or (wishes_manual_setup != 'да'\
                                                      and wishes_manual_setup != 'нет')):
        print('Приказ не ясен, повторите ответ')
        wishes_manual_setup = input()
    print('Принято!')

    if(wishes_manual_setup == 'да'):
        players[0].auto_ship_setup = False

    
    #hit_count = 0
    
    while True:
        #checking game status every turn and acting based on it
        game.status_check() #THIS FUNCTION IS RESPONSIBLE FOR STARTING THE GAME => ASSIGNING
                            #CURRENT AND NEXT PLAYERS

        if game.status == 'prepare':
            if(wants_to_play_first.lower() == 'да'):
                game.add_player(players.pop(0))
                #game.add_player(players.pop(-1))
                #if the player chooses to go second, we could pop(-1)?
            else:
                game.add_player(players.pop(-1))
                
            if(len(game.players) == 2):     
                print('\n======= К БОЮ! =======\n')

        if game.status == 'in game':
            #in the main part we clear the screen and add a message for the current player
            #then draw the game
            Game.clear_screen()
            Game.clear_screen()


            #==========РАБОТА С СООБЩЕНИЯМИ==================
            # набрасываем говно
            # на вентилятор, в смысле сообщения в массив
            #================================================



            game.current_player.message.append("\nЖдём приказа (формат ввода:"+
                                               "[буква][цифра], например a1): ")
            game.draw()
            if(game.current_player.hit_count > 0):
                game.current_player.announce_combo(game.current_player.hit_count)
            for line in game.current_player.message:
                print(line)
            #cleaning up the current player's messages
            #next turn he'll get new ones
            game.current_player.message.clear()





            #==============ОТКРЫТЬ МЕНЮ ОРУЖИЯ
            #                      ИЛИ
            #==============СДЕЛАТЬ ВЫСТРЕЛ


            #players_action = input()

            #if(players_action == 0)
            #   на следующем витке цикла отрисовать арсенал

            #   ставим current_player.draw_arsenal = true; и скипаем этот виток цикла

            #   функция draw будет проверять draw_arsenal;
            #   если true, то кроме функции отрисовки полей draw_field будет вызываться
            #   ещё и какая-нибудь draw_menu
            #elif(players_action = )

            
            # waiting for the result of the current player's shot:




            shot_result = game.current_player.make_shot(game.next_player)


            if shot_result == 'miss':
                game.next_player.message.append('На этот раз '+
                                                '{} промахнулся! '.format(game.current_player.name))
                game.current_player.hit_count = 0
                game.next_player.message.append('Ваш ход, {}!'.format(game.next_player.name))
                game.switch_players()
                continue
            elif shot_result == 'retry':
                game.current_player.message.append('Попробуйте еще раз!')
                continue
            else:
                game.current_player.hit_count += 1
                if shot_result == 'get':
                    game.current_player.message.append('Отличный выстрел,'+
                                                       'продолжайте, сэр {}!'.format(game.current_player.name))
                    if(game.next_player.is_ai == False):
                        game.next_player.message.append('Наш корабль попал '+
                                                        'под обстрел,'+
                                                        'сэр {}!'.format(game.next_player.name))
                    continue
                elif shot_result == 'kill':
                    game.current_player.message.append('Корабль противника уничтожен! '+
                                                       'Продолжайте,'+
                                                       'сэр {}!'.format(game.current_player.name))
                    if(game.next_player.is_ai == False):
                        game.next_player.message.append('Плохие новости, сэр {},'.format(game.next_player.name)+
                                                        'наш корабль был уничтожен.')
                    continue

        if game.status == 'game over':
            Game.clear_screen()
            print(f'\n●●●● {game.current_player.name} ●●●●\n')
            game.current_player.field.draw_field(FieldPart.main)
            print(f'\n●●●● {game.next_player.name} ●●●●\n')
            game.next_player.field.draw_field(FieldPart.main)
            print('Это был последний корабль адмирала {}.'.format(game.next_player.name))
            print('{} выиграл матч! С победой!'.format(game.current_player.name))
            break

    print('Спасибо за игру!')
    input('')



