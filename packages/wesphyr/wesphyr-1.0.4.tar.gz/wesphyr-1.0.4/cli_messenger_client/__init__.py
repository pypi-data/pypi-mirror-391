import requests
import os
import sys
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.layout import Layout
from rich.align import Align
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

# Configuration
API_BASE_URL = os.getenv("API_URL", "https://www.fly.dev")
SESSION_FILE = "session.txt"

# Initialize Rich Console
console = Console()


class CLIMessenger:
    def __init__(self):
        self.user_id: Optional[str] = None
        self.load_session()
    
    def load_session(self):
        """Load saved session if exists"""
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, 'r') as f:
                    self.user_id = f.read().strip()
            except:
                pass
    
    def save_session(self):
        """Save current session"""
        with open(SESSION_FILE, 'w') as f:
            f.write(self.user_id)
    
    def clear_session(self):
        """Clear saved session"""
        self.user_id = None
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
    
    def clear_screen(self):
        """Clear the terminal screen"""
        console.clear()
    
    def print_banner(self):
        """Print a beautiful welcome banner"""
        banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║    ██╗    ██╗███████╗███████╗██████╗ ██╗  ██╗██╗   ██╗██████╗  ║
    ║    ██║    ██║██╔════╝██╔════╝██╔══██╗██║  ██║╚██╗ ██╔╝██╔══██╗ ║
    ║    ██║ █╗ ██║█████╗  ███████╗██████╔╝███████║ ╚████╔╝ ██████╔╝ ║
    ║    ██║███╗██║██╔══╝  ╚════██║██╔═══╝ ██╔══██║  ╚██╔╝  ██╔══██╗ ║
    ║    ╚███╔███╔╝███████╗███████║██║     ██║  ██║   ██║   ██║  ██║ ║
    ║     ╚══╝╚══╝ ╚══════╝╚══════╝╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ║
    ║                                                           ║
    ║              📬 Secure Messaging - Retro Style 📬        ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
        """
        console.print(banner, style="bold cyan")
    
    def show_success(self, message: str):
        """Show success message"""
        console.print(f"✅ {message}", style="bold green")
    
    def show_error(self, message: str):
        """Show error message"""
        console.print(f"❌ {message}", style="bold red")
    
    def show_warning(self, message: str):
        """Show warning message"""
        console.print(f"⚠️  {message}", style="bold yellow")
    
    def show_info(self, message: str):
        """Show info message"""
        console.print(f"ℹ️  {message}", style="bold blue")
    
    def register(self):
        """Register a new user with beautiful UI"""
        self.clear_screen()
        
        # Registration panel
        console.print(Panel.fit(
            "[bold cyan]🎉 CREATE YOUR ACCOUNT 🎉[/bold cyan]\n\n"
            "[yellow]You'll receive a unique 6-digit User ID[/yellow]",
            border_style="cyan"
        ))
        console.print()
        
        # Password input
        password = Prompt.ask("[bold green]🔐 Create Password[/bold green]", password=True)
        
        if len(password) < 4:
            self.show_error("Password must be at least 4 characters!")
            console.input("\n[dim]Press Enter to continue...[/dim]")
            return
        
        confirm_password = Prompt.ask("[bold green]🔐 Confirm Password[/bold green]", password=True)
        
        if password != confirm_password:
            self.show_error("Passwords don't match!")
            console.input("\n[dim]Press Enter to continue...[/dim]")
            return
        
        # Show loading spinner
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Creating your account...", total=None)
            
            try:
                response = requests.post(
                    f"{API_BASE_URL}/register",
                    json={"password": password},
                    timeout=10
                )
                
                if response.status_code == 201:
                    data = response.json()
                    
                    # Success message with user ID
                    console.print()
                    success_panel = Panel.fit(
                        f"[bold green]🎊 REGISTRATION SUCCESSFUL! 🎊[/bold green]\n\n"
                        f"[bold yellow]YOUR USER ID:[/bold yellow] [bold cyan on black] {data['user_id']} [/bold cyan on black]\n\n"
                        f"[yellow]⚠️  IMPORTANT: Save this ID![/yellow]\n"
                        f"[dim]You'll need it to login[/dim]",
                        border_style="green",
                        box=box.DOUBLE
                    )
                    console.print(Align.center(success_panel))
                    
                else:
                    self.show_error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
            
            except requests.RequestException as e:
                self.show_error(f"Connection error: {e}")
            except Exception as e:
                self.show_error(f"Unexpected error: {e}")
        
        console.input("\n[dim]Press Enter to continue...[/dim]")
    
    def login(self):
        """Login with beautiful UI"""
        self.clear_screen()
        
        console.print(Panel.fit(
            "[bold cyan]🔓 LOGIN TO YOUR ACCOUNT 🔓[/bold cyan]",
            border_style="cyan"
        ))
        console.print()
        
        user_id = Prompt.ask("[bold green]👤 User ID (6 digits)[/bold green]")
        password = Prompt.ask("[bold green]🔐 Password[/bold green]", password=True)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Logging in...", total=None)
            
            try:
                response = requests.post(
                    f"{API_BASE_URL}/login",
                    json={"user_id": user_id, "password": password},
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.user_id = user_id
                    self.save_session()
                    self.show_success("Login successful! Welcome back! 👋")
                else:
                    self.show_error(f"Login failed: {response.json().get('detail', 'Invalid credentials')}")
            
            except requests.RequestException as e:
                self.show_error(f"Connection error: {e}")
            except Exception as e:
                self.show_error(f"Unexpected error: {e}")
        
        console.input("\n[dim]Press Enter to continue...[/dim]")
    
    def send_friend_request(self):
        """Send friend request with beautiful UI"""
        self.clear_screen()
        
        console.print(Panel.fit(
            "[bold cyan]👥 SEND FRIEND REQUEST 👥[/bold cyan]",
            border_style="cyan"
        ))
        console.print()
        
        friend_id = Prompt.ask("[bold green]👤 Enter friend's User ID[/bold green]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Sending friend request...", total=None)
            
            try:
                response = requests.post(
                    f"{API_BASE_URL}/friends/request",
                    params={"user_id": self.user_id},
                    json={"friend_id": friend_id},
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.show_success(f"Friend request sent to {friend_id}! 🎉")
                else:
                    self.show_error(response.json().get('detail', 'Unknown error'))
            
            except requests.RequestException as e:
                self.show_error(f"Connection error: {e}")
            except Exception as e:
                self.show_error(f"Unexpected error: {e}")
        
        console.input("\n[dim]Press Enter to continue...[/dim]")
    
    def view_friend_requests(self):
        """View and respond to friend requests with beautiful table"""
        self.clear_screen()
        
        console.print(Panel.fit(
            "[bold cyan]📬 FRIEND REQUESTS 📬[/bold cyan]",
            border_style="cyan"
        ))
        console.print()
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/friends/requests",
                params={"user_id": self.user_id},
                timeout=10
            )
            
            if response.status_code == 200:
                requests_list = response.json()
                
                if not requests_list:
                    self.show_info("No pending friend requests 📭")
                    console.input("\n[dim]Press Enter to continue...[/dim]")
                    return
                
                # Create beautiful table
                table = Table(title="Pending Friend Requests", box=box.ROUNDED, border_style="cyan")
                table.add_column("#", style="cyan", justify="center")
                table.add_column("From User ID", style="green", justify="center")
                table.add_column("Date", style="yellow")
                
                for idx, req in enumerate(requests_list, 1):
                    date_str = datetime.fromisoformat(req['created_at']).strftime("%Y-%m-%d %H:%M")
                    table.add_row(str(idx), req['friend_id'], date_str)
                
                console.print(table)
                console.print()
                
                choice = Prompt.ask(
                    "[bold green]Enter number to respond (or 0 to go back)[/bold green]",
                    default="0"
                )
                
                try:
                    choice = int(choice)
                    if choice == 0:
                        return
                    
                    if 1 <= choice <= len(requests_list):
                        friend_id = requests_list[choice - 1]['friend_id']
                        
                        action = Prompt.ask(
                            f"[bold yellow]Accept or Reject {friend_id}?[/bold yellow]",
                            choices=["accept", "reject", "cancel"],
                            default="cancel"
                        )
                        
                        if action == "cancel":
                            return
                        
                        with Progress(
                            SpinnerColumn(),
                            TextColumn("[progress.description]{task.description}"),
                            console=console,
                        ) as progress:
                            task = progress.add_task(f"[cyan]Processing request...", total=None)
                            
                            resp = requests.post(
                                f"{API_BASE_URL}/friends/respond",
                                params={"user_id": self.user_id, "action": action},
                                json={"friend_id": friend_id},
                                timeout=10
                            )
                            
                            if resp.status_code == 200:
                                if action == "accept":
                                    self.show_success(f"You are now friends with {friend_id}! 🎉")
                                else:
                                    self.show_warning(f"Friend request from {friend_id} rejected")
                            else:
                                self.show_error(resp.json().get('detail', 'Unknown error'))
                    else:
                        self.show_error("Invalid number!")
                except ValueError:
                    self.show_error("Please enter a valid number!")
            else:
                self.show_error(response.json().get('detail', 'Unknown error'))
        
        except requests.RequestException as e:
            self.show_error(f"Connection error: {e}")
        except Exception as e:
            self.show_error(f"Unexpected error: {e}")
        
        console.input("\n[dim]Press Enter to continue...[/dim]")
    
    def view_friends(self):
        """View all friends with beautiful table"""
        self.clear_screen()
        
        console.print(Panel.fit(
            "[bold cyan]👥 MY FRIENDS 👥[/bold cyan]",
            border_style="cyan"
        ))
        console.print()
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/friends",
                params={"user_id": self.user_id},
                timeout=10
            )
            
            if response.status_code == 200:
                friends = response.json()
                
                if not friends:
                    self.show_info("You don't have any friends yet 😢")
                    console.print("\n[dim]Send friend requests to connect with others![/dim]")
                else:
                    # Create beautiful table
                    table = Table(title=f"Your Friends ({len(friends)})", box=box.ROUNDED, border_style="green")
                    table.add_column("#", style="cyan", justify="center")
                    table.add_column("Friend ID", style="green", justify="center")
                    table.add_column("Friends Since", style="yellow")
                    
                    for idx, friend in enumerate(friends, 1):
                        date_str = datetime.fromisoformat(friend['created_at']).strftime("%Y-%m-%d")
                        table.add_row(str(idx), friend['friend_id'], date_str)
                    
                    console.print(table)
            else:
                self.show_error(response.json().get('detail', 'Unknown error'))
        
        except requests.RequestException as e:
            self.show_error(f"Connection error: {e}")
        except Exception as e:
            self.show_error(f"Unexpected error: {e}")
        
        console.input("\n[dim]Press Enter to continue...[/dim]")
    
    def send_message(self):
        """Send message with beautiful UI"""
        self.clear_screen()
        
        console.print(Panel.fit(
            "[bold cyan]✉️  SEND MESSAGE ✉️[/bold cyan]",
            border_style="cyan"
        ))
        console.print()
        
        receiver_id = Prompt.ask("[bold green]👤 To (User ID)[/bold green]")
        
        console.print("\n[bold yellow]📝 Message content:[/bold yellow]")
        console.print("[dim]Type your message (press Enter twice when done)[/dim]\n")
        
        lines = []
        while True:
            line = input()
            if line:
                lines.append(line)
            else:
                if lines:
                    break
        
        content = "\n".join(lines)
        
        if not content.strip():
            self.show_error("Message cannot be empty!")
            console.input("\n[dim]Press Enter to continue...[/dim]")
            return
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Sending message...", total=None)
            
            try:
                response = requests.post(
                    f"{API_BASE_URL}/messages",
                    params={"user_id": self.user_id},
                    json={"receiver_id": receiver_id, "content": content},
                    timeout=10
                )
                
                if response.status_code == 201:
                    self.show_success(f"Message sent to {receiver_id}! 📤")
                else:
                    self.show_error(response.json().get('detail', 'Unknown error'))
            
            except requests.RequestException as e:
                self.show_error(f"Connection error: {e}")
            except Exception as e:
                self.show_error(f"Unexpected error: {e}")
        
        console.input("\n[dim]Press Enter to continue...[/dim]")
    
    def view_inbox(self):
        """View inbox with beautiful UI"""
        self.clear_screen()
        
        console.print(Panel.fit(
            "[bold cyan]📬 INBOX 📬[/bold cyan]",
            border_style="cyan"
        ))
        console.print()
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/messages/inbox",
                params={"user_id": self.user_id},
                timeout=10
            )
            
            if response.status_code == 200:
                messages = response.json()
                
                if not messages:
                    self.show_info("Your inbox is empty 📭")
                    console.input("\n[dim]Press Enter to continue...[/dim]")
                    return
                
                # Count unread messages
                unread_count = sum(1 for m in messages if not m['is_read'])
                
                console.print(f"[bold green]You have {len(messages)} message(s)[/bold green]", end="")
                if unread_count > 0:
                    console.print(f" [bold yellow]({unread_count} unread)[/bold yellow]")
                else:
                    console.print()
                console.print()
                
                # Display messages
                for idx, msg in enumerate(messages, 1):
                    status = "✅ READ" if msg['is_read'] else "🆕 NEW"
                    status_style = "green" if msg['is_read'] else "yellow"
                    
                    date_str = datetime.fromisoformat(msg['created_at']).strftime("%Y-%m-%d %H:%M")
                    
                    message_panel = Panel(
                        f"[bold cyan]From:[/bold cyan] {msg['sender_id']}  |  [{status_style}]{status}[/{status_style}]\n"
                        f"[dim]{date_str}[/dim]\n\n"
                        f"{msg['content']}",
                        title=f"[bold cyan]Message {idx}[/bold cyan]",
                        border_style=status_style,
                        box=box.ROUNDED
                    )
                    console.print(message_panel)
                    console.print()
                
                choice = Prompt.ask(
                    "[bold green]Enter message number to mark as read (0 to go back)[/bold green]",
                    default="0"
                )
                
                try:
                    choice = int(choice)
                    if choice > 0 and choice <= len(messages):
                        msg_id = messages[choice - 1]['id']
                        
                        resp = requests.post(
                            f"{API_BASE_URL}/messages/{msg_id}/read",
                            params={"user_id": self.user_id},
                            timeout=10
                        )
                        
                        if resp.status_code == 200:
                            self.show_success("Message marked as read! ✅")
                        else:
                            self.show_error(resp.json().get('detail', 'Unknown error'))
                        
                        console.input("\n[dim]Press Enter to continue...[/dim]")
                except ValueError:
                    pass
            else:
                self.show_error(response.json().get('detail', 'Unknown error'))
                console.input("\n[dim]Press Enter to continue...[/dim]")
        
        except requests.RequestException as e:
            self.show_error(f"Connection error: {e}")
            console.input("\n[dim]Press Enter to continue...[/dim]")
        except Exception as e:
            self.show_error(f"Unexpected error: {e}")
            console.input("\n[dim]Press Enter to continue...[/dim]")
    
    def view_sent_messages(self):
        """View sent messages with beautiful UI"""
        self.clear_screen()
        
        console.print(Panel.fit(
            "[bold cyan]📤 SENT MESSAGES 📤[/bold cyan]",
            border_style="cyan"
        ))
        console.print()
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/messages/sent",
                params={"user_id": self.user_id},
                timeout=10
            )
            
            if response.status_code == 200:
                messages = response.json()
                
                if not messages:
                    self.show_info("You haven't sent any messages yet 📭")
                else:
                    console.print(f"[bold green]You have sent {len(messages)} message(s)[/bold green]\n")
                    
                    for idx, msg in enumerate(messages, 1):
                        status = "✅ READ" if msg['is_read'] else "⏳ UNREAD"
                        status_style = "green" if msg['is_read'] else "yellow"
                        
                        date_str = datetime.fromisoformat(msg['created_at']).strftime("%Y-%m-%d %H:%M")
                        
                        message_panel = Panel(
                            f"[bold cyan]To:[/bold cyan] {msg['receiver_id']}  |  [{status_style}]{status}[/{status_style}]\n"
                            f"[dim]{date_str}[/dim]\n\n"
                            f"{msg['content']}",
                            title=f"[bold cyan]Message {idx}[/bold cyan]",
                            border_style="cyan",
                            box=box.ROUNDED
                        )
                        console.print(message_panel)
                        console.print()
            else:
                self.show_error(response.json().get('detail', 'Unknown error'))
        
        except requests.RequestException as e:
            self.show_error(f"Connection error: {e}")
        except Exception as e:
            self.show_error(f"Unexpected error: {e}")
        
        console.input("\n[dim]Press Enter to continue...[/dim]")
    
    def main_menu(self):
        """Display beautiful main menu"""
        while True:
            self.clear_screen()
            
            # Header panel
            header = Panel(
                f"[bold cyan]WELCOME, USER {self.user_id}! 👋[/bold cyan]",
                border_style="cyan",
                box=box.DOUBLE
            )
            console.print(Align.center(header))
            console.print()
            
            # Menu options table
            menu_table = Table(show_header=False, box=box.SIMPLE, border_style="cyan")
            menu_table.add_column("Option", style="cyan bold", justify="right")
            menu_table.add_column("Description", style="white")
            
            menu_table.add_row("1", "👥 View Friends")
            menu_table.add_row("2", "📬 View Friend Requests")
            menu_table.add_row("3", "➕ Send Friend Request")
            menu_table.add_row("4", "📬 View Inbox")
            menu_table.add_row("5", "📤 View Sent Messages")
            menu_table.add_row("6", "✉️  Send Message")
            menu_table.add_row("7", "🚪 Logout")
            menu_table.add_row("8", "❌ Exit")
            
            console.print(menu_table)
            console.print()
            
            choice = Prompt.ask(
                "[bold green]Select option[/bold green]",
                choices=["1", "2", "3", "4", "5", "6", "7", "8"],
                default="1"
            )
            
            if choice == '1':
                self.view_friends()
            elif choice == '2':
                self.view_friend_requests()
            elif choice == '3':
                self.send_friend_request()
            elif choice == '4':
                self.view_inbox()
            elif choice == '5':
                self.view_sent_messages()
            elif choice == '6':
                self.send_message()
            elif choice == '7':
                if Confirm.ask("[yellow]Are you sure you want to logout?[/yellow]"):
                    self.clear_session()
                    self.show_success("Logged out successfully! 👋")
                    time.sleep(1)
                    break
            elif choice == '8':
                if Confirm.ask("[yellow]Are you sure you want to exit?[/yellow]"):
                    console.print("\n[bold cyan]👋 Goodbye! Thanks for using WESPHYR![/bold cyan]\n")
                    sys.exit(0)
    
    def start(self):
        """Start the application with beautiful welcome screen"""
        while True:
            if self.user_id:
                self.main_menu()
            else:
                self.clear_screen()
                self.print_banner()
                console.print()
                
                # Welcome menu
                welcome_panel = Panel(
                    "[bold cyan]🎉 WELCOME TO WESPHYR! 🎉[/bold cyan]\n\n"
                    "[yellow]The retro way to stay connected[/yellow]",
                    border_style="cyan",
                    box=box.DOUBLE
                )
                console.print(Align.center(welcome_panel))
                console.print()
                
                # Menu options
                menu_table = Table(show_header=False, box=box.SIMPLE, border_style="cyan")
                menu_table.add_column("Option", style="cyan bold", justify="right")
                menu_table.add_column("Description", style="white")
                
                menu_table.add_row("1", "🎉 Register (Create New Account)")
                menu_table.add_row("2", "🔓 Login (Existing Account)")
                menu_table.add_row("3", "❌ Exit")
                
                console.print(menu_table)
                console.print()
                
                choice = Prompt.ask(
                    "[bold green]Select option[/bold green]",
                    choices=["1", "2", "3"],
                    default="2"
                )
                
                if choice == '1':
                    self.register()
                elif choice == '2':
                    self.login()
                elif choice == '3':
                    console.print("\n[bold cyan]👋 Goodbye! Thanks for checking out WESPHYR![/bold cyan]\n")
                    sys.exit(0)


def main():
    """Main entry point for the CLI messenger client"""
    console.clear()
    
    # Show connection status
    console.print("\n[bold cyan]🚀 Starting WESPHYR...[/bold cyan]")
    console.print(f"[cyan]📡 Connecting to:[/cyan] {API_BASE_URL}")
    
    # Test server connection with progress bar
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Checking server connection...", total=None)
            response = requests.get(f"{API_BASE_URL}/", timeout=10)
            
            if response.status_code == 200:
                console.print("[bold green]✅ Connected to server![/bold green]\n")
                time.sleep(1)
            else:
                console.print("[bold yellow]⚠️  Server responded with unexpected status[/bold yellow]\n")
                time.sleep(1)
    except requests.RequestException:
        console.print("\n[bold red]❌ Cannot connect to server![/bold red]")
        console.print(f"[yellow]   Make sure the server is running at {API_BASE_URL}[/yellow]")
        console.print("[dim]   Set environment variable: export API_URL=https://www.fly.dev[/dim]")
        console.input("\n[dim]Press Enter to exit...[/dim]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]❌ Unexpected error: {e}[/bold red]")
        console.input("\n[dim]Press Enter to exit...[/dim]")
        sys.exit(1)
    
    # Start the app
    app = CLIMessenger()
    app.start()


if __name__ == "__main__":
    main()
