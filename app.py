from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Allows Vercel to connect securely

@app.route('/', methods=['GET'])
def home():
    return "NEXUS BRAIN IS ONLINE. RUNNING V3.2 MATH ENGINE (DUAL METHOD)."

@app.route('/simulate', methods=['POST'])
def simulate():
    incoming_data = request.json
    print("Received parameters from Vercel:", incoming_data)
    
    # Check which method the dashboard sent
    sim_method = incoming_data.get('method', 'A')
    
    # ==========================================
    # METHOD A: COMPONENT MATH
    # ==========================================
    if sim_method == 'A':
        v_sh = float(incoming_data.get('shower', 120))
        v_tl = float(incoming_data.get('toilet', 40))
        v_ln = float(incoming_data.get('laundry', 25))
        v_ml = float(incoming_data.get('meals', 3.0))
        occ_rate = float(incoming_data.get('occupancy', 85)) / 100.0
        
        projects = [
            {'Category': 'Non-Hotel', 'Type': '1BR', 'Count': 236},
            {'Category': 'Hotel', 'Type': 'Villa', 'Count': 6},
            {'Category': 'Non-Hotel', 'Type': '2BR', 'Count': 47},
            {'Category': 'Non-Hotel', 'Type': '1BR', 'Count': 139}
        ]
        
        sum_variable_L = 0
        sum_fixed_L = 0
        
        for p in projects:
            count = p['Count']
            is_hotel = p['Category'] == 'Hotel'
            pax_map = {'1BR': 2, '2BR': 4, '3BR': 5, '4BR': 6, 'Villa': 6}
            total_pax = count * pax_map.get(p['Type'], 2)
            
            v_mc = 40 if is_hotel else 30
            v_wm = 25 if is_hotel else 20
            staff_ratio = 1.2 if is_hotel else 0.2
            
            sum_variable_L += (total_pax * (v_sh + v_tl + v_mc + v_ln)) + (total_pax * v_ml * v_wm)
            sum_fixed_L += (count * staff_ratio * 100) 
            
        peak_m3 = ((sum_variable_L * 0.90) + sum_fixed_L) / 1000
        annual_m3 = (((sum_variable_L * occ_rate) + sum_fixed_L) / 1000) * 365
        
        growth_factor = (1 + 0.035) ** 4 
        peak_m3_final = peak_m3 * growth_factor * 1.10
        annual_m3_final = annual_m3 * growth_factor * 1.10

        return jsonify({
            "status": "success",
            "method_used": "A",
            "peak_demand": round(peak_m3_final, 0),
            "annual_demand": round(annual_m3_final, 0)
        })

    # ==========================================
    # METHOD B: SMART INFERENCE MATH
    # ==========================================
    elif sim_method == 'B':
        units = float(incoming_data.get('units', 120))
        pools = float(incoming_data.get('pools', 8))
        
        # Smart Inference Base Rates (Derived from Laguna Baseline Logic)
        base_unit_avg = 1.8  # m3/day per unit
        base_unit_peak = 2.2 # m3/day per unit
        base_pool_avg = 15.0 # m3/day per pool
        base_pool_peak = 20.0 # m3/day per pool
        
        avg_daily = (units * base_unit_avg) + (pools * base_pool_avg)
        peak_daily = (units * base_unit_peak) + (pools * base_pool_peak)
        
        annual_m3 = avg_daily * 365
        
        # Apply identical infrastructure factors (Growth + NRW)
        growth_factor = (1 + 0.035) ** 4 
        peak_m3_final = peak_daily * growth_factor * 1.10
        annual_m3_final = annual_m3 * growth_factor * 1.10
        
        return jsonify({
            "status": "success",
            "method_used": "B",
            "peak_demand": round(peak_m3_final, 0),
            "annual_demand": round(annual_m3_final, 0)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
