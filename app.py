from flask import Flask, render_template, request
import model

app = Flask(__name__)

# アプリケーション起動時に、モデルと全ジャンルのデータをロードする
model.load_data()

@app.route('/')
def index():
    """トップページを表示"""
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    """結果ページを表示"""
    try:
        # フォームから'user_text'と'genre'のデータを取得
        user_text = request.form['user_text']
        genre = request.form['genre'] # ← 追加

        # model.pyの関数に、テキストとジャンルの両方を渡す
        recommendations = model.get_recommendations(user_text, genre) # ← 変更

        # 結果をresult.htmlに渡して表示
        return render_template('result.html', recommendations=recommendations, genre=genre)
    except Exception as e:
        print(f"Error processing request: {e}")
        return render_template('index.html', error_message="処理中にエラーが発生しました。もう一度お試しください。")

if __name__ == '__main__':
    app.run(debug=True)