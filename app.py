from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Sunucuda saklanan geçici veriler (Serverless yapıda kalıcı değildir)
current_command = ""
execution_logs = []

HTML_PAGE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Delta Uzaktan Kontrol Paneli</title>
    <style>
        body { background-color: #121212; color: #e0e0e0; font-family: monospace; padding: 20px; }
        textarea { width: 100%; height: 150px; background: #1e1e1e; color: #fff; border: 1px solid #333; padding: 10px; font-size: 14px; }
        button { background: #4CAF50; color: white; border: none; padding: 10px 20px; cursor: pointer; font-size: 14px; margin-right: 10px; margin-top: 10px; }
        button.clear { background: #f44336; }
        pre { background: #1e1e1e; padding: 15px; border: 1px solid #333; height: 300px; overflow-y: scroll; }
    </style>
</head>
<body>
    <h2>Delta Roblox Uzaktan Yonetim Paneli</h2>
    <p>Çalıştırmak istediğin Lua kodunu yaz ve Gönder'e bas:</p>
    <textarea id="codeinput" placeholder="print('Merhaba Dünya!')"></textarea><br>
    <button onclick="sendCommand()">Kodu Gönder</button>
    <button class="clear" onclick="clearLogs()">Konsolu Temizle</button>

    <h3>Oyun Konsol Çıktıları (Live Log):</h3>
    <pre id="output">Bağlantı bekleniyor...</pre>

    <script>
        function sendCommand() {
            let code = document.getElementById("codeinput").value;
            fetch('/set_command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({code: code})
            }).then(res => res.json()).then(data => {
                alert("Kod Delta'ya iletildi!");
            });
        }

        function clearLogs() {
            fetch('/clear_logs', {method: 'POST'})
            .then(res => res.json())
            .then(data => {
                document.getElementById("output").innerText = "Konsol temizlendi.";
            });
        }

        setInterval(() => {
            fetch('/get_logs')
            .then(res => res.json())
            .then(data => {
                document.getElementById("output").innerText = data.logs.join("\\n");
            });
        }, 1500);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/set_command', methods=['POST'])
def set_command():
    global current_command
    data = request.json
    current_command = data.get('code', '')
    return jsonify({"status": "success"})

@app.route('/command', methods=['GET'])
def get_command():
    global current_command
    cmd = current_command
    current_command = "" # Komut bir kez çekilince sıfırlanır
    return cmd, 200, {'Content-Type': 'text/plain'}

@app.route('/result', methods=['POST'])
def receive_result():
    global execution_logs
    data = request.json
    if data and 'output' in data:
        execution_logs.append(data['output'])
    return jsonify({"status": "success"})

@app.route('/get_logs', methods=['GET'])
def get_logs():
    global execution_logs
    return jsonify({"logs": execution_logs})

@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    global execution_logs
    execution_logs = []
    return jsonify({"status": "success"})
  
