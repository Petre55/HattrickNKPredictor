"""Main application module for Hattrick prediction game management."""
import os
import smtplib
import pathlib
import tkinter as tk
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from tkinter import messagebox
import tkinter.font as tkFont
from tkinter.ttk import Checkbutton

from selenium.common import TimeoutException

from HattrickNKPredictor.forum.auth_manager import AuthManager
from HattrickNKPredictor.forum.csv_handler import handler
from HattrickNKPredictor.forum.forum_manager import (ForumFetcher,
                                                     ForumDateAnalyzer)
from HattrickNKPredictor.calculators.calculator import PredictionGame
from HattrickNKPredictor.calculators.exporters import (export_results_to_txt,
                                                       NKScoreAggregator)


class HattrickLoginApp:
    """Main application class for Hattrick prediction game management."""

    def __init__(self, root):
        """Initialize the application with root window."""
        self.session = None
        self.date_keys = None
        self.date_ranges = None
        self.root = root
        self.root.geometry("400x400")
        self.root.title("Hattrick Login")
        self.username = None
        self.password = None
        self.hattrick_scraper = None
        self.nk_var = None
        self.check = None
        self.round_label = None
        self.round = None
        self.recipient_label = None
        self.recipient = None
        self.subject_label = None
        self.subject = None
        self.file_options = None
        self.checkbox_vars = None
        self.first_msg_label = None
        self.first_msg = None
        self.last_msg_label = None
        self.last_msg = None
        self._setup_login_ui()

    def _setup_login_ui(self):
        """Set up the initial login UI components."""
        large_font = tkFont.Font(family="Arial", size=14, weight="bold")
        self.username_label = tk.Label(self.root, text="Username:",
                                       font=large_font)
        self.username_label.pack(pady=5)
        self.username_entry = tk.Entry(self.root, width=20, font=large_font,
                                       justify='center')
        self.username_entry.pack(pady=5)

        self.password_label = tk.Label(self.root, text="Password:",
                                       font=large_font)
        self.password_label.pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*", width=20,
                                       font=large_font, justify='center')
        self.password_entry.pack(pady=5)

        self.login_button = tk.Button(
            self.root,
            text="Login",
            command=self.validate_login,
            font=large_font
        )
        self.login_button.pack()

        tk.Button(
            self.root,
            text="Sending e-mail",
            width=20,
            height=2,
            command=self.email_menu,
            font=large_font
        ).pack(pady=10)

    def validate_login(self):
        """Validate user credentials and initiate login."""
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()

        if not self.username or not self.password:
            messagebox.showerror("Error",
                                 "Username and password are required!")
            return

        try:
            self.hattrick_scraper = AuthManager(
                self.username,
                self.password,
                "https://www.hattrick.org/hu/"
                "?ReturnUrl=%2fMyHattrick%2fDashboard.aspx"
            )
            self.hattrick_scraper.login()
            self.hattrick_scraper.driver.quit()

            self.show_main_menu()
        except (ConnectionError, TimeoutError) as e:
            messagebox.showerror("Login Failed", f"Network error: {str(e)}")

    def show_main_menu(self):
        """Display the main menu after successful login."""
        for widget in self.root.winfo_children():
            widget.destroy()
        large_font = tkFont.Font(family="Arial", size=14, weight="bold")
        self.root.title("Main menu")

        tk.Button(
            self.root,
            text="Sending e-mail",
            width=20,
            height=2,
            command=self.email_menu,
            font=large_font
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Prediction calculator",
            width=20,
            height=2,
            command=self.do_results,
            font=large_font
        ).pack(pady=10)

    def do_results(self):
        """Az összes forduló kiértékelése egyszerre"""
        fetcher = ForumDateAnalyzer(
            self.username,
            self.password,
            "https://www83.hattrick.org/Forum/Read.aspx?t=17632450&",
        )
        self.date_ranges = fetcher.get_date_ranges()
        if not hasattr(self, 'date_ranges') or not self.date_ranges:
            messagebox.showerror("Hiba", "Először töltsd le a fordulókat!")
            return
        base_dir = pathlib.Path(__file__).parent.resolve()
        eredmenyek_dir = base_dir / "eredmenyek"
        eredmenyek_dir.mkdir(exist_ok=True)
        fetcher = ForumFetcher(
            self.username,
            self.password,
            "https://www.hattrick.org/hu/Forum/Read.aspx?",
            0,
            0
        )
        fetcher.login.login_forum()
        fetcher.session=fetcher.login.convert_cookies_to_requests()
        for index, (first_post, last_post) in enumerate(self.date_ranges):
            try:
                fetcher.kezdo=first_post
                fetcher.utolso=last_post
                data = fetcher.fetch_forum_data()

                csv_filename = f"fordulo_{index + 1}.csv"
                fetcher.save_to_csv(data, csv_filename)

                # Eredmények számolása
                game = PredictionGame(handler.csv_reader(csv_filename))
                game.calculate_all_scores()

                # Eredmények exportálása
                export_results_to_txt(
                    game.participants,
                    f"NK - {index + 1}. Forduló eredmény",
                    game.correct_results,
                    game.correct_replay,
                    game.correct_bonus,
                    game.countrys,
                    f"{eredmenyek_dir}\\fordulo{index + 1}.txt"
                )

                os.remove(csv_filename)
            except TimeoutException as e:
                print(f"Hiba a {index + 1}. forduló feldolgozásakor: {str(e)}")
                continue
        fetcher.login.driver.quit()
        aggregator = NKScoreAggregator()
        aggregator.add_folder(f"{eredmenyek_dir}")
        aggregator.save_result()

        messagebox.showinfo("Kész",
                            "Minden forduló kiértékelése befejeződött!")

    def email_menu(self):
        """Display the email sending interface."""
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.title("Sending e-mail")
        self.recipient_label = tk.Label(self.root, text="Recipient e-mail:")
        self.recipient_label.pack()
        self.recipient = tk.Entry(self.root, width=30)
        self.recipient.pack()

        self.subject_label = tk.Label(self.root, text="Subject:")
        self.subject_label.pack()
        self.subject = tk.Entry(self.root, width=30)
        self.subject.pack()

        self.checkbox_vars = {}
        for abs_path in self.get_file_paths():
            filename = os.path.basename(abs_path)

            var = tk.BooleanVar()
            chk = Checkbutton(self.root, text=filename, variable=var)
            chk.pack(anchor='w')
            self.checkbox_vars[abs_path] = var

        tk.Button(
            self.root,
            text="Email küldése",
            command=self.send_gmail_with_attachments
        ).pack(pady=10)
        tk.Button(
            self.root,
            text="Login screen",
            command=self._setup_login_ui
        ).pack(pady=10)

    def send_gmail_with_attachments(self):
        """Send email with selected attachments via Gmail."""
        recipient = self.recipient.get()
        if not recipient:
            messagebox.showinfo("No recipient", "Please enter a recipient.")
            return

        subject = self.subject.get()
        attachment_paths = self.get_selected_files()

        if not attachment_paths:
            return

        password = "psou dasi wylv nanp"
        sender = "kukanakvan@gmail.com"

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject

        for file_path in attachment_paths:
            try:
                filename = os.path.basename(file_path)

                with open(file_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())

                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename}",
                )
                msg.attach(part)
            except (IOError, OSError) as e:
                messagebox.showerror("Error", f"Failed to attach file: {e}")
                return

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender, password)
                server.sendmail(sender, recipient, msg.as_string())
            self.root.destroy()
        except smtplib.SMTPException as e:
            messagebox.showerror("Error", f"Failed to send email: {e}")

    def get_file_paths(self):
        """Get list of available result files.

        Returns:
            list: Paths to available result files
        """
        files = []

        base_dir = pathlib.Path(__file__).parent.resolve()
        eredmenyek_dir = base_dir / "eredmenyek"
        for f in os.listdir(eredmenyek_dir):
            full_path = os.path.join(eredmenyek_dir, f)
            if os.path.isfile(full_path):
                files.append(full_path)

        if os.path.isfile("score.txt"):
            files.append("score.txt")

        return files

    def get_selected_files(self):
        """Get list of selected files from checkboxes."""
        selected_files = []
        for path, var in self.checkbox_vars.items():
            if var.get():
                selected_files.append(path)
        return selected_files


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    HattrickLoginApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
