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
from src.application.use_cases.techwatch_use_cases import LoadDataUseCase
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
    This interface now works with a single, unified database file (techwatch_db.json).
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
        self.load_use_case = LoadDataUseCase(self.post_repository)

        # Interface variables
        self.days_back_var = ctk.IntVar(value=0)
        self.source_var = ctk.StringVar(value="All sources")

        # List to store result URLs
        self.stored_urls = []

        # Current data
        self.current_posts = []
        self.current_metadata = {}

        # Indexes for fast filtering
        self.index_by_source = {}
        self.index_by_date = []
        # LRU cache for filter results
        from collections import OrderedDict
        self.filter_cache = OrderedDict()
        self.cache_max_size = 20
        # Debounce timer
        self.debounce_timer = None
        # Spinner/progress bar
        self.progress_bar = None

        # Lock for thread-safe display
        self.display_lock = threading.Lock()
        # Batch size for progressive rendering
        self.batch_size = 40  # Default value, can be adjusted

        # Track scheduled after callbacks to avoid TclError
        self.scheduled_after_ids = []

        # Create the interface
        self.create_widgets()

        # Logging configuration for the interface
        self.setup_logging()

        # Directly load data from the unified database
        self.load_latest_data()

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
                except Exception:
                    pass

        gui_handler = GuiLogHandler(self)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(gui_handler)

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

    def build_indexes(self):
        """Build indexes for fast filtering (by source, by date)"""
        self.index_by_source.clear()
        self.index_by_date.clear()
        for post in self.current_posts:
            # Index by source
            if post.source:
                self.index_by_source.setdefault(post.source, []).append(post)
            # Index by date
            if post.date:
                self.index_by_date.append(post)
        self.index_by_date.sort(key=lambda p: p.date)

    def show_spinner(self, message="Chargement..."):
        if self.progress_bar:
            self.progress_bar.destroy()
        self.progress_bar = ctk.CTkLabel(self.results_main_frame, text=message, font=ctk.CTkFont(size=16), text_color=self.colors['accent'])
        self.progress_bar.grid(row=0, column=0, columnspan=2, pady=20)

    def hide_spinner(self):
        if self.progress_bar:
            self.progress_bar.destroy()
            self.progress_bar = None

    def load_latest_data(self):
        """
        Load all articles from the unified database and update the interface.
        """
        self.show_spinner("Chargement des données...")
        def load_and_index():
            try:
                result = self.load_use_case.load_latest()
                if result.posts:
                    self.current_posts = [dto.to_entity() for dto in result.posts]
                    self.current_metadata = result.metadata
                    sources = list(set(post.source for post in self.current_posts if post.source))
                    # Schedule all Tkinter widget updates in the main thread
                    self.root.after(0, lambda: self.source_combo.configure(values=["All sources"] + sorted(sources)))
                    self.root.after(0, lambda: self.source_combo.set("All sources"))
                    self.source_post_count = {}
                    for source in sources:
                        self.source_post_count[source] = len([p for p in self.current_posts if p.source == source])
                    self.build_indexes()
                    self.root.after(0, self.hide_spinner)
                    self.root.after(0, self.update_info_display)
                    self.root.after(0, self.apply_filters)
                    self.root.after(0, lambda: self.status_label.configure(text="🟢 Data loaded from techwatch_db.json"))
                else:
                    self.current_posts = []
                    self.current_metadata = {}
                    self.source_post_count = {}
                    self.root.after(0, self.hide_spinner)
                    self.root.after(0, lambda: self.status_label.configure(text="❌ No articles found in techwatch_db.json"))
            except Exception as e:
                logging.error(f"Error loading data: {e}", exc_info=True)
                self.root.after(0, self.hide_spinner)
                # Use a default argument to capture 'e' in the lambda
                self.root.after(0, lambda err=e: self.status_label.configure(text=f"❌ Loading error: {err}"))
        threading.Thread(target=load_and_index, daemon=True).start()

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
        """Apply date and source filters and update the display, with debounce and LRU cache"""
        # Debounce: cancel previous timer if exists
        if self.debounce_timer:
            self.root.after_cancel(self.debounce_timer)
        # Schedule filter after short delay (e.g. 200ms)
        self.debounce_timer = self.root.after(200, self._do_filter)

    def _do_filter(self):
        self.show_spinner("Filtrage en cours...")
        def filter_and_display():
            with self.display_lock:
                if not self.current_posts:
                    self.root.after(0, self.hide_spinner)
                    return
                # Cache key
                cache_key = (self.days_back_var.get(), self.source_var.get())
                # LRU cache: move to end if used, pop oldest if over max size
                if cache_key in self.filter_cache:
                    filtered_posts = self.filter_cache[cache_key]
                    self.filter_cache.move_to_end(cache_key)
                else:
                    from src.domain.services.post_service import PostFilteringService
                    filtering_service = PostFilteringService()
                    filtered_posts = self.current_posts.copy()
                    days_back = self.days_back_var.get()
                    if days_back >= 0:
                        date_range = DateRange.from_days_back(days_back)
                        filtered_posts = filtering_service.filter_by_date_range(filtered_posts, date_range)
                    source_filter = self.source_var.get()
                    filtered_posts = filtering_service.filter_by_source(filtered_posts, source_filter)
                    filtered_posts = filtering_service.sort_by_date(filtered_posts)
                    self.filter_cache[cache_key] = filtered_posts
                    if len(self.filter_cache) > self.cache_max_size:
                        self.filter_cache.popitem(last=False)
                self.displayed_batch_index = 0
                self.displayed_posts = filtered_posts
                self.root.after(0, self.hide_spinner)
                self.root.after(0, lambda: self.status_label.configure(text=f"📊 {len(filtered_posts)}/{len(self.current_posts)} articles displayed"))
                self.root.after(0, self.display_next_batch)
        threading.Thread(target=filter_and_display, daemon=True).start()

    def display_next_batch(self):
        self.show_spinner("Affichage des articles...")
        def batch_render():
            with self.display_lock:
                start = self.displayed_batch_index * self.batch_size
                end = start + self.batch_size
                batch = self.displayed_posts[start:end]
                if not batch and self.displayed_batch_index == 0:
                    self.root.after(0, self.hide_spinner)
                    self.root.after(0, self.show_no_results_message)
                    return
                # Cancel all scheduled after callbacks before clearing display
                for after_id in self.scheduled_after_ids:
                    try:
                        self.root.after_cancel(after_id)
                    except Exception:
                        pass
                self.scheduled_after_ids.clear()
                # Clear display uniquement au début
                if self.displayed_batch_index == 0:
                    def clear_results_area():
                        for widget in self.results_main_frame.winfo_children():
                            widget.destroy()
                        self.left_column_row = 0
                        self.right_column_row = 0
                        self.stored_urls.clear()
                    self.root.after(0, clear_results_area)
                # Affichage progressif par chunk
                after_id = self.root.after(0, lambda: self._render_batch_chunk(batch, 0))
                self.scheduled_after_ids.append(after_id)
        threading.Thread(target=batch_render, daemon=True).start()

    def _render_batch_chunk(self, batch, chunk_index):
        chunk_size = 10
        chunk = batch[chunk_index*chunk_size:(chunk_index+1)*chunk_size]
        sources_attendues = self.source_combo.cget('values')
        if "All sources" in sources_attendues:
            sources_attendues = [s for s in sources_attendues if s != "All sources"]
        posts_by_source = {}
        for post in chunk:
            source = post.source or "Unknown source"
            if source not in posts_by_source:
                posts_by_source[source] = []
            posts_by_source[source].append(post)
        any_result = False
        for source in sources_attendues:
            source_posts = posts_by_source.get(source, [])
            self.display_posts_for_source(source, source_posts)
            if source_posts:
                any_result = True
        if not any_result and self.displayed_batch_index == 0 and chunk_index == 0:
            self.show_no_results_message()
        # Affichage du bouton "Afficher plus" si batch incomplet
        total_len = len(self.displayed_posts)
        end = (self.displayed_batch_index+1)*self.batch_size
        if end < total_len and chunk_index == ((self.batch_size-1)//chunk_size):
            show_more_btn = ctk.CTkButton(
                self.results_main_frame,
                text="Afficher plus d'articles",
                command=self.load_more_batch,
                font=ctk.CTkFont(size=14),
                fg_color=self.colors['accent'],
                hover_color="#2a9fd6"
            )
            show_more_btn.grid(row=max(self.left_column_row, self.right_column_row)+1, column=0, columnspan=2, pady=20)
        # Si il reste des chunks à afficher, planifier le suivant
        if (chunk_index+1)*chunk_size < len(batch):
            after_id = self.root.after(10, lambda: self._render_batch_chunk(batch, chunk_index+1))
            self.scheduled_after_ids.append(after_id)
        else:
            self.hide_spinner()

    def load_more_batch(self):
        """Charge le batch suivant d'articles"""
        with self.display_lock:
            self.displayed_batch_index += 1
            self.display_next_batch()
        # Always destroy and recreate status_frame to avoid stale references and TclError
        import tkinter
        def recreate_status_frame():
            try:
                if hasattr(self, 'status_frame') and self.status_frame.winfo_exists():
                    self.status_frame.destroy()
            except Exception:
                pass  # Ignore if already destroyed
            self.status_frame = ctk.CTkFrame(self.results_main_frame, fg_color="transparent")
            self.status_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)
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
        self.root.after(0, recreate_status_frame)

    def display_filtered_posts(self, posts: List[Post]):
        """Display filtered posts in the interface, with alert for sources sans post (affichage progressif)"""
        # Clear current display only at the start of a batch
        if self.displayed_batch_index == 0:
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
        if not any_result and self.displayed_batch_index == 0:
            self.show_no_results_message()

    def show_welcome_message(self):
        """Display a modern welcome/info card about auto-update and manual generation in the status_frame."""
        for widget in self.status_frame.winfo_children():
            widget.destroy()
        doc_card = ctk.CTkFrame(self.status_frame, corner_radius=14, fg_color=self.colors['secondary'])
        doc_card.pack(fill="x", padx=18, pady=18)

        # Main title
        doc_title = ctk.CTkLabel(
            doc_card,
            text="🚀 Techwatch Auto-Update & Manual Generation",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.colors['text']
        )
        doc_title.pack(pady=(18, 8))

        # Subtitle
        doc_subtitle = ctk.CTkLabel(
            doc_card,
            text="Stay up-to-date automatically or generate new data on demand!",
            font=ctk.CTkFont(size=16, weight="normal"),
            text_color=self.colors['accent']
        )
        doc_subtitle.pack(pady=(0, 12))

        # Features list
        features = [
            ("⏰", "Automatic periodic updates with cron job (autoupdate)"),
            ("🖱️", "Manual data generation with the 'Generate New Data' button"),
            ("🔔", "Desktop notifications for new articles"),
            ("📊", "Unified JSON database for all results"),
            ("🛡️", "Robust logging and error handling")
        ]
        for icon, text in features:
            feature_label = ctk.CTkLabel(
                doc_card,
                text=f"{icon}  {text}",
                font=ctk.CTkFont(size=14),
                text_color=self.colors['text_secondary'],
                anchor="w",
                justify="left"
            )
            feature_label.pack(pady=(2, 2), padx=12, anchor="w")

        # Instructions block
        instructions = (
            "\nTo enable auto-update, run:\n"
            "   make install.autoupdate MINUTES=<N>\n\n"
            "To generate data manually, click the 'Generate New Data' button below.\n"
        )
        doc_instructions = ctk.CTkLabel(
            doc_card,
            text=instructions,
            font=ctk.CTkFont(size=13),
            text_color=self.colors['accent'],
            justify="left"
        )
        doc_instructions.pack(pady=(10, 6), padx=12, anchor="w")

        # Note
        doc_note = ctk.CTkLabel(
            doc_card,
            text="⚠️ No cron job is installed unless you use the autoupdate option.",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['warning']
        )
        doc_note.pack(pady=(0, 10), padx=12, anchor="w")

    def display_posts_for_source(self, source, posts):
        """Affiche tous les posts pour une source donnée dans la zone de résultats, dans la bonne colonne."""
        if not posts:
            return  # Rien à afficher pour cette source
        # Ajout du label de la source
        source_label = ctk.CTkLabel(
            self.results_main_frame,
            text=f"📰 {source}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['accent']
        )
        # Alternance des colonnes : gauche pour pair, droite pour impair
        col = 0 if self.left_column_row <= self.right_column_row else 1
        row = self.left_column_row if col == 0 else self.right_column_row
        source_label.grid(row=row, column=col, sticky="w", padx=10, pady=(10, 2))
        if col == 0:
            self.left_column_row += 1
        else:
            self.right_column_row += 1
        # Affichage de chaque post sous le label source
        for post in posts:
            post_frame = ctk.CTkFrame(self.results_main_frame, corner_radius=8, fg_color="gray15")
            post_frame.grid(row=(self.left_column_row if col == 0 else self.right_column_row), column=col, sticky="ew", padx=10, pady=4)
            # Titre
            title_label = ctk.CTkLabel(
                post_frame,
                text=post.title,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=self.colors['text']
            )
            title_label.pack(anchor="w", padx=8, pady=(6, 2))
            # Date et source
            meta_label = ctk.CTkLabel(
                post_frame,
                text=f"{post.date} • {post.source}",
                font=ctk.CTkFont(size=12),
                text_color=self.colors['text_secondary']
            )
            meta_label.pack(anchor="w", padx=8, pady=(0, 2))
            # Boutons d'action (Open + Copy URL)
            if post.url:
                btn_frame = ctk.CTkFrame(post_frame, fg_color="transparent")
                btn_frame.pack(anchor="w", padx=8, pady=(0, 6))
                link_btn = ctk.CTkButton(
                    btn_frame,
                    text="🔗 Ouvrir l'article",
                    command=lambda url=post.url: self.open_link(url),
                    font=ctk.CTkFont(size=12),
                    fg_color=self.colors['accent'],
                    hover_color="#2a9fd6",
                    height=28,
                    width=120
                )
                link_btn.pack(side="left", padx=(0, 8))
                copy_btn = ctk.CTkButton(
                    btn_frame,
                    text="📋 Copier l'URL",
                    command=lambda url=post.url: self.copy_to_clipboard(url),
                    font=ctk.CTkFont(size=12),
                    fg_color=self.colors['primary'],
                    hover_color=self.colors['secondary'],
                    height=28,
                    width=120
                )
                copy_btn.pack(side="left")
            # Incrémentation de la ligne pour le prochain post
            if col == 0:
                self.left_column_row += 1
            else:
                self.right_column_row += 1

    def copy_to_clipboard(self, url):
        """Copie l'URL dans le presse-papier et affiche une notification."""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(url)
            self.root.update()  # Nécessaire pour que le presse-papier soit mis à jour
            self.status_label.configure(text="✅ URL copiée dans le presse-papier")
            try:
                notification.notify(
                    title="URL copiée",
                    message=url,
                    timeout=3
                )
            except Exception:
                pass
        except Exception as e:
            self.status_label.configure(text=f"❌ Erreur copie: {e}")

    def handle_exception(self, exception_type, exception_value, exception_traceback):
        """Exception handling in the Tkinter interface"""
        error_msg = f"Interface error: {exception_type.__name__}: {exception_value}"
        logging.error(error_msg)
        logging.error("Full traceback:", exc_info=(exception_type, exception_value, exception_traceback))
        # Display the error in the interface if possible
        try:
            self.status_label.configure(text=f"❌ {exception_value}")
        except Exception:
            pass  # If even the status doesn't work, continue

    def force_data_generation(self):
        """Force the generation of new data via the console service"""
        def run_generation():
            try:
                self.root.after(0, lambda: self.status_label.configure(text="⏳ Generating new data..."))
                self.root.after(0, lambda: self.generate_button.configure(state="disabled", text="⏳ Generating..."))

                import subprocess
                import os

                result = subprocess.run(
                    ["python", "techwatch_service.py"],
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=os.getcwd()
                )

                if result.returncode == 0:
                    output_lines = result.stdout.strip().split('\n')
                    articles_count = "new"
                    for line in output_lines:
                        if "articles found" in line:
                            articles_count = line.split("articles found")[0].strip().split()[-1]
                            break
                    self.root.after(0, lambda: self.status_label.configure(text=f"✅ New data generated - {articles_count} articles"))
                    self.root.after(0, lambda: self.load_latest_data())
                    try:
                        notification.notify(
                            title="🔍 Technology Watch",
                            message=f"✅ New data generated with {articles_count} articles",
                            timeout=10
                        )
                    except Exception:
                        pass
                else:
                    error_msg = result.stderr or "Unknown error during generation"
                    self.root.after(0, lambda: self.status_label.configure(text=f"❌ Error: {error_msg[:50]}..."))

            except subprocess.TimeoutExpired:
                self.root.after(0, lambda: self.status_label.configure(text="❌ Timeout: generation too long"))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.status_label.configure(text=f"❌ Error: {error_msg[:50]}..."))
                logging.error(f"Error generating data: {e}", exc_info=True)
            finally:
                self.root.after(0, lambda: self.generate_button.configure(state="normal", text="Generate new data"))

        # Start generation in a separate thread to avoid blocking the interface
        generation_thread = threading.Thread(target=run_generation, daemon=True)
        generation_thread.start()

    def run(self):
        """Launch the modern graphical interface"""
        self.root.mainloop()

def main():
    """Entry point of the modern GUI application"""
    print("[DEBUG] main() started")
    app = TechWatchGUI()
    print("[DEBUG] TechWatchGUI instance created, starting mainloop...")
    app.run()
    print("[DEBUG] mainloop finished")

if __name__ == "__main__":
    main()
