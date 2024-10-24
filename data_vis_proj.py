import tkinter as tk
from tkinter import messagebox, filedialog
import mysql.connector
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

global db_name
global db_pass
#database name and pass
db_name = "dashboard_db"
db_pass = "14Phoenix$"

# MySQL connection for login and registration
def authenticate(username, password):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=db_pass,
            database=db_name
        )
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        connection.close()
        return user is not None
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return False

def register_user(username, password):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=db_pass,
            database=db_name
        )
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        connection.commit()
        connection.close()
        messagebox.showinfo("Success", "User registered successfully!")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

# Main Application
class DashboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Interactive Data Visualization Dashboard")
        self.geometry("600x400")

        self.init_login_screen()

    def init_login_screen(self):
        self.login_frame = tk.Frame(self)
        self.login_frame.pack(pady=50)

        tk.Label(self.login_frame, text="Username:").grid(row=0, column=0)
        tk.Label(self.login_frame, text="Password:").grid(row=1, column=0)

        self.username_entry = tk.Entry(self.login_frame)
        self.password_entry = tk.Entry(self.login_frame, show="*")

        self.username_entry.grid(row=0, column=1)
        self.password_entry.grid(row=1, column=1)

        tk.Button(self.login_frame, text="Login", command=self.login).grid(row=2, column=1, pady=10)
        tk.Button(self.login_frame, text="Register", command=self.register_user_prompt).grid(row=3, column=1, pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if authenticate(username, password):
            messagebox.showinfo("Login", "Login successful!")
            self.login_frame.destroy()
            self.init_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def register_user_prompt(self):
        reg_window = tk.Toplevel(self)
        reg_window.title("Register New User")
        reg_window.geometry("300x200")

        tk.Label(reg_window, text="Enter Username:").pack(pady=10)
        username_entry = tk.Entry(reg_window)
        username_entry.pack()

        tk.Label(reg_window, text="Enter Password:").pack(pady=10)
        password_entry = tk.Entry(reg_window, show="*")
        password_entry.pack()

        def register():
            username = username_entry.get()
            password = password_entry.get()
            register_user(username, password)
            reg_window.destroy()

        tk.Button(reg_window, text="Register", command=register).pack(pady=20)

    def init_dashboard(self):
        self.dashboard_frame = tk.Frame(self)
        self.dashboard_frame.pack(pady=20)

        tk.Button(self.dashboard_frame, text="Load Dataset", command=self.load_dataset).pack(pady=10)
        tk.Button(self.dashboard_frame, text="Exit", command=self.destroy).pack(pady=10)

    def load_dataset(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.df = pd.read_csv(file_path)
            self.dashboard_frame.pack_forget()
            self.show_column_selection()

    def show_column_selection(self):
        self.column_selection_frame = tk.Frame(self)
        self.column_selection_frame.pack(pady=10, expand=True, fill='both')

        selection_container = tk.Frame(self.column_selection_frame)
        selection_container.pack(expand=True)

        tk.Label(selection_container, text="Select Columns for Plotting:").pack()

        self.select_all_var = tk.IntVar(value=0)
        select_all_chk = tk.Checkbutton(selection_container, text="Select All", variable=self.select_all_var, command=self.select_all_columns)
        select_all_chk.pack(anchor=tk.W)

        self.column_vars = {}
        for col in self.df.columns:
            var = tk.IntVar()
            chk = tk.Checkbutton(selection_container, text=col, variable=var)
            chk.pack(anchor=tk.W)
            self.column_vars[col] = var

        tk.Button(selection_container, text="Next", command=self.show_plot_type_selection).pack(pady=10)

    def select_all_columns(self):
        
        select_all = self.select_all_var.get() == 1
        for var in self.column_vars.values():
            var.set(1 if select_all else 0)

    def show_plot_type_selection(self):
        
        self.selected_columns = [col for col, var in self.column_vars.items() if var.get() == 1]

        if not self.selected_columns:
            messagebox.showerror("Error", "Please select at least one column.")
            return

        self.column_selection_frame.pack_forget()

        self.plot_type_frame = tk.Frame(self)
        self.plot_type_frame.pack(pady=10, fill="both", expand=True)

        tk.Label(self.plot_type_frame, text="Choose Plot Type:").pack(pady=10)

        plot_types = ["Bar Plot", "Violin Plot", "Scatter Plot", "Line Plot", "Histogram", "Box Plot"]
        self.plot_type_var = tk.StringVar(value="Bar Plot")

        radio_frame = tk.Frame(self.plot_type_frame)
        radio_frame.pack(pady=10)

        for plot in plot_types:
            tk.Radiobutton(radio_frame, text=plot, variable=self.plot_type_var, value=plot).pack(anchor=tk.W)

        tk.Button(self.plot_type_frame, text="Generate Plot", command=self.generate_plot).pack(pady=10)

    def generate_plot(self):
        plot_type = self.plot_type_var.get()
        data_to_plot = self.df[self.selected_columns]

        if plot_type == "Bar Plot":
            plt.figure(figsize=(10, 6))
            sns.barplot(data=data_to_plot)
            plt.show()

        elif plot_type == "Violin Plot":
            plt.figure(figsize=(10, 6))
            sns.violinplot(data=data_to_plot)
            plt.show()

        elif plot_type == "Scatter Plot":
            plt.figure(figsize=(10, 6))
            sns.scatterplot(data=data_to_plot)
            plt.show()

        elif plot_type == "Line Plot":
            plt.figure(figsize=(10, 6))
            sns.lineplot(data=data_to_plot)
            plt.show()

        elif plot_type == "Histogram":
            plt.figure(figsize=(10, 6))
            data_to_plot.hist(bins=15)
            plt.show()

        elif plot_type == "Box Plot":
            plt.figure(figsize=(10, 6))
            sns.boxplot(data=data_to_plot)
            plt.show()
#main method
if __name__ == "__main__":
    app = DashboardApp()
    app.mainloop()
