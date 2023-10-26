from kivy.core.text import LabelBase
from kivy.properties import NumericProperty, ListProperty
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivy.lang.builder import Builder
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.animation import Animation


class Player(Widget):
    speed = NumericProperty(0)


class Obstacle(Widget):
    color = ListProperty([.3, .3, .2, 1])
    scored = False
    game_screen = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anim = Animation(x=-self.width, duration=4)
        self.anim.bind(on_complete=self.vanish)
        self.anim.start(self)
        self.game_screen = app.root.get_screen('game')

    def on_x(self, *args):
        if self.game_screen:
            if self.x < self.game_screen.ids.player.x and not self.scored:
                self.game_screen.score += 1/2
                self.scored = True

    def vanish(self, *args):
        self.game_screen.remove_widget(self)
        self.game_screen.obstacles.remove(self)


class Login(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class GameOver(MDScreen):
    pass


class Game(MDScreen):
    obstacles = []
    score: float = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.ids.player.x = self.width / 20
        self.ids.player.y = self.height / 2
        self.ids.player.speed = 0
        self.score = 0

    def on_enter(self, *args):
        Clock.schedule_interval(self.update, 1 / 30)
        Clock.schedule_interval(self.put_obstacle, 1)

    def update(self, *args):
        # atualizando a posição do objeto
        self.ids.player.speed += -self.height * 0.7 * 1 / 30
        self.ids.player.y += self.ids.player.speed * 1 / 30

        # verificando a derrota
        if self.ids.player.y >= self.height or self.ids.player.y <= .001 * self.height:
            self.gameover()
        if self.player_collided():
            self.gameover()

    def put_obstacle(self, *args):
        from random import random
        gap = self.height*.3
        position = (self.height - gap)*random()
        large = self.width*.05

        obstacleHigh = Obstacle(x=self.width,
                                y=position + gap,
                                height=(self.height - position - gap)/2,
                                width=large)
        obstacleLow = Obstacle(x=self.width,
                               height=position/2,
                               width=large)

        self.add_widget(obstacleLow, 1)
        self.obstacles.append(obstacleLow)

        self.add_widget(obstacleHigh, 1)
        self.obstacles.append(obstacleHigh)

    def gameover(self):
        Clock.unschedule(self.update, 1 / 30)
        Clock.unschedule(self.put_obstacle, 1)
        for ob in self.obstacles:
            ob.anim.cancel(ob)
            self.remove_widget(ob)
        self.obstacles = []
        app.root.current = 'gameover'

    def on_touch_down(self, touch, *args, **kwargs):
        super().on_touch_down(touch, *args, **kwargs)
        if self.height/3 <= self.ids.player.y <= touch.pos[1]:
            self.ids.player.speed = -self.height * 0.2
        elif touch.pos[1] >= self.height*0.8:
            self.ids.player.speed = -self.height * 0.2
        else:
            self.ids.player.speed = +self.height * 0.3

    def collided(self, wid1, wid2):
        if wid2.x < wid1.x + wid1.width and \
                wid1.x < wid2.x + wid2.width and \
                wid1.y < wid2.y + wid2.height and \
                wid2.y < wid1.y + wid1.height:
            return True
        return False

    def player_collided(self):
        collided = False
        for obstacle in self.obstacles:
            if self.collided(self.ids.player, obstacle):
                collided = True
                break
        return collided


class Principal(MDScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Bird(MDApp):
    def build(self, **kwargs):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.material_style = 'M3'
        self.theme_cls.primary_palette = 'Green'
        Builder.load_file('game.kv')
        return Principal()


if __name__ == '__main__':
    LabelBase.register(
        name='Skranji',
        fn_regular='./Skranji-Regular.ttf'
    )
    app = Bird()
    app.run()
