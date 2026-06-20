# SerialLink Pro: Automated Hardware Diagnostic Tool

A multithreaded Python desktop application designed to automate hardware diagnostics and inventory management. 

## Features
* **Asynchronous Serial Communication:** Uses `pyserial` to send commands to external hardware without freezing the GUI.
* **Modern Interface:** Built with `customtkinter` for a responsive, dark-mode ready UI.
* **Automated Data Pipeline:** Parses QR scanner inputs and automatically generates timestamped `.xlsx` inventory logs using `openpyxl`.
* **Network Ready:** Architected to support version control queries via subprocesses.

## How to Run
1. Install requirements: `pip install customtkinter pyserial openpyxl`
2. Run the application: `python app.py`
