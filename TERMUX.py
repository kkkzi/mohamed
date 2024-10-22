import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock
import socket
import time

HOST = "www.google.com"
PORTS = [443]
SLEEP_TIME = 2.0

colors = [
    "[color=#FF0000]",  # Red
    "[color=#00FF00]",  # Green
    "[color=#FFFF00]",  # Yellow
    "[color=#0000FF]",  # Blue
    "[color=#FF00FF]",  # Magenta
    "[color=#00FFFF]",  # Cyan
]

idx = 0
is_running = False

class NetworkApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        # Label for displaying the results
        self.label = Label(text='Press Start to Begin', markup=True)
        self.layout.add_widget(self.label)

        # Button to start the application
        self.start_button = Button(text="Start", on_press=self.start_app)
        self.layout.add_widget(self.start_button)

        # Button to stop the application
        self.stop_button = Button(text="Stop", on_press=self.stop_app)
        self.layout.add_widget(self.stop_button)

        return self.layout

    def start_app(self, instance):
        global is_running
        if not is_running:
            is_running = True
            self.label.text = "Starting..."
            # Schedule the update function to run periodically
            Clock.schedule_interval(self.update_status, SLEEP_TIME)

    def stop_app(self, instance):
        global is_running
        if is_running:
            is_running = False
            self.label.text = "Stopped"
            # Unschedule the update function
            Clock.unschedule(self.update_status)

    def update_status(self, dt):
        global idx
        color = colors[idx % len(colors)]
        idx += 1

        results = []
        for port in PORTS:
            try:
                start_time = time.perf_counter()
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(5)
                    s.connect((HOST, port))
                end_time = time.perf_counter()

                elapsed_time_ms = (end_time - start_time) * 1000
                if elapsed_time_ms < 100:
                    results.append(f"{port} ([color=#00FF00]{elapsed_time_ms:.2f} ms[/color])")
                elif 100 <= elapsed_time_ms < 150:
                    results.append(f"{port} ([color=#FFFF00]{elapsed_time_ms:.2f} ms[/color])")
                else:
                    results.append(f"{port} ([color=#FF0000]{elapsed_time_ms:.2f} ms[/color])")
            except socket.error:
                results.append(f"{port} ([color=#FF0000]error[/color])")

            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(5)
                    s.connect((HOST, port))
                    s.send(b"HEAD / HTTP/1.1\r\nHost: " + HOST.encode() + b"\r\n\r\n" + b"A" * (100 * 1024))
                    data = s.recv(1024)
                if b"Server" in data:
                    results.append("MS ([color=#00FF00]up[/color])")
                else:
                    results.append("MS ([color=#FF0000]down[/color])")
            except socket.error:
                results.append("MS ([color=#FF0000]down[/color])")

        results_str = ", ".join(results)
        self.label.text = f"{color}MF ({results_str})[/color]"

if __name__ == "__main__":
    NetworkApp().run()