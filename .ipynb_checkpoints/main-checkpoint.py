import os
import sys
import torch
import glob
import pretty_midi
import shutil
import subprocess
from audio_utils import prepare_media, run_demucs
from subtitle_utils import generate_ass

# --- 1. 路径与参数配置区 ---
INPUT_FILE = "input/如果可以.wav"           # 输入文件名
OUTPUT_VIDEO_NAME = "output/如果可以_音高版.mp4" # 最终输出文件名
FONT_SIZE = 80                       # 字幕字号
CLEAN_UP = True                      # 是否在完成后删除临时文件

# 中间件目录配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
YOURMT3_PATH = os.path.join(BASE_DIR, "YourMT3")
TEMP_WAV = "temp_voice.wav"          # 临时音频名
TEMP_BG_VIDEO = "temp_bg.mp4"        # 临时背景视频
ASS_FILE = "output.ass"              # 临时字幕文件

# 挂载 YourMT3 路径
sys.path.extend([YOURMT3_PATH, os.path.join(YOURMT3_PATH, "amt/src")])
from infer import YourMT3Inference

# --------------------------

def main(input_path):
    original_cwd = os.getcwd()
    
    try:
        # 1. 准备音频与背景
        bg_video = prepare_media(input_path, TEMP_WAV, TEMP_BG_VIDEO)
        
        # 2. 音源分离提取人声
        vocal_wav = run_demucs(TEMP_WAV)
        abs_vocal_wav = os.path.abspath(vocal_wav)
        
        # 3. YourMT3 转录音高
        print("--- 步骤 3: YourMT3 模型转录 ---")
        midi_obj = None
        try:
            os.chdir(YOURMT3_PATH)
            engine = YourMT3Inference()
            # 必须传绝对路径，因为 chdir 了
            engine.run_transcription(abs_vocal_wav)
            
            # 捡取最新的 MIDI 结果
            midis = glob.glob("model_output/*.mid")
            midis.sort(key=os.path.getmtime, reverse=True)
            if not midis:
                raise FileNotFoundError("model_output 下没找到生成的 MIDI")
            
            midi_obj = pretty_midi.PrettyMIDI(midis[0])
            print(f"✅ 成功读取 MIDI 结果: {midis[0]}")
        finally:
            os.chdir(original_cwd) # 保证后续 FFmpeg 在正确路径运行

        # 4. 生成字幕并压制视频
        if midi_obj:
            print(f"--- 步骤 4: 生成字幕 (字号: {FONT_SIZE}) ---")
            generate_ass(midi_obj, ASS_FILE, fontsize=FONT_SIZE)
            
            print("--- 步骤 5: 最终视频合成 ---")
            abs_ass_path = os.path.abspath(ASS_FILE)
            safe_ass_path = abs_ass_path.replace("\\", "/").replace(":", "\\:")
            
            v_enc = "h264_nvenc" if torch.cuda.is_available() else "libx264"
            
            cmd = [
                'ffmpeg', '-y', 
                '-i', bg_video,
                '-vf', f"subtitles='{safe_ass_path}'",
                '-c:v', v_enc, 
                '-preset', 'fast', 
                '-c:a', 'copy', 
                OUTPUT_VIDEO_NAME
            ]
            
            # --- 关键：必须加入下面这一行来执行命令 ---
            subprocess.run(cmd, check=True) 
            
            print(f"🎉 任务大功告成！文件保存为: {OUTPUT_VIDEO_NAME}")

    except Exception as e:
        print(f"❌ 运行过程中出错: {e}")

    finally:
        # --- 5. 彻底清理临时资源 ---
        if CLEAN_UP:
            print("--- 步骤 6: 正在执行清理流程 ---")
            # 清理文件
            for f in [TEMP_WAV, TEMP_BG_VIDEO, ASS_FILE]:
                if os.path.exists(f):
                    os.remove(f)
                    print(f"  已删除文件: {f}")
            
            # 清理 Demucs 目录
            if os.path.exists("separated"):
                shutil.rmtree("separated")
                print("  已移除目录: separated")
            
            # 清理 YourMT3 的 model_output 缓存 (可选，建议清理以免混淆)
            mt3_out = os.path.join(YOURMT3_PATH, "model_output")
            if os.path.exists(mt3_out):
                for m in glob.glob(os.path.join(mt3_out, "*.mid")):
                    os.remove(m)
                print("  已重置 YourMT3 结果缓存")
            
            print("🧹 临时空间已全部释放。")

if __name__ == "__main__":
    main(INPUT_FILE)