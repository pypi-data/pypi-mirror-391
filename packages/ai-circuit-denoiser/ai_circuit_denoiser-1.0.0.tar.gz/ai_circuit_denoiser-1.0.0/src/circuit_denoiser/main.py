#!/usr/bin/env python3
"""
AI Circuit Denoiser - 主应用程序入口点
"""

import sys
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('circuit_denoiser.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def get_model_path():
    """获取模型文件路径"""
    # 首先尝试包内模型
    package_models_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
    package_model_path = os.path.join(package_models_dir, 'circuit_denoiser_model_final.pth')
    
    if os.path.exists(package_model_path):
        return package_model_path
    
    # 然后尝试当前目录的models文件夹
    local_models_dir = os.path.join(os.getcwd(), 'models')
    local_model_path = os.path.join(local_models_dir, 'circuit_denoiser_model_final.pth')
    
    if os.path.exists(local_model_path):
        return local_model_path
    
    # 最后尝试用户主目录
    home_dir = os.path.expanduser('~')
    home_model_path = os.path.join(home_dir, '.circuit_denoiser', 'models', 'circuit_denoiser_model_final.pth')
    
    if os.path.exists(home_model_path):
        return home_model_path
    
    raise FileNotFoundError("Could not find the AI model file. Please ensure the model is installed.")

def main():
    """应用程序主函数"""
    try:
        from PyQt5.QtWidgets import QApplication
        
        # 使用相对导入
        from .main_window import MainWindow
        
        # 创建QApplication实例
        app = QApplication(sys.argv)
        app.setApplicationName("AI Circuit Denoiser")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("CircuitAI")
        
        # 设置应用程序样式
        app.setStyle('Fusion')
        
        # 创建并显示主窗口
        logger.info("启动AI Circuit Denoiser")
        window = MainWindow()
        window.show()
        
        logger.info("应用程序启动成功")
        
        # 运行应用程序
        sys.exit(app.exec_())
        
    except ImportError as e:
        logger.error(f"导入失败: {e}")
        print(f"错误: 缺少必要的依赖包")
        print("请确保已安装: PyQt5, torch, numpy, matplotlib")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"应用程序错误: {e}")
        print(f"应用程序启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
