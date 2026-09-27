
from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle
import os, json, datetime, math, sys

def resource_path(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)

class MusicPlus(App):
    def build(self):
        self.title = "Music+"
        self.tracks=[]
        self.current=-1
        self.sound=None
        self.duration=0
        self.playing=False
        self.root_layout=FloatLayout()

        # Wallpaper from uploaded image
        self.bg=Image(source=resource_path("wallpaper.jpg"), allow_stretch=True, keep_ratio=False,
                      size_hint=(1,1), opacity=.16)
        self.root_layout.add_widget(self.bg)

        # White translucent surface
        with self.root_layout.canvas.before:
            Color(1,1,1,.88)
            self.rect=RoundedRectangle(pos=(0,0), size=Window.size, radius=[(0,0)]*4)
        Window.bind(size=self._resize)

        self.loading=FloatLayout()
        with self.loading.canvas.before:
            Color(1,1,1,.78)
            self.loading_bg=RoundedRectangle(pos=(0,0), size=Window.size, radius=[(28,)])
        self.root_layout.add_widget(self.loading)

        # Logo (uploaded GIF) centered, starts small/far and scales up
        self.logo=Image(source=resource_path("logo.gif"), size_hint=(.2,.2),
                        pos_hint={"center_x":.5,"center_y":.57})
        self.loading.add_widget(self.logo)
        self.percent=Label(text="0.0%", color=(.05,.05,.05,1),
                           font_size="20sp", size_hint=(1,.08),
                           pos_hint={"x":0,"y":.25})
        self.loading.add_widget(self.percent)
        self.bar=ProgressBar(max=100,value=0,size_hint=(.7,.025),
                             pos_hint={"center_x":.5,"y":.21})
        self.loading.add_widget(self.bar)
        self.clock_label=Label(text=self.msk_time(), color=(.1,.1,.1,1),
                               font_size="14sp", size_hint=(1,.06),
                               pos_hint={"x":0,"y":.14})
        self.loading.add_widget(self.clock_label)
        Clock.schedule_interval(self.loading_tick, .03)

        return self.root_layout

    def _resize(self,*args):
        self.loading_bg.size=Window.size
        self.rect.size=Window.size

    def msk_time(self):
        from datetime import timezone, timedelta
        now=datetime.datetime.now(timezone.utc)+timedelta(hours=3)
        return "МСК  " + now.strftime("%H:%M:%S")

    def loading_tick(self,dt):
        v=min(100,self.bar.value+1.1)
        self.bar.value=v
        self.percent.text=f"{v:.1f}%"
        self.clock_label.text=self.msk_time()
        # far -> middle smooth pop
        s=.2 + .8*(v/100)
        self.logo.size_hint=(.2*s,.2*s)
        if v>=100:
            Clock.unschedule(self.loading_tick)
            self.root_layout.remove_widget(self.loading)
            self.show_player()

    def show_player(self):
        panel=BoxLayout(orientation="vertical", padding=18, spacing=10,
                        size_hint=(.92,.88), pos_hint={"center_x":.5,"center_y":.48})
        with panel.canvas.before:
            Color(1,1,1,.96)
            self.panel_rect=RoundedRectangle(pos=panel.pos,size=panel.size,radius=[(24,)])
        panel.bind(pos=lambda *_: setattr(self.panel_rect,'pos',panel.pos),
                   size=lambda *_: setattr(self.panel_rect,'size',panel.size))

        top=BoxLayout(size_hint_y=.14)
        top.add_widget(Label(text="Music+",color=(.05,.05,.05,1),font_size="28sp"))
        self.time=Label(text=self.msk_time(),color=(.3,.3,.3,1))
        top.add_widget(self.time)
        panel.add_widget(top)

        self.list_box=BoxLayout(orientation="vertical",spacing=6)
        panel.add_widget(self.list_box)

        controls=BoxLayout(size_hint_y=.2,spacing=8)
        self.prev=Button(text="⏮",background_color=(.95,.95,.95,1),color=(.05,.05,.05,1))
        self.play=Button(text="▶",background_color=(.15,.15,.15,1),color=(1,1,1,1))
        self.next=Button(text="⏭",background_color=(.95,.95,.95,1),color=(.05,.05,.05,1))
        self.add=Button(text="Добавить музыку",background_color=(.95,.95,.95,1),color=(.05,.05,.05,1))
        self.prev.bind(on_release=lambda *_:self.prev_track())
        self.play.bind(on_release=lambda *_:self.toggle())
        self.next.bind(on_release=lambda *_:self.next_track())
        self.add.bind(on_release=lambda *_:self.open_files())
        for b in [self.prev,self.play,self.next,self.add]: controls.add_widget(b)
        panel.add_widget(controls)

        self.root_layout.add_widget(panel)
        Clock.schedule_interval(self.update_ui,1)
        self.load_demo()

    def load_demo(self):
        self.tracks=[
            {"title":"Моя первая песня","artist":"Локальная музыка","path":None},
            {"title":"Ночной плейлист","artist":"Локальная музыка","path":None},
            {"title":"Добавь свои песни","artist":"Music+","path":None},
        ]
        self.refresh_list()

    def refresh_list(self):
        self.list_box.clear_widgets()
        for i,t in enumerate(self.tracks):
            b=Button(text=f"{t['title']} — {t['artist']}",background_color=(.96,.96,.96,1),
                     color=(.08,.08,.08,1),halign="left")
            b.bind(on_release=lambda _,n=i:self.play_track(n))
            self.list_box.add_widget(b)

    def open_files(self):
        fc=FileChooserListView(filters=["*.mp3","*.wav","*.ogg","*.m4a","*.aac"],path="/")
        box=FloatLayout()
        box.add_widget(fc)
        close=Button(text="Добавить выбранные",size_hint=(1,.1),pos_hint={"x":0,"y":0})
        box.add_widget(close)
        self.root_layout.add_widget(box)
        def add(*_):
            for p in fc.selection:
                self.tracks.append({"title":os.path.basename(p),"artist":"Моя музыка","path":p})
            self.root_layout.remove_widget(box)
            self.refresh_list()
        close.bind(on_release=add)

    def play_track(self,i):
        t=self.tracks[i]
        if not t["path"]:
            return
        if self.sound: self.sound.stop()
        self.sound=SoundLoader.load(t["path"])
        if self.sound:
            self.current=i
            self.sound.play()
            self.play.text="⏸"
            self.playing=True

    def toggle(self):
        if not self.sound: return
        if self.playing:
            self.sound.stop()
            self.playing=False
            self.play.text="▶"
        else:
            self.sound.play()
            self.playing=True
            self.play.text="⏸"

    def next_track(self):
        if not self.tracks:return
        start=(self.current+1)%len(self.tracks)
        for j in range(len(self.tracks)):
            i=(start+j)%len(self.tracks)
            if self.tracks[i]["path"]:
                self.play_track(i); return

    def prev_track(self):
        if not self.tracks:return
        i=(self.current-1)%len(self.tracks)
        if self.tracks[i]["path"]: self.play_track(i)

    def update_ui(self,dt):
        if hasattr(self,"time"):
            self.time.text=self.msk_time()

if __name__=="__main__":
    MusicPlus().run()
