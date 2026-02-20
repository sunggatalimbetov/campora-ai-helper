import subprocess
import sys
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class BotReloader(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_bot()

    def start_bot(self):
        """Start the bot process."""
        if self.process:
            self.stop_bot()

        print("🚀 Starting bot...")
        self.process = subprocess.Popen([sys.executable, "main.py"])

    def stop_bot(self):
        """Stop the bot process."""
        if self.process:
            print("🛑 Stopping bot...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

    def on_modified(self, event):
        """Restart bot when Python files change."""
        if event.is_directory:
            return

        if event.src_path.endswith(".py"):
            print(f"📝 File changed: {event.src_path}")
            print("🔄 Restarting bot...")
            self.start_bot()


def main():
    """Main function to start file watching."""
    event_handler = BotReloader()
    observer = Observer()

    # Watch current directory and subdirectories
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()

    print("👁️  Watching for changes... Press Ctrl+C to stop")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping file watcher...")
        event_handler.stop_bot()
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
