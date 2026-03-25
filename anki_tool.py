import pandas as pd
import random
import os

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
WORD_COL       = df.columns[0]   # 標準的な表記
SPELLING_COL   = df.columns[1]   # 読み
DIFFICULTY_COL = df.columns[2]   # 語彙の難易度
POS_COL        = df.columns[3]   # 品詞1（词性）
GOSHU_COL      = df.columns[5]   # 語種（语种）

# ========= 4. 通用选择菜单函数 =========
def choose_from_list(title, options, allow_all=True, all_label="All (no filter)"):
    """
    通用菜单：传入标题和选项列表，返回选中的值，None 表示全选。
    """
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

# 展示难度时附上英文说明
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

# 第一层过滤
if selected_level:
    df_step1 = df[df[DIFFICULTY_COL].astype(str).str.contains(selected_level, na=False)]
else:
    df_step1 = df.copy()

if df_step1.empty:
    print(f"❌ No words found for difficulty '{selected_level}'.")
    exit()

print(f"\n  ✅ Difficulty: {selected_level or 'All'}  →  {len(df_step1)} words remaining.")

# ========= 6. 第二层：选语种（語種） =========
# 从第一层筛选结果中动态读取唯一值，排序后展示
goshu_options = sorted(df_step1[GOSHU_COL].dropna().astype(str).unique().tolist())

selected_goshu = choose_from_list(
    title="🌐 Step 2 — Choose word origin（語種）",
    options=goshu_options,
    allow_all=True,
    all_label="All origins (no filter)"
)

# 第二层过滤
if selected_goshu:
    df_step2 = df_step1[df_step1[GOSHU_COL].astype(str) == selected_goshu]
else:
    df_step2 = df_step1.copy()

if df_step2.empty:
    print(f"❌ No words found for 語種 '{selected_goshu}' under difficulty '{selected_level or 'All'}'.")
    exit()

print(f"\n  ✅ 語種: {selected_goshu or 'All'}  →  {len(df_step2)} words remaining.")

# ========= 7. 第三层：选词性（品詞1） =========
# 从第二层筛选结果中动态读取唯一值
pos_options = sorted(df_step2[POS_COL].dropna().astype(str).unique().tolist())

selected_pos = choose_from_list(
    title="🔤 Step 3 — Choose part of speech（品詞1）",
    options=pos_options,
    allow_all=True,
    all_label="All parts of speech (no filter)"
)

# 第三层过滤
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

# ========= 8. 最终结果汇总 =========
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
print("\n🎯 Let's study!  (y = I know it / n = I don't know it / q = quit)\n")

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
    input("  👉 Press Enter to reveal the spelling...")
    print(f"  🔤 Spelling: {word[SPELLING_COL]}")

    result = input("  ❓ Did you know it? (y/n/q): ").strip().lower()

    if result == "q":
        print("\n👋 Goodbye! Great work today.")
        break
    elif result == "n":
        if word not in wrong_words:
            wrong_words.append(word)
        print("  ❌ Added to wrong-answer bank.")
    elif result == "y":
        if word in wrong_words:
            wrong_words.remove(word)
            print("  ✅ Removed from wrong-answer bank. Nice!")
        else:
            print("  ✅ Nice work!")
    else:
        print("  ⚠️  Invalid input — please enter y, n, or q.")

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
