import tkinter as tk
from tkcalendar import Calendar
from datetime import datetime

root = tk.Tk()
root.title("Radar Data Viewer")
root.geometry("400x400")

selected_date = None

calendar = Calendar(
    root,
    selectmode="day",
    year=2026,
    month=11,
    day=18,
    date_pattern="yyyy-mm-dd"
)

calendar.pack(pady=20)

def get_date():
    global selected_date

    selected_date = calendar.selection_get()

    print("Selected date:", selected_date)
    print("Formatted:", selected_date.strftime("%Y%m%d"))
    selected_date = str(selected_date)
    #print(str(selected_date))
    print(type(selected_date))

button = tk.Button(
    root,
    text="Confirm date",
    command=get_date
)

button.pack(pady=10)

root.mainloop()