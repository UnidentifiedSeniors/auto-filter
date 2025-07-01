from automate_filters import AutoFilter
import tkinter as tk
import threading, time, ctypes
import keyboard

# Callback to display extracted results
def display_results(text):
    text_output.config(state="normal")
    text_output.delete("1.0", tk.END)
    text_output.insert(tk.END, text)
    text_output.config(state="disabled")

automation_on = False
should_stop = False

# Run the AutoFilter start() n times on a background thread
def start_script_loop(times):
    def runner():
        global automation_on
        for _ in range(times):
            if not automation_on:
                break
            lister.start()
        update_gui_on_stop()
    threading.Thread(target=runner, daemon=True).start()

def safe_stop_gui():
    update_gui_on_stop()

def stop_script():
    global should_stop
    should_stop = True
    root.after(0, safe_stop_gui)

def update_gui_on_stop():
    global automation_on
    status_label.config(text="Automation stopped", fg="#FF5555")
    button.config(text="Start Automation", state="normal", bg="#00FFAA")
    amount_entry.config(state="normal")  # re‑enable
    automation_on = False

def click_button():
    global automation_on, should_stop

    def delayed_start():
        global automation_on, should_stop

        # Parse count
        try:
            times = int(amount_entry.get())
            if times < 1:
                raise ValueError
        except ValueError:
            status_label.config(text="Enter a valid number", fg="#FF5555")
            return

        # Lock out controls
        amount_entry.delete(0, tk.END)
        amount_entry.config(state="disabled")
        button.config(state="disabled")

        # Countdown
        for i in (2, 1):
            status_label.config(text=f"Starting in {i}s…", fg="#FFAA00")
            time.sleep(1)

        # Kick off
        status_label.config(text="Automation started!", fg="#55FF55")
        button.config(text="Stop Automation", state="normal", bg="#FF5555")
        automation_on = True
        should_stop = False

        start_script_loop(times)

    def delayed_stop():
        global automation_on
        button.config(state="disabled")
        for i in (1,):
            status_label.config(text=f"Stopping in {i}s…", fg="#FFAA00")
            time.sleep(1)
        automation_on = False
        update_gui_on_stop()

    if not automation_on:
        threading.Thread(target=delayed_start, daemon=True).start()
    else:
        threading.Thread(target=delayed_stop, daemon=True).start()

# GUI setup
root = tk.Tk()
root.title("Auto Listing Script - Cyber Tech")
root.geometry("800x650")
root.attributes("-topmost", True)
root.config(bg="#000010")

# make window click-through (optional)
hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
styles = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
ctypes.windll.user32.SetWindowLongW(hwnd, -20, styles | 0x80000 | 0x20)

# Styles
label_font = ("Consolas", 14)
button_font = ("Consolas", 16, "bold")
entry_font = ("Consolas", 14)

def create_neon_label(text, x, y, fg="#2FB858"):
    return tk.Label(root, text=text, font=label_font, fg=fg, bg="#000010")

def create_neon_entry(x, y, width=10):
    ent = tk.Entry(root, font=entry_font, fg="#00FFEE", bg="#101030", insertbackground="#00FFEE", 
                   width=width)
    ent.place(relx=x, rely=y, anchor="w")
    return ent

#title label
title_label = tk.Label(root, width=16, height=10, fg="#00FF95", bg="#000000", 
                        text="Auto Task Script \n Helper", font=("Times New Roman", 25))
title_label.place(relx=0.5, rely=0.1, anchor="center")

# Status Label
status_label = tk.Label(root, width=16, fg="#00FF95", bg="#000000", 
                        text="", font=("Times New Roman", 18))
status_label.place(relx=0.5, rely=0.22, anchor="center")

# Amount Input
amount_label = create_neon_label("Enter amount of products:", 0.15, 0.2)
amount_label.place(relx=0.185, rely=0.29, anchor="w")
amount_entry = create_neon_entry(0.54, 0.29)

apply_color_var = tk.BooleanVar(value=True)  # Checked by default
apply_color_checkbox = tk.Checkbutton(
    root, text="Apply Color Filter", variable=apply_color_var,
    font=("Consolas", 13), fg="#4BEBD5", bg="#000010",
    activebackground="#000010", activeforeground="#00FF95",
    selectcolor="#101030"
)
apply_color_checkbox.place(relx=0.5, rely=0.38, anchor="center")

# Description Label
dsc_label = create_neon_label("", 0.5, 0.55)
dsc_label.place(relx=0.5, rely=0.62, anchor="center")

# Results Text Box
text_output = tk.Text(root, height=6, width=70, font=("Consolas", 12), fg="#00FFEE", bg="#000020", bd=0)
text_output.place(relx=0.5, rely=0.75, anchor="center")
text_output.config(state="disabled")

# Initialize AutoFilter with callbacks
lister = AutoFilter(
    status_callback=lambda msg: dsc_label.config(text=msg, fg="#55FFEE"),
    results_callback=display_results,
    done_callback=lambda: None, 
    should_stop_fn=lambda: should_stop,
    apply_color_fn=lambda: apply_color_var.get()
)

# Main Button
button = tk.Button(
    root, text="Start Automation", command=click_button,
    font=button_font, width=20, height=2, fg="#000010",
    bg="#00FFAA", activebackground="#00DD88", bd=0, highlightthickness=0
)
button.place(relx=0.5, rely=0.47, anchor="center")

# Global hotkey
def on_hotkey():
    if button["state"] != "disabled":
        stop_script()
    else:
        dsc_label.config(text="on cooldown..", fg="#FFAA00")

keyboard.add_hotkey("ctrl+s", on_hotkey)

root.mainloop()
