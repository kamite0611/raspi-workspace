#!/usr/bin/env python3
"""赤外線信号キャプチャプログラム"""
import pigpio
import json
import time
import sys
from datetime import datetime

# GPIO設定
IR_RECEIVER_GPIO = 17

class IRCapture:
    def __init__(self, pi, gpio):
        self.pi = pi
        self.gpio = gpio
        self.pulses = []
        self.last_tick = None
        self.capturing = False
        self.timeout = 100000  # 100ms無信号でキャプチャ終了

        # GPIO設定
        self.pi.set_mode(gpio, pigpio.INPUT)
        self.pi.set_pull_up_down(gpio, pigpio.PUD_UP)

        # コールバック設定
        self.callback = self.pi.callback(gpio, pigpio.EITHER_EDGE, self._cb)

    def _cb(self, gpio, level, tick):
        if self.last_tick is not None:
            duration = pigpio.tickDiff(self.last_tick, tick)
            if duration < self.timeout:
                self.pulses.append((level, duration))
                self.capturing = True
        self.last_tick = tick

    def capture(self):
        """信号をキャプチャして返す"""
        self.pulses = []
        self.last_tick = None
        self.capturing = False

        print("リモコンを受信モジュールに向けてボタンを押してください...")

        # 信号待機
        while not self.capturing:
            time.sleep(0.1)

        # 信号終了待機
        time.sleep(0.2)

        return self.pulses.copy()

    def stop(self):
        self.callback.cancel()


def save_signal(name, pulses, filename):
    """信号をJSONファイルに保存"""
    data = {
        "name": name,
        "captured_at": datetime.now().isoformat(),
        "pulses": pulses
    }

    # 既存ファイルを読み込み
    try:
        with open(filename, 'r') as f:
            signals = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        signals = {}

    signals[name] = data

    with open(filename, 'w') as f:
        json.dump(signals, f, indent=2)

    print(f"保存完了: {name} ({len(pulses)} パルス)")


def main():
    pi = pigpio.pi()
    if not pi.connected:
        print("Error: pigpiodに接続できません")
        return 1

    print("=== 赤外線信号キャプチャ ===\n")

    capture = IRCapture(pi, IR_RECEIVER_GPIO)
    config_file = "/home/akamite/iot-lighting-control/iot/config/ir_signals.json"

    try:
        while True:
            print("\n操作を選択:")
            print("  1: 信号をキャプチャ")
            print("  2: 保存済み信号を表示")
            print("  q: 終了")

            choice = input("\n> ").strip()

            if choice == '1':
                name = input("信号の名前 (例: light_on): ").strip()
                if not name:
                    print("名前を入力してください")
                    continue

                pulses = capture.capture()
                print(f"\nキャプチャ完了: {len(pulses)} パルス")

                # パルス情報を表示
                if pulses:
                    total_time = sum(p[1] for p in pulses) / 1000
                    print(f"  総時間: {total_time:.1f}ms")

                    save = input("保存しますか? (y/n): ").strip().lower()
                    if save == 'y':
                        save_signal(name, pulses, config_file)

            elif choice == '2':
                try:
                    with open(config_file, 'r') as f:
                        signals = json.load(f)
                    print("\n保存済み信号:")
                    for name, data in signals.items():
                        print(f"  - {name}: {len(data['pulses'])} パルス")
                except FileNotFoundError:
                    print("保存済み信号はありません")

            elif choice == 'q':
                break

    except KeyboardInterrupt:
        print("\n終了")
    finally:
        capture.stop()
        pi.stop()

    return 0


if __name__ == "__main__":
    sys.exit(main())
