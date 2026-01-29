def midi_number_to_name(midi_number):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_number // 12) - 1
    return f"{notes[midi_number % 12]}{octave}"

def generate_ass(midi_obj, output_ass, fontsize=80):
    """生成自带位置信息的 ASS 字幕，确保正中心对齐"""
    with open(output_ass, 'w', encoding='utf-8') as f:
        # 1. 补充 ScaledBorderAndShadow，确保大字号下描边正常
        f.write("[Script Info]\n")
        f.write("ScriptType: v4.00+\n")
        f.write("PlayResX: 1280\n")
        f.write("PlayResY: 720\n")
        f.write("ScaledBorderAndShadow: yes\n\n")

        # 2. 样式定义
        f.write("[V4+ Styles]\n")
        f.write("Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
        # Alignment=5 是绝对中心
        f.write(f"Style: Default,Arial,{fontsize},&H00FFFF,&H000000,1,3,2,5,10,10,10,1\n\n")

        f.write("[Events]\n")
        f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        
        # 音轨筛选逻辑
        target_instrument = next((i for i in midi_obj.instruments if 'singing' in i.name.lower() or 'vocal' in i.name.lower()), None)
        if not target_instrument:
            target_instrument = max(midi_obj.instruments, key=lambda i: len(i.notes))
        
        print(f"✅ 正在从音轨 [{target_instrument.name}] 提取音符...")

        def format_time_ass(seconds):
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            ms = int((seconds % 1) * 100) # ASS 使用的是百分秒 (Centiseconds)
            return f"{h}:{m:02d}:{s:02d}.{ms:02d}"

        for note in sorted(target_instrument.notes, key=lambda x: x.start):
            if note.end - note.start < 0.05: continue
            start = format_time_ass(note.start)
            end = format_time_ass(note.end)
            pitch = midi_number_to_name(note.pitch)
            # 写入对话行
            f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{pitch}\n")