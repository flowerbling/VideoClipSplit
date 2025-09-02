import cv2
import os
from scenedetect import SceneManager, FrameTimecode
from scenedetect.detectors import ContentDetector
from scenedetect.scene_manager import save_images, write_scene_list
from scenedetect.backends.opencv import VideoStreamCv2 # Explicitly import VideoStream

class VideoProcessor:
    def __init__(self):
        pass

    def process_video(self, video_path, output_dir, output_first_frame, save_segments, min_scene_len, progress_callback=None):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        video_stream = VideoStreamCv2(path=video_path) # Pass path as keyword argument
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(min_scene_len=min_scene_len)) # Pass min_scene_len
        
        # Detect scenes
        # Get total frames for progress calculation
        total_frames = int(video_stream._cap.get(cv2.CAP_PROP_FRAME_COUNT)) # Use length_in_frames attribute

        def _progress_callback(value, progress_value):
            if progress_callback:
                # current_frame = int(progress_value * total_frames)
                progress = progress_value / total_frames * 100
                progress_callback(progress)

        scene_manager.detect_scenes(video=video_stream, callback=_progress_callback)
        scene_list = scene_manager.get_scene_list()

        if not scene_list:
            print("No scenes detected.")
            return

        base_name = os.path.splitext(os.path.basename(video_path))[0]

        # Save first frame of each segment
        if output_first_frame:
            progress_callback(msg="状态：正在保存首帧...")
            save_images(
                scene_list,
                video_stream,
                num_images=1,
                output_dir=output_dir,
                image_name_template=f"{base_name}-scene-$SCENE_NUMBER-00.jpg"
            )

        # Save video segments
        if save_segments:
            progress_callback(msg="状态：正在保存视频片段...")
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            for i, scene in enumerate(scene_list):
                start_frame = scene[0].get_frames()
                end_frame = scene[1].get_frames()

                output_filename = os.path.join(output_dir, f"{base_name}-scene-{i+1:03d}.mp4")
                fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec for .mp4
                out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))

                cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                for frame_num in range(start_frame, end_frame):
                    ret, frame = cap.read()
                    if not ret:
                        break
                    out.write(frame)
                out.release()
            cap.release()
            
        print("状态：正在写入场景列表文件...")
        progress_callback(msg="状态：正在写入场景列表文件...")
        # Write scene list to a file
        with open(os.path.join(output_dir, f"{base_name}_scene_list.csv"), "w") as f:
            write_scene_list(f, scene_list)

        progress_callback(msg="状态：处理完成。")    
        print(f"Video processing complete for {video_path}")

if __name__ == "__main__":
    # Example usage (for testing)
    processor = VideoProcessor()
    # Replace with your actual video file and output directory for testing
    # processor.process_video("path/to/your/video.mp4", "output/directory", True, True)
    print("VideoProcessor class created. Add example usage for testing.")