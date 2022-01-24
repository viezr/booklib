'''
Styles for appllication
'''
import tkinter as tk
from tkinter import ttk
from pathlib import Path


class Style(ttk.Style):
    '''
    Main class for application style.
    '''
    def __init__(self, colors_type: int, platform: str):
        ttk.Style.__init__(self)

        self.colors = _colors[colors_type]
        self._platform = platform
        self.map(".", background=[("disabled", self.colors["bg_mid"])])

        self.configure(".",
            background=self.colors["bg"],
            foreground=self.colors["fg"],
            troughcolor=self.colors["bg"],
            selectbg=self.colors["select_bg"],
            selectfg=self.colors["fg"],
            fieldbg=self.colors["bg"],
            font=("TkDefaultFont",),
            borderwidth=1,
            bordercolor=self.colors["bg"],
            focuscolor=self.colors["select_bg"]
        )

        if self._platform == "win32":
            self.configure(".", foreground="#000000")

        self.images = self._load_images()

        self._configure_buttons()
        self._configure_labels()
        self._configure_entries()
        self._configure_combobox()
        self._configure_treeview()
        self._configure_scrollbar()
        self._configure_progressbar()
        self._modify_checkbutton_layout()
        self._modify_radiobutton_layout()
        self._create_rating_checkbutton()

    @staticmethod
    def _load_images() -> dict:
        '''
        Load images for style.
        '''
        return {file.stem: tk.PhotoImage(file.stem, file=file)
            for file in Path('app/static/style_img').iterdir()}

    def _configure_buttons(self) -> None:
        '''
        Configure buttons style.
        '''

        self.configure("TButton", padding=(8, 4, 8, 4), width=12,
            anchor="center", relief="flat")
        self.configure("Field.TButton", padding=(2, 0, 2, 0))
        self.map("TButton",
            foreground=[
                ("active", self.colors["select_fg"])
            ],
            background=[
                ("active", self.colors["select_bg"]),
                ("!focus", self.colors["bg_light"]),
                ("focus", self.colors["bg_light"])
            ]
        )
        self.map("Mark.TButton",
            background=[
                ("active", self.colors["accent_bg_good"]),
                ("!focus", self.colors["accent_bg_good"]),
                ("focus", self.colors["accent_bg_good"])
            ]
        )
        self.map("Bad.TButton",
            background=[
                ("active", self.colors["accent_bg_bad"]),
                ("!focus", self.colors["bg_light"]),
                ("focus", self.colors["bg_light"])
            ]
        )
        self.configure("TCheckbutton", padding=(10, 4, 10, 4))
        self.configure("Rating.TCheckbutton", padding=(0, 0, 12, 0))

        if self._platform == "win32":
            self.map("TButton", foreground=[("active", "#000000")])

    def _configure_labels(self) -> None:
        '''
        Configure labels style.
        '''
        self.configure("TLabel", background=self.colors["bg"])
        self.configure("Title.TLabel", font=("Sans","12","bold"))
        self.configure("Subtitle.TLabel", font=("Sans","10","bold"))

        self.configure("ReadPerc.TLabel", relief="sunken", anchor="center",
            width=6, padding=(0, 1, 0, 1), background=self.colors["bg"],
            foreground=self.colors["fg"])

        self.map("Info.TLabel",
            background=[
                ("!focus", self.colors["accent_bg_info"])
            ]
        )
        self.map("Good.TLabel",
            background=[
                ("!focus", self.colors["accent_bg_good"])
            ]
        )
        self.map("Bad.TLabel",
            foreground=[
                ("!focus", self.colors["bg"])
            ],
            background=[
                ("!focus", self.colors["accent_bg_bad"])
            ]
        )

    def _configure_entries(self) -> None:
        '''
        Configure entries style.
        '''
        self.configure("TEntry", foreground=self.colors["treeview_fg"])
        self.map("TEntry",
            fieldbackground=[
                ("disabled", self.colors["bg_light"])
            ],
            foreground=[
                ("disabled", self.colors["fg"])
            ]
        )

        self.map("Bad.TEntry",
            fieldbackground=[
                ("!focus", self.colors["accent_bg_bad"])
            ]
        )

        if self._platform == "win32":
            self.configure("TEntry", foreground="#000000")

    def _configure_combobox(self) -> None:
        '''
        Configure combobox style.
        '''
        self.configure("TCombobox",
            background=self.colors["bg_light"],
            foreground=self.colors["treeview_fg"]
        )
        self.map("TCombobox",
            background=[
                ("active", self.colors["select_bg"]),
                ("selected", self.colors["select_bg"])
            ],
            foreground=[
                ("active", self.colors["select_bg"]),
                ("selected", self.colors["select_bg"])
            ]
        )

    def _configure_treeview(self) -> None:
        '''
        Configure treeview style.
        '''
        self.configure("Treeview", relief="flat", borderwidth=0,
            background=self.colors["treeview_bg1"],
            foreground=self.colors["treeview_fg"])

        self.configure("Treeview.Item", padding=(2, 0, 0, 0), relief="flat")
        self.configure("Treeview.Heading", borderwidth=1, relief="groove",
            bordercolor=self.colors["bg"])
        self.configure("Books.Treeview", rowheight=30,
            fieldbackground=self.colors["treeview_bg1"])
        self.configure("Side.Treeview", rowheight=20, borderwidth=1,
            foreground=self.colors["fg"],
            fieldbackground=self.colors["bg"])


        self.map("Treeview",
            background=[
                ("focus", self.colors["select_bg"]),
                ("selected", self.colors["select_inactive"])
            ]
        )

    def _configure_scrollbar(self) -> None:
        '''
        Configure scrollbar style.
        '''
        self.configure("Vertical.TScrollbar",
            background=self.colors["bg_light"],
        )

    def _configure_progressbar(self) -> None:
        '''
        Configure progressbar style.
        '''
        self.configure("Horizontal.TProgressbar",
            background=self.colors["select_bg"])

    def _modify_checkbutton_layout(self) -> None:
        '''
        Moify radiobutton layout.
        '''
        self.element_create('CustomCheck.indicator', 'image',
            'checkbox-unchecked',
            ('disabled', 'checkbox-unchecked-insensitive'),
            ('active selected', 'checkbox-checked'),
            ('pressed selected', 'checkbox-checked'),
            ('active', 'checkbox-unchecked'),
            ('selected', 'checkbox-checked'),
            ('disabled selected', 'checkbox-checked-insensitive'),
            width=22, sticky='w')

        self.layout('TCheckbutton',[
                ('Checkbutton.padding',
                {'sticky': 'nswe', 'children': [
                    ('CustomCheck.indicator', {'side': 'left', 'sticky': ''}),
                    ('Checkbutton.focus', {'side': 'left', 'sticky': '',
                        'children': [
                            ('Checkbutton.label', {'sticky': 'nswe'})
                        ]})
                ]})
            ])

    def _modify_radiobutton_layout(self) -> None:
        '''
        Moify radiobutton layout.
        '''
        self.element_create('CustomRadio.indicator', 'image',
            'radio-unchecked',
            ('disabled', 'radio-unchecked-insensitive'),
            ('active selected', 'radio-checked'),
            ('pressed selected', 'radio-checked'),
            ('active', 'radio-unchecked'),
            ('selected', 'radio-checked'),
            ('disabled selected', 'radio-checked-insensitive'),
            width=22, sticky='w')

        self.layout('TRadiobutton',[
                ('Radiobutton.padding',
                {'sticky': 'nswe', 'children': [
                    ('CustomRadio.indicator', {'side': 'left', 'sticky': ''}),
                    ('Radiobutton.focus', {'side': 'left', 'sticky': '',
                        'children': [
                            ('Radiobutton.label', {'sticky': 'nswe'})
                        ]})
                ]})
            ])

    def _create_rating_checkbutton(self) -> None:
        '''
        Moify radiobutton layout.
        '''
        self.element_create('RatingCheck.indicator', 'image',
            'rating-radio-unchecked',
            ('disabled', 'rating-radio-unchecked'),
            ('active selected', 'rating-radio-checked'),
            ('pressed selected', 'rating-radio-checked'),
            ('active', 'rating-radio-unchecked'),
            ('selected', 'rating-radio-checked'),
            ('disabled selected', 'rating-radio-checked-insensitive'),
            width=16, sticky='w')

        self.layout('Rating.TCheckbutton',[
                ('Checkbutton.padding',
                {'sticky': 'nswe', 'children': [
                    ('RatingCheck.indicator', {'side': 'left', 'sticky': ''}),
                    ('Checkbutton.focus', {'side': 'left', 'sticky': '',
                        'children': [
                            ('Checkbutton.label', {'sticky': 'nswe'})
                        ]})
                ]})
            ])

    @staticmethod
    def get_colors_set():
        '''
        Return color names used in style.
        '''
        return ("Dark", "Light")

_colors = (
    { # dark
        "fg": "#ffffff",
        "bg": "#272c33",
        "bg_mid": "#2c313a",
        "bg_light": "#424a57",
        "select_fg": "#ffffff",
        "select_inactive": "#204860",
        "select_bg": "#2e8bc0",
        "treeview_fg": "#272c33",
        "treeview_bg1": "#d4f1f4",
        "treeview_bg2": "#b1d4e0",
        "treeview_side_bg2": "#2c313a",
        "accent_bg_info": "#2e8bc0",
        "accent_bg_good": "#59981a",
        "accent_bg_bad": "#ffaebc"
    },
    { # light
        "fg": "#000000",
        "bg": "#eff0f1",
        "bg_mid": "#b3b3b9",
        "bg_light": "#cccccc",
        "select_fg": "#ffffff",
        "select_inactive": "#147eb8",
        "select_bg": "#3daee9",
        "treeview_fg": "#272c33",
        "treeview_bg1": "#d4f1f4",
        "treeview_bg2": "#b1d4e0",
        "treeview_side_bg2": "#d9d9d9",
        "accent_bg_info": "#2e8bc0",
        "accent_bg_good": "#59981a",
        "accent_bg_bad": "#ffaebc"
    }
)
