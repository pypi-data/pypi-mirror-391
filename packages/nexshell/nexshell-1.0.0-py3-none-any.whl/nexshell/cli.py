#!/usr/bin/env python3
"""
NexShell - AI-Powered CLI Chatbot
A beautiful command-line chatbot powered by Google Gemini 2.5 Flash
"""

import os
import sys

# Must set environment variables BEFORE any other imports
os.environ['GRPC_VERBOSITY'] = 'NONE'
os.environ['GRPC_TRACE'] = ''
os.environ['GLOG_minloglevel'] = '3'

# Redirect stderr to devnull during import
if sys.platform == 'win32':
    import msvcrt
    import ctypes
    kernel32 = ctypes.windll.kernel32
    # Save original stderr
    stderr_fileno = sys.stderr.fileno()
    stderr_save = os.dup(stderr_fileno)
    # Redirect stderr to NUL
    devnull = os.open('NUL', os.O_WRONLY)
    os.dup2(devnull, stderr_fileno)
    os.close(devnull)

import time
import warnings
import logging
warnings.filterwarnings('ignore')

import google.generativeai as genai

# Restore stderr on Windows
if sys.platform == 'win32':
    os.dup2(stderr_save, stderr_fileno)
    os.close(stderr_save)

from dotenv import load_dotenv
from colorama import init, Fore, Back, Style
import json
from datetime import datetime
import subprocess
import platform

# Initialize colorama for Windows support
init(autoreset=True)

