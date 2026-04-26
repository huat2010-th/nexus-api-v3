from flask import Flask, request, jsonify
from flask_cors import CORS
import math

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "NEXUS BRAIN IS ONLINE. RUNNING V3.2 MATH ENGINE (WITH LIVE CHARTS)."

@app.route('/simulate', methods=['POST'])
def simulate():
    incoming_data = request.json
    sim_method = incoming_data.get('method', 'A')
    
    # 1. Base Variables
    peak_m3_final = 0
    annual_m3_final = 0
    
    # ==========================================
    # METHOD A MATH
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
        
        sum_var, sum_fix = 0, 0
        for p in projects:
            count = p['Count']
            is_hotel = p['Category'] == 'Hotel'
            pax = count * {'1BR': 2, '2BR': 4, '3BR': 5, '4BR': 6, 'Villa': 6}.get(p['Type'], 2)
            
            sum_var += (pax * (v_sh + v_tl + (40 if is_hotel else 30) + v_ln)) + (pax * v_ml * (25 if is_hotel else 20))
            sum_fix += (count * (1.2 if is_hotel else 0.2) * 100) 
            
        peak_m3 = ((sum_var * 0.90) + sum_fix) / 1000
        annual_m3 = (((sum_var * occ_rate) + sum_fix) / 1000) * 365
        growth_factor = (1 + 0.035) ** 4 
        
        peak_m3_final = peak_m3 * growth_factor * 1.10
        annual_m3_final = annual_m3 * growth_factor * 1.10

    # ==========================================
    # METHOD B MATH
    # ==========================================
    elif sim_method == 'B':
        units = float(incoming_data.get('units', 120))
        pools = float(incoming_data.get('pools', 8))
        
        avg_daily = (units * 1.8) + (pools * 15.0)
        peak_daily = (units * 2.2) + (pools * 20.0)
        growth_factor = (1 + 0.035) ** 4 
        
        peak_m3_final = peak_daily * growth_factor * 1.10
        annual_m3_final = (avg_daily * 365) * growth_factor * 1.10

    # ==========================================
    # CHART GENERATOR (The Magic)
    # ==========================================
    avg_daily_m3 = annual_m3_final / 365
    
    # 1. 12-Month Flow vs Demand Curve
    # We use a sine wave to simulate the seasonal "Peak" in July/August
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    chart_consumption = []
    
    for i, month in enumerate(months):
        # Creates a bell curve peaking in month 6 (July)
        seasonality = 1 + (math.sin((i / 11) * math.pi) * ((peak_m3_final - avg_daily_m3) / avg_daily_m3))
        
        demand_val = int(avg_daily_m3 * seasonality)
        flow_val = int(demand_val * 1.08) # Flow is slightly higher than demand (NRW buffer)
        
        chart_consumption.append({
            "month": month,
            "flow": flow_val,
            "demand": demand_val
        })

    # 2. Sector Distribution (Bar Chart)
    # We slice the total annual demand into categories
    q_base = annual_m3_final / 4
    chart_distribution = [
        {"sector": "Residential", "q1": int(q_base * 0.40), "q2": int(q_base * 0.42), "q3": int(q_base * 0.45), "q4": int(q_base * 0.41)},
        {"sector": "Commercial", "q1": int(q_base * 0.25), "q2": int(q_base * 0.28), "q3": int(q_base * 0.30), "q4": int(q_base * 0.26)},
        {"sector": "Industrial", "q1": int(q_base * 0.20), "q2": int(q_base * 0.21), "q3": int(q_base * 0.22), "q4": int(q_base * 0.20)},
        {"sector": "Agriculture", "q1": int(q_base * 0.10), "q2": int(q_base * 0.15), "q3": int(q_base * 0.18), "q4": int(q_base * 0.11)},
        {"sector": "Public", "q1": int(q_base * 0.05), "q2": int(q_base * 0.06), "q3": int(q_base * 0.07), "q4": int(q_base * 0.05)}
    ]

    return jsonify({
        "status": "success",
        "method_used": sim_method,
        "peak_demand": round(peak_m3_final, 0),
        "annual_demand": round(annual_m3_final, 0),
        "chart_consumption": chart_consumption,
        "chart_distribution": chart_distribution
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
