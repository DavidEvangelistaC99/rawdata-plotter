
import tkinter as tk
from tkinter import filedialog, messagebox

from backend import process_radar_data

from tkcalendar import Calendar

from datetime import datetime, time, timezone

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import numpy as np


# =====================================================
# MAIN WINDOW
# =====================================================

root = tk.Tk()

root.title("Radar Data Viewer")
root.geometry("1100x850")

root.minsize(900, 700)


# =====================================================
# MAIN CONFIGURATION FRAME
# =====================================================

config_frame = tk.LabelFrame(
    root,
    text="Radar Configuration",
    font=("Arial", 11, "bold")
)

config_frame.pack(
    fill=tk.X,
    padx=10,
    pady=10
)


# =====================================================
# DATE SELECTOR
# =====================================================

tk.Label(
    config_frame,
    text="Acquisition Date",
    font=("Arial", 11, "bold")
).grid(row=0, column=0, padx=15, pady=10)

calendar = Calendar(
    config_frame,
    selectmode="day",
    year=2026,
    month=11,
    day=19,
    date_pattern="yyyy-mm-dd"
)

calendar.grid(
    row=1,
    column=0,
    rowspan=4,
    padx=15,
    pady=5
)


# =====================================================
# TIME SELECTOR
# =====================================================

tk.Label(
    config_frame,
    text="Acquisition Time (UTC)",
    font=("Arial", 11, "bold")
).grid(row=0, column=1, columnspan=3, pady=10)


time_frame = tk.Frame(config_frame)

time_frame.grid(
    row=1,
    column=1,
    columnspan=3,
    pady=10
)


# HOURS

tk.Label(
    time_frame,
    text="Hour"
).grid(row=0, column=0, padx=10)

hour_spin = tk.Spinbox(
    time_frame,
    from_=0,
    to=23,
    increment=1,
    width=5,
    format="%02.0f",
    wrap=True
)

hour_spin.grid(row=1, column=0, padx=10)


# MINUTES

tk.Label(
    time_frame,
    text="Minute"
).grid(row=0, column=1, padx=10)

minute_spin = tk.Spinbox(
    time_frame,
    from_=0,
    to=59,
    increment=1,
    width=5,
    format="%02.0f",
    wrap=True
)

minute_spin.grid(row=1, column=1, padx=10)


# SECONDS

tk.Label(
    time_frame,
    text="Second"
).grid(row=0, column=2, padx=10)

second_spin = tk.Spinbox(
    time_frame,
    from_=0,
    to=59,
    increment=1,
    width=5,
    format="%02.0f",
    wrap=True
)

second_spin.grid(row=1, column=2, padx=10)


# =====================================================
# DIRECTORY SELECTOR
# =====================================================

tk.Label(
    config_frame,
    text="Raw Data Directory",
    font=("Arial", 11, "bold")
).grid(
    row=5,
    column=0,
    columnspan=4,
    pady=(15, 5)
)


directory_frame = tk.Frame(config_frame)

directory_frame.grid(
    row=6,
    column=0,
    columnspan=4,
    pady=5
)


directory_entry = tk.Entry(
    directory_frame,
    width=65
)

directory_entry.pack(
    side=tk.LEFT,
    padx=5
)


def select_directory():

    selected_directory = filedialog.askdirectory(
        title="Select radar data directory"
    )

    if selected_directory:

        directory_entry.delete(0, tk.END)

        directory_entry.insert(
            0,
            selected_directory
        )


browse_button = tk.Button(
    directory_frame,
    text="Browse",
    command=select_directory
)

browse_button.pack(side=tk.LEFT)


# =====================================================
# NUMBER OF BLOCKS
# =====================================================

tk.Label(
    config_frame,
    text="Number of Blocks (NBLOCKS)",
    font=("Arial", 11, "bold")
).grid(
    row=7,
    column=0,
    columnspan=4,
    pady=(15, 5)
)


nblocks_entry = tk.Entry(
    config_frame,
    width=15,
    justify="center"
)

nblocks_entry.insert(0, "214")

nblocks_entry.grid(
    row=8,
    column=0,
    columnspan=4,
    pady=5
)


# =====================================================
# GET CONFIGURATION
# =====================================================

