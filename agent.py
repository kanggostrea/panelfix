import threading
import time
import requests

# Existing functions and code here...

# === TAMBAHKAN SETELAH send_heartbeat_to_dashboard() ===

# ==========================================
# 🔄 POLL COMMANDS FROM DASHBOARD
# ==========================================
def poll_commands_from_dashboard():
    """Background thread yang pull commands dari dashboard setiap 5 detik"""
    global CURRENT_SLOT
    
    print("🔄 [POLL] Starting command polling thread...", flush=True)
    
    while True:
        try:
            if not CURRENT_SLOT:
                time.sleep(5)
                continue
            
            # Build full URL dengan environment variable
            dashboard_url = os.getenv("DASHBOARD_URL", "https://dashboard.jujulefek.qzz.io")
            url = f"{dashboard_url}/api/command/get/{CURRENT_SLOT}"
            
            response = requests.get(
                url,
                headers={"X-Auth-Key": DASHBOARD_AUTH_KEY},
                timeout=10,
                verify=False
            )
            
            if response.status_code == 200:
                commands = response.json()
                if isinstance(commands, list) and len(commands) > 0:
                    print(f"📨 [POLL] Received {len(commands)} commands", flush=True)
                    
                    # Execute each command
                    for cmd in commands:
                        if cmd.get('status') == 'PENDING':
                            execute_command(cmd)
            
            elif response.status_code == 404:
                # No commands - silent
                pass
            else:
                print(f"⚠️ [POLL] API Error: {response.status_code}", flush=True)
                
        except Exception as e:
            print(f"❌ [POLL] Error: {e}", flush=True)
        
        time.sleep(5)

def execute_command(cmd):
    """Execute command received from dashboard"""
    global CURRENT_SLOT
    
    cmd_id = cmd.get('id', 'unknown')
    action = cmd.get('action')
    payload = cmd.get('payload', {})
    
    print(f"⚡ [EXEC] Executing: {action} (ID: {cmd_id})", flush=True)
    
    try:
        if action == "start_login":
            if check_process(FILE_LOGIN) or check_process(FILE_LOOP):
                print(f"⚠️ [EXEC] Process already running", flush=True)
                return
            
            cmd_login = (
                f"xvfb-run -a --server-args='-screen 0 {SCREEN_LOGIN}' "
                f"{sys.executable} {FILE_LOGIN}"
            )
            threading.Thread(target=run_and_monitor, args=(cmd_login, "LOGIN"), daemon=True).start()
            print(f"✅ [EXEC] Login started", flush=True)
            
        elif action == "start_loop":
            if check_process(FILE_LOOP):
                print(f"⚠️ [EXEC] Loop already running", flush=True)
                return
            
            cmd_loop = (
                f"xvfb-run -a --server-args='-screen 0 {SCREEN_LOOP}' "
                f"{sys.executable} -u {FILE_LOOP}"
            )
            threading.Thread(target=run_and_monitor, args=(cmd_loop, "LOOP"), daemon=True).start()
            print(f"✅ [EXEC] Loop started", flush=True)
            
        elif action == "stop":
            kill_processes()
            clean_system()
            print(f"✅ [EXEC] Stopped all processes", flush=True)
            
        elif action == "clean_ram":
            clean_system()
            mem = psutil.virtual_memory()
            print(f"✅ [EXEC] RAM Cleaned: {mem.available // 1048576} MB free", flush=True)
        
        else:
            print(f"❌ [EXEC] Unknown action: {action}", flush=True)
            
    except Exception as e:
        print(f"❌ [EXEC] Error executing {action}: {e}", flush=True)

# Modify startup to include command polling thread
command_polling_thread = threading.Thread(target=poll_commands_from_dashboard)
command_polling_thread.start()
