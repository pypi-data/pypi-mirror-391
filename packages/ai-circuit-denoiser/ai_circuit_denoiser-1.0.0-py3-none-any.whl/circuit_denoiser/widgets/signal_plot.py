import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QSizePolicy
import numpy as np

class SignalPlotWidget(FigureCanvas):
    def __init__(self, parent=None, width=10, height=4, dpi=100):
        # 创建图形和坐标轴
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#f8f9fa')
        self.axes = self.fig.add_subplot(111)
        
        super().__init__(self.fig)
        self.setParent(parent)
        
        # 设置尺寸策略
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()
        
        # 初始化空图表
        self._init_plot()
    
    def _init_plot(self):
        """初始化空白图表"""
        self.axes.clear()
        self.axes.set_title('Signal Display Area', fontsize=12, fontweight='bold', pad=15)
        self.axes.set_xlabel('Sample Points', fontsize=10)
        self.axes.set_ylabel('Amplitude', fontsize=10)
        self.axes.grid(True, alpha=0.3)
        self.axes.set_facecolor('#ffffff')
        self.fig.tight_layout()
        self.draw()
    
    def plot_signals(self, original_signal, denoised_signal=None, time_axis=None):
        """
        绘制信号对比图
        """
        self.axes.clear()
        
        # 创建时间轴（如果未提供）
        if time_axis is None:
            time_axis = np.arange(len(original_signal))
        
        # 绘制原始信号
        self.axes.plot(time_axis, original_signal, 
                      color='#e74c3c', linewidth=1.5, alpha=0.7, label='Original Signal')
        
        # 如果提供了去噪信号，绘制对比
        if denoised_signal is not None:
            self.axes.plot(time_axis, denoised_signal, 
                          color='#2ecc71', linewidth=1.8, label='Denoised Signal')
        
        # 设置图表属性
        self.axes.set_title('Signal Denoising Comparison', fontsize=12, fontweight='bold', pad=15)
        self.axes.set_xlabel('Sample Points', fontsize=10)
        self.axes.set_ylabel('Amplitude', fontsize=10)
        self.axes.legend(fontsize=9)
        self.axes.grid(True, alpha=0.3)
        self.axes.set_facecolor('#ffffff')
        
        # 自动调整坐标轴范围
        self.axes.relim()
        self.axes.autoscale_view()
        
        self.fig.tight_layout()
        self.draw()
    
    def clear_plot(self):
        """清空图表"""
        self._init_plot()
    
    def save_plot(self, filename):
        """保存图表为图片"""
        self.fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#f8f9fa')
