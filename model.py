import json
from janome.tokenizer import Tokenizer
import os

# --- グローバル変数 ---
pn_declinable_dict = []
pn_wago_dict = []
jiwc_dict = []
tokenizer = None

# ▼▼▼ 変更点 ▼▼▼
# ジャンルごとに映画レビューデータを保持する辞書
all_movie_reviews = {} 
# 対応するジャンルのリスト（ここの名前がJSONファイル名と対応します）
GENRES = ['anime', 'love', 'action','SF', 'adventure', 'comedy', 'fantasy', 'horror', 'suspense'] 
# 感情キーの順番をuserfeeling関数と合わせる（重要）
EMOTION_KEYS = ["悲しい", "不安", "怒り", "嫌悪感", "信頼感", "驚き", "楽しい"]
# ▲▲▲ 変更点 ▲▲▲

# --- ① データ読み込み関数 (修正) ---
def load_data():
    global pn_declinable_dict, pn_wago_dict, jiwc_dict, tokenizer, all_movie_reviews

    tokenizer = Tokenizer()

    # 感情分析辞書の読み込み（ここは変更なし）
    # ... (前回のコードと同じなので省略) ...
    try:
        with open('data/pn.csv.m3.120408.trim', 'r', encoding='utf-8-sig') as f:
            pn_declinable_dict = f.readlines()
        with open('data/wago.121808.pn', 'r', encoding='utf-8') as f:
            pn_wago_dict = f.readlines()
        with open('data/JIWC-C_2018_2019.csv', 'r', encoding='utf-8') as f:
            jiwc_dict = f.readlines()
    except Exception as e:
        print(f"感情辞書の読み込みに失敗しました: {e}")


    # ▼▼▼ 変更点 ▼▼▼
    # ジャンルごとのJSONファイルを全て読み込む
    for genre in GENRES:
        file_path = f'static/json/{genre}_movie_sentiment_summary.json'
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    all_movie_reviews[genre] = json.load(f)
                print(f"✅ Loaded {file_path}")
            except Exception as e:
                print(f"❌ Failed to load {file_path}: {e}")
        else:
            print(f"⚠️ Warning: JSON file not found at {file_path}")
    # ▲▲▲ 変更点 ▲▲▲

# --- ② 感情分析関数群 (変更なし) ---
# ... (textcheck, userfeeling関数は前回のコードと全く同じなので省略) ...
def textcheck(user, boxname, check=0):
    for boxword in boxname:
        if user.find(boxword) != -1:
            check += 1
    return check

def userfeeling(user, textbox, textbox2, feeldic):
    # (前回のコードをそのままここに記述)
    # ...
    pleasure = 0.0
    sad, afraid, angry, hate, trust, surprise, happy = 0, 0, 0, 0, 0, 0, 0
    feel = [sad, afraid, angry, hate, trust, surprise, happy]
    # (以下、省略) ...
    return pleasure, feel # pleasureは今回は使いませんが、関数はそのまま流用

# --- ③ 推薦ロジックのメイン関数 (修正) ---
def get_recommendations(user_text, genre):
    if not user_text or not genre:
        return []

    # 1. ユーザーの入力を感情分析 (pleasureスコアは今回比較に使わない)
    _, user_feel_scores = userfeeling(user_text, pn_declinable_dict, pn_wago_dict, jiwc_dict)

    # 2. 選択されたジャンルのレビューリストを取得
    reviews_for_genre = all_movie_reviews.get(genre, [])
    if not reviews_for_genre:
        print(f"Warning: No review data found for genre '{genre}'")
        return []

    results = []
    # 3. ジャンル内の全映画レビューと比較
    for review_data in reviews_for_genre:
        
        # 4. JSONから感情スコアを正しい順番でリスト化
        review_scores = [review_data.get(key, 0.0) for key in EMOTION_KEYS]
        
        # 5. 二乗和誤差を計算
        error = 0
        if len(user_feel_scores) == len(review_scores):
            for i in range(len(user_feel_scores)):
                error += (user_feel_scores[i] - review_scores[i]) ** 2
        
        results.append({
            'title': review_data.get("映画タイトル", "タイトル不明"),
            'synopsis': review_data.get("あらすじ", "あらすじが見つかりません。"),
            'error': error
            # 'text'キーはもう無いので削除
        })

    # 6. 誤差が小さい順に並び替え
    sorted_results = sorted(results, key=lambda x: x['error'])

    # 7. 上位3件を返す
    return sorted_results[:3]