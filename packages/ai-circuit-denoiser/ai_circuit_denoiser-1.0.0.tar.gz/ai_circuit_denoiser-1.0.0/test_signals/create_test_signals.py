import numpy as np
import matplotlib.pyplot as plt

def create_test_signals():
    """创建几种典型的电路测试信号"""
    
    # 信号1：电容充电曲线 + 噪声
    t = np.linspace(0, 1, 1000)
    
    # 1. 干净的电容充电曲线
    clean_charge = 3.0 * (1 - np.exp(-t / 0.3))
    np.savetxt('test_signals/clean_capacitor_charge.txt', clean_charge, fmt='%.6f')
    
    # 2. 含噪版本（高斯噪声 + 脉冲噪声）
    gaussian_noise = 0.4 * np.random.normal(0, 1, 1000)
    impulse_noise = np.zeros(1000)
    impulse_positions = np.random.choice(1000, 15, replace=False)
    impulse_noise[impulse_positions] = 1.0 * np.random.randn(15)
    
    noisy_charge = clean_charge + gaussian_noise + impulse_noise
    np.savetxt('test_signals/noisy_capacitor_charge.txt', noisy_charge, fmt='%.6f')
    
    # 3. 正弦波 + 工频干扰
    clean_sine = 2.0 * np.sin(2 * np.pi * 10 * t)
    powerline_noise = 0.3 * np.sin(2 * np.pi * 50 * t)
    noisy_sine = clean_sine + powerline_noise + 0.2 * np.random.normal(0, 1, 1000)
    np.savetxt('test_signals/noisy_sine_wave.txt', noisy_sine, fmt='%.6f')
    
    # 4. 方波信号 + 振铃噪声
    clean_square = 2.0 * (np.sin(2 * np.pi * 5 * t) > 0).astype(float) - 1.0
    ringing_noise = 0.5 * np.exp(-t * 8) * np.sin(2 * np.pi * 50 * t)
    noisy_square = clean_square + ringing_noise + 0.1 * np.random.normal(0, 1, 1000)
    np.savetxt('test_signals/noisy_square_wave.txt', noisy_square, fmt='%.6f')
    
    print("✅ 测试信号创建完成！")
    print("📁 生成的文件:")
    print("   - clean_capacitor_charge.txt (干净电容充电)")
    print("   - noisy_capacitor_charge.txt (含噪电容充电)") 
    print("   - noisy_sine_wave.txt (含噪正弦波)")
    print("   - noisy_square_wave.txt (含噪方波)")

if __name__ == "__main__":
    create_test_signals()
