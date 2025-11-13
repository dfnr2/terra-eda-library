#!/usr/bin/env python3
"""
Yageo RC Series Resistor Generator
Generates comprehensive E96 series resistors for Terra EDA Library

Configuration:
- Symbol style: R (European) or R_US (American)
- Full E96 series across multiple decades
- All standard SMD package sizes
"""

import argparse
from decimal import Decimal

# E96 series values (1% resistors)
E96_VALUES = [
    1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24,
    1.27, 1.30, 1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58,
    1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, 1.96, 2.00,
    2.05, 2.10, 2.15, 2.21, 2.26, 2.32, 2.37, 2.43, 2.49, 2.55,
    2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09, 3.16, 3.24,
    3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
    4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23,
    5.36, 5.49, 5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65,
    6.81, 6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45,
    8.66, 8.87, 9.09, 9.31, 9.53, 9.76
]

# Package specifications: size -> (power, voltage, kicad_footprint)
PACKAGES = {
    '0201': ('1/20W', '50V', 'Resistor_SMD:R_0201_0603Metric'),
    '0402': ('1/16W', '50V', 'Resistor_SMD:R_0402_1005Metric'),
    '0603': ('1/10W', '75V', 'Resistor_SMD:R_0603_1608Metric'),
    '0805': ('1/8W', '150V', 'Resistor_SMD:R_0805_2012Metric'),
    '1206': ('1/4W', '200V', 'Resistor_SMD:R_1206_3216Metric'),
    '2512': ('1W', '500V', 'Resistor_SMD:R_2512_6332Metric'),
}

# Resistance decades to generate (7 decades: 1 ohm to 10 Megohm, full E96 coverage)
DECADES = [
    (1, 'R'),       # 1R to 9.76R  
    (10, 'R'),      # 10R to 97.6R
    (100, 'R'),     # 100R to 976R
    (1000, 'K'),    # 1K to 9.76K
    (10000, 'K'),   # 10K to 97.6K
    (100000, 'K'),  # 100K to 976K
    (1000000, 'M'), # 1M to 9.76M
]

def format_resistance_display(value):
    """Format resistance value for display and part naming (MPN format)"""
    if value >= 1000000:
        if value % 1000000 == 0:
            return f"{int(value // 1000000)}M"
        else:
            return f"{value / 1000000:.2f}M".rstrip('0').rstrip('.')
    elif value >= 1000:
        if value % 1000 == 0:
            return f"{int(value // 1000)}K"
        else:
            return f"{value / 1000:.2f}K".rstrip('0').rstrip('.')
    elif value >= 1:
        if value == int(value):
            return f"{int(value)}R"
        else:
            return f"{value:.2f}R".rstrip('0').rstrip('.')
    else:  # < 1 ohm
        return f"{int(value * 1000)}mR"

def format_resistance_simulation(value):
    """Format resistance value for SPICE simulation (numeric only)"""
    if value >= 1000000:
        if value % 1000000 == 0:
            return f"{int(value // 1000000)}Meg"
        else:
            return f"{value / 1000000:.6g}Meg"
    elif value >= 1000:
        if value % 1000 == 0:
            return f"{int(value // 1000)}K"
        else:
            return f"{value / 1000:.6g}K"
    elif value >= 1:
        if value == int(value):
            return str(int(value))
        else:
            return f"{value:.6g}"
    else:  # < 1 ohm
        return f"{value:.6g}"

def generate_mpn(value_str, package):
    """
    Generate Yageo RC series MPN
    
    MPN Format: RC{package}FR-07{value_code}
    - RC: Series prefix
    - {package}: Package size (0201, 0402, 0603, 0805, 1206, 2512)
    - FR: Tolerance code (F=1%, R=thick film)
    - 07: Packaging code (07 = taping/reel, 1 = paper taping reel)
    - {value_code}: Resistance value encoded as:
      * Decimal point → 'R' (e.g., 4.7R → 4R7L)
      * 'K' → 'KL' (e.g., 10K → 10KL)
      * 'M' → 'ML' (e.g., 1M → 1ML)
      * Trailing 'R' → 'L' for integer ohm values (e.g., 10R → 10L)
    
    Examples:
    - 1R → RC0603FR-071L
    - 4.7R → RC0603FR-074R7L  
    - 10K → RC0603FR-0710KL
    - 1M → RC0603FR-071ML
    """
    # Convert display format to MPN format
    mpn_value = value_str.replace('mR', 'R').replace('K', 'KL').replace('M', 'ML').replace('.', 'R')
    if mpn_value.endswith('R') and 'R' in mpn_value[:-1]:
        mpn_value = mpn_value[:-1] + 'L'
    return f"RC{package}FR-07{mpn_value}"

def generate_manufacturer_link(mpn):
    """Generate manufacturer product page link"""
    return f"https://www.yageogroup.com/products/Resistors/part/{mpn}"

def generate_part_id(value_str, tolerance, power, tempco, package):
    """Generate standardized part ID"""
    return f"RES-{value_str}-{tolerance}-{power}-{tempco}-{package}"

