import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
import matplotlib.pyplot as plt


selectionbar_color = '#D3D3D3'  # Light Gray
sidebar_color = '#ADD8E6'       # Light Blue
header_color = '#2C3E50'        # Dark Blue-Gray
visualisation_frame_color = "#FFFFFF"  # White



db_file = "bmi_history.db"

def initialize_database():
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bmi_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            height REAL NOT NULL,
            weight REAL NOT NULL,
            bmi REAL NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    connection.commit()
    connection.close()


class TkinterApp(tk.Tk):
    def __init__(self):
        initialize_database()
        tk.Tk.__init__(self)
        self.title("BMI Calculator App")


        self.geometry("1200x700")
        self.resizable(0, 0)
        self.title('BMI Calculator')
        self.config(background=selectionbar_color)
        icon = tk.PhotoImage(file='images\\LU_logo.png')
        self.iconphoto(True, icon)


        self.header = tk.Frame(self, bg=header_color)
        self.header.place(relx=0.15, rely=0, relwidth=0.85, relheight=0.1)

        self.sidebar = tk.Frame(self, bg=sidebar_color)
        self.sidebar.place(relx=0, rely=0, relwidth=0.15, relheight=1)

        self.brand_frame = tk.Frame(self.sidebar, bg=sidebar_color)
        self.brand_frame.place(relx=0, rely=0, relwidth=1, relheight=0.15)
        self.uni_logo = icon.subsample(9)
        logo = tk.Label(self.brand_frame, image=self.uni_logo, bg=sidebar_color)
        logo.place(x=5, y=20)

        uni_name = tk.Label(self.brand_frame, text='BMI', bg=sidebar_color, font=("", 15, "bold"))
        uni_name.place(x=55, y=27, anchor="w")

        uni_name = tk.Label(self.brand_frame, text='Calculator', bg=sidebar_color, font=("", 15, "bold"))
        uni_name.place(x=55, y=60, anchor="w")


        self.submenu_frame = tk.Frame(self.sidebar, bg=sidebar_color)
        self.submenu_frame.place(relx=0, rely=0.2, relwidth=1, relheight=0.85)
        att_submenu = SidebarSubMenu(self.submenu_frame, sub_menu_heading='Menu', sub_menu_options=["BMI Calculator", "History", "Trend Analysis"])
        att_submenu.options["BMI Calculator"].config(command=lambda: self.show_frame(Frame1))
        att_submenu.options["History"].config(command=lambda: self.show_frame(Frame2))
        att_submenu.options["Trend Analysis"].config(command=lambda: self.show_frame(Frame3))
        att_submenu.place(relx=0, rely=0.025, relwidth=1, relheight=0.3)


        container = tk.Frame(self, bg="grey")
        container.config(highlightbackground="#808080", highlightthickness=0.7)
        container.place(relx=0.15, rely=0.1, relwidth=0.85, relheight=0.9)

        self.frames = {}

        for F in (Frame1, Frame2, Frame3):
            frame = F(container, self)
            self.frames[F] = frame
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.show_frame(Frame1)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()



