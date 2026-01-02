# maimai店舗情報マップ - 日本サーバー

## 説明

### 1. 機能／コア機能の実装

#### JavaScript (geolocation_js)
```javascript
// 主要機能：
- navigator.geolocation.getCurrentPosition() - ユーザー位置の取得
- localStorage.setItem() - 座標をローカルストレージに保存
- URLクエリパラメータの変更 - URLを通じて座標をPythonに渡す
- 自動ページ更新 - location.reload()でアプリケーションの再読み込みをトリガー
```

**特徴**：
- 完全なエラー処理（権限拒否、タイムアウトなど）
- ユーザーフレンドリーなステータス表示
- 精度情報の表示（±X メートル）
- 保存された位置の表示チェック

#### Python 位置自動読み込み (main() 関数)
```python
# 主要ロジック：
1. query_params = st.query_params  # URLパラメータの読み取り
2. browser_latとbrowser_lonがある場合：
   - 座標値を解析
   - st.session_state['user_location']を設定
   - 成功メッセージを表示
   - URLパラメータをクリア

# メリット：
- 完全自動化、ユーザー操作不要
- 位置が即座にマップに反映
- パラメータクリアで重複読み込みを回避
```

### 2. 技術アーキテクチャ

#### 階層構成

| 階層 | 技術 | 機能 |
|------|------|------|
| ブラウザ | JavaScript | 位置情報取得、localStorage管理 |
| HTTP | URLクエリパラメータ | 座標の受け渡し |
| サーバー | Python/Streamlit | session_state管理 |
| UI | PyDeck | マップの可視化 |

#### データフロー

```
JavaScript (ブラウザ)
    ↓ localStorage
    ├─ user_lat: "35.6762"
    └─ user_lon: "139.6503"
    
    ↓ URLパラメータ
    
Python (Streamlit)
    ↓ session_state
    ├─ user_location: {lat: 35.6762, lon: 139.6503}
    
    ↓ PyDeck
    
マップ (UI)
    └─ 青い点 at (35.6762, 139.6503)
```

### 4. 主要なコードスニペット

#### 位置取得と更新
```javascript
navigator.geolocation.getCurrentPosition(function(position) {
    var lat = position.coords.latitude;
    var lon = position.coords.longitude;
    
    localStorage.setItem('user_lat', lat);
    localStorage.setItem('user_lon', lon);
    
    var url = new URL(window.location);
    url.searchParams.set('browser_lat', lat);
    url.searchParams.set('browser_lon', lon);
    window.history.replaceState({}, '', url.toString());
    
    setTimeout(function() { location.reload(); }, 1500);
});
```

#### Python 自動読み込み
```python
query_params = st.query_params
if 'browser_lat' in query_params and 'browser_lon' in query_params:
    lat = float(query_params['browser_lat'])
    lon = float(query_params['browser_lon'])
    st.session_state['user_location'] = {'lat': lat, 'lon': lon}
    st.success(f"🎉 ブラウザから位置を自動読み込みしました: ({lat:.6f}, {lon:.6f})")
```

## 🔧 技術詳細

### 使用するAPI
- **Geolocation API** - デバイス位置の取得
- **localStorage API** - ローカルデータストレージ
- **URL API** - クエリパラメータ管理
- **Streamlit Query Params** - URLパラメータの読み取り

### 依存関係
- Python 3.10+
- Streamlit
- Pandas
- PyDeck
- geopy

### ブラウザ要件
- Geolocation APIのサポート（すべてのモダンブラウザ）
- localStorageのサポート（すべてのモダンブラウザ）
- HTTPS接続（本番環境）

## 📝 使用方法

### アプリケーションの起動
```bash
cd /プロジェクトフォルダー
streamlit run Home.py
```
