import tkinter as tk
from tkinter import filedialog
from tkcalendar import Calendar
from datetime import datetime, time, timezone

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#from rawdata-visor import 

root = tk.Tk()
root.title("Radar Data Viewer")
root.geometry("500x750")

# Main layout
controls_frame = tk.Frame(root)
controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

plot_frame = tk.Frame(root)
plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

selected_datetime = None
selected_directory = None
selected_nBlocks = None

def plot_signal():

    # Generate sinusoidal signal
    t = np.linspace(0, 2*np.pi, 1000)

    frequency = 2
    signal = np.sin(frequency * t)

    # Create figure
    fig = Figure(figsize=(10, 6), dpi=100)

    ax = fig.add_subplot(111)

    ax.plot(t, signal)

    ax.set_title("Reference Sinusoidal Signal")
    ax.set_xlabel("Time")
    ax.set_ylabel("Amplitude")

    ax.grid(True)

    fig.tight_layout()

    # Embed plot in Tkinter
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)

    canvas.draw()

    canvas.get_tk_widget().pack(
        fill=tk.BOTH,
        expand=True
    )

# -----------------------------
# DATE SELECTOR
# -----------------------------

tk.Label(
    controls_frame,
    text="Select acquisition date",
    font=("Arial", 12, "bold")
).pack(pady=10)

calendar = Calendar(
    controls_frame,
    selectmode="day",
    year=2026,
    month=11,
    day=18,
    date_pattern="yyyy-mm-dd"
)

calendar.pack(pady=10)


# -----------------------------
# TIME SELECTOR
# -----------------------------

tk.Label(
    controls_frame,
    text="Select acquisition time (UTC)",
    font=("Arial", 12, "bold")
).pack(pady=10)

time_frame = tk.Frame(controls_frame)
time_frame.pack(pady=10)

# Hours
tk.Label(time_frame, text="Hour").grid(row=0, column=0, padx=10)

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

# Minutes
tk.Label(time_frame, text="Minute").grid(row=0, column=1, padx=10)

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

# Seconds
tk.Label(time_frame, text="Second").grid(row=0, column=2, padx=10)

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


# -----------------------------
# DIRECTORY SELECTOR
# -----------------------------

tk.Label(
    controls_frame,
    text="Select raw data directory",
    font=("Arial", 12, "bold")
).pack(pady=15)

directory_frame = tk.Frame(controls_frame)
directory_frame.pack(pady=5)

directory_entry = tk.Entry(
    directory_frame,
    width=40
)
directory_entry.pack(side=tk.LEFT, padx=5)


def select_directory():

    global selected_directory

    selected_directory = filedialog.askdirectory(
        title="Select radar data directory"
    )

    if selected_directory:

        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, selected_directory)

        print("Selected directory:", selected_directory)


browse_button = tk.Button(
    directory_frame,
    text="Browse",
    command=select_directory
)

browse_button.pack(side=tk.LEFT)


# -----------------------------
# NUMBER OF BLOCKS SELECTOR
# -----------------------------

tk.Label(
    controls_frame,
    text="Number of blocks (nBlocks)",
    font=("Arial", 12, "bold")
).pack(pady=15)

nblocks_entry = tk.Entry(
    controls_frame,
    width=15,
    justify="center"
)

nblocks_entry.insert(0, "214")  # Default value
nblocks_entry.pack(pady=5)


# -----------------------------
# GET CONFIGURATION
# -----------------------------

def get_datetime():

    global selected_datetime
    global selected_directory
    global selected_nBlocks

    # Get selected date
    selected_date = calendar.selection_get()

    # Get selected time
    hour = int(hour_spin.get())
    minute = int(minute_spin.get())
    second = int(second_spin.get())

    # Combine date and time (UTC)
    selected_datetime = datetime.combine(
        selected_date,
        time(hour, minute, second),
        tzinfo=timezone.utc
    )

    # Unix timestamp
    timestamp = selected_datetime.timestamp()

    # Get directory
    selected_directory = directory_entry.get()

    # Get number of blocks
    selected_nBlocks = int(nblocks_entry.get())

    print("\n========== RADAR CONFIGURATION ==========")

    print("Selected datetime:", selected_datetime)

    print(
        "Formatted:",
        selected_datetime.strftime("%Y%m%d_%H%M%S")
    )

    print("Unix timestamp:", timestamp)

    print("Selected directory:", selected_directory)

    print("Number of blocks:", selected_nBlocks)

    print("Type nBlocks:", type(selected_nBlocks))

    print("=========================================\n")

    #aqui se genera la grafica
    plot_signal()


# -----------------------------
# CONFIRM BUTTON
# -----------------------------

button = tk.Button(
    controls_frame,
    text="Confirm configuration",
    command=get_datetime,
    font=("Arial", 11, "bold")
)

button.pack(pady=25)



#controls_frame.mainloop()
root.mainloop()