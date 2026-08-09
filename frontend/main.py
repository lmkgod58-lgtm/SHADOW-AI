from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock
import json

# ═══════════════════════════════════════════
# CONFIG: Paste your Railway URL here
BACKEND_URL = "http://shadow-ai-production-aa93.up.railway.app"
# ═══════════════════════════════════════════

class GhostFrameChatApp(App):
    def build(self):
        self.title = "GhostFrame // Vex"
        Window.clearcolor = (0.02, 0.02, 0.03, 1)

        root = BoxLayout(orientation="vertical", padding=6, spacing=4)

        # Header
        self.header = Label(
            text="[ GHOSTFRAME v2.0 ] // VEX // NEURAL LINK",
            size_hint_y=None,
            height=36,
            color=(0, 1, 0.4, 1),
            bold=True,
            font_size="14sp"
        )
        root.add_widget(self.header)

        # Chat scroll area
        scroll = ScrollView()
        self.chat_layout = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=6,
            padding=8
        )
        self.chat_layout.bind(minimum_height=self.chat_layout.setter("height"))
        scroll.add_widget(self.chat_layout)
        root.add_widget(scroll)

        # Status bar
        self.status = Label(
            text="[ SYSTEM READY ]",
            size_hint_y=None,
            height=24,
            color=(0.3, 0.6, 0.3, 1),
            font_size="11sp"
        )
        root.add_widget(self.status)

        # Input row
        input_box = BoxLayout(size_hint_y=None, height=50, spacing=6)
        self.msg_input = TextInput(
            hint_text="Enter command...",
            multiline=False,
            background_color=(0.06, 0.06, 0.08, 1),
            foreground_color=(0, 1, 0.4, 1),
            cursor_color=(0, 1, 0.4, 1),
            hint_text_color=(0.25, 0.35, 0.25, 1),
            padding=[10, 10]
        )
        self.msg_input.bind(on_text_validate=self.send_message)

        send_btn = Button(
            text="TRANSMIT",
            size_hint_x=None,
            width=100,
            background_color=(0, 0.5, 0.2, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        send_btn.bind(on_press=self.send_message)

        input_box.add_widget(self.msg_input)
        input_box.add_widget(send_btn)
        root.add_widget(input_box)

        # Welcome message from Vex
        self._add_vex_msg(
            "[NEURAL LINK ESTABLISHED]
"
            "I am Vex, your netrunner guide. I search the grid, compile intel, "
            "and write clean code. The net is vast — what do you want to know?

"
            "— Vex"
        )

        return root

    def _add_user_msg(self, text):
        self._add_msg("[YOU] >> " + text, color=(0.6, 0.8, 1, 1))

    def _add_vex_msg(self, text):
        self._add_msg("[VEX] >> " + text, color=(0, 1, 0.35, 1))

    def _add_msg(self, text, color):
        label = Label(
            text=text,
            color=color,
            size_hint_y=None,
            text_size=(Window.width - 30, None),
            halign="left",
            valign="top",
            markup=True,
            font_name="DejaVuSans"
        )
        label.bind(texture_size=label.setter("size"))

        container = BoxLayout(size_hint_y=None)
        container.add_widget(label)
        label.bind(height=lambda instance, value: setattr(container, "height", value + 12))

        self.chat_layout.add_widget(container)
        Clock.schedule_once(lambda dt: setattr(self.chat_layout.parent, "scroll_y", 0), 0.1)

    def send_message(self, instance):
        text = self.msg_input.text.strip()
        if not text:
            return

        self._add_user_msg(text)
        self.msg_input.text = ""
        self.status.text = "[ VEX IS SEARCHING THE NET... ]"
        self.status.color = (1, 0.8, 0, 1)

        headers = {"Content-Type": "application/json"}
        body = json.dumps({"message": text})

        UrlRequest(
            f"{BACKEND_URL}/chat",
            req_body=body,
            req_headers=headers,
            on_success=self._on_success,
            on_error=self._on_error,
            on_failure=self._on_error,
            timeout=90
        )

    def _on_success(self, req, result):
        self.status.text = "[ LINK ACTIVE ]"
        self.status.color = (0.3, 0.6, 0.3, 1)

        response = result.get("response", "[ SIGNAL LOST ]")
        mode = result.get("mode", "unknown")

        if mode == "fallback":
            response = "[FALLBACK MODE — AI MODEL OFFLINE]
" + response

        self._add_vex_msg(response)

    def _on_error(self, req, error):
        self.status.text = "[ LINK FAILURE ]"
        self.status.color = (1, 0.2, 0.2, 1)
        self._add_vex_msg(
            f"[CONNECTION ERROR]
{str(error)}

"
            "Diagnostics:
"
            "1. Check BACKEND_URL in main.py
"
            "2. Verify Railway backend is deployed
"
            "3. Check internet connection"
        )

    def on_pause(self):
        return True

if __name__ == "__main__":
    GhostFrameChatApp().run()
