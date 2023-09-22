import logging
import json
import random

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Game:
    """
        Initialize the game.

        Args:
            login (str): The player's login name.
        """

    def __init__(self, login):
        self.heroes = []  # List to store hero objects
        self.round = 0  # Current round number
        self.current_turn = 0  # Index of the current hero's turn
        self.player_login = login  # Player's login
        self.fire_cells = []  # Coordinates of cells with fire
        self.labyrinth = Labyrinth()  # Initialize the labyrinth

    def add_heroes(self):
        """
        Add heroes to the game.

        Asks the user for the number of heroes and their names, then adds them to the game.
        """
        while True:
            try:
                num_heroes = int(input('Введіть число героїв: \n'))
                if 0 < num_heroes <= 5:
                    for i in range(num_heroes):
                        while True:
                            name = input(f"Введіть ім'я героя {i + 1}: ")
                            if name and name not in [hero.name for hero in self.heroes]:
                                self.heroes.append(Hero(name))
                                break
                            else:
                                logger.info('Введіть ім`я для героя. Однакові імена не допустимі')
                    break
                else:
                    raise MaxHeroesError('Максимальна кількість героїв - 5')
            except ValueError:
                print("Введіть ціле число.")
            except MaxHeroesError as e:
                print(e)

    def check_hero_health(self, current_hero):
        """
                Check the health of a hero.

                Args:
                    current_hero (Hero): The hero to check.

                Returns:
                    bool: True if the hero is alive, False if the hero has no remaining lives.
                """
        if current_hero.health <= 0:
            logger.info(f'На жаль  герой {current_hero.name} отримав не сумістні з життям поранення та загинув')
            if current_hero.has_key:
                logger.info(f'З {current_hero.name} випав ключ за координатами {current_hero.position}')
                self.labyrinth.key = True
                self.labyrinth.key_coord = current_hero.position
            return False
        return True

    def check_near_hero(self, hero):
        """
                Check if there are other heroes or items near the given hero's position.

                Args:
                    hero (Hero): The hero to check for nearby entities.

                Returns:
                    bool: True if there are actions available, False if not.
                """
        logger.info('Перевірка чи знаходиться герой з кимось або чимось в клітині')
        near_heroes = []
        action = []

        for near_hero in self.heroes:
            if hero.position == near_hero.position and hero.name != near_hero.name and near_hero.health > 0:
                logger.info(f'Герой {hero.name} знаходиться в одній клітинці з іншим героєм - {near_hero.name}')
                near_heroes.append(near_hero)
                action.append(f'Атакувати мечем {near_hero.name}')
        if not near_heroes:
            logger.info('Поряд немає героїв')

        if self.labyrinth.key and hero.position == self.labyrinth.key_coord:
            logger.info(f'Герой {hero.name} знаходиться в одній клітинці з ключем та може його підібрати')
            action.append('Підібрати ключ')

        elif hero.position in self.labyrinth.hearts_coords:
            logger.info(f'Герой {hero.name} знаходиться в одній клітинці з сердцем та може поповнити свої життя')
            action.append('Поповнити життя')

        else:
            logger.info('Поряд немає предметів')
        return action, near_heroes

    def check_save(self):
        """
                Check if a saved game exists for the current login.

                Returns:
                    bool: True if a saved game exists, False otherwise.
                """
        logger.info('Перевіряємо наявність збереженої гри.')
        try:
            with open("game_save.json", "r") as save_file:
                game_data = json.load(save_file)
                if self.player_login in game_data:
                    while True:
                        load_save = input('У Вас є збережена гра, бажаєте її завантажити? (Відповідь: yes/no): ')
                        load_save = load_save.strip().lower()

                        if load_save == 'yes':
                            logger.info('Гра завантажується')
                            return True
                        elif load_save == 'no':
                            logger.info('Гравець не захотів заванатажувати гру тому вона була видалена')
                            del game_data[self.player_login]
                            with open("game_save.json", "w") as updated_save_file:
                                json.dump(game_data, updated_save_file, indent=4, sort_keys=True)
                            return False
                        else:
                            print('Неправильний ввід. Будь ласка, введіть "yes" або "no".')
                else:
                    logger.info('Для цього логіна немає збереженої гри.')
                    return False
        except FileNotFoundError:
            logging.warning('Файл game_save.json не знайдено.')
            return False
        except json.decoder.JSONDecodeError:
            logging.warning('Файл game_save.json пустий або містить некоректні дані.')
            return False

    def hero_move(self, current_hero):
        """
                Allow the hero to move in different directions.

                Args:
                    current_hero (Hero): The hero to move.

                Returns:
                    bool: True if the hero successfully moved, False otherwise.
                """
        new_x, new_y = 0, 0
        while True:
            x, y = current_hero.position
            action = ['Вгору', 'Вниз', 'Вліво', 'Вправо']
            print('Виберіть напрямок: ')
            for i, act in enumerate(action):
                print(f'{i + 1}. {act}')
            choice = input('Введіть номер напрямку або "NO" для відмови: ')
            choice = choice.strip().upper()

            if choice == 'NO':
                logger.info(f'Герой {current_hero.name} не вибрав жодного напрямку')
                return False
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(action):
                    selected_action = action[choice_num - 1]
                    if selected_action == "Вгору":
                        new_x, new_y = x - 1, y
                    elif selected_action == "Вниз":
                        new_x, new_y = x + 1, y
                    elif selected_action == "Вліво":
                        new_x, new_y = x, y - 1
                    elif selected_action == "Вправо":
                        new_x, new_y = x, y + 1
                    else:
                        print("Некорректний напрямок. Спробуйте ще раз.")
                        continue
                    break
            except ValueError:
                print('Неправильний ввід. Будь ласка, введіть номер дії або "NO".')
        if 0 <= x < 4 and 0 <= y < 8 and self.labyrinth.grid[new_x][new_y]:
            if self.labyrinth.grid[new_x][new_y] == 1:
                if (new_x, new_y) == current_hero.prev_position:
                    while True:
                        logger.info(f'Герой {current_hero.name} злякався та хоче повернутись назад')
                        action = input(
                            'Ви впевнені? Ваш герой помре(Відповідь: yes/no').strip().lower()
                        if action == 'yes':
                            current_hero.health = 0
                            return True
                        elif action == 'no':
                            return False
                current_hero.prev_position = current_hero.position
            current_hero.position = (new_x, new_y)
            logger.info(f'Герой {current_hero.name} перемістився у клітину {current_hero.position}')
            if current_hero.position in self.fire_cells:
                logger.info(
                    f'Герой {current_hero.name} потрапив у клітину яка зайнялась полум`ям та втратив одне життя')
                current_hero.health -= 1
            if current_hero.position == self.labyrinth.golem_coord:
                logger.info(f'Герой {current_hero.name} зустрів Голема')
                if current_hero.has_key:
                    logger.info(f'Герой {current_hero.name} відав ключ Голему и тот його пропустив далі')
                    logger.info(f'Герой {current_hero.name} отримав перемогу в цій грі')
                    exit()
                else:
                    logger.info(f'У Героя  {current_hero.name} не виявилося ключа для Голема, тому він його атакував.')
                    current_hero.health = 0

        else:
            logger.info(f'Герой {current_hero.name} врізався у стіну та втрачає одне життя')
            current_hero.health -= 1
        return True

    def load_game(self):
        """
                Load a saved game from a JSON file.

                This method loads a saved game state, including hero details, current round, and labyrinth state,
                 from a JSON file.
                """
        try:
            with open("game_save.json", "r") as save_file:
                all_game_saves = json.load(save_file)
                if self.player_login in all_game_saves:
                    game_data = all_game_saves[self.player_login]
                    self.round = game_data["round"]
                    self.current_turn = game_data["current_turn"]
                    self.fire_cells = game_data["fire_cells"]
                    self.heroes = [Hero.from_dict(data) for data in game_data["heroes"]]
                    self.labyrinth = Labyrinth.from_dict(game_data["labyrinth"])
                else:
                    logging.warning('Для цього логіна немає збереженої гри.')
        except FileNotFoundError:
            logging.warning('Файл game_save.json не знайдено.')
        except json.decoder.JSONDecodeError:
            logging.warning('Файл game_save.json пустий або містить некоректні дані.')

    def play(self):
        """
                Start and manage the game loop.

                This method handles the game's rounds, hero turns, and game-over conditions.
                """
        if not self.current_turn:
            self.start_new_round()
        while True:
            if self.heroes:
                current_hero = self.heroes[self.current_turn]
                logger.info(f"Зараз ходить герой з ім'ям {current_hero.name}")
                logger.info(f'Кількість здоров`я героя: {current_hero.health}')
                if self.check_hero_health(current_hero):
                    while True:
                        action, near_heroes = self.check_near_hero(current_hero)
                        if current_hero.hero_action(action, near_heroes):
                            if self.check_hero_health(current_hero):
                                self.current_turn = (self.current_turn + 1) % len(self.heroes)
                                if not self.current_turn and self.heroes:
                                    self.start_new_round()
                            else:
                                self.heroes.remove(current_hero)
                            break
                        else:
                            logger.info('Не можливо пропустити хід')
                else:
                    self.heroes.remove(current_hero)
                    logger.info('Ход переходить до наступного гравця')

            else:
                logger.info('Усі герої померли, ніхто не отримав перемоги. Гра завершена')
                exit()

    def save_game(self):
        """
                Save the current game state to a JSON file.

                This method saves the game's data, including hero details, current round, and labyrinth state, to a JSON
                 file.
                """
        game_data = {
            "heroes": [hero.to_dict() for hero in self.heroes],
            "round": self.round,
            "current_turn": self.current_turn,
            "labyrinth": self.labyrinth.to_dict(),
            "fire_cells": self.fire_cells
        }

        try:
            with open("game_save.json", "r") as save_file:
                all_game_saves = json.load(save_file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            all_game_saves = {}

        all_game_saves[self.player_login] = game_data

        with open("game_save.json", "w") as save_file:
            json.dump(all_game_saves, save_file, indent=4, sort_keys=True)

    def start_new_round(self):
        """
        Start a new round of the game.

        This method increments the round counter and updates the labyrinth, fire cells,
         and golem position for the new round.
        """
        self.round += 1
        self.labyrinth.generate_fire()
        self.fire_cells = self.labyrinth.fire_coords
        logger.info(f"Почався раунд {self.round}. Клітини з вогнем: {', '.join(str(i) for i in self.fire_cells)}")
        for hero in self.heroes:
            logger.info(f'{hero.name} має {hero.health} здоров`я')
            if hero.has_key:
                logger.info(f'{hero.name} має ключ')


class MaxHeroesError(Exception):
    """Custom exception for exceeding the maximum number of heroes"""
    pass


class Labyrinth:
    def __init__(self):
        """
        Initialize the Labyrinth with its properties.

        The Labyrinth consists of a grid, key, heart coordinates, and golem coordinate.
        """
        self.size_x = 4
        self.size_y = 8
        self.grid = [
            [0, 0, 0, 0, 2, 1, 1, 1],
            [0, 0, 2, 0, 0, 1, 0, 0],
            [0, 1, 1, 1, 0, 1, 2, 0],
            [1, 1, 0, 1, 1, 1, 0, 0]
        ]
        self.key = True
        self.key_coord = (1, 2)  # Coordinates of the key
        self.hearts_coords = [(0, 4), (2, 6)]  # Coordinates of the hearts
        self.golem_coord = (0, 7)
        self.fire_coords = []

    def generate_fire(self):
        """
        Generate the coordinates of fire cells.

        This method randomly selects four valid cells to set on fire within the Labyrinth.
        """
        self.fire_coords = []
        while len(self.fire_coords) != 4:
            x, y = random.randint(0, self.size_x - 1), random.randint(0, self.size_y - 1)
            if self.grid[x][y] == 1 and (x, y) not in self.fire_coords:
                self.fire_coords.append((x, y))

    def is_valid_move(self, x, y):
        """
        Check if a cell is a valid move.

        Args:
            x (int): X-coordinate of the cell.
            y (int): Y-coordinate of the cell.

        Returns:
            bool: True if the cell is a valid move, False otherwise.
        """
        if 0 <= x < self.size_x and 0 <= y < self.size_y:
            return self.grid[y][x] in [1, 2]
        return False

    def to_dict(self):
        """
        Convert Labyrinth data to a dictionary for saving.

        Returns:
            dict: A dictionary containing Labyrinth data.
        """
        return {
            "grid": self.grid,
            "fire_coords": self.fire_coords,
            "key_coord": self.key_coord,
            "golem_coord": self.golem_coord,
            "key": self.key
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create a Labyrinth object from a dictionary.

        Args:
            data (dict): A dictionary containing Labyrinth data.

        Returns:
            Labyrinth: A Labyrinth object created from the dictionary.
        """
        labyrinth = cls()
        labyrinth.grid = data["grid"]
        labyrinth.fire_coords = data["fire_coords"]
        labyrinth.key_coord = data["key_coord"]
        labyrinth.golem_coord = data["golem_coord"],
        labyrinth.key = data["key"]
        return labyrinth


class Hero:
    def __init__(self, name):
        """
        Initialize a Hero with its properties.

        Args:
            name (str): The name of the Hero.
        """
        self.name = name
        self.health = 5
        self.has_key = False
        self.position = (3, 0)
        self.prev_position = (0, 0)
        self.count_heal = 3

    def attack(self, damage_hero):
        """
        Perform an attack between two heroes.

        Args:
            damage_hero (Hero): The hero receiving the damage.

        Logs the attack action and decreases the health of the damage_hero.
        """

        logger.info(f'Герой {self.name} дістав меч та наніс удар {damage_hero.name}.'
                    f' В результаті чого {damage_hero.name} втратив одне життя')
        damage_hero.health -= 1

    def hero_action(self, action, near_heroes):

        static_action = ['Перемістити героя', 'Самолікування', 'Зберегти гру', 'Вихід з гри']
        action += static_action

        while True:
            print(f'Виберіть дію для героя {self.name}:')
            for i, act in enumerate(action):
                print(f"{i + 1}. {act}")
            try:
                choice_num = int(input('Введіть номер дії: '))
                if 1 <= choice_num <= len(action):
                    selected_action = action[choice_num - 1]

                    if 'Атакувати мечем' in selected_action:
                        logger.info(
                            f'Герой {self.name} зібрався атакувати {near_heroes[choice_num - 1].name}')
                        self.attack(near_heroes[choice_num - 1])
                        return True
                    elif selected_action == 'Підібрати ключ':
                        logger.info(f'Герой {self.name} підібрав ключ')
                        self.has_key = True
                        game.labyrinth.key = False
                        return True
                    elif selected_action == 'Поповнити життя':
                        if self.health == 5:
                            logger.info(f'Герой {self.name} має повне життя')
                        else:
                            logger.info(f'Герой {self.name} поповнив життя')
                            self.health = 5
                            return True
                    elif selected_action == 'Перемістити героя':
                        if self.hero_move():
                            return True
                        else:
                            return False
                    elif selected_action == 'Самолікування':
                        if self.self_heal():
                            return True
                        else:
                            return False

                    elif selected_action == 'Зберегти гру':
                        game.save_game()
                        logger.info('Гра успішно збережена')
                        return False

                    elif selected_action == 'Вихід з гри':
                        logger.info('Ви завершили гру')
                        exit()
                else:
                    print('Неправильний ввід. Будь ласка, введіть номер дії або "NO".')
                    continue

            except ValueError:
                print('Неправильний ввід. Будь ласка, введіть номер дії або "NO".')

    def hero_move(self):
        """
                Allow the hero to move in different directions.

                Returns:
                    bool: True if the hero successfully moved, False otherwise.
                """
        new_x, new_y = 0, 0
        while True:
            x, y = self.position
            action = ['Вгору', 'Вниз', 'Вліво', 'Вправо']
            print('Виберіть напрямок: ')
            for i, act in enumerate(action):
                print(f'{i + 1}. {act}')
            choice = input('Введіть номер напрямку або "NO" для відмови: ')
            choice = choice.strip().upper()

            if choice == 'NO':
                logger.info(f'Герой {self.name} не вибрав жодного напрямку')
                return False
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(action):
                    selected_action = action[choice_num - 1]
                    if selected_action == "Вгору":
                        new_x, new_y = x - 1, y
                    elif selected_action == "Вниз":
                        new_x, new_y = x + 1, y
                    elif selected_action == "Вліво":
                        new_x, new_y = x, y - 1
                    elif selected_action == "Вправо":
                        new_x, new_y = x, y + 1
                    else:
                        print("Некорректний напрямок. Спробуйте ще раз.")
                        continue
                    break
            except ValueError:
                print('Неправильний ввід. Будь ласка, введіть номер дії або "NO".')
        if 0 <= x < 4 and 0 <= y < 8 and game.labyrinth.grid[new_x][new_y]:
            if game.labyrinth.grid[new_x][new_y] == 1:
                if (new_x, new_y) == self.prev_position:
                    while True:
                        logger.info(f'Герой {self.name} злякався та хоче повернутись назад')
                        action = input(
                            'Ви впевнені? Ваш герой помре(Відповідь: yes/no').strip().lower()
                        if action == 'yes':
                            self.health = 0
                            return True
                        elif action == 'no':
                            return False
                self.prev_position = self.position
            self.position = (new_x, new_y)
            logger.info(f'Герой {self.name} перемістився у клітину {self.position}')
            game.check_near_hero(self)
            if self.position in game.fire_cells:
                logger.info(
                    f'Герой {self.name} потрапив у клітину яка зайнялась полум`ям та втратив одне життя')
                self.health -= 1
            if self.position == game.labyrinth.golem_coord:
                logger.info(f'Герой {self.name} зустрів Голема')
                if self.has_key:
                    logger.info(f'Герой {self.name} відав ключ Голему и тот його пропустив далі')
                    logger.info(f'Герой {self.name} отримав перемогу в цій грі')
                    exit()
                else:
                    logger.info(f'У Героя  {self.name} не виявилося ключа для Голема, тому він його атакував.')
                    self.health = 0

        else:
            logger.info(f'Герой {self.name} врізався у стіну та втрачає одне життя')
            self.health -= 1
        return True

    def self_heal(self):
        """
                Allow the hero to heal themselves.


                Returns:
                    bool: True if the hero successfully healed, False otherwise.
                """
        logger.info(f'Герой {self.name} дістав аптечку, щоб поповнити здоров`є')
        if self.count_heal > 0:
            if self.health != 5:
                self.health += 1
                self.count_heal -= 1
                logger.info(f'Герой {self.name} вилікувався, зараз він має: {self.health} здоров`я')
                return True
            else:
                logger.info(f'Герой {self.name} має повне здоров`я')
                return False
        else:
            logger.info('Аптечка виявилась порожньою, герой не має більше змоги лікуватись')
            return False

    def to_dict(self):
        """
        Convert Hero data to a dictionary for saving.

        Returns:
            dict: A dictionary containing Hero data.
        """
        return {
            "name": self.name,
            "health": self.health,
            "position": self.position,
            "has_key": self.has_key,
            "prev_position": self.prev_position,
            "count_heal": self.count_heal
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create a Hero object from a dictionary.

        Args:
            data (dict): A dictionary containing Hero data.

        Returns:
            Hero: A Hero object created from the dictionary.
        """
        hero = cls(data["name"])
        hero.health = data["health"]
        hero.position = tuple(data["position"])
        hero.prev_position = tuple(data["prev_position"])
        hero.has_key = data["has_key"]
        hero.count_heal = data["count_heal"]
        return hero


if __name__ == "__main__":
    print('Вітаю, ви потрапили до гри "Лабіринт".')
    log_in = input('Введіть свій логін: ')
    game = Game(log_in)
    if game.check_save():
        game.load_game()
    else:
        logger.info('Створюється нова гра')
        game.add_heroes()
    logger.info('Гра почалась')
    game.play()
