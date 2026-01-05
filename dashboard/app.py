from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable, Log
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from core.event_bus import EventBus, EventType, Event
from core.token_manager import TokenManager
import asyncio

class CouncilDashboard(App):
    """Gemini Council TUI Dashboard v6.0 (Flight Recorder)."""
    
    CSS = """
    Screen {
        background: #000b1e;
    }
    Header {
        background: #001635;
        color: #00d4ff;
        text-style: bold;
    }
    #main-container {
        height: 1fr;
        padding: 1;
    }
    #token-status {
        height: auto;
        border: solid #00d4ff;
        margin-bottom: 1;
        background: #001635;
        padding: 1;
    }
    .provider-box {
        padding: 1;
        border: solid #00d4ff;
        margin: 1;
        width: 1fr;
    }
    .provider-name {
        text-style: bold;
        color: #00d4ff;
    }
    .status-healthy { color: #00ff00; }
    .status-warn { color: #ffff00; }
    .status-critical { color: #ff0000; }
    
    DataTable {
        height: 1fr;
        border: solid #00d4ff;
        background: #001635;
    }
    Log {
        height: 1fr;
        border: solid #00d4ff;
        margin-top: 1;
        background: #000b1e;
    }
    #loop-alert {
        background: #ff0000;
        color: #ffffff;
        text-align: center;
        display: none;
    }
    Footer {
        background: #001635;
    }
    """

    def __init__(self):
        super().__init__()
        self.token_manager = TokenManager()
        self.event_bus = EventBus()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        # Alert Bar
        yield Static("!!! LOOP DETECTED - HALTING AGENT !!!", id="loop-alert")

        # Token Status Panel
        with Container(id="token-status"):
            with Horizontal():
                with Vertical(classes="provider-box"):
                    yield Static("GROQ (FREE)", classes="provider-name")
                    yield Static("RPM: --/--", id="groq-rpm")
                    yield Static("TPM: --/--", id="groq-tpm")
                    yield Static("Status: CHECKING", id="groq-status")
                
                with Vertical(classes="provider-box"):
                    yield Static("GEMINI (PAID)", classes="provider-name")
                    yield Static("Spend Today: $--", id="gemini-spend")
                    yield Static("Budget: $--", id="gemini-budget")
                    yield Static("Status: CHECKING", id="gemini-status")

        with Container(id="main-container"):
            yield Static("--- COUNCIL DELIBERATION GRID ---", id="title")
            yield DataTable(id="agent-table")
            yield Log(id="event-log")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#agent-table", DataTable)
        table.add_columns("Agent", "Status", "Verdict", "Confidence")
        
        # Subscribe to Events
        self.event_bus.subscribe(EventType.DELIBERATION_START, self.handle_start)
        self.event_bus.subscribe(EventType.AGENT_VOTE, self.handle_vote)
        self.event_bus.subscribe(EventType.CONSENSUS_REACHED, self.handle_consensus)
        self.event_bus.subscribe(EventType.LOOP_DETECTED, self.handle_loop)
        
        # Start Token Refresh Timer
        self.set_interval(2.0, self.update_tokens)
        
        self.log_event("Dashboard initialized. Flight Recorder Active.")

    def update_tokens(self):
        """Polls TokenManager for latest stats."""
        stats = self.token_manager.get_status()
        
        # Groq Updates
        groq = stats["groq"]
        self.query_one("#groq-rpm", Static).update(f"RPM: {groq['rpm']}/{groq['rpm_limit']}")
        self.query_one("#groq-tpm", Static).update(f"TPM: {groq['tpm']:.0f}")
        self.query_one("#groq-status", Static).update(f"Status: {groq['status']}")
        
        # Gemini Updates
        gemini = stats["gemini"]
        self.query_one("#gemini-spend", Static).update(f"Spend Today: ${gemini['spend']:.4f}")
        self.query_one("#gemini-budget", Static).update(f"Budget: ${gemini['budget']:.2f}")
        self.query_one("#gemini-status", Static).update(f"Status: {gemini['status']}")

    def log_event(self, message: str):
        self.query_one("#event-log", Log).write_line(f"[{asyncio.get_event_loop().time():.2f}] {message}")

    def handle_start(self, event: Event):
        table = self.query_one("#agent-table", DataTable)
        table.clear()
        self.query_one("#loop-alert").styles.display = "none"
        self.log_event(f"Deliberation Started: {event.data.get('session_id', 'Unknown')[:8]}")

    def handle_vote(self, event: Event):
        table = self.query_one("#agent-table", DataTable)
        agent = event.data["agent"]
        verdict = event.data["verdict"]
        confidence = event.data.get("confidence", 0.0)
        
        found = False
        for row_key in table.rows:
            if table.get_row(row_key)[0] == agent:
                table.update_row(row_key, [agent, "DONE", verdict, f"{confidence:.2f}"])
                found = True
                break
        if not found:
            table.add_row(agent, "DONE", verdict, f"{confidence:.2f}")
            
        self.log_event(f"Agent {agent} voted {verdict} ({confidence:.2f})")

    def handle_consensus(self, event: Event):
        consensus = event.data["consensus"]
        decision = consensus.get("decision", "UNKNOWN")
        self.log_event(f"CONSENSUS REACHED: {decision}")

    def handle_loop(self, event: Event):
        data = event.data
        alert = self.query_one("#loop-alert")
        alert.update(f"!!! LOOP DETECTED: {data['agent']} repeated '{data['action']}' {data['count']} times !!!")
        alert.styles.display = "block"
        self.log_event(f"[CRITICAL] Loop Detected for {data['agent']} on {data['target']}")

if __name__ == "__main__":
    app = CouncilDashboard()
    app.run()