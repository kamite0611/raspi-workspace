.PHONY: web ngrok

# ラズパイでWebサーバーを起動
web:
	ssh raspi "cd ~/iot-lighting-control/web && python3 app.py"

# ラズパイでngrokを起動（port 5000をトンネル）
ngrok:
	ssh raspi "ngrok http 5000"
