import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
import subprocess
import threading
import sys
import webbrowser

class MinecraftVideoProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Official Watch Video Converter")
        self.root.geometry("600x500")
        
        self.input_file = None
        self.is_processing = False
        self.process = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame with minimal padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Minecraft Official Watch Video Converter", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 5))
        
        # Description
        desc_text = "Converts any video to a format that the official Minecraft watch supports.\nYou need a microSD card and screwdrivers to open it up."
        desc_label = ttk.Label(main_frame, text=desc_text, justify=tk.CENTER, font=("Arial", 8))
        desc_label.grid(row=1, column=0, columnspan=2, pady=(0, 5))
        
        # Amazon link
        link_frame = ttk.Frame(main_frame)
        link_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        ttk.Label(link_frame, text="Official Watch:", font=("Arial", 8)).pack(side=tk.LEFT)
        link_label = ttk.Label(link_frame, text="Amazon Link", foreground="blue", cursor="hand2", font=("Arial", 8))
        link_label.pack(side=tk.LEFT, padx=2)
        link_label.bind("<Button-1>", lambda e: webbrowser.open("https://www.amazon.com/Accutime-Minecraft-Educational-Learning-Touchscreen/dp/B0BMK86R2J?ref_=ast_sto_dp"))
        
        # Input file selection
        ttk.Label(main_frame, text="Select Video File:").grid(row=3, column=0, sticky=tk.W, pady=2)
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        self.input_entry = ttk.Entry(input_frame, width=40)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(input_frame, text="Browse", command=self.browse_input).pack(side=tk.RIGHT)
        
        # Compression options
        compression_frame = ttk.LabelFrame(main_frame, text="Compression Settings", padding="5")
        compression_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Compression level
        ttk.Label(compression_frame, text="Compression:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.compression_var = tk.StringVar(value="Medium")
        compression_combo = ttk.Combobox(compression_frame, textvariable=self.compression_var,
                                        values=["Low (Best Quality)", 
                                               "Medium", 
                                               "High",
                                               "Very High (Smallest)"],
                                        state="readonly", width=20)
        compression_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # File size estimation
        self.size_label = ttk.Label(compression_frame, text="Estimated: ~10-50MB/min", 
                                   foreground="blue", font=("Arial", 7))
        self.size_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=1)
        
        # Progress bars
        progress_frame = ttk.LabelFrame(main_frame, text="Conversion Progress", padding="5")
        progress_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(progress_frame, text="Progress:").grid(row=0, column=0, sticky=tk.W)
        self.overall_progress = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.overall_progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        self.progress_label = ttk.Label(progress_frame, text="Ready to convert", font=("Arial", 8))
        self.progress_label.grid(row=2, column=0, sticky=tk.W, pady=1)
        
        self.status_text = tk.Text(progress_frame, height=6, width=50, state=tk.DISABLED, font=("Arial", 8))
        self.status_text.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Control buttons - at the bottom where they're visible
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        self.process_btn = ttk.Button(button_frame, text="Convert Video", command=self.process_video)
        self.process_btn.pack(side=tk.LEFT, padx=3)
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.cancel_processing, state='disabled')
        self.cancel_btn.pack(side=tk.LEFT, padx=3)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        compression_frame.columnconfigure(1, weight=1)
    
    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm *.m4v *.3gp")]
        )
        if filename:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, filename)
    
    def get_compression_settings(self):
        """Returns MJPEG quality value based on compression level"""
        compression_map = {
            "Low (Best Quality)": "1",
            "Medium": "3", 
            "High": "5",
            "Very High (Smallest)": "7"
        }
        return compression_map.get(self.compression_var.get(), "3")
    
    def update_progress(self, value, status):
        self.overall_progress['value'] = value
        self.progress_label.config(text=status)
        self.root.update_idletasks()
    
    def log_status(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def process_video(self):
        if self.is_processing:
            return
            
        input_file = self.input_entry.get()
        
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Error", "Please select a valid video file")
            return
        
        # Create output filename
        input_path = Path(input_file)
        output_file = input_path.parent / f"{input_path.stem}_minecraft_watch.avi"
        
        self.is_processing = True
        self.process_btn.config(state='disabled')
        self.cancel_btn.config(state='normal')
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)
        
        # Start processing in separate thread
        thread = threading.Thread(target=self.run_processing, args=(input_file, str(output_file)))
        thread.daemon = True
        thread.start()
    
    def run_processing(self, input_file, output_file):
        try:
            self.log_status("Starting Minecraft Watch video conversion...")
            self.update_progress(10, "Initializing...")
            
            # Get compression setting
            compression_level = self.get_compression_settings()
            compression_name = self.compression_var.get()
            
            self.log_status(f"Compression: {compression_name}")
            self.log_status("Converting: 200% volume, 128x108 with aspect ratio...")
            
            # FFmpeg command with aspect ratio preservation, black padding, and compression
            cmd = [
                'ffmpeg',
                '-i', input_file,
                '-af', 'volume=2.0',  # 200% volume
                # Scale to fit within 128x108 while maintaining aspect ratio, then pad with black
                '-vf', 'scale=128:108:force_original_aspect_ratio=decrease:flags=lanczos,pad=128:108:(ow-iw)/2:(oh-ih)/2:black',
                '-c:v', 'mjpeg',  # MJPEG video codec
                '-q:v', compression_level,  # Quality setting from compression option
                '-c:a', 'pcm_s16le',  # PCM audio for AVI
                '-y',  # Overwrite output file
                output_file
            ]
            
            self.log_status("Starting conversion...")
            self.update_progress(20, "Processing...")
            
            # Run FFmpeg process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                encoding='utf-8',
                errors='replace'
            )
            
            # Monitor progress
            while True:
                if self.process.poll() is not None:
                    break
                    
                output = self.process.stdout.readline()
                if output:
                    self.log_status(output.strip())
                
                # Simple progress simulation
                current_progress = self.overall_progress['value']
                if current_progress < 90:
                    self.update_progress(current_progress + 0.5, "Converting...")
            
            # Get any remaining output
            remaining_output, _ = self.process.communicate()
            if remaining_output:
                self.log_status(remaining_output.strip())
            
            # Check if process completed successfully
            if self.process.returncode == 0:
                self.update_progress(100, "Complete!")
                
                # Show file size information
                if os.path.exists(output_file):
                    file_size = os.path.getsize(output_file)
                    size_mb = file_size / (1024 * 1024)
                    self.log_status(f"Success! Saved as: {output_file}")
                    self.log_status(f"File size: {size_mb:.2f} MB")
                    self.log_status("Ready for microSD card!")
                    
                    messagebox.showinfo("Success", 
                                      f"Video converted successfully!\n\n"
                                      f"Output: {output_file}\n"
                                      f"Size: {size_mb:.2f} MB\n\n"
                                      f"Transfer to microSD card and insert into watch!")
                else:
                    self.log_status(f"Success! Output: {output_file}")
                    messagebox.showinfo("Success", f"Video converted!\nOutput: {output_file}")
            else:
                raise Exception(f"FFmpeg failed with return code {self.process.returncode}")
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.log_status(error_msg)
            self.update_progress(0, "Error")
            if not self.is_processing:
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        finally:
            self.root.after(0, self.reset_ui)
    
    def reset_ui(self):
        self.is_processing = False
        self.process_btn.config(state='normal')
        self.cancel_btn.config(state='disabled')
        if self.process:
            self.process = None
    
    def cancel_processing(self):
        if self.is_processing and self.process:
            self.is_processing = False
            self.process.terminate()
            self.log_status("Cancelled")
            self.update_progress(0, "Cancelled")
            messagebox.showinfo("Cancelled", "Conversion cancelled")

def check_ffmpeg():
    """Check if FFmpeg is available in system PATH"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def main():
    if not check_ffmpeg():
        print("Error: FFmpeg is not installed or not in system PATH.")
        print("Please install FFmpeg from: https://ffmpeg.org/download.html")
        response = messagebox.showerror(
            "FFmpeg Not Found", 
            "FFmpeg is required but not found.\n\nPlease install FFmpeg from: https://ffmpeg.org/download.html"
        )
        return
    
    root = tk.Tk()
    app = MinecraftVideoProcessor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
