from flask import Flask, request, jsonify
from flask_cors import CORS
import math

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "NEXUS BRAIN IS ONLINE. RUNNING V3.4 (COMPLETE DEEP SYNC)."

@app.route('/simulate', methods=['POST'])
def simulate():
    incoming_data = request.json
    sim_method = incoming_data.get('method', 'A')
    
    # ==========================================
    # METHOD A MATH 
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

        projects = [{'Category': 'Non-Hotel', 'Type': '1BR', 'Count': 236}, {'Category': 'Hotel', 'Type': 'Villa', 'Count': 6}, {'Category': 'Non-Hotel', 'Type': '2BR', 'Count': 47}, {'Category': 'Non-Hotel', 'Type': '1BR', 'Count': 139}]
        
        sum_dom_avg, sum_fnb_avg, sum_stf, sum_irr, sum_pol = 0, 0, 0, 0, 0
        sum_dom_pk, sum_fnb_pk = 0, 0

        for p in projects:
            count = p['Count']
            is_hotel = p['Category'] == 'Hotel'
            pax = count * {'1BR': 2, '2BR': 4, '3BR': 5, '4BR': 6, 'Villa': 6}.get(p['Type'], 2)
            stf_count = count * (r_hot if is_hotel else r_non)
            
            if is_hotel:
                dom, fnb, pol = pax * (h_sh + h_tl + h_ms + h_ln), pax * h_ml * h_wm, count * i_pol * (h_pe + h_pbw)
            else:
                dom, fnb, pol = pax * (n_sh + n_tl + n_ms + n_ln), pax * n_ml * n_wm, count * i_pol * (n_pe + n_pbw)
                
            stf_vol, irr_vol = (stf_count * b_stf) + (count * i_gfa * b_cool), count * i_lnd * b_irr
            
            sum_dom_avg += (dom * av_occ); sum_fnb_avg += (fnb * av_occ); sum_stf += stf_vol; sum_irr += irr_vol; sum_pol += pol
            sum_dom_pk += dom; sum_fnb_pk += fnb
            
        avg_daily_m3 = (sum_dom_avg + sum_fnb_avg + sum_stf + sum_irr + sum_pol) / 1000
        peak_m3 = (((sum_dom_pk + sum_fnb_pk) * pk_occ) + sum_stf + sum_pol + (sum_irr * irr_mult)) / 1000
        
        peak_m3_final = peak_m3 * ((1 + g_rate)**4) * (1 + nrw)
        avg_daily_final = avg_daily_m3 * ((1 + g_rate)**4) * (1 + nrw)
        annual_m3_final = avg_daily_final * 365

        total_vol = sum_dom_avg + sum_fnb_avg + sum_stf + sum_irr + sum_pol
        breakdown_data = [
            {"category": "Domestic", "value": round(sum_dom_avg/total_vol * 100, 1) if total_vol else 0},
            {"category": "F&B / Dining", "value": round(sum_fnb_avg/total_vol * 100, 1) if total_vol else 0},
            {"category": "Staff & Cooling", "value": round(sum_stf/total_vol * 100, 1) if total_vol else 0},
            {"category": "Pools", "value": round(sum_pol/total_vol * 100, 1) if total_vol else 0},
            {"category": "Irrigation", "value": round(sum_irr/total_vol * 100, 1) if total_vol else 0}
        ]

        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        chart_consumption = []
        for i, month in enumerate(months):
            seasonality = 1 + (math.sin((i / 11) * math.pi) * ((peak_m3_final - avg_daily_final) / avg_daily_final)) if avg_daily_final else 1
            demand_val = int(avg_daily_final * seasonality)
            chart_consumption.append({"month": month, "flow": int(demand_val * 1.08), "demand": demand_val})

        matrix_data = [
            {"id": 1, "zone": "Skypark 2", "category": "Condo", "actual": 236, "status": "Optimal"},
            {"id": 2, "zone": "Banyan Tree Oceanfront", "category": "Villa", "actual": 6, "status": "Optimal"},
            {"id": 3, "zone": "Lakeland Waterfront", "category": "Condo", "actual": 47, "status": "Optimal"},
            {"id": 4, "zone": "Laguna Golf Res.", "category": "Condo", "actual": 139, "status": "Optimal"}
        ]

        return jsonify({
            "status": "success", "method_used": "A", "peak_demand": round(peak_m3_final, 0), "avg_daily": round(avg_daily_final, 0), "annual_demand": round(annual_m3_final, 0),
            "chart_consumption": chart_consumption, "breakdown": breakdown_data, "matrix_data": matrix_data
        })

    # ==========================================
    # METHOD B MATH (Future Cumulative Timeline)
    # ==========================================
    elif sim_method == 'B':
        w_1bed = float(incoming_data.get('w_1bed', 1.0))
        w_2bed = float(incoming_data.get('w_2bed', 1.5))
        w_3bed = float(incoming_data.get('w_3bed', 2.0))
        w_4bed = float(incoming_data.get('w_4bed', 2.5))
        w_unspec = float(incoming_data.get('w_unspec', 1.5))
        w_sh_pool = float(incoming_data.get('w_sh_pool', 20.0))
        w_pr_pool = float(incoming_data.get('w_pr_pool', 3.0))
        
        # Exact Future Timeline from laguna_simulator-v3.py
        future_projects = [
            {"id": 1, "Year": 2026, "Project Name": "Laguna Seashore", "Type": "Condo", "1-Bed": 0, "2-Bed": 0, "3-Bed": 0, "4+ Bed": 0, "Unspec": 50, "Shared Pools": 0, "Private Pools": 0},
            {"id": 2, "Year": 2026, "Project Name": "Skypark 2", "Type": "Condo", "1-Bed": 0, "2-Bed": 0, "3-Bed": 0, "4+ Bed": 0, "Unspec": 398, "Shared Pools": 0, "Private Pools": 0},
            {"id": 3, "Year": 2026, "Project Name": "Banyan Tree Oceanfront", "Type": "Villa", "1-Bed": 0, "2-Bed": 0, "3-Bed": 0, "4+ Bed": 0, "Unspec": 10, "Shared Pools": 0, "Private Pools": 0},
            {"id": 4, "Year": 2026, "Project Name": "Sea View Residences", "Type": "Villa", "1-Bed": 0, "2-Bed": 0, "3-Bed": 0, "4+ Bed": 0, "Unspec": 40, "Shared Pools": 0, "Private Pools": 0},
            {"id": 5, "Year": 2027, "Project Name": "Lakeland Waterfront (4S)", "Type": "Condo", "1-Bed": 0, "2-Bed": 0, "3-Bed": 0, "4+ Bed": 0, "Unspec": 95, "Shared Pools": 0, "Private Pools": 0},
            {"id": 6, "Year": 2027, "Project Name": "Lakeland Waterfront (7S)", "Type": "Condo", "1-Bed": 0, "2-Bed": 0, "3-Bed": 0, "4+ Bed": 0, "Unspec": 232, "Shared Pools": 0, "Private Pools": 0},
            {"id": 7, "Year": 2027, "Project Name": "Lakeland Villa", "Type": "Villa", "1-Bed": 0, "2-Bed": 0, "3-Bed": 0, "4+ Bed": 0, "Unspec": 14, "Shared Pools": 0, "Private Pools": 0},
            {"id": 8, "Year": 2028, "Project Name": "Lakeside 2", "Type": "Condo", "1-Bed": 0, "2-Bed": 0, "3-Bed": 0, "4+ Bed": 0, "Unspec": 159, "Shared Pools": 0, "Private Pools": 0},
            {"id": 9, "Year": 2028, "Project Name": "Bayside", "Type": "Condo", "1-Bed": 0, "2-Bed": 0, "3-Bed": 0, "4+ Bed": 0, "Unspec": 237, "Shared Pools": 0, "Private Pools": 0},
            {"id": 10, "Year": 2029, "Project Name": "Skypark Elara", "Type": "Condo", "1-Bed": 0, "2-Bed": 0, "3-Bed": 0, "4+ Bed": 0, "Unspec": 234, "Shared Pools": 0, "Private Pools": 0},
            {"id": 11, "Year": 2029, "Project Name": "Garrya Residences", "Type": "Condo", "1-Bed": 0, "2-Bed": 0, "3-Bed": 0, "4+ Bed": 0, "Unspec": 25, "Shared Pools": 0, "Private Pools": 0},
            {"id": 12, "Year": 2030, "Project Name": "Laguna Golf Residences", "Type": "Condo", "1-Bed": 0, "2-Bed": 0, "3-Bed": 0, "4+ Bed": 0, "Unspec": 179, "Shared Pools": 0, "Private Pools": 0},
            {"id": 13, "Year": 2030, "Project Name": "Lotus Lake Condo", "Type": "Condo", "1-Bed": 0, "2-Bed": 0, "3-Bed": 0, "4+ Bed": 0, "Unspec": 319, "Shared Pools": 0, "Private Pools": 0}
        ]
        # Add 2031 to 2050 Planning
        for y in range(2031, 2041):
            future_projects.append({"id": len(future_projects)+1, "Year": y, "Project Name": "Future Planning", "Type": "Condo", "1-Bed": 0, "2-Bed": 0, "3-Bed": 0, "4+ Bed": 0, "Unspec": 200, "Shared Pools": 0, "Private Pools": 0})
            future_projects.append({"id": len(future_projects)+1, "Year": y, "Project Name": "Future Planning", "Type": "Villa", "1-Bed": 0, "2-Bed": 0, "3-Bed": 0, "4+ Bed": 0, "Unspec": 40, "Shared Pools": 0, "Private Pools": 0})
        
        yearly_data = {}
        for p in future_projects:
            # Calculate Equivalents
            eq_u = (p['1-Bed']*w_1bed) + (p['2-Bed']*w_2bed) + (p['3-Bed']*w_3bed) + (p['4+ Bed']*w_4bed) + (p['Unspec']*w_unspec)
            eq_p = (p['Shared Pools']*w_sh_pool) + (p['Private Pools']*w_pr_pool)
            
            p_avg = (eq_u + eq_p) * 1.8 
            p_pk = (eq_u + eq_p) * 2.2
            
            y = p['Year']
            if y not in yearly_data:
                yearly_data[y] = {"avg": 0, "peak": 0, "condo_avg": 0, "villa_avg": 0}
            yearly_data[y]["avg"] += p_avg
            yearly_data[y]["peak"] += p_pk
            if p['Type'] == 'Condo':
                yearly_data[y]["condo_avg"] += p_avg
            else:
                yearly_data[y]["villa_avg"] += p_avg
                
        # Build Cumulative Chart Data
        sorted_years = sorted(yearly_data.keys())
        cum_chart = []
        type_chart = []
        cum_avg, cum_peak = 0, 0
        
        for y in sorted_years:
            cum_avg += yearly_data[y]["avg"]
            cum_peak += yearly_data[y]["peak"]
            cum_chart.append({"year": str(y), "New Avg": int(cum_avg), "New Peak": int(cum_peak)})
            type_chart.append({"year": str(y), "Condo": int(yearly_data[y]["condo_avg"]), "Villa": int(yearly_data[y]["villa_avg"])})

        return jsonify({
            "status": "success", "method_used": "B", "peak_demand": round(cum_peak, 0), "avg_daily": round(cum_avg, 0), "annual_demand": round(cum_avg*365, 0),
            "cum_chart": cum_chart, "type_chart": type_chart, "matrix_data": future_projects
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
