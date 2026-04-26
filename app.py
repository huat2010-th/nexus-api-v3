from flask import Flask, request, jsonify
from flask_cors import CORS
import math

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "NEXUS BRAIN IS ONLINE. RUNNING V3.2 (PHASE 1 - DEEP SYNC)."

@app.route('/simulate', methods=['POST'])
def simulate():
    incoming_data = request.json
    sim_method = incoming_data.get('method', 'A')
    
    peak_m3_final = 0
    annual_m3_final = 0
    breakdown_data = []
    
    # ==========================================
    # METHOD A MATH (With Component Breakdown)
    # ==========================================
    if sim_method == 'A':
        v_sh = float(incoming_data.get('shower', 120))
        v_tl = float(incoming_data.get('toilet', 40))
        v_ln = float(incoming_data.get('laundry', 25))
        v_ml = float(incoming_data.get('meals', 3.0))
        occ_rate = float(incoming_data.get('occupancy', 85)) / 100.0
        
        # Base Engineering Params (We will make these sliders in Phase 2)
        b_cooling = 2.0
        b_irrigation = 5.0
        b_staff = 100.0
        inf_pool = 3.0
        inf_land = 20.0
        inf_gfa = 120.0

        projects = [
            {'Category': 'Non-Hotel', 'Type': '1BR', 'Count': 236},
            {'Category': 'Hotel', 'Type': 'Villa', 'Count': 6},
            {'Category': 'Non-Hotel', 'Type': '2BR', 'Count': 47},
            {'Category': 'Non-Hotel', 'Type': '1BR', 'Count': 139}
        ]
        
        sum_dom, sum_fnb, sum_stf, sum_irr, sum_pol = 0, 0, 0, 0, 0
        
        for p in projects:
            count = p['Count']
            is_hotel = p['Category'] == 'Hotel'
            pax = count * {'1BR': 2, '2BR': 4, '3BR': 5, '4BR': 6, 'Villa': 6}.get(p['Type'], 2)
            total_staff = count * (1.2 if is_hotel else 0.2)
            
            # Sub-calculations per component
            dom = pax * (v_sh + v_tl + (40 if is_hotel else 30) + v_ln)
            fnb = pax * v_ml * (25 if is_hotel else 20)
            stf = (total_staff * b_staff) + (count * inf_gfa * b_cooling)
            irr = count * inf_land * b_irrigation
            pol = count * inf_pool * (10 + 5)
            
            sum_dom += (dom * occ_rate)
            sum_fnb += (fnb * occ_rate)
            sum_stf += stf
            sum_irr += irr
            sum_pol += pol
            
        avg_daily_m3 = (sum_dom + sum_fnb + sum_stf + sum_irr + sum_pol) / 1000
        peak_m3 = (((sum_dom + sum_fnb)/occ_rate * 0.90) + sum_stf + sum_pol + (sum_irr * 1.5)) / 1000
        
        growth_factor = (1 + 0.035) ** 4 
        peak_m3_final = peak_m3 * growth_factor * 1.10
        annual_m3_final = (avg_daily_m3 * 365) * growth_factor * 1.10

        # Create percentage breakdown for the UI Chart
        total_vol = sum_dom + sum_fnb + sum_stf + sum_irr + sum_pol
        breakdown_data = [
            {"category": "Domestic", "value": round(sum_dom/total_vol * 100, 1)},
            {"category": "F&B / Dining", "value": round(sum_fnb/total_vol * 100, 1)},
            {"category": "Staff & Cooling", "value": round(sum_stf/total_vol * 100, 1)},
            {"category": "Pools", "value": round(sum_pol/total_vol * 100, 1)},
            {"category": "Irrigation", "value": round(sum_irr/total_vol * 100, 1)}
        ]

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

        breakdown_data = [
            {"category": "Housing Units", "value": round(((units * 1.8)/avg_daily) * 100, 1)},
            {"category": "Pool Equivalents", "value": round(((pools * 15.0)/avg_daily) * 100, 1)}
        ]

    # Shared Chart Logic
    avg_daily_final = annual_m3_final / 365
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    chart_consumption = []
    for i, month in enumerate(months):
        seasonality = 1 + (math.sin((i / 11) * math.pi) * ((peak_m3_final - avg_daily_final) / avg_daily_final))
        demand_val = int(avg_daily_final * seasonality)
        chart_consumption.append({"month": month, "flow": int(demand_val * 1.08), "demand": demand_val})

    matrix_data = [
        {"id": 1, "zone": "Skypark 2", "category": "Condo", "baseline": 236, "actual": 236, "variance": 0.0, "status": "Optimal"},
        {"id": 2, "zone": "Banyan Tree Oceanfront", "category": "Villa", "baseline": 6, "actual": 6, "variance": 0.0, "status": "Optimal"},
        {"id": 3, "zone": "Lakeland Waterfront", "category": "Condo", "baseline": 47, "actual": 47, "variance": 0.0, "status": "Optimal"},
        {"id": 4, "zone": "Laguna Golf Res.", "category": "Condo", "baseline": 139, "actual": 139, "variance": 0.0, "status": "Optimal"},
        {"id": 5, "zone": "Laguna Fairway", "category": "Villa", "baseline": 24, "actual": 24, "variance": 0.0, "status": "Optimal"},
        {"id": 6, "zone": "Cassia Residence", "category": "Condo", "baseline": 193, "actual": 193, "variance": 0.0, "status": "Optimal"},
        {"id": 7, "zone": "Beachside", "category": "Condo", "baseline": 184, "actual": 184, "variance": 0.0, "status": "Optimal"},
        {"id": 8, "zone": "Laguna Village (LVR)", "category": "Villa", "baseline": 95, "actual": 95, "variance": 0.0, "status": "Optimal"},
    ]

    return jsonify({
        "status": "success",
        "method_used": sim_method,
        "peak_demand": round(peak_m3_final, 0),
        "avg_daily": round(avg_daily_final, 0),
        "annual_demand": round(annual_m3_final, 0),
        "chart_consumption": chart_consumption,
        "breakdown": breakdown_data,
        "matrix_data": matrix_data
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
