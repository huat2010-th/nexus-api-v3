from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import math

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "NEXUS BRAIN IS ONLINE. V5.0 (FINAL SYNC - DYNAMIC MATRICES)."

@app.route('/simulate', methods=['POST'])
def simulate():
    incoming_data = request.json
    sim_method = incoming_data.get('method', 'A')
    
    # ==========================================
    # METHOD A: TIME-SERIES COMPONENT MATH
    # ==========================================
    if sim_method == 'A':
        h_sh, h_tl, h_ms, h_ln = float(incoming_data.get('h_shower', 120)), float(incoming_data.get('h_toilet', 45)), float(incoming_data.get('h_misc', 40)), float(incoming_data.get('h_laundry', 60))
        h_ml, h_wm = float(incoming_data.get('h_meals', 2.5)), float(incoming_data.get('h_water_meal', 25))
        h_pe, h_pbw = float(incoming_data.get('h_pool_evap', 10)), float(incoming_data.get('h_pool_bw', 5))

        n_sh, n_tl, n_ms, n_ln = float(incoming_data.get('n_shower', 90)), float(incoming_data.get('n_toilet', 40)), float(incoming_data.get('n_misc', 30)), float(incoming_data.get('n_laundry', 25))
        n_ml, n_wm = float(incoming_data.get('n_meals', 0.2)), float(incoming_data.get('n_water_meal', 20))
        n_pe, n_pbw = float(incoming_data.get('n_pool_evap', 10)), float(incoming_data.get('n_pool_bw', 5))

        b_cool, b_irr, b_stf = float(incoming_data.get('b_cooling', 2.0)), float(incoming_data.get('b_irrigation', 5.0)), float(incoming_data.get('b_staff', 100.0))
        r_hot, r_non = float(incoming_data.get('ratio_hotel', 1.2)), float(incoming_data.get('ratio_non', 0.2))
        i_pol, i_lnd, i_gfa = float(incoming_data.get('inf_pool', 3.0)), float(incoming_data.get('inf_land', 20.0)), float(incoming_data.get('inf_gfa', 120.0))

        pk_occ, av_occ = float(incoming_data.get('peak_occ', 90))/100.0, float(incoming_data.get('avg_occ', 65))/100.0
        irr_mult, g_rate, nrw = float(incoming_data.get('irr_peak_mult', 1.5)), float(incoming_data.get('growth_rate', 3.5))/100.0, float(incoming_data.get('nrw_loss', 10.0))/100.0

        # FETCH DYNAMIC TABLE FROM FRONTEND
        projects_a = incoming_data.get('matrix_a', [])
        
        if not projects_a:
            return jsonify({"status": "error", "message": "No project data provided."})

        # Find timeline range safely
        years = [int(p.get('Year', 2026)) for p in projects_a]
        start_year = min(years) if years else 2026
        end_year = max(years) + 10 if years else 2036
        
        chart_consumption = []
        bd_dom, bd_fnb, bd_stf, bd_irr, bd_pol = 0, 0, 0, 0, 0
        final_peak, final_avg, final_ann = 0, 0, 0

        # Run multi-year cumulative engine
        for y in range(start_year, end_year + 1):
            active = [p for p in projects_a if int(p.get('Year', 2026)) <= y]
            s_dom_pk, s_fnb_pk, s_dom_av, s_fnb_av, s_stf, s_irr, s_pol = 0,0,0,0,0,0,0
            
            for p in active:
                count = int(p.get('Count', 0))
                is_hotel = p.get('Category', 'Non-Hotel') == 'Hotel'
                pax = count * {'1BR': 2, '2BR': 4, '3BR': 5, '4BR': 6, '5BR': 8, 'Villa': 6}.get(p.get('Type', '1BR'), 2)
                stf_count = count * (r_hot if is_hotel else r_non)
                
                dom = pax * ((h_sh + h_tl + h_ms + h_ln) if is_hotel else (n_sh + n_tl + n_ms + n_ln))
                fnb = pax * ((h_ml * h_wm) if is_hotel else (n_ml * n_wm))
                pol = count * i_pol * ((h_pe + h_pbw) if is_hotel else (n_pe + n_pbw))
                
                s_dom_pk += dom; s_fnb_pk += fnb
                s_dom_av += (dom * av_occ); s_fnb_av += (fnb * av_occ)
                s_stf += (stf_count * b_stf) + (count * i_gfa * b_cool)
                s_irr += (count * i_lnd * b_irr)
                s_pol += pol

            g_fac, n_fac = (1 + g_rate)**(y - start_year), (1 + nrw)
            
            avg_m3 = ((s_dom_av + s_fnb_av + s_stf + s_irr + s_pol) * g_fac * n_fac) / 1000
            peak_m3 = ((((s_dom_pk + s_fnb_pk)*pk_occ) + s_stf + s_pol + (s_irr*irr_mult)) * g_fac * n_fac) / 1000
            
            chart_consumption.append({"year": str(y), "Average": round(avg_m3,0), "Peak": round(peak_m3,0)})
            
            if y == end_year:
                final_peak, final_avg, final_ann = peak_m3, avg_m3, avg_m3 * 365
                total_vol = s_dom_av + s_fnb_av + s_stf + s_irr + s_pol
                if total_vol > 0:
                    bd_dom, bd_fnb, bd_stf, bd_irr, bd_pol = (s_dom_av/total_vol)*100, (s_fnb_av/total_vol)*100, (s_stf/total_vol)*100, (s_irr/total_vol)*100, (s_pol/total_vol)*100

        breakdown_data = [
            {"category": "Domestic", "value": round(bd_dom, 1)}, {"category": "F&B / Dining", "value": round(bd_fnb, 1)},
            {"category": "Staff/Cooling", "value": round(bd_stf, 1)}, {"category": "Pools", "value": round(bd_pol, 1)}, {"category": "Irrigation", "value": round(bd_irr, 1)}
        ]

        return jsonify({"status": "success", "method_used": "A", "peak_demand": round(final_peak, 0), "avg_daily": round(final_avg, 0), "annual_demand": round(final_ann, 0), "chart_consumption": chart_consumption, "breakdown": breakdown_data})

    # ==========================================
    # METHOD B: DYNAMIC INFERENCE + FUTURE CUMULATIVE
    # ==========================================
    elif sim_method == 'B':
        w_weights = {
            '1-Bed': float(incoming_data.get('w_1bed', 1.0)), '2-Bed': float(incoming_data.get('w_2bed', 1.5)),
            '3-Bed': float(incoming_data.get('w_3bed', 2.0)), '4+ Bed': float(incoming_data.get('w_4bed', 2.5)),
            'Unspec': float(incoming_data.get('w_unspec', 1.5)), 'Sh_Pool': float(incoming_data.get('w_sh_pool', 20.0)),
            'Pr_Pool': float(incoming_data.get('w_pr_pool', 3.0))
        }
        
        # 1. Dynamic Inference from 25 Existing Properties (Internal Baseline)
        baselines = [
            {"Type": "Villa", "1-Bed":0,"2-Bed":0,"3-Bed":0,"4+ Bed":0,"Unspec":24,"Sh_Pool":0,"Pr_Pool":0,"Ann":14865,"Pk":1743},
            {"Type": "Condo", "1-Bed":0,"2-Bed":0,"3-Bed":0,"4+ Bed":0,"Unspec":193,"Sh_Pool":0,"Pr_Pool":0,"Ann":16372,"Pk":2210},
            {"Type": "Condo", "1-Bed":0,"2-Bed":0,"3-Bed":0,"4+ Bed":0,"Unspec":184,"Sh_Pool":0,"Pr_Pool":0,"Ann":16922,"Pk":1410},
            {"Type": "Condo", "1-Bed":0,"2-Bed":0,"3-Bed":0,"4+ Bed":0,"Unspec":416,"Sh_Pool":0,"Pr_Pool":0,"Ann":28017,"Pk":4047},
            {"Type": "Villa", "1-Bed":0,"2-Bed":0,"3-Bed":0,"4+ Bed":0,"Unspec":56,"Sh_Pool":0,"Pr_Pool":0,"Ann":51827,"Pk":6552},
            {"Type": "Villa", "1-Bed":0,"2-Bed":0,"3-Bed":0,"4+ Bed":0,"Unspec":36,"Sh_Pool":0,"Pr_Pool":0,"Ann":36782,"Pk":4409}
        ] 
        
        def get_rates(b_type):
            av, pk = [], []
            for b in [x for x in baselines if x["Type"] == b_type]:
                eq = sum(b[k]*w_weights[k] for k in w_weights.keys() if k in b)
                if eq > 0:
                    av.append((b["Ann"]/eq)/365)
                    pk.append((b["Pk"]/eq)/31)
            return np.mean(av) if av else 1.8, np.mean(pk) if pk else 2.2
            
        c_av, c_pk = get_rates("Condo")
        v_av, v_pk = get_rates("Villa")

        # 2. Apply to Future Custom Matrix from UI
        future = incoming_data.get('matrix_b', [])
        
        y_data = {}
        for p in future:
            # Safely get values
            u_1b, u_2b, u_3b, u_4b = int(p.get('1-Bed',0)), int(p.get('2-Bed',0)), int(p.get('3-Bed',0)), int(p.get('4+ Bed',0))
            u_uns, p_sh, p_pr = int(p.get('Unspec',0)), int(p.get('Sh Pool',0)), int(p.get('Pr Pool',0))
            
            eq = (u_1b*w_weights['1-Bed']) + (u_2b*w_weights['2-Bed']) + (u_3b*w_weights['3-Bed']) + (u_4b*w_weights['4+ Bed']) + (u_uns*w_weights['Unspec']) + (p_sh*w_weights['Sh_Pool']) + (p_pr*w_weights['Pr_Pool'])
            
            p_av = eq * (c_av if p.get('Type')=="Condo" else v_av)
            p_pk = eq * (c_pk if p.get('Type')=="Condo" else v_pk)
            
            y = int(p.get('Year', 2026))
            if y not in y_data: y_data[y] = {"av": 0, "pk": 0, "c_av": 0, "v_av": 0}
            y_data[y]["av"] += p_av; y_data[y]["pk"] += p_pk
            if p.get('Type') == 'Condo': y_data[y]["c_av"] += p_av 
            else: y_data[y]["v_av"] += p_av
                
        cum_chart, type_chart = [], []
        cum_av, cum_pk = 0, 0
        for y in sorted(y_data.keys()):
            cum_av += y_data[y]["av"]; cum_pk += y_data[y]["pk"]
            cum_chart.append({"year": str(y), "New Avg": int(cum_av), "New Peak": int(cum_pk)})
            type_chart.append({"year": str(y), "Condo": int(y_data[y]["c_av"]), "Villa": int(y_data[y]["v_av"])})

        return jsonify({"status": "success", "method_used": "B", "peak_demand": round(cum_pk, 0), "avg_daily": round(cum_av, 0), "annual_demand": round(cum_av*365, 0), "cum_chart": cum_chart, "type_chart": type_chart})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
