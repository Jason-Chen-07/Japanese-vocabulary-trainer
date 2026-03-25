import pandas as pd
import random
import os
import sys

# ========= 0. 跨平台单键读取 =========
if sys.platform == "win32":
    import msvcrt

    def get_single_key(prompt):
        print(prompt, end="", flush=True)
        while True:
            key = msvcrt.getwch()
            if key in ("\x00", "\xe0"):
                msvcrt.getwch()
                continue
            if key in ("\r", "\n"):
                print()
                return "enter"
            if key == " ":
                print()
                return "space"
            if key.lower() == "q":
                print()
                return "q"
            print(f"\n  ⚠️  Invalid key. Press Enter(✅) / Space(❌) / Q(quit)", end="", flush=True)

else:
    # Mac / Linux
    import tty
    import termios

    def get_single_key(prompt):
        print(prompt, end="", flush=True)
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                key = sys.stdin.read(1)
                # 处理方向键等转义序列（ESC + [ + X），直接吞掉
                if key == "\x1b":
                    sys.stdin.read(2)
                    continue
                if key in ("\r", "\n"):
                    print()
                    return "enter"
                if key == " ":
                    print()
                    return "space"
                if key.lower() == "q":
                    print()
                    return "q"
                # Ctrl+C 手动触发中断
                if key == "\x03":
                    raise KeyboardInterrupt
                print(f"\n  ⚠️  Invalid key. Press Enter(✅) / Space(❌) / Q(quit)", end="", flush=True)
        finally:
            # 无论如何都还原终端设置，防止终端卡住
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# ========= 1. File Path =========
file_path = r"C:\Users\chenj\OneDrive\goi - 副本.xlsx"

if not os.path.exists(file_path):
    print(f"❌ File not found: {file_path}")
    exit()

# ========= 2. Read Excel =========
try:
    df = pd.read_excel(file_path)
except Exception as e:
    print("❌ Failed to read Excel:", e)
    exit()

print("✅ File loaded successfully!")
print("📊 Detected columns:", list(df.columns))

# ========= 3. Column Settings =========
WORD_COL       = df.columns[0]
SPELLING_COL   = df.columns[1]
DIFFICULTY_COL = df.columns[2]
POS_COL        = df.columns[3]
GOSHU_COL      = df.columns[5]

# ========= 4. 通用选择菜单函数 =========
def choose_from_list(title, options, allow_all=True, all_label="All (no filter)"):
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)
    if allow_all:
        print(f"  [0]  {all_label}")
    for i, opt in enumerate(options, 1):
        print(f"  [{i}]  {opt}")
    print("=" * 50)
    max_choice = len(options)
    while True:
        choice = input(f"👉 Enter a number (0–{max_choice}): ").strip()
        if allow_all and choice == "0":
            return None
        elif choice.isdigit() and 1 <= int(choice) <= max_choice:
            return options[int(choice) - 1]
        else:
            print(f"⚠️  Invalid input. Please enter 0 to {max_choice}.")

# ========= 5. 第一层：选难度 =========
LEVELS = ["初級前半", "初級後半", "中級前半", "中級後半", "上級前半", "上級後半"]
LEVEL_LABELS = {
    "初級前半": "Beginner  (Part 1)",
    "初級後半": "Beginner  (Part 2)",
    "中級前半": "Intermediate (Part 1)",
    "中級後半": "Intermediate (Part 2)",
    "上級前半": "Advanced  (Part 1)",
    "上級後半": "Advanced  (Part 2)",
}

level_display = [f"{lvl}  ({LEVEL_LABELS[lvl]})" for lvl in LEVELS]

print("\n" + "=" * 50)
print("  📚 Step 1 — Choose difficulty level")
print("=" * 50)
print("  [0]  All levels (mix everything)")
for i, label in enumerate(level_display, 1):
    print(f"  [{i}]  {label}")
print("=" * 50)

selected_level = None
while True:
    choice = input(f"👉 Enter a number (0–{len(LEVELS)}): ").strip()
    if choice == "0":
        selected_level = None
        break
    elif choice.isdigit() and 1 <= int(choice) <= len(LEVELS):
        selected_level = LEVELS[int(choice) - 1]
        break
    else:
        print(f"⚠️  Invalid input.")

if selected_level:
    df_step1 = df[df[DIFFICULTY_COL].astype(str).str.contains(selected_level, na=False)]
