import os
import re
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

def vtt_time_to_lrc(vtt_time: str) -> str:
    """Convert VTT timestamp to LRC timestamp format."""
    time_obj = datetime.strptime(vtt_time, "%H:%M:%S.%f")
    return time_obj.strftime("%M:%S.%f")[:-3]  # Convert to MM:SS.xx format

def clean_filename(filename: str) -> str:
    """Remove audio file extensions (.mp3, .wav, etc.) from filename."""
    return re.sub(r"\.(mp3|wav|flac|aac|ogg|m4a)$", "", filename, flags=re.IGNORECASE)

def convert_vtt_to_lrc(vtt_file: str, lrc_file: str):
    """Convert a .vtt file to .lrc format with single-line lyrics."""
    with open(vtt_file, "r", encoding="utf-8", errors="replace") as vf, \
         open(lrc_file, "w", encoding="utf-8") as lf:
        
        current_line = ""
        timestamp = None
        
        for line in vf:
            line = line.strip()
            if line.isdigit():  # Skip subtitle index numbers
                continue
            
            time_match = re.match(r"(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->", line)
            if time_match:
                # Write the previous subtitle before processing the new timestamp
                if timestamp and current_line:
                    lf.write(f"[{timestamp}] {current_line}\n")
                
                timestamp = vtt_time_to_lrc(time_match.group(1))
                current_line = ""  # Reset text storage for new subtitle block
            elif line and not line.startswith("WEBVTT"):  # Ignore WEBVTT header
                current_line += (" " if current_line else "") + line  # Append line with space
        
        # Write the last subtitle block without an extra newline
        if timestamp and current_line:
            lf.write(f"[{timestamp}] {current_line}")

def batch_convert(folder: str):
    """Convert all .vtt files in a folder and its subfolders to .lrc format."""
    converted_files = 0
    
    # os.walk()를 사용하여 하위 폴더까지 검색
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".vtt"):
                vtt_path = os.path.join(root, file)
                base_name = file[:-4]  # .vtt 제거
                base_name = clean_filename(base_name)  # 오디오 확장자 제거
                lrc_path = os.path.join(root, base_name + ".lrc")  # 같은 폴더에 .lrc 저장
                convert_vtt_to_lrc(vtt_path, lrc_path)
                converted_files += 1

    return converted_files

def select_folder():
    """Open folder selection dialog and convert .vtt files in all subfolders."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder = filedialog.askdirectory(title="Select a folder containing .vtt files")
    
    if folder:
        converted_count = batch_convert(folder)
        if converted_count > 0:
            messagebox.showinfo("Conversion Complete", f"Converted {converted_count} .vtt files to .lrc format!")
        else:
            messagebox.showwarning("No Files Found", "No .vtt files found in the selected folder or its subfolders.")
    else:
        messagebox.showerror("Operation Cancelled", "No folder selected. Conversion aborted.")

if __name__ == "__main__":
    select_folder()
