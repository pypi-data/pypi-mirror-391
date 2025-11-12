"""Settings configuration modal for myDash."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, TabbedContent, TabPane, Static
from textual.containers import Container, Horizontal, Vertical
from src.config.config_manager import config_manager


class SettingsModal(ModalScreen):
    """Modal for configuring application settings."""

    CSS = """
    SettingsModal {
        align: center middle;
    }

    #settings-dialog {
        width: 100;
        height: 40;
        border: thick $primary;
        background: $surface;
        padding: 1;
    }

    .settings-title {
        text-align: center;
        text-style: bold;
        background: $primary;
        padding: 1;
        margin-bottom: 1;
    }

    .settings-content {
        height: 1fr;
        overflow-y: auto;
    }

    .setting-row {
        height: auto;
        margin: 1 0;
    }

    .setting-label {
        width: 30;
        padding: 0 1;
        content-align: left middle;
    }

    .setting-input {
        width: 1fr;
    }

    .button-row {
        height: 3;
        align: center middle;
        margin-top: 1;
    }

    .button-row Button {
        margin: 0 1;
    }

    TabPane {
        padding: 1;
    }

    .info-text {
        color: $text-muted;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the settings modal."""
        with Container(id="settings-dialog"):
            yield Static("⚙️ Settings Configuration", classes="settings-title")

            with Vertical(classes="settings-content"):
                with TabbedContent():
                    # Database Tab
                    with TabPane("Database"):
                        yield Static(
                            "Configure database storage location",
                            classes="info-text"
                        )
                        with Horizontal(classes="setting-row"):
                            yield Label("Database Path:", classes="setting-label")
                            yield Input(
                                value=config_manager.get('database', 'path', './data/mydash.db'),
                                placeholder="./data/mydash.db",
                                id="db_path",
                                classes="setting-input"
                            )

                    # OpenWeather Tab
                    with TabPane("Weather API"):
                        yield Static(
                            "Configure OpenWeather API (optional)\nGet API key: https://openweathermap.org/api",
                            classes="info-text"
                        )
                        with Horizontal(classes="setting-row"):
                            yield Label("API Key:", classes="setting-label")
                            yield Input(
                                value=config_manager.get('openweather', 'api_key', ''),
                                placeholder="your_api_key_here",
                                id="weather_api_key",
                                classes="setting-input"
                            )
                        with Horizontal(classes="setting-row"):
                            yield Label("City:", classes="setting-label")
                            yield Input(
                                value=config_manager.get('openweather', 'city', 'Seoul'),
                                placeholder="Seoul",
                                id="weather_city",
                                classes="setting-input"
                            )
                        with Horizontal(classes="setting-row"):
                            yield Label("Units:", classes="setting-label")
                            yield Input(
                                value=config_manager.get('openweather', 'units', 'metric'),
                                placeholder="metric",
                                id="weather_units",
                                classes="setting-input"
                            )

                    # Google Services Tab
                    with TabPane("Google APIs"):
                        yield Static(
                            "Configure Google OAuth credentials (optional)\nSetup: https://console.cloud.google.com/",
                            classes="info-text"
                        )
                        with Horizontal(classes="setting-row"):
                            yield Label("Credentials Path:", classes="setting-label")
                            yield Input(
                                value=config_manager.get('google', 'credentials_path', '.credentials.json'),
                                placeholder=".credentials.json",
                                id="google_creds",
                                classes="setting-input"
                            )
                        with Horizontal(classes="setting-row"):
                            yield Label("Token Path:", classes="setting-label")
                            yield Input(
                                value=config_manager.get('google', 'token_path', '.token.json'),
                                placeholder=".token.json",
                                id="google_token",
                                classes="setting-input"
                            )

                    # Refresh Intervals Tab
                    with TabPane("Intervals"):
                        yield Static(
                            "Configure refresh intervals (in seconds)",
                            classes="info-text"
                        )
                        with Horizontal(classes="setting-row"):
                            yield Label("System Info:", classes="setting-label")
                            yield Input(
                                value=str(config_manager.get_int('refresh_intervals', 'system', 5)),
                                placeholder="5",
                                id="interval_system",
                                classes="setting-input"
                            )
                        with Horizontal(classes="setting-row"):
                            yield Label("Weather:", classes="setting-label")
                            yield Input(
                                value=str(config_manager.get_int('refresh_intervals', 'weather', 1800)),
                                placeholder="1800",
                                id="interval_weather",
                                classes="setting-input"
                            )
                        with Horizontal(classes="setting-row"):
                            yield Label("Calendar:", classes="setting-label")
                            yield Input(
                                value=str(config_manager.get_int('refresh_intervals', 'calendar', 900)),
                                placeholder="900",
                                id="interval_calendar",
                                classes="setting-input"
                            )
                        with Horizontal(classes="setting-row"):
                            yield Label("Gmail:", classes="setting-label")
                            yield Input(
                                value=str(config_manager.get_int('refresh_intervals', 'gmail', 300)),
                                placeholder="300",
                                id="interval_gmail",
                                classes="setting-input"
                            )
                        with Horizontal(classes="setting-row"):
                            yield Label("Tasks:", classes="setting-label")
                            yield Input(
                                value=str(config_manager.get_int('refresh_intervals', 'tasks', 600)),
                                placeholder="600",
                                id="interval_tasks",
                                classes="setting-input"
                            )
                        with Horizontal(classes="setting-row"):
                            yield Label("Stocks:", classes="setting-label")
                            yield Input(
                                value=str(config_manager.get_int('refresh_intervals', 'stocks', 60)),
                                placeholder="60",
                                id="interval_stocks",
                                classes="setting-input"
                            )

                    # Advanced Tab
                    with TabPane("Advanced"):
                        yield Static(
                            "Advanced configuration options",
                            classes="info-text"
                        )
                        with Horizontal(classes="setting-row"):
                            yield Label("Log Level:", classes="setting-label")
                            yield Input(
                                value=config_manager.get('logging', 'level', 'INFO'),
                                placeholder="INFO",
                                id="log_level",
                                classes="setting-input"
                            )
                        with Horizontal(classes="setting-row"):
                            yield Label("Log File:", classes="setting-label")
                            yield Input(
                                value=config_manager.get('logging', 'file', './data/mydash.log'),
                                placeholder="./data/mydash.log",
                                id="log_file",
                                classes="setting-input"
                            )
                        with Horizontal(classes="setting-row"):
                            yield Label("Cache Enabled:", classes="setting-label")
                            yield Input(
                                value=str(config_manager.get_bool('cache', 'enabled', True)).lower(),
                                placeholder="true",
                                id="cache_enabled",
                                classes="setting-input"
                            )
                        with Horizontal(classes="setting-row"):
                            yield Label("Cache TTL (sec):", classes="setting-label")
                            yield Input(
                                value=str(config_manager.get_int('cache', 'ttl', 3600)),
                                placeholder="3600",
                                id="cache_ttl",
                                classes="setting-input"
                            )

            with Horizontal(classes="button-row"):
                yield Button("💾 Save", variant="primary", id="save-btn")
                yield Button("🔄 Reset to Defaults", variant="warning", id="reset-btn")
                yield Button("❌ Cancel", id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save-btn":
            self._save_settings()
            self.dismiss(True)
        elif event.button.id == "reset-btn":
            config_manager.reset_to_defaults()
            self.dismiss(True)
        elif event.button.id == "cancel-btn":
            self.dismiss(False)

    def _save_settings(self) -> None:
        """Save all settings to config file."""
        # Database
        config_manager.set('database', 'path', self.query_one("#db_path").value)

        # OpenWeather
        config_manager.set('openweather', 'api_key', self.query_one("#weather_api_key").value)
        config_manager.set('openweather', 'city', self.query_one("#weather_city").value)
        config_manager.set('openweather', 'units', self.query_one("#weather_units").value)

        # Google
        config_manager.set('google', 'credentials_path', self.query_one("#google_creds").value)
        config_manager.set('google', 'token_path', self.query_one("#google_token").value)

        # Refresh Intervals
        config_manager.set('refresh_intervals', 'system', self.query_one("#interval_system").value)
        config_manager.set('refresh_intervals', 'weather', self.query_one("#interval_weather").value)
        config_manager.set('refresh_intervals', 'calendar', self.query_one("#interval_calendar").value)
        config_manager.set('refresh_intervals', 'gmail', self.query_one("#interval_gmail").value)
        config_manager.set('refresh_intervals', 'tasks', self.query_one("#interval_tasks").value)
        config_manager.set('refresh_intervals', 'stocks', self.query_one("#interval_stocks").value)

        # Logging
        config_manager.set('logging', 'level', self.query_one("#log_level").value)
        config_manager.set('logging', 'file', self.query_one("#log_file").value)

        # Cache
        config_manager.set('cache', 'enabled', self.query_one("#cache_enabled").value)
        config_manager.set('cache', 'ttl', self.query_one("#cache_ttl").value)

        # Save to file
        config_manager.save()