def get_configuration():

    try:

        # DATE

        selected_date = calendar.selection_get()

        DIA = selected_date.strftime("%d/%m/%Y")

        print(DIA)


        # TIME (UTC)

        hour = int(hour_spin.get())

        minute = int(minute_spin.get())

        second = int(second_spin.get())

        HORA = f"{hour:02d}:{minute:02d}:{second:02d}"


        # PATH

        PATH = directory_entry.get().strip()


        # NBLOCKS

        NBLOCKS = int(nblocks_entry.get())


        # VALIDATION

        if not PATH:

            messagebox.showerror(
                "Configuration Error",
                "Please select a data directory."
            )

            return

        import os

        if not os.path.isdir(PATH):

            messagebox.showerror(
                "Configuration Error",
                "The selected directory does not exist."
            )

            return

        if NBLOCKS <= 0:

            messagebox.showerror(
                "Configuration Error",
                "NBLOCKS must be greater than zero."
            )

            return


        # DATETIME

        selected_datetime = datetime.combine(
            selected_date,
            time(hour, minute, second),
            tzinfo=timezone.utc
        )

        timestamp = int(selected_datetime.timestamp())


        # DISPLAY CONFIGURATION

        print("\n========== RADAR CONFIGURATION ==========")

        print("PATH:", PATH)

        print("DIA:", DIA)

        print("HORA:", HORA)

        print("NBLOCKS:", NBLOCKS)

        print("UTC timestamp:", timestamp)

        print("=========================================\n")


        return PATH, DIA, HORA, NBLOCKS


    except ValueError:

        messagebox.showerror(
            "Configuration Error",
            "Please enter valid time and NBLOCKS values."
        )


# =====================================================
# GRAPH AREA
# =====================================================

plot_frame = tk.LabelFrame(
    root,
    text="Radar Signal Visualization",
    font=("Arial", 11, "bold")
)

plot_frame.pack(
    fill=tk.BOTH,
    expand=True,
    padx=10,
    pady=10
)


# =====================================================
# MATPLOTLIB FIGURE
# =====================================================

fig = Figure(
    figsize=(9, 5),
    dpi=100
)

ax = fig.add_subplot(111)

ax.set_title("Radar Signal")

ax.set_xlabel("Samples")

ax.set_ylabel("Amplitude")

ax.grid(True)


# =====================================================
# TKINTER CANVAS
# =====================================================

canvas = FigureCanvasTkAgg(
    fig,
    master=plot_frame
)

canvas_widget = canvas.get_tk_widget()

canvas_widget.pack(
    fill=tk.BOTH,
    expand=True
)


# =====================================================
# TEST PLOT
# =====================================================

def test_plot():

    x = np.arange(800)

    signal = np.sin(2 * np.pi * x / 100)

    ax.clear()

    ax.plot(
        x,
        signal,
        label="Test Signal"
    )

    ax.set_title("Radar Signal Visualization")

    ax.set_xlabel("Samples")

    ax.set_ylabel("Amplitude")

    ax.grid(True)

    ax.legend()

    canvas.draw_idle()

def run_processing():

    # 1. Get configuration from frontend
    configuration = get_configuration()

    if configuration is None:
        return

    PATH, DIA, HORA, NBLOCKS = configuration

    try:

        # 2. Execute backend
        processed_data = process_radar_data(
            PATH,
            DIA,
            HORA,
            NBLOCKS
        )

        # 3. Check returned data
        if len(processed_data) == 0:

            messagebox.showwarning(
                "Processing Warning",
                "No radar blocks were found for the selected time."
            )

            return

        # 4. Select first processed block
        temp = processed_data[0]

        # 5. Plot first profile of channel 0
        x = np.arange(temp.shape[2])

        ax.clear()

        ax.plot(
            x,
            temp[0, 0, :].real,
            label="Real"
        )

        ax.plot(
            x,
            temp[0, 0, :].imag,
            label="Imaginary"
        )

        ax.set_title("Channel 0 - Profile 1")

        ax.set_xlabel("Samples")

        ax.set_ylabel("Amplitude")

        ax.grid(True)

        ax.legend()

        canvas.draw_idle()

        messagebox.showinfo(
            "Processing Completed",
            f"Processed blocks: {len(processed_data)}"
        )

    except Exception as e:

        messagebox.showerror(
            "Processing Error",
            str(e)
        )
# =====================================================
# BUTTONS
# =====================================================

button_frame = tk.Frame(root)

button_frame.pack(
    pady=10
)


confirm_button = tk.Button(
    button_frame,
    text="Confirm Configuration",
    font=("Arial", 11, "bold"),
    width=22,
    command=run_processing
)

confirm_button.pack(
    side=tk.LEFT,
    padx=10
)


test_button = tk.Button(
    button_frame,
    text="Test Plot",
    font=("Arial", 11, "bold"),
    width=15,
    command=test_plot
)

test_button.pack(
    side=tk.LEFT,
    padx=10
)

plot_button = tk.Button(
    button_frame,
    text="Plot Radar Data",
    font=("Arial", 11, "bold"),
    width=18,
    command=run_processing
)

plot_button.pack(
    side=tk.LEFT,
    padx=10
)
# =====================================================
# MAIN LOOP
# =====================================================

root.mainloop()
