""" 
Title: Coil_Parameter_Selection
Author: John
Version: 1.0
Date:19/01/24

Idea is input max outer diamter and get a list of potential coils with parameters in a csv file
The code will generate the following columns:
coil_number,out_diameter,avg_diameter, trace_width, trace_spacing, turns_per_layer, coil_fill_ratio,series_impedance,
parallel_impedance, dc_resistance, ac_resistance, capacitance_parasitic, capaciatnce_tank, total_inductance, 
operating_frequency,q_factor

The csv file will be read and edited to sort the coils will be sorted according to the:
highest inductance, lowest resistance, highest q factor.
In that order in order to read the most optimum coil parameters in the row.

lengths are in micrometers divide by 1e6 for calculations in meters and 1000 in mm
length_in_micrometers = 150  # Replace with your actual length in micrometers
length_in_meters = length_in_micrometers / 1e6
"""
import math
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy
import sympy as sp


""" Variables """
# Inputs 
input_outter_diameter = 20  # Set default value for out_diameter

# CSV Creation
csv_file_name = 'coil_parameters_20mm.csv'
coil_number = 0  # Number of the coil in the CSV file
trace_width = 0  # Script will create a range of trace widths from 0.15mm(min) to 1mm(max) in steps of 0.01mm
trace_spacing = 0  # Create a range of trace spacings from 0.15mm(min) to 0.3mm(max) in steps of 0.01mm
turns_per_layer = 0  # Turns per layer of the coil from 1(min) to 120(max) in steps of 1(always a whole number)
capacitance_tank = [10, 15, 22, 33, 47, 68, 100, 150, 220, 330, 470, 680, 1000, 1500, 2200, 3300, 4700, 6800, 10000]
# The external capacitor simulated from 10pF to 10000pF in standard EIA-96 code values

# Calculations
inner_diameter = 0  # Calculated from the trace_width, trace_spacing & turns_per_layer from the out_diameter
avg_diameter = 0  # Calculated average diameter of the coil
coil_fill_ratio = 0  # Should always be more than 0.3. Delete rows with less
series_impedance = 0  # Rs calculated 
parallel_impedance = 0  # Rp calculated
dc_resistance = 0  # DC resistance calculated 
ac_resistance = 0  # AC resistance calculated
capacitance_parasitic = 0  # The calculated parasitic capacitance of the coil
q_factor = 0
operating_frequency = 0
total_inductance = 0  # The 

# Boundaries
min_coil_fill_ratio = 0.3

""" Functions """
def calculate_inner_diameter(tw_csv, ts_csv, tpl_csv, od_csv):
    tw_m = tw_csv/(1000*1000)  #Convert trace width to m
    ts_m = ts_csv/(1000*1000)  #Convert spacing to m
    od_m = od_csv/(1000*1000) 
    id_m = od_m - 2 * (tpl_csv * ((tw_m) + (ts_m)))
    #id_m = id_m - (2*ts_m)
    id_mm = id_m*1000 #convert to mm
    id_um = id_mm*1000 #convert to um
    return id_um

def calculate_avg_diameter(id_csv, od_csv):
    id_m = id_csv/(1000*1000)                                #convert to m
    od_m = od_csv/(1000*1000)
    ad_m = (((id_m) + od_m) / 2)                              #Avergae diameter in m
    ad_mm = ad_m*1000                                           #covert to mm
    ad_um = ad_mm*1000                                          #convert to um
    return ad_um

def calculate_coil_fill_ratio(od_csv, id_csv):
    od_m = od_csv/(1000*1000)                         #um to m
    id_m = id_csv/(1000*1000)                         #um to m 
    cfr_m = id_m/od_m                               #((od_calc4-(id_calc2)) / (od_calc4+(id_calc2)))
    cfr_mm = cfr_m*1000                                     #Convert m to mm
    cfr_um = cfr_mm*1000                                    #Convert mm to um
    return cfr_um

