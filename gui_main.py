#!/usr/bin/env python3
"""
Modern GUI interface for the technology watch tool
Desktop application based on CustomTkinter with modern design and dark theme
VERSION 2.0 - JSON files reading only (no direct crawling)
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
import logging
from datetime import datetime, date
from typing import List, Optional
import webbrowser
import re
import os
from plyer import notification

# Imports from the new hexagonal DDD architecture
from src.application.use_cases.veille_use_cases import LoadVeilleDataUseCase
from src.application.dto.post_dto import PostDTO, WatchResultDTO
from src.infrastructure.repositories.json_post_repository import JsonPostRepository
from src.domain.entities.post import Post
from src.domain.value_objects.date_range import DateRange

# CustomTkinter theme configuration
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class TechWatchGUI:
    """
    Modern GUI interface for technology watch results consultation.
    This interface now works with a single, unified database file (veille_db.json).
    All articles are loaded from this file, and file selection is no longer required.
    """

    def __init__(self):
        # Create logs folder if it doesn't exist
        os.makedirs('var/logs', exist_ok=True)

        # Global logging configuration to capture all errors
        self.setup_global_logging()

        self.root = ctk.CTk()
        self.root.title("🔍 Technology Watch Tool - Consultation")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)

        # Handle uncaught exceptions in the interface
        self.root.report_callback_exception = self.handle_exception

        # Custom colors configuration
        self.colors = {
            'primary': "#1f538d",
            'secondary': "#14375e",
            'accent': "#36719f",
            'success': "#2d7d32",
            'warning': "#f57f17",
            'error': "#c62828",
            'text': "#ffffff",
            'text_secondary': "#b0b0b0"
        }

        # Dependency injection - Hexagonal Architecture DDD
        self.post_repository = JsonPostRepository()
        self.load_use_case = LoadVeilleDataUseCase(self.post_repository)

        # Interface variables
        self.days_back_var = ctk.IntVar(value=0)
        self.source_var = ctk.StringVar(value="All sources")

        # List to store result URLs
        self.stored_urls = []

        # Current data
        self.current_posts = []
        self.current_metadata = {}

        # Create the interface
        self.create_widgets()

        # Logging configuration for the interface
        self.setup_logging()

        # Directly load data from the unified database
        self.load_latest_data()

    def create_widgets(self):
        """
        Create all widgets for the modern interface.
        The file selection ComboBox has been removed; only filtering options remain.
        """
        # Main grid configuration
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # === Header with title and icon ===
        header_frame = ctk.CTkFrame(self.root, height=80, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_propagate(False)

        title_label = ctk.CTkLabel(
            header_frame,
            text="🔍 Technology Watch - Consultation",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors['text']
        )
        title_label.grid(row=0, column=0, pady=20)

        # === Main frame ===
        main_frame = ctk.CTkFrame(self.root, corner_radius=0)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # === Configuration panel (left) ===
        config_frame = ctk.CTkFrame(main_frame, width=350, corner_radius=10)
        config_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(20, 10), pady=20)
        config_frame.grid_propagate(False)

        # Configuration title
        config_title = ctk.CTkLabel(
            config_frame,
            text="⚙️ Configuration",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        config_title.pack(pady=(20, 30))

        # Period selection
        period_label = ctk.CTkLabel(
            config_frame,
            text="📅 Period Filtering",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        period_label.pack(pady=(0, 15))

        # Radio buttons for periods with modern style
        periods = [
            ("All articles", -1),
            ("Today", 0),
            ("Yesterday", 1),  # Added yesterday filter
            ("2 days", 2),
            ("7 days", 6),
            ("30 days", 29)
        ]

        for text, value in periods:
            radio = ctk.CTkRadioButton(
                config_frame,
                text=text,
                variable=self.days_back_var,
                value=value,
                command=self.apply_filters,
                font=ctk.CTkFont(size=14)
            )
            radio.pack(pady=5, padx=20, anchor="w")

        # Source selection
        source_label = ctk.CTkLabel(
            config_frame,
            text="🎯 Source Filtering",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        source_label.pack(pady=(30, 15))

        self.source_combo = ctk.CTkComboBox(
            config_frame,
            values=["All sources"],
            variable=self.source_var,
            command=self.apply_filters,
            width=300,
            font=ctk.CTkFont(size=14)
        )
        self.source_combo.pack(pady=10, padx=20)

        # Action buttons
        buttons_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        buttons_frame.pack(pady=(40, 20), fill="x", padx=20)

        # Button to force data generation
        self.generate_button = ctk.CTkButton(
            buttons_frame,
            text="🔄 Generate New Data",
            command=self.force_data_generation,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary']
        )
        self.generate_button.pack(fill="x")

        # === Results area with tabs (right) ===
        results_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        results_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(10, 20), pady=20)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(1, weight=1)

        # Results header
        results_header = ctk.CTkLabel(
            results_frame,
            text="📊 Watch Results",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        results_header.grid(row=0, column=0, pady=(20, 10))

        # Modern tabs
        self.tabview = ctk.CTkTabview(results_frame, width=700, height=600)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        # Results tab with two columns
        self.tabview.add("📰 Results")

        # Main frame for results with scrollbar
        self.results_main_frame = ctk.CTkScrollableFrame(
            self.tabview.tab("📰 Results"),
            corner_radius=8
        )
        self.results_main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Grid configuration for two columns
        self.results_main_frame.grid_columnconfigure(0, weight=1)
        self.results_main_frame.grid_columnconfigure(1, weight=1)

        # Variables to track positions in columns
        self.left_column_row = 0
        self.right_column_row = 0

        # Frame for status messages (welcome, errors)
        self.status_frame = ctk.CTkFrame(self.results_main_frame, fg_color="transparent")
        self.status_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)

        # Metadata tab
        self.tabview.add("📋 Information")
        self.info_textbox = ctk.CTkTextbox(
            self.tabview.tab("📋 Information"),
            wrap="word",
            corner_radius=8
        )
        self.info_textbox.pack(fill="both", expand=True, padx=10, pady=10)

        # === Modern status bar ===
        status_frame = ctk.CTkFrame(self.root, height=40, corner_radius=0)
        status_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        status_frame.grid_columnconfigure(0, weight=1)
        status_frame.grid_propagate(False)

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="🟢 Ready",
            font=ctk.CTkFont(size=14),
            anchor="w"
        )
        self.status_label.grid(row=0, column=0, sticky="w", padx=20, pady=8)

        # Welcome message
        self.show_welcome_message()

    def load_latest_data(self):
        """
        Load all articles from the unified database and update the interface.
        """
        try:
            # Using the new hexagonal use case
            result = self.load_use_case.load_latest()
            if result.posts:
                # Convert DTOs to entities for display
                self.current_posts = [dto.to_entity() for dto in result.posts]
                self.current_metadata = result.metadata

                # Update available sources
                sources = list(set(post.source for post in self.current_posts if post.source))
                # Update source ComboBox
                self.source_combo.configure(values=["All sources"] + sorted(sources))
                self.source_combo.set("All sources")

                # Calculer le nombre total de posts par source (all time)
                self.source_post_count = {}
                for source in sources:
                    self.source_post_count[source] = len([p for p in self.current_posts if p.source == source])

                # Display information
                self.update_info_display()
                self.apply_filters()

                self.status_label.configure(text="🟢 Data loaded from veille_db.json")
            else:
                self.current_posts = []
                self.current_metadata = {}
                self.source_post_count = {}
                self.status_label.configure(text="❌ No articles found in veille_db.json")
        except Exception as e:
            logging.error(f"Error loading data: {e}", exc_info=True)
            self.status_label.configure(text=f"❌ Loading error: {e}")

    def update_info_display(self):
        """Update the display of information/metadata"""
        info_text = f"""📊 WATCH INFORMATION

