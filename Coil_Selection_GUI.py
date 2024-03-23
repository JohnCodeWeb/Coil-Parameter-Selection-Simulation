import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas as pd

class CoilSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Coil Selector")

        # Variables for GUI options
        self.csv_file_name = tk.StringVar()
        self.sort_options = []
        self.num_rows_displayed = tk.IntVar()

        # Set default values
        self.csv_file_name.set('coil_parameters_10mm.csv')
        self.sort_options = ['CSV_CoilInductance']
        self.num_rows_displayed.set(10)

        # Frame for parameter selection
        parameter_frame = ttk.Frame(root, padding="10")
        parameter_frame.grid(row=0, column=0, sticky="nsew")

        # CSV File Selection
        ttk.Label(parameter_frame, text="Select CSV File:").grid(row=0, column=0, sticky="w")
        ttk.Entry(parameter_frame, textvariable=self.csv_file_name).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(parameter_frame, text="Browse", command=self.browse_csv).grid(row=0, column=2, padx=5, pady=5)

        # Sort Options
        ttk.Label(parameter_frame, text="Sort Options:").grid(row=1, column=0, sticky="w")
        sort_options_combobox = ttk.Combobox(parameter_frame, values=self.get_csv_headers(), state="readonly", height=5)
        sort_options_combobox.set(self.sort_options[0])
        sort_options_combobox.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(parameter_frame, text="Add", command=lambda: self.add_sort_option(sort_options_combobox)).grid(row=1, column=2, padx=5, pady=5)

        # Number of Rows Displayed
        ttk.Label(parameter_frame, text="Number of Rows Displayed:").grid(row=2, column=0, sticky="w")
        ttk.Entry(parameter_frame, textvariable=self.num_rows_displayed).grid(row=2, column=1, padx=5, pady=5)

        # Apply Button
        ttk.Button(parameter_frame, text="Apply", command=self.apply_filters).grid(row=3, column=0, columnspan=3, pady=10)

        # Frame for displaying coil table
        table_frame = ttk.Frame(root, padding="10")
        table_frame.grid(row=1, column=0, sticky="nsew")

        # Table
        # Table
        self.coil_table = ttk.Treeview(table_frame)
        self.coil_table["columns"] = tuple(self.get_csv_headers())
        self.coil_table["show"] = "headings"

        # Set column widths (adjust these values as needed)
        column_widths = {
            "CSV_CoilNumber": 80,
            "CSV_OutterDiameter": 100,
            "CSV_TraceWidth": 80,
            "CSV_TraceSpacing": 80,
            "CSV_TurnsPerLayer": 100,
            "CSV_TankCap": 100,
            "CSV_InnerDiameter": 100,
            "CSV_AvgDiameter": 100,
            "CSV_CFR": 80,
            "CSV_CoilInductance": 100,
            "CSV_SensorFreq":100
        }

        for header in self.get_csv_headers():
            self.coil_table.heading(header, text=header, anchor="center")
            self.coil_table.column(header, width=column_widths.get(header, 100), anchor="center")
        self.coil_table.grid(row=0, column=0, sticky="nsew")

        # Scrollbars
        y_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.coil_table.yview)
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        self.coil_table.configure(yscrollcommand=y_scrollbar.set)

        x_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.coil_table.xview)
        x_scrollbar.grid(row=1, column=0, sticky="ew")
        self.coil_table.configure(xscrollcommand=x_scrollbar.set)

        root.grid_rowconfigure(1, weight=1)
        root.columnconfigure(0, weight=1)

    def browse_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.csv_file_name.set(file_path)

    def add_sort_option(self, combobox):
        selected_option = combobox.get()
        if selected_option not in self.sort_options:
            self.sort_options.append(selected_option)
        self.update_sort_options()

    def update_sort_options(self):
        sort_options_str = ", ".join(self.sort_options)
        tk.messagebox.showinfo("Sort Options", f"Current Sort Options: {sort_options_str}")

    def get_csv_headers(self):
        df = pd.read_csv(self.csv_file_name.get())
        return list(df.columns)

    def apply_filters(self):
        df = pd.read_csv(self.csv_file_name.get())
        df = df.sort_values(by=self.sort_options, ascending=False)
        num_rows = self.num_rows_displayed.get()
        df = df.head(num_rows)
        self.update_coil_table(df)

    def update_coil_table(self, dataframe):
        # Clear existing items in the table
        for item in self.coil_table.get_children():
            self.coil_table.delete(item)

        # Insert new data into the table
        for index, row in dataframe.iterrows():
            values = tuple(row)
            self.coil_table.insert("", "end", values=values)



if __name__ == "__main__":
    root = tk.Tk()
    app = CoilSelectorApp(root)
    root.mainloop()
