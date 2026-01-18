#!/usr/bin/env python3
"""赤外線受信モジュールの動作確認スクリプト"""
import pigpio
import time

# GPIO設定
IR_RECEIVER_GPIO = 17

def main():
    pi = pigpio.pi()
    if not pi.connected:
        print("Error: pigpiodに接続できません")
        return 1

    print("=== 赤外線受信モジュール テスト ===")
    print(f"GPIO{IR_RECEIVER_GPIO}で受信待機中...")
    print("リモコンのボタンを押してください (Ctrl+Cで終了)\n")

    # 入力モードに設定（プルアップ）
    pi.set_mode(IR_RECEIVER_GPIO, pigpio.INPUT)
    pi.set_pull_up_down(IR_RECEIVER_GPIO, pigpio.PUD_UP)

    last_state = pi.read(IR_RECEIVER_GPIO)
    pulse_count = 0
    last_change = time.time()

    try:
        while True:
            state = pi.read(IR_RECEIVER_GPIO)
            if state != last_state:
                now = time.time()
                duration = (now - last_change) * 1000000  # マイクロ秒

                if duration > 10000:  # 10ms以上の間隔で新しい信号とみなす
                    if pulse_count > 0:
                        print(f"  → 検出パルス数: {pulse_count}")
                    pulse_count = 0
                    print(f"\n[{time.strftime('%H:%M:%S')}] 赤外線信号を検出!")

                pulse_count += 1
                last_state = state
                last_change = now

            time.sleep(0.0001)  # 100μs

    except KeyboardInterrupt:
        print("\n\n終了します")
    finally:
        pi.stop()

    return 0

if __name__ == "__main__":
    exit(main())
