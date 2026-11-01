set projectPath to "/Users/tezsidai/MyAI"
set pythonPath to projectPath & "/ai-env/bin/python"
set apiPath to projectPath & "/ai/api.py"
set logPath to projectPath & "/ai/my_ai_engine.log"
set htmlPath to projectPath & "/index.html"

do shell script "if ! pgrep -f " & quoted form of apiPath & " >/dev/null; then nohup " & quoted form of pythonPath & " " & quoted form of apiPath & " > " & quoted form of logPath & " 2>&1 & fi"

delay 3

do shell script "open -a 'Google Chrome' " & quoted form of htmlPath
