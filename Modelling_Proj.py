import random
from time import sleep
import tkinter as tk
from tkinter import ttk, messagebox
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class TrafficSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Traffic Flow Simulator")

        # Window setup
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        taskbar_height = 50
        window_height = screen_height - taskbar_height

        self.root.geometry(f"{screen_width}x{window_height}+0+0")
        self.root.state('zoomed')
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.minsize(800, 600)
        self.root.configure(bg='#f0f0f0')

        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill='both', expand=True, padx=40, pady=30)

        # Traffic solution options
        self.traffic_options = {
            "Traffic Lights": {
                "id": "traffic_lights",
                "efficiency": 0.8,
                "cost": 2500000,
                "description": "Traditional traffic lights with timer system and backup power",
                "wait_time": 45,
                "maintenance_cost": 100000
            },
            "Redesigned Lanes": {
                "id": "redesigned_lanes",
                "efficiency": 1.2,
                "cost": 7500000,
                "description": "Optimized lane layout with dedicated turn lanes and improved signage",
                "wait_time": 30,
                "maintenance_cost": 200000
            },
            "Roundabout": {
                "id": "roundabout",
                "efficiency": 1.0,
                "cost": 10000000,
                "description": "Modern roundabout with yield signs and proper lighting",
                "wait_time": 20,
                "maintenance_cost": 300000
            },
            "U-Turn Slot System": {
                "id": "u_turn",
                "efficiency": 0.9,
                "cost": 5000000,
                "description": "Strategic U-turn slots to reduce intersection crossing",
                "wait_time": 25,
                "maintenance_cost": 150000
            },
            "Overpass Bridge": {
                "id": "overpass",
                "efficiency": 1.6,
                "cost": 25000000,
                "description": "Elevated road structure with pedestrian walkway",
                "wait_time": 10,
                "maintenance_cost": 800000
            },
            "Road Widening": {
                "id": "widening",
                "efficiency": 1.3,
                "cost": 20000000,
                "description": "Expanded road capacity with additional lanes and sidewalks",
                "wait_time": 15,
                "maintenance_cost": 400000
            }
        }

        self.setup_gui()

    def setup_gui(self):
        # Create notebook for tabs
        style = ttk.Style()
        style.configure('TNotebook', padding=(20, 10))
        style.configure('TNotebook.Tab', padding=(10, 5))

        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill='both', expand=True)

        # Main tabs setup
        sim_frame = ttk.Frame(self.notebook, padding="30")
        results_container = ttk.Frame(self.notebook, padding="30")
        viz_frame = ttk.Frame(self.notebook, padding="30")

        self.notebook.add(sim_frame, text="Simulation")
        self.notebook.add(results_container, text="Results")
        self.notebook.add(viz_frame, text="Visualization")

        self.setup_simulation_display(viz_frame)

        # Setup results tab with scrollbar
        results_canvas = tk.Canvas(results_container)
        scrollbar = ttk.Scrollbar(results_container, orient="vertical",
                                  command=results_canvas.yview)
        self.results_frame = ttk.Frame(results_canvas, padding="20")

        self.results_frame.bind(
            "<Configure>",
            lambda e: results_canvas.configure(scrollregion=results_canvas.bbox("all"))
        )

        results_canvas.create_window((0, 0), window=self.results_frame, anchor="nw")
        results_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y", padx=(5, 0))
        results_canvas.pack(side="left", fill="both", expand=True)

        self.setup_simulation_controls(sim_frame)

    def setup_simulation_controls(self, frame):
        # Create container
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Register validation command
        validate_cmd = self.root.register(self.validate_number_input)

        # Title
        title_label = ttk.Label(content_frame, text="Traffic Flow Simulator",
                                font=('Helvetica', 16, 'bold'))
        title_label.pack(pady=(0, 15))

        # Traffic solution selection
        solution_frame = ttk.Frame(content_frame)
        solution_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(solution_frame, text="Select Traffic Solution:",
                  font=('Helvetica', 10, 'bold')).pack(anchor='w')
        self.solution_var = tk.StringVar()
        solution_combo = ttk.Combobox(solution_frame, textvariable=self.solution_var,
                                      values=list(self.traffic_options.keys()),
                                      state='readonly', width=35)
        solution_combo.pack(fill='x', pady=(2, 0))
        solution_combo.set("Select an option")
        solution_combo.bind('<<ComboboxSelected>>', self.update_solution_info)

        # Solution information display
        self.info_text = tk.Text(content_frame, height=4, width=45, wrap=tk.WORD)
        self.info_text.pack(pady=(2, 10), fill='x')
        self.info_text.config(state=tk.DISABLED)

        # Traffic parameters
        params_frame = ttk.LabelFrame(content_frame, text="Traffic Parameters",
                                      padding="10")
        params_frame.pack(fill='x', pady=(0, 10))

        # Vehicles per minute input
        vehicles_frame = ttk.Frame(params_frame)
        vehicles_frame.pack(fill='x', pady=2)
        ttk.Label(vehicles_frame, text="Vehicles per minute:").pack(side='left')
        self.vehicles_var = tk.StringVar()
        vehicles_entry = ttk.Entry(vehicles_frame, textvariable=self.vehicles_var,
                                   validate='key',
                                   validatecommand=(validate_cmd, '%P'),
                                   width=12)
        vehicles_entry.pack(side='right')

        # Simulation time input
        time_frame = ttk.Frame(params_frame)
        time_frame.pack(fill='x', pady=2)
        ttk.Label(time_frame, text="Simulation time (minutes):").pack(side='left')
        self.time_var = tk.StringVar()
        time_entry = ttk.Entry(time_frame, textvariable=self.time_var,
                               validate='key',
                               validatecommand=(validate_cmd, '%P'),
                               width=12)
        time_entry.pack(side='right')

        # Peak hour toggle
        self.peak_hour_var = tk.BooleanVar()
        peak_hour_check = ttk.Checkbutton(params_frame,
                                          text="Peak Hour Traffic",
                                          variable=self.peak_hour_var)
        peak_hour_check.pack(pady=5)

        # Progress bar
        progress_frame = ttk.Frame(content_frame)
        progress_frame.pack(fill='x', pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame,
                                            variable=self.progress_var,
                                            maximum=100)
        self.progress_bar.pack(fill='x', pady=2)

        # Results display
        self.result_var = tk.StringVar()
        result_label = ttk.Label(content_frame,
                                 textvariable=self.result_var,
                                 wraplength=400)
        result_label.pack(pady=5)

        # Simulation button
        self.simulate_btn = ttk.Button(content_frame,
                                       text="Start Simulation",
                                       command=self.start_simulation)

        # Bind validation to fields
        self.vehicles_var.trace_add('write', self.validate_all_fields)
        self.time_var.trace_add('write', self.validate_all_fields)
        self.solution_var.trace_add('write', self.validate_all_fields)

    def validate_number_input(self, P):
        return P == "" or P.isdigit()

    def update_solution_info(self, event=None):
        selected = self.solution_var.get()
        if selected in self.traffic_options:
            info = self.traffic_options[selected]
            info_text = (
                f"Description: {info['description']}\n"
                f"Implementation Cost: ₱{info['cost']:,.2f}\n"
                f"Annual Maintenance: ₱{info['maintenance_cost']:,.2f}\n"
                f"Average Wait Time: {info['wait_time']} seconds\n"
                f"Efficiency Rating: {info['efficiency'] * 100}%"
            )
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, info_text)
            self.info_text.config(state=tk.DISABLED)

    def setup_simulation_display(self, frame):
        """Setup a simple visual representation of traffic flow"""
        display_frame = ttk.LabelFrame(frame, text="Traffic Flow Visualization", padding="10")
        display_frame.pack(fill='x', pady=(0, 10))

        # Create canvas for simple visualization
        self.sim_canvas = tk.Canvas(display_frame, height=150, bg='white')
        self.sim_canvas.pack(fill='x', pady=5)

        # Status display
        self.status_frame = ttk.Frame(display_frame)
        self.status_frame.pack(fill='x')

        # Current statistics
        stats_frame = ttk.Frame(self.status_frame)
        stats_frame.pack(side='left', padx=10)

        self.current_flow = tk.StringVar(value="Vehicles/min: 0")
        self.current_wait = tk.StringVar(value="Current wait: 0s")
        self.current_time = tk.StringVar(value="Time: 00:00")

        ttk.Label(stats_frame, textvariable=self.current_flow).pack(anchor='w')
        ttk.Label(stats_frame, textvariable=self.current_wait).pack(anchor='w')
        ttk.Label(stats_frame, textvariable=self.current_time).pack(anchor='w')

    def update_simulation_display(self, minute, vehicles, wait_time):
        """Update the simple visualization"""
        self.sim_canvas.delete('all')

        # Draw road
        self.sim_canvas.create_rectangle(50, 60, 550, 90, fill='#404040')

        # Draw traffic indicators
        flow_rate = min(1.0, vehicles / 100)  # Normalize flow rate
        num_indicators = int(flow_rate * 10)  # Show up to 10 indicators

        for i in range(num_indicators):
            x = 80 + i * 50
            self.sim_canvas.create_oval(x, 65, x + 20, 85, fill='yellow')

        # Update status text
        self.current_flow.set(f"Vehicles/min: {vehicles:.1f}")
        self.current_wait.set(f"Current wait: {wait_time:.1f}s")
        hours = minute // 60
        mins = minute % 60
        self.current_time.set(f"Time: {hours:02d}:{mins:02d}")

        # Draw congestion level indicator
        congestion = min(1.0, wait_time / 60)  # Normalize wait time
        color = f'#{int(255 * congestion):02x}{int(255 * (1 - congestion)):02x}00'
        self.sim_canvas.create_rectangle(50, 100, 550, 120, fill=color)
        self.sim_canvas.create_text(300, 140,
                                    text=f"Congestion Level: {int(congestion * 100)}%",
                                    font=('Helvetica', 10))

    def simulate_traffic(self, option, vehicles_per_minute, simulation_time):
        total_vehicles = 0
        wait_times = []
        solution_info = self.traffic_options[option]

        base_efficiency = solution_info["efficiency"]

        for minute in range(simulation_time):
            progress = (minute + 1) / simulation_time * 100
            self.progress_var.set(progress)

            current_efficiency = base_efficiency
            if self.peak_hour_var.get():
                if 15 <= minute % 60 <= 45:
                    current_efficiency *= 0.7

            passed_vehicles = vehicles_per_minute * current_efficiency
            weather_factor = random.uniform(0.8, 1.2)
            passed_vehicles *= weather_factor

            base_wait_time = solution_info["wait_time"]
            current_wait = base_wait_time * (vehicles_per_minute / passed_vehicles)
            wait_times.append(current_wait)

            total_vehicles += max(0, passed_vehicles)

            # Update the visualization
            self.update_simulation_display(minute, passed_vehicles, current_wait)
            self.root.update()
            sleep(0.1)  # Short delay to show progress

        return int(total_vehicles), wait_times

    def create_explanation_frame(self, parent, title, explanation):
        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=5)

        button_frame = ttk.Frame(frame, style='Explanation.TFrame')
        button_frame.pack(fill='x')

        is_expanded = tk.BooleanVar(value=False)

        text = tk.Text(frame, height=4, wrap=tk.WORD, font=('Helvetica', 9))
        text.insert('1.0', explanation)
        text.config(state='disabled')

        def toggle_explanation():
            if is_expanded.get():
                text.pack_forget()
                btn.configure(text=f"{title} (Click to See Explanation) ▼")
            else:
                text.pack(fill='x', pady=(5, 0))
                btn.configure(text=f"{title} (Click to Hide Explanation) ▲")
            is_expanded.set(not is_expanded.get())

        btn = ttk.Button(button_frame,
                         text=f"{title} (Click to See Explanation) ▼",
                         command=toggle_explanation,
                         style='Explanation.TButton')
        btn.pack(fill='x')

        return frame

    def plot_results(self, wait_times):
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Create main frame for results
        main_results_frame = ttk.Frame(self.results_frame)
        main_results_frame.pack(fill='both', expand=True)

        # Create figure
        fig = plt.figure(figsize=(12, 8))
        plt.subplots_adjust(hspace=0.5)

        # Plot 1: Wait Times
        ax1 = fig.add_subplot(311)
        ax1.plot(wait_times, linewidth=2, color='#2196F3')
        ax1.set_title('Wait Times During Simulation', pad=15, fontsize=12, fontweight='bold')
        ax1.set_xlabel('Simulation Minute')
        ax1.set_ylabel('Wait Time (seconds)')
        ax1.grid(True, linestyle='--', alpha=0.7)

        wait_times_explanation = (
            "This graph shows how wait times change during the simulation. "
            "Lower wait times indicate better traffic flow. Spikes in the graph "
            "may indicate congestion periods. The average wait time helps evaluate "
            "the overall effectiveness of the chosen solution."
        )

        # Plot 2: Efficiency
        ax2 = fig.add_subplot(312)
        solutions = list(self.traffic_options.keys())
        efficiencies = [self.traffic_options[s]["efficiency"] * 100 for s in solutions]
        bars = ax2.bar(solutions, efficiencies, color='#4CAF50')
        ax2.set_title('Efficiency Comparison', pad=15, fontsize=12, fontweight='bold')
        ax2.set_xlabel('Solutions')
        ax2.set_ylabel('Efficiency (%)')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        ax2.grid(True, linestyle='--', alpha=0.7, axis='y')

        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{int(height)}%',
                     ha='center', va='bottom')

        efficiency_explanation = (
            "The efficiency comparison shows how well each solution handles traffic flow. "
            "Higher percentages indicate better traffic management. Solutions above 100% "
            "represent improvements over the baseline traffic flow."
        )

        # Plot 3: Cost
        ax3 = fig.add_subplot(313)
        costs = [self.traffic_options[s]["cost"] / 1000000 for s in solutions]
        bars = ax3.bar(solutions, costs, color='#FF5722')
        ax3.set_title('Implementation Cost Comparison', pad=15, fontsize=12, fontweight='bold')
        ax3.set_xlabel('Solutions')
        ax3.set_ylabel('Cost (Million ₱)')
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
        ax3.grid(True, linestyle='--', alpha=0.7, axis='y')

        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width() / 2., height,
                     f'₱{height:.1f}M',
                     ha='center', va='bottom')

        cost_explanation = (
            "This graph compares the implementation costs of different solutions. "
            "Costs are shown in millions of Philippine Pesos (₱). Consider this alongside "
            "efficiency and wait times to determine the most cost-effective solution."
        )

        plt.tight_layout()

        canvas_widget = FigureCanvasTkAgg(fig, master=main_results_frame)
        canvas_widget.draw()
        canvas_widget.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=10)

        # Add explanations
        explanations_frame = ttk.Frame(main_results_frame)
        explanations_frame.pack(fill='x', padx=20, pady=10)

        style = ttk.Style()
        style.configure('Explanation.TButton', font=('Helvetica', 10, 'bold'), padding=10)
        style.configure('Explanation.TFrame', relief='solid', borderwidth=1)

        self.create_explanation_frame(explanations_frame, "Wait Times Analysis", wait_times_explanation)
        self.create_explanation_frame(explanations_frame, "Efficiency Analysis", efficiency_explanation)
        self.create_explanation_frame(explanations_frame, "Cost Analysis", cost_explanation)

    def start_simulation(self):
        try:
            if self.solution_var.get() == "Select an option":
                messagebox.showerror("Error", "Please select a traffic solution!")
                return

            vehicles = int(self.vehicles_var.get())
            sim_time = int(self.time_var.get())

            if vehicles <= 0 or sim_time <= 0:
                messagebox.showerror("Error", "Please enter positive numbers!")
                return

            self.result_var.set("")
            for widget in self.results_frame.winfo_children():
                widget.destroy()

            self.progress_var.set(0)
            self.result_var.set("Simulation in progress...")
            self.root.update()

            # Switch to results tab first
            self.notebook.select(1)

            total, wait_times = self.simulate_traffic(self.solution_var.get(), vehicles, sim_time)

            # Display results
            avg_wait = sum(wait_times) / len(wait_times)
            solution_info = self.traffic_options[self.solution_var.get()]
            yearly_cost = solution_info['maintenance_cost']

            self.result_var.set(
                f"SIMULATION RESULTS\n" +
                f"==================\n" +
                f"Solution: {self.solution_var.get()}\n" +
                f"Total vehicles processed: {total:,}\n" +
                f"Average wait time: {avg_wait:.1f} seconds\n\n" +
                f"COST ANALYSIS\n" +
                f"==================\n" +
                f"Implementation cost: ₱{solution_info['cost']:,.2f}\n" +
                f"Yearly maintenance: ₱{yearly_cost:,.2f}\n" +
                f"5-year total cost: ₱{(solution_info['cost'] + yearly_cost * 5):,.2f}"
            )

            self.plot_results(wait_times)

            # Switch to visualization tab after results are shown
            self.notebook.select(2)

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for vehicles and time!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def validate_all_fields(self, *args):
        vehicles = self.vehicles_var.get().strip()
        sim_time = self.time_var.get().strip()
        solution = self.solution_var.get()

        if (vehicles and sim_time and
                solution != "Select an option" and
                vehicles.isdigit() and sim_time.isdigit() and
                int(vehicles) > 0 and int(sim_time) > 0):
            self.simulate_btn.pack(pady=5)
        else:
            self.simulate_btn.pack_forget()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            self.root.destroy()

def main():
    root = tk.Tk()
    app = TrafficSimulator(root)
    root.mainloop()

if __name__ == "__main__":
    main()