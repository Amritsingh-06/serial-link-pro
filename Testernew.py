import os
import time
import threading
import datetime
import subprocess
import serial
import serial.tools.list_ports
import openpyxl
import customtkinter as ctk
from tkinter import messagebox


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_asset(filename):
    return os.path.join(BASE_DIR, 'assets', filename)


ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("blue")  

class HardwareTesterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

       
        self.title("Automated Hardware Diagnostic Tool")
        self.geometry("650x450")
        self.resizable(False, False)
        
        
        icon_path = get_asset('icon.ico')
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

       
        self.part_number = ""
        self.revision = ""
        self.serial_number = ""
        
        self.current_state = "idle" 
        self.task_running = False

        self.status_var = ctk.StringVar(value="Status: IDLE")
        self.selected_com_port = ctk.StringVar()
        self.check_all_var = ctk.IntVar()
        self.check_serial_var = ctk.IntVar()

        self.setup_ui()
        self.refresh_com_ports()

        self.protocol("WM_DELETE_WINDOW", self.open_quit_window)

    def setup_ui(self):
        """Builds the modern UI layout using CustomTkinter grids and frames."""
        
    # --- HEADER ---
        self.header_label = ctk.CTkLabel(self, text="SERIAL-LINK PRO", font=ctk.CTkFont(size=24, weight="bold"), text_color="#3b8ed0")
        self.header_label.place(relx=0.05, rely=0.03)
        
        date_str = datetime.datetime.now().strftime("Date: %d-%m-%Y")
        self.date_label = ctk.CTkLabel(self, text=date_str, font=ctk.CTkFont(size=12))
        self.date_label.place(relx=0.75, rely=0.05)

        # --- LEFT PANEL (Test Cases) ---
        self.frame_1 = ctk.CTkFrame(self, width=180, height=280)
        self.frame_1.place(relx=0.05, rely=0.15)
        
        ctk.CTkLabel(self.frame_1, text="Test Cases", font=ctk.CTkFont(weight="bold")).place(relx=0.1, rely=0.05)
        
        self.c1 = ctk.CTkCheckBox(self.frame_1, text="SELECT ALL", variable=self.check_all_var, command=self.toggle_all)
        self.c1.place(relx=0.1, rely=0.2)
        
        self.c2 = ctk.CTkCheckBox(self.frame_1, text="Set Serial", variable=self.check_serial_var)
        self.c2.place(relx=0.1, rely=0.35)

        # --- RIGHT TOP PANEL (PCD INFO) ---
        self.frame_2 = ctk.CTkFrame(self, width=380, height=160)
        self.frame_2.place(relx=0.36, rely=0.15)
        
        ctk.CTkLabel(self.frame_2, text="Scanned Data Info", font=ctk.CTkFont(weight="bold")).place(relx=0.05, rely=0.05)

        ctk.CTkLabel(self.frame_2, text="Serial Number:").place(relx=0.05, rely=0.25)
        self.entry_sno = ctk.CTkEntry(self.frame_2, width=200, state="disabled")
        self.entry_sno.place(relx=0.35, rely=0.25)

        ctk.CTkLabel(self.frame_2, text="Revision:").place(relx=0.05, rely=0.5)
        self.entry_rno = ctk.CTkEntry(self.frame_2, width=200, state="disabled")
        self.entry_rno.place(relx=0.35, rely=0.5)

        ctk.CTkLabel(self.frame_2, text="Part Number:").place(relx=0.05, rely=0.75)
        self.entry_pno = ctk.CTkEntry(self.frame_2, width=200, state="disabled")
        self.entry_pno.place(relx=0.35, rely=0.75)

        # --- RIGHT BOTTOM PANEL (Hardware Settings) ---
        self.frame_3 = ctk.CTkFrame(self, width=380, height=100)
        self.frame_3.place(relx=0.36, rely=0.55)
        
        ctk.CTkLabel(self.frame_3, text="Hardware Settings", font=ctk.CTkFont(weight="bold")).place(relx=0.05, rely=0.1)
        
        ctk.CTkLabel(self.frame_3, text="COM Port:").place(relx=0.05, rely=0.45)
        self.com_combobox = ctk.CTkComboBox(self.frame_3, variable=self.selected_com_port, width=150)
        self.com_combobox.place(relx=0.25, rely=0.45)
        
        self.btn_refresh = ctk.CTkButton(self.frame_3, text="Refresh", width=80, command=self.refresh_com_ports)
        self.btn_refresh.place(relx=0.7, rely=0.45)

        # --- BOTTOM CONTROLS ---
        self.btn_start = ctk.CTkButton(self, text="START SCAN", fg_color="green", hover_color="darkgreen", command=self.toggle_program)
        self.btn_start.place(relx=0.05, rely=0.82)

        self.btn_stop = ctk.CTkButton(self, text="STOP", fg_color="#b22222", hover_color="#8b0000", command=self.open_stop_window)
        self.btn_stop.place(relx=0.3, rely=0.82)

        self.btn_quit = ctk.CTkButton(self, text="QUIT", fg_color="transparent", border_width=1, text_color="gray", command=self.open_quit_window)
        self.btn_quit.place(relx=0.8, rely=0.82)

        # --- STATUS BAR ---
        self.status_bar = ctk.CTkLabel(self, textvariable=self.status_var, fg_color="gray15", corner_radius=5, padx=10)
        self.status_bar.place(relx=0.0, rely=0.93, relwidth=1.0)



    # LOGIC AND METHODS
  
    def refresh_com_ports(self):
        """Scans the computer for available COM ports."""
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        self.com_combobox.configure(values=port_list)
        
        if port_list:
            self.com_combobox.set(port_list[0])
        else:
            self.com_combobox.set("No Ports Found")

    def toggle_all(self):
        """Selects/Deselects all test cases."""
        if self.check_all_var.get() == 1:
            self.check_serial_var.set(1)
        else:
            self.check_serial_var.set(0)

    def toggle_program(self):
        """Handles Start/Pause logic."""
        if self.check_serial_var.get() == 0:
            messagebox.showwarning("Warning", "No test selected. Please select a test case.")
            return

        if self.current_state in ["idle", "finished"]:
            self.open_qr_scan_popup()
        elif self.current_state == "running":
            self.pause_program()
        elif self.current_state == "paused":
            self.resume_program()

    # --- STATE MANAGEMENT ---
    def start_program(self):
        self.current_state = "running"
        self.btn_start.configure(text="PAUSE", fg_color="#cf8e1f", hover_color="#b87a14")
        self.task_running = True

    def pause_program(self):
        self.current_state = "paused"
        self.btn_start.configure(text="RESUME", fg_color="green", hover_color="darkgreen")
        self.status_var.set("Status: Paused")
        self.task_running = False

    def resume_program(self):
        self.current_state = "running"
        self.btn_start.configure(text="PAUSE", fg_color="#cf8e1f")
        self.task_running = True
        self.status_var.set("Status: Running")

    def stop_program(self):
        if self.current_state in ["running", "paused"]:
            self.current_state = "idle"
            self.btn_start.configure(text="START SCAN", fg_color="green")
            self.task_running = False
            self.status_var.set("Status: Stopped")
            self.after(1500, lambda: self.status_var.set("Status: IDLE"))

    # --- POPUP WINDOWS ---
    def open_qr_scan_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Scanner Input")
        popup.geometry("350x200")
        popup.attributes('-topmost', True) # Keep popup on top
        
        ctk.CTkLabel(popup, text="Awaiting Scanner Input...").place(relx=0.25, rely=0.1)
        
        text_box = ctk.CTkEntry(popup, width=250)
        text_box.place(relx=0.15, rely=0.35)
        text_box.focus_set()

        def handle_qr_ok():
            qr_data = text_box.get().strip()
            parts = qr_data.split(";")
            
            if len(parts) == 3:
                self.part_number = parts[0]
                self.revision = parts[1]
                self.serial_number = parts[2]
                
                
                self.update_entry(self.entry_sno, self.serial_number)
                self.update_entry(self.entry_rno, self.revision)
                self.update_entry(self.entry_pno, self.part_number)
                
                popup.destroy()
                self.start_program()
                
               
                self.log_to_excel()
                self.after(500, self.check_svn_updates) 
                self.start_serial_thread()
            else:
                messagebox.showwarning("Invalid Scan", "Format must be: Part;Revision;Serial")

        ctk.CTkButton(popup, text="PROCESS SCAN", command=handle_qr_ok).place(relx=0.3, rely=0.7)

    def update_entry(self, entry_widget, text):
        """Helper to safely update disabled Entry widgets."""
        entry_widget.configure(state="normal")
        entry_widget.delete(0, "end")
        entry_widget.insert(0, text)
        entry_widget.configure(state="disabled")

    # --- HARDWARE & DATA LOGIC ---
    def start_serial_thread(self):
        self.status_var.set("Status: Connecting to Hardware...")
        thread = threading.Thread(target=self.handle_serial_communication, daemon=True)
        thread.start()

    def handle_serial_communication(self):
        port = self.selected_com_port.get()
        
        if not port or port == "No Ports Found":
            self.after(0, lambda: messagebox.showerror("Error", "Please select a valid COM port."))
            self.after(0, self.stop_program)
            return

        try:
            ser = serial.Serial(port, 115200, timeout=1)
            time.sleep(2) 
            ser.write(b"access admin@123\n")
            command = f"setserial -system {self.serial_number}\n"
            ser.write(command.encode('utf-8'))
            time.sleep(0.5)
            
            response = ser.readlines()
            ser.close()
            
            self.after(0, lambda: messagebox.showinfo("Hardware Success", f"Configuration sent to {port}."))
            self.after(0, lambda: self.status_var.set("Status: Running"))
            
        except serial.SerialException as e:
            self.after(0, lambda: messagebox.showerror("Hardware Error", f"Connection failed: {e}"))
            self.after(0, self.stop_program)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("System Error", str(e)))
            self.after(0, self.stop_program)

    def log_to_excel(self):
        """Saves data to Excel without needing MS Office installed."""
        os.makedirs(os.path.join(BASE_DIR, 'assets'), exist_ok=True)
        excel_path = get_asset('ScanInventory.xlsx') 
        
        try:
            if not os.path.exists(excel_path):
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Scans"
                ws.append(["Timestamp", "Part Number", "Revision", "Serial Number"])
            else:
                wb = openpyxl.load_workbook(excel_path)
                ws = wb.active
                
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ws.append([timestamp, self.part_number, self.revision, self.serial_number])
            wb.save(excel_path)
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not save to Excel:\n{e}")

    def check_svn_updates(self):
        """MOCK SVN CHECK: Validates part numbers against a simulated server."""
        self.status_var.set("Status: Querying Server...")
        
        # Simulating network delay
        self.after(1500, self._show_mock_svn_result)

    def _show_mock_svn_result(self):
        messagebox.showinfo(
            "Version Control", 
            f"Server Check Complete.\n\nPart: {self.part_number}\nStatus: Verified and up-to-date with central repository."
        )
        if self.current_state == "running":
            self.status_var.set("Status: Running")

   
    def open_stop_window(self):
        if self.current_state == "idle": return
        confirm = messagebox.askyesno("Confirm Stop", "Halt the current diagnostic process?")
        if confirm:
            self.stop_program()

    def open_quit_window(self):
        confirm = messagebox.askyesno("Exit", "Are you sure you want to exit the application?")
        if confirm:
            self.quit()

if __name__ == "__main__":
    app = HardwareTesterApp()
    app.mainloop()