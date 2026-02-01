"""
Bin Day Brain - Wollongong Smart Bin Reminders
A smart desktop utility for tracking bin collection days with weather-aware alerts.
"""

import customtkinter as ctk
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import sys
import threading
from PIL import Image, ImageTk

# Constants
API_BASE = "https://wollongong.waste-info.com.au/api/v1"
WEATHER_API = "https://api.open-meteo.com/v1/forecast"
WOLLONGONG_LAT = -34.4278
WOLLONGONG_LON = 150.8931
CONFIG_FILE = "config.json"
CACHE_FILE = "cache.json"

# Weather thresholds
WIND_WARNING_KMH = 40  # Warn about bin blowover above this wind speed
RAIN_ADVISORY_MM = 5   # Suggest adding weight to FOGO if rain expected

# CustomTkinter appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Copyright
COPYRIGHT = "© 2026 Scott Leimroth"


class AutocompleteCombobox(ctk.CTkFrame):
    """A combobox with autocomplete/type-ahead functionality using a popup listbox"""

    def __init__(self, master, values=None, command=None, placeholder="Type to search...", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.values = values or []
        self.filtered_values = self.values.copy()
        self.command = command
        self.placeholder = placeholder
        self.dropdown_window = None
        self.listbox = None
        self._enabled = True

        # Entry field
        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder)
        self.entry.pack(fill="x")
        self.entry.bind("<KeyRelease>", self._on_key_release)
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<Down>", self._on_arrow_down)
        self.entry.bind("<Return>", self._on_enter)
        self.entry.bind("<Escape>", self._on_escape)

    def configure(self, **kwargs):
        """Configure the widget"""
        if "values" in kwargs:
            self.values = kwargs.pop("values")
            self.filtered_values = self.values.copy()
        if "state" in kwargs:
            state = kwargs.pop("state")
            self._enabled = (state == "normal")
            self.entry.configure(state=state)
        super().configure(**kwargs)

    def set(self, value):
        """Set the entry value"""
        current_state = self.entry.cget("state")
        if current_state == "disabled":
            self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        self.entry.insert(0, value)
        if current_state == "disabled":
            self.entry.configure(state="disabled")

    def get(self):
        """Get the current value"""
        return self.entry.get()

    def _on_key_release(self, event):
        """Filter options as user types"""
        if event.keysym in ("Up", "Down", "Return", "Escape"):
            return

        typed = self.entry.get().lower()
        if typed:
            self.filtered_values = [v for v in self.values if typed in v.lower()]
        else:
            self.filtered_values = self.values.copy()

        self._show_dropdown()

    def _on_focus_in(self, event):
        """Show dropdown when entry gets focus"""
        if self._enabled and self.values:
            self.filtered_values = self.values.copy()
            self._show_dropdown()

    def _on_focus_out(self, event):
        """Hide dropdown when focus lost"""
        self.after(150, self._hide_dropdown)

    def _on_arrow_down(self, event):
        """Handle down arrow - move selection in listbox"""
        if self.listbox and self.dropdown_window:
            self.listbox.focus_set()
            if self.listbox.size() > 0:
                self.listbox.selection_clear(0, "end")
                self.listbox.selection_set(0)
                self.listbox.activate(0)
        return "break"

    def _on_enter(self, event):
        """Handle enter key - select first match"""
        if self.filtered_values:
            self._select_value(self.filtered_values[0])
        return "break"

    def _on_escape(self, event):
        """Handle escape key - hide dropdown"""
        self._hide_dropdown()
        return "break"

    def _show_dropdown(self):
        """Show the dropdown list as a popup window"""
        if not self.filtered_values:
            self._hide_dropdown()
            return

        # Create or update dropdown window
        if self.dropdown_window is None or not self.dropdown_window.winfo_exists():
            self.dropdown_window = ctk.CTkToplevel(self)
            self.dropdown_window.withdraw()
            self.dropdown_window.overrideredirect(True)
            self.dropdown_window.attributes("-topmost", True)

            # Create listbox with scrollbar
            frame = ctk.CTkFrame(self.dropdown_window, fg_color="white", border_width=1, border_color="gray70")
            frame.pack(fill="both", expand=True)

            self.listbox = ctk.CTkScrollableFrame(frame, fg_color="white", height=200)
            self.listbox.pack(fill="both", expand=True, padx=1, pady=1)

        # Clear existing items
        for widget in self.listbox.winfo_children():
            widget.destroy()

        # Add all filtered items (no limit)
        for value in self.filtered_values:
            btn = ctk.CTkButton(
                self.listbox,
                text=value,
                anchor="w",
                fg_color="transparent",
                text_color="black",
                hover_color="#e3f2fd",
                height=28,
                corner_radius=0,
                command=lambda v=value: self._select_value(v)
            )
            btn.pack(fill="x", padx=0, pady=0)

        # Position dropdown below entry
        self.update_idletasks()
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        width = self.entry.winfo_width()

        self.dropdown_window.geometry(f"{width}x220+{x}+{y}")
        self.dropdown_window.deiconify()

    def _hide_dropdown(self):
        """Hide the dropdown list"""
        if self.dropdown_window and self.dropdown_window.winfo_exists():
            self.dropdown_window.withdraw()

    def _select_value(self, value):
        """Handle selection of a value"""
        self.entry.delete(0, "end")
        self.entry.insert(0, value)
        self._hide_dropdown()
        if self.command:
            self.command(value)


