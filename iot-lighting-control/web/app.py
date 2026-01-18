#!/usr/bin/env python3
"""照明制御 Webインターフェース"""
from flask import Flask, render_template, jsonify, request, Response
from functools import wraps
from dotenv import load_dotenv
import pigpio
import json
import time
import os

# .env読み込み
load_dotenv()

app = Flask(__name__)

# 設定
IR_GPIO = 18
FREQ = 38000
CONFIG_PATH = "/home/akamite/iot-lighting-control/iot/config/ir_signals.json"

# Basic認証
AUTH_USERNAME = os.getenv('BASIC_AUTH_USERNAME', 'admin')
AUTH_PASSWORD = os.getenv('BASIC_AUTH_PASSWORD', 'password')

# コマンドマッピング
COMMANDS = {
    "on": "light_on",
    "off": "light_off",
    "super": "light_super_on",
}


def check_auth(username, password):
    """認証チェック"""
    return username == AUTH_USERNAME and password == AUTH_PASSWORD


def authenticate():
    """認証要求"""
    return Response(
        '認証が必要です', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )


def requires_auth(f):
    """Basic認証デコレータ"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


def load_signals():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except:
        return {}


def transmit_signal(signal_name, repeat=3):
    """赤外線信号を送信"""
    signals = load_signals()
    if signal_name not in signals:
        return False, f"信号が見つかりません: {signal_name}"

    pi = pigpio.pi()
    if not pi.connected:
        return False, "pigpiod接続失敗"

    try:
        pulses = signals[signal_name]['pulses']
        pi.hardware_PWM(IR_GPIO, FREQ, 0)

        for _ in range(repeat):
            for level, duration in pulses:
                if level == 1:
                    pi.hardware_PWM(IR_GPIO, FREQ, 500000)
                else:
                    pi.hardware_PWM(IR_GPIO, FREQ, 0)
                end = time.perf_counter() + (duration / 1000000.0)
                while time.perf_counter() < end:
                    pass
            time.sleep(0.1)

        pi.hardware_PWM(IR_GPIO, FREQ, 0)
        return True, "送信完了"
    except Exception as e:
        return False, str(e)
    finally:
        pi.hardware_PWM(IR_GPIO, FREQ, 0)
        pi.stop()


@app.route('/')
@requires_auth
def index():
    return render_template('index.html')


@app.route('/api/light/<action>', methods=['POST'])
@requires_auth
def control_light(action):
    signal_name = COMMANDS.get(action, action)
    success, message = transmit_signal(signal_name)
    return jsonify({
        'success': success,
        'action': action,
        'message': message
    })


@app.route('/api/signals')
@requires_auth
def list_signals():
    signals = load_signals()
    return jsonify({
        'signals': list(signals.keys())
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
