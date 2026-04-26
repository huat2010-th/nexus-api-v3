from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import math

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "NEXUS BRAIN IS ONLINE. V6.1 (ORGANIC GROWTH ENGINE)."

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

        projects_a = incoming_data.get('matrix_a', [])
        if not projects_a: return jsonify({"status": "error", "message": "No project data."})

        years = [int(p.get('Year', 2026)) for p in projects_a]
        start_year, end_year = min(years) if years else 2026, (max(years) + 10 if years else 2036)
        
        chart_consumption, table_a_results = [], []
        bd_dom, bd_fnb, bd_stf, bd_irr, bd_pol = 0, 0, 0, 0, 0
        final_peak, final_avg, final_ann = 0, 0, 0

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
            
            chart_consumption.append({"year": str(y), "Average": round(avg_m3,0), "Peak (Jan)": round(peak_m3,0)})
            
            bd_factor = (g_fac * n_fac) / 1000
            table_a_results.append({
                "Year": y, "Daily Peak (m3/day)": round(peak_m3, 2), "Daily Avg (m3/day)": round(avg_m3, 2),
                "Annual Total (m3/year)": round(avg_m3 * 365, 0), "Domestic (Avg m3/d)": round(s_dom_av * bd_factor, 1),
                "Irrigation (Avg m3/d)": round(s_irr * bd_factor, 1), "Pools (Avg m3/d)": round(s_pol * bd_factor, 1)
            })
            
            if y == end_year:
                final_peak, final_avg, final_ann = peak_m3, avg_m3, avg_m3 * 365
                total_vol = s_dom_av + s_fnb_av + s_stf + s_irr + s_pol
                if total_vol > 0:
                    bd_dom, bd_fnb, bd_stf, bd_irr, bd_pol = (s_dom_av/total_vol)*100, (s_fnb_av/total_vol)*100, (s_stf/total_vol)*100, (s_irr/total_vol)*100, (s_pol/total_vol)*100

        breakdown_data = [{"category": "Domestic", "value": round(bd_dom, 1)}, {"category": "F&B / Dining", "value": round(bd_fnb, 1)}, {"category": "Staff/Cooling", "value": round(bd_stf, 1)}, {"category": "Pools", "value": round(bd_pol, 1)}, {"category": "Irrigation", "value": round(bd_irr, 1)}]

        return jsonify({"status": "success", "method_used": "A", "peak_demand": round(final_peak, 0), "avg_daily": round(final_avg, 0), "annual_demand": round(final_ann, 0), "chart_consumption": chart_consumption, "breakdown": breakdown_data, "table_a_results": table_a_results})

    # ==========================================
    # METHOD B: DYNAMIC INFERENCE + ORGANIC GROWTH
    # ==========================================
    elif sim_method == 'B':
        w_weights = {
            '1-Bed': float(incoming_data.get('w_1bed', 1.0)), '2-Bed': float(incoming_data.get('w_2bed', 1.5)),
            '3-Bed': float(incoming_data.get('w_3bed', 2.0)), '4+ Bed': float(incoming_data.get('w_4bed', 2.5)),
            'Unspec': float(incoming_data.get('w_unspec', 1.5)), 'Sh Pool': float(incoming_data.get('w_sh_pool', 20.0)),
            'Pr Pool': float(incoming_data.get('w_pr_pool', 3.0))
        }
        
        b_growth_rate = float(incoming_data.get('b_growth_rate', 1.5)) / 100.0
        
        matrix_baseline = incoming_data.get('matrix_b_baseline', [])
        matrix_future = incoming_data.get('matrix_b_future', [])
        
        # Calculate Total Baseline Volume (Before new projects)
        base_total_av = sum(float(b.get("Ann", 0)) for b in matrix_baseline) / 365 if matrix_baseline else 0
        base_total_pk = sum(float(b.get("Pk", 0)) for b in matrix_baseline) / 31 if matrix_baseline else 0
        
        def get_rates(b_type):
            av, pk = [], []
            for b in [x for x in matrix_baseline if x.get("Type") == b_type]:
                eq = sum(float(b.get(k, 0))*w_weights[k] for k in w_weights.keys() if k in b)
                if eq > 0:
                    av.append((float(b.get("Ann", 0))/eq)/365)
                    pk.append((float(b.get("Pk", 0))/eq)/31)
            return np.mean(av) if av else 1.8, np.mean(pk) if pk else 2.2
            
        c_av, c_pk = get_rates("Condo")
        v_av, v_pk = get_rates("Villa")

        y_data = {}
        indiv_proj = []
        for p in matrix_future:
            u_1b, u_2b, u_3b, u_4b = float(p.get('1-Bed',0)), float(p.get('2-Bed',0)), float(p.get('3-Bed',0)), float(p.get('4+ Bed',0))
            u_uns, p_sh, p_pr = float(p.get('Unspec',0)), float(p.get('Sh Pool',0)), float(p.get('Pr Pool',0))
            
            eq = (u_1b*w_weights['1-Bed']) + (u_2b*w_weights['2-Bed']) + (u_3b*w_weights['3-Bed']) + (u_4b*w_weights['4+ Bed']) + (u_uns*w_weights['Unspec']) + (p_sh*w_weights['Sh Pool']) + (p_pr*w_weights['Pr Pool'])
            
            p_av = eq * (c_av if p.get('Type')=="Condo" else v_av)
            p_pk = eq * (c_pk if p.get('Type')=="Condo" else v_pk)
            
            y = int(p.get('Year', 2026))
            if y not in y_data: y_data[y] = {"new_av": 0, "new_pk": 0, "c_av": 0, "v_av": 0}
            y_data[y]["new_av"] += p_av; y_data[y]["new_pk"] += p_pk
            if p.get('Type') == 'Condo': y_data[y]["c_av"] += p_av 
            else: y_data[y]["v_av"] += p_av
            
            indiv_proj.append({
                "Year": y, "Project": p.get('Project Name', ''), "Type": p.get('Type', ''),
                "Total Units": sum([u_1b, u_2b, u_3b, u_4b, u_uns]), "Avg Daily (m3/d)": round(p_av, 1),
                "Peak Daily (m3/d)": round(p_pk, 1), "Ann Total (m3/y)": round(p_av*365, 0)
            })
                
        # Combine Baseline Organic Growth + Cumulative New Projects
        years = [int(p.get('Year', 2026)) for p in matrix_future]
        start_y = min(years) if years else 2026
        end_y = max(years) if years else 2050
        if end_y < 2050: end_y = 2050 

        cum_chart, type_chart, table_cum = [], [], []
        cum_new_av, cum_new_pk = 0, 0
        final_av, final_pk = 0, 0
        
        for y in range(start_y, end_y + 1):
            if y in y_data:
                cum_new_av += y_data[y]["new_av"]
                cum_new_pk += y_data[y]["new_pk"]
                type_chart.append({"year": str(y), "Condo": int(y_data[y]["c_av"]), "Villa": int(y_data[y]["v_av"])})
            else:
                type_chart.append({"year": str(y), "Condo": 0, "Villa": 0})
            
            # Organic Growth applied to Baseline properties
            grown_base_av = base_total_av * ((1 + b_growth_rate) ** (y - start_y))
            grown_base_pk = base_total_pk * ((1 + b_growth_rate) ** (y - start_y))
            
            total_av = grown_base_av + cum_new_av
            total_pk = grown_base_pk + cum_new_pk
            
            cum_chart.append({
                "year": str(y), 
                "Baseline (Organic)": int(grown_base_av),
                "New Projects": int(cum_new_av),
                "Total Peak (Jan)": int(total_pk)
            })
            
            table_cum.append({
                "Year": y, 
                "Baseline Organic Avg": round(grown_base_av, 1),
                "New Projects Avg": round(cum_new_av, 1), 
                "Total Avg Daily": round(total_av, 1), 
                "Total Peak (Jan)": round(total_pk, 1)
            })
            
            if y == end_y:
                final_av = total_av
                final_pk = total_pk

        return jsonify({"status": "success", "method_used": "B", "peak_demand": round(final_pk, 0), "avg_daily": round(final_av, 0), "annual_demand": round(final_av*365, 0), "cum_chart": cum_chart, "type_chart": type_chart, "table_b_individual": indiv_proj, "table_b_cum": table_cum})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
