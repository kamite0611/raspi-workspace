#!/usr/bin/env python3
"""赤外線信号送信プログラム（シンプル版）"""
import pigpio
import json
import sys
import time
import argparse

# GPIO設定
IR_LED_GPIO = 18
CARRIER_FREQ = 38000  # 38kHz
DEFAULT_REPEAT = 3


class IRTransmit:
    def __init__(self, pi, gpio, freq=CARRIER_FREQ):
        self.pi = pi
        self.gpio = gpio
        self.freq = freq

        self.pi.set_mode(gpio, pigpio.OUTPUT)
        self.pi.write(gpio, 0)

        # ハードウェアPWMを使用（より正確な38kHz）
        # GPIO18はPWM0に対応
        self.pi.hardware_PWM(gpio, freq, 0)

    def transmit(self, pulses):
        """パルスデータを送信"""
        for level, duration in pulses:
            if level == 1:
                # Mark: 38kHzキャリアON（デューティ50%=500000）
                self.pi.hardware_PWM(self.gpio, self.freq, 500000)
            else:
                # Space: キャリアOFF
                self.pi.hardware_PWM(self.gpio, self.freq, 0)

            # マイクロ秒単位の待機
            self._delay_us(duration)

        # 確実にOFF
        self.pi.hardware_PWM(self.gpio, self.freq, 0)

    def _delay_us(self, us):
        """マイクロ秒単位の遅延（ビジーウェイト）"""
        end = time.perf_counter() + (us / 1000000.0)
        while time.perf_counter() < end:
            pass

    def transmit_repeat(self, pulses, repeat=1, gap_ms=100):
        """信号を複数回送信"""
        for i in range(repeat):
            self.transmit(pulses)
            if i < repeat - 1:
                time.sleep(gap_ms / 1000.0)

    def stop(self):
        self.pi.hardware_PWM(self.gpio, self.freq, 0)
        self.pi.write(self.gpio, 0)


def load_signals(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def main():
    parser = argparse.ArgumentParser(description='赤外線信号送信')
    parser.add_argument('signal', nargs='?', help='送信する信号名')
    parser.add_argument('--list', action='store_true', help='保存済み信号を一覧表示')
    parser.add_argument('-r', '--repeat', type=int, default=DEFAULT_REPEAT,
                        help=f'送信回数 (デフォルト: {DEFAULT_REPEAT})')

    args = parser.parse_args()

    config_file = "/home/akamite/iot-lighting-control/iot/config/ir_signals.json"
    signals = load_signals(config_file)

    if not signals:
        print(f"Error: 信号ファイルが見つかりません: {config_file}")
        return 1

    if args.list:
        print("保存済み信号:")
        for name, data in signals.items():
            print(f"  - {name}: {len(data['pulses'])} パルス")
        return 0

    if not args.signal:
        parser.print_help()
        return 1

    signal_name = args.signal

    if signal_name not in signals:
        print(f"Error: '{signal_name}' が見つかりません")
        print("利用可能:")
        for name in signals.keys():
            print(f"  - {name}")
        return 1

    pi = pigpio.pi()
    if not pi.connected:
        print("Error: pigpiodに接続できません")
        return 1

    transmitter = IRTransmit(pi, IR_LED_GPIO)

    try:
        pulses = signals[signal_name]['pulses']
        print(f"送信: {signal_name} ({len(pulses)}パルス x {args.repeat}回)")

        transmitter.transmit_repeat(pulses, repeat=args.repeat)

        print("完了!")

    finally:
        transmitter.stop()
        pi.stop()

    return 0


if __name__ == "__main__":
    sys.exit(main())
