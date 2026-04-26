from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Allows Vercel to connect securely

@app.route('/', methods=['GET'])
def home():
    return "NEXUS BRAIN IS ONLINE. RUNNING V3.2 MATH ENGINE."

@app.route('/simulate', methods=['POST'])
def simulate():
    # 1. Catch the Data from Vercel
    incoming_data = request.json
    print("Received parameters from Vercel:", incoming_data)
    
    # Extract sliders (If Vercel doesn't send a number, use these Laguna defaults)
    v_sh = float(incoming_data.get('shower', 120))
    v_tl = float(incoming_data.get('toilet', 40))
    v_ln = float(incoming_data.get('laundry', 25))
    v_ml = float(incoming_data.get('meals', 3.0))
    occ_rate = float(incoming_data.get('occupancy', 72)) / 100.0
    
    # 2. The Laguna Internal Database (From your original Streamlit code)
    projects = [
        {'Category': 'Non-Hotel', 'Type': '1BR', 'Count': 236},
        {'Category': 'Hotel', 'Type': 'Villa', 'Count': 6},
        {'Category': 'Non-Hotel', 'Type': '2BR', 'Count': 47},
        {'Category': 'Non-Hotel', 'Type': '1BR', 'Count': 139}
    ]
    
    # 3. Method A Core Math Engine
    sum_variable_L = 0
    sum_fixed_L = 0
    
    for p in projects:
        count = p['Count']
        is_hotel = p['Category'] == 'Hotel'
        
        # Pax Map
        pax_map = {'1BR': 2, '2BR': 4, '3BR': 5, '4BR': 6, 'Villa': 6}
        pax_per_unit = pax_map.get(p['Type'], 2)
        total_pax = count * pax_per_unit
        
        # Fixed Engineering Constants
        v_mc = 40 if is_hotel else 30 # Misc faucet usage
        v_wm = 25 if is_hotel else 20 # Water per meal
        staff_ratio = 1.2 if is_hotel else 0.2
        
        # Calculate daily liters per project
        row_dom = total_pax * (v_sh + v_tl + v_mc + v_ln)
        row_fnb = total_pax * v_ml * v_wm
        
        sum_variable_L += (row_dom + row_fnb)
        sum_fixed_L += (count * staff_ratio * 100) 
        
    # 4. Final Demand Calculation (Converting to m3)
    peak_occ = 0.90 # 90% peak season assumption
    
    peak_m3 = ((sum_variable_L * peak_occ) + sum_fixed_L) / 1000
    avg_m3 = ((sum_variable_L * occ_rate) + sum_fixed_L) / 1000
    annual_m3 = avg_m3 * 365
    
    # Apply 3.5% Growth to Year 2030 and 10% Leakage (NRW)
    growth_factor = (1 + 0.035) ** 4 
    peak_m3_final = peak_m3 * growth_factor * 1.10
    annual_m3_final = annual_m3 * growth_factor * 1.10
    
    # 5. Send the exact calculations back to the Vercel Dashboard
    return jsonify({
        "status": "success",
        "peak_demand": round(peak_m3_final, 0),
        "annual_demand": round(annual_m3_final, 0),
        "message": "Method A Mathematical Projection Complete."
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
