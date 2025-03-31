import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os, time, re, random, logging, sys, json, subprocess
from threading import Thread
import yt_dlp
from urllib.parse import parse_qs, urlparse
from ttkthemes import ThemedTk
from tkinter import font as tkfont
import concurrent.futures
import requests

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader Pro")
        self.root.geometry("800x500")
        
        # Professional color scheme
        self.colors = {
            'bg_dark': '#1E1E1E',
            'bg_light': '#2D2D2D',
            'accent': '#007ACC',  # Professional blue
            'accent_hover': '#005C99',
            'text': '#E0E0E0',
            'text_dim': '#B0B0B0',
            'success': '#28A745',
            'error': '#DC3545',
            'entry_bg': '#3D3D3D',
            'entry_text': '#FFFFFF'
        }
        
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Update Entry style with black text
        self.style = ttk.Style(self.root)
        self.style.configure(
            "Custom.TEntry",
            fieldbackground="#FFFFFF",  # White background
            foreground="#000000",  # Black text
            insertcolor="#000000",  # Black cursor
            borderwidth=0,
            padding=5
        )
        
        # Update focus state with maintaining black text
        self.style.map('Custom.TEntry',
            fieldbackground=[('focus', '#FFFFFF')],  # Keep white background on focus
            foreground=[('focus', '#000000')]  # Keep black text on focus
        )
        
        self.style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor=self.colors['bg_light'],
            background=self.colors['accent'],
            thickness=8,
            borderwidth=0
        )

        # Create main frame with padding
        self.main_frame = tk.Frame(
            self.root,
            bg=self.colors['bg_dark'],
            padx=40,
            pady=30
        )
        self.main_frame.pack(expand=True, fill="both")

        # Set up consistent paths
        try:
            # Get application base path
            if getattr(sys, 'frozen', False):
                self.base_path = os.path.dirname(sys.executable)
            else:
                self.base_path = os.path.dirname(os.path.abspath(__file__))

            # Set up paths relative to application
            self.download_path = os.path.join(self.base_path, "downloads")
            self.log_file = os.path.join(self.base_path, "logs", "downloader.log")
            self.data_path = os.path.join(self.base_path, ".data")
            
            # Create necessary directories
            os.makedirs(self.download_path, exist_ok=True)
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            os.makedirs(self.data_path, exist_ok=True)
            
            # Configure logging
            logging.getLogger().handlers = []
            logging.basicConfig(
                filename=self.log_file,
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            
            logging.info("=== Application Started ===")
            logging.info(f"Downloads path: {self.download_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize: {str(e)}")
            self.root.quit()
            return

        self.setup_gui()
        self.setup_bindings()
        
        # Restore working yt-dlp options
        self.ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': True,
            'nocheckcertificate': True,
            'extract_flat': True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.youtube.com/'
            }
        }
        
        logging.info("Application started")
        self.download_in_progress = False
        self.current_download = None

        # Add menu bar with legal information
        self.setup_menu()
        
        # First time run checks
        self.first_run_checks()

    def first_run_checks(self):
        """Handle first-run notices and agreements"""
        try:
            # Always show legal notice first
            self.show_legal_notice()
            
            # Then check EULA
            eula_file = os.path.join(self.data_path, '.eula_accepted')
            if not os.path.exists(eula_file):
                logging.info("EULA not yet accepted - showing prompt")
                self.show_eula()
            else:
                logging.info("EULA previously accepted")
                
        except Exception as e:
            logging.error(f"Error in first run checks: {str(e)}")
            messagebox.showerror("Error", "Failed to verify legal agreements. Please restart the application.")
            self.root.quit()

    def show_eula(self):
        """Show EULA and get acceptance"""
        try:
            with open('EULA.md', 'r') as f:
                eula_text = f.read()
                
            response = messagebox.askokcancel(
                "End User License Agreement",
                f"{eula_text}\n\nDo you accept these terms?",
                icon='warning'
            )
            
            if response:
                # Save acceptance
                eula_file = os.path.join(self.data_path, '.eula_accepted')
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                username = os.getenv('USERNAME', 'Unknown')
                
                with open(eula_file, 'w') as f:
                    f.write(f"Accepted by {username} on {timestamp}")
                    
                logging.info(f"EULA accepted by user {username} at {timestamp}")
            else:
                logging.info("EULA declined - exiting")
                self.root.quit()
                
        except Exception as e:
            logging.error(f"Error showing EULA: {str(e)}")
            self.root.quit()

    def setup_gui(self):
        # Title with enhanced styling
        title_font = tkfont.Font(family="Segoe UI", size=28, weight="bold")
        title = tk.Label(
            self.main_frame,
            text="YouTube Downloader Pro",
            fg=self.colors['accent'],
            bg=self.colors['bg_dark'],
            font=title_font
        )
        title.pack(pady=(0, 10))  # Reduced bottom padding to fit subtitle

        # Add subtitle guide text
        subtitle_font = tkfont.Font(family="Segoe UI", size=11)
        subtitle = tk.Label(
            self.main_frame,
            text="Enter YouTube URL and click Download",
            fg=self.colors['text_dim'],
            bg=self.colors['bg_dark'],
            font=subtitle_font
        )
        subtitle.pack(pady=(0, 30))  # Add padding after subtitle

        # URL Frame with enhanced styling
        url_frame = tk.Frame(
            self.main_frame,
            bg=self.colors['bg_dark'],
            pady=20
        )
        url_frame.pack(fill="x")

        # Enhanced URL Entry with updated styling
        self.url_entry = ttk.Entry(
            url_frame,
            font=("Segoe UI", 12),
            style="Custom.TEntry",
            width=50,
            foreground="#000000"  # Ensure black text
        )
        self.url_entry.pack(side="left", expand=True, padx=(0, 10))
        
        # Enhanced Download Button
        self.download_button = tk.Button(
            url_frame,
            text="Download",
            command=self.start_download,
            bg=self.colors['accent'],
            fg=self.colors['text'],
            font=("Segoe UI", 12, "bold"),
            bd=0,
            padx=25,
            pady=12,
            cursor="hand2",
            activebackground=self.colors['accent_hover'],
            activeforeground=self.colors['text']
        )
        self.download_button.pack(side="right")

        # Status Label with enhanced styling
        self.status_label = tk.Label(
            self.main_frame,
            text="Ready to download",
            fg=self.colors['text_dim'],
            bg=self.colors['bg_dark'],
            font=("Segoe UI", 11)
        )
        self.status_label.pack(pady=20)

        # Progress section with improved spacing
        progress_frame = tk.Frame(self.main_frame, bg=self.colors['bg_dark'])
        progress_frame.pack(fill="x", pady=20)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            style="Custom.Horizontal.TProgressbar",
            length=700,
            mode='determinate'
        )
        self.progress_bar.pack(pady=15)

        # Progress info with better layout
        progress_info_frame = tk.Frame(progress_frame, bg=self.colors['bg_dark'])
        progress_info_frame.pack(fill="x", padx=5)

        self.percent_label = tk.Label(
            progress_info_frame,
            text="0%",
            fg=self.colors['text_dim'],
            bg=self.colors['bg_dark'],
            font=("Segoe UI", 10)
        )
        self.percent_label.pack(side="left")

        self.speed_label = tk.Label(
            progress_info_frame,
            text="",
            fg=self.colors['text_dim'],
            bg=self.colors['bg_dark'],
            font=("Segoe UI", 10)
        )
        self.speed_label.pack(side="right")

    def setup_bindings(self):
        """Simplified bindings without custom focus style"""
        # Button hover effect
        self.download_button.bind(
            '<Enter>', 
            lambda e: e.widget.config(bg=self.colors['accent_hover'])
        )
        self.download_button.bind(
            '<Leave>', 
            lambda e: e.widget.config(bg=self.colors['accent'])
        )

    def progress_hook(self, d):
        """Enhanced progress hook with state checking"""
        if not self.download_in_progress:
            return
            
        try:
            if d['status'] == 'downloading':
                total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                
                if total > 0:
                    percent = (downloaded / total) * 100
                    speed = d.get('speed', 0)
                    if speed:
                        speed_mb = speed / (1024 * 1024)
                        status = f"Downloading: {percent:.1f}% ({speed_mb:.1f} MB/s)"
                    else:
                        status = f"Downloading: {percent:.1f}%"
                    
                    self.root.after(0, self._update_progress, percent, status)
                    
            elif d['status'] == 'finished':
                logging.info("Download finished, processing file...")
                
        except Exception as e:
            logging.error(f"Progress calculation error: {str(e)}")

    def sanitize_filename(self, title):
        """Sanitize filename to avoid special characters"""
        # Remove invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '')
        # Replace problematic characters with underscore
        title = title.replace('：', '_')  # Replace full-width colon
        title = title.replace('\'', '')  # Remove apostrophes
        return title.strip()

    def handle_download(self, url, retries=3):
        """Restored working download handler"""
        self.download_in_progress = True
        for attempt in range(retries):
            try:
                logging.info(f"Download attempt {attempt + 1} for URL: {url}")
                video_id = url.split('watch?v=')[-1].split('&')[0]
                clean_url = f'https://www.youtube.com/watch?v={video_id}'
                
                ydl_opts = self.ydl_opts.copy()
                ydl_opts['progress_hooks'] = [self.progress_hook]
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(clean_url, download=False)
                    if info:
                        title = self.sanitize_filename(info.get('title', 'Unknown Title'))
                        output_template = os.path.join(
                            self.download_path,
                            f'{title}.%(ext)s'
                        )
                        ydl_opts['outtmpl'] = output_template
                        
                        logging.info(f"Starting download of: {title}")
                        self.status_label.config(text=f"Downloading: {title}")
                        
                        # Perform download
                        ydl = yt_dlp.YoutubeDL(ydl_opts)
                        ydl.download([clean_url])
                        
                        expected_file = os.path.join(self.download_path, f"{title}.mp4")
                        if os.path.exists(expected_file):
                            file_size = os.path.getsize(expected_file) / (1024 * 1024)
                            logging.info(f"Download completed successfully - Title: {title}")
                            logging.info(f"File saved to: {expected_file} (Size: {file_size:.2f} MB)")
                            
                            self.root.after(0, self._handle_successful_download, expected_file, title, file_size)
                            return True

            except Exception as e:
                logging.error(f"Download attempt {attempt + 1} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                self.root.after(0, self._handle_failed_download, str(e))
                break
        
        self.download_in_progress = False
        return False

    def _handle_successful_download(self, file_path, title, file_size):
        """Simplified success handler"""
        if not self.download_in_progress:
            return
            
        self.download_in_progress = False
        self.progress_bar['value'] = 100
        self.percent_label.config(text="100%")
        self.status_label.config(
            text=f"Download Complete: {title}",
            fg=self.colors['success']
        )
        self.speed_label.config(text="")
        self.download_button.config(state=tk.NORMAL)
        self.url_entry.delete(0, tk.END)
        
        # Single success message with details
        messagebox.showinfo(
            "Download Complete",
            f"Successfully downloaded:\n\nTitle: {title}\nSize: {file_size:.1f} MB\nLocation: {file_path}"
        )
        
        # Final log entry
        logging.info(f"Download process completed successfully for: {title}")

    def _handle_failed_download(self, error_msg):
        """Unified error handler"""
        if not self.download_in_progress:
            return
            
        self.download_in_progress = False
        logging.error(f"Download failed: {error_msg}")
        
        self.status_label.config(
            text="Download Failed",
            fg=self.colors['error']
        )
        self.progress_bar['value'] = 0
        self.percent_label.config(text="0%")
        self.speed_label.config(text="")
        self.download_button.config(state=tk.NORMAL)
        
        # Single error message
        messagebox.showerror(
            "Download Failed",
            f"Could not download video:\n\n{error_msg}"
        )

    def start_download(self):
        """Enhanced download with additional legal confirmation"""
        legal_warning = """IMPORTANT LEGAL NOTICE

By proceeding, you confirm that:
1. This download is for personal use only
2. You accept all legal responsibility
3. You will comply with copyright laws
4. You understand this is not affiliated with YouTube
5. You indemnify the developer against any claims

Do you agree and wish to proceed?"""

        if not messagebox.askyesno("Legal Confirmation", legal_warning, icon='warning'):
            return

        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
            
        if not ('youtube.com' in url or 'youtu.be' in url):
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            return
        
        self.download_button.config(state=tk.DISABLED)
        self.status_label.config(text="Starting download...")
        self.progress_bar['value'] = 0
        self.percent_label.config(text="0%")
        
        Thread(target=self.handle_download, args=(url,), daemon=True).start()

    def _update_progress(self, percent, status=None):
        """Simplified direct progress update"""
        try:
            # Direct progress update
            self.progress_bar['value'] = percent
            self.percent_label.config(text=f"{percent:.1f}%")
            
            # Update status and speed
            if status:
                self.status_label.config(text=status)
                if hasattr(self, 'speed_label'):
                    speed = status.split('(')[-1].split(')')[0] if '(' in status else ""
                    self.speed_label.config(text=speed)
                    
        except Exception as e:
            logging.error(f"Progress update error: {str(e)}")

    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

    def setup_menu(self):
        """Simplified menu without location changes"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Download Folder", command=self.open_download_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Legal menu
        legal_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Legal", menu=legal_menu)
        legal_menu.add_command(label="EULA", command=lambda: self.show_legal_doc('EULA.md'))
        legal_menu.add_command(label="Terms of Use", command=lambda: self.show_legal_doc('LICENSE.md'))
        legal_menu.add_command(label="Disclaimer", command=lambda: self.show_legal_doc('DISCLAIMER.md'))
        legal_menu.add_separator()
        legal_menu.add_command(label="YouTube Terms", 
            command=lambda: webbrowser.open('https://www.youtube.com/static?template=terms'))

    def open_download_folder(self):
        """Open downloads folder in explorer"""
        try:
            os.startfile(self.download_path)
        except:
            subprocess.run(['explorer', self.download_path])

    def show_legal_doc(self, filename):
        """Show legal document in scrollable window"""
        try:
            with open(filename, 'r') as f:
                text = f.read()
            self.show_scrolled_text(filename.split('.')[0], text)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load {filename}: {str(e)}")

    def show_legal_notice(self):
        """Show legal notice on first run"""
        legal_text = """LEGAL NOTICE

This software is for personal use only and is not affiliated with YouTube.

By using this software you agree to:
1. Use it for personal, non-commercial purposes only
2. Comply with YouTube's Terms of Service
3. Take full responsibility for downloaded content
4. Not use it for copyright infringement

Continue only if you agree to these terms.
"""
        messagebox.showwarning("Legal Notice", legal_text)

    def show_terms(self):
        """Show full terms of use"""
        with open('LICENSE.md', 'r') as f:
            terms = f.read()
        self.show_scrolled_text("Terms of Use", terms)

    def show_disclaimer(self):
        """Show full disclaimer"""
        with open('DISCLAIMER.md', 'r') as f:
            disclaimer = f.read()
        self.show_scrolled_text("Disclaimer", disclaimer)

    def show_scrolled_text(self, title, text):
        """Show scrollable text window"""
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("600x400")
        
        text_widget = tk.Text(window, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget.insert(tk.END, text)
        text_widget.config(state=tk.DISABLED)

def main():
    root = ThemedTk(theme="arc")  # Using modern theme
    root.resizable(True, True)  # Allow resizing
    root.minsize(800, 500)  # Set minimum size
    app = YouTubeDownloader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