else:
    df_step1 = df.copy()

if df_step1.empty:
    print(f"❌ No words found for difficulty '{selected_level}'.")
    exit()

print(f"\n  ✅ Difficulty: {selected_level or 'All'}  →  {len(df_step1)} words remaining.")

# ========= 6. 第二层：选语种 =========
goshu_options = sorted(df_step1[GOSHU_COL].dropna().astype(str).unique().tolist())
selected_goshu = choose_from_list(
    title="🌐 Step 2 — Choose word origin（語種）",
    options=goshu_options,
    allow_all=True,
    all_label="All origins (no filter)"
)

if selected_goshu:
    df_step2 = df_step1[df_step1[GOSHU_COL].astype(str) == selected_goshu]
else:
    df_step2 = df_step1.copy()

if df_step2.empty:
    print(f"❌ No words found for 語種 '{selected_goshu}'.")
    exit()

print(f"\n  ✅ 語種: {selected_goshu or 'All'}  →  {len(df_step2)} words remaining.")

# ========= 7. 第三层：选词性 =========
pos_options = sorted(df_step2[POS_COL].dropna().astype(str).unique().tolist())
selected_pos = choose_from_list(
    title="🔤 Step 3 — Choose part of speech（品詞1）",
    options=pos_options,
    allow_all=True,
    all_label="All parts of speech (no filter)"
)

if selected_pos:
    df_step3 = df_step2[df_step2[POS_COL].astype(str) == selected_pos]
else:
    df_step3 = df_step2.copy()

if df_step3.empty:
    print(f"\n❌ No words found for the combination:")
    print(f"   Difficulty : {selected_level or 'All'}")
    print(f"   語種       : {selected_goshu or 'All'}")
    print(f"   品詞1      : {selected_pos or 'All'}")
    print("👉 Please restart and try a different combination.")
    exit()

# ========= 8. 汇总 =========
words = df_step3.to_dict(orient="records")

print("\n" + "=" * 50)
print("  📋 Study Session Configuration")
print("=" * 50)
print(f"  Difficulty : {selected_level or 'All levels'}")
print(f"  語種       : {selected_goshu or 'All origins'}")
print(f"  品詞1      : {selected_pos or 'All POS'}")
print(f"  Word count : {len(words)}")
print("=" * 50)

# ========= 9. Wrong-Answer Bank =========
wrong_words = []
print("\n🎯 Let's study!")
print("   ↵ Enter  =  ✅ I know it")
print("   Space    =  ❌ I don't know it")
print("   Q        =  🚪 Quit\n")

# ========= 10. Main Loop =========
while True:
    if wrong_words and random.random() < 0.6:
        word = random.choice(wrong_words)
        tag  = "🔁 Review"
    else:
        word = random.choice(words)
        tag  = "🆕 New"

    print("\n" + "=" * 50)
    print(f"  {tag}")
    print(f"  📌 Word:     {word[WORD_COL]}")

    get_single_key("  👉 Press any key to reveal spelling... ")
    print(f"  🔤 Spelling: {word[SPELLING_COL]}")

    key = get_single_key("  ❓ Know it?  [ ↵ Enter = ✅  |  Space = ❌  |  Q = quit ] ")

    if key == "q":
        print("\n👋 Goodbye! Great work today.")
        break
    elif key == "space":
        if word not in wrong_words:
            wrong_words.append(word)
        print("  ❌ Added to wrong-answer bank.")
    elif key == "enter":
        if word in wrong_words:
            wrong_words.remove(word)
            print("  ✅ Removed from wrong-answer bank. Nice!")
        else:
            print("  ✅ Nice work!")

    print(f"  📌 Wrong-answer bank: {len(wrong_words)} word(s)")

# ========= 11. Session Summary =========
print("\n" + "=" * 50)
print("  📊 Session Summary")
print("=" * 50)
print(f"  Difficulty : {selected_level or 'All levels'}")
print(f"  語種       : {selected_goshu or 'All origins'}")
print(f"  品詞1      : {selected_pos or 'All POS'}")
print(f"  Total words: {len(words)}")
print(f"  Still unsure: {len(wrong_words)} word(s)")
if wrong_words:
    print("\n  🔁 Words to review next time:")
    for w in wrong_words:
        print(f"     • {w[WORD_COL]}  →  {w[SPELLING_COL]}")
print("=" * 50)
