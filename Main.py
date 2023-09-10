# -----------------------
# Import Necessary Libraries
# -----------------------
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
from bs4 import BeautifulSoup
import subprocess
import os
import re
import webbrowser
import threading

# -----------------------
# Utility Functions
# -----------------------
def get_workshop_ids_from_collection(collection_url):
    """Fetch workshop IDs from the provided collection URL."""
    response = requests.get(collection_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    mod_links = soup.find_all('div', class_='workshopItem')
    return [link.find('a', href=True)['href'].split('id=')[-1] for link in mod_links]

def get_game_id_from_mod(mod_url):
    """Fetch game ID from the provided mod URL."""
    response = requests.get(mod_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    breadcrumbs_div = soup.find('div', class_='breadcrumbs')
    if breadcrumbs_div:
        game_link = breadcrumbs_div.find('a', href=True)
        if game_link:
            match = re.search(r'/app/(\d+)', game_link['href'])
            if match:
                return match.group(1)
    return None

def get_game_id_from_collection(collection_url):
    """Fetch game ID from the provided collection URL."""
    response = requests.get(collection_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    game_id_tag = soup.find('span', class_='workshopItemAuthorName').find('a', href=True)
    if game_id_tag:
        match = re.search(r'appid=(\d+)', game_id_tag['href'])
        if match:
            return match.group(1)
    return None

def download_mod(steamcmd_path, game_id, workshop_id):
    script_path = os.path.join(os.getcwd(), "temp_steamcmd_script.txt")
    with open(script_path, "w") as f:
        f.write("login anonymous\n")
        f.write("workshop_download_item {} {}\n".format(game_id, workshop_id))
        f.write("quit\n")
    cmd = "{} +runscript {}".format(steamcmd_path, script_path)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    os.remove(script_path)
    if "Success. Downloaded item" in result.stdout:
        write_to_console(f"Successfully downloaded mod with ID: {workshop_id}")
    elif "ERROR! Download item" in result.stdout:
        error_message = result.stdout.split("ERROR!")[1].strip()  # Extract the error message
        write_to_console(f"Failed to download mod with ID: {workshop_id}. Reason: {error_message}")
    else:
        write_to_console(f"Unexpected output for mod with ID: {workshop_id}. Please check manually.")
    return "Success. Downloaded item" in result.stdout



# -----------------------
# GUI-related Functions
# -----------------------
def write_to_console(message):
    """Write the given message to the UI console."""
    console_output.insert(tk.END, message + "\n")
    console_output.see(tk.END)
    root.update()

def threaded_start_download():
    """Start the download process in a separate thread."""
    disable_ui_elements()
    download_thread = threading.Thread(target=start_download)
    download_thread.start()

    # Start checking the thread status
    check_thread_status(download_thread)

def check_thread_status(thread):
    """Check the status of the given thread and re-enable UI elements if it's not running."""
    if not thread.is_alive():
        enable_ui_elements()
    else:
        root.after(1000, check_thread_status, thread)

def disable_ui_elements():
    """Disable all UI elements."""
    link_entry.config(state=tk.DISABLED)
    load_button.config(state=tk.DISABLED)
    game_id_entry.config(state=tk.DISABLED)
    start_button.config(state=tk.DISABLED)
    browse_button.config(state=tk.DISABLED)
    steamcmd_path_entry.config(state=tk.DISABLED)
    delete_button.config(state=tk.DISABLED)
    add_button.config(state=tk.DISABLED)
    add_from_file_button.config(state=tk.DISABLED)

def enable_ui_elements():
    """Enable all UI elements."""
    link_entry.config(state=tk.NORMAL)
    load_button.config(state=tk.NORMAL)
    game_id_entry.config(state=tk.NORMAL)
    start_button.config(state=tk.NORMAL)
    browse_button.config(state=tk.NORMAL)
    steamcmd_path_entry.config(state=tk.NORMAL)
    delete_button.config(state=tk.NORMAL)
    add_button.config(state=tk.NORMAL)
    add_from_file_button.config(state=tk.NORMAL)

def add_from_file():
    """Add mods from a provided text file."""
    filepath = filedialog.askopenfilename(title="Select a text file", filetypes=[("Text files", "*.txt")])
    if not filepath:
        return
    with open(filepath, 'r') as file:
        lines = file.readlines()
    for line in lines:
        if "https://steamcommunity.com/sharedfiles/filedetails/?id=" in line:
            mod_id = line.split('id=')[-1].split('&')[0].strip()  # Split at '&' and take the first part
            mod_ids_listbox.insert(tk.END, mod_id)
            game_id = get_game_id_from_mod(line.strip())
            if game_id:
                game_id_entry.delete(0, tk.END)
                game_id_entry.insert(0, game_id)

def start_download():
    """Start the mod download process."""
    collection_url = link_entry.get()
    game_id = game_id_entry.get()
    steamcmd_path = steamcmd_path_entry.get()
    if not os.path.basename(steamcmd_path).lower() == "steamcmd.exe":
        messagebox.showerror("Error", "The provided path does not point to steamcmd.exe.")
        return
    if not game_id or not steamcmd_path:
        messagebox.showerror("Error", "Please fill in all the fields.")
        return
    workshop_ids = list(mod_ids_listbox.get(0, tk.END))
    if not workshop_ids:
        write_to_console("Error: No mod IDs provided. Please add mod links first.")
        enable_ui_elements()  # Re-enable the UI since there's nothing to download
        return

    progress_bar['maximum'] = len(workshop_ids)
    progress_bar['value'] = 0
    for index, workshop_id in enumerate(workshop_ids):
        success = download_mod(steamcmd_path, game_id, workshop_id)
        if success:
            mod_ids_listbox.itemconfig(index, {'bg': 'green'})
        else:
            mod_ids_listbox.itemconfig(index, {'bg': 'red'})
        progress_bar['value'] += 1
        root.update()

def browse_steamcmd():
    """Open a file dialog to select steamcmd.exe."""
    filepath = filedialog.askopenfilename(title="Select steamcmd.exe", filetypes=[("Executable", "*.exe")])
    if filepath:
        steamcmd_path_entry.delete(0, tk.END)
        steamcmd_path_entry.insert(0, filepath)

def delete_selected_entry():
    """Delete the selected entry from the listbox."""
    selected_index = mod_ids_listbox.curselection()
    if selected_index:
        mod_ids_listbox.delete(selected_index)

def add_from_link_dialog():
    """Open a dialog to add a mod from a provided link."""
    dialog = tk.Toplevel(root)
    dialog.title("Add Mod from Link")
    label = ttk.Label(dialog, text="Enter the mod link:")
    label.pack(pady=10, padx=10)
    link_entry_dialog = ttk.Entry(dialog, width=50)
    link_entry_dialog.pack(pady=10, padx=10)

    def add_link():
        link = link_entry_dialog.get()
        mod_id = link.split('id=')[-1].split('&')[0]  # Split at '&' and take the first part
        mod_ids_listbox.insert(tk.END, mod_id)
        game_id = get_game_id_from_mod(link)
        if game_id:
            game_id_entry.delete(0, tk.END)
            game_id_entry.insert(0, game_id)
        dialog.destroy()

    ok_button = ttk.Button(dialog, text="OK", command=add_link)
    ok_button.pack(pady=10)

def populate_mod_ids(event=None):
    """Populate the listbox with mod IDs from the provided collection link."""
    collection_url = link_entry.get()
    if not collection_url.strip():
        write_to_console("Error: Please provide a mod collection link before pressing 'Load'.")
        return
    workshop_ids = get_workshop_ids_from_collection(collection_url)
    mod_ids_listbox.delete(0, tk.END)
    for workshop_id in workshop_ids:
        mod_ids_listbox.insert(tk.END, workshop_id)
    game_id = get_game_id_from_collection(collection_url)
    if game_id:
        game_id_entry.delete(0, tk.END)
        game_id_entry.insert(0, game_id)

def reset_program():
    """Reset all UI elements and variables to their initial state."""
    link_entry.delete(0, tk.END)
    game_id_entry.delete(0, tk.END)
    mod_ids_listbox.delete(0, tk.END)
    console_output.delete(1.0, tk.END)
    progress_bar['value'] = 0
    enable_ui_elements()

def open_mod_page(event):
    """Open the mod page in the default web browser."""
    selected_mod_id = mod_ids_listbox.get(mod_ids_listbox.curselection())
    mod_page_url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={selected_mod_id}"
    webbrowser.open(mod_page_url)

# -----------------------
# Main GUI Layout
# -----------------------
root = tk.Tk()
root.title("Steam Workshop Downloader")

# Create and configure widgets
# Labels
link_label = ttk.Label(root, text="Enter the mod collection link:")
game_id_label = ttk.Label(root, text="Enter the game ID:")
steamcmd_path_label = ttk.Label(root, text="Path to steamcmd.exe:")
console_label = ttk.Label(root, text="Console Output:")

# Entries
link_entry = ttk.Entry(root, width=50)
game_id_entry = ttk.Entry(root, width=50)
steamcmd_path_entry = ttk.Entry(root, width=40)

# Buttons
load_button = ttk.Button(root, text="Load", command=populate_mod_ids)
browse_button = ttk.Button(root, text="Browse", command=browse_steamcmd)
start_button = ttk.Button(root, text="Start Download", command=threaded_start_download)
reset_button = ttk.Button(root, text="Reset", command=reset_program)
delete_button = ttk.Button(root, text="Delete Selected", command=delete_selected_entry)
add_button = ttk.Button(root, text="Add from Link", command=add_from_link_dialog)
add_from_file_button = ttk.Button(root, text="Add from File", command=add_from_file)

# Listbox and Scrollbar
mod_ids_listbox = tk.Listbox(root, width=50, height=20)

# Text and Progressbar
console_output = tk.Text(root, width=70, height=10, wrap=tk.WORD)
progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='determinate')

# Scrollbar
scrollbar = ttk.Scrollbar(root, command=console_output.yview)
console_output.config(yscrollcommand=scrollbar.set)

# Bind events to widgets
link_entry.bind('<Return>', populate_mod_ids)
mod_ids_listbox.bind('<Double-Button-1>', open_mod_page)

# Place widgets on the grid
link_label.grid(row=0, column=0, pady=10, sticky=tk.W, padx=10)
link_entry.grid(row=1, column=0, pady=10, padx=10, columnspan=2, sticky=tk.W+tk.E)
load_button.grid(row=2, column=0, pady=10, columnspan=2)

game_id_label.grid(row=3, column=0, pady=10, sticky=tk.W, padx=10)
game_id_entry.grid(row=4, column=0, pady=10, padx=10, columnspan=2, sticky=tk.W+tk.E)

steamcmd_path_label.grid(row=5, column=0, pady=10, sticky=tk.W, padx=10)
steamcmd_path_entry.grid(row=6, column=0, pady=10, padx=10, sticky=tk.W+tk.E)
browse_button.grid(row=6, column=1, pady=10)

mod_ids_listbox.grid(row=7, column=0, pady=10, padx=10, sticky=tk.W+tk.E, rowspan=3)
delete_button.grid(row=7, column=1, pady=10, padx=5, sticky=tk.N)
add_button.grid(row=8, column=1, pady=10, padx=5, sticky=tk.N)
add_from_file_button.grid(row=9, column=1, columnspan=2, pady=10)

progress_bar.grid(row=11, column=0, pady=20, padx=10, columnspan=2, sticky=tk.W+tk.E)
start_button.grid(row=12, column=0, pady=20, columnspan=2)

console_label.grid(row=13, column=0, pady=10, sticky=tk.W, padx=10)
console_output.grid(row=14, column=0, pady=10, padx=10, columnspan=2, sticky=tk.W+tk.E)
scrollbar.grid(row=14, column=2, pady=10, sticky=tk.N+tk.S)

reset_button.grid(row=15, column=0, pady=20, columnspan=2)

root.mainloop()
