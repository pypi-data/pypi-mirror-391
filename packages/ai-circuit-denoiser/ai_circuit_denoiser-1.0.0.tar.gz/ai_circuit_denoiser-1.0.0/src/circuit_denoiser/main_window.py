import sys
import os
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QMessageBox,
                             QProgressBar, QGroupBox, QSplitter, QFrame,
                             QInputDialog, QListWidget, QTabWidget, QTextEdit,
                             QSlider, QCheckBox, QSpinBox, QDoubleSpinBox, QComboBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

# 使用相对导入
from .denoiser_engine import DenoiserEngine
from .widgets.signal_plot import SignalPlotWidget

class DenoiserThread(QThread):
    """在后台线程中执行去噪任务"""
    finished = pyqtSignal(object)  # 去噪完成信号
    error = pyqtSignal(str)        # 错误信号
    
    def __init__(self, denoiser, signal, strength=5):
        super().__init__()
        self.denoiser = denoiser
        self.signal = signal
        self.strength = strength
    
    def run(self):
        try:
            result = self.denoiser.denoise_signal(self.signal, self.strength)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class BatchDenoiserThread(QThread):
    """批量处理线程"""
    progress = pyqtSignal(int, int, str)  # 当前进度，总数，文件名
    finished = pyqtSignal(dict)           # 完成信号，包含所有结果
    error = pyqtSignal(str, str)          # 错误信号，文件名和错误信息
    
    def __init__(self, denoiser, file_list, output_dir, strength=5):
        super().__init__()
        self.denoiser = denoiser
        self.file_list = file_list
        self.output_dir = output_dir
        self.strength = strength
    
    def run(self):
        results = {}
        total_files = len(self.file_list)
        
        for i, file_path in enumerate(self.file_list):
            try:
                filename = os.path.basename(file_path)
                self.progress.emit(i + 1, total_files, filename)
                
                # 加载信号
                if file_path.endswith('.csv'):
                    signal = np.loadtxt(file_path, delimiter=',')
                else:
                    signal = np.loadtxt(file_path)
                
                if signal.ndim > 1:
                    signal = signal.flatten()
                
                # 去噪处理（使用指定的强度）
                denoised = self.denoiser.denoise_signal(signal, self.strength)
                
                # 保存结果 - 修复文件路径
                base_name = os.path.splitext(filename)[0]
                output_path = os.path.join(self.output_dir, f"denoised_{base_name}.txt")
                np.savetxt(output_path, denoised, fmt='%.6f')
                
                # 同时保存处理前后的对比图
                plot_path = os.path.join(self.output_dir, f"comparison_{base_name}.png")
                self._save_comparison_plot(signal, denoised, plot_path)
                
                results[filename] = {
                    'original': signal,
                    'denoised': denoised,
                    'output_path': output_path,
                    'plot_path': plot_path
                }
                
                self.progress.emit(i + 1, total_files, f"{filename} ✓")
                
            except Exception as e:
                self.error.emit(filename, str(e))
        
        self.finished.emit(results)
    
    def _save_comparison_plot(self, original, denoised, save_path):
        """保存对比图"""
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 6))
        plt.plot(original, 'r-', label='Original Signal', linewidth=1, alpha=0.7)
        plt.plot(denoised, 'g-', label='Denoised Signal', linewidth=1.5)
        plt.title('Signal Denoising Comparison')
        plt.xlabel('Sample Points')
        plt.ylabel('Amplitude')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.denoiser = None
        self.current_signal = None
        self.denoised_signal = None
        self.processing_history = []
        
        self.init_ui()
        self.load_ai_model()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("AI电路噪声去除器 v2.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #3498db;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
            QPushButton#processBtn {
                background-color: #27ae60;
            }
            QPushButton#processBtn:hover {
                background-color: #219a52;
            }
            QPushButton#generateBtn {
                background-color: #9b59b6;
            }
            QPushButton#generateBtn:hover {
                background-color: #8e44ad;
            }
            QLabel {
                color: #2c3e50;
            }
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 标题
        title_label = QLabel("AI电路噪声去除器 v2.0")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin: 10px; padding: 15px; background-color: #3498db; color: white; border-radius: 8px;")
        main_layout.addWidget(title_label)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 单文件处理标签页
        self.single_tab = self.create_single_file_tab()
        self.tab_widget.addTab(self.single_tab, "单文件处理")
        
        # 批量处理标签页
        self.batch_tab = self.create_batch_tab()
        self.tab_widget.addTab(self.batch_tab, "批量处理")
        
        # 信号生成标签页
        self.generate_tab = self.create_generate_tab()
        self.tab_widget.addTab(self.generate_tab, "信号生成")
        
        # 历史记录标签页
        self.history_tab = self.create_history_tab()
        self.tab_widget.addTab(self.history_tab, "处理历史")
        
        main_layout.addWidget(self.tab_widget)
        
        # 状态栏
        self.statusBar().showMessage("就绪 - 请选择处理模式")
    
    def create_single_file_tab(self):
        """创建单文件处理标签页"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧控制面板
        left_panel = self.create_control_panel()
        splitter.addWidget(left_panel)
        
        # 右侧图表区域
        right_panel = self.create_plot_panel()
        splitter.addWidget(right_panel)
        
        # 设置分割比例
        splitter.setSizes([400, 800])
        
        layout.addWidget(splitter)
        return tab
    
    def create_batch_tab(self):
        """创建批量处理标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 批量处理控制面板
        batch_group = QGroupBox("批量处理控制")
        batch_layout = QVBoxLayout()
        
        # 文件列表
        file_list_layout = QHBoxLayout()
        self.batch_file_list = QListWidget()
        self.batch_file_list.setMaximumHeight(200)
        file_list_layout.addWidget(self.batch_file_list)
        
        # 文件列表按钮
        file_buttons_layout = QVBoxLayout()
        self.batch_add_btn = QPushButton("添加文件")
        self.batch_add_btn.clicked.connect(self.batch_add_files)
        self.batch_clear_btn = QPushButton("清空列表")
        self.batch_clear_btn.clicked.connect(self.batch_clear_files)
        self.batch_process_btn = QPushButton("开始批量处理")
        self.batch_process_btn.clicked.connect(self.batch_process)
        self.batch_process_btn.setEnabled(False)
        
        file_buttons_layout.addWidget(self.batch_add_btn)
        file_buttons_layout.addWidget(self.batch_clear_btn)
        file_buttons_layout.addWidget(self.batch_process_btn)
        file_buttons_layout.addStretch()
        
        file_list_layout.addLayout(file_buttons_layout)
        batch_layout.addLayout(file_list_layout)
        
        # 进度显示
        self.batch_progress_label = QLabel("就绪")
        self.batch_progress_bar = QProgressBar()
        batch_layout.addWidget(self.batch_progress_label)
        batch_layout.addWidget(self.batch_progress_bar)
        
        # 日志显示
        self.batch_log = QTextEdit()
        self.batch_log.setMaximumHeight(150)
        self.batch_log.setReadOnly(True)
        batch_layout.addWidget(QLabel("处理日志:"))
        batch_layout.addWidget(self.batch_log)
        
        batch_group.setLayout(batch_layout)
        layout.addWidget(batch_group)
        
        return tab
    
    def create_generate_tab(self):
        """创建信号生成标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 信号生成控制
        generate_group = QGroupBox("信号生成设置")
        generate_layout = QVBoxLayout()
        
        # 信号类型选择
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("信号类型:"))
        self.signal_type_combo = QComboBox()
        self.signal_type_combo.addItems(["电容充电曲线", "正弦波", "方波", "三角波", "指数衰减"])
        type_layout.addWidget(self.signal_type_combo)
        type_layout.addStretch()
        
        # 参数设置
        param_layout = QHBoxLayout()
        param_layout.addWidget(QLabel("频率/时间常数:"))
        self.freq_spin = QDoubleSpinBox()
        self.freq_spin.setRange(0.1, 100.0)
        self.freq_spin.setValue(10.0)
        param_layout.addWidget(self.freq_spin)
        
        param_layout.addWidget(QLabel("噪声水平:"))
        self.noise_spin = QDoubleSpinBox()
        self.noise_spin.setRange(0.0, 2.0)
        self.noise_spin.setValue(0.3)
        self.noise_spin.setSingleStep(0.1)
        param_layout.addWidget(self.noise_spin)
        
        param_layout.addStretch()
        
        # 生成按钮
        self.generate_btn = QPushButton("生成测试信号")
        self.generate_btn.setObjectName("generateBtn")
        self.generate_btn.clicked.connect(self.generate_test_signal)
        
        generate_layout.addLayout(type_layout)
        generate_layout.addLayout(param_layout)
        generate_layout.addWidget(self.generate_btn)
        generate_group.setLayout(generate_layout)
        layout.addWidget(generate_group)
        
        # 生成的信号预览
        preview_group = QGroupBox("Signal Preview")
        preview_layout = QVBoxLayout()
        self.preview_plot = SignalPlotWidget(self)
        preview_layout.addWidget(self.preview_plot)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        return tab
    
    def create_history_tab(self):
        """创建历史记录标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 历史记录列表
        history_group = QGroupBox("处理历史")
        history_layout = QVBoxLayout()
        
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.load_history_item)
        history_layout.addWidget(self.history_list)
        
        # 历史记录操作按钮
        history_buttons_layout = QHBoxLayout()
        self.clear_history_btn = QPushButton("清空历史")
        self.clear_history_btn.clicked.connect(self.clear_history)
        self.export_history_btn = QPushButton("导出历史报告")
        self.export_history_btn.clicked.connect(self.export_history_report)
        
        history_buttons_layout.addWidget(self.clear_history_btn)
        history_buttons_layout.addWidget(self.export_history_btn)
        history_buttons_layout.addStretch()
        
        history_layout.addLayout(history_buttons_layout)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        return tab
    
    def create_control_panel(self):
        """创建左侧控制面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 文件操作组
        file_group = QGroupBox("文件操作")
        file_layout = QVBoxLayout()
        
        self.load_btn = QPushButton("加载信号文件")
        self.load_btn.clicked.connect(self.load_signal_file)
        file_layout.addWidget(self.load_btn)
        
        self.export_btn = QPushButton("导出去噪结果")
        self.export_btn.clicked.connect(self.export_result)
        self.export_btn.setEnabled(False)
        file_layout.addWidget(self.export_btn)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 信号信息组
        info_group = QGroupBox("信号信息")
        info_layout = QVBoxLayout()
        
        self.signal_info = QLabel("未加载信号")
        self.signal_info.setWordWrap(True)
        self.signal_info.setStyleSheet("background-color: white; padding: 8px; border-radius: 4px; min-height: 120px;")
        info_layout.addWidget(self.signal_info)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 处理控制组
        process_group = QGroupBox("AI处理")
        process_layout = QVBoxLayout()
        
        self.process_btn = QPushButton("开始去噪")
        self.process_btn.setObjectName("processBtn")
        self.process_btn.clicked.connect(self.start_denoising)
        self.process_btn.setEnabled(False)
        process_layout.addWidget(self.process_btn)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        process_layout.addWidget(self.progress_bar)
        
        process_group.setLayout(process_layout)
        layout.addWidget(process_group)
        
        # 高级设置组
        advanced_group = QGroupBox("高级设置")
        advanced_layout = QVBoxLayout()
        
        # 去噪强度调节
        strength_layout = QHBoxLayout()
        strength_layout.addWidget(QLabel("去噪强度:"))
        self.strength_slider = QSlider(Qt.Horizontal)
        self.strength_slider.setRange(1, 10)
        self.strength_slider.setValue(5)
        self.strength_slider.setTickPosition(QSlider.TicksBelow)
        self.strength_slider.setTickInterval(1)
        strength_layout.addWidget(self.strength_slider)
        self.strength_label = QLabel("5")
        strength_layout.addWidget(self.strength_label)
        
        self.strength_slider.valueChanged.connect(lambda v: self.strength_label.setText(str(v)))
        
        advanced_layout.addLayout(strength_layout)
        
        # 自动保存选项
        self.auto_save_check = QCheckBox("处理后自动保存结果")
        self.auto_save_check.setChecked(True)
        advanced_layout.addWidget(self.auto_save_check)
        
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)
        
        # AI模型信息组
        model_group = QGroupBox("AI模型信息")
        model_layout = QVBoxLayout()
        
        self.model_info = QLabel("模型加载中...")
        self.model_info.setWordWrap(True)
        self.model_info.setStyleSheet("background-color: #e8f4fd; padding: 8px; border-radius: 4px; min-height: 100px;")
        model_layout.addWidget(self.model_info)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        layout.addStretch()
        
        return panel
    
    def create_plot_panel(self):
        """创建右侧图表面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 图表标题和操作按钮
        plot_header_layout = QHBoxLayout()
        plot_title = QLabel("Signal Display")
        plot_title.setFont(QFont("Arial", 12, QFont.Bold))
        plot_header_layout.addWidget(plot_title)
        
        self.save_plot_btn = QPushButton("保存图表")
        self.save_plot_btn.clicked.connect(self.save_current_plot)
        self.save_plot_btn.setEnabled(False)
        plot_header_layout.addWidget(self.save_plot_btn)
        
        plot_header_layout.addStretch()
        layout.addLayout(plot_header_layout)
        
        # 信号图表
        self.signal_plot = SignalPlotWidget(self)
        layout.addWidget(self.signal_plot)
        
        return panel

    def load_ai_model(self):
        """加载AI模型"""
        try:
            self.denoiser = DenoiserEngine()
            model_info = self.denoiser.get_model_info()
            info_text = f"✅ 模型加载成功\n\n"
            info_text += f"• 设备: {model_info['device']}\n"
            info_text += f"• 参数: {model_info['parameters']}\n"
            info_text += f"• 输入: {model_info['input_shape']}\n"
            info_text += f"• 输出: {model_info['output_shape']}\n"
            info_text += f"• 强度范围: {model_info['strength_range']}"
            self.model_info.setText(info_text)
            self.statusBar().showMessage("AI模型加载成功")
        except Exception as e:
            error_msg = f"❌ 模型加载失败:\n{str(e)}"
            self.model_info.setText(error_msg)
            self.statusBar().showMessage("模型加载失败")
            QMessageBox.critical(self, "错误", f"无法加载AI模型:\n{str(e)}")

    def load_signal_file(self):
        """加载信号文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择信号文件",
            "",
            "文本文件 (*.txt);;CSV文件 (*.csv);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                # 加载信号数据
                if file_path.endswith('.csv'):
                    data = np.loadtxt(file_path, delimiter=',')
                else:
                    data = np.loadtxt(file_path)
                
                # 确保是一维信号
                if data.ndim > 1:
                    data = data.flatten()
                
                self.current_signal = data
                self.denoised_signal = None
                
                # 更新信号信息
                info_text = f"✅ 信号加载成功\n\n"
                info_text += f"• 文件: {os.path.basename(file_path)}\n"
                info_text += f"• 长度: {len(data):,} 采样点\n"
                info_text += f"• 均值: {np.mean(data):.4f}\n"
                info_text += f"• 标准差: {np.std(data):.4f}\n"
                info_text += f"• 动态范围: [{np.min(data):.4f}, {np.max(data):.4f}]"
                
                self.signal_info.setText(info_text)
                
                # 绘制信号
                self.signal_plot.plot_signals(self.current_signal)
                
                # 启用处理按钮
                self.process_btn.setEnabled(True)
                self.export_btn.setEnabled(False)
                self.save_plot_btn.setEnabled(True)
                
                self.statusBar().showMessage(f"已加载信号: {os.path.basename(file_path)}")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"文件加载失败:\n{str(e)}")
                self.statusBar().showMessage("文件加载失败")

    def generate_test_signal(self):
        """生成测试信号"""
        signal_type = self.signal_type_combo.currentText()
        frequency = self.freq_spin.value()
        noise_level = self.noise_spin.value()
        
        t = np.linspace(0, 1, 1000)
        
        if signal_type == "电容充电曲线":
            clean = 3.0 * (1 - np.exp(-t / (1.0/frequency)))
            signal_name = f"电容充电曲线 (τ={1.0/frequency:.2f}s)"
            
        elif signal_type == "正弦波":
            clean = 2.0 * np.sin(2 * np.pi * frequency * t)
            signal_name = f"正弦波 (f={frequency}Hz)"
            
        elif signal_type == "方波":
            clean = 2.0 * (np.sin(2 * np.pi * frequency * t) > 0).astype(float) - 1.0
            signal_name = f"方波 (f={frequency}Hz)"
            
        elif signal_type == "三角波":
            clean = 2.0 * (2 * np.abs(2 * frequency * t - np.floor(2 * frequency * t + 0.5)) - 1)
            signal_name = f"三角波 (f={frequency}Hz)"
            
        else:  # 指数衰减
            clean = 3.0 * np.exp(-t * frequency)
            signal_name = f"指数衰减 (τ={1.0/frequency:.2f}s)"
        
        # 添加噪声
        gaussian_noise = noise_level * np.random.normal(0, 1, 1000)
        impulse_noise = np.zeros(1000)
        impulse_positions = np.random.choice(1000, 8, replace=False)
        impulse_noise[impulse_positions] = noise_level * 2 * np.random.randn(8)
        
        self.current_signal = clean + gaussian_noise + impulse_noise
        self.denoised_signal = None
        
        # 更新界面
        info_text = f"✅ 生成的测试信号\n\n"
        info_text += f"• 类型: {signal_name}\n"
        info_text += f"• 噪声水平: {noise_level:.2f}\n"
        info_text += f"• 长度: 1000 采样点\n"
        info_text += f"• 均值: {np.mean(self.current_signal):.4f}\n"
        info_text += f"• 标准差: {np.std(self.current_signal):.4f}"
        
        self.signal_info.setText(info_text)
        self.signal_plot.plot_signals(self.current_signal)
        self.preview_plot.plot_signals(self.current_signal)
        self.process_btn.setEnabled(True)
        self.export_btn.setEnabled(False)
        self.save_plot_btn.setEnabled(True)
        
        self.statusBar().showMessage(f"已生成测试信号: {signal_name}")

    def start_denoising(self):
        """开始去噪处理"""
        if self.current_signal is None:
            QMessageBox.warning(self, "警告", "请先加载或生成信号")
            return
        
        if self.denoiser is None:
            QMessageBox.critical(self, "错误", "AI模型未正确加载")
            return
        
        # 获取当前去噪强度
        strength = self.strength_slider.value()
        
        # 禁用按钮，显示进度条
        self.process_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度模式
        
        # 在后台线程中执行去噪（传递强度参数）
        self.denoiser_thread = DenoiserThread(self.denoiser, self.current_signal, strength)
        self.denoiser_thread.finished.connect(self.denoising_finished)
        self.denoiser_thread.error.connect(self.denoising_error)
        self.denoiser_thread.start()
        
        self.statusBar().showMessage(f"AI正在处理信号... (强度: {strength})")

    def denoising_finished(self, result):
        """去噪完成"""
        self.denoised_signal = result
        self.progress_bar.setVisible(False)
        self.process_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        
        # 计算性能指标
        original_std = np.std(self.current_signal)
        residual_std = np.std(self.denoised_signal - self.current_signal)
        improvement = original_std / residual_std if residual_std > 0 else 1.0
        
        # 更新信号信息
        current_info = self.signal_info.text()
        strength = self.strength_slider.value()
        new_info = current_info + f"\n• 去噪完成: ✅\n• 强度: {strength}\n• 噪声降低: {improvement:.2f}x\n• 残余误差: {residual_std:.6f}"
        self.signal_info.setText(new_info)
        
        # 绘制对比图
        self.signal_plot.plot_signals(self.current_signal, self.denoised_signal)
        
        # 添加到历史记录
        self.add_to_history(improvement, residual_std, strength)
        
        self.statusBar().showMessage(f"去噪完成 - 强度: {strength}, 噪声降低: {improvement:.2f}x")
        
        # 自动保存
        if self.auto_save_check.isChecked():
            self.auto_save_result(improvement, strength)
        
        QMessageBox.information(self, "完成", 
                               f"信号去噪处理完成！\n\n"
                               f"去噪强度: {strength}\n"
                               f"噪声降低: {improvement:.2f} 倍\n"
                               f"残余误差: {residual_std:.6f}")

    def denoising_error(self, error_msg):
        """去噪错误"""
        self.progress_bar.setVisible(False)
        self.process_btn.setEnabled(True)
        
        QMessageBox.critical(self, "错误", f"去噪处理失败:\n{error_msg}")
        self.statusBar().showMessage("去噪处理失败")

    def export_result(self):
        """导出去噪结果"""
        if self.denoised_signal is None:
            QMessageBox.warning(self, "警告", "没有可导出的去噪结果")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存去噪结果",
            f"denoised_{int(np.random.rand()*10000)}.txt",
            "文本文件 (*.txt);;CSV文件 (*.csv);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    np.savetxt(file_path, self.denoised_signal, delimiter=',', fmt='%.6f')
                else:
                    np.savetxt(file_path, self.denoised_signal, fmt='%.6f')
                
                # 同时保存对比图
                plot_path = file_path.replace('.txt', '_plot.png').replace('.csv', '_plot.png')
                self.signal_plot.save_plot(plot_path)
                
                QMessageBox.information(self, "成功", 
                                       f"结果已导出到:\n{file_path}\n\n"
                                       f"对比图已保存到:\n{plot_path}")
                self.statusBar().showMessage(f"结果已导出: {os.path.basename(file_path)}")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败:\n{str(e)}")

    def auto_save_result(self, improvement, strength):
        """自动保存结果"""
        try:
            # 创建输出目录
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成文件名
            timestamp = np.datetime64('now').astype(str).replace(':', '').replace('-', '').replace('T', '_').split('.')[0]
            filename = f"auto_save_{timestamp}_strength_{strength}_improvement_{improvement:.2f}x.txt"
            file_path = os.path.join(output_dir, filename)
            
            # 保存数据
            np.savetxt(file_path, self.denoised_signal, fmt='%.6f')
            
            # 保存图表
            plot_path = file_path.replace('.txt', '.png')
            self.signal_plot.save_plot(plot_path)
            
            self.statusBar().showMessage(f"已自动保存: {filename}")
            
        except Exception as e:
            print(f"自动保存失败: {e}")

    def save_current_plot(self):
        """保存当前图表"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存图表",
            "signal_plot.png",
            "PNG图像 (*.png);;JPEG图像 (*.jpg);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                self.signal_plot.save_plot(file_path)
                QMessageBox.information(self, "成功", f"图表已保存到:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"图表保存失败:\n{str(e)}")

    def batch_add_files(self):
        """批量添加文件"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择信号文件",
            "",
            "文本文件 (*.txt);;CSV文件 (*.csv);;所有文件 (*.*)"
        )
        
        for file_path in file_paths:
            self.batch_file_list.addItem(file_path)
        
        if file_paths:
            self.batch_process_btn.setEnabled(True)
            self.batch_log.append(f"✅ 添加了 {len(file_paths)} 个文件")

    def batch_clear_files(self):
        """清空批量文件列表"""
        self.batch_file_list.clear()
        self.batch_process_btn.setEnabled(False)
        self.batch_log.append("🗑️ 已清空文件列表")

    def batch_process(self):
        """开始批量处理"""
        if self.batch_file_list.count() == 0:
            QMessageBox.warning(self, "警告", "请先添加要处理的文件")
            return
        
        if self.denoiser is None:
            QMessageBox.critical(self, "错误", "AI模型未正确加载")
            return
        
        # 自动创建输出目录，不需要用户选择
        output_dir = "batch_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取当前去噪强度
        strength = self.strength_slider.value()
        
        # 准备文件列表
        file_list = []
        for i in range(self.batch_file_list.count()):
            file_list.append(self.batch_file_list.item(i).text())
        
        # 显示确认对话框
        reply = QMessageBox.question(self, "确认批量处理",
                                   f"即将批量处理 {len(file_list)} 个文件\n\n"
                                   f"去噪强度: {strength}\n"
                                   f"输出目录: {os.path.abspath(output_dir)}\n\n"
                                   f"确定开始处理吗？",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return
        
        # 禁用按钮，重置进度
        self.batch_process_btn.setEnabled(False)
        self.batch_add_btn.setEnabled(False)
        self.batch_clear_btn.setEnabled(False)
        self.batch_progress_bar.setRange(0, len(file_list))
        self.batch_progress_bar.setValue(0)
        self.batch_progress_label.setText(f"准备处理 {len(file_list)} 个文件...")
        
        # 清空日志并显示开始信息
        self.batch_log.clear()
        self.batch_log.append("🚀 开始批量处理...")
        self.batch_log.append(f"📁 输出目录: {os.path.abspath(output_dir)}")
        self.batch_log.append(f"⚡ 去噪强度: {strength}")
        self.batch_log.append(f"📄 文件数量: {len(file_list)}")
        self.batch_log.append("-" * 40)
        
        # 启动批量处理线程
        self.batch_thread = BatchDenoiserThread(self.denoiser, file_list, output_dir, strength)
        self.batch_thread.progress.connect(self.batch_progress_update)
        self.batch_thread.finished.connect(self.batch_finished)
        self.batch_thread.error.connect(self.batch_error)
        self.batch_thread.start()
        
        self.statusBar().showMessage(f"批量处理中... ({len(file_list)} 个文件)")

    def batch_progress_update(self, current, total, filename):
        """批量处理进度更新"""
        self.batch_progress_bar.setValue(current)
        progress_percent = (current / total) * 100
        
        if "✓" in filename:
            # 这是完成信号
            clean_filename = filename.replace(" ✓", "")
            self.batch_progress_label.setText(f"完成: {current}/{total} ({progress_percent:.1f}%)")
            self.batch_log.append(f"✅ 完成: {clean_filename}")
        else:
            # 这是开始处理信号
            self.batch_progress_label.setText(f"处理中: {current}/{total} ({progress_percent:.1f}%) - {filename}")
            self.batch_log.append(f"🔄 处理: {filename}")

    def batch_finished(self, results):
        """批量处理完成"""
        self.batch_process_btn.setEnabled(True)
        self.batch_add_btn.setEnabled(True)
        self.batch_clear_btn.setEnabled(True)
        
        success_count = len(results)
        output_dir = os.path.abspath(self.batch_thread.output_dir)
        
        self.batch_progress_label.setText(f"批量处理完成: {success_count} 个文件")
        self.batch_log.append("-" * 40)
        self.batch_log.append(f"🎉 批量处理完成!")
        self.batch_log.append(f"✅ 成功处理: {success_count} 个文件")
        self.batch_log.append(f"📁 输出目录: {output_dir}")
        
        # 自动滚动到日志底部
        self.batch_log.verticalScrollBar().setValue(self.batch_log.verticalScrollBar().maximum())
        
        self.statusBar().showMessage(f"批量处理完成: {success_count} 个文件")
        
        # 简单的完成提示，不自动打开文件夹
        QMessageBox.information(self, "批量处理完成", 
                               f"批量处理完成！\n\n"
                               f"成功处理: {success_count} 个文件\n"
                               f"输出目录: {output_dir}")

    def batch_error(self, filename, error_msg):
        """批量处理错误"""
        self.batch_log.append(f"❌ 错误 - {filename}: {error_msg}")

    def add_to_history(self, improvement, residual_error, strength):
        """添加到处理历史"""
        timestamp = np.datetime64('now').astype(str)
        history_item = {
            'timestamp': timestamp,
            'improvement': improvement,
            'residual_error': residual_error,
            'strength': strength,
            'signal_length': len(self.current_signal),
            'has_denoised': self.denoised_signal is not None
        }
        
        self.processing_history.append(history_item)
        
        # 更新历史列表
        item_text = f"{timestamp} - 强度:{strength} - 改善:{improvement:.2f}x - 误差:{residual_error:.4f}"
        self.history_list.addItem(item_text)
        
        # 保持最近50条记录
        if len(self.processing_history) > 50:
            self.processing_history.pop(0)
            self.history_list.takeItem(0)

    def load_history_item(self, item):
        """加载历史记录项"""
        # 这里可以实现加载历史记录的具体信号数据
        QMessageBox.information(self, "历史记录", f"选择了: {item.text()}")

    def clear_history(self):
        """清空历史记录"""
        self.processing_history.clear()
        self.history_list.clear()
        self.batch_log.append("历史记录已清空")

    def export_history_report(self):
        """导出历史报告"""
        if not self.processing_history:
            QMessageBox.warning(self, "警告", "没有历史记录可导出")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存历史报告",
            "processing_history_report.txt",
            "文本文件 (*.txt);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("AI电路噪声去除器 - 处理历史报告\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"生成时间: {np.datetime64('now')}\n")
                    f.write(f"总处理次数: {len(self.processing_history)}\n\n")
                    
                    for i, history in enumerate(self.processing_history):
                        f.write(f"{i+1}. {history['timestamp']}\n")
                        f.write(f"   去噪强度: {history['strength']}\n")
                        f.write(f"   改善倍数: {history['improvement']:.2f}x\n")
                        f.write(f"   残余误差: {history['residual_error']:.6f}\n")
                        f.write(f"   信号长度: {history['signal_length']}\n\n")
                
                QMessageBox.information(self, "成功", f"历史报告已导出到:\n{file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"报告导出失败:\n{str(e)}")

    def closeEvent(self, event):
        """关闭应用程序前的确认"""
        reply = QMessageBox.question(self, "确认退出",
                                   "确定要退出AI电路噪声去除器吗？",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 保存历史记录到文件
            try:
                history_data = {
                    'processing_history': self.processing_history,
                    'timestamp': np.datetime64('now').astype(str)
                }
                np.save('app_history.npy', history_data)
            except:
                pass  # 忽略保存错误
            
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    # 简单测试
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
