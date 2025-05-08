import pandas as pd
import os

# directory (please update this to your exact path)
BASE_DIR = r"C:\Users\64846\Desktop\SCED"

def read_generator_data():
    """Read and validate generator data from exact path"""
    file_path = os.path.join(BASE_DIR, "data", "Gen.xlsx")
    try:
        # Verify file exists before reading
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at: {file_path}")
        
        df = pd.read_excel(file_path)
        
        # Validate required columns
        required_cols = ['Generator', 'Max Capacity', 'Region', 'Price']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing columns: {missing_cols}")
            
        # Validate no empty values
        if df.isnull().values.any():
            raise ValueError("Generator data contains empty values")
            
        return df
    
    except Exception as e:
        raise Exception(f"Failed to read generator data: {str(e)}\n"
                      f"Attempted path: {file_path}")

def read_demand_data():
    """Read and validate demand data from exact path"""
    file_path = os.path.join(BASE_DIR, "data", "Demand.xlsx")
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at: {file_path}")
            
        df = pd.read_excel(file_path, index_col=0)
        df.index.name = 'Hour'
        
        if df.isnull().values.any():
            raise ValueError("Demand data contains empty values")
            
        # Validate all demand values are non-negative
        if (df < 0).any().any():
            raise ValueError("Demand values cannot be negative")
            
        return df
    
    except Exception as e:
        raise Exception(f"Failed to read demand data: {str(e)}\n"
                      f"Attempted path: {file_path}")

def read_region_data():
    """Read and validate region data from exact path"""
    file_path = os.path.join(BASE_DIR, "data", "Region.xlsx")
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at: {file_path}")
            
        df = pd.read_excel(file_path)
        
        required_cols = ['Region', 'Import Limit', 'Export Limit']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing columns: {missing_cols}")
            
        # Validate limits are non-negative
        if (df['Import Limit'] < 0).any() or (df['Export Limit'] < 0).any():
            raise ValueError("Import/Export limits cannot be negative")
            
        return df
    
    except Exception as e:
        raise Exception(f"Failed to read region data: {str(e)}\n"
                      f"Attempted path: {file_path}")