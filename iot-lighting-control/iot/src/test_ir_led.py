#!/usr/bin/env python3
"""赤外線LED送信回路の動作確認スクリプト"""
import pigpio
import time

# GPIO設定
IR_LED_GPIO = 18

def main():
    pi = pigpio.pi()
    if not pi.connected:
        print("Error: pigpiodに接続できません")
        return 1

    print("=== 赤外線LED送信回路 テスト ===")
    print(f"GPIO{IR_LED_GPIO}を使用\n")

    # 出力モードに設定
    pi.set_mode(IR_LED_GPIO, pigpio.OUTPUT)

    # テスト1: 単純なON/OFF
    print("テスト1: LED ON/OFF (5回)")
    print("  ※スマホのカメラで赤外線LEDを見ると光が確認できます")
    for i in range(5):
        pi.write(IR_LED_GPIO, 1)
        print(f"  {i+1}: ON")
        time.sleep(0.5)
        pi.write(IR_LED_GPIO, 0)
        print(f"  {i+1}: OFF")
        time.sleep(0.5)

    time.sleep(1)

    # テスト2: 38kHz PWM（赤外線リモコンの標準周波数）
    print("\nテスト2: 38kHz PWM信号 (2秒間)")
    print("  ※これが実際のリモコン信号で使う周波数です")

    # 38kHz = 38000Hz
    pi.set_PWM_frequency(IR_LED_GPIO, 38000)
    pi.set_PWM_dutycycle(IR_LED_GPIO, 128)  # 50% duty

    time.sleep(2)

    pi.set_PWM_dutycycle(IR_LED_GPIO, 0)

    # テスト3: パルス送信（リモコン風）
    print("\nテスト3: パルスパターン送信")
    for i in range(3):
        # 短いバースト
        pi.set_PWM_dutycycle(IR_LED_GPIO, 128)
        time.sleep(0.0005)  # 500μs
        pi.set_PWM_dutycycle(IR_LED_GPIO, 0)
        time.sleep(0.0005)

    print("  パルス送信完了")

    # クリーンアップ
    pi.write(IR_LED_GPIO, 0)
    pi.stop()

    print("\n赤外線LEDテスト完了!")
    print("\n確認方法:")
    print("  1. スマホのカメラ(インカメラ推奨)でLEDを見る")
    print("  2. 紫色の光が見えれば正常に動作しています")

    return 0

if __name__ == "__main__":
    exit(main())