class Frame1(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text='BMI Calculator', font=("Arial", 15))
        label.pack(pady=10)

        container = tk.Frame(self)
        container.config(highlightbackground="#100000", highlightthickness=0.5)
        container.place(relx=0.3, rely=0.1, relwidth=0.4, relheight=0.7)

        def validate_number_input(value):
            return value == "" or value.replace('.', '', 1).isdigit()

        def calculate_bmi():
            initialize_database()
            try:
                name = name_entry.get().strip()
                height = float(height_entry.get())
                weight = float(weight_entry.get())

                if not name:
                    raise ValueError("Name cannot be empty.")
                if height <= 0 or weight <= 0:
                    raise ValueError("Height and weight must be positive values.")

                height = height / 100.0
                bmi = weight / (height ** 2)
                bmi = round(bmi, 2)

                category = 'severely underweight :(' if bmi <= 16 else 'underweight :(' if bmi <= 18.5 else 'healthy :)' if bmi <= 25 else 'overweight :(' if bmi <= 30 else 'suffering from obesity.'

                result_label.config(text=f'Your BMI is: {bmi}\nYou are {category}')

                connection = sqlite3.connect(db_file)
                cursor = connection.cursor()
                cursor.execute("INSERT INTO bmi_records (name, height, weight, bmi, date) VALUES (?, ?, ?, ?, ?)",
                               (name, height * 100, weight, bmi, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                connection.commit()
                connection.close()

            except ValueError as e:
                messagebox.showerror("Invalid input", f"Error: {e}")

        validate_cmd = self.register(validate_number_input)

        tk.Label(container, text="Enter your name:", font=("Helvetica", 14)).pack(pady=10)
        name_entry = tk.Entry(container,font=("Helvetica", 14))
        name_entry.pack(pady=5)

        tk.Label(container, text="Enter your height (in cm):",font=("Helvetica", 14)).pack(pady=10)
        height_entry = tk.Entry(container, validate="key", validatecommand=(validate_cmd, '%P'),font=("Helvetica", 14))
        height_entry.pack(pady=5)

        tk.Label(container, text="Enter your weight (in kg):",font=("Helvetica", 14)).pack(pady=10)
        weight_entry = tk.Entry(container, validate="key", validatecommand=(validate_cmd, '%P'),font=("Helvetica", 14))
        weight_entry.pack(pady=5)

        calculate_button = tk.Button(container, text="Calculate BMI",font=("Helvetica", 14), command=calculate_bmi)
        calculate_button.pack(pady=10)

        result_label = tk.Label(container, text="", font=("Helvetica", 16))
        result_label.pack(pady=10)

class Frame2(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text='History', font=("Arial", 15))
        label.pack(pady=10)

        # Treeview for displaying history
        self.tree = ttk.Treeview(self, columns=("Name", "Height", "Weight", "BMI", "Date"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Height", text="Height (cm)")
        self.tree.heading("Weight", text="Weight (kg)")
        self.tree.heading("BMI", text="BMI")
        self.tree.heading("Date", text="Date")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.refresh_button = tk.Button(self, text="Refresh History", command=self.load_data)
        self.refresh_button.pack(pady=10)
        
        self.clear_button = tk.Button(self, text="Clear History", command=self.clear_history)
        self.clear_button.pack(pady=10)

    def clear_history(self):
        try:
            # Connect to the database
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            # Clear all history data
            cursor.execute("DELETE FROM bmi_records;")
            conn.commit()

            conn.close()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", f"Unable to clear data: {e}")

    def load_data(self):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            cursor.execute("SELECT name, height, weight, bmi, date FROM bmi_records")
            rows = cursor.fetchall()

            #print(rows)
            for i in self.tree.get_children():
                self.tree.delete(i)

            for row in rows:
                self.tree.insert("", tk.END, values=row)

            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Unable to load data: {e}")


class Frame3(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text='BMI Trends', font=("Arial", 15))
        label.pack(pady=10)

        trend_frame = tk.Frame(self)
        trend_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.plot_button = tk.Button(self, text="Plot BMI Trends", command=self.plot_trends)
        self.plot_button.pack(pady=10)

    def plot_trends(self):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            cursor.execute("SELECT date, bmi FROM bmi_records ORDER BY date ASC")
            rows = cursor.fetchall()

            conn.close()

            if not rows:
                messagebox.showinfo("No Data", "No BMI records found to plot.")
                return

            dates = [datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') for row in rows]
            bmis = [row[1] for row in rows]

            plt.figure(figsize=(10, 6))
            plt.plot(dates, bmis, marker='o', linestyle='-', color='blue')
            plt.title("BMI Trends Over Time")
            plt.xlabel("Date")
            plt.ylabel("BMI")
            plt.grid(True)
            plt.tight_layout()
            plt.gcf().autofmt_xdate()
            plt.show()

        except Exception as e:
            messagebox.showerror("Error", f"Unable to plot trends: {e}")



class SidebarSubMenu(tk.Frame):
    def __init__(self, parent, sub_menu_heading, sub_menu_options):
        tk.Frame.__init__(self, parent)
        self.config(bg=sidebar_color)
        self.sub_menu_heading_label = tk.Label(self, text=sub_menu_heading, bg=sidebar_color, fg="#333333", font=("Arial", 10))
        self.sub_menu_heading_label.place(x=30, y=10, anchor="w")

        sub_menu_sep = ttk.Separator(self, orient='horizontal')
        sub_menu_sep.place(x=30, y=30, relwidth=0.8, anchor="w")

        self.options = {}
        for n, x in enumerate(sub_menu_options):
            self.options[x] = tk.Button(self, text=x, bg=sidebar_color, font=("Arial", 9, "bold"), bd=0, cursor='hand2', activebackground='#ffffff')
            self.options[x].place(x=30, y=45 * (n + 1), anchor="w")


app = TkinterApp()
app.mainloop()
