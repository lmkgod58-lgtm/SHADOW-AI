from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.network.urlrequest import UrlRequest
from kivy.properties import NumericProperty
import json


# ============================================================
# SHADOW AI CONFIGURATION
# ============================================================

BACKEND_URL = "https://shadow-ai-production-aa93.up.railway.app"

# Put your background image here:
# frontend/background.jpg
BACKGROUND_IMAGE = "background.jpg"


# ============================================================
# MESSAGE BUBBLE
# ============================================================

class MessageBubble(BoxLayout):

    def __init__(self, text, is_user=False, **kwargs):

        super().__init__(
            orientation="vertical",
            size_hint=(None, None),
            padding=(dp(15), dp(11)),
            **kwargs
        )

        self.is_user = is_user

        # Maximum bubble width
        self.width = Window.width * (
            0.78 if is_user else 0.84
        )

        self.message = Label(
            text=text,
            color=(0.96, 0.98, 1, 1),
            font_size="15sp",
            markup=True,
            halign="left",
            valign="top",
            size_hint=(1, None),
            text_size=(self.width - dp(30), None)
        )

        self.message.bind(
            texture_size=self.update_size
        )

        self.add_widget(self.message)

        # ----------------------------------------------------
        # Bubble background
        # ----------------------------------------------------

        with self.canvas.before:

            if is_user:
                self.background_color = Color(
                    0.08, 0.34, 0.25, 0.98
                )
            else:
                self.background_color = Color(
                    0.055, 0.07, 0.09, 0.97
                )

            self.rectangle = RoundedRectangle(
                radius=[dp(20)]
            )

        # ----------------------------------------------------
        # Bubble border
        # ----------------------------------------------------

        with self.canvas.after:

            self.border_color = Color(
                0.20, 0.28, 0.30, 0.65
            )

            self.border = Line(
                rounded_rectangle=(
                    0,
                    0,
                    0,
                    0,
                    dp(20)
                ),
                width=0.8
            )

        self.bind(
            pos=self.update_graphics,
            size=self.update_graphics
        )

    def update_size(self, *_):

        self.message.text_size = (
            self.width - dp(30),
            None
        )

        self.height = (
            self.message.texture_size[1]
            + dp(22)
        )

        self.update_graphics()

    def update_graphics(self, *_):

        self.rectangle.pos = self.pos
        self.rectangle.size = self.size

        self.border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(20)
        )


# ============================================================
# MESSAGE ROW
# ============================================================

class MessageRow(BoxLayout):

    def __init__(self, bubble, is_user=False, **kwargs):

        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            padding=(dp(9), dp(3)),
            spacing=dp(4),
            **kwargs
        )

        self.add_widget(
            Widget()
        )

        if is_user:

            self.add_widget(
                bubble
            )

        else:

            self.clear_widgets()

            self.add_widget(
                bubble
            )

            self.add_widget(
                Widget()
            )

        self.bind(
            minimum_height=self.setter("height")
        )


# ============================================================
# SHADOW AI APPLICATION
# ============================================================