📅 Generated on: {self.current_metadata.get('generated_at', 'Unknown')}
📈 Total articles: {self.current_metadata.get('total_articles', len(self.current_posts))}
🏷️ Format version: {self.current_metadata.get('format_version', 'Not specified')}

🎯 CRAWLED SOURCES:
"""

        sources = self.current_metadata.get('sources', [])
        if sources:
            for source in sorted(sources):
                count = len([p for p in self.current_posts if p.source == source])
                info_text += f"  • {source} ({count} articles)\n"
        else:
            info_text += "  No source specified\n"

        date_range = self.current_metadata.get('date_range', {})
        if date_range.get('earliest') and date_range.get('latest'):
            info_text += f"""
📅 DATE RANGE:
  From: {date_range['earliest']}
  To: {date_range['latest']}
"""

        self.info_textbox.delete("0.0", "end")
        self.info_textbox.insert("0.0", info_text)

    def apply_filters(self, *args):
        """Apply date and source filters and update the display"""
        try:
            if not self.current_posts:
                return

            # Using domain services for filtering
            from src.domain.services.post_service import PostFilteringService
            filtering_service = PostFilteringService()

            filtered_posts = self.current_posts.copy()

            # Date range filtering
            days_back = self.days_back_var.get()
            if days_back >= 0:  # -1 = all articles
                date_range = DateRange.from_days_back(days_back)
                filtered_posts = filtering_service.filter_by_date_range(filtered_posts, date_range)

            # Source filtering
            source_filter = self.source_var.get()
            filtered_posts = filtering_service.filter_by_source(filtered_posts, source_filter)

            # Sort by date
            filtered_posts = filtering_service.sort_by_date(filtered_posts)

            # Display filtered results
            self.display_filtered_posts(filtered_posts)

            # Update status
            total = len(self.current_posts)
            filtered = len(filtered_posts)
            self.status_label.configure(text=f"📊 {filtered}/{total} articles displayed")

        except Exception as e:
            logging.error(f"Error filtering: {e}", exc_info=True)
            self.status_label.configure(text=f"❌ Filtering error: {e}")

    def display_filtered_posts(self, posts: List[Post]):
        """Display filtered posts in the interface, with alert for sources sans post"""
        # Clear current display
        for widget in self.results_main_frame.winfo_children():
            widget.destroy()
        self.left_column_row = 0
        self.right_column_row = 0
        self.stored_urls.clear()

        # Récupérer toutes les sources attendues
        sources_attendues = self.source_combo.cget('values')
        if "All sources" in sources_attendues:
            sources_attendues = [s for s in sources_attendues if s != "All sources"]

        # Group posts by source
        posts_by_source = {}
        for post in posts:
            source = post.source or "Unknown source"
            if source not in posts_by_source:
                posts_by_source[source] = []
            posts_by_source[source].append(post)

        # Afficher les résultats pour chaque source attendue
        any_result = False
        for source in sources_attendues:
            source_posts = posts_by_source.get(source, [])
            self.display_posts_for_source(source, source_posts)
            if source_posts:
                any_result = True
        if not any_result:
            self.show_no_results_message()

    def display_posts_for_source(self, source_name: str, posts: List[Post]):
        """Display posts from a given source"""
        # Si aucun post filtré ET aucun post all time, afficher le bloc d'alerte
        has_alert = hasattr(self, 'source_post_count') and self.source_post_count.get(source_name, 0) == 0
        if not posts and not has_alert:
            # Ne rien afficher si pas d'alerte et pas de post filtré
            return
        # Create a header for the source
        source_header = ctk.CTkFrame(self.results_main_frame, corner_radius=8, fg_color=self.colors['primary'])
        current_row = max(self.left_column_row, self.right_column_row)
        source_header.grid(row=current_row, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))

        # Source title
        source_label_text = f"📍 {source_name} ({len(posts)} articles)"
        source_label = ctk.CTkLabel(
            source_header,
            text=source_label_text,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        source_label.pack(pady=10)

        # Affichage de l'alerte non intrusive si le crawler n'a jamais eu de post
        if has_alert:
            alert_label = ctk.CTkLabel(
                source_header,
                text="⚠️ Aucun article trouvé pour cette source depuis le début. Veuillez vérifier le crawler.",
                font=ctk.CTkFont(size=13, weight="normal"),
                text_color=self.colors['warning']
            )
            alert_label.pack(pady=(0, 10))

        # Increment row for next cards
        self.left_column_row = current_row + 1
        self.right_column_row = current_row + 1

        # Display each post in columns
        for post in posts:
            # Determine column (alternating)
            if self.left_column_row <= self.right_column_row:
                column = 0
                row = self.left_column_row
                self.left_column_row += 1
            else:
                column = 1
                row = self.right_column_row
                self.right_column_row += 1

            # Create post card
            post_card = ctk.CTkFrame(self.results_main_frame, corner_radius=8, fg_color="gray15")
            post_card.grid(row=row, column=column, sticky="ew", padx=10, pady=5)

            # Title with wrapping
            title_label = ctk.CTkLabel(
                post_card,
                text=post.title,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=self.colors['text'],
                wraplength=250,  # Limit width for wrapping
                anchor="w",
                justify="left"
            )
            title_label.pack(anchor="w", padx=12, pady=(12, 8), fill="x")

            # Store URL and create button
            self.stored_urls.append(post.url)

            # Frame for button and date
            info_frame = ctk.CTkFrame(post_card, fg_color="transparent")
            info_frame.pack(fill="x", padx=12, pady=(0, 12))

            link_button = ctk.CTkButton(
                info_frame,
                text="🔗 Read article",
                command=lambda url=post.url: self.open_link(url),
                font=ctk.CTkFont(size=11),
                fg_color=self.colors['accent'],
                hover_color="#2a9fd6",
                height=28,
                width=100
            )
            link_button.pack(side="left")

            # Display post date
            if post.date:
                date_info = ctk.CTkLabel(
                    info_frame,
                    text=f"📅 {post.date}",
                    font=ctk.CTkFont(size=10),
                    text_color=self.colors['text_secondary']
                )
                date_info.pack(side="right", padx=(10, 0))

    def show_welcome_message(self):
        """Display the modern welcome message - only if no data is loaded"""
        # Do not show welcome message if data is already loaded
        if hasattr(self, 'current_posts') and self.current_posts:
            return

        # Clear previous content of status_frame only
        for widget in self.status_frame.winfo_children():
            widget.destroy()

        # Create welcome card
        welcome_card = ctk.CTkFrame(self.status_frame, corner_radius=10, fg_color="gray20")
        welcome_card.pack(fill="x", padx=10, pady=10)

        welcome_title = ctk.CTkLabel(
            welcome_card,
            text="🎉 Welcome to the Watch Results Consultation Interface!",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['text']
        )
        welcome_title.pack(pady=(15, 10))

        welcome_desc = ctk.CTkLabel(
            welcome_card,
            text="📖 This interface reads JSON files generated by the console watch service",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['text_secondary']
        )
        welcome_desc.pack(pady=(0, 5))

        instructions = ctk.CTkLabel(
            welcome_card,
            text="📋 1️⃣ Select a file • 2️⃣ Filter by period/source • 3️⃣ View results",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        )
        instructions.pack(pady=(0, 15))

    def show_no_data_message(self):
        """Display a message when no data is available"""
        # Clear previous content
        for widget in self.status_frame.winfo_children():
            widget.destroy()

        # Create no data card
        no_data_card = ctk.CTkFrame(self.status_frame, corner_radius=10, fg_color="gray20")
        no_data_card.pack(fill="x", padx=10, pady=10)

        no_data_title = ctk.CTkLabel(
            no_data_card,
            text="📭 No watch data available",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['warning']
        )
        no_data_title.pack(pady=(15, 10))

        instructions = ctk.CTkLabel(
            no_data_card,
            text="💡 First, run the console service to generate watch data",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['text_secondary']
        )
        instructions.pack(pady=(0, 15))

    def show_no_results_message(self):
        """Display a message when no results match the filters"""
        no_results_frame = ctk.CTkFrame(self.results_main_frame, corner_radius=8, fg_color="gray20")
        no_results_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        no_results_label = ctk.CTkLabel(
            no_results_frame,
            text="🔍 No article matches the selected filters",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['warning']
        )
        no_results_label.pack(pady=15)

    def open_link(self, url: str):
        """Open a link in the browser with feedback"""
        try:
            webbrowser.open(url)
            self.status_label.configure(text="🌐 Article opened in browser...")
        except Exception as e:
            self.status_label.configure(text=f"❌ Error opening: {str(e)}")

    def setup_global_logging(self):
        """Global logging configuration to capture all errors"""
        import sys

        # Main logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('var/logs/gui_main.log'),
                logging.StreamHandler()
            ]
        )

        # Handler for uncaught exceptions
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            logging.critical("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))

        sys.excepthook = handle_exception

    def handle_exception(self, exception_type, exception_value, exception_traceback):
        """Exception handling in the Tkinter interface"""
        error_msg = f"Interface error: {exception_type.__name__}: {exception_value}"
        logging.error(error_msg)
        logging.error("Full traceback:", exc_info=(exception_type, exception_value, exception_traceback))

        # Display the error in the interface if possible
        try:
            self.status_label.configure(text=f"❌ {exception_value}")
        except:
            pass  # If even the status doesn't work, continue

    def setup_logging(self):
        """Logging configuration for the graphical interface"""
        class GuiLogHandler(logging.Handler):
            def __init__(self, gui_instance):
                super().__init__()
                self.gui = gui_instance

            def emit(self, record):
                msg = self.format(record)
                # Write to GUI log file
                try:
                    with open('var/logs/gui_events.log', 'a', encoding='utf-8') as f:
                        f.write(f"{msg}\n")
                except:
                    pass

        gui_handler = GuiLogHandler(self)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(gui_handler)

    def run(self):
        """Launch the modern graphical interface"""
        # Full initialization at startup
        self.refresh_file_list()

        # Start the main loop
        self.root.mainloop()

    def refresh_file_list(self):
        """
        Refresh the technology watch data from the unified database file.
        This replaces the old file selection logic and ensures the latest data is loaded.
        """
        self.load_latest_data()
        # Optionally, update the GUI display if needed
        # Example: self.update_display()

    def force_data_generation(self):
        """Force the generation of new data via the console service"""
        def run_generation():
            try:
                # Update status on the main thread
                self.root.after(0, lambda: self.status_label.configure(text="⏳ Generating new data..."))
                self.root.after(0, lambda: self.generate_button.configure(state="disabled", text="⏳ Generating..."))

                # Launch the console service to generate new data
                import subprocess
                import os

                # Path to the virtual environment and script
                venv_python = os.path.join(os.getcwd(), ".venv", "bin", "python")
                service_script = os.path.join(os.getcwd(), "veille_service.py")

                command = [venv_python, service_script]

                # Execute the console service
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minutes timeout
                    cwd=os.getcwd()
                )

                if result.returncode == 0:
                    # Success - extract the number of articles from the output
                    output_lines = result.stdout.strip().split('\n')
                    articles_count = "new"
                    for line in output_lines:
                        if "articles found" in line:
                            articles_count = line.split("articles found")[0].strip().split()[-1]
                            break

                    # Update interface on the main thread
                    self.root.after(0, lambda: self.status_label.configure(text=f"✅ New data generated - {articles_count} articles"))
                    self.root.after(0, lambda: self.refresh_file_list())

                    # Success notification
                    try:
                        notification.notify(
                            title="🔍 Technology Watch",
                            message=f"✅ New data generated with {articles_count} articles",
                            timeout=10
                        )
                    except:
                        pass  # Optional notification

                else:
                    # Error during execution
                    error_msg = result.stderr or "Unknown error during generation"
                    self.root.after(0, lambda: self.status_label.configure(text=f"❌ Error: {error_msg[:50]}..."))

            except subprocess.TimeoutExpired:
                self.root.after(0, lambda: self.status_label.configure(text="❌ Timeout: generation too long"))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.status_label.configure(text=f"❌ Error: {error_msg[:50]}..."))
                logging.error(f"Error generating data: {e}", exc_info=True)
            finally:
                # Reactivate button on the main thread
                self.root.after(0, lambda: self.generate_button.configure(state="normal", text="🔄 Generate New Data"))

        # Start generation in a separate thread to avoid blocking the interface
        generation_thread = threading.Thread(target=run_generation, daemon=True)
        generation_thread.start()

def main():
    """Entry point of the modern GUI application"""
    app = TechWatchGUI()
    app.run()

if __name__ == "__main__":
    main()
