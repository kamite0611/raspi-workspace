#!/usr/bin/env python3
"""GPIO動作確認スクリプト"""
import pigpio
import time

# GPIO18を使用（PWM対応ピン）
GPIO_PIN = 18

def main():
    pi = pigpio.pi()
    if not pi.connected:
        print("Error: pigpiodに接続できません")
        return 1

    print(f"pigpio接続OK (version: {pi.get_pigpio_version()})")
    print(f"GPIO{GPIO_PIN}をテスト中...")

    # 出力モードに設定
    pi.set_mode(GPIO_PIN, pigpio.OUTPUT)

    # LEDチカチカ（5回）
    print("LED点滅テスト開始（5回）")
    for i in range(5):
        pi.write(GPIO_PIN, 1)
        print(f"  {i+1}: ON")
        time.sleep(0.5)
        pi.write(GPIO_PIN, 0)
        print(f"  {i+1}: OFF")
        time.sleep(0.5)

    # PWMテスト
    print("\nPWMテスト（徐々に明るく→暗く）")
    for duty in range(0, 256, 25):
        pi.set_PWM_dutycycle(GPIO_PIN, duty)
        print(f"  PWM: {duty}/255")
        time.sleep(0.2)
    for duty in range(255, -1, -25):
        pi.set_PWM_dutycycle(GPIO_PIN, duty)
        print(f"  PWM: {duty}/255")
        time.sleep(0.2)

    # クリーンアップ
    pi.set_PWM_dutycycle(GPIO_PIN, 0)
    pi.stop()

    print("\nGPIOテスト完了!")
    return 0

if __name__ == "__main__":
    exit(main())
