import sys
import os
sys.path.append(os.path.abspath('scripts'))
from generate_schematic import build_schematic
import openpyxl

def create_mock_excel(path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Schematic"
    
    # Simple data structure
    data = [
        ["Carrier", "Status", "Auth", "%", "Premium"],
        ["$10,000,000 xs Primary"],
        ["Carrier A", "Bound", 10000000, 1.0, 100000],
        ["$15,000,000 xs $10,000,000"],
        ["Carrier B", "Bound", 15000000, 0.5, 75000],
        ["Carrier C", "Bound", 15000000, 0.5, 75000],
    ]
    
    for row in data:
        ws.append(row)
    
    wb.save(path)

def test_render():
    excel_path = "tests/data/test_input.xlsx"
    pptx_path = "tests/data/test_output.pptx"
    
    os.makedirs("tests/data", exist_ok=True)
    create_mock_excel(excel_path)
    
    print(f"Running build_schematic on {excel_path}...")
    build_schematic(excel_path, pptx_path, account_name_override="Test Account")
    
    if os.path.exists(pptx_path):
        print(f"✅ Success: {pptx_path} generated.")
    else:
        print(f"❌ Error: {pptx_path} NOT generated.")

if __name__ == "__main__":
    test_render()