# Function to create the CSV file
def create_coils(max_outer_diameter, csv_filename):
    coil_numbers = []
    out_diameters = []
    trace_widths = []
    trace_spacings = []
    turns_per_layers = []
    capacitance_tanks = []
    cn = 1 # Initialize coil_number
    # Generate rows for each combination of parameters
    for tw1 in range(150, 1010, 10):                        # 0.15mm to 1mm in steps of 0.01mm
        for ts1 in range(150, 301, 10):                     # 0.15mm to 0.3mm in steps of 0.01mm
            for tpl2 in range(1, 121):                      # 1 to 120
                for cap_value in capacitance_tank:
                    coil_numbers.append(cn)
                    out_diameters.append(max_outer_diameter)
                    trace_widths.append(tw1 )
                    trace_spacings.append(ts1)
                    turns_per_layers.append(tpl2)
                    capacitance_tanks.append(cap_value)
                    cn += 1 
    df = pd.DataFrame({                                    # Create a DataFrame from the lists
        'CSV_CoilNumber': coil_numbers,
        'CSV_OutterDiameter': out_diameters,
        'CSV_TraceWidth': trace_widths,
        'CSV_TraceSpacing': trace_spacings,
        'CSV_TurnsPerLayer': turns_per_layers,
        'CSV_TankCap': capacitance_tanks})
    # Write DataFrame to CSV
    df.to_csv(csv_filename, index=False)


def inner_diameter_csv(input_csv, output_csv):
    df = pd.read_csv(input_csv)                                         # Read the existing CSV file
    if 'CSV_InnerDiameter' not in df.columns:                           # Check if 'CSV_InnerDiameter' column already exists
        df['CSV_InnerDiameter'] = calculate_inner_diameter(df['CSV_TraceWidth'], df['CSV_TraceSpacing'], df['CSV_TurnsPerLayer'], df['CSV_OutterDiameter'])# Calculate and add CSV_InnerDiameter to the DataFrame
    else: 
        df['CSV_InnerDiameter'] = calculate_inner_diameter(df['CSV_TraceWidth'], df['CSV_TraceSpacing'], df['CSV_TurnsPerLayer'], df['CSV_OutterDiameter'])        # Overwrite the existing 'CSV_InnerDiameter' column
    df['CSV_InnerDiameter'] = df['CSV_InnerDiameter'].astype(int)       # Convert 'CSV_InnerDiameter' to integers
    df.to_csv(output_csv, index=False)                                  # Write the updated DataFrame to the new CSV file
    updated_df = pd.read_csv(output_csv)                                # Read the CSV file again
    updated_df = updated_df[updated_df['CSV_InnerDiameter'] >= 0]       # Remove rows with inner diameter less than 0
    updated_df.to_csv(output_csv, index=False)                          # Write the updated DataFrame to the same CSV file


def avg_diameter_csv(input_csv, output_csv):
    df = pd.read_csv(input_csv)                                         # Read the existing CSV file
    if 'CSV_AvgDiameter' not in df.columns:                             # Check if 'CSV_AvgDiameter' column already exists
        df['CSV_AvgDiameter'] = calculate_avg_diameter(df['CSV_InnerDiameter'], df['CSV_OutterDiameter'])# Calculate and add CSV_AvgDiameter to the DataFrame
    else:
        df['CSV_AvgDiameter'] = calculate_avg_diameter(df['CSV_InnerDiameter'], df['CSV_OutterDiameter'])# Overwrite the existing 'CSV_AvgDiameter' column
    df['CSV_AvgDiameter'] = df['CSV_AvgDiameter'].astype(int)           # Convert 'CSV_AvgDiameter' to integers
    df.to_csv(output_csv, index=False)                                  # Write the updated DataFrame to the new CSV file


def coil_fill_ratio_csv(input_csv, output_csv):
    df = pd.read_csv(input_csv)                                         # Read the existing CSV file
    if 'CSV_OutterDiameter' not in df.columns:                          # Check if 'CSV_AvgDiameter' and 'CSV_InnerDiameter' columns already exist
        create_coils(max_outer_diameter, csv_filename)                  # Make sure outer diameter is available
    if 'CSV_InnerDiameter' not in df.columns:
        inner_diameter_csv(input_csv, input_csv)                        # Make sure CSV_InnerDiameter is available
    df['CSV_CFR'] = calculate_coil_fill_ratio(df['CSV_OutterDiameter'], df['CSV_InnerDiameter'])# Calculate coil fill ratio
    df['CSV_CFR'] = df['CSV_CFR'].astype(int)                                     # Convert 'coil_fill_ratio' to integers
    df.to_csv(output_csv, index=False)                                  # Write the updated DataFrame to the new CSV file
    df = df[df['CSV_CFR'] >= min_coil_fill_ratio]                            # Remove rows with coil fill ratio below the threshold
    df.to_csv(output_csv, index=False)                                  # Write the updated DataFrame to the new CSV file

    
