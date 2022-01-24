'''
Menu frame.
'''
import tkinter as tk
from tkinter import ttk

from app import state


class WaitProcess(tk.Toplevel):
    '''
    First start frame class.
    '''
    def __init__(self, root: object, container: object):
        self.root, self.container = root, container
        tk.Toplevel.__init__(self, self.container)
        self.title(" - ".join([self.root.wtitle, "Processing..."]))
        self.attributes('-topmost', 'true')
        if state.platform != "win32":
            self.attributes('-type', 'dialog')
        self._colors = self.root.style.colors
        self.configure(bg=self._colors["bg"])

        # Public methods: show, get_progress_func

        self._fill()

    def _fill(self) -> None:
        '''
        Load widgets.
        '''
        self.columnconfigure(0, weight=1)

        self._title_label=ttk.Label(self, anchor="center",
            style = "Title.TLabel",
            text="Please, wait.")
        self._title_label.grid(row=0, column=0, pady=(20, 10), sticky="WE")

        self._status_label=ttk.Label(self, anchor="center",
            style = "Subtitle.TLabel", text=" ".join(
                ["Process: ", "...", "of", "..."]))
        self._status_label.grid(row=1, column=0, pady=(0, 20), sticky="WE")

        pbar_frame = tk.Frame(self, bg=self._colors["bg"])
        pbar_frame.grid(row=2, column=0)
        self._progress_bar = ttk.Progressbar(pbar_frame, orient='horizontal',
            mode='determinate', length=280)
        self._progress_bar.grid(row=0, column=0, padx=(20, 0), pady=20)

        self.percent_label=ttk.Label(pbar_frame, width=4, text="  ")
        self.percent_label.grid(row=0, column=1, padx=(4, 0), sticky="W")

    def show(self, title_label_add: str) -> None:
        '''
        Show and center waitnig window, set title label text.
        '''
        self.deiconify()
        self.root.center_child(self, (480, 192))
        self._title_label.configure(text=' '.join(["Please wait.", title_label_add]))

    def get_progress_func(self, amount: int) -> callable:
        '''
        Return function for changing progress bar.
        '''
        pki = amount / 100 # divider for progress bar value
        def wrapper(num_of_amount: int) -> None:
            '''
            Change wait frame progress bar, status label and percent label.
            '''
            num_of_amount += 1
            bar_value = int((num_of_amount) / pki)
            self._status_label.configure(text=' '.join(
                ["Process: book", str(num_of_amount), "of", str(amount)]))
            self.percent_label.configure(text=''.join([str(bar_value), "%"]))
            self._progress_bar["value"] = bar_value
            self.update()
        return wrapper
