import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QCheckBox, QFileDialog, QMessageBox, QSpinBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont # Import QFont
import os # Import os module
from video_processor import VideoProcessor

class WorkerThread(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, video_path, output_dir, output_first_frame, save_segments, min_scene_len):
        super().__init__()
        self.video_path = video_path
        self.output_dir = output_dir
        self.output_first_frame = output_first_frame
        self.save_segments = save_segments
        self.min_scene_len = min_scene_len # New parameter
        self.processor = VideoProcessor()

    def run(self):
        try:
            self.progress.emit("状态: 正在处理视频...")
            self.processor.process_video(
                self.video_path,
                self.output_dir,
                self.output_first_frame,
                self.save_segments,
                self.min_scene_len, # Pass new parameter
                progress_callback=self.update_progress_callback # Pass callback for progress updates
            )
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def update_progress_callback(self, progress_value: str = "", msg: str = ""):
        # This callback will be called by scenedetect
        # We can emit a signal to update the GUI with progress
        if msg:
            self.progress.emit(msg)
        else:
            self.progress.emit(f"状态: 正在处理... {progress_value:.1f}%")


class VideoClipSplitterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("视频分镜头工具")
        self.setGeometry(100, 100, 600, 300)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # 视频文件选择
        video_file_layout = QHBoxLayout()
        self.video_file_label = QLabel("视频文件:")
        self.video_file_input = QLineEdit()
        self.video_file_input.setPlaceholderText("请选择视频文件")
        self.video_file_button = QPushButton("选择文件")
        self.video_file_button.clicked.connect(self.select_video_file)
        video_file_layout.addWidget(self.video_file_label)
        video_file_layout.addWidget(self.video_file_input)
        video_file_layout.addWidget(self.video_file_button)
        main_layout.addLayout(video_file_layout)

        # 输出目录选择
        output_dir_layout = QHBoxLayout()
        self.output_dir_label = QLabel("输出目录:")
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setPlaceholderText("请选择输出目录")
        self.output_dir_button = QPushButton("选择目录")
        self.output_dir_button.clicked.connect(self.select_output_directory)
        output_dir_layout.addWidget(self.output_dir_label)
        output_dir_layout.addWidget(self.output_dir_input)
        output_dir_layout.addWidget(self.output_dir_button)
        main_layout.addLayout(output_dir_layout)

        # 选项
        options_layout = QHBoxLayout()
        self.output_first_frame_checkbox = QCheckBox("输出视频首帧")
        self.output_first_frame_checkbox.setChecked(True) # 默认选中
        self.save_segments_checkbox = QCheckBox("将视频分段保存")
        
        self.min_scene_len_label = QLabel("最小分镜帧数:")
        self.min_scene_len_spinbox = QSpinBox()
        self.min_scene_len_spinbox.setRange(1, 99999) # 合理的范围
        self.min_scene_len_spinbox.setValue(15) # 默认值，scenedetect 默认是 15 帧

        options_layout.addWidget(self.output_first_frame_checkbox)
        options_layout.addWidget(self.save_segments_checkbox)
        options_layout.addWidget(self.min_scene_len_label)
        options_layout.addWidget(self.min_scene_len_spinbox)
        options_layout.addStretch(1) # 填充空白
        main_layout.addLayout(options_layout)

        # 开始处理按钮
        self.process_button = QPushButton("开始处理")
        self.process_button.clicked.connect(self.start_processing)
        main_layout.addWidget(self.process_button)

        # 状态显示
        self.status_label = QLabel("状态: 等待操作...")
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

    def select_video_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择视频文件", "", "视频文件 (*.mp4 *.avi *.mov *.mkv);;所有文件 (*)")
        if file_path:
            self.video_file_input.setText(file_path)

    def select_output_directory(self):
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        dir_dialog = QFileDialog()
        dir_path = dir_dialog.getExistingDirectory(self, "选择输出目录", desktop_path)
        if dir_path:
            self.output_dir_input.setText(dir_path)

    def start_processing(self):
        video_file = self.video_file_input.text()
        output_dir = self.output_dir_input.text()
        output_first_frame = self.output_first_frame_checkbox.isChecked()
        save_segments = self.save_segments_checkbox.isChecked()

        if not video_file:
            QMessageBox.warning(self, "警告", "请选择一个视频文件。")
            return
        if not output_dir:
            QMessageBox.warning(self, "警告", "请选择一个输出目录。")
            return

        self.status_label.setText("状态: 正在处理视频...")
        self.process_button.setEnabled(False) # Disable button during processing
        min_scene_len = self.min_scene_len_spinbox.value() # Get value from spinbox

        self.worker_thread = WorkerThread(video_file, output_dir, output_first_frame, save_segments, min_scene_len)
        self.worker_thread.finished.connect(self.processing_finished)
        self.worker_thread.error.connect(self.processing_error)
        self.worker_thread.progress.connect(self.update_status_label)
        self.worker_thread.start()

    def processing_finished(self):
        QMessageBox.information(self, "信息", "视频处理完成！")
        self.status_label.setText("状态: 处理完成。")
        self.process_button.setEnabled(True)
        # 尝试加载并显示第一帧作为预览
        # output_dir = self.output_dir_input.text()
        # video_file = self.video_file_input.text()
        # base_name = os.path.splitext(os.path.basename(video_file))[0]
        # first_frame_path = os.path.join(output_dir, f"{base_name}-scene-001-00.jpg") # Assuming first scene's first frame
        # pass

    def processing_error(self, error_message):
        QMessageBox.critical(self, "错误", f"视频处理失败: {error_message}")
        self.status_label.setText("状态: 处理失败。")
        self.process_button.setEnabled(True)

    def update_status_label(self, message):
        self.status_label.setText(message)


def main():
    app = QApplication(sys.argv)
    

    ex = VideoClipSplitterApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
