import pandas as pd
import xlsxwriter
from typing import Dict, Tuple

def save_generation_schedule(output_path: str, 
                           schedule: pd.DataFrame, 
                           gen_info: pd.DataFrame) -> None:
    """Save generation schedule with generator metadata"""
    try:
        with pd.ExcelWriter(output_path) as writer:
            schedule.to_excel(writer, sheet_name='Generation_Schedule')
            gen_info.to_excel(writer, sheet_name='Generator_Info', index=False)
    except Exception as e:
        raise Exception(f"Failed to save generation schedule: {str(e)}")

def save_regional_flows(output_path: str, 
                      flows: pd.DataFrame) -> None:
    """Save regional power flows with sign convention:
       Positive = Import, Negative = Export"""
    try:
        flows.to_excel(output_path, 
                      sheet_name='Regional_Flows',
                      float_format="%.2f")
    except Exception as e:
        raise Exception(f"Failed to save regional flows: {str(e)}")

def save_demand_analysis(output_path: str,
                       met_demand: pd.DataFrame,
                       curtailed: pd.DataFrame,
                       reasons: pd.DataFrame) -> None:
    """Save demand analysis with conditional formatting"""
    try:
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            # Sheet 1: Met Demand
            met_demand.to_excel(writer, sheet_name='Met_Demand')
            
            # Sheet 2: Curtailed Demand (with formatting)
            curtailed.to_excel(writer, sheet_name='Curtailed_Demand')
            
            # Sheet 3: Curtailment Reasons
            reasons.to_excel(writer, sheet_name='Curtailment_Reasons')
            
            # Formatting
            workbook = writer.book
            worksheet = writer.sheets['Curtailed_Demand']
            
            # Red highlight for curtailed demand
            red_format = workbook.add_format({
                'bg_color': '#FFC7CE',
                'font_color': '#9C0006'
            })
            
            # Apply to cells > 0
            worksheet.conditional_format(
                'B2:Z100',  # Adjust range as needed
                {
                    'type': 'cell',
                    'criteria': '>',
                    'value': 0,
                    'format': red_format
                }
            )
    except Exception as e:
        raise Exception(f"Failed to save demand analysis: {str(e)}")