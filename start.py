#!/usr/bin/env python3
"""
Startup script for Quantum-Enhanced AI Logistics Engine
D3CODE 2025 Hackathon Project
"""

import subprocess
import sys
import time
import os
import signal
from threading import Thread

class LogisticsEngineStarter:
    def __init__(self):
        self.python_process = None
        self.node_process = None
        self.running = True
        
    def start_python_backend(self):
        """Start the Python Flask backend"""
        print("🐍 Starting Python backend...")
        try:
            self.python_process = subprocess.Popen([
                sys.executable, 'solver.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("✅ Python backend started on http://localhost:5000")
            return True
        except Exception as e:
            print(f"❌ Failed to start Python backend: {e}")
            return False
    
    def start_node_frontend(self):
        """Start the Node.js frontend"""
        print("🌐 Starting Node.js frontend...")
        try:
            self.node_process = subprocess.Popen([
                'node', 'server.js'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("✅ Node.js frontend started on http://localhost:3000")
            return True
        except Exception as e:
            print(f"❌ Failed to start Node.js frontend: {e}")
            return False
    
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("🔍 Checking dependencies...")
        
        # Check Python dependencies
        try:
            import numpy, scipy, pandas, sklearn, flask, dimod
            print("✅ Python dependencies OK")
        except ImportError as e:
            print(f"❌ Missing Python dependency: {e}")
            print("Run: pip install -r requirements.txt")
            return False
        
        # Check Node.js dependencies
        if not os.path.exists('node_modules'):
            print("❌ Node.js dependencies not installed")
            print("Run: npm install")
            return False
        else:
            print("✅ Node.js dependencies OK")
        
        return True
    
    def start(self):
        """Start both backend and frontend"""
        print("🚀 Starting Quantum-Enhanced AI Logistics Engine")
        print("=" * 60)
        
        if not self.check_dependencies():
            return False
        
        # Start Python backend
        if not self.start_python_backend():
            return False
        
        # Wait a moment for backend to start
        time.sleep(3)
        
        # Start Node.js frontend
        if not self.start_node_frontend():
            self.stop()
            return False
        
        print("\n🎉 System started successfully!")
        print("📱 Frontend: http://localhost:3000")
        print("🔧 Backend API: http://localhost:5000")
        print("\nPress Ctrl+C to stop")
        
        return True
    
    def stop(self):
        """Stop both processes"""
        print("\n🛑 Stopping services...")
        
        if self.python_process:
            self.python_process.terminate()
            print("✅ Python backend stopped")
        
        if self.node_process:
            self.node_process.terminate()
            print("✅ Node.js frontend stopped")
        
        print("👋 Goodbye!")
    
    def run(self):
        """Main run loop"""
        try:
            if self.start():
                # Keep running until interrupted
                while self.running:
                    time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        finally:
            self.stop()

def main():
    """Main entry point"""
    starter = LogisticsEngineStarter()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        starter.running = False
        starter.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    starter.run()

if __name__ == "__main__":
    main()
