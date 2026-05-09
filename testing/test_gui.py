#!/usr/bin/env python3
"""
BitRAG Testing GUI Application

A tkinter-based GUI for running indexing and inference tests.

Usage:
    python test_gui.py
"""

import os
import sys
import subprocess
import threading
from pathlib import Path
from typing import Optional

# Add src to path
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Use the directory where test_gui.py is located as project root
_PROJECT_ROOT = _SCRIPT_DIR
_SRC_PATH = os.path.join(_PROJECT_ROOT, 'src')

# Remove any conflicting paths first
if '' in sys.path:
    sys.path.remove('')
if _PROJECT_ROOT in sys.path:
    sys.path.remove(_PROJECT_ROOT)

sys.path.insert(0, _SRC_PATH)

# Get the correct Python executable with correct PYTHONPATH
def get_python_path():
    """Get Python path from venv or .venv."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Check venv first (it has the required packages like llama_index)
    if (Path(script_dir) / "venv/bin/python").exists():
        return os.path.abspath(str(Path(script_dir) / "venv/bin/python"))
    # Then check .venv
    if (Path(script_dir) / ".venv/bin/python").exists():
        return os.path.abspath(str(Path(script_dir) / ".venv/bin/python"))
    # Fall back to python3
    return "python3"

def get_python_env():
    """Get environment with correct PYTHONPATH and CPU-only mode."""
    env = os.environ.copy()
    # Remove any conflicting PYTHONPATH
    env.pop('PYTHONPATH', None)
    # Set new PYTHONPATH
    env["PYTHONPATH"] = _SRC_PATH
    # Force CPU-only mode (disable CUDA GPU)
    env["CUDA_VISIBLE_DEVICES"] = ""
    return env

_PYTHON_PATH = get_python_path()

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
except ImportError:
    print("tkinter not available. Please install tkinter.")
    sys.exit(1)


class BitRAGTestGUI:
    """Main GUI Application for BitRAG Testing."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("BitRAG Testing Application")
        self.root.geometry("750x900")
        self.root.resizable(True, True)

        # Style configuration
        self.style = ttk.Style()
        self.style.configure("Title.TLabel", font=("Helvetica", 16, "bold"))
        self.style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))
        self.style.configure("TButton", font=("Helvetica", 10))
        self.style.configure("TCheckbutton", font=("Helvetica", 10))

        # Initialize variables
        self.current_test_type = None
        self.output_text = None

        # Show main menu
        self.show_main_menu()

    def clear_window(self):
        """Clear all widgets from window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        """Show the main selection menu."""
        self.clear_window()

        # Title
        title_label = ttk.Label(
            self.root,
            text="BitRAG Testing Application",
            style="Title.TLabel"
        )
        title_label.pack(pady=40)

        # Subtitle
        subtitle = ttk.Label(
            self.root,
            text="Select Test Type",
            font=("Helvetica", 12)
        )
        subtitle.pack(pady=10)

        # Test buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=30)

        indexing_btn = ttk.Button(
            button_frame,
            text="1. Test Indexing",
            command=self.show_indexing_form,
            width=25
        )
        indexing_btn.pack(pady=10)

        inference_btn = ttk.Button(
            button_frame,
            text="2. Test Inference",
            command=self.show_inference_form,
            width=25
        )
        inference_btn.pack(pady=10)

        # Exit button
        exit_btn = ttk.Button(
            self.root,
            text="Exit",
            command=self.root.quit,
            width=15
        )
        exit_btn.pack(pady=30)

    def show_indexing_form(self):
        """Show indexing test form."""
        self.clear_window()
        self.current_test_type = "indexing"

        # Title
        title = ttk.Label(self.root, text="Test Indexing", style="Title.TLabel")
        title.pack(pady=15)

        # Back button
        back_btn = ttk.Button(self.root, text="← Back", command=self.show_main_menu)
        back_btn.pack(anchor=tk.W, padx=10, pady=5)

        # Create canvas with scrollbar for scrolling
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding=15)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Input file
        row = 0
        ttk.Label(scrollable_frame, text="Input File:").grid(row=row, column=0, sticky=tk.W, pady=(10, 2))
        input_var = tk.StringVar()
        input_entry = ttk.Entry(scrollable_frame, textvariable=input_var, width=50)
        input_entry.grid(row=row, column=1, pady=(10, 2), padx=5)
        ttk.Button(scrollable_frame, text="Browse", command=lambda: self.browse_file(input_var)).grid(row=row, column=2, pady=(10, 2))
        ttk.Label(scrollable_frame, text="Path to file to index (PDF, TXT, etc.)", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        # Output file
        row += 2
        ttk.Label(scrollable_frame, text="Output File:").grid(row=row, column=0, sticky=tk.W, pady=5)
        output_var = tk.StringVar(value="indexing_results.txt")
        ttk.Entry(scrollable_frame, textvariable=output_var, width=50).grid(row=row, column=1, pady=5, padx=5)
        ttk.Label(scrollable_frame, text="File name to save results", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        # Chunk size
        row += 2
        ttk.Label(scrollable_frame, text="Chunk Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
        chunk_size_var = tk.IntVar(value=512)
        ttk.Spinbox(scrollable_frame, from_=100, to=4096, increment=100, textvariable=chunk_size_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(scrollable_frame, text="Number of characters per chunk (default: 512)", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        # Chunk overlap
        row += 2
        ttk.Label(scrollable_frame, text="Chunk Overlap:").grid(row=row, column=0, sticky=tk.W, pady=5)
        chunk_overlap_var = tk.IntVar(value=50)
        ttk.Spinbox(scrollable_frame, from_=0, to=512, increment=10, textvariable=chunk_overlap_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(scrollable_frame, text="Overlap between chunks in characters (default: 50)", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        # Embedding model
        row += 2
        ttk.Label(scrollable_frame, text="Embedding Model:").grid(row=row, column=0, sticky=tk.W, pady=5)
        model_var = tk.StringVar(value="sentence-transformers/all-MiniLM-L6-v2")
        model_combo = ttk.Combobox(scrollable_frame, textvariable=model_var, width=47, values=[
            "sentence-transformers/all-MiniLM-L6-v2",
            "sentence-transformers/all-mpnet-base-v2",
            "BAAI/bge-small-en-v1.5",
            "BAAI/bge-base-en-v1.5",
        ])
        model_combo.grid(row=row, column=1, pady=5, padx=5)
        model_combo['state'] = 'readonly'
        ttk.Label(scrollable_frame, text="Model for generating embeddings", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        # Run button
        row += 2
        run_btn = ttk.Button(scrollable_frame, text="Run Indexing Test", command=lambda: self.run_indexing_test(
            input_var.get(), output_var.get(), chunk_size_var.get(), chunk_overlap_var.get(), model_var.get()
        ))
        run_btn.grid(row=row, column=0, columnspan=3, pady=20)

        # Progress bar
        self.indexing_progress = ttk.Progressbar(scrollable_frame, mode="indeterminate", length=300)
        self.indexing_progress.grid(row=row+1, column=0, columnspan=3, pady=5)

        # Status label
        self.indexing_status = ttk.Label(scrollable_frame, text="Ready", font=("Helvetica", 9), foreground="gray")
        self.indexing_status.grid(row=row+2, column=0, columnspan=3, pady=5)

    def show_inference_form(self):
        """Show inference test form."""
        self.clear_window()
        self.current_test_type = "inference"

        # Title
        title = ttk.Label(self.root, text="Test Inference", style="Title.TLabel")
        title.pack(pady=15)

        # Back button
        back_btn = ttk.Button(self.root, text="← Back", command=self.show_main_menu)
        back_btn.pack(anchor=tk.W, padx=10, pady=5)

        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Basic tab
        basic_frame = ttk.Frame(notebook, padding=15)
        notebook.add(basic_frame, text="Basic")

        row = 0
        # Model
        ttk.Label(basic_frame, text="LLM Model:").grid(row=row, column=0, sticky=tk.W, pady=(10, 2))
        model_var = tk.StringVar()
        model_combo = ttk.Combobox(basic_frame, textvariable=model_var, width=40)
        model_combo.grid(row=row, column=1, pady=(10, 2), padx=5)
        threading.Thread(target=self.populate_models, args=(model_combo,), daemon=True).start()
        ttk.Label(basic_frame, text="Ollama model to use for inference", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        # Query
        row += 2
        ttk.Label(basic_frame, text="Query:").grid(row=row, column=0, sticky=tk.W, pady=5)
        query_text = tk.Text(basic_frame, height=3, width=40)
        query_text.grid(row=row, column=1, pady=5, padx=5)
        ttk.Label(basic_frame, text="Question to ask the model", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        # Output file
        row += 2
        ttk.Label(basic_frame, text="Output File:").grid(row=row, column=0, sticky=tk.W, pady=5)
        output_var = tk.StringVar(value="inference_results.txt")
        ttk.Entry(basic_frame, textvariable=output_var, width=42).grid(row=row, column=1, pady=5, padx=5)
        ttk.Label(basic_frame, text="File name to save results", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        # Top-K for retrieval
        row += 2
        ttk.Label(basic_frame, text="Top-K (retrieval):").grid(row=row, column=0, sticky=tk.W, pady=5)
        top_k_var = tk.IntVar(value=3)
        ttk.Spinbox(basic_frame, from_=1, to=10, textvariable=top_k_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(basic_frame, text="Number of chunks to retrieve (default: 3)", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        # Ollama parameters tab
        ollama_frame = ttk.Frame(notebook, padding=15)
        notebook.add(ollama_frame, text="Ollama Parameters")

        row = 0
        # Temperature
        ttk.Label(ollama_frame, text="Temperature:").grid(row=row, column=0, sticky=tk.W, pady=(10, 2))
        temp_var = tk.DoubleVar(value=0.1)
        ttk.Spinbox(ollama_frame, from_=0.0, to=2.0, increment=0.1, textvariable=temp_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(ollama_frame, text="Sampling temperature - higher = more creative (default: 0.1)", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        # Top-P
        row += 2
        ttk.Label(ollama_frame, text="Top-P:").grid(row=row, column=0, sticky=tk.W, pady=5)
        top_p_var = tk.DoubleVar(value=0.9)
        ttk.Spinbox(ollama_frame, from_=0.0, to=1.0, increment=0.1, textvariable=top_p_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(ollama_frame, text="Nucleus sampling threshold (default: 0.9)", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        # Top-K
        row += 2
        ttk.Label(ollama_frame, text="Top-K:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ollama_top_k_var = tk.IntVar(value=40)
        ttk.Spinbox(ollama_frame, from_=1, to=100, textvariable=ollama_top_k_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(ollama_frame, text="Number of tokens to consider (default: 40)", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        # Context size
        row += 2
        ttk.Label(ollama_frame, text="Context Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ctx_var = tk.IntVar(value=2048)
        ttk.Spinbox(ollama_frame, from_=512, to=8192, increment=512, textvariable=ctx_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(ollama_frame, text="Context window size in tokens (default: 2048)", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        # Repeat penalty
        row += 2
        ttk.Label(ollama_frame, text="Repeat Penalty:").grid(row=row, column=0, sticky=tk.W, pady=5)
        repeat_var = tk.DoubleVar(value=1.1)
        ttk.Spinbox(ollama_frame, from_=0.0, to=2.0, increment=0.1, textvariable=repeat_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(ollama_frame, text="Penalty for repeated tokens (default: 1.1)", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        # Seed
        row += 2
        ttk.Label(ollama_frame, text="Seed (-1 for random):").grid(row=row, column=0, sticky=tk.W, pady=5)
        seed_var = tk.IntVar(value=-1)
        ttk.Spinbox(ollama_frame, from_=-1, to=999999, textvariable=seed_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(ollama_frame, text="Random seed for reproducibility (-1 = random)", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        # GPU layers
        row += 2
        ttk.Label(ollama_frame, text="GPU Layers (-1 for all):").grid(row=row, column=0, sticky=tk.W, pady=5)
        gpu_layers_var = tk.IntVar(value=-1)
        ttk.Spinbox(ollama_frame, from_=-1, to=100, textvariable=gpu_layers_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(ollama_frame, text="Number of layers to offload to GPU (-1 = all)", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        # Threads
        row += 2
        ttk.Label(ollama_frame, text="Threads (-1 for auto):").grid(row=row, column=0, sticky=tk.W, pady=5)
        threads_var = tk.IntVar(value=-1)
        ttk.Spinbox(ollama_frame, from_=-1, to=32, textvariable=threads_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(ollama_frame, text="Number of CPU threads to use (-1 = auto)", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        # Batch size
        row += 2
        ttk.Label(ollama_frame, text="Batch Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
        batch_var = tk.IntVar(value=512)
        ttk.Spinbox(ollama_frame, from_=1, to=4096, increment=128, textvariable=batch_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(ollama_frame, text="Batch size for prompt processing (default: 512)", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        # Checkboxes
        row += 2
        mmap_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ollama_frame, text="Memory Mapping (mmap)", variable=mmap_var).grid(row=row, column=0, sticky=tk.W, pady=5)

        numa_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ollama_frame, text="NUMA Binding", variable=numa_var).grid(row=row, column=1, sticky=tk.W, pady=5)

        # Format
        row += 1
        ttk.Label(ollama_frame, text="Output Format:").grid(row=row, column=0, sticky=tk.W, pady=5)
        format_var = tk.StringVar(value="json")
        format_combo = ttk.Combobox(ollama_frame, textvariable=format_var, width=20, values=["json", "beauty"])
        format_combo.grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        format_combo['state'] = 'readonly'
        ttk.Label(ollama_frame, text="Response format from Ollama", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        # Indexing info tab
        indexing_frame = ttk.Frame(notebook, padding=15)
        notebook.add(indexing_frame, text="Indexing Info")

        row = 0
        ttk.Label(indexing_frame, text="Embedding Model:").grid(row=row, column=0, sticky=tk.W, pady=(10, 2))
        embed_model_var = tk.StringVar(value="sentence-transformers/all-MiniLM-L6-v2")
        ttk.Entry(indexing_frame, textvariable=embed_model_var, width=42).grid(row=row, column=1, pady=5, padx=5)
        ttk.Label(indexing_frame, text="Model used for embedding the indexed documents", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        row += 2
        ttk.Label(indexing_frame, text="Chunk Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
        index_chunk_size_var = tk.IntVar(value=512)
        ttk.Spinbox(indexing_frame, from_=100, to=4096, increment=100, textvariable=index_chunk_size_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(indexing_frame, text="Chunk size used when indexing", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        row += 2
        ttk.Label(indexing_frame, text="Chunk Overlap:").grid(row=row, column=0, sticky=tk.W, pady=5)
        index_chunk_overlap_var = tk.IntVar(value=50)
        ttk.Spinbox(indexing_frame, from_=0, to=512, increment=10, textvariable=index_chunk_overlap_var, width=20).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(indexing_frame, text="Chunk overlap used when indexing", font=("Helvetica", 8), foreground="gray").grid(row=row+1, column=1, sticky=tk.W, padx=5)

        # Run button
        run_frame = ttk.Frame(self.root, padding=10)
        run_frame.pack(fill=tk.X)

        run_btn = ttk.Button(run_frame, text="Run Inference Test", command=lambda: self.run_inference_test(
            model_var.get(), query_text.get("1.0", tk.END).strip(), output_var.get(),
            top_k_var.get(), temp_var.get(), top_p_var.get(), ollama_top_k_var.get(),
            ctx_var.get(), repeat_var.get(), seed_var.get(), gpu_layers_var.get(),
            threads_var.get(), batch_var.get(), mmap_var.get(), numa_var.get(),
            format_var.get(), embed_model_var.get(), index_chunk_size_var.get(), index_chunk_overlap_var.get()
        ))
        run_btn.pack(pady=10)

        # Progress bar
        self.inference_progress = ttk.Progressbar(run_frame, mode="indeterminate", length=300)
        self.inference_progress.pack(pady=5)

        # Status label
        self.inference_status = ttk.Label(run_frame, text="Ready", font=("Helvetica", 9), foreground="gray")
        self.inference_status.pack(pady=5)

        # Output area
        output_frame = ttk.LabelFrame(self.root, text="Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=10, font=("Courier", 9))
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def populate_models(self, combobox: ttk.Combobox):
        """Populate model combobox with available Ollama models."""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = [m["name"] for m in response.json().get("models", [])]
                if models:
                    self.root.after(0, lambda: self.update_combobox(combobox, models))
        except Exception:
            fallback = ["llama3.2:1b", "llama3.2", "mistral", "codellama:7b", "phi3:14b"]
            self.root.after(0, lambda: self.update_combobox(combobox, fallback))

    def update_combobox(self, combobox: ttk.Combobox, values: list):
        """Update combobox with values."""
        combobox['values'] = values
        if values:
            combobox.current(0)
            combobox['state'] = 'readonly'

    def browse_file(self, var: tk.StringVar):
        """Browse for input file."""
        filename = filedialog.askopenfilename(
            title="Select File to Index",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if filename:
            var.set(filename)

    def run_indexing_test(self, input_file, output_file, chunk_size, chunk_overlap, model):
        """Run indexing test."""
        if not input_file:
            messagebox.showerror("Error", "Please select an input file")
            return

        if not os.path.exists(input_file):
            messagebox.showerror("Error", f"File not found: {input_file}")
            return

        # Start progress bar
        if hasattr(self, 'indexing_progress'):
            self.indexing_progress.start(10)
        if hasattr(self, 'indexing_status'):
            self.indexing_status.config(text="Indexing in progress...", foreground="blue")

        # Show progress message in output if available
        if self.output_text:
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, f"Running indexing test...\n")
            self.output_text.insert(tk.END, f"Input: {input_file}\n")
            self.output_text.insert(tk.END, f"Output: {output_file}\n\n")
        else:
            print(f"Running indexing test...")
            print(f"Input: {input_file}")
            print(f"Output: {output_file}")

        def run_test():
            try:
                cmd = [
                    _PYTHON_PATH, "test_indexing.py",
                    "--input", input_file,
                    "--output", output_file,
                    "--chunk-size", str(chunk_size),
                    "--chunk-overlap", str(chunk_overlap),
                    "--model", model,
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=_PROJECT_ROOT, env=get_python_env())
                self.root.after(0, lambda: self.finish_indexing_test(result))
            except Exception as e:
                self.root.after(0, lambda: self.handle_test_error(str(e)))

        threading.Thread(target=run_test, daemon=True).start()

    def finish_indexing_test(self, result):
        """Finish indexing test and update UI."""
        # Stop progress bar
        if hasattr(self, 'indexing_progress'):
            self.indexing_progress.stop()
        if hasattr(self, 'indexing_status'):
            if result.returncode == 0:
                self.indexing_status.config(text="Completed successfully!", foreground="green")
            else:
                self.indexing_status.config(text="Failed - check output", foreground="red")
        
        self.display_output(result)

    def run_inference_test(self, model, query, output_file, top_k, temperature, top_p, top_k_ollama, ctx, repeat_penalty, seed, gpu_layers, threads, batch, mmap, numa, format_val, embed_model, chunk_size, chunk_overlap):
        """Run inference test."""
        if not model:
            messagebox.showerror("Error", "Please select a model")
            return

        if not query:
            messagebox.showerror("Error", "Please enter a query")
            return

        # Start progress bar
        if hasattr(self, 'inference_progress'):
            self.inference_progress.start(10)
        if hasattr(self, 'inference_status'):
            self.inference_status.config(text="Running inference...", foreground="blue")

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, f"Running inference test...\n")
        self.output_text.insert(tk.END, f"Model: {model}\n")
        self.output_text.insert(tk.END, f"Query: {query}\n\n")

        def run_test():
            try:
                cmd = [
                    _PYTHON_PATH, "test_inference.py",
                    "--model", model,
                    "--query", query,
                    "--output", output_file,
                    "--top-k", str(top_k),
                    "--temperature", str(temperature),
                    "--top-p", str(top_p),
                    "--ollama-top-k", str(top_k_ollama),
                    "--ctx", str(ctx),
                    "--repeat-penalty", str(repeat_penalty),
                    "--seed", str(seed),
                    "--num-gpu-layers", str(gpu_layers),
                    "--threads", str(threads),
                    "--batch", str(batch),
                    "--embedding-model", embed_model,
                    "--chunk-size", str(chunk_size),
                    "--chunk-overlap", str(chunk_overlap),
                ]
                if mmap:
                    cmd.append("--mmap")
                else:
                    cmd.append("--no-mmap")
                if numa:
                    cmd.append("--numa")
                else:
                    cmd.append("--no-numa")
                cmd.extend(["--format", format_val])

                result = subprocess.run(cmd, capture_output=True, text=True, cwd=_PROJECT_ROOT, env=get_python_env())
                self.root.after(0, lambda: self.finish_inference_test(result))
            except Exception as e:
                self.root.after(0, lambda: self.handle_test_error(str(e)))

        threading.Thread(target=run_test, daemon=True).start()

    def finish_inference_test(self, result):
        """Finish inference test and update UI."""
        # Stop progress bar
        if hasattr(self, 'inference_progress'):
            self.inference_progress.stop()
        if hasattr(self, 'inference_status'):
            if result.returncode == 0:
                self.inference_status.config(text="Completed successfully!", foreground="green")
            else:
                self.inference_status.config(text="Failed - check output", foreground="red")
        
        self.display_output(result)

    def handle_test_error(self, error_message):
        """Handle test execution errors."""
        # Stop progress bars
        if hasattr(self, 'indexing_progress'):
            self.indexing_progress.stop()
        if hasattr(self, 'inference_progress'):
            self.inference_progress.stop()
        
        # Update status labels
        if hasattr(self, 'indexing_status'):
            self.indexing_status.config(text="Error occurred", foreground="red")
        if hasattr(self, 'inference_status'):
            self.inference_status.config(text="Error occurred", foreground="red")
        
        messagebox.showerror("Error", error_message)

    def display_output(self, result):
        """Display subprocess output."""
        if not self.output_text:
            # Print to console if no GUI output
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
            return
            
        if result.returncode == 0:
            self.output_text.insert(tk.END, "✓ Test completed successfully!\n\n")
        else:
            self.output_text.insert(tk.END, "✗ Test failed!\n\n")

        if result.stdout:
            self.output_text.insert(tk.END, result.stdout)

        if result.stderr:
            self.output_text.insert(tk.END, "\n--- Errors ---\n")
            self.output_text.insert(tk.END, result.stderr)

        self.output_text.see(tk.END)


def main():
    """Main entry point."""
    root = tk.Tk()
    app = BitRAGTestGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
