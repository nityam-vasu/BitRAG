#!/usr/bin/env python3
"""
BitRAG - PyTermGUI Terminal User Interface

A proper PyTermGUI-based TUI for BitRAG.
"""

import sys
import os

# Add src to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, "src"))

# Suppress warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

import warnings
warnings.filterwarnings("ignore")

import pytermgui as ptg
from pytermgui import Window, Label, Button, Splitter, InputField


def print_banner():
    """Print ASCII art banner."""
    banner = """
████████  ████ ████████ ████████      ███      ██████
██     ██  ██     ██    ██     ██   ██  ██   ██    ██
██     ██  ██     ██    ██     ██  ██   ██  ██
████████   ██     ██    ████████  ██     ██ ██   ████
██     ██  ██     ██    ██   ██   █████████ ██    ██
██     ██  ██     ██    ██    ██  ██     ██ ██    ██
████████  ████    ██    ██     ██ ██     ██  ██████
    """
    print(banner)
    print("  1-bit LLM RAG System")
    print("  PyTermGUI Terminal Interface\n")


class BitRAGTerminal:
    """Main BitRAG Terminal Application using PyTermGUI."""
    
    def __init__(self):
        self.app = None
        self.manager = None
        self.query_engine = None
        self.session_id = "default"
        
    def load_config(self):
        """Load configuration."""
        try:
            from bitrag.core.config import get_config
            self.config = get_config()
            print(f"[OK] Config loaded: {self.config.default_model}")
        except Exception as e:
            print(f"[WARN] Config error: {e}")
            self.config = None
    
    def init_query_engine(self):
        """Initialize query engine."""
        try:
            from bitrag.core.query import QueryEngine
            self.query_engine = QueryEngine(
                session_id=self.session_id,
                model=self.config.default_model if self.config else "llama3.2:1b"
            )
            print(f"[OK] Query engine ready")
        except Exception as e:
            print(f"[WARN] Query engine: {e}")
    
    def create_app(self):
        """Create PyTermGUI application."""
        # Create app
        self.app = ptg.App()
        
        # Create layout
        self.app.layout = ptg.Layout()
        self.app.layout.add_slot("header", height=3)
        self.app.layout.add_slot("body", weight=1)
        self.app.layout.add_slot("footer", height=3)
        
        # Header window
        header = Window(
            Splitter(
                Label("[bold cyan]BitRAG[/] [dim]- 1-bit LLM RAG[/]"),
                Label("[dim]|[/]"),
                Button("[📄 Documents]", self.show_documents),
                Label("[dim]|[/]"),
                Button("[⚙ Settings]", self.show_settings),
            )
        )
        
        # Body - Chat area
        self.chat_window = Window(
            Label("[dim]Welcome to BitRAG![/]"),
            Label(""),
            Label("[dim]Press 'C' for chat, 'U' to upload documents[/]"),
            Label(""),
            Label("[dim]Type your query below and press Enter[/]"),
        )
        
        # Input area
        input_splitter = Splitter(
            Button("[📁 Upload]", self.upload_file),
            self.query_input := InputField(prompt="[green]>[/] ", placeholder="Type your question..."),
            Button("[▶ Send]", self.send_query),
        )
        
        # Footer
        footer = Window(
            Label("[dim]C - Chat  |  S - Settings  |  U - Upload  |  Q - Quit[/]"),
        )
        
        # Add windows to app
        self.app.add(header, "header")
        self.app.add(self.chat_window, "body")
        self.app.add(input_splitter, "footer")
        self.app.add(footer, "footer")
        
        # Bind keys
        self.app.bind("q", lambda _: self.app.stop())
        self.app.bind("Q", lambda _: self.app.stop())
        self.app.bind("c", self.show_chat)
        self.app.bind("C", self.show_chat)
        self.app.bind("s", self.show_settings)
        self.app.bind("S", self.show_settings)
        self.app.bind("u", self.upload_file)
        self.app.bind("U", self.upload_file)
        
        # Bind Enter in input to send
        self.query_input.bind(ptg.keys.Keys.ENTER, self.send_query)
    
    def send_query(self, widget=None):
        """Send query."""
        query = self.query_input.value
        if not query:
            return
        
        # Clear input
        self.query_input.value = ""
        
        # Add to chat
        self.chat_window.append(Label(f"[green]You:[/] {query}"))
        
        if self.query_engine is None:
            self.chat_window.append(Label("[red]Query engine not ready[/]"))
            return
        
        # Check for documents
        if not self.has_documents():
            self.chat_window.append(Label("[yellow]No documents indexed. Upload documents first.[/]"))
            return
        
        # Process query
        self.chat_window.append(Label("[dim]Processing...[/]"))
        
        try:
            result = self.query_engine.query(query)
            response = result.get("response", "No response")
            sources = result.get("sources", [])
            
            self.chat_window.append(Label(f"[cyan]Bot:[/] {response[:200]}"))
            
            if sources:
                self.chat_window.append(Label(f"[dim]Sources: {len(sources)}[/]"))
        except Exception as e:
            self.chat_window.append(Label(f"[red]Error: {e}[/]"))
    
    def has_documents(self) -> bool:
        """Check for indexed documents."""
        if self.query_engine is None:
            return False
        try:
            return self.query_engine.has_documents()
        except:
            return False
    
    def show_chat(self, widget=None):
        """Show chat window."""
        self.chat_window.append(Label("[dim]Chat mode activated[/]"))
    
    def show_documents(self, widget=None):
        """Show documents."""
        self.chat_window.append(Label("[bold]Document Management[/]"))
        
        try:
            from bitrag.tui.document_manager import DocumentManager
            doc_mgr = DocumentManager(session_id=self.session_id)
            docs = doc_mgr.ui.list_documents()
            
            if docs:
                for doc in docs:
                    self.chat_window.append(Label(f"  📄 {doc.file_name}"))
            else:
                self.chat_window.append(Label("[dim]No documents indexed[/]"))
        except Exception as e:
            self.chat_window.append(Label(f"[red]Error: {e}[/]"))
    
    def show_settings(self, widget=None):
        """Show settings."""
        self.chat_window.append(Label("[bold]Settings[/]"))
        
        if self.config:
            self.chat_window.append(Label(f"  Model: {self.config.default_model}"))
            self.chat_window.append(Label(f"  Ollama: {self.config.ollama_base_url}"))
            self.chat_window.append(Label(f"  Data: {self.config.data_dir}"))
    
    def upload_file(self, widget=None):
        """Upload file."""
        self.chat_window.append(Label("[bold]Upload Document[/]"))
        self.chat_window.append(Label("[dim]Enter file path in input field[/]"))
    
    def run(self):
        """Run the application."""
        print_banner()
        
        # Load config
        self.load_config()
        
        # Init query engine
        self.init_query_engine()
        
        # Create app
        print("\n[INFO] Starting PyTermGUI...")
        
        try:
            self.create_app()
            print("[INFO] Press 'q' to quit\n")
            self.app.run()
        except Exception as e:
            print(f"[WARN] PyTermGUI failed: {e}")
            print("\n[FALLBACK] Starting interactive menu instead...\n")
            self.run_fallback_menu()
    
    def run_fallback_menu(self):
        """Fallback to text-based menu if PyTermGUI fails."""
        from bitrag.tui.app import BitRAGApp
        app = BitRAGApp()
        app.initialize()
        app._run_interactive_menu()


def main():
    """Main entry point."""
    app = BitRAGTerminal()
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
