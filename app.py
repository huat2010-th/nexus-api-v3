from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# This line is CRITICAL: It allows your Vercel site to talk to this Render site safely
CORS(app) 

# 1. The "Ping" Test (To see if the server is awake)
@app.route('/', methods=['GET'])
def home():
    return "NEXUS BRAIN IS ONLINE AND WAITING FOR DATA."

# 2. The Simulation Receiver
@app.route('/simulate', methods=['POST'])
def simulate():
    # This captures the data sent by the Vercel sliders
    incoming_data = request.json
    print("Received data from Vercel:", incoming_data)
    
    # --- WE WILL PUT YOUR FULL METHOD A & B MATH HERE LATER ---
    
    # For now, we send back a fake "Success" message to test the wires
    return jsonify({
        "status": "success",
        "peak_demand": 12847,
        "annual_demand": 3420000,
        "message": "Wires successfully connected!"
    })

if __name__ == '__main__':
    # Render requires port 10000
    app.run(host='0.0.0.0', port=10000)