def calculate_total_inductance(turns_per_layer, avg_diameter, coil_fill_ratio):
    mu_0 = 4 * math.pi * 1e-7  # Permeability of free space
    # Geometry of coil
    k1=2.34
    k2=2.75
    C1 = 1.27  # Adjust the value of C1 based on your specific units and requirements
    C2 = 2.07  # Adjust the value of C2 based on your specific units and requirements
    C3 = 0.18  # Adjust the value of C3 based on your specific units and requirements
    C4 = 0.13  # Adjust the value of C4 based on your specific units and requirements
    
    ad_m = avg_diameter / (1000 * 1000)  # Convert 'avg_diameter' to meters
    cfr_m = coil_fill_ratio / (1000 * 1000)  # Convert 'coil_fill_ratio' to meters
    
    L_H = ((mu_0*(turns_per_layer**2)*ad_m*C1) / 2) * (math.log(float(C2)/float(cfr_m))+(C3*cfr_m)+(C4*cfr_m**2))
    #L_H = ((k1*mu_0*(turns_per_layer**2)*ad_m*C1) / (1+k2*cfr_m)) * (math.log(float(C2)/float(cfr_m))+(C3*cfr_m)+(C4*cfr_m**2))
    L_H = L_H * 4
    L_pH = L_H * 1e12
    return L_pH

def inductance_csv(input_csv, output_csv):
    # Read the existing CSV file
    df = pd.read_csv(input_csv)
    # Apply the calculate_total_inductance function to each row
    df['CSV_CoilInductance'] = df.apply(lambda row: calculate_total_inductance(row['CSV_TurnsPerLayer'], row['CSV_AvgDiameter'], row['CSV_CFR']), axis=1)
    df['CSV_CoilInductance'] = df['CSV_CoilInductance'].astype(int)                                     # Convert 'coil_fill_ratio' to integers
    # Write the updated DataFrame to the new CSV file
    df.to_csv(output_csv, index=False)

def calculate_sensor_frequency(coil_inductance, tank_cap):
    f_sens_Hz = 1 / (2 * math.pi * math.sqrt(float(coil_inductance) * float(tank_cap)))
    f_sens_pHz = f_sens_Hz * 1e12 #convert to picoHz
    return f_sens_pHz

