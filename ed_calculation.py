import pandas as pd

def perform_dispatch(generators, demand, regions):
    """
    Robust Economic Dispatch
    """
    try:
        # ======================
        # 1. Data Preparation
        # ======================
        
        generators = generators.sort_values('Price').reset_index(drop=True)
        regions = regions.set_index('Region')
        demand = demand.copy()
        
        # align lists of names
        hours = demand.index.tolist()
        region_names = regions.index.tolist()
        gen_names = generators['Generator'].tolist()
        
        # Initialize outputs 
        generation_schedule = pd.DataFrame(0, index=hours, columns=gen_names)
        regional_flows = pd.DataFrame(0, index=hours, columns=region_names)
        met_demand = pd.DataFrame(0, index=hours, columns=region_names)
        curtailment = pd.DataFrame(0, index=hours, columns=region_names)
        curtailment_reasons = pd.DataFrame('', index=hours, columns=region_names)

        # lookup dictionaries
        gen_info = generators.set_index('Generator').to_dict('index')
        region_limits = regions.to_dict('index')

        # ======================
        # 2. Main Dispatch Loop
        # ======================
        for hour in hours:
            hour_demand = demand.loc[hour].to_dict()
            remaining_demand = hour_demand.copy()
            
            # ----------------------
            # Stage 1: Local Dispatch
            # ----------------------
            for gen_name, gen_data in gen_info.items():
                gen_region = gen_data['Region']
                
                if remaining_demand[gen_region] > 0:
                    dispatch = min(gen_data['Max Capacity'], remaining_demand[gen_region])
                    generation_schedule.at[hour, gen_name] = dispatch
                    remaining_demand[gen_region] -= dispatch
                    met_demand.at[hour, gen_region] += dispatch

            # ----------------------
            # Stage 2: Regional Transfers
            # ----------------------
            # Find regions needing imports (sorted by highest marginal cost)
            importers = sorted(
                [r for r in region_names if remaining_demand[r] > 0],
                key=lambda r: max(g['Price'] for g in gen_info.values() if g['Region'] == r),
                reverse=True
            )
            
            for importer in importers:
                # Find available exporters (cheapest first)
                exporters = sorted(
                    [(name, data) for name, data in gen_info.items() 
                     if data['Region'] != importer and 
                     data['Max Capacity'] > generation_schedule.at[hour, name]],
                    key=lambda x: x[1]['Price']
                )
                
                for gen_name, gen_data in exporters:
                    if remaining_demand[importer] <= 0:
                        break
                        
                    export_region = gen_data['Region']
                    
                    # Calculate transfer capacity
                    available = min(
                        region_limits[export_region]['Export Limit'],
                        gen_data['Max Capacity'] - generation_schedule.at[hour, gen_name]
                    )
                    needed = min(
                        region_limits[importer]['Import Limit'],
                        remaining_demand[importer]
                    )
                    transfer = min(available, needed)
                    
                    if transfer > 0:
                        # Execute transfer
                        generation_schedule.at[hour, gen_name] += transfer
                        regional_flows.at[hour, export_region] -= transfer
                        regional_flows.at[hour, importer] += transfer
                        met_demand.at[hour, importer] += transfer
                        remaining_demand[importer] -= transfer

            # ----------------------
            # Stage 3: Curtailment
            # ----------------------
            for region in region_names:
                if remaining_demand[region] > 0:
                    curtailment.at[hour, region] = remaining_demand[region]
                    
                    reasons = []
                    # Check local generation
                    local_cap = sum(g['Max Capacity'] for g in gen_info.values() if g['Region'] == region)
                    if hour_demand[region] > local_cap:
                        reasons.append("Insufficient local generation")
                    # Check import limits
                    if remaining_demand[region] > region_limits[region]['Import Limit']:
                        reasons.append("Import limit reached")
                        
                    curtailment_reasons.at[hour, region] = ", ".join(reasons) or "Network constraints"

        return generation_schedule, regional_flows, met_demand, curtailment, curtailment_reasons

    except Exception as e:
        raise Exception(f"Dispatch failed at hour {hour if 'hour' in locals() else 'N/A'}: {str(e)}") from e