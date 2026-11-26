import os
import tkinter as tk
import customtkinter as ctk
import numpy as np

from tkinter import filedialog, messagebox
from tkcalendar import Calendar
from datetime import datetime

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from radar_profiles_back import iter_valid_blocks


def run_continuous_viewer():

    # ==================================================
    # CONFIGURATION
    # ==================================================

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    BG = "#101827"
    PANEL = "#192438"
    GRAPH_BG = "#111C2E"

    ACCENT = "#3B82F6"
    TEXT = "#E5E7EB"
    MUTED = "#94A3B8"
    GRID = "#334155"

    COLOR_I = "#22D3EE"
    COLOR_Q = "#FB923C"

    # ==================================================
    # DATA VARIABLES
    # ==================================================

    block_gen = None

    loaded_blocks = []

    block_index = -1
    current_block = None
    current_profile = -1

    # ==================================================
    # MAIN WINDOW
    # ==================================================

    root = ctk.CTk()

    root.title("Raw Data Viewer | Radar Signal Analysis")
    root.geometry("1450x900")
    root.minsize(1150, 750)

    root.configure(fg_color=BG)

    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(1, weight=1)

    # ==================================================
    # HEADER
    # ==================================================

    header = ctk.CTkFrame(
        root,
        fg_color=PANEL,
        corner_radius=0
    )

    header.grid(
        row=0,
        column=0,
        columnspan=2,
        padx=15,
        pady=(15, 8),
        sticky="ew"
    )

    title = ctk.CTkLabel(
        header,
        text="RAW DATA VIEWER",
        font=("Arial", 24, "bold"),
        text_color=TEXT
    )

    title.pack(
        anchor="w",
        padx=20,
        pady=(12, 2)
    )

    subtitle = ctk.CTkLabel(
        header,
        text="Radar signal processing | I/Q profile visualization",
        font=("Arial", 12),
        text_color=MUTED
    )

    subtitle.pack(
        anchor="w",
        padx=21,
        pady=(0, 12)
    )

    # ==================================================
    # LEFT CONFIGURATION PANEL
    # ==================================================

    controls_frame = ctk.CTkFrame(
        root,
        width=355,
        fg_color=PANEL,
        corner_radius=0
    )

    controls_frame.grid(
        row=1,
        column=0,
        padx=(15, 8),
        pady=8,
        sticky="ns"
    )

    controls_frame.grid_propagate(False)

    controls_frame.grid_columnconfigure(0, weight=1)

    config_title = ctk.CTkLabel(
        controls_frame,
        text="DATA CONFIGURATION",
        font=("Arial", 17, "bold"),
        text_color=TEXT
    )

    config_title.grid(
        row=0,
        column=0,
        padx=15,
        pady=(18, 10),
        sticky="w"
    )

    # ==================================================
    # DATE SELECTOR
    # ==================================================

    date_label = ctk.CTkLabel(
        controls_frame,
        text="Acquisition date",
        font=("Arial", 13, "bold"),
        text_color=TEXT
    )

    date_label.grid(
        row=1,
        column=0,
        padx=15,
        pady=(8, 5),
        sticky="w"
    )

    calendar = Calendar(
        controls_frame,
        selectmode="day",
        year=datetime.now().year,
        month=datetime.now().month,
        day=datetime.now().day,
        date_pattern="dd/mm/yyyy",
        background="#192438",
        foreground="#E5E7EB",
        headersbackground="#263449",
        headersforeground="#E5E7EB",
        selectbackground="#3B82F6",
        selectforeground="#FFFFFF",
        normalbackground="#192438",
        normalforeground="#E5E7EB",
        weekendbackground="#192438",
        weekendforeground="#94A3B8",
        othermonthbackground="#101827",
        othermonthforeground="#64748B",
        bordercolor="#334155",
        font=("Arial", 10)
    )

    calendar.grid(
        row=2,
        column=0,
        padx=15,
        pady=5
    )

    # ==================================================
    # TIME SELECTOR
    # ==================================================

    time_label = ctk.CTkLabel(
        controls_frame,
        text="Acquisition time (UTC)",
        font=("Arial", 13, "bold"),
        text_color=TEXT
    )

    time_label.grid(
        row=3,
        column=0,
        padx=15,
        pady=(15, 5),
        sticky="w"
    )

    time_frame = ctk.CTkFrame(
        controls_frame,
        fg_color="transparent"
    )

    time_frame.grid(
        row=4,
        column=0,
        padx=10,
        pady=5
    )

    # Hour

    hour_spin = tk.Spinbox(
        time_frame,
        from_=0,
        to=23,
        width=5,
        format="%02.0f",
        wrap=True,
        justify="center",
        font=("Arial", 12),
        bg="#263449",
        fg="white",
        buttonbackground="#34495E",
        insertbackground="white"
    )

    hour_spin.grid(
        row=0,
        column=0,
        padx=5
    )

    tk.Label(
        time_frame,
        text="HH",
        bg=PANEL,
        fg=MUTED
    ).grid(
        row=1,
        column=0
    )

    # Minute

    minute_spin = tk.Spinbox(
        time_frame,
        from_=0,
        to=59,
        width=5,
        format="%02.0f",
        wrap=True,
        justify="center",
        font=("Arial", 12),
        bg="#263449",
        fg="white",
        buttonbackground="#34495E",
        insertbackground="white"
    )

    minute_spin.grid(
        row=0,
        column=1,
        padx=5
    )

    tk.Label(
        time_frame,
        text="MM",
        bg=PANEL,
        fg=MUTED
    ).grid(
        row=1,
        column=1
    )

    # Second

    second_spin = tk.Spinbox(
        time_frame,
        from_=0,
        to=59,
        width=5,
        format="%02.0f",
        wrap=True,
        justify="center",
        font=("Arial", 12),
        bg="#263449",
        fg="white",
        buttonbackground="#34495E",
        insertbackground="white"
    )

    second_spin.grid(
        row=0,
        column=2,
        padx=5
    )

    tk.Label(
        time_frame,
        text="SS",
        bg=PANEL,
        fg=MUTED
    ).grid(
        row=1,
        column=2
    )

    # ==================================================
    # DIRECTORY SELECTOR
    # ==================================================

    directory_label = ctk.CTkLabel(
        controls_frame,
        text="Raw data directory",
        font=("Arial", 13, "bold"),
        text_color=TEXT
    )

    directory_label.grid(
        row=5,
        column=0,
        padx=15,
        pady=(15, 5),
        sticky="w"
    )

    directory_entry = ctk.CTkEntry(
        controls_frame,
        width=315,
        height=35,
        placeholder_text="Select data directory...",
        fg_color="#263449",
        border_color="#34495E",
        corner_radius=0,
        font=("Arial", 11)
    )

    directory_entry.grid(
        row=6,
        column=0,
        padx=15,
        pady=5
    )

    def select_directory():

        directory = filedialog.askdirectory(
            parent=root,
            title="Select radar data directory"
        )

        if directory:

            directory_entry.delete(0, "end")
            directory_entry.insert(0, directory)

    browse_button = ctk.CTkButton(
        controls_frame,
        text="Browse directory",
        command=select_directory,
        width=315,
        height=35,
        corner_radius=0,
        fg_color="#34495E",
        hover_color="#456078"
    )

    browse_button.grid(
        row=7,
        column=0,
        padx=15,
        pady=5
    )

    # ==================================================
    # NUMBER OF BLOCKS
    # ==================================================

    blocks_label = ctk.CTkLabel(
        controls_frame,
        text="Number of blocks",
        font=("Arial", 13, "bold"),
        text_color=TEXT
    )

    blocks_label.grid(
        row=8,
        column=0,
        padx=15,
        pady=(15, 5),
        sticky="w"
    )

    nblocks_entry = ctk.CTkEntry(
        controls_frame,
        width=315,
        height=35,
        fg_color="#263449",
        border_color="#34495E",
        corner_radius=0,
        font=("Arial", 12)
    )

    nblocks_entry.insert(0, "50")

    nblocks_entry.grid(
        row=9,
        column=0,
        padx=15,
        pady=5
    )

    # ==================================================
    # NUMBER OF FILES
    # ==================================================

    files_label = ctk.CTkLabel(
        controls_frame,
        text="File number",
        font=("Arial", 13, "bold"),
        text_color=TEXT
    )

    files_label.grid(
        row=10,
        column=0,
        padx=15,
        pady=(10, 5),
        sticky="w"
    )

    nfiles_entry = ctk.CTkEntry(
        controls_frame,
        width=315,
        height=35,
        fg_color="#263449",
        border_color="#34495E",
        corner_radius=0,
        font=("Arial", 12)
    )

    nfiles_entry.insert(0, "85")

    nfiles_entry.grid(
        row=11,
        column=0,
        padx=15,
        pady=5
    )

    # ==================================================
    # STATUS LABEL
    # ==================================================

    status_label = ctk.CTkLabel(
        controls_frame,
        text="Waiting for configuration...",
        font=("Arial", 11),
        text_color=MUTED,
        wraplength=310
    )

    status_label.grid(
        row=12,
        column=0,
        padx=15,
        pady=(12, 5)
    )

    # ==================================================
    # LOAD DATA BUTTON
    # ==================================================

    # Se define más adelante, después de las funciones
    # de navegación.

    # ==================================================
    # RIGHT VISUALIZATION PANEL
    # ==================================================

    viewer_frame = ctk.CTkFrame(
        root,
        fg_color=PANEL,
        corner_radius=0
    )

    viewer_frame.grid(
        row=1,
        column=1,
        padx=(8, 15),
        pady=8,
        sticky="nsew"
    )

    viewer_frame.grid_columnconfigure(0, weight=1)
    viewer_frame.grid_rowconfigure(0, weight=1)

    # ==================================================
    # MATPLOTLIB FIGURE
    # ==================================================

    fig = Figure(
        figsize=(10, 7),
        dpi=120,
        facecolor=PANEL
    )

    ax0, ax1 = fig.subplots(2, 1, sharex=True)

    axes = [ax0, ax1]

    def configure_axis(ax):

        ax.set_facecolor(GRAPH_BG)

        ax.tick_params(
            colors=TEXT,
            labelsize=9
        )

        ax.grid(
            True,
            linestyle="--",
            linewidth=0.6,
            color=GRID,
            alpha=0.7
        )

        for spine in ax.spines.values():
            spine.set_color(GRID)

        ax.xaxis.label.set_color(TEXT)
        ax.yaxis.label.set_color(TEXT)
        ax.title.set_color(TEXT)

    for ax in axes:

        configure_axis(ax)

    ax0.set_title(
        "CHANNEL 0",
        color=TEXT
    )

    ax1.set_title(
        "CHANNEL 1",
        color=TEXT
    )

    ax0.text(
        0.5, 0.5,
        "Load raw data to visualize profiles",
        transform=ax0.transAxes,
        color=MUTED,
        ha="center",
        va="center",
        fontsize=13
    )

    ax1.text(
        0.5, 0.5,
        "Load raw data to visualize profiles",
        transform=ax0.transAxes,
        color=MUTED,
        ha="center",
        va="center",
        fontsize=13
    )

    fig.subplots_adjust(
        left=0.10,
        right=0.97,
        top=0.95,
        bottom=0.09,
        hspace=0.32
    )

    canvas = FigureCanvasTkAgg(
        fig,
        master=viewer_frame
    )

    canvas.get_tk_widget().grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # ==================================================
    # INFORMATION PANEL
    # ==================================================

    info_frame = ctk.CTkFrame(
        viewer_frame,
        fg_color="#263449",
        corner_radius=0
    )

    info_frame.grid(
        row=1,
        column=0,
        padx=10,
        pady=5,
        sticky="ew"
    )

    info_frame.grid_columnconfigure(
        (0, 1, 2),
        weight=1
    )

    block_label = ctk.CTkLabel(
        info_frame,
        text="BLOCK: --",
        font=("Arial", 13, "bold"),
        text_color=TEXT
    )

    block_label.grid(
        row=0,
        column=0,
        pady=12
    )

    profile_label = ctk.CTkLabel(
        info_frame,
        text="PROFILE: --",
        font=("Arial", 13, "bold"),
        text_color=TEXT
    )

    profile_label.grid(
        row=0,
        column=1,
        pady=12
    )

    time_label = ctk.CTkLabel(
        info_frame,
        text="TIME: --",
        font=("Arial", 13, "bold"),
        text_color=TEXT
    )

    time_label.grid(
        row=0,
        column=2,
        pady=12
    )

    # ==================================================
    # PROGRESS BAR
    # ==================================================

    progress = ctk.CTkProgressBar(
        viewer_frame,
        height=7,
        corner_radius=0,
        progress_color=ACCENT,
        fg_color="#263449"
    )

    progress.grid(
        row=2,
        column=0,
        padx=15,
        pady=8,
        sticky="ew"
    )

    progress.set(0)

    # ==================================================
    # NAVIGATION PANEL
    # ==================================================

    button_frame = ctk.CTkFrame(
        viewer_frame,
        fg_color=PANEL,
        corner_radius=0
    )

    button_frame.grid(
        row=3,
        column=0,
        pady=(5, 15)
    )

    # ==================================================
    # BUTTON STATES
    # ==================================================

    def update_button_states():

        at_very_start = (
            current_block is None
            or (
                block_index == 0
                and current_profile <= 0
            )
        )

        prev_button.configure(
            state="disabled" if at_very_start else "normal"
        )

    # ==================================================
    # LOAD NEXT BLOCK
    # ==================================================

    def load_next_block():

        nonlocal loaded_blocks
        nonlocal block_index
        nonlocal current_block
        nonlocal current_profile

        if block_index + 1 < len(loaded_blocks):

            block_index += 1

            current_block = loaded_blocks[block_index]

            current_profile = 0

            return True

        try:

            new_block = next(block_gen)

            loaded_blocks.append(new_block)

            block_index = len(loaded_blocks) - 1

            current_block = new_block

            current_profile = 0

            return True

        except StopIteration:

            return False

    # ==================================================
    # RENDER CURRENT PROFILE
    # ==================================================

    def render_current_profile():

        temp = current_block["temp"]

        n_profiles = current_block["nProfiles"]
        n_samples = current_block["nSamples"]

        blockcount = current_block["blockcount"]
        peru_time = current_block["peru_time"]

        t = np.arange(n_samples)

        ax0.clear()
        ax1.clear()

        for ax in axes:
            configure_axis(ax)

        # CHANNEL 0

        ax0.plot(
            t,
            np.real(temp[0, current_profile, :]),
            color=COLOR_I,
            label="I",
            linewidth=0.85
        )

        ax0.plot(
            t,
            np.imag(temp[0, current_profile, :]),
            color=COLOR_Q,
            label="Q",
            linewidth=0.85
        )

        ax0.set_title(
            "CHANNEL 0",
            fontsize=12,
            fontweight="bold",
            loc="left",
            color=TEXT
        )

        ax0.set_ylabel(
            "Amplitude (normalized)"
        )

        ax0.set_xlim(0, n_samples)
        ax0.set_ylim(-1.5, 1.5)

        # CHANNEL 1

        ax1.plot(
            t,
            np.real(temp[1, current_profile, :]),
            color=COLOR_I,
            label="I",
            linewidth=0.85
        )

        ax1.plot(
            t,
            np.imag(temp[1, current_profile, :]),
            color=COLOR_Q,
            label="Q",
            linewidth=0.85
        )

        ax1.set_title(
            "CHANNEL 1",
            fontsize=12,
            fontweight="bold",
            loc="left",
            color=TEXT
        )

        ax1.set_ylabel(
            "Amplitude (normalized)"
        )

        ax1.set_xlabel(
            "Heights (Samples)"
        )

        ax1.set_xlim(0, n_samples)
        ax1.set_ylim(-1.5, 1.5)

        # LEGENDS

        for ax in axes:

            legend = ax.legend(
                loc="upper right",
                frameon=True,
                fancybox=False,
                facecolor=PANEL,
                edgecolor=GRID,
                fontsize=9
            )

            for item in legend.get_texts():
                item.set_color(TEXT)

        # UPDATE INFORMATION

        block_label.configure(
            text=f"BLOCK: {blockcount}"
        )

        profile_label.configure(
            text=f"PROFILE: {current_profile + 1}/{n_profiles}"
        )

        time_label.configure(
            text=f"TIME: {peru_time.strftime('%H:%M:%S')} PE"
        )

        progress.set(
            (current_profile + 1) / n_profiles
        )

        fig.tight_layout(pad=2)

        canvas.draw()

        update_button_states()

    # ==================================================
    # NEXT PROFILE
    # ==================================================

    def show_next_profile():

        nonlocal current_profile

        if block_gen is None:
            return

        try:

            if current_block is None:

                if not load_next_block():

                    status_label.configure(
                        text="No blocks available.",
                        text_color="#F87171"
                    )

                    next_button.configure(
                        state="disabled",
                        text="Completed"
                    )

                    return

            else:

                current_profile += 1

                if current_profile >= current_block["nProfiles"]:

                    if not load_next_block():

                        status_label.configure(
                            text="All blocks and profiles completed.",
                            text_color="#4ADE80"
                        )

                        next_button.configure(
                            state="disabled",
                            text="Completed"
                        )

                        return

            render_current_profile()

            status_label.configure(
                text="Radar data loaded successfully.",
                text_color="#4ADE80"
            )

            print(
                f"Block {current_block['blockcount']} - "
                f"Profile {current_profile + 1}/"
                f"{current_block['nProfiles']}"
            )

        except Exception as error:

            status_label.configure(
                text="Error reading radar data.",
                text_color="#F87171"
            )

            messagebox.showerror(
                "Data loading error",
                str(error),
                parent=root
            )

            next_button.configure(
                state="disabled"
            )

    # ==================================================
    # PREVIOUS PROFILE
    # ==================================================

    def show_previous_profile():

        nonlocal block_index
        nonlocal current_block
        nonlocal current_profile

        if current_block is None:
            return

        next_button.configure(
            state="normal",
            text="Next Profile"
        )

        if current_profile > 0:

            current_profile -= 1

        elif block_index > 0:

            block_index -= 1

            current_block = loaded_blocks[block_index]

            current_profile = current_block["nProfiles"] - 1

        else:

            update_button_states()
            return

        render_current_profile()

    # ==================================================
    # GET CONFIGURATION AND LOAD DATA
    # ==================================================

    def load_data():

        nonlocal block_gen
        nonlocal loaded_blocks
        nonlocal block_index
        nonlocal current_block
        nonlocal current_profile

        try:

            # DIRECTORY

            variable_path = directory_entry.get().strip()

            if not variable_path:

                raise ValueError(
                    "Please select a radar data directory."
                )

            if not os.path.isdir(variable_path):

                raise ValueError(
                    "The selected directory does not exist."
                )

            # DATE

            selected_date = calendar.selection_get()

            variable_fecha = selected_date.strftime(
                "%d/%m/%Y"
            )

            # TIME

            hour = int(hour_spin.get())
            minute = int(minute_spin.get())
            second = int(second_spin.get())

            if not (0 <= hour <= 23):
                raise ValueError("Invalid hour.")

            if not (0 <= minute <= 59):
                raise ValueError("Invalid minute.")

            if not (0 <= second <= 59):
                raise ValueError("Invalid second.")

            variable_hora = (
                f"{hour:02d}:{minute:02d}:{second:02d}"
            )

            # NUMBER OF BLOCKS

            num_bloques = int(nblocks_entry.get())

            if num_bloques <= 0:

                raise ValueError(
                    "Number of blocks must be greater than zero."
                )

            # NUMBER OF FILES

            num_file = int(nfiles_entry.get())

            if num_file <= 0:

                raise ValueError(
                    "Number of files must be greater than zero."
                )

            # PRINT CONFIGURATION

            print("\n========== RADAR CONFIGURATION ==========")

            print("Directory:", variable_path)
            print("Date:", variable_fecha)
            print("Time:", variable_hora)
            print("Number of blocks:", num_bloques)
            print("Number of files:", num_file)

            print("=========================================\n")

            # RESET NAVIGATION

            loaded_blocks = []

            block_index = -1

            current_block = None

            current_profile = -1

            # CREATE GENERATOR

            block_gen = iter_valid_blocks(
                variable_path,
                variable_fecha,
                variable_hora,
                num_bloques,
                num_file
            )

            # RESET GRAPH

            for ax in axes:

                ax.clear()

                configure_axis(ax)

            ax0.set_title(
                "CHANNEL 0",
                color=TEXT
            )

            ax1.set_title(
                "CHANNEL 1",
                color=TEXT
            )

            canvas.draw()

            # RESET BUTTONS

            next_button.configure(
                state="normal",
                text="Next Profile"
            )

            prev_button.configure(
                state="disabled"
            )

            progress.set(0)

            status_label.configure(
                text="Loading radar data...",
                text_color=ACCENT
            )

            # LOAD FIRST PROFILE

            show_next_profile()

        except ValueError as error:

            messagebox.showwarning(
                "Invalid configuration",
                str(error),
                parent=root
            )

        except Exception as error:

            messagebox.showerror(
                "Configuration error",
                str(error),
                parent=root
            )

    # ==================================================
    # LOAD DATA BUTTON
    # ==================================================

    load_button = ctk.CTkButton(
        controls_frame,
        text="LOAD DATA",
        command=load_data,
        width=315,
        height=45,
        corner_radius=0,
        fg_color=ACCENT,
        hover_color="#2563EB",
        font=("Arial", 14, "bold")
    )

    load_button.grid(
        row=13,
        column=0,
        padx=15,
        pady=(12, 15)
    )

    # ==================================================
    # NAVIGATION BUTTONS
    # ==================================================

    prev_button = ctk.CTkButton(
        button_frame,
        text="◀ Previous Profile",
        command=show_previous_profile,
        width=190,
        height=42,
        corner_radius=0,
        fg_color="#34495E",
        hover_color="#456078",
        font=("Arial", 13, "bold"),
        state="disabled"
    )

    prev_button.pack(
        side="left",
        padx=8
    )

    next_button = ctk.CTkButton(
        button_frame,
        text="Next Profile ▶",
        command=show_next_profile,
        width=190,
        height=42,
        corner_radius=0,
        fg_color=ACCENT,
        hover_color="#2563EB",
        font=("Arial", 13, "bold"),
        state="disabled"
    )

    next_button.pack(
        side="left",
        padx=8
    )

    # ==================================================
    # KEYBOARD SHORTCUTS
    # ==================================================

    root.bind(
        "<Right>",
        lambda event: show_next_profile()
    )

    root.bind(
        "<Left>",
        lambda event: show_previous_profile()
    )

    # ==================================================
    # CLOSE WINDOW
    # ==================================================

    def on_close():

        root.destroy()

    root.protocol(
        "WM_DELETE_WINDOW",
        on_close
    )

    # ==================================================
    # START APPLICATION
    # ==================================================

    root.mainloop()


# ======================================================
# MAIN
# ======================================================

if __name__ == "__main__":

    run_continuous_viewer()