def sensor_freq_csv(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    df['CSV_SensorFreq'] = df.apply(lambda row: calculate_sensor_frequency(row['CSV_CoilInductance'], row['CSV_TankCap']), axis=1)
    df['CSV_SensorFreq'] = df['CSV_SensorFreq'].astype(int)                                     # Convert 'coil_fill_ratio' to integers
    df.to_csv(output_csv, index=False)


def calculate_R_s(sens_freq, traced_width ):
    """Calculate the impedance of a winding with a given number of turns and diameter.
    https://www.infineon.com/dgdl/Infineon-AN219207_Inductive_Sensing_Design_Guide-ApplicationNotes-v04_00-EN.pdf?fileId=8ac78c8c7cdc391c017d0d358bd5662c
    Equation 20"""
    frequency = sens_freq/1e12 #convert to Hz
    trace_width = traced_width/1000 #convert to mm
    trace_height = 34.79/1e3  # Trace height in mm
    relative_resistivity = 1 # 1.526 #constant
    f_rho_R = 2.16e-7  # Constant factor
    #series_resistance = ((f_rho_R)*math.sqrt(frequency*relative_resistivity))/(2*(trace_width+trace_height))
    # Calculate Rs GPT
    Rs = (f_rho_R * math.sqrt(frequency * relative_resistivity)) / (2 * (trace_width + trace_height))
    Rs_zOhms = Rs*1e21 #convert to ztta ohms
    return Rs_zOhms

def calculate_R_s_csv(input_csv, output_csv):
    # Read the CSV file
    df = pd.read_csv(input_csv)
    # Calculate Rs for each row and create a new column 'CSV_SeriesACResistance'
    df['CSV_SeriesACResistance'] = df.apply(lambda row: calculate_R_s(row['CSV_TraceWidth'], row['CSV_SensorFreq']), axis=1)
    # Save the results to the output CSV file
    df['CSV_SeriesACResistance'] = df['CSV_SeriesACResistance'].astype(int)                                     # Convert 'coil_fill_ratio' to integers
    df.to_csv(output_csv, index=False)

def calculate_trace_length(outer_diameter, num_turns, trace_width, trace_spacing):
    wire_length = 0
    side_length = outer_diameter # convert to mm
    for _ in range(int(num_turns)):
        wire_length += 4 * side_length
        side_length -= 2 * (trace_width + trace_spacing)
    return wire_length

def trace_length_csv(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    # Calculate wire length using the effective side length and number of turns
    df['CSV_TraceLength'] = df.apply(lambda row: calculate_trace_length(row['CSV_OutterDiameter'], row['CSV_TurnsPerLayer'], row['CSV_TraceWidth'], row['CSV_TraceSpacing']), axis=1)
    # Convert to appropriate units if needed
    # Save the updated DataFrame to the output CSV
    df['CSV_TraceLength'] = df['CSV_TraceLength'].astype(int)                                     # Convert 'coil_fill_ratio' to integers
    df.to_csv(output_csv, index=False)

def calculate_dc_resistance(wire_length, trace_width):
    # Convert trace dimensions to meters
    trace_width_m = trace_width / 1000*1000  # converting um to m
    trace_height = 34.79/1e3/1000  # Trace height in m
    resistivity_copper = 1.68e-7  # in Ohm * m^2 / square
    # Calculate cross-sectional area
    cross_sectional_area = trace_width_m * trace_height
    # Calculate resistance
    resistance = resistivity_copper * (wire_length / cross_sectional_area)
    return resistance*1e3

def calculate_dc_resistance_csv(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    # Calculate DC resistance
    df['CSV_DCResistance'] = df.apply(lambda row: calculate_dc_resistance(row['CSV_TraceLength'], row['CSV_TraceWidth']), axis=1)
    # Save the updated DataFrame to the output CSV
    df['CSV_DCResistance'] = df['CSV_DCResistance'].astype(int)                                     # Convert 'coil_fill_ratio' to integers
    df.to_csv(output_csv, index=False)

#Using DC resistance in the wrong way 
def calculate_q_factor(s_f, i_v, s_r):
    sense_freq = s_f * 1e3
    inductnace_val = i_v * 1e3
    series_resistance = s_r/1e3
    q_factor = (2*(math.pi)*sense_freq * inductnace_val)/series_resistance

def calculate_q_factor_chatgpt(series_impedance, ac_resistance):
    reactance = series_impedance - ac_resistance
    q_factor = reactance / ac_resistance
    return q_factor

def calculate_q_factor_csv(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    # Calculate DC resistance
    df['CSV_Qfactor'] = df.apply(lambda row: calculate_q_factor(row['CSV_SensorFreq'], row['CSV_CoilInductance'], row['CSV_DCResistance']), axis=1)
    # Save the updated DataFrame to the output CSV
    df['CSV_Qfactor'] = df['CSV_Qfactor'].astype(int)                                     # Convert 'coil_fill_ratio' to integers
    df.to_csv(output_csv, index=False)






def top_five_options(input_csv):
    # Read the CSV file
    df = pd.read_csv(input_csv)

    # Sort the DataFrame by 'CSV_CoilInductance' and 'CSV_Qfactor' columns in descending order
    df_sorted = df.sort_values(by=['CSV_CoilInductance', 'CSV_Qfactor'], ascending=[False, False])

    # Print the top 5 rows
    print("Top 5 Options with Highest Inductance and Q Factor:")
    print(df_sorted.head(5))

if __name__ == "__main__":
    max_outer_diameter = input_outter_diameter*1000  # Set your max outer diameter value here
    csv_filename = csv_file_name
    #create_coils(max_outer_diameter, csv_filename)
    #inner_diameter_csv(csv_file_name, csv_file_name)
    #avg_diameter_csv(csv_file_name, csv_file_name)
    #coil_fill_ratio_csv(csv_file_name,csv_file_name)
    #inductance_csv(csv_file_name, csv_file_name)
    #sensor_freq_csv(csv_file_name, csv_file_name)
    #calculate_R_s_csv(csv_file_name, csv_file_name)
    #trace_length_csv(csv_file_name, csv_file_name)
    calculate_dc_resistance_csv(csv_file_name, csv_file_name)
    calculate_q_factor_csv(csv_file_name, csv_file_name)
    df = pd.read_csv(csv_filename)
    print(df.dtypes)
    # Call the top_five_options function
    #top_five_options(csv_file_name)