def should_include_package(resistance_ohms, package):
    """Determine if a resistance value should be available in a given package"""
    # Since we confirmed E96 coverage from 1R to 10M, all packages should support all values
    # in our range (we removed sub-1 ohm values)
    return True

def generate_resistors(symbol_style='R', packages=None, decades=None):
    """Generate resistor SQL statements"""
    if packages is None:
        packages = list(PACKAGES.keys())
    if decades is None:
        decades = DECADES
    
    symbol_ref = f"Device:{symbol_style}"
    
    sql_lines = [
        "-- Yageo RC Series SMT Resistors - E96 1% Values",
        "-- Generated from PYU-RC_GROUP_51_ROHS_L datasheet", 
        f"-- Symbol: {symbol_ref}",
        "-- Tolerance: F (1%)",
        "-- Packaging: 07 (taping/reel), 1 (paper taping reel)",
        "-- Temp coeff: ±200ppm/°C",
        "-- ",
        "-- Value Formats:",
        "-- - MPN uses display format (1R, 10K, 1M) for part identification",
        "-- - Database value uses simulation format (1, 10K, 1Meg) for SPICE compatibility",
        "-- - Booleans stored as 'yes'/'no' for KiCad compatibility",
        "",
        "BEGIN TRANSACTION;",
        ""
    ]
    
    total_parts = 0
    
    for package in packages:
        if package not in PACKAGES:
            continue
            
        power, voltage, footprint = PACKAGES[package]
        sql_lines.append(f"-- {package} Package ({power}, {voltage})")
        
        for decade_mult, unit_suffix in decades:
            for base_value in E96_VALUES:
                resistance_ohms = base_value * decade_mult
                
                if not should_include_package(resistance_ohms, package):
                    continue
                
                value_display = format_resistance_display(resistance_ohms)
                value_simulation = format_resistance_simulation(resistance_ohms)
                mpn = generate_mpn(value_display, package)
                manufacturer_link = generate_manufacturer_link(mpn)
                part_id = generate_part_id(value_display, "1%", power.replace('/', '_'), "200PPM", package)
                
                description = f"Resistor {value_display} 1% {power} thick film"
                
                sql_line = f"""INSERT INTO resistors (part_id, mpn, manufacturer, package, value, description, datasheet, manufacturer_link, kicad_symbol, kicad_footprint, source, dump_priority, tolerance, power_rating, temp_coeff, voltage_rating, composition, temp_operating, sim_device, sim_pins, lifecycle_status, rohs) 
VALUES ('{part_id}', '{mpn}', 'Yageo', '{package}', '{value_simulation}', '{description}', 'https://www.yageogroup.com/content/datasheet/asset/file/PYU-RC_GROUP_51_ROHS_L', '{manufacturer_link}', '{symbol_ref}', '{footprint}', 'yageo_rc', 0, '1%', '{power}', '±200ppm/°C', '{voltage}', 'Thick Film', '-55°C to +155°C', 'R', '1=+ 2=-', 'Active', 'yes');"""
                
                sql_lines.append(sql_line)
                total_parts += 1
        
        sql_lines.append("")  # Blank line between packages
    
    sql_lines.extend([
        "COMMIT;",
        "",
        f"-- Generated {total_parts} resistor parts"
    ])
    
    return '\n'.join(sql_lines)

def main():
    parser = argparse.ArgumentParser(description='Generate Yageo RC series resistors')
    parser.add_argument('--symbol', choices=['R', 'R_US'], default='R_US',
                        help='Resistor symbol style: R (European) or R_US (American)')
    parser.add_argument('--packages', nargs='+', choices=list(PACKAGES.keys()), 
                        default=list(PACKAGES.keys()),
                        help='Package sizes to generate')
    parser.add_argument('--output', '-o', 
                        default='resistors_200_yageo_rc.sql',
                        help='Output SQL file')
    parser.add_argument('--decades', type=int, nargs=2, metavar=('START', 'END'),
                        help='Resistance range as decade powers (e.g., -1 6 for 0.1R to 1M)')
    
    args = parser.parse_args()
    
    # Filter decades if specified
    decades = DECADES
    if args.decades:
        start_exp, end_exp = args.decades
        decades = [(10**exp, 'R' if exp <= 2 else ('K' if exp <= 5 else 'M')) 
                   for exp in range(start_exp, end_exp + 1)]
    
    sql_content = generate_resistors(
        symbol_style=args.symbol,
        packages=args.packages,
        decades=decades
    )
    
    # Write to file
    import os
    output_dir = os.path.dirname(args.output)
    if output_dir:  # Only create dir if there's a directory component
        os.makedirs(output_dir, exist_ok=True)
    
    with open(args.output, 'w') as f:
        f.write(sql_content)
    
    print(f"Generated {args.output}")
    print(f"Symbol style: Device:{args.symbol}")
    print(f"Packages: {', '.join(args.packages)}")

if __name__ == '__main__':
    main()