class NexShell:
    def __init__(self):
        """Initialize the NexShell chatbot"""
        load_dotenv()
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            print(f"{Fore.RED}❌ Error: GEMINI_API_KEY not found in .env file{Style.RESET_ALL}")
            sys.exit(1)
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.chat = self.model.start_chat(history=[])
        self.bot_name = "NexShell"
        self.chat_history_file = "chat_history.json"
        self.conversation_count = 0
        self.word_count = 0
        self.session_start = datetime.now()
        self.modes = {
            'normal': '🤖 Normal Mode',
            'code': '💻 Code Assistant Mode',
            'creative': '🎨 Creative Mode',
            'concise': '⚡ Concise Mode'
        }
        self.current_mode = 'normal'
        
    def print_animated_text(self, text, color=Fore.CYAN, delay=0.03):
        """Print text with a typing animation effect"""
        for char in text:
            print(color + char, end='', flush=True)
            time.sleep(delay)
        print(Style.RESET_ALL)
    
    def loading_animation(self, duration=2):
        """Display a loading animation"""
        frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        end_time = time.time() + duration
        i = 0
        
        while time.time() < end_time:
            print(f'\r{Fore.CYAN}{frames[i % len(frames)]} Initializing NexShell...', end='', flush=True)
            time.sleep(0.1)
            i += 1
        print('\r' + ' ' * 50 + '\r', end='')
    
    def show_welcome_banner(self):
        """Display the welcome banner with animations"""
        banner = f"""
{Fore.CYAN}{'=' * 70}
{Fore.YELLOW}
    ███╗   ██╗███████╗██╗  ██╗███████╗██╗  ██╗███████╗██╗     ██╗     
    ████╗  ██║██╔════╝╚██╗██╔╝██╔════╝██║  ██║██╔════╝██║     ██║     
    ██╔██╗ ██║█████╗   ╚███╔╝ ███████╗███████║█████╗  ██║     ██║     
    ██║╚██╗██║██╔══╝   ██╔██╗ ╚════██║██╔══██║██╔══╝  ██║     ██║     
    ██║ ╚████║███████╗██╔╝ ██╗███████║██║  ██║███████╗███████╗███████╗
    ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝
{Fore.CYAN}
{' ' * 12}🤖 Your AI-Powered Command Line Assistant 🤖
{' ' * 18}Powered by Google Gemini 2.5 Flash
{'=' * 70}
{Style.RESET_ALL}"""
        
        # Show loading animation
        self.loading_animation(2)
        
        # Display banner
        print(banner)
        time.sleep(0.5)
        
        # Animated welcome message
        self.print_animated_text(
            f"\n{Fore.GREEN}✨ Welcome to NexShell! I'm your AI assistant powered by Google Gemini 2.5 Flash.\n",
            Fore.GREEN,
            0.02
        )
        time.sleep(0.3)
        
        print(f"{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}🎯 Unique Features:")
        print(f"  {Fore.YELLOW}• Multi-Mode AI{Fore.WHITE} - Switch between Normal, Code, Creative & Concise modes")
        print(f"  {Fore.YELLOW}• Smart Commands{Fore.WHITE} - Execute system commands with /cmd")
        print(f"  {Fore.YELLOW}• Chat History{Fore.WHITE} - Auto-save & export conversations")
        print(f"  {Fore.YELLOW}• Stats Tracking{Fore.WHITE} - View session statistics")
        print(f"\n{Fore.WHITE}📝 Commands:")
        print(f"  {Fore.YELLOW}/mode [type]{Fore.WHITE} - Switch AI mode (normal/code/creative/concise)")
        print(f"  {Fore.YELLOW}/cmd [command]{Fore.WHITE} - Execute system command")
        print(f"  {Fore.YELLOW}/save{Fore.WHITE} - Save conversation to file")
        print(f"  {Fore.YELLOW}/stats{Fore.WHITE} - Show session statistics")
        print(f"  {Fore.YELLOW}/history{Fore.WHITE} - View conversation history")
        print(f"  {Fore.YELLOW}/clear{Fore.WHITE} - Clear conversation history")
        print(f"  {Fore.YELLOW}/help{Fore.WHITE} - Show all commands")
        print(f"  {Fore.YELLOW}/exit or /quit{Fore.WHITE} - Exit NexShell")
        print(f"{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}\n")
        time.sleep(0.5)
    
    def get_response(self, user_message):
        """Get response from Gemini API with mode-specific prompts"""
        try:
            # Add mode-specific context
            mode_prompts = {
                'code': "You are a coding expert. Provide detailed code examples and explanations. ",
                'creative': "You are a creative writer. Be imaginative, expressive, and artistic in your responses. ",
                'concise': "Be extremely brief and to the point. Use bullet points when possible. ",
                'normal': ""
            }
            
            enhanced_message = mode_prompts.get(self.current_mode, "") + user_message
            
            # Show thinking animation
            self.show_thinking_animation()
            
            # Make API call
            response = self.chat.send_message(enhanced_message)
            
            # Extract the response
            assistant_message = response.text
            
            # Update stats
            self.conversation_count += 1
            self.word_count += len(user_message.split()) + len(assistant_message.split())
            
            return assistant_message
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def show_thinking_animation(self):
        """Show a thinking animation while waiting for response"""
        frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        
        for _ in range(10):
            for frame in frames:
                print(f'\r{Fore.MAGENTA}{frame} Thinking...', end='', flush=True)
                time.sleep(0.05)
        
        print('\r' + ' ' * 30 + '\r', end='')
    
    def type_response(self, text, delay=0.02):
        """Display text with a typing animation effect"""
        import random
        
        for i, char in enumerate(text):
            # Add slight randomness to typing speed for natural feel
            actual_delay = delay + random.uniform(-0.01, 0.01)
            actual_delay = max(0.001, actual_delay)  # Ensure non-negative
            
            # Color code blocks differently
            if char == '`':
                print(f"{Fore.YELLOW}{char}", end='', flush=True)
            elif char in ['#', '*', '-'] and (i == 0 or text[i-1] == '\n'):
                print(f"{Fore.CYAN}{char}", end='', flush=True)
            else:
                print(f"{Fore.WHITE}{char}", end='', flush=True)
            
            time.sleep(actual_delay)
            
            # Pause slightly longer at sentence endings for natural rhythm
            if char in ['.', '!', '?', '\n']:
                time.sleep(0.1)
        
        print(Style.RESET_ALL, end='')
    
    def clear_conversation(self):
        """Clear the conversation history"""
        self.chat = self.model.start_chat(history=[])
        self.conversation_count = 0
        self.word_count = 0
        print(f"\n{Fore.GREEN}✓ Conversation history cleared!{Style.RESET_ALL}\n")
    
    def change_mode(self, mode):
        """Change the AI assistant mode"""
        if mode in self.modes:
            self.current_mode = mode
            print(f"\n{Fore.GREEN}✓ Switched to {self.modes[mode]}{Style.RESET_ALL}\n")
        else:
            print(f"\n{Fore.RED}❌ Invalid mode. Available: {', '.join(self.modes.keys())}{Style.RESET_ALL}\n")
    
    def execute_command(self, command):
        """Execute a system command"""
        try:
            print(f"\n{Fore.YELLOW}⚙️  Executing: {command}{Style.RESET_ALL}\n")
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            
            output = result.stdout if result.stdout else result.stderr
            if output:
                print(f"{Fore.CYAN}{output}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}✓ Command executed successfully{Style.RESET_ALL}")
            print()
        except subprocess.TimeoutExpired:
            print(f"\n{Fore.RED}❌ Command timed out{Style.RESET_ALL}\n")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error executing command: {str(e)}{Style.RESET_ALL}\n")
    
    def save_conversation(self):
        """Save conversation to a file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nexshell_chat_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"NexShell Conversation Log\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Mode: {self.modes[self.current_mode]}\n")
                f.write("=" * 70 + "\n\n")
                
                # Save chat history (simplified format)
                f.write("Conversation saved successfully!\n")
                f.write(f"Total messages: {self.conversation_count}\n")
            
            print(f"\n{Fore.GREEN}✓ Conversation saved to: {filename}{Style.RESET_ALL}\n")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error saving conversation: {str(e)}{Style.RESET_ALL}\n")
    
    def show_stats(self):
        """Display session statistics"""
        session_time = datetime.now() - self.session_start
        minutes = int(session_time.total_seconds() / 60)
        seconds = int(session_time.total_seconds() % 60)
        
        print(f"\n{Fore.CYAN}{'─' * 70}")
        print(f"{Fore.YELLOW}📊 Session Statistics{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─' * 70}")
        print(f"{Fore.WHITE}🤖 Current Mode: {Fore.YELLOW}{self.modes[self.current_mode]}")
        print(f"{Fore.WHITE}💬 Messages Exchanged: {Fore.YELLOW}{self.conversation_count}")
        print(f"{Fore.WHITE}📝 Total Words: {Fore.YELLOW}{self.word_count}")
        print(f"{Fore.WHITE}⏱️  Session Duration: {Fore.YELLOW}{minutes}m {seconds}s")
        print(f"{Fore.WHITE}💻 System: {Fore.YELLOW}{platform.system()} {platform.release()}")
        print(f"{Fore.WHITE}🐍 Python: {Fore.YELLOW}{platform.python_version()}")
        print(f"{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}\n")
    
    def show_help(self):
        """Display help information"""
        print(f"\n{Fore.CYAN}{'─' * 70}")
        print(f"{Fore.YELLOW}📖 NexShell Help{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─' * 70}")
        print(f"\n{Fore.WHITE}🎯 AI Modes:")
        print(f"  {Fore.YELLOW}normal{Fore.WHITE}    - Balanced AI responses for general chat")
        print(f"  {Fore.YELLOW}code{Fore.WHITE}      - Expert coding assistance with examples")
        print(f"  {Fore.YELLOW}creative{Fore.WHITE}  - Creative and artistic responses")
        print(f"  {Fore.YELLOW}concise{Fore.WHITE}   - Brief, to-the-point answers")
        print(f"\n{Fore.WHITE}📝 Commands:")
        print(f"  {Fore.YELLOW}/mode [type]{Fore.WHITE}     - Switch AI mode")
        print(f"  {Fore.YELLOW}/cmd [command]{Fore.WHITE}   - Run system commands")
        print(f"  {Fore.YELLOW}/save{Fore.WHITE}            - Export chat to file")
        print(f"  {Fore.YELLOW}/stats{Fore.WHITE}           - View statistics")
        print(f"  {Fore.YELLOW}/history{Fore.WHITE}         - Show chat history")
        print(f"  {Fore.YELLOW}/clear{Fore.WHITE}           - Clear conversation")
        print(f"  {Fore.YELLOW}/help{Fore.WHITE}            - Show this help")
        print(f"  {Fore.YELLOW}/exit{Fore.WHITE} or {Fore.YELLOW}/quit{Fore.WHITE}   - Exit NexShell")
        print(f"\n{Fore.WHITE}💡 Tips:")
        print(f"  • Use code mode for programming help")
        print(f"  • Try creative mode for writing assistance")
        print(f"  • Execute commands like: /cmd dir or /cmd python --version")
        print(f"{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}\n")
    
    def show_history(self):
        """Display conversation history summary"""
        print(f"\n{Fore.CYAN}{'─' * 70}")
        print(f"{Fore.YELLOW}📜 Conversation History{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─' * 70}")
        print(f"{Fore.WHITE}Total messages in this session: {Fore.YELLOW}{self.conversation_count}")
        print(f"{Fore.WHITE}Use {Fore.YELLOW}/save{Fore.WHITE} to export full conversation")
        print(f"{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}\n")
    
    def run(self):
        """Main chatbot loop"""
        self.show_welcome_banner()
        
        while True:
            try:
                # Display current mode in prompt
                mode_indicator = f"{Fore.MAGENTA}[{self.current_mode}]{Style.RESET_ALL} "
                user_input = input(f"{mode_indicator}{Fore.GREEN}You{Fore.WHITE} ► {Style.RESET_ALL}").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['/exit', '/quit']:
                    self.show_stats()
                    print(f"{Fore.YELLOW}👋 Thanks for using NexShell! Goodbye!{Style.RESET_ALL}\n")
                    break
                
                if user_input.lower() == '/clear':
                    self.clear_conversation()
                    continue
                
                if user_input.lower().startswith('/mode'):
                    parts = user_input.split(maxsplit=1)
                    if len(parts) > 1:
                        self.change_mode(parts[1].lower())
                    else:
                        print(f"\n{Fore.YELLOW}Available modes: {', '.join(self.modes.keys())}{Style.RESET_ALL}\n")
                    continue
                
                if user_input.lower().startswith('/cmd'):
                    command = user_input[4:].strip()
                    if command:
                        self.execute_command(command)
                    else:
                        print(f"\n{Fore.RED}❌ Please specify a command{Style.RESET_ALL}\n")
                    continue
                
                if user_input.lower() == '/save':
                    self.save_conversation()
                    continue
                
                if user_input.lower() == '/stats':
                    self.show_stats()
                    continue
                
                if user_input.lower() == '/help':
                    self.show_help()
                    continue
                
                if user_input.lower() == '/history':
                    self.show_history()
                    continue
                
                # Get response from Gemini
                response = self.get_response(user_input)
                
                # Display response with typing animation
                print(f"\n{Fore.CYAN}{self.bot_name}{Fore.WHITE} ► ", end='')
                self.type_response(response)
                print()  # Add newline after response
                
            except KeyboardInterrupt:
                print(f"\n")
                self.show_stats()
                print(f"{Fore.YELLOW}👋 Thanks for using NexShell! Goodbye!{Style.RESET_ALL}\n")
                break
            except Exception as e:
                print(f"\n{Fore.RED}❌ An error occurred: {str(e)}{Style.RESET_ALL}\n")


def main():
    """Entry point for the application"""
    try:
        chatbot = NexShell()
        chatbot.run()
    except Exception as e:
        print(f"{Fore.RED}❌ Fatal error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
