import requests
import os
import sys
from datetime import datetime
from typing import Optional

# Configuration
API_BASE_URL = os.getenv("API_URL", "https://wesphyr.fly.dev")  # Defaults to your server
SESSION_FILE = "session.txt"


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
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, text: str):
        """Print a formatted header"""
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60)
    
    def register(self):
        """Register a new user"""
        self.clear_screen()
        self.print_header("REGISTRATION")
        
        print("\nCreate a password for your account.")
        password = input("Password: ").strip()
        
        if len(password) < 4:
            print("❌ Password must be at least 4 characters!")
            input("\nPress Enter to continue...")
            return
        
        confirm_password = input("Confirm Password: ").strip()
        
        if password != confirm_password:
            print("❌ Passwords don't match!")
            input("\nPress Enter to continue...")
            return
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/register",
                json={"password": password}
            )
            
            if response.status_code == 201:
                data = response.json()
                print(f"\n✅ Registration successful!")
                print(f"\n╔════════════════════════════════╗")
                print(f"║   YOUR USER ID: {data['user_id']}        ║")
                print(f"╚════════════════════════════════╝")
                print("\n⚠️  IMPORTANT: Save this ID! You'll need it to login.")
                input("\nPress Enter to continue...")
            else:
                print(f"❌ Registration failed: {response.json().get('detail', 'Unknown error')}")
                input("\nPress Enter to continue...")
        except Exception as e:
            print(f"❌ Error: {e}")
            input("\nPress Enter to continue...")
    
    def login(self):
        """Login with user ID and password"""
        self.clear_screen()
        self.print_header("LOGIN")
        
        user_id = input("\nUser ID (6 digits): ").strip()
        password = input("Password: ").strip()
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/login",
                json={"user_id": user_id, "password": password}
            )
            
            if response.status_code == 200:
                self.user_id = user_id
                self.save_session()
                print("\n✅ Login successful!")
                input("\nPress Enter to continue...")
            else:
                print(f"❌ Login failed: {response.json().get('detail', 'Invalid credentials')}")
                input("\nPress Enter to continue...")
        except Exception as e:
            print(f"❌ Error: {e}")
            input("\nPress Enter to continue...")
    
    def send_friend_request(self):
        """Send a friend request"""
        self.clear_screen()
        self.print_header("SEND FRIEND REQUEST")
        
        friend_id = input("\nEnter friend's User ID: ").strip()
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/friends/request",
                params={"user_id": self.user_id},
                json={"friend_id": friend_id}
            )
            
            if response.status_code == 200:
                print("\n✅ Friend request sent!")
            else:
                print(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
            
            input("\nPress Enter to continue...")
        except Exception as e:
            print(f"❌ Error: {e}")
            input("\nPress Enter to continue...")
    
    def view_friend_requests(self):
        """View and respond to friend requests"""
        self.clear_screen()
        self.print_header("FRIEND REQUESTS")
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/friends/requests",
                params={"user_id": self.user_id}
            )
            
            if response.status_code == 200:
                requests_list = response.json()
                
                if not requests_list:
                    print("\n📭 No pending friend requests.")
                    input("\nPress Enter to continue...")
                    return
                
                print(f"\n📬 You have {len(requests_list)} pending request(s):\n")
                
                for idx, req in enumerate(requests_list, 1):
                    print(f"{idx}. From: {req['friend_id']} - {req['created_at']}")
                
                print("\n" + "-" * 60)
                choice = input("\nEnter number to respond (or 0 to go back): ").strip()
                
                try:
                    choice = int(choice)
                    if choice == 0:
                        return
                    
                    if 1 <= choice <= len(requests_list):
                        friend_id = requests_list[choice - 1]['friend_id']
                        action = input(f"\nAccept or Reject {friend_id}? (a/r): ").strip().lower()
                        
                        if action in ['a', 'r']:
                            action_text = "accept" if action == 'a' else "reject"
                            
                            resp = requests.post(
                                f"{API_BASE_URL}/friends/respond",
                                params={"user_id": self.user_id, "action": action_text},
                                json={"friend_id": friend_id}
                            )
                            
                            if resp.status_code == 200:
                                print(f"\n✅ Friend request {action_text}ed!")
                            else:
                                print(f"❌ Error: {resp.json().get('detail', 'Unknown error')}")
                        else:
                            print("❌ Invalid choice!")
                    else:
                        print("❌ Invalid number!")
                except ValueError:
                    print("❌ Please enter a number!")
                
                input("\nPress Enter to continue...")
            else:
                print(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                input("\nPress Enter to continue...")
        except Exception as e:
            print(f"❌ Error: {e}")
            input("\nPress Enter to continue...")
    
    def view_friends(self):
        """View all friends"""
        self.clear_screen()
        self.print_header("MY FRIENDS")
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/friends",
                params={"user_id": self.user_id}
            )
            
            if response.status_code == 200:
                friends = response.json()
                
                if not friends:
                    print("\n👤 You have no friends yet.")
                    print("   Send friend requests to connect with others!")
                else:
                    print(f"\n👥 You have {len(friends)} friend(s):\n")
                    for idx, friend in enumerate(friends, 1):
                        print(f"{idx}. {friend['friend_id']}")
                
                input("\nPress Enter to continue...")
            else:
                print(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                input("\nPress Enter to continue...")
        except Exception as e:
            print(f"❌ Error: {e}")
            input("\nPress Enter to continue...")
    
    def send_message(self):
        """Send a message to a friend"""
        self.clear_screen()
        self.print_header("SEND MESSAGE")
        
        receiver_id = input("\nRecipient User ID: ").strip()
        
        print("\nEnter your message (type END on a new line to finish):")
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        
        content = "\n".join(lines).strip()
        
        if not content:
            print("❌ Message cannot be empty!")
            input("\nPress Enter to continue...")
            return
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/messages",
                params={"user_id": self.user_id},
                json={"receiver_id": receiver_id, "content": content}
            )
            
            if response.status_code == 201:
                print("\n✅ Message sent!")
            else:
                print(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
            
            input("\nPress Enter to continue...")
        except Exception as e:
            print(f"❌ Error: {e}")
            input("\nPress Enter to continue...")
    
    def view_inbox(self):
        """View received messages"""
        self.clear_screen()
        self.print_header("INBOX")
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/messages/inbox",
                params={"user_id": self.user_id}
            )
            
            if response.status_code == 200:
                messages = response.json()
                
                if not messages:
                    print("\n📭 Your inbox is empty.")
                    input("\nPress Enter to continue...")
                    return
                
                print(f"\n📬 You have {len(messages)} message(s):\n")
                
                for idx, msg in enumerate(messages, 1):
                    status = "✅ READ" if msg['is_read'] else "🆕 NEW"
                    print(f"\n{'-' * 60}")
                    print(f"[{idx}] From: {msg['sender_id']} | {status}")
                    print(f"Date: {msg['created_at']}")
                    print(f"\n{msg['content']}")
                
                print(f"\n{'-' * 60}")
                
                choice = input("\nEnter message number to mark as read (0 to go back): ").strip()
                
                try:
                    choice = int(choice)
                    if choice > 0 and choice <= len(messages):
                        msg_id = messages[choice - 1]['id']
                        
                        resp = requests.post(
                            f"{API_BASE_URL}/messages/{msg_id}/read",
                            params={"user_id": self.user_id}
                        )
                        
                        if resp.status_code == 200:
                            print("\n✅ Message marked as read!")
                        else:
                            print(f"❌ Error: {resp.json().get('detail', 'Unknown error')}")
                        
                        input("\nPress Enter to continue...")
                except ValueError:
                    pass
            else:
                print(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                input("\nPress Enter to continue...")
        except Exception as e:
            print(f"❌ Error: {e}")
            input("\nPress Enter to continue...")
    
    def view_sent_messages(self):
        """View sent messages"""
        self.clear_screen()
        self.print_header("SENT MESSAGES")
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/messages/sent",
                params={"user_id": self.user_id}
            )
            
            if response.status_code == 200:
                messages = response.json()
                
                if not messages:
                    print("\n📭 You haven't sent any messages yet.")
                else:
                    print(f"\n📤 You have sent {len(messages)} message(s):\n")
                    
                    for idx, msg in enumerate(messages, 1):
                        status = "✅ READ" if msg['is_read'] else "⏳ UNREAD"
                        print(f"\n{'-' * 60}")
                        print(f"[{idx}] To: {msg['receiver_id']} | {status}")
                        print(f"Date: {msg['created_at']}")
                        print(f"\n{msg['content']}")
                    
                    print(f"\n{'-' * 60}")
                
                input("\nPress Enter to continue...")
            else:
                print(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                input("\nPress Enter to continue...")
        except Exception as e:
            print(f"❌ Error: {e}")
            input("\nPress Enter to continue...")
    
    def main_menu(self):
        """Display main menu when logged in"""
        while True:
            self.clear_screen()
            self.print_header(f"MAIN MENU - User: {self.user_id}")
            
            print("\n1. View Friends")
            print("2. View Friend Requests")
            print("3. Send Friend Request")
            print("4. View Inbox")
            print("5. View Sent Messages")
            print("6. Send Message")
            print("7. Logout")
            print("8. Exit")
            
            choice = input("\nSelect option: ").strip()
            
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
                self.clear_session()
                break
            elif choice == '8':
                sys.exit(0)
            else:
                print("❌ Invalid option!")
                input("\nPress Enter to continue...")
    
    def start(self):
        """Start the CLI application"""
        while True:
            if self.user_id:
                self.main_menu()
            else:
                self.clear_screen()
                self.print_header("WESPHYR - Welcome!")
                
                print("\n1. Register")
                print("2. Login")
                print("3. Exit")
                
                choice = input("\nSelect option: ").strip()
                
                if choice == '1':
                    self.register()
                elif choice == '2':
                    self.login()
                elif choice == '3':
                    sys.exit(0)
                else:
                    print("❌ Invalid option!")
                    input("\nPress Enter to continue...")


def main():
    """Entry point for the CLI client"""
    print("\n🚀 Starting CLI Messenger...")
    print(f"📡 Connecting to: {API_BASE_URL}")
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            print("✅ Connected to server!\n")
        else:
            print("⚠️  Server responded with unexpected status")
    except:
        print("❌ Cannot connect to server!")
        print(f"   Make sure the server is running at {API_BASE_URL}")
        print("   Run: python server.py")
        input("\nPress Enter to exit...")
        sys.exit(1)

    app = CLIMessenger()
    app.start()


def main():
    """Main entry point for the CLI messenger client"""
    try:
        # Test server connection
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        if response.status_code != 200:
            raise requests.RequestException("Server not responding")
    except:
        print("❌ Cannot connect to server!")
        print(f"   Make sure the server is running at {API_BASE_URL}")
        print("   For your server, set: export API_URL=https://wesphyr.fly.dev")
        input("\nPress Enter to exit...")
        sys.exit(1)

    app = CLIMessenger()
    app.start()


if __name__ == "__main__":
    main()
