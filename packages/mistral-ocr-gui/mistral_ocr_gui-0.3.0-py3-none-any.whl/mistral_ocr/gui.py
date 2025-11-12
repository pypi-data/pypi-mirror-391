# mistral_ocr/gui.py
"""
Main GUI application for Mistral OCR processing.
Integrates core logic with a Tkinter interface.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import concurrent.futures
import threading
import queue
import time
from pathlib import Path

# --- Dependency Imports ---
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    TkinterDnD = None

try:
    from mistralai import Mistral
except ImportError:
    Mistral = None

# --- Local Package Imports ---
from .core import (
    process_image_with_ocr, 
    OCR_API_KEY, 
    MAX_WORKERS, 
    SUPPORTED_IMAGE_EXTENSIONS,
    PROCESSING_COLOR,
    PROCESSED_COLOR,
    ERROR_COLOR
)
from .widgets import ProgressBarGrid

# --- GUI Application Class ---
class OcrApp(TkinterDnD.Tk if TkinterDnD else tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mistral OCR Processor")
        self.geometry("800x650")

        # --- Style Configuration ---
        self.style = ttk.Style(self)
        self.style.map('Canceling.TButton',
                       background=[('disabled', 'medium blue')],
                       foreground=[('disabled', 'medium blue')])


        # --- Shared State ---
        self.log_queue = queue.Queue()
        self.cancel_event = threading.Event()
        self.executor = None
        self.processing_thread = None
        self.active_tab_index = 0
        self.status_var = tk.StringVar(value="Ready")

        # --- Individual Images State ---
        self.image_paths = []
        self.ind_progress_bar = None
        self.ind_path_map = {}
        self.ind_start_time = 0
        self.ind_timer_id = None
        self.ind_elapsed_time_var = tk.StringVar(value="0.0s")
        
        # --- Folder State ---
        self.folder_path = ""
        self.folder_image_paths = []
        self.fld_progress_bar = None
        self.fld_path_map = {}
        self.fld_start_time = 0
        self.fld_timer_id = None
        self.fld_elapsed_time_var = tk.StringVar(value="0.0s")
        self.combine_md_var = tk.BooleanVar(value=False)
        self.sort_method_var = tk.StringVar(value="natural")

        # --- Subfolders State ---
        self.subfolders_parent_path = ""
        self.subfolders_to_process = []
        self.subfolder_all_image_paths = []
        self.sub_progress_bar = None
        self.sub_path_map = {}
        self.sub_start_time = 0
        self.sub_timer_id = None
        self.sub_elapsed_time_var = tk.StringVar(value="0.0s")
        self.sub_recursive_var = tk.BooleanVar(value=False)
        self.combine_per_subfolder_var = tk.BooleanVar(value=False)
        self.combine_all_subfolders_var = tk.BooleanVar(value=False)
        self.sub_sort_method_var = tk.StringVar(value="natural")

        self.check_dependencies()
        self.create_widgets()
        if TkinterDnD:
            self.setup_drag_and_drop()
        self.process_log_queue()

    def check_dependencies(self):
        if Mistral is None:
            messagebox.showerror("Dependency Error", "The 'mistralai' package is not installed.\nPlease install it using: pip install mistralai")
            self.destroy()
            sys.exit(1)
        if TkinterDnD is None:
            messagebox.showerror("Dependency Error", "The 'tkinterdnd2' package is not installed.\nPlease install it using: pip install tkinterdnd2")
            self.destroy()
            sys.exit(1)
        if not OCR_API_KEY:
            messagebox.showerror(
                "Configuration Error", 
                "The MISTRAL_API_KEY environment variable is not set.\n\n"
                "Please set it in your system's environment variables and restart the application."
            )
            self.destroy()
            sys.exit(1)
            
    def create_widgets(self):
        # --- Status Bar ---
        # Pack this FIRST, so it reserves its space at the bottom.
        status_bar_frame = ttk.Frame(self, relief=tk.SOLID, padding=(8, 4), borderwidth=0)
        status_bar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_label = ttk.Label(status_bar_frame, textvariable=self.status_var, anchor='w', font=("Terminal", 10))
        status_label.pack(fill=tk.X)

        # --- Main Content ---
        # Now, pack the notebook to fill the REMAINING space.
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text='Individual Images')
        self.create_tab1_widgets()

        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text='Folder')
        self.create_tab2_widgets()

        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text='Subfolders')
        self.create_tab3_widgets()
        
    def _create_progress_section(self, parent, timer_var):
        progress_container = ttk.Frame(parent)
        progress_container.pack(expand=True, fill='both', pady=5, padx=5)

        header_frame = ttk.Frame(progress_container)
        header_frame.pack(fill='x', anchor='w')

        legend_frame = tk.Frame(header_frame)
        legend_frame.pack(side='left', fill='x', pady=5, padx=5)

        SQUARE_LEGEND_SIZE = 12

        # Processing
        tk.Label(legend_frame, text="Processing").grid(row=0, column=0, sticky='w', padx=(0, 5), pady=1)
        frame_yellow = tk.Frame(legend_frame, width=SQUARE_LEGEND_SIZE, height=SQUARE_LEGEND_SIZE, bg=PROCESSING_COLOR, relief='solid', borderwidth=1)
        frame_yellow.grid(row=0, column=1, sticky='w', pady=1)
        frame_yellow.grid_propagate(False)

        # Processed
        tk.Label(legend_frame, text="Processed").grid(row=1, column=0, sticky='w', padx=(0, 5), pady=1)
        frame_green = tk.Frame(legend_frame, width=SQUARE_LEGEND_SIZE, height=SQUARE_LEGEND_SIZE, bg=PROCESSED_COLOR, relief='solid', borderwidth=1)
        frame_green.grid(row=1, column=1, sticky='w', pady=1)
        frame_green.grid_propagate(False)

        # Error occurred
        tk.Label(legend_frame, text="Error occurred").grid(row=2, column=0, sticky='w', padx=(0, 5), pady=1)
        frame_red = tk.Frame(legend_frame, width=SQUARE_LEGEND_SIZE, height=SQUARE_LEGEND_SIZE, bg=ERROR_COLOR, relief='solid', borderwidth=1)
        frame_red.grid(row=2, column=1, sticky='w', pady=1)
        frame_red.grid_propagate(False)

        stopwatch_label = ttk.Label(header_frame, textvariable=timer_var)
        stopwatch_label.pack(side='right', padx=10, anchor='n', pady=5)

        progress_bar = ProgressBarGrid(progress_container)
        progress_bar.pack(expand=True, fill='both')

        return progress_bar

    def create_tab1_widgets(self):
        desc_label = ttk.Label(
            self.tab1,
            text="Process one or more individual image files. Drag and drop files onto the window or use the button.\nEach image will produce a separate markdown file in its original directory.",
            wraplength=770,
            justify=tk.LEFT
        )
        desc_label.pack(side='top', fill='x', pady=(5, 10), padx=7)
        ttk.Separator(self.tab1).pack(fill='x', padx=5, pady=(0, 5))

        controls_frame = ttk.Frame(self.tab1)
        controls_frame.pack(side='top', fill='x', pady=5, padx=5)
        
        self.select_button = ttk.Button(controls_frame, text="Select Images", command=self.select_files)
        self.select_button.pack(side='left', padx=5)

        self.process_button = ttk.Button(controls_frame, text="Process Images", command=self.start_individual_processing, state='disabled')
        self.process_button.pack(side='left', padx=5)

        self.cancel_button = ttk.Button(controls_frame, text="Cancel", command=self.cancel_processing, state='disabled')
        self.cancel_button.pack(side='left', padx=5)
        
        list_frame = ttk.Frame(self.tab1)
        list_frame.pack(fill='x', pady=5, padx=5)
        ttk.Label(list_frame, text="Selected Files:").pack(anchor='w')
        
        self.file_listbox = tk.Listbox(list_frame, height=6)
        self.file_listbox.pack(side='left', fill='x', expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.file_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.file_listbox['yscrollcommand'] = scrollbar.set

        self.ind_progress_bar = self._create_progress_section(self.tab1, self.ind_elapsed_time_var)

    def create_tab2_widgets(self):
        desc_label = ttk.Label(
            self.tab2,
            text="Process all images in a folder. Drag and drop a folder onto the window or use the button.\nOptionally, combine the OCR results into a single markdown file.",
            wraplength=770,
            justify=tk.LEFT
        )
        desc_label.pack(side='top', fill='x', pady=(5, 10), padx=7)
        ttk.Separator(self.tab2).pack(fill='x', padx=5, pady=(0, 5))

        controls_frame = ttk.Frame(self.tab2)
        controls_frame.pack(side='top', fill='x', pady=5, padx=5)
        
        self.folder_select_button = ttk.Button(controls_frame, text="Select Folder", command=self.select_folder)
        self.folder_select_button.pack(side='left', padx=5)

        self.folder_process_button = ttk.Button(controls_frame, text="Process Images", command=self.start_folder_processing, state='disabled')
        self.folder_process_button.pack(side='left', padx=5)

        self.folder_cancel_button = ttk.Button(controls_frame, text="Cancel", command=self.cancel_processing, state='disabled')
        self.folder_cancel_button.pack(side='left', padx=5)
        
        folder_info_frame = ttk.Frame(self.tab2)
        folder_info_frame.pack(fill='x', padx=5, pady=(5, 0))
        ttk.Label(folder_info_frame, text="Selected Folder:").pack(side='left')
        self.folder_path_label = ttk.Label(folder_info_frame, text="None", font=("Helvetica", 9, "italic"), foreground="gray")
        self.folder_path_label.pack(side='left', padx=5)

        self.fld_settings_frame = ttk.LabelFrame(self.tab2, text="Settings", padding=10)
        self.fld_settings_frame.pack(fill='x', padx=5, pady=10)
        
        combine_check = ttk.Checkbutton(
            self.fld_settings_frame, text="Create a combined markdown file", variable=self.combine_md_var, command=self.toggle_folder_sort_options
        )
        combine_check.grid(row=0, column=0, sticky='w')

        self.sort_options_frame = ttk.Frame(self.fld_settings_frame)
        self.sort_options_frame.grid(row=1, column=0, columnspan=2, sticky='w', padx=20, pady=5)

        ttk.Radiobutton(self.sort_options_frame, text="Natural Sort (e.g., img1, img2, img10)", variable=self.sort_method_var, value="natural").pack(anchor='w')
        ttk.Radiobutton(self.sort_options_frame, text="Reverse Natural Sort", variable=self.sort_method_var, value="reverse_natural").pack(anchor='w')
        ttk.Radiobutton(self.sort_options_frame, text="Date Modified (Newest to Oldest)", variable=self.sort_method_var, value="mtime_desc").pack(anchor='w')
        ttk.Radiobutton(self.sort_options_frame, text="Date Modified (Oldest to Newest)", variable=self.sort_method_var, value="mtime_asc").pack(anchor='w')

        self.fld_progress_bar = self._create_progress_section(self.tab2, self.fld_elapsed_time_var)
        self.toggle_folder_sort_options()

    def create_tab3_widgets(self):
        desc_label = ttk.Label(
            self.tab3,
            text="Process images in subfolders. Drag and drop a parent folder or use the button.\nUse the 'Recursive' option to process all subfolders at any depth. Optionally, combine results per subfolder and create a final compilation.",
            wraplength=770,
            justify=tk.LEFT
        )
        desc_label.pack(side='top', fill='x', pady=(5, 10), padx=7)
        ttk.Separator(self.tab3).pack(fill='x', padx=5, pady=(0, 5))

        controls_frame = ttk.Frame(self.tab3)
        controls_frame.pack(side='top', fill='x', pady=5, padx=5)
        
        self.subfolder_select_button = ttk.Button(controls_frame, text="Select Parent Folder", command=self.select_parent_folder)
        self.subfolder_select_button.pack(side='left', padx=5)

        self.subfolder_process_button = ttk.Button(controls_frame, text="Process Subfolders", command=self.start_subfolder_processing, state='disabled')
        self.subfolder_process_button.pack(side='left', padx=5)

        self.subfolder_cancel_button = ttk.Button(controls_frame, text="Cancel", command=self.cancel_processing, state='disabled')
        self.subfolder_cancel_button.pack(side='left', padx=5)

        folder_info_frame = ttk.Frame(self.tab3)
        folder_info_frame.pack(fill='x', padx=5, pady=(5, 0))
        ttk.Label(folder_info_frame, text="Selected Parent Folder:").pack(side='left')
        self.subfolder_path_label = ttk.Label(folder_info_frame, text="None", font=("Helvetica", 9, "italic"), foreground="gray")
        self.subfolder_path_label.pack(side='left', padx=5)

        self.sub_settings_frame = ttk.LabelFrame(self.tab3, text="Settings", padding=10)
        self.sub_settings_frame.pack(fill='x', padx=5, pady=10)
        
        recursive_check = ttk.Checkbutton(
            self.sub_settings_frame, text="Recursive (process all nested subfolders)", variable=self.sub_recursive_var, command=self.update_subfolder_view_if_path_exists
        )
        recursive_check.grid(row=0, column=0, sticky='w', pady=(0, 5))

        combine_per_sub_check = ttk.Checkbutton(
            self.sub_settings_frame, text="Create a combined markdown file for each subfolder", variable=self.combine_per_subfolder_var, command=self.toggle_subfolder_options
        )
        combine_per_sub_check.grid(row=1, column=0, sticky='w')

        self.sub_sort_options_frame = ttk.Frame(self.sub_settings_frame)
        self.sub_sort_options_frame.grid(row=2, column=0, columnspan=2, sticky='w', padx=20, pady=5)
        
        ttk.Radiobutton(self.sub_sort_options_frame, text="Natural Sort (e.g., img1, img2, img10)", variable=self.sub_sort_method_var, value="natural").pack(anchor='w')
        ttk.Radiobutton(self.sub_sort_options_frame, text="Reverse Natural Sort", variable=self.sub_sort_method_var, value="reverse_natural").pack(anchor='w')
        ttk.Radiobutton(self.sub_sort_options_frame, text="Date Modified (Newest to Oldest)", variable=self.sub_sort_method_var, value="mtime_desc").pack(anchor='w')
        ttk.Radiobutton(self.sub_sort_options_frame, text="Date Modified (Oldest to Newest)", variable=self.sub_sort_method_var, value="mtime_asc").pack(anchor='w')
        
        self.combine_all_check = ttk.Checkbutton(
            self.sub_settings_frame, text="Create a combined markdown file of all subfolders", variable=self.combine_all_subfolders_var
        )
        self.combine_all_check.grid(row=3, column=0, sticky='w', pady=(5,0))

        self.sub_progress_bar = self._create_progress_section(self.tab3, self.sub_elapsed_time_var)
        self.toggle_subfolder_options()

    def _set_widget_state_recursive(self, parent_widget, state):
            """Recursively sets the state of all child widgets."""
            for child in parent_widget.winfo_children():
                try:
                    # This works for most ttk widgets (buttons, checkbuttons, etc.).
                    child.configure(state=state)
                except tk.TclError:
                    # If it fails, it might be a container like a Frame.
                    # Recurse into it to affect its children.
                    self._set_widget_state_recursive(child, state)

    def setup_drag_and_drop(self):
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)

    def handle_drop(self, event):
        # Allow drop if not processing, OR if we are in the "canceling" state.
        if self.processing_thread and self.processing_thread.is_alive() and not self.cancel_event.is_set():
            return

        try:
            paths = self.tk.splitlist(event.data)
        except tk.TclError:
            paths = event.data.strip().split('\n')

        if not paths:
            return

        current_tab_index = self.notebook.index(self.notebook.select())

        if current_tab_index == 0:  # Individual Images
            image_files = [p for p in paths if os.path.isfile(p) and p.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS)]
            if image_files:
                self._load_individual_images(image_files)
        elif current_tab_index == 1:  # Folder
            folder_path = paths[0]
            if os.path.isdir(folder_path):
                self._load_folder(folder_path)
        elif current_tab_index == 2:  # Subfolders
            parent_folder_path = paths[0]
            if os.path.isdir(parent_folder_path):
                self._load_parent_folder(parent_folder_path)

    def toggle_folder_sort_options(self):
        state = 'normal' if self.combine_md_var.get() else 'disabled'
        for child in self.sort_options_frame.winfo_children():
            child.configure(state=state)

    def toggle_subfolder_options(self):
        is_per_sub_enabled = self.combine_per_subfolder_var.get()
        sort_state = 'normal' if is_per_sub_enabled else 'disabled'
        all_state = 'normal' if is_per_sub_enabled else 'disabled'
        
        for child in self.sub_sort_options_frame.winfo_children():
            child.configure(state=sort_state)
        
        self.combine_all_check.configure(state=all_state)
        if not is_per_sub_enabled:
            self.combine_all_subfolders_var.set(False)

    def _load_individual_images(self, paths):
        self.image_paths = list(paths)
        self.file_listbox.delete(0, tk.END)
        for path in self.image_paths:
            self.file_listbox.insert(tk.END, os.path.basename(path))
        
        # Only enable the process button if nothing is currently processing/canceling
        if not (self.processing_thread and self.processing_thread.is_alive()):
            self.process_button.config(state='normal')
            
        self.ind_progress_bar.setup_grid(len(self.image_paths))
        self.status_var.set(f"{len(self.image_paths)} file(s) loaded.")

    def select_files(self):
        file_types = [("Image files", " ".join([f"*{ext}" for ext in SUPPORTED_IMAGE_EXTENSIONS])), ("All files", "*.*")]
        paths = filedialog.askopenfilenames(title="Select one or more images for OCR", filetypes=file_types)
        if paths:
            self._load_individual_images(paths)

    def start_individual_processing(self):
        if not self.image_paths:
            messagebox.showwarning("No Files", "Please select images to process first.")
            return

        self.active_tab_index = 0
        self.set_ui_state(is_processing=True, active_tab_index=self.active_tab_index)
        
        self.ind_path_map = {path: i for i, path in enumerate(self.image_paths)}
        self.ind_progress_bar.setup_grid(len(self.image_paths))
        
        self.cancel_event.clear()
        
        self.ind_start_time = time.time()
        self.ind_elapsed_time_var.set("0.0s")
        self.update_individual_stopwatch()

        self.processing_thread = threading.Thread(target=self.run_individual_processing_logic, daemon=True)
        self.processing_thread.start()
        
    def run_individual_processing_logic(self):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
        futures = {self.executor.submit(process_image_with_ocr, path, self.log_queue, self.cancel_event) for path in self.image_paths}

        try:
            concurrent.futures.wait(futures)
        finally:
            self.executor.shutdown(wait=True)
            self.executor = None
            self.after(0, self.set_ui_state, False, self.active_tab_index)

    def update_individual_stopwatch(self):
        elapsed = time.time() - self.ind_start_time
        self.ind_elapsed_time_var.set(f"{elapsed:.1f}s")
        self.ind_timer_id = self.after(100, self.update_individual_stopwatch)

    def _load_folder(self, path):
        self.folder_path = path
        try:
            self.folder_image_paths = sorted([os.path.join(self.folder_path, f) for f in os.listdir(self.folder_path)
                                              if f.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS)])
        except OSError as e:
            messagebox.showerror("Error", f"Error accessing folder: {e}")
            self.folder_image_paths = []

        self.folder_path_label.config(text=self.folder_path, foreground="black")
        
        if self.folder_image_paths:
            self.status_var.set(f"Folder loaded. Found {len(self.folder_image_paths)} image(s).")
            # Only enable the process button if nothing is currently processing/canceling
            if not (self.processing_thread and self.processing_thread.is_alive()):
                self.folder_process_button.config(state='normal')
        else:
            self.status_var.set("Folder loaded. Found 0 images.")
            self.folder_process_button.config(state='disabled')
        self.fld_progress_bar.setup_grid(len(self.folder_image_paths))

    def select_folder(self):
        path = filedialog.askdirectory(title="Select a folder containing images")
        if path:
            self._load_folder(path)

    def start_folder_processing(self):
        if not self.folder_image_paths:
            messagebox.showwarning("No Images", "The selected folder contains no supported images to process.")
            return

        self.active_tab_index = 1
        self.set_ui_state(is_processing=True, active_tab_index=self.active_tab_index)

        self.fld_path_map = {path: i for i, path in enumerate(self.folder_image_paths)}
        self.fld_progress_bar.setup_grid(len(self.folder_image_paths))

        self.cancel_event.clear()
        
        self.fld_start_time = time.time()
        self.fld_elapsed_time_var.set("0.0s")
        self.update_folder_stopwatch()

        self.processing_thread = threading.Thread(target=self.run_folder_processing_logic, daemon=True)
        self.processing_thread.start()

    def run_folder_processing_logic(self):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
        futures = {self.executor.submit(process_image_with_ocr, path, self.log_queue, self.cancel_event) for path in self.folder_image_paths}
        
        processed_md_files = []
        try:
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    processed_md_files.append(result)
            
            if not self.cancel_event.is_set():
                if self.combine_md_var.get() and processed_md_files:
                    folder_name = os.path.basename(self.folder_path)
                    output_filename = f"Combined_OCR_{folder_name}.md"
                    output_path = os.path.join(self.folder_path, output_filename)
                    self._combine_markdown_files(processed_md_files, output_path, self.sort_method_var.get())
        
        finally:
            self.executor.shutdown(wait=True)
            self.executor = None
            self.after(0, self.set_ui_state, False, self.active_tab_index)
            
    def _combine_markdown_files(self, md_files, output_path, sort_method):
        def natural_sort_key(s):
            return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', os.path.basename(s))]

        try:
            if sort_method == "natural":
                md_files.sort(key=natural_sort_key)
            elif sort_method == "reverse_natural":
                md_files.sort(key=natural_sort_key, reverse=True)
            elif sort_method == "mtime_desc":
                md_files.sort(key=os.path.getmtime, reverse=True)
            elif sort_method == "mtime_asc":
                md_files.sort(key=os.path.getmtime)
            
            combined_content = []
            for md_file in md_files:
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        combined_content.append(f.read().strip())
                except Exception:
                    pass

            if not combined_content:
                return
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n\n".join(combined_content))
                
        except Exception as e:
            messagebox.showerror("Combine Error", f"Error combining files: {e}")

    def update_folder_stopwatch(self):
        elapsed = time.time() - self.fld_start_time
        self.fld_elapsed_time_var.set(f"{elapsed:.1f}s")
        self.fld_timer_id = self.after(100, self.update_folder_stopwatch)
    
    def update_subfolder_view_if_path_exists(self):
        if self.subfolders_parent_path:
            self._load_parent_folder(self.subfolders_parent_path)

    def _load_parent_folder(self, path):
        self.subfolders_parent_path = path
        self.subfolders_to_process = []
        self.subfolder_all_image_paths = []

        def natural_sort_key(s):
            return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

        try:
            if self.sub_recursive_var.get():
                # Recursive search
                all_dirs_with_images = []
                for dirpath, _, filenames in os.walk(path):
                    images = [os.path.join(dirpath, f) for f in filenames if f.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS)]
                    if images:
                        all_dirs_with_images.append(dirpath)
                        self.subfolder_all_image_paths.extend(images)
                
                all_dirs_with_images.sort(key=natural_sort_key)
                self.subfolders_to_process = all_dirs_with_images
            else:
                # Non-recursive (immediate subfolders only)
                subfolders = [d.path for d in os.scandir(path) if d.is_dir()]
                subfolders.sort(key=natural_sort_key)
                
                for sub_path in subfolders:
                    try:
                        images = [os.path.join(sub_path, f) for f in os.listdir(sub_path) if f.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS)]
                        if images:
                            self.subfolders_to_process.append(sub_path)
                            self.subfolder_all_image_paths.extend(images)
                    except OSError:
                        pass
        except OSError as e:
            messagebox.showerror("Error", f"Error accessing folder: {e}")
            self.subfolders_to_process = []
            self.subfolder_all_image_paths = []

        self.subfolder_path_label.config(text=self.subfolders_parent_path, foreground="black")

        if self.subfolder_all_image_paths:
            num_folders = len(self.subfolders_to_process)
            folder_text = "folders" if num_folders != 1 else "folder"
            self.status_var.set(f"Parent folder loaded. Found {len(self.subfolder_all_image_paths)} image(s) in {num_folders} sub-{folder_text}.")
            if not (self.processing_thread and self.processing_thread.is_alive()):
                self.subfolder_process_button.config(state='normal')
        else:
            self.status_var.set("Parent folder loaded. Found 0 images.")
            self.subfolder_process_button.config(state='disabled')
        
        self.sub_progress_bar.setup_grid(len(self.subfolder_all_image_paths))

    def select_parent_folder(self):
        path = filedialog.askdirectory(title="Select a parent folder containing subfolders with images")
        if path:
            self._load_parent_folder(path)
    
    def start_subfolder_processing(self):
        if not self.subfolder_all_image_paths:
            messagebox.showwarning("No Images Found", "No supported images were found in any subfolders to process.")
            return

        self.active_tab_index = 2
        self.set_ui_state(is_processing=True, active_tab_index=self.active_tab_index)
        
        self.sub_path_map = {path: i for i, path in enumerate(self.subfolder_all_image_paths)}
        self.sub_progress_bar.setup_grid(len(self.subfolder_all_image_paths))

        self.cancel_event.clear()

        self.sub_start_time = time.time()
        self.sub_elapsed_time_var.set("0.0s")
        self.update_subfolder_stopwatch()
        
        self.processing_thread = threading.Thread(target=self.run_subfolder_processing_logic, args=(self.subfolder_all_image_paths,), daemon=True)
        self.processing_thread.start()

    def run_subfolder_processing_logic(self, all_image_paths):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
        future_to_path = {self.executor.submit(process_image_with_ocr, path, self.log_queue, self.cancel_event): path for path in all_image_paths}
        
        processed_md_by_subfolder = {sub_path: [] for sub_path in self.subfolders_to_process}
        
        try:
            for future in concurrent.futures.as_completed(future_to_path):
                result_md_path = future.result()
                if result_md_path:
                    parent_dir = os.path.dirname(result_md_path)
                    if parent_dir in processed_md_by_subfolder:
                        processed_md_by_subfolder[parent_dir].append(result_md_path)

            if self.cancel_event.is_set():
                return

            subfolder_combined_mds = []
            if self.combine_per_subfolder_var.get():
                # self.subfolders_to_process is already sorted from _load_parent_folder
                for sub_path in self.subfolders_to_process:
                    md_files = processed_md_by_subfolder.get(sub_path, [])
                    if not md_files: continue
                    sub_name = os.path.basename(sub_path)
                    output_filename = f"Combined_OCR_{sub_name}.md"
                    output_path = os.path.join(self.subfolders_parent_path, output_filename)
                    self._combine_markdown_files(md_files, output_path, self.sub_sort_method_var.get())
                    subfolder_combined_mds.append(output_path)
            
            if self.combine_all_subfolders_var.get() and subfolder_combined_mds:
                # The list is already correctly ordered because it was built from the pre-sorted
                # self.subfolders_to_process list. No need for an additional sort here.
                all_content = []
                for md_path in subfolder_combined_mds:
                    try:
                        with open(md_path, 'r', encoding='utf-8') as f:
                            all_content.append(f.read())
                    except Exception:
                        pass

                if all_content:
                    parent_folder_name = os.path.basename(self.subfolders_parent_path)
                    final_output_name = f"{parent_folder_name}_OCR_Compilation.md"
                    final_output_path = os.path.join(self.subfolders_parent_path, final_output_name)
                    
                    with open(final_output_path, 'w', encoding='utf-8') as f:
                        f.write("\n\n---\n\n".join(all_content))
        finally:
            self.executor.shutdown(wait=True)
            self.executor = None
            self.after(0, self.set_ui_state, False, self.active_tab_index)

    def update_subfolder_stopwatch(self):
        elapsed = time.time() - self.sub_start_time
        self.sub_elapsed_time_var.set(f"{elapsed:.1f}s")
        self.sub_timer_id = self.after(100, self.update_subfolder_stopwatch)

    def cancel_processing(self):
        if self.processing_thread and self.processing_thread.is_alive():
            self.status_var.set("Cancelling...")
            # Signal the thread to stop
            self.cancel_event.set()

            # --- Immediately update UI to show "canceling" state ---
            active_button = None
            if self.active_tab_index == 0:
                if self.ind_timer_id:
                    self.after_cancel(self.ind_timer_id)
                    self.ind_timer_id = None
                self.ind_elapsed_time_var.set("0.0s")
                active_button = self.cancel_button
            elif self.active_tab_index == 1:
                if self.fld_timer_id:
                    self.after_cancel(self.fld_timer_id)
                    self.fld_timer_id = None
                self.fld_elapsed_time_var.set("0.0s")
                active_button = self.folder_cancel_button
            elif self.active_tab_index == 2:
                if self.sub_timer_id:
                    self.after_cancel(self.sub_timer_id)
                    self.sub_timer_id = None
                self.sub_elapsed_time_var.set("0.0s")
                active_button = self.subfolder_cancel_button
            
            if active_button:
                active_button.config(text='Canceling...', style='Canceling.TButton', state='disabled')

            # --- Immediately re-enable selection and settings ---
            self.select_button.config(state='normal')
            self.folder_select_button.config(state='normal')
            self.subfolder_select_button.config(state='normal')

            self._set_widget_state_recursive(self.fld_settings_frame, 'normal')
            self._set_widget_state_recursive(self.sub_settings_frame, 'normal')
            self.toggle_folder_sort_options()
            self.toggle_subfolder_options()

    def set_ui_state(self, is_processing, active_tab_index=0):
        if is_processing:
            self.status_var.set("Processing Files...")
            # --- Disable UI for processing ---
            self.select_button.config(state='disabled')
            self.process_button.config(state='disabled')
            self.folder_select_button.config(state='disabled')
            self.folder_process_button.config(state='disabled')
            self.subfolder_select_button.config(state='disabled')
            self.subfolder_process_button.config(state='disabled')
            
            self._set_widget_state_recursive(self.fld_settings_frame, 'disabled')
            self._set_widget_state_recursive(self.sub_settings_frame, 'disabled')
            
            if active_tab_index == 0: self.cancel_button.config(state='normal', text='Cancel')
            elif active_tab_index == 1: self.folder_cancel_button.config(state='normal', text='Cancel')
            elif active_tab_index == 2: self.subfolder_cancel_button.config(state='normal', text='Cancel')

            for i in range(len(self.notebook.tabs())):
                if i != active_tab_index:
                    self.notebook.tab(i, state="disabled")
        else:
            # --- Re-enable UI after processing/cancellation is complete ---
            if self.ind_timer_id:
                self.after_cancel(self.ind_timer_id)
                self.ind_timer_id = None
            if self.fld_timer_id:
                self.after_cancel(self.fld_timer_id)
                self.fld_timer_id = None
            if self.sub_timer_id:
                self.after_cancel(self.sub_timer_id)
                self.sub_timer_id = None

            if self.cancel_event.is_set():
                self.status_var.set("Process Canceled")
                if active_tab_index == 0:
                    self.ind_progress_bar.setup_grid(len(self.ind_progress_bar.square_ids))
                elif active_tab_index == 1:
                    self.fld_progress_bar.setup_grid(len(self.fld_progress_bar.square_ids))
                elif active_tab_index == 2:
                    self.sub_progress_bar.setup_grid(len(self.sub_progress_bar.square_ids))
            else:
                self.status_var.set("Files Processed")

            # Re-enable all controls now that the thread is finished.
            self.select_button.config(state='normal')
            self.process_button.config(state='normal' if self.image_paths else 'disabled')
            self.cancel_button.config(state='disabled', text='Cancel', style='TButton')
            
            self.folder_select_button.config(state='normal')
            self.folder_process_button.config(state='normal' if self.folder_image_paths else 'disabled')
            self.folder_cancel_button.config(state='disabled', text='Cancel', style='TButton')

            self.subfolder_select_button.config(state='normal')
            self.subfolder_process_button.config(state='normal' if self.subfolder_all_image_paths else 'disabled')
            self.subfolder_cancel_button.config(state='disabled', text='Cancel', style='TButton')

            self._set_widget_state_recursive(self.fld_settings_frame, 'normal')
            self._set_widget_state_recursive(self.sub_settings_frame, 'normal')
            self.toggle_folder_sort_options()
            self.toggle_subfolder_options()

            for i in range(len(self.notebook.tabs())):
                self.notebook.tab(i, state="normal")

    def process_log_queue(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                if isinstance(message, tuple) and len(message) == 3 and message[0] == 'status_update':
                    _, path, status = message
                    
                    progress_bar = None
                    path_map = None

                    if self.active_tab_index == 0:
                        progress_bar, path_map = self.ind_progress_bar, self.ind_path_map
                    elif self.active_tab_index == 1:
                        progress_bar, path_map = self.fld_progress_bar, self.fld_path_map
                    elif self.active_tab_index == 2:
                        progress_bar, path_map = self.sub_progress_bar, self.sub_path_map

                    if progress_bar and path_map and path in path_map:
                        index = path_map[path]
                        color_map = {'processing': PROCESSING_COLOR, 'success': PROCESSED_COLOR, 'error': ERROR_COLOR}
                        color = color_map.get(status, 'white')
                        progress_bar.update_square(index, color)
        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_log_queue)

    def on_closing(self):
        if self.processing_thread and self.processing_thread.is_alive():
            if messagebox.askyesno("Exit", "Processing is active. Are you sure you want to exit?"):
                self.cancel_event.set()
                if self.executor:
                    self.executor.shutdown(wait=False, cancel_futures=True)
                self.destroy()
        else:
            self.destroy()

def main():
    """The main entry point for the GUI application."""
    app = OcrApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()