class ShadowAI(App):

    def build(self):

        self.title = "Shadow AI"

        Window.clearcolor = (
            0.015,
            0.02,
            0.025,
            1
        )

        # Conversation state
        self.history = []

        # Network state
        self.busy = False

        # Royal mode
        self.royal_mode = False

        # ====================================================
        # ROOT
        # ====================================================

        root = FloatLayout()

        # ====================================================
        # BACKGROUND IMAGE
        # ====================================================

        self.background = Image(
            source=BACKGROUND_IMAGE,
            allow_stretch=True,
            keep_ratio=False,
            opacity=0.18
        )

        root.add_widget(
            self.background
        )

        # ====================================================
        # MAIN UI
        # ====================================================

        interface = BoxLayout(
            orientation="vertical"
        )

        root.add_widget(
            interface
        )

        # ====================================================
        # HEADER
        # ====================================================

        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(68),
            padding=(
                dp(15),
                dp(9)
            ),
            spacing=dp(10)
        )

        with header.canvas.before:

            Color(
                0.018,
                0.027,
                0.034,
                0.96
            )

            header.background = RoundedRectangle(
                radius=[
                    0,
                    0,
                    dp(16),
                    dp(16)
                ]
            )

        header.bind(
            pos=lambda *_:
                setattr(
                    header.background,
                    "pos",
                    header.pos
                ),

            size=lambda *_:
                setattr(
                    header.background,
                    "size",
                    header.size
                )
        )

        # ====================================================
        # TITLE
        # ====================================================

        title_area = BoxLayout(
            orientation="vertical"
        )

        self.title_label = Label(
            text="SHADOW AI",
            font_size="20sp",
            bold=True,
            color=(
                0.55,
                1,
                0.82,
                1
            ),
            halign="left",
            valign="middle"
        )

        self.subtitle = Label(
            text="ONLINE • READY TO THINK",
            font_size="10sp",
            color=(
                0.46,
                0.58,
                0.62,
                1
            ),
            halign="left"
        )

        title_area.add_widget(
            self.title_label
        )

        title_area.add_widget(
            self.subtitle
        )

        header.add_widget(
            title_area
        )

        # ====================================================
        # NEW CHAT BUTTON
        # ====================================================

        new_chat = Button(
            text="＋",
            font_size="24sp",
            size_hint_x=None,
            width=dp(50),
            background_normal="",
            background_color=(
                0.08,
                0.11,
                0.14,
                1
            ),
            color=(
                0.8,
                0.9,
                0.92,
                1
            )
        )

        new_chat.bind(
            on_press=self.new_chat
        )

        header.add_widget(
            new_chat
        )

        interface.add_widget(
            header
        )

        # ====================================================
        # CHAT SCROLL AREA
        # ====================================================

        self.scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(3),
            scroll_type=["content"]
        )

        self.chat = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(5),
            padding=(
                dp(5),
                dp(12)
            )
        )

        self.chat.bind(
            minimum_height=self.chat.setter(
                "height"
            )
        )

        self.scroll.add_widget(
            self.chat
        )

        interface.add_widget(
            self.scroll
        )

        # ====================================================
        # STATUS BAR
        # ====================================================

        self.status = Label(
            text="READY",
            size_hint_y=None,
            height=dp(23),
            font_size="10sp",
            color=(
                0.44,
                0.55,
                0.58,
                1
            )
        )

        interface.add_widget(
            self.status
        )

        # ====================================================
        # MESSAGE COMPOSER
        # ====================================================

        composer = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(72),
            padding=(
                dp(9),
                dp(8)
            ),
            spacing=dp(7)
        )

        with composer.canvas.before:

            Color(
                0.025,
                0.035,
                0.045,
                0.98
            )

            composer.background = RoundedRectangle(
                radius=[dp(18)]
            )

        composer.bind(
            pos=lambda *_:
                setattr(
                    composer.background,
                    "pos",
                    composer.pos
                ),

            size=lambda *_:
                setattr(
                    composer.background,
                    "size",
                    composer.size
                )
        )

        # ====================================================
        # TEXT INPUT
        # ====================================================

        self.input = TextInput(
            hint_text="Message Shadow AI…",
            multiline=True,

            background_normal="",
            background_active="",

            background_color=(
                0.065,
                0.08,
                0.095,
                1
            ),

            foreground_color=(
                0.95,
                0.97,
                1,
                1
            ),

            hint_text_color=(
                0.40,
                0.46,
                0.50,
                1
            ),

            cursor_color=(
                0.55,
                1,
                0.82,
                1
            ),

            padding=(
                dp(14),
                dp(12)
            ),

            font_size="15sp"
        )

        composer.add_widget(
            self.input
        )

        # ====================================================
        # SEND BUTTON
        # ====================================================

        self.send_button = Button(
            text="➤",
            font_size="22sp",
            bold=True,

            color=(
                1,
                1,
                1,
                1
            ),

            size_hint_x=None,
            width=dp(55),

            background_normal="",

            background_color=(
                0.13,
                0.50,
                0.36,
                1
            )
        )

        self.send_button.bind(
            on_press=self.send_message
        )

        composer.add_widget(
            self.send_button
        )

        interface.add_widget(
            composer
        )

        # ====================================================
        # WELCOME MESSAGE
        # ====================================================

        self.add_message(
            "Hey. I'm Shadow AI.\n\n"
            "Ask me anything. I can research information, "
            "explain complicated topics, compare options, "
            "help you plan things, and use the tools available "
            "through my Railway backend.\n\n"
            "Hidden mode: type 666(LINDO)"
        )

        # Automatically focus input
        Clock.schedule_once(
            lambda dt:
                setattr(
                    self.input,
                    "focus",
                    True
                ),
            0.3
        )

        return root

    # ========================================================
    # ADD MESSAGE
    # ========================================================

    def add_message(
        self,
        text,
        is_user=False
    ):

        bubble = MessageBubble(
            text,
            is_user=is_user
        )

        row = MessageRow(
            bubble,
            is_user=is_user
        )

        self.chat.add_widget(
            row
        )

        Clock.schedule_once(
            self.scroll_to_bottom,
            0.05
        )

    # ========================================================
    # SCROLL TO BOTTOM
    # ========================================================

    def scroll_to_bottom(self, *_):

        self.scroll.scroll_y = 0

    # ========================================================
    # NEW CHAT
    # ========================================================

    def new_chat(self, *_):

        self.history = []

        self.royal_mode = False

        self.chat.clear_widgets()

        self.add_message(
            "New conversation started.\n\n"
            "Shadow AI is ready."
        )

        self.status.text = "READY"

        self.subtitle.text = (
            "ONLINE • READY TO THINK"
        )

        self.input.text = ""

        self.input.focus = True

    # ========================================================
    # SEND MESSAGE
    # ========================================================

    def send_message(self, *_):

        if self.busy:
            return

        text = self.input.text.strip()

        if not text:
            return

        # ----------------------------------------------------
        # Detect LINDO mode locally
        # ----------------------------------------------------

        if "666(LINDO)" in text.upper():

            self.royal_mode = True

            text = text.replace(
                "666(LINDO)",
                ""
            )

            text = text.replace(
                "666(lindo)",
                ""
            )

            text = text.strip()

            # If user only typed the activation code
            if not text:

                text = (
                    "Activate royal mode."
                )

        # ----------------------------------------------------
        # Display user's message
        # ----------------------------------------------------

        display_text = text

        if self.royal_mode:

            self.add_message(
                display_text,
                is_user=True
            )

        else:

            self.add_message(
                display_text,
                is_user=True
            )

        # ----------------------------------------------------
        # Add to conversation history
        # ----------------------------------------------------

        self.history.append(
            {
                "role": "user",
                "content": text
            }
        )

        # Keep history reasonable
        self.history = self.history[-20:]

        # Clear input
        self.input.text = ""

        # ----------------------------------------------------
        # Network state
        # ----------------------------------------------------

        self.busy = True

        self.status.text = (
            "THINKING • RESEARCHING WHEN NEEDED…"
        )

        if self.royal_mode:

            self.subtitle.text = (
                "ROYAL MODE • LINDO"
            )

        else:

            self.subtitle.text = (
                "PROCESSING • RAILWAY ACTIVE"
            )

        # ----------------------------------------------------
        # Backend request
        # ----------------------------------------------------

        request_body = {
            "message": text,

            "history": self.history[-20:],

            "deep_search": True,

            "royal_mode": self.royal_mode
        }

        body = json.dumps(
            request_body
        )

        headers = {
            "Content-Type":
                "application/json",

            "Accept":
                "application/json"
        }

        UrlRequest(
            BACKEND_URL + "/chat",

            req_body=body,

            req_headers=headers,

            on_success=self.on_success,

            on_error=self.on_error,

            on_failure=self.on_error,

            timeout=120
        )

    # ========================================================
    # BACKEND SUCCESS
    # ========================================================

    def on_success(
        self,
        request,
        result
    ):

        self.busy = False

        # ----------------------------------------------------
        # Validate response
        # ----------------------------------------------------

        if not isinstance(result, dict):

            answer = (
                "The backend returned an invalid response."
            )

        else:

            answer = result.get(
                "response",
                "The backend returned an empty response."
            )

        # ----------------------------------------------------
        # Store assistant message
        # ----------------------------------------------------

        self.history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        self.history = self.history[-20:]

        # ----------------------------------------------------
        # Backend may confirm royal mode
        # ----------------------------------------------------

        if isinstance(result, dict):

            self.royal_mode = bool(
                result.get(
                    "royal_mode",
                    self.royal_mode
                )
            )

        # ----------------------------------------------------
        # Display answer
        # ----------------------------------------------------

        self.add_message(
            answer,
            is_user=False
        )

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        if isinstance(result, dict):

            mode = result.get(
                "mode",
                "AI"
            )

            sources = result.get(
                "sources_count",
                0
            )

        else:

            mode = "AI"
            sources = 0

        self.status.text = (
            f"READY • {str(mode).upper()} • "
            f"{sources} SOURCE BLOCKS"
        )

        if self.royal_mode:

            self.subtitle.text = (
                "ROYAL MODE • LINDO"
            )

        else:

            self.subtitle.text = (
                "ONLINE • READY TO THINK"
            )

        self.input.focus = True

    # ========================================================
    # BACKEND ERROR
    # ========================================================

    def on_error(
        self,
        request,
        error
    ):

        self.busy = False

        self.status.text = (
            "CONNECTION ERROR"
        )

        self.subtitle.text = (
            "BACKEND UNREACHABLE"
        )

        self.add_message(
            "I couldn't reach the Railway backend.\n\n"
            "Check the backend URL, Railway deployment, "
            "internet connection, and /chat endpoint."
        )

        self.input.focus = True

    # ========================================================
    # ANDROID PAUSE
    # ========================================================

    def on_pause(self):

        return True


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    ShadowAI().run()
