"""
FOGI App - Wollongong Bin Collection Tracker
A simple, offline-first desktop utility for tracking bin collection days.
"""

import customtkinter as ctk
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import sys

# Constants
API_BASE = "https://wollongong.waste-info.com.au/api/v1"
CONFIG_FILE = "config.json"
CACHE_FILE = "cache.json"

# CustomTkinter appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class WasteAPI:
    """Handle all API interactions with Wollongong Waste Info"""
    
    @staticmethod
    def get_localities() -> Optional[List[Dict]]:
        """Fetch all available localities"""
        try:
            response = requests.get(f"{API_BASE}/localities.json", timeout=10)
            response.raise_for_status()
            return response.json()
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
            return response.json()
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
            return response.json()
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
            return response.json()
        except Exception as e:
            print(f"Error fetching collection data: {e}")
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
        
        self.title("FOGI App - Setup")
        self.geometry("600x500")
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
            text="Welcome to FOGI App!",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)
        
        subtitle = ctk.CTkLabel(
            self,
            text="Let's find your address to track bin collection days",
            font=ctk.CTkFont(size=14)
        )
        subtitle.pack(pady=10)
        
        # Form frame
        form = ctk.CTkFrame(self)
        form.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Locality
        ctk.CTkLabel(form, text="Suburb/Locality:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(20, 5))
        self.locality_combo = ctk.CTkComboBox(
            form,
            values=["Loading..."],
            command=self.on_locality_selected,
            state="disabled"
        )
        self.locality_combo.pack(pady=5, padx=20, fill="x")
        
        # Street
        ctk.CTkLabel(form, text="Street:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(20, 5))
        self.street_combo = ctk.CTkComboBox(
            form,
            values=["Select locality first"],
            command=self.on_street_selected,
            state="disabled"
        )
        self.street_combo.pack(pady=5, padx=20, fill="x")
        
        # Property
        ctk.CTkLabel(form, text="Property Number:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(20, 5))
        self.property_combo = ctk.CTkComboBox(
            form,
            values=["Select street first"],
            command=self.on_property_selected,
            state="disabled"
        )
        self.property_combo.pack(pady=5, padx=20, fill="x")
        
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
            self.locality_combo.set("Select your suburb")
            self.status_label.configure(text="")
        else:
            self.status_label.configure(
                text="Error: Could not connect to server. Check internet connection.",
                text_color="red"
            )
    
    def on_locality_selected(self, choice):
        """Handle locality selection"""
        # Find locality ID
        locality = next((loc for loc in self.localities if loc['name'] == choice), None)
        if not locality:
            return
        
        # Reset downstream
        self.street_combo.configure(values=["Loading..."], state="disabled")
        self.property_combo.configure(values=["Select street first"], state="disabled")
        self.complete_btn.configure(state="disabled")
        
        # Load streets
        self.status_label.configure(text="Loading streets...")
        streets = WasteAPI.get_streets(locality['id'])
        
        if streets:
            self.streets = sorted(streets, key=lambda x: x.get('name', ''))
            street_names = [street['name'] for street in self.streets]
            self.street_combo.configure(values=street_names, state="normal")
            self.street_combo.set("Select your street")
            self.status_label.configure(text="")
        else:
            self.status_label.configure(
                text="Error loading streets",
                text_color="red"
            )
    
    def on_street_selected(self, choice):
        """Handle street selection"""
        # Find street ID
        street = next((s for s in self.streets if s['name'] == choice), None)
        if not street:
            return
        
        # Reset downstream
        self.property_combo.configure(values=["Loading..."], state="disabled")
        self.complete_btn.configure(state="disabled")
        
        # Load properties
        self.status_label.configure(text="Loading properties...")
        properties = WasteAPI.get_properties(street['id'])
        
        if properties:
            self.properties = sorted(properties, key=lambda x: x.get('name', ''))
            property_names = [prop['name'] for prop in self.properties]
            self.property_combo.configure(values=property_names, state="normal")
            self.property_combo.set("Select your property number")
            self.status_label.configure(text="")
        else:
            self.status_label.configure(
                text="Error loading properties",
                text_color="red"
            )
    
    def on_property_selected(self, choice):
        """Handle property selection"""
        # Find property ID
        prop = next((p for p in self.properties if p['name'] == choice), None)
        if prop:
            self.selected_property_id = prop['id']
            self.complete_btn.configure(state="normal")
            self.status_label.configure(
                text=f"✓ Property selected (ID: {prop['id']})",
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


class BinCard(ctk.CTkFrame):
    """Color-coded card for a bin type"""
    
    def __init__(self, parent, bin_type: str, color: str):
        super().__init__(parent, fg_color=color, corner_radius=15)
        
        self.bin_type = bin_type
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text=bin_type,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        self.title_label.pack(pady=(20, 10))
        
        # Days remaining
        self.days_label = ctk.CTkLabel(
            self,
            text="--",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color="white"
        )
        self.days_label.pack(pady=10)
        
        # Days text
        self.days_text = ctk.CTkLabel(
            self,
            text="days until collection",
            font=ctk.CTkFont(size=14),
            text_color="white"
        )
        self.days_text.pack(pady=(0, 10))
        
        # Next collection date
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
            return
        
        try:
            # Parse date
            collection_date = datetime.fromisoformat(next_date.replace('Z', '+00:00'))
            now = datetime.now(collection_date.tzinfo)
            
            # Calculate days
            days_until = (collection_date - now).days
            
            # Update UI
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
        
        self.title("FOGI App - Bin Collection Tracker")
        self.geometry("800x600")
        self.resizable(False, False)
        
        # Load config
        self.config = Config.load()
        
        # Create UI
        self.create_ui()
        
        # Check if setup needed
        if not self.config or not self.config.get('setup_completed'):
            self.after(100, self.show_setup)
        else:
            self.load_data()
    
    def create_ui(self):
        """Create dashboard UI"""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Wollongong Bin Collection",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=20)
        
        # Cards container
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Configure grid
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        cards_frame.grid_columnconfigure(2, weight=1)
        cards_frame.grid_rowconfigure(0, weight=1)
        
        # Create bin cards
        self.fogo_card = BinCard(cards_frame, "FOGO", "#2d7f2d")  # Green
        self.fogo_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.recycling_card = BinCard(cards_frame, "Recycling", "#d4a500")  # Yellow/Gold
        self.recycling_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.landfill_card = BinCard(cards_frame, "Landfill", "#c92a2a")  # Red
        self.landfill_card.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        # Bottom frame
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(pady=10, padx=40, fill="x")
        
        # Status label
        self.status_label = ctk.CTkLabel(
            bottom_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.status_label.pack(side="left")
        
        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            bottom_frame,
            text="Refresh",
            command=self.refresh_data,
            width=120,
            height=35
        )
        self.refresh_btn.pack(side="right")
    
    def show_setup(self):
        """Show setup wizard"""
        SetupWizard(self, self.on_setup_complete)
    
    def on_setup_complete(self):
        """Handle setup completion"""
        self.config = Config.load()
        self.load_data()
    
    def load_data(self):
        """Load and display collection data"""
        # Try to load from cache first
        cache = Cache.load()
        
        if cache and cache.get('collections'):
            self.update_cards(cache['collections'])
            cached_time = cache.get('cached_at', 'Unknown')
            self.status_label.configure(text=f"Using cached data from {cached_time[:16]}")
        else:
            self.status_label.configure(text="No cached data available")
        
        # Try to refresh from API
        self.refresh_data(silent=True)
    
    def refresh_data(self, silent=False):
        """Refresh data from API"""
        if not silent:
            self.status_label.configure(text="Refreshing...")
            self.refresh_btn.configure(state="disabled")
        
        property_id = self.config.get('property_id')
        if not property_id:
            self.status_label.configure(text="Error: No property configured")
            self.refresh_btn.configure(state="normal")
            return
        
        # Fetch from API
        data = WasteAPI.get_collection_data(property_id)
        
        if data and data.get('collections'):
            # Save to cache
            Cache.save(data)
            
            # Update UI
            self.update_cards(data['collections'])
            self.status_label.configure(
                text=f"Last updated: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            )
        else:
            # API failed, show cached data if available
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
        # Map collection types to cards
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