class WeatherAPI:
    """Handle weather data from Open-Meteo (free, no API key required)"""

    @staticmethod
    def get_forecast(days_ahead: int = 0) -> Optional[Dict]:
        """Get weather forecast for a specific day (0 = today, 1 = tomorrow, etc.)"""
        try:
            target_date = datetime.now() + timedelta(days=days_ahead)
            response = requests.get(
                WEATHER_API,
                params={
                    "latitude": WOLLONGONG_LAT,
                    "longitude": WOLLONGONG_LON,
                    "daily": "precipitation_sum,wind_speed_10m_max,weather_code",
                    "timezone": "Australia/Sydney",
                    "forecast_days": days_ahead + 1
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            daily = data.get('daily', {})
            if daily and days_ahead < len(daily.get('time', [])):
                return {
                    'date': daily['time'][days_ahead],
                    'rain_mm': daily['precipitation_sum'][days_ahead],
                    'wind_kmh': daily['wind_speed_10m_max'][days_ahead],
                    'weather_code': daily['weather_code'][days_ahead]
                }
            return None
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return None

    @staticmethod
    def get_weather_alerts(collection_date: datetime) -> List[Dict]:
        """Get weather-based alerts for a collection day"""
        alerts = []
        days_ahead = (collection_date.date() - datetime.now().date()).days

        if days_ahead < 0 or days_ahead > 7:
            return alerts

        forecast = WeatherAPI.get_forecast(days_ahead)
        if not forecast:
            return alerts

        # Wind warning - bins might blow over
        wind = forecast.get('wind_kmh', 0)
        if wind and wind >= WIND_WARNING_KMH:
            alerts.append({
                'type': 'wind',
                'severity': 'warning' if wind >= 50 else 'info',
                'message': f"Windy ({int(wind)} km/h) - secure your bins!",
                'icon': 'wind'
            })

        # Rain advisory for FOGO - wet garden waste is heavier
        rain = forecast.get('rain_mm', 0)
        if rain and rain >= RAIN_ADVISORY_MM:
            alerts.append({
                'type': 'rain',
                'severity': 'info',
                'message': f"Rain expected ({int(rain)}mm) - good for weighing down FOGO",
                'icon': 'rain'
            })

        return alerts


class WasteAPI:
    """Handle all API interactions with Wollongong Waste Info"""

    @staticmethod
    def get_localities() -> Optional[List[Dict]]:
        """Fetch all available localities"""
        try:
            response = requests.get(f"{API_BASE}/localities.json", timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('localities', [])
        except Exception as e:
            print(f"Error fetching localities: {e}")
            return None

    @staticmethod
    def get_streets(locality_id: int) -> Optional[List[Dict]]:
        """Fetch streets for a given locality"""
        try:
            response = requests.get(
                f"{API_BASE}/streets.json",
                params={"locality": locality_id},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get('streets', [])
        except Exception as e:
            print(f"Error fetching streets: {e}")
            return None

    @staticmethod
    def get_properties(street_id: int) -> Optional[List[Dict]]:
        """Fetch properties for a given street"""
        try:
            response = requests.get(
                f"{API_BASE}/properties.json",
                params={"street": street_id},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get('properties', [])
        except Exception as e:
            print(f"Error fetching properties: {e}")
            return None

    @staticmethod
    def get_collection_data(property_id: int) -> Optional[Dict]:
        """Fetch collection schedule for a property"""
        try:
            response = requests.get(
                f"{API_BASE}/properties/{property_id}.json",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            # If API returns empty collections, calculate from collection_day
            if not data.get('collections') and data.get('collection_day'):
                data['collections'] = WasteAPI._calculate_collections(data['collection_day'])

            return data
        except Exception as e:
            print(f"Error fetching collection data: {e}")
            return None

    @staticmethod
    def _calculate_collections(collection_day: int) -> List[Dict]:
        """Calculate collection dates from collection_day (1=Mon, 2=Tue, etc.)"""
        today = datetime.now()

        # Find next occurrence of collection day (API uses 1=Mon, Python uses 0=Mon)
        days_ahead = (collection_day - 1) - today.weekday()
        if days_ahead < 0:
            days_ahead += 7
        next_collection = today + timedelta(days=days_ahead)

        # FOGO is weekly, Recycling/Landfill alternate fortnightly
        # Use week number to determine which bin (even week = recycling, odd = landfill)
        week_num = next_collection.isocalendar()[1]
        is_recycling_week = (week_num % 2 == 0)

        collections = [
            {
                'type': 'FOGO',
                'next': {'date': next_collection.strftime('%Y-%m-%dT06:00:00+11:00')}
            },
            {
                'type': 'Recycling',
                'next': {'date': (next_collection if is_recycling_week else next_collection + timedelta(days=7)).strftime('%Y-%m-%dT06:00:00+11:00')}
            },
            {
                'type': 'Landfill',
                'next': {'date': (next_collection if not is_recycling_week else next_collection + timedelta(days=7)).strftime('%Y-%m-%dT06:00:00+11:00')}
            }
        ]
        return collections

    @staticmethod
    def get_materials() -> Optional[List[Dict]]:
        """Fetch A-Z waste guide materials"""
        try:
            response = requests.get(f"{API_BASE}/materials.json", timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('materials', [])
        except Exception as e:
            print(f"Error fetching materials: {e}")
            return None

    @staticmethod
    def get_events() -> Optional[List[Dict]]:
        """Fetch upcoming events"""
        try:
            response = requests.get(f"{API_BASE}/events.json", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching events: {e}")
            return None


class Config:
    """Manage app configuration"""

    @staticmethod
    def load() -> Optional[Dict]:
        """Load config from file"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
        return None

    @staticmethod
    def save(data: Dict):
        """Save config to file"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")


class Cache:
    """Manage collection data cache"""

    @staticmethod
    def load() -> Optional[Dict]:
        """Load cache from file"""
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cache: {e}")
        return None

    @staticmethod
    def save(data: Dict):
        """Save cache to file"""
        try:
            data['cached_at'] = datetime.now().isoformat()
            with open(CACHE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")


class SetupWizard(ctk.CTkToplevel):
    """First-run setup wizard to find user's property"""

    def __init__(self, parent, on_complete):
        super().__init__(parent)
        self.on_complete = on_complete

        self.title("Bin Day Brain - Setup")
        self.geometry("600x580")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Data
        self.localities = []
        self.streets = []
        self.properties = []
        self.selected_property_id = None

        # UI
        self.create_ui()
        self.load_localities()

    def create_ui(self):
        """Create wizard UI"""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Welcome to Bin Day Brain!",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)

        subtitle = ctk.CTkLabel(
            self,
            text="Let's find your address for smart bin reminders",
            font=ctk.CTkFont(size=14)
        )
        subtitle.pack(pady=10)

        # Form frame
        form = ctk.CTkFrame(self)
        form.pack(pady=20, padx=40, fill="both", expand=True)

        # Locality
        ctk.CTkLabel(form, text="Suburb/Locality:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(20, 5))
        self.locality_combo = AutocompleteCombobox(
            form,
            values=[],
            command=self.on_locality_selected,
            placeholder="Loading..."
        )
        self.locality_combo.pack(pady=5, padx=20, fill="x")
        self.locality_combo.configure(state="disabled")

        # Street
        ctk.CTkLabel(form, text="Street:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(20, 5))
        self.street_combo = AutocompleteCombobox(
            form,
            values=[],
            command=self.on_street_selected,
            placeholder="Select suburb first..."
        )
        self.street_combo.pack(pady=5, padx=20, fill="x")
        self.street_combo.configure(state="disabled")

        # Property
        ctk.CTkLabel(form, text="Property Number:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(20, 5))
        self.property_combo = AutocompleteCombobox(
            form,
            values=[],
            command=self.on_property_selected,
            placeholder="Select street first..."
        )
        self.property_combo.pack(pady=5, padx=20, fill="x")
        self.property_combo.configure(state="disabled")

        # Status
        self.status_label = ctk.CTkLabel(
            form,
            text="",
            text_color="gray"
        )
        self.status_label.pack(pady=20)

        # Complete button
        self.complete_btn = ctk.CTkButton(
            self,
            text="Complete Setup",
            command=self.complete_setup,
            state="disabled",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.complete_btn.pack(pady=20, padx=40, fill="x")

    def load_localities(self):
        """Load localities from API"""
        self.status_label.configure(text="Loading localities...")
        localities = WasteAPI.get_localities()

        if localities:
            self.localities = sorted(localities, key=lambda x: x.get('name', ''))
            locality_names = [loc['name'] for loc in self.localities]
            self.locality_combo.configure(values=locality_names, state="normal")
            self.locality_combo.set("")
            self.status_label.configure(text="")
        else:
            self.status_label.configure(
                text="Error: Could not connect to server. Check internet connection.",
                text_color="red"
            )

    def on_locality_selected(self, choice):
        """Handle locality selection"""
        locality = next((loc for loc in self.localities if loc['name'] == choice), None)
        if not locality:
            return

        self.street_combo.configure(values=[], state="disabled")
        self.property_combo.configure(values=[], state="disabled")
        self.complete_btn.configure(state="disabled")

        self.status_label.configure(text="Loading streets...")
        streets = WasteAPI.get_streets(locality['id'])

        if streets:
            self.streets = sorted(streets, key=lambda x: x.get('name', ''))
            street_names = [street['name'] for street in self.streets]
            self.street_combo.configure(values=street_names, state="normal")
            self.street_combo.set("")
            self.status_label.configure(text="")
        else:
            self.status_label.configure(text="Error loading streets", text_color="red")

    def on_street_selected(self, choice):
        """Handle street selection"""
        street = next((s for s in self.streets if s['name'] == choice), None)
        if not street:
            return

        self.property_combo.configure(values=[], state="disabled")
        self.complete_btn.configure(state="disabled")

        self.status_label.configure(text="Loading properties...")
        properties = WasteAPI.get_properties(street['id'])

        if properties:
            self.properties = sorted(properties, key=lambda x: x.get('name', ''))
            property_names = [prop['name'] for prop in self.properties]
            self.property_combo.configure(values=property_names, state="normal")
            self.property_combo.set("")
            self.status_label.configure(text="")
        else:
            self.status_label.configure(text="Error loading properties", text_color="red")

    def on_property_selected(self, choice):
        """Handle property selection"""
        prop = next((p for p in self.properties if p['name'] == choice), None)
        if prop:
            self.selected_property_id = prop['id']
            self.complete_btn.configure(state="normal")
            self.status_label.configure(
                text=f"Property selected (ID: {prop['id']})",
                text_color="green"
            )

    def complete_setup(self):
        """Complete setup and save config"""
        if self.selected_property_id:
            config = {
                'property_id': self.selected_property_id,
                'setup_completed': True,
                'setup_date': datetime.now().isoformat()
            }
            Config.save(config)
            self.destroy()
            self.on_complete()


class WhichBinWindow(ctk.CTkToplevel):
    """Window to search the A-Z waste guide"""

    BIN_COLORS = {
        'recycle': ('#d4a500', 'Yellow Recycling Bin'),
        'organic': ('#2d7f2d', 'Green FOGO Bin'),
        'waste': ('#c92a2a', 'Red Landfill Bin'),
        'crc': ('#1e88e5', 'Community Recycling Centre'),
        'clean_up': ('#7b1fa2', 'Council Clean-up'),
        'special': ('#ff6f00', 'Special Disposal'),
        'waste_drop_off': ('#455a64', 'Waste Drop-off'),
    }

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.title("Which Bin? - A-Z Waste Guide")
        self.geometry("700x600")
        self.resizable(True, True)

        # Position window beside the parent, slightly offset
        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        # Position to the right of parent, or left if no space
        new_x = parent_x + parent_width + 10
        new_y = parent_y + 50
        # Check if it would go off screen, if so position to left
        screen_width = self.winfo_screenwidth()
        if new_x + 700 > screen_width:
            new_x = parent_x - 710
        if new_x < 0:
            new_x = parent_x + 50  # Overlap if no space
        self.geometry(f"700x600+{new_x}+{new_y}")

        # Force window to front
        self.attributes("-topmost", True)
        self.focus_force()
        self.after(200, lambda: self.attributes("-topmost", False))

        self.materials = []
        self.filtered_materials = []

        self.create_ui()
        self.load_materials()

    def create_ui(self):
        """Create the search UI"""
        title = ctk.CTkLabel(
            self,
            text="Which Bin Does It Go In?",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(15, 5))

        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(search_frame, text="Search:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 10))
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="e.g. batteries, plastic bags, pizza box...")
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        self.results_label = ctk.CTkLabel(self, text="Loading...", font=ctk.CTkFont(size=11), text_color="gray")
        self.results_label.pack(pady=(5, 10))

        self.results_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.results_frame.pack(pady=10, padx=20, fill="both", expand=True)

    def load_materials(self):
        """Load materials from API"""
        materials = WasteAPI.get_materials()
        if materials:
            self.materials = sorted(materials, key=lambda x: x.get('title', ''))
            self.filtered_materials = self.materials
            self.results_label.configure(text=f"Showing all {len(self.materials)} items (type to search)")
            self.display_results()
        else:
            self.results_label.configure(text="Error loading materials", text_color="red")

    def on_search(self, event=None):
        """Filter materials based on search"""
        query = self.search_entry.get().lower().strip()

        if not query:
            self.filtered_materials = self.materials
        else:
            self.filtered_materials = [
                m for m in self.materials
                if query in (m.get('title') or '').lower()
                or query in (m.get('keywords') or '').lower()
            ]

        self.results_label.configure(
            text=f"Found {len(self.filtered_materials)} items" if query else f"Showing all {len(self.materials)} items"
        )
        self.display_results()

    def display_results(self):
        """Display filtered results"""
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        for material in self.filtered_materials[:50]:
            self.create_material_card(material)

        if len(self.filtered_materials) > 50:
            ctk.CTkLabel(
                self.results_frame,
                text=f"... and {len(self.filtered_materials) - 50} more. Refine your search.",
                text_color="gray"
            ).pack(pady=10)

    def create_material_card(self, material: Dict):
        """Create a card for a material"""
        bin_type = material.get('bin_type', 'waste')
        color, bin_name = self.BIN_COLORS.get(bin_type, ('#666666', 'Unknown'))

        card = ctk.CTkFrame(self.results_frame, fg_color=color, corner_radius=8)
        card.pack(pady=5, padx=5, fill="x")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(pady=10, padx=15, fill="x")

        ctk.CTkLabel(
            content,
            text=material.get('title', 'Unknown'),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white",
            anchor="w"
        ).pack(fill="x")

        ctk.CTkLabel(
            content,
            text=bin_name,
            font=ctk.CTkFont(size=11),
            text_color="white",
            anchor="w"
        ).pack(fill="x")


class BinCard(ctk.CTkFrame):
    """Color-coded card for a bin type"""

    def __init__(self, parent, bin_type: str, color: str):
        super().__init__(parent, fg_color=color, corner_radius=15)

        self.bin_type = bin_type
        self.collection_date = None

        self.title_label = ctk.CTkLabel(
            self,
            text=bin_type,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        self.title_label.pack(pady=(20, 10))

        self.days_label = ctk.CTkLabel(
            self,
            text="--",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color="white"
        )
        self.days_label.pack(pady=10)

        self.days_text = ctk.CTkLabel(
            self,
            text="days until collection",
            font=ctk.CTkFont(size=14),
            text_color="white"
        )
        self.days_text.pack(pady=(0, 10))

        self.date_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="white"
        )
        self.date_label.pack(pady=(0, 20))

    def update_data(self, next_date: Optional[str]):
        """Update card with collection date"""
        if not next_date:
            self.days_label.configure(text="--")
            self.date_label.configure(text="No data")
            self.collection_date = None
            return

        try:
            collection_date = datetime.fromisoformat(next_date.replace('Z', '+00:00'))
            self.collection_date = collection_date
            now = datetime.now(collection_date.tzinfo)
            days_until = (collection_date - now).days

            if days_until < 0:
                self.days_label.configure(text="--")
                self.date_label.configure(text="Date passed")
            elif days_until == 0:
                self.days_label.configure(text="TODAY")
                self.days_text.configure(text="")
                self.date_label.configure(text=collection_date.strftime("%d %B %Y"))
            elif days_until == 1:
                self.days_label.configure(text="1")
                self.days_text.configure(text="day until collection")
                self.date_label.configure(text=collection_date.strftime("%d %B %Y"))
            else:
                self.days_label.configure(text=str(days_until))
                self.days_text.configure(text="days until collection")
                self.date_label.configure(text=collection_date.strftime("%d %B %Y"))
        except Exception as e:
            print(f"Error parsing date: {e}")
            self.days_label.configure(text="--")
            self.date_label.configure(text="Error")


class Dashboard(ctk.CTk):
    """Main dashboard window"""

    def __init__(self):
        super().__init__()

        self.title("Bin Day Brain")
        self.geometry("800x700")
        self.resizable(False, False)

        # Set window icon
        self._set_icon()

        self.config = Config.load()
        self.create_ui()

        # Check if setup is needed or load data
        if not self.config or not self.config.get('setup_completed'):
            self.after(100, self.show_setup)
        else:
            self.load_data()
            self.load_events()
            self.load_weather()

    def _set_icon(self):
        """Set the window icon"""
        try:
            # Handle PyInstaller bundle path
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))

            icon_path = os.path.join(base_path, "bin-day-brain-icon.png")
            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
                icon_photo = ImageTk.PhotoImage(icon_image)
                self.wm_iconphoto(True, icon_photo)
                self._icon_photo = icon_photo  # Keep reference to prevent garbage collection
        except Exception as e:
            print(f"Could not load icon: {e}")

    def create_ui(self):
        """Create dashboard UI"""
        title = ctk.CTkLabel(
            self,
            text="Bin Day Brain",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(15, 5))

        subtitle = ctk.CTkLabel(
            self,
            text="Wollongong Smart Bin Reminders",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        subtitle.pack(pady=(0, 10))

        # Weather alert banner (hidden by default)
        self.weather_frame = ctk.CTkFrame(self, fg_color="#e65100", corner_radius=8)
        self.weather_label = ctk.CTkLabel(
            self.weather_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="white"
        )
        self.weather_label.pack(pady=8, padx=15)

        # Events banner (hidden by default)
        self.events_frame = ctk.CTkFrame(self, fg_color="#1565c0", corner_radius=8)
        self.events_label = ctk.CTkLabel(
            self.events_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="white"
        )
        self.events_label.pack(pady=8, padx=15)

        # Cards container
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(pady=15, padx=40, fill="both", expand=True)

        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        cards_frame.grid_columnconfigure(2, weight=1)
        cards_frame.grid_rowconfigure(0, weight=1)

        self.fogo_card = BinCard(cards_frame, "FOGO", "#2d7f2d")
        self.fogo_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.recycling_card = BinCard(cards_frame, "Recycling", "#d4a500")
        self.recycling_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.landfill_card = BinCard(cards_frame, "Landfill", "#c92a2a")
        self.landfill_card.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.status_label.pack(pady=(5, 10))

        # Bottom toolbar
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(pady=(0, 15), padx=40, fill="x")

        ctk.CTkButton(
            toolbar,
            text="Change Address",
            command=self.change_address,
            width=130,
            height=35,
            fg_color="#455a64",
            hover_color="#37474f"
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            toolbar,
            text="Which Bin?",
            command=self.show_which_bin,
            width=110,
            height=35,
            fg_color="#7b1fa2",
            hover_color="#6a1b9a"
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            toolbar,
            text="Add to Calendar",
            command=self.export_calendar,
            width=120,
            height=35,
            fg_color="#0d47a1",
            hover_color="#1565c0"
        ).pack(side="left", padx=(0, 10))

        self.refresh_btn = ctk.CTkButton(
            toolbar,
            text="Refresh",
            command=self.refresh_data,
            width=100,
            height=35
        )
        self.refresh_btn.pack(side="right")

        # Copyright
        copyright_label = ctk.CTkLabel(
            self,
            text=COPYRIGHT,
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        copyright_label.pack(pady=(0, 8))

    def load_weather(self):
        """Load weather alerts for collection day"""
        # Find the nearest collection date
        nearest_date = None
        for card in [self.fogo_card, self.recycling_card, self.landfill_card]:
            if card.collection_date:
                if nearest_date is None or card.collection_date < nearest_date:
                    nearest_date = card.collection_date

        if not nearest_date:
            return

        alerts = WeatherAPI.get_weather_alerts(nearest_date)
        if alerts:
            # Show the most important alert
            alert = alerts[0]
            color = "#e65100" if alert['severity'] == 'warning' else "#1976d2"
            self.weather_frame.configure(fg_color=color)
            self.weather_label.configure(text=alert['message'])
            self.weather_frame.pack(pady=(0, 10), padx=40, fill="x", after=self.winfo_children()[1])

    def load_events(self):
        """Load and display upcoming events"""
        events = WasteAPI.get_events()
        self._display_events(events)

    def _display_events(self, events):
        """Display events data"""
        if not events:
            return

        today = datetime.now().date()
        month_later = today + timedelta(days=30)

        upcoming = []
        for event in events:
            start = event.get('start_date')
            if start:
                try:
                    event_date = datetime.strptime(start, '%Y-%m-%d').date()
                    if today <= event_date <= month_later:
                        upcoming.append((event_date, event))
                except ValueError:
                    pass

        if upcoming:
            upcoming.sort(key=lambda x: x[0])
            event_date, event = upcoming[0]
            days_until = (event_date - today).days
            title = event.get('title', 'Upcoming Event')

            if days_until == 0:
                time_text = "TODAY"
            elif days_until == 1:
                time_text = "Tomorrow"
            else:
                time_text = f"In {days_until} days"

            self.events_label.configure(text=f"Event: {title} - {time_text} ({event_date.strftime('%d %b')})")
            self.events_frame.pack(pady=(0, 10), padx=40, fill="x", after=self.winfo_children()[1])

    def change_address(self):
        """Open setup wizard to change address"""
        SetupWizard(self, self.on_setup_complete)

    def show_which_bin(self):
        """Open the Which Bin? search window"""
        WhichBinWindow(self)

    def export_calendar(self):
        """Export bin collection dates to ICS calendar file"""
        import subprocess
        import uuid

        # Collect all collection dates
        events_data = []
        for card, bin_name in [(self.fogo_card, "FOGO Bin"),
                                (self.recycling_card, "Recycling Bin"),
                                (self.landfill_card, "Landfill Bin")]:
            if card.collection_date:
                events_data.append({
                    'name': bin_name,
                    'date': card.collection_date
                })

        if not events_data:
            self.status_label.configure(text="No collection dates to export", text_color="orange")
            return

        # Generate ICS content
        ics_lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Bin Day Brain//Wollongong Waste//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
        ]

        for event in events_data:
            date_str = event['date'].strftime('%Y%m%d')
            uid = str(uuid.uuid4())
            ics_lines.extend([
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTART;VALUE=DATE:{date_str}",
                f"DTEND;VALUE=DATE:{date_str}",
                f"SUMMARY:Put out {event['name']}",
                f"DESCRIPTION:Bin Day Brain reminder - {event['name']} collection day",
                "BEGIN:VALARM",
                "TRIGGER:-PT18H",
                "ACTION:DISPLAY",
                f"DESCRIPTION:Put out {event['name']} tonight!",
                "END:VALARM",
                "END:VEVENT",
            ])

        ics_lines.append("END:VCALENDAR")
        ics_content = "\r\n".join(ics_lines)

        # Save to file
        ics_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin_collection.ics")
        try:
            with open(ics_path, 'w') as f:
                f.write(ics_content)

            # Open with default calendar app
            if sys.platform == 'win32':
                os.startfile(ics_path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', ics_path])
            else:
                subprocess.run(['xdg-open', ics_path])

            self.status_label.configure(text="Calendar file created - check your calendar app!", text_color="green")
        except Exception as e:
            print(f"Error exporting calendar: {e}")
            self.status_label.configure(text=f"Error: {e}", text_color="red")

    def show_setup(self):
        """Show setup wizard"""
        SetupWizard(self, self.on_setup_complete)

    def on_setup_complete(self):
        """Handle setup completion"""
        self.config = Config.load()
        self.load_data()

    def load_data(self):
        """Load and display collection data"""
        cache = Cache.load()

        if cache and cache.get('collections'):
            self.update_cards(cache['collections'])
            cached_time = cache.get('cached_at', 'Unknown')
            self.status_label.configure(text=f"Loading fresh data...")
        else:
            self.status_label.configure(text="Loading data...")

        # Run API calls in background thread
        thread = threading.Thread(target=self._load_all_data_background, daemon=True)
        thread.start()

    def _load_all_data_background(self):
        """Background thread to load all data from APIs"""
        property_id = self.config.get('property_id') if self.config else None
        if not property_id:
            self.after(0, lambda: self.status_label.configure(text="Error: No property configured"))
            return

        # Fetch all data in parallel
        collection_data = WasteAPI.get_collection_data(property_id)
        events_data = WasteAPI.get_events()

        # Update UI on main thread
        self.after(0, lambda: self._update_ui_with_data(collection_data, events_data))

    def _update_ui_with_data(self, collection_data, events_data):
        """Update UI with fetched data (called on main thread)"""
        if collection_data and collection_data.get('collections'):
            Cache.save(collection_data)
            self.update_cards(collection_data['collections'])
            self.status_label.configure(
                text=f"Last updated: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            )
            # Load weather after cards are updated
            self.load_weather()
        else:
            cache = Cache.load()
            if cache:
                self.status_label.configure(text="Offline - showing cached data", text_color="orange")
            else:
                self.status_label.configure(text="Error loading data", text_color="red")

        # Update events
        if events_data:
            self._display_events(events_data)

    def refresh_data(self, silent=False):
        """Refresh data from API"""
        if not silent:
            self.status_label.configure(text="Refreshing...")
            self.refresh_btn.configure(state="disabled")

        property_id = self.config.get('property_id') if self.config else None
        if not property_id:
            self.status_label.configure(text="Error: No property configured")
            if not silent:
                self.refresh_btn.configure(state="normal")
            return

        # Run in background thread
        def do_refresh():
            data = WasteAPI.get_collection_data(property_id)
            self.after(0, lambda: self._finish_refresh(data, silent))

        thread = threading.Thread(target=do_refresh, daemon=True)
        thread.start()

    def _finish_refresh(self, data, silent):
        """Finish refresh on main thread"""
        if data and data.get('collections'):
            Cache.save(data)
            self.update_cards(data['collections'])
            self.status_label.configure(
                text=f"Last updated: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            )
            self.load_weather()
        else:
            if not silent:
                cache = Cache.load()
                if cache:
                    self.status_label.configure(
                        text="Offline - showing cached data",
                        text_color="orange"
                    )
                else:
                    self.status_label.configure(
                        text="Error: No internet and no cached data",
                        text_color="red"
                    )

        if not silent:
            self.refresh_btn.configure(state="normal")

    def update_cards(self, collections: List[Dict]):
        """Update all bin cards with collection data"""
        for collection in collections:
            bin_type = collection.get('type', '').lower()
            next_date = collection.get('next', {}).get('date')

            if 'fogo' in bin_type or 'organics' in bin_type:
                self.fogo_card.update_data(next_date)
            elif 'recycling' in bin_type:
                self.recycling_card.update_data(next_date)
            elif 'landfill' in bin_type or 'garbage' in bin_type or 'waste' in bin_type:
                self.landfill_card.update_data(next_date)


def main():
    """Main entry point"""
    app = Dashboard()
    app.mainloop()


if __name__ == "__main__":
    main()
