# maimai店舗情報マップ - 日本サーバー

Try it: https://eeezhisalt.top/maimai-map

## 説明

**特徴**：
- 完全なエラー処理（権限拒否、タイムアウトなど）
- ユーザーフレンドリーなステータス表示
- 精度情報の表示（±X メートル）
- 保存された位置の表示チェック


### 技術アーキテクチャ

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
