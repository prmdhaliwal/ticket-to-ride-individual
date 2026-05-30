"""Application entrypoint."""

import sys
import tkinter as tk
import sv_ttk
from controllers.game_setup import GameSetup
from controllers.game_controller import GameController
from views.main_window import MainWindow
from views.setup_window import get_player_names

def main():
    players = get_player_names()
    if not players:
        sys.exit(0) # Exit if the user closed the setup window
        
    root = tk.Tk()
    # Bootstrap the backend.
    setup = GameSetup()
    turn_manager = setup.set_up_game_for_map("London", players)
    
    controller = GameController(turn_manager)
    
    main_window = MainWindow(root, controller)
    
    turn_manager.attach(main_window)

    sv_ttk.set_theme("light")
    
    root.mainloop()

if __name__ == "__main__":
    main()
