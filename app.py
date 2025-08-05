from flask import Flask, render_template, request, jsonify
import subprocess
import os
import threading
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Store running processes
running_processes = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_traffic', methods=['POST'])
def start_traffic():
    try:
        data = request.get_json()
        target_url = data.get('url', '').strip()
        visits_per_hour = int(data.get('visits_per_hour', 12))
        proxy_type = data.get('proxy_type', 'free')
        
        if not target_url:
            return jsonify({'success': False, 'message': 'URL is required'})
        
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'https://' + target_url
        
        # Kill existing process for this URL if running
        if target_url in running_processes:
            try:
                running_processes[target_url].terminate()
                del running_processes[target_url]
            except:
                pass
        
        # Start traffic generator in background
        def run_traffic_generator():
            try:
                process = subprocess.Popen([
                    'python', 'traffic_generator.py',
                    '--url', target_url,
                    '--visits-per-hour', str(visits_per_hour),
                    '--proxy-type', proxy_type
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                running_processes[target_url] = process
                process.wait()
                
                # Clean up when process ends
                if target_url in running_processes:
                    del running_processes[target_url]
                    
            except Exception as e:
                logging.error(f"Error running traffic generator: {e}")
        
        # Start in background thread
        thread = threading.Thread(target=run_traffic_generator)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True, 
            'message': f'Traffic generation started for {target_url} at {visits_per_hour} visits/hour using {proxy_type} proxies'
        })
        
    except Exception as e:
        logging.error(f"Error starting traffic: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/stop_traffic', methods=['POST'])
def stop_traffic():
    try:
        data = request.get_json()
        target_url = data.get('url', '').strip()
        
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'https://' + target_url
        
        if target_url in running_processes:
            running_processes[target_url].terminate()
            del running_processes[target_url]
            return jsonify({'success': True, 'message': f'Traffic stopped for {target_url}'})
        else:
            return jsonify({'success': False, 'message': 'No running traffic found for this URL'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/status')
def status():
    return jsonify({
        'running_urls': list(running_processes.keys()),
        'total_running': len(running_processes)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
