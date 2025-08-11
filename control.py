from flask import Flask, jsonify, request, Response
import requests

app = Flask(__name__)

NODE_RED_URL = "http://149.157.142.59:1880/data"      # Your Node-RED data endpoint
NODE_RED_CONTROL_URL = "http://149.157.142.59:1880/control"  # Your Node-RED control endpoint

# Serve dashboard HTML with actuator buttons
@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Sensor & Actuator Dashboard</title>
      <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 2rem auto; }
        h1 { text-align: center; }
        .sensor, .controls { padding: 1rem; border: 1px solid #ccc; margin-bottom: 1rem; border-radius: 6px; }
        .label { font-weight: bold; }
        button { margin: 0.3rem; padding: 0.5rem 1rem; font-size: 1rem; }
      </style>
    </head>
    <body>
      <h1>Sensor & Actuator Dashboard</h1>

      <div class="sensor">
        <div><span class="label">Soil Moisture:</span> <span id="soil"></span></div>
        <div><span class="label">Soil Status:</span> <span id="soil_text"></span></div>
        <div><span class="label">Light (LDR):</span> <span id="ldr"></span></div>
        <div><span class="label">Temperature (°C):</span> <span id="temperature"></span></div>
        <div><span class="label">Humidity (%):</span> <span id="humidity"></span></div>
      </div>

      <div class="controls">
        <h2>Actuators</h2>
        <div>
          <button onclick="sendCommand('fan', 'on')">Fan ON</button>
          <button onclick="sendCommand('fan', 'off')">Fan OFF</button>
        </div>
        <div>
          <button onclick="sendCommand('pump', 'on')">Pump ON</button>
          <button onclick="sendCommand('pump', 'off')">Pump OFF</button>
        </div>
        <div>
          <button onclick="sendCommand('led', 'on')">LED ON</button>
          <button onclick="sendCommand('led', 'off')">LED OFF</button>
        </div>
        <div>
          <button onclick="sendCommand('buzzer', 'on')">Buzzer ON</button>
          <button onclick="sendCommand('buzzer', 'off')">Buzzer OFF</button>
        </div>
        <div>
          <button onclick="sendCommand('vent', 'open')">Vent Open</button>
          <button onclick="sendCommand('vent', 'close')">Vent Close</button>
        </div>
      </div>

      <script>
        async function fetchData() {
          try {
            const res = await fetch('/data');
            const data = await res.json();

            document.getElementById('soil').textContent = data.soil;
            document.getElementById('soil_text').textContent = data.soil_text;
            document.getElementById('ldr').textContent = data.ldr;
            document.getElementById('temperature').textContent = data.temperature;
            document.getElementById('humidity').textContent = data.humidity;
          } catch (e) {
            console.error('Failed to fetch data:', e);
          }
        }

        async function sendCommand(device, state) {
          try {
            const res = await fetch('/control', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({ device, state })
            });
            const result = await res.json();
            if(result.status === 'ok'){
              alert(`${device} turned ${state}`);
            } else {
              alert(`Error: ${result.message}`);
            }
          } catch (e) {
            alert('Failed to send command');
            console.error(e);
          }
        }

        fetchData();
        setInterval(fetchData, 3000);
      </script>
    </body>
    </html>
    """
    return Response(html, mimetype='text/html')


@app.route("/data")
def get_data():
    try:
        response = requests.get(NODE_RED_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
    except Exception:
        data = {
            "soil": 736,
            "soil_text": "Good",
            "ldr": 534,
            "temperature": 21.0,
            "humidity": 48.0
        }
    return jsonify(data)


@app.route("/control", methods=["POST"])
def control():
    data = request.json
    if not data or "device" not in data or "state" not in data:
        return jsonify({"status": "error", "message": "Invalid payload"}), 400

    try:
        response = requests.post(NODE_RED_CONTROL_URL, json=data, timeout=5)
        if response.status_code == 200:
            return jsonify({"status": "ok"})
        else:
            return jsonify({"status": "error", "message": "Node-RED error"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)


