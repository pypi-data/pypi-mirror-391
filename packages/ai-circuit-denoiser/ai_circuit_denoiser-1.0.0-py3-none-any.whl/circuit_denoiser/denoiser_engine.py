import torch
import numpy as np
import os

class DenoiserEngine:
    def __init__(self, model_path=None):
        """
        AI去噪引擎
        
        Args:
            model_path: 训练好的模型文件路径，如果为None则自动查找
        """
        self.device = self._setup_device()
        
        if model_path is None:
            model_path = self._find_model_path()
            
        self.model = self._load_model(model_path)
        self.model.eval()  # 设置为评估模式
        print(f"✅ AI去噪引擎初始化完成，使用设备: {self.device}")
    
    def _find_model_path(self):
        """自动查找模型文件路径"""
        # 尝试多个可能的路径
        possible_paths = [
            # 包安装路径
            os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'circuit_denoiser_model_final.pth'),
            # 开发环境路径
            os.path.join(os.path.dirname(__file__), '..', 'models', 'circuit_denoiser_model_final.pth'),
            # 用户主目录
            os.path.join(os.path.expanduser('~'), '.circuit_denoiser', 'models', 'circuit_denoiser_model_final.pth'),
            # 当前工作目录
            os.path.join(os.getcwd(), 'models', 'circuit_denoiser_model_final.pth'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        raise FileNotFoundError("Could not find the AI model file. Please ensure the model is installed.")
    
    def _setup_device(self):
        """设置计算设备"""
        if torch.backends.mps.is_available():
            return torch.device("mps")
        elif torch.cuda.is_available():
            return torch.device("cuda")
        else:
            return torch.device("cpu")
    
    def _load_model(self, model_path):
        """加载训练好的模型"""
        try:
            # 使用相对导入
            from .model import UNet1D
            model = UNet1D(n_channels=1, n_classes=1)
            model.load_state_dict(torch.load(model_path, map_location=self.device))
            model.to(self.device)
            print(f"✅ 模型加载成功: {model_path}")
            return model
        except Exception as e:
            raise Exception(f"模型加载失败: {str(e)}")
    
    def denoise_signal(self, signal, strength=5):
        """
        对输入信号进行去噪处理
        
        Args:
            signal: 输入信号 (numpy数组, 形状 [n_samples])
            strength: 去噪强度 (1-10)
            
        Returns:
            denoised_signal: 去噪后的信号 (numpy数组, 形状 [n_samples])
        """
        if len(signal) == 0:
            raise ValueError("输入信号不能为空")
        
        # 确保信号是浮点数类型
        signal = signal.astype(np.float32)
        
        # 归一化信号到 [-1, 1] 范围
        signal_min, signal_max = signal.min(), signal.max()
        if signal_max - signal_min > 0:
            signal_normalized = 2 * (signal - signal_min) / (signal_max - signal_min) - 1
        else:
            signal_normalized = signal * 0  # 处理常值信号
        
        # 转换为PyTorch张量并添加批次和通道维度 [1, 1, n_samples]
        input_tensor = torch.FloatTensor(signal_normalized).unsqueeze(0).unsqueeze(0).to(self.device)
        
        # 使用模型进行去噪
        with torch.no_grad():
            output_tensor = self.model(input_tensor)
        
        # 将输出转换回numpy数组
        denoised_normalized = output_tensor.cpu().squeeze().numpy()
        
        # 应用去噪强度调节
        denoised_normalized = self._apply_strength(signal_normalized, denoised_normalized, strength)
        
        # 反归一化到原始范围
        if signal_max - signal_min > 0:
            denoised_signal = (denoised_normalized + 1) / 2 * (signal_max - signal_min) + signal_min
        else:
            denoised_signal = denoised_normalized
        
        return denoised_signal
    
    def _apply_strength(self, original, denoised, strength):
        """
        应用去噪强度调节
        
        Args:
            original: 原始归一化信号
            denoised: 去噪后的归一化信号  
            strength: 去噪强度 (1-10)
            
        Returns:
            调节后的去噪信号
        """
        # 将强度从1-10映射到混合比例
        # strength=1: 更多保留原始信号 (弱去噪)
        # strength=10: 更多使用去噪结果 (强去噪)
        alpha = (strength - 1) / 9.0  # 映射到 0.0 - 1.0
        
        # 基础混合
        result = alpha * denoised + (1 - alpha) * original
        
        # 对于高强度，额外应用一些后处理
        if strength >= 7:
            # 轻微平滑
            from scipy import ndimage
            result = ndimage.gaussian_filter1d(result, sigma=0.5)
        
        return result
    
    def denoise_with_iterations(self, signal, iterations=1, strength=5):
        """
        多次迭代去噪（更强的去噪效果）
        
        Args:
            signal: 输入信号
            iterations: 迭代次数
            strength: 每次迭代的强度
            
        Returns:
            多次去噪后的信号
        """
        current_signal = signal.copy()
        
        for i in range(iterations):
            current_strength = min(10, strength + i * 2)  # 每次迭代稍微增加强度
            current_signal = self.denoise_signal(current_signal, current_strength)
            
        return current_signal
    
    def batch_denoise(self, signals, strength=5):
        """批量处理多个信号"""
        return [self.denoise_signal(signal, strength) for signal in signals]
    
    def get_model_info(self):
        """获取模型信息"""
        total_params = sum(p.numel() for p in self.model.parameters())
        return {
            "device": str(self.device),
            "parameters": f"{total_params:,}",
            "input_shape": "(1, 1, n_samples)",
            "output_shape": "(1, 1, n_samples)",
            "strength_range": "1-10 (可调节)"
        }
    
    def test_denoising_strength(self, signal):
        """
        测试不同去噪强度的效果
        """
        print("🧪 测试不同去噪强度效果...")
        
        results = {}
        original_std = np.std(signal)
        
        for strength in [1, 3, 5, 7, 10]:
            denoised = self.denoise_signal(signal, strength)
            residual_std = np.std(denoised - signal)
            improvement = original_std / residual_std if residual_std > 0 else 1.0
            
            results[strength] = {
                'denoised': denoised,
                'improvement': improvement,
                'residual_std': residual_std
            }
            
            print(f"   强度 {strength}: 改善 {improvement:.2f}x, 残余误差 {residual_std:.4f}")
        
        return results
    
    def test_denoising(self):
        """测试去噪功能"""
        print("🧪 测试去噪功能...")
        
        # 创建测试信号（电容充电曲线 + 噪声）
        t = np.linspace(0, 1, 1000)
        clean_signal = 2.0 * (1 - np.exp(-t / 0.2)) - 1.0
        noise = 0.3 * np.random.normal(0, 1, 1000)
        test_signal = clean_signal + noise
        
        try:
            # 测试默认强度
            denoised = self.denoise_signal(test_signal)
            improvement = np.std(test_signal - clean_signal) / np.std(denoised - clean_signal)
            
            print(f"✅ 去噪测试成功!")
            print(f"   - 输入信号长度: {len(test_signal)}")
            print(f"   - 输出信号长度: {len(denoised)}")
            print(f"   - 噪声改善倍数: {improvement:.2f}x")
            
            # 测试不同强度
            self.test_denoising_strength(test_signal)
            
            return True
            
        except Exception as e:
            print(f"❌ 去噪测试失败: {e}")
            return False

if __name__ == "__main__":
    # 独立测试
    print("🔧 DenoiserEngine 独立测试")
    print("=" * 50)
    
    try:
        engine = DenoiserEngine()
        print("✅ 引擎初始化成功")
        
        model_info = engine.get_model_info()
        print(f"📊 模型信息:")
        for key, value in model_info.items():
            print(f"   - {key}: {value}")
        
        # 运行测试
        engine.test_denoising()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
