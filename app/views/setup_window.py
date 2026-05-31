import tkinter as tk
import sv_ttk
from tkinter import ttk, messagebox
from models.map_catalog import MapCatalog

class SetupWindow(tk.Tk):
    def __init__(self, map_catalog=None):
        super().__init__()
        self.title("Game Setup")
        self.resizable(False, False)
        self.players = []
        self.selected_map = None
        self.current_map_definition = None

        if map_catalog is None:
            self.map_catalog = MapCatalog()
        else:
            self.map_catalog = map_catalog

        self.available_maps = self.map_catalog.available_maps()

        ttk.Label(self, text="Map:").pack(pady=(12, 5))

        self.map_var = tk.StringVar()
        if self.available_maps:
            self.map_var.set(self.available_maps[0])

        self.map_dropdown = ttk.Combobox(
            self,
            textvariable=self.map_var,
            values=self.available_maps,
            state="readonly"
        )
        self.map_dropdown.pack(pady=5)
        self.map_dropdown.bind("<<ComboboxSelected>>", self.handle_map_change)
        
        self.player_count_label = ttk.Label(self, text="Number of Players:")
        self.player_count_label.pack(pady=5)
        
        self.num_var = tk.IntVar(value=2)
        self.num_spinbox = ttk.Spinbox(
            self,
            from_=2,
            to=4,
            textvariable=self.num_var,
            command=self.update_player_entries
        )
        self.num_spinbox.pack(pady=5)
        
        self.entries_frame = ttk.Frame(self)
        self.entries_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.player_entries = []
        self.update_player_limits()
        
        ttk.Button(self, text="Start Game", command=self.start_game, style="Accent.TButton").pack(pady=20)
        
        sv_ttk.set_theme("light")
        self.fit_window()

    def fit_window(self):
        self.update_idletasks()

        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        if width < 360:
            width = 360

        if width > screen_width - 80:
            width = screen_width - 80

        if height > screen_height - 100:
            height = screen_height - 100

        x = int((screen_width - width) / 2)
        y = int((screen_height - height) / 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)

    def handle_map_change(self, event=None):
        self.update_player_limits()

    def selected_map_name(self):
        return self.map_var.get()

    def load_selected_map_definition(self):
        map_name = self.selected_map_name()

        if not map_name:
            return None

        try:
            return self.map_catalog.load_map(map_name)
        except ValueError as error:
            messagebox.showerror("Error", str(error), parent=self)
            return None

    def update_player_limits(self):
        map_definition = self.load_selected_map_definition()

        if map_definition is None:
            self.player_count_label.config(text="Number of Players:")
            self.num_spinbox.config(state=tk.DISABLED)
            self.update_player_entries()
            return

        self.current_map_definition = map_definition
        self.player_count_label.config(
            text=(
                f"Number of Players "
                f"({map_definition.min_players}-{map_definition.max_players}):"
            )
        )
        self.num_spinbox.config(
            from_=map_definition.min_players,
            to=map_definition.max_players,
            state=tk.NORMAL
        )

        try:
            player_count = self.num_var.get()
        except tk.TclError:
            player_count = map_definition.min_players

        if player_count < map_definition.min_players:
            self.num_var.set(map_definition.min_players)

        if player_count > map_definition.max_players:
            self.num_var.set(map_definition.max_players)

        self.update_player_entries()
        
    def update_player_entries(self):
        for widget in self.entries_frame.winfo_children():
            widget.destroy()
            
        self.player_entries.clear()

        min_players = 2
        max_players = 4

        if self.current_map_definition is not None:
            min_players = self.current_map_definition.min_players
            max_players = self.current_map_definition.max_players
        
        try:
            num = self.num_var.get()
            if num < min_players or num > max_players:
                return
        except tk.TclError:
            return
            
        for i in range(num):
            frame = ttk.Frame(self.entries_frame)
            frame.pack(fill=tk.X, padx=10, pady=2)
            ttk.Label(frame, text=f"Player {i+1} Name:").pack(side=tk.LEFT, padx=(20, 10))
            entry = ttk.Entry(frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))
            self.player_entries.append(entry)

        self.fit_window()

    def start_game(self):
        map_definition = self.load_selected_map_definition()

        if map_definition is None:
            messagebox.showerror("Error", "Choose a map before starting.", parent=self)
            return

        try:
            player_count = self.num_var.get()
        except tk.TclError:
            messagebox.showerror("Error", "Choose a valid number of players.", parent=self)
            return

        if player_count < map_definition.min_players:
            messagebox.showerror("Error", "Choose a valid number of players.", parent=self)
            return

        if player_count > map_definition.max_players:
            messagebox.showerror("Error", "Choose a valid number of players.", parent=self)
            return

        names = []
        for entry in self.player_entries:
            name = entry.get().strip()
            if not name:
                messagebox.showerror("Error", "All player names must be filled out.", parent=self)
                return
            names.append(name)
            
        self.players = names
        self.selected_map = self.selected_map_name()
        self.destroy()

def get_game_setup():
    dialog = SetupWindow()
    dialog.mainloop()
    return dialog.selected_map, dialog.players

def get_player_names():
    dialog = SetupWindow()
    dialog.mainloop()
    return dialog.players
