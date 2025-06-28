import tkinter as tk

# --- Configuration Constants ---
BG_COLOR = "#1e1e1e"

BUTTON_BG = "#2d2d30"
BUTTON_FG = "white"
BUTTON_ACTIVE_BG = "#007acc"

OFFSET_BUTTON_V = 7    # Vertical offset for buttons
OFFSET_X = 20          # Horizontal offset to shift all buttons right
BUTTON_WIDTH = 121
BUTTON_HEIGHT = 128

# --- Button Positions ---
# Key: button label, Value: (x, y) coordinate before offset
POSITIONS = {
    "C1": (-32, 319),  "C2": (138, 317),  "C3": (305, 316),  "C4": (475, 316),
    "C5": (645, 316),  "C6": (815, 316),  "C7": (985, 316),  "C8": (1153, 316),
    "D1": (-35, 488),  "D2": (135, 488),  "D3": (305, 488),  "D4": (475, 488),
    "D5": (645, 488),  "D6": (815, 488),  "D7": (985, 488),  "D8": (1153, 488),
    "E1": (-32, 663),  "E2": (138, 663),  "E3": (305, 662),  "E4": (475, 662),
    "E5": (645, 662),  "E6": (815, 662),  "E7": (985, 662),  "E8": (1153, 662)
}

def create_button(root, label, x, y):
    """
    Create a styled button at a specified position.

    Parameters:
        root (tk.Tk): The root window.
        label (str): The text label of the button.
        x (int): The x-coordinate of the button.
        y (int): The y-coordinate of the button.
    """
    return tk.Button(
        root,
        text=label,
        bg=BUTTON_BG,
        fg=BUTTON_FG,
        activebackground=BUTTON_ACTIVE_BG
    ).place(x=x + OFFSET_X, y=y + OFFSET_BUTTON_V, width=BUTTON_WIDTH, height=BUTTON_HEIGHT)

def main():
    """
    Main entry point for the Tkinter button grid application.
    """
    root = tk.Tk()
    root.attributes('-fullscreen', True)      # Start in fullscreen mode
    root.configure(bg=BG_COLOR)               # Set background color
    root.config(cursor="none")                # Hide mouse cursor

    # Bind Escape key to exit fullscreen mode
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

    # Create buttons from the POSITIONS dictionary
    for label, (x, y) in POSITIONS.items():
        create_button(root, label, x, y)

    root.mainloop()

if __name__ == "__main__":
    main()
