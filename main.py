import os
import random
import feedparser
import requests

def get_qiita_article():
    """Qiitaから人気記事（ストック数30以上）を1件取得"""
    url = "https://qiita.com/api/v2/items?query=stocks:>30&page=1&per_page=20"
    res = requests.get(url, headers={"Accept": "application/json"})
    if res.status_code == 200 and res.json():
        item = random.choice(res.json())
        return {"title": item["title"], "url": item["url"], "site": "Qiita"}
    return None

def get_zenn_article():
    """ZennのトレンドRSSから記事を1件取得"""
    feed = feedparser.parse("https://zenn.dev/feed")
    if feed.entries:
        item = random.choice(feed.entries[:20]) # 最新20件からランダム
        return {"title": item.title, "url": item.link, "site": "Zenn"}
    return None

def main():
    # QiitaまたはZennからランダムに選択 (50%の確率)
    fetch_func = random.choice([get_qiita_article, get_zenn_article])
    article = fetch_func()

    # 片方が失敗した場合はもう一方を試すフォールバック処理
    if not article:
        fallback_func = get_zenn_article if fetch_func == get_qiita_article else get_qiita_article
        article = fallback_func()

    if not article:
        print("記事の取得に失敗しました。")
        return

    # アイコンとメッセージの組み立て
    site_emoji = "🟢" if article["site"] == "Qiita" else "🔵"
    message = {
        "text": (
            f"☀️ **【今朝のおすすめ記事 ({site_emoji} {article['site']})】**\n\n"
            f"📖 **{article['title']}**\n"
            f"🔗 {article['url']}\n\n"
            "💬 *コメントやスタンプでリアクションしてみましょう！！*"
        )
    }

    # Google Chatへ送信
    webhook_url = os.environ.get("WEBHOOK_URL")
    if webhook_url:
        res = requests.post(webhook_url, json=message)
        print(f"[{article['site']}] 送信完了: ステータスコード {res.status_code}")
    else:
        print("エラー: WEBHOOK_URLが設定されていません。")

if __name__ == "__main__":
    main()
