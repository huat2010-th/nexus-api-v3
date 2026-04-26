from flask import Flask, request, jsonify
from flask_cors import CORS
import math

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "NEXUS BRAIN IS ONLINE. RUNNING V3.3 (FINAL DEEP SYNC)."

@app.route('/simulate', methods=['POST'])
def simulate():
    incoming_data = request.json
    sim_method = incoming_data.get('method', 'A')
    
    peak_m3_final = 0
    annual_m3_final = 0
    avg_daily_final = 0
    breakdown_data = []
    
    # ==========================================
    # METHOD A MATH
    # ==========================================
    if sim_method == 'A':
        h_sh = float(incoming_data.get('h_shower', 120))
        h_tl = float(incoming_data.get('h_toilet', 45))
        h_ms = float(incoming_data.get('h_misc', 40))
        h_ln = float(incoming_data.get('h_laundry', 60))
        h_ml = float(incoming_data.get('h_meals', 2.5))
        h_wm = float(incoming_data.get('h_water_meal', 25))
        h_pe = float(incoming_data.get('h_pool_evap', 10))
        h_pbw = float(incoming_data.get('h_pool_bw', 5))

        n_sh = float(incoming_data.get('n_shower', 90))
        n_tl = float(incoming_data.get('n_toilet', 40))
        n_ms = float(incoming_data.get('n_misc', 30))
        n_ln = float(incoming_data.get('n_laundry', 25))
        n_ml = float(incoming_data.get('n_meals', 0.2))
        n_wm = float(incoming_data.get('n_water_meal', 20))
        n_pe = float(incoming_data.get('n_pool_evap', 10))
        n_pbw = float(incoming_data.get('n_pool_bw', 5))

        b_cool = float(incoming_data.get('b_cooling', 2.0))
        b_irr = float(incoming_data.get('b_irrigation', 5.0))
        b_stf = float(incoming_data.get('b_staff', 100.0))
        r_hot = float(incoming_data.get('ratio_hotel', 1.2))
        r_non = float(incoming_data.get('ratio_non', 0.2))
        i_pol = float(incoming_data.get('inf_pool', 3.0))
        i_lnd = float(incoming_data.get('inf_land', 20.0))
        i_gfa = float(incoming_data.get('inf_gfa', 120.0))

        pk_occ = float(incoming_data.get('peak_occ', 90)) / 100.0
        av_occ = float(incoming_data.get('avg_occ', 65)) / 100.0
        irr_mult = float(incoming_data.get('irr_peak_mult', 1.5))
        g_rate = float(incoming_data.get('growth_rate', 3.5)) / 100.0
        nrw = float(incoming_data.get('nrw_loss', 10.0)) / 100.0

        projects = [
            {'Category': 'Non-Hotel', 'Type': '1BR', 'Count': 236},
            {'Category': 'Hotel', 'Type': 'Villa', 'Count': 6},
            {'Category': 'Non-Hotel', 'Type': '2BR', 'Count': 47},
            {'Category': 'Non-Hotel', 'Type': '1BR', 'Count': 139}
        ]
        
        sum_dom_avg, sum_fnb_avg, sum_stf, sum_irr, sum_pol = 0, 0, 0, 0, 0
        sum_dom_pk, sum_fnb_pk = 0, 0

        for p in projects:
            count = p['Count']
            is_hotel = p['Category'] == 'Hotel'
            pax = count * {'1BR': 2, '2BR': 4, '3BR': 5, '4BR': 6, 'Villa': 6}.get(p['Type'], 2)
            stf_count = count * (r_hot if is_hotel else r_non)
            
            if is_hotel:
                dom = pax * (h_sh + h_tl + h_ms + h_ln)
                fnb = pax * h_ml * h_wm
                pol = count * i_pol * (h_pe + h_pbw)
            else:
                dom = pax * (n_sh + n_tl + n_ms + n_ln)
                fnb = pax * n_ml * n_wm
                pol = count * i_pol * (n_pe + n_pbw)
                
            stf_vol = (stf_count * b_stf) + (count * i_gfa * b_cool)
            irr_vol = count * i_lnd * b_irr
            
            sum_dom_avg += (dom * av_occ)
            sum_fnb_avg += (fnb * av_occ)
            sum_stf += stf_vol
            sum_irr += irr_vol
            sum_pol += pol
            sum_dom_pk += dom
            sum_fnb_pk += fnb
            
        avg_daily_m3 = (sum_dom_avg + sum_fnb_avg + sum_stf + sum_irr + sum_pol) / 1000
        peak_m3 = (((sum_dom_pk + sum_fnb_pk) * pk_occ) + sum_stf + sum_pol + (sum_irr * irr_mult)) / 1000
        
        g_factor = (1 + g_rate) ** 4 
        n_factor = 1 + nrw
        
        peak_m3_final = peak_m3 * g_factor * n_factor
        avg_daily_final = avg_daily_m3 * g_factor * n_factor
        annual_m3_final = avg_daily_final * 365

        total_vol = sum_dom_avg + sum_fnb_avg + sum_stf + sum_irr + sum_pol
        breakdown_data = [
            {"category": "Domestic", "value": round(sum_dom_avg/total_vol * 100, 1) if total_vol else 0},
            {"category": "F&B / Dining", "value": round(sum_fnb_avg/total_vol * 100, 1) if total_vol else 0},
            {"category": "Staff & Cooling", "value": round(sum_stf/total_vol * 100, 1) if total_vol else 0},
            {"category": "Pools", "value": round(sum_pol/total_vol * 100, 1) if total_vol else 0},
            {"category": "Irrigation", "value": round(sum_irr/total_vol * 100, 1) if total_vol else 0}
        ]

    # ==========================================
    # METHOD B MATH (Smart Inference Weights)
    # ==========================================
    elif sim_method == 'B':
        # Counts
        c_1bed = float(incoming_data.get('c_1bed', 0))
        c_2bed = float(incoming_data.get('c_2bed', 0))
        c_3bed = float(incoming_data.get('c_3bed', 0))
        c_4bed = float(incoming_data.get('c_4bed', 0))
        c_unspec = float(incoming_data.get('c_unspec', 120))
        c_sh_pool = float(incoming_data.get('c_sh_pool', 8))
        c_pr_pool = float(incoming_data.get('c_pr_pool', 0))
        
        # Weights
        w_1bed = float(incoming_data.get('w_1bed', 1.0))
        w_2bed = float(incoming_data.get('w_2bed', 1.5))
        w_3bed = float(incoming_data.get('w_3bed', 2.0))
        w_4bed = float(incoming_data.get('w_4bed', 2.5))
        w_unspec = float(incoming_data.get('w_unspec', 1.5))
        w_sh_pool = float(incoming_data.get('w_sh_pool', 20.0))
        w_pr_pool = float(incoming_data.get('w_pr_pool', 3.0))

        # Calculate Total Equivalent Units
        eq_units = (c_1bed * w_1bed) + (c_2bed * w_2bed) + (c_3bed * w_3bed) + (c_4bed * w_4bed) + (c_unspec * w_unspec)
        eq_pools = (c_sh_pool * w_sh_pool) + (c_pr_pool * w_pr_pool)
        total_eq = eq_units + eq_pools
        
        # Base Rates per Equivalent Unit (Derived from Laguna baselines)
        avg_daily = total_eq * 1.8 
        peak_daily = total_eq * 2.2
        
        g_factor = (1 + 0.035) ** 4 
        n_factor = 1 + 0.10
        
        peak_m3_final = peak_daily * g_factor * n_factor
        avg_daily_final = avg_daily * g_factor * n_factor
        annual_m3_final = avg_daily_final * 365

        breakdown_data = [
            {"category": "Housing Eq. Volume", "value": round((eq_units/total_eq)*100, 1) if total_eq else 0},
            {"category": "Pool Eq. Volume", "value": round((eq_pools/total_eq)*100, 1) if total_eq else 0}
        ]

    # Shared Chart Generation
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    chart_consumption = []
    for i, month in enumerate(months):
        seasonality = 1 + (math.sin((i / 11) * math.pi) * ((peak_m3_final - avg_daily_final) / avg_daily_final)) if avg_daily_final else 1
        demand_val = int(avg_daily_final * seasonality)
        chart_consumption.append({"month": month, "flow": int(demand_val * 1.08), "demand": demand_val})

    matrix_data = [
        {"id": 1, "zone": "Skypark 2", "category": "Condo", "baseline": 236, "actual": 236, "variance": 0.0, "status": "Optimal"},
        {"id": 2, "zone": "Banyan Tree Oceanfront", "category": "Villa", "baseline": 6, "actual": 6, "variance": 0.0, "status": "Optimal"},
        {"id": 3, "zone": "Lakeland Waterfront", "category": "Condo", "baseline": 47, "actual": 47, "variance": 0.0, "status": "Optimal"},
        {"id": 4, "zone": "Laguna Golf Res.", "category": "Condo", "baseline": 139, "actual": 139, "variance": 0.0, "status": "Optimal"}
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
