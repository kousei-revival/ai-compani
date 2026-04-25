#!/usr/bin/env python3
"""
デモ用の画像（PNG）と BGM（WAV）を public/ に生成する。
BGM は標準ライブラリの数学だけで多層合成（和音進行・ベース・アルペジオ・短メロ）。
著作権: このリポジトリ内で生成した波形・グラデのみ（外部サンプル不使用）。
"""
from __future__ import annotations

import math
import struct
import wave
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
IMG = PUBLIC / "images"
AUDIO = PUBLIC / "audio"


def write_png(path: Path, w: int, h: int, pixel_fn) -> None:
    """pixel_fn(x,y) -> (r,g,b) 0-255"""
    rows = []
    for y in range(h):
        row = b"\x00"
        for x in range(w):
            r, g, b = pixel_fn(x, y)
            row += bytes((r & 255, g & 255, b & 255))
        rows.append(row)
    raw = b"".join(rows)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    body = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)


def midi_to_hz(note: float) -> float:
    """MIDI ノート番号 → 周波数（A4=69→440Hz）"""
    return 440.0 * (2 ** ((note - 69) / 12))


def write_ambient_wav(path: Path, seconds: float = 10.0, sr: int = 44100) -> None:
    """
    単調になりにくい BGM（標準ライブラリだけで合成）。
    - 4 和音のループ（Am → F → C → G のダイアトニック進行イメージ）
    - パッド（和音のサイン重ね）
    - ベース（拍に乗せたルート音）
    - アルペジオ（8分音符）
    - 短いメロディ（各ブロック頭にワンノート）
    ループのつなぎ目でクリックしにくいよう全体フェードあり。
    """
    n = int(sr * seconds)
    path.parent.mkdir(parents=True, exist_ok=True)

    # 各要素: (パッド用3音の MIDI, ベースのルート MIDI)
    chord_blocks: list[tuple[list[int], int]] = [
        ([57, 60, 64], 45),  # Am  A3 C4 E4  / A2
        ([53, 57, 60], 41),  # F   F3 A3 C4  / F2
        ([48, 52, 55], 36),  # C   C3 E3 G3  / C2
        ([55, 59, 62], 43),  # G   G3 B3 D4  / G2
    ]
    block_sec = seconds / len(chord_blocks)  # 10秒なら 2.5 秒 × 4

    # メロディ: 各ブロックの頭で鳴らす高めの1音（ペンタトニック風）
    melody_notes = [72, 71, 69, 76]  # C5 B4 A4 E5

    bpm = 118.0
    quarter = 60.0 / bpm
    eighth = quarter / 2.0
    two_pi = 2 * math.pi

    def chord_index_at(t: float) -> int:
        return int(t // block_sec) % len(chord_blocks)

    def pluck_env(t_local: float, note_len: float) -> float:
        """短いキラッとした減衰（アルペジオ用）"""
        if t_local <= 0 or t_local >= note_len:
            return 0.0
        atk = min(0.012, note_len * 0.15)
        if t_local < atk:
            return t_local / atk
        return math.exp(-10.0 * (t_local - atk) / max(note_len - atk, 1e-6))

    def bass_env(t_local: float, q: float) -> float:
        """四拍子の1拍ごとにベースを鳴らす簡易エンベロープ"""
        pos = t_local % q
        atk = 0.02
        if pos < atk:
            return pos / atk
        rel = (pos - atk) / (q - atk)
        return max(0.0, 1.0 - rel * 1.1)

    def frame(i: int) -> int:
        t = i / sr
        ci = chord_index_at(t)
        pad_notes, bass_root = chord_blocks[ci]
        t_block = t % block_sec

        v = 0.0

        # --- パッド: 各音を2系統ずつわずかにデチューンして厚み ---
        for note in pad_notes:
            f = midi_to_hz(note)
            v += 0.055 * math.sin(two_pi * f * t)
            v += 0.035 * math.sin(two_pi * f * 1.003 * t + 0.7)
        # ブロック境界で少しだけクロスフェード風に次和音を混ぜる（切り替わりを柔らかく）
        blend_w = 0.08
        if t_block > block_sec - blend_w:
            mix = (t_block - (block_sec - blend_w)) / blend_w
            nxt = chord_blocks[(ci + 1) % len(chord_blocks)][0]
            for note in nxt:
                f = midi_to_hz(note)
                v += mix * 0.04 * math.sin(two_pi * f * t)

        # --- ベース: 現在の和音ブロック内で四分音符ごとにルート ---
        beat_in_block = int(t_block / quarter)
        t_since_beat = t_block - beat_in_block * quarter
        f_bass = midi_to_hz(bass_root)
        env_b = bass_env(t_since_beat, quarter)
        # 少し倍音を足して「ベースっぽい」胴鳴り
        v += env_b * (
            0.14 * math.sin(two_pi * f_bass * t)
            + 0.05 * math.sin(two_pi * f_bass * 2 * t)
        )

        # --- アルペジオ: 8分音符で根・3度・5度を順に弾く ---
        idx8 = int(t_block / eighth)
        arp_pattern = [0, 1, 2, 1]
        tone_idx = arp_pattern[idx8 % len(arp_pattern)]
        arp_note = pad_notes[tone_idx % len(pad_notes)]
        t8 = t_block % eighth
        env_a = pluck_env(t8, eighth * 0.95)
        f_a = midi_to_hz(arp_note)
        v += env_a * 0.11 * math.sin(two_pi * f_a * t)

        # --- メロディ: ブロック先頭から約0.4秒だけ鐘型エンベロープ ---
        mel_note = melody_notes[ci % len(melody_notes)]
        if t_block < 0.4:
            env_m = math.sin((t_block / 0.4) * math.pi)
            f_m = midi_to_hz(mel_note)
            v += env_m * 0.09 * math.sin(two_pi * f_m * t)

        # マスター: はみ出し防止＆少し温かみ
        v = math.tanh(v * 1.35) * 0.92

        fade_in = min(1.0, t / 0.5)
        fade_out = min(1.0, (seconds - t) / 0.5)
        v *= fade_in * fade_out
        v = max(-1.0, min(1.0, v))
        return int(v * 32767)

    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        for i in range(n):
            w.writeframes(struct.pack("<h", frame(i)))


def main() -> None:
    # --- 画像1: イントロ（ティール〜藍）---
    def pix_intro(x, y):
        t = x / 1919.0
        u = y / 1079.0
        r = int(15 + (13 - 15) * t + (30 - 15) * u)
        g = int(118 + (80 - 118) * t + (160 - 118) * u)
        b = int(168 + (120 - 168) * t + (200 - 168) * u)
        return r, g, b

    write_png(IMG / "scene-intro.png", 1920, 1080, pix_intro)

    # --- 画像2: メイン（暖色グラデ + 柔らかい円形の光）---
    def pix_main(x, y):
        cx, cy = 960, 380
        d = math.hypot(x - cx, y - cy)
        spot = max(0.0, 1.0 - d / 520.0)
        r = int(254 - 40 * (x / 1920) + 35 * spot)
        g = int(243 - 70 * (y / 1080) + 25 * spot)
        b = int(230 - 90 * (x / 1920) + 15 * spot)
        return max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))

    write_png(IMG / "scene-main.png", 1920, 1080, pix_main)

    # --- 画像3: アウトロ（紫〜深紫）---
    def pix_outro(x, y):
        t = x / 1919.0
        r = int(120 + (60 - 120) * t)
        g = int(70 + (30 - 70) * t)
        b = int(200 + (140 - 200) * (y / 1079.0))
        return r, g, b

    write_png(IMG / "scene-outro.png", 1920, 1080, pix_outro)

    # --- 挿絵（ロゴ代わりのシンプルバッジ）---
    def pix_badge(x, y):
        cx, cy = 320, 200
        d = math.hypot(x - cx, y - cy)
        if d < 150:
            br = int(255 - (d / 150) * 40)
            return br, br - 20, br - 10
        return 248, 250, 252

    write_png(IMG / "badge-focus.png", 640, 400, pix_badge)

    write_ambient_wav(AUDIO / "bgm.wav", seconds=10.0)
    print("Wrote:", IMG / "scene-intro.png", IMG / "scene-main.png", IMG / "scene-outro.png")
    print("Wrote:", IMG / "badge-focus.png", AUDIO / "bgm.wav")


if __name__ == "__main__":
    main()
