import subprocess
import os
import shutil
import sys
import torch

def prepare_media(input_path, temp_raw_audio, temp_video_no_sub):
    """提取音频并准备背景视频"""
    print("--- 步骤 1: 准备素材 ---")
    
    # 提取音频 (这步通常很快)
    subprocess.run(['ffmpeg', '-y', '-i', input_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', temp_raw_audio], check=True, capture_output=True)
    
    # 如果是音频，生成黑底视频
    if not mimetypes_guess_is_video(input_path):
        print("--- 正在快速生成黑底背景视频 ---")
        duration_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_path]
        duration = float(subprocess.check_output(duration_cmd).decode('utf-8').strip())
        
        # 优化后的 FFmpeg 命令
        v_encoder = "h264_nvenc" if torch.cuda.is_available() else "libx264"
        
        fast_gen_cmd = [
            'ffmpeg', '-y', 
            '-f', 'lavfi', '-i', f'color=c=black:s=1280x720:r=5:d={duration}', # 降帧到 5fps
            '-i', input_path, 
            '-c:v', v_encoder, 
            '-preset', 'p1' if v_encoder == "h264_nvenc" else "ultrafast", # 使用最快预设
            '-c:a', 'aac', 
            '-shortest', temp_video_no_sub
        ]
        subprocess.run(fast_gen_cmd, check=True, capture_output=True)
        
    return input_path if mimetypes_guess_is_video(input_path) else temp_video_no_sub

def run_demucs(input_wav):
    """运行音源分离"""
    print("--- 步骤 2: 音源分离 (Demucs) ---")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # 因为取消了 -o 参数，输入文件放在最后
    cmd = [
        sys.executable, "-m", "demucs.separate", 
        "-d", device, 
        "--two-stems", "vocals", 
        input_wav
    ]
    subprocess.run(cmd, check=True)
    
    # Demucs 默认输出逻辑是：./separated/htdemucs/{文件名}/vocals.wav
    filename = os.path.splitext(os.path.basename(input_wav))[0]
    vocal_path = os.path.join("separated", "htdemucs", filename, "vocals.wav")
    
    print(f"--- 预期人声路径: {vocal_path} ---")
    return vocal_path

def mimetypes_guess_is_video(path):
    import mimetypes
    mime = mimetypes.guess_type(path)[0]
    return mime and mime.startswith('video')