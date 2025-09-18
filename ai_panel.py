#!/usr/bin/env python3
import gi, signal
gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gtk, WebKit2, GtkLayerShell, GLib,Gdk

screen = Gdk.Screen.get_default()
screen_width = screen.get_width()
screen_height = screen.get_height()
# --- Configurable Panel Settings ---
PANEL_WIDTH = (screen_width * 2) // 5   # easily change width
PANEL_HEIGHT = screen_height - 50  # easily change height
ANIMATION_STEPS = 20  # more steps = smoother animation
ANIMATION_DELAY = 15  # ms per step (~60fps)


class AIPanel(Gtk.Window):
    def __init__(self):
        super().__init__()
        GtkLayerShell.init_for_window(self)

        # Overlay layer
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, False)

        GtkLayerShell.set_exclusive_zone(self, 0)
        GtkLayerShell.set_keyboard_interactivity(self, True)  # overlay, no reserved space
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)

        self.set_accept_focus(True)
        self.set_focus_on_map(True)

        # Webview
        self.webview = WebKit2.WebView()
        self.webview.load_uri("http://localhost:8080")
        self.add(self.webview)

        self.visible = False
        self.set_opacity(0.0)
        self.set_default_size(PANEL_WIDTH, PANEL_HEIGHT)  # start hidden
        self.hide()

    def slide_in(self):
        self.show_all()
        self.present()
        self.grab_focus()
        self.visible = True
        step = 1 / ANIMATION_STEPS
        self.current_opacity = 0
        
        def grow():
            if self.current_opacity < 1:
                self.current_opacity += step
                if self.current_opacity > 1:
                    self.current_opacity = 1
                self.set_opacity(self.current_opacity)
                return True
            return False

        GLib.timeout_add(ANIMATION_DELAY, grow)

    def slide_out(self):
        step = 1 / ANIMATION_STEPS
        self.current_opacity = 1

        def shrink():
            if self.current_opacity > 0:
                self.current_opacity -= step
                if self.current_opacity < 0:
                    self.current_opacity = 0
                self.set_opacity(self.current_opacity)
                return True
            else:
                self.hide()
                self.visible = False
                return False

        GLib.timeout_add(ANIMATION_DELAY, shrink)

    def toggle(self):
        if self.visible:
            self.slide_out()
        else:
            self.slide_in()

# --- Global instance ---
panel = AIPanel()

# Toggle via SIGUSR1
def handle_signal(signum, frame):
    panel.toggle()

signal.signal(signal.SIGUSR1, handle_signal)

panel.connect("destroy", Gtk.main_quit)
Gtk.main()