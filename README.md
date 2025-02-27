# Rika

一個基於 Python 的 Discord Bot，可以播放音樂，搜索 Youtube 影片，等等。(Minimal 版本不提供播放音樂的功能)

> 專案介紹：[目錄結構](#結構概覽)

## 使用教學

> 可以先看 [入門最推薦運行方式](#方法-2使用命令行運行機器人--後端-入門最推薦)。

### MongoDB

> 你需要先注冊一個 MongoDB 賬號，然後創建一個新的 Cluster。  
> 在 Cluster 中創建一個新的 Database。  
> 將你的 MongoDB 連接字符串 `DB_STRING` (形如 `mongodb+srv://...`) 複製到後面的步驟中。

### 安裝依賴

```bash
apt-get install ffmpeg libopus0 git curl lsof
pip install -r requirements.txt
```

如果需要開發，請額外安裝開發依賴

```bash
pip install -r requirements.dev.txt
```

### Rika 後端

設置環境變數

```py
RIKA_MODE = {dev, stag, prod}
RIKA_DB_STRING = {your mongoDB link}
PORT = {your backend port}
```

> `PORT`通常設置成`5000`。如果你在 Heroku 上部署，`PORT` 會自動設置，不需要手動設置。

使用命令行**單獨**運行後端（開發模式）**(建議不要用這個，除非對專案已經很熟悉了)**

```bash
. script/apidev.sh
```

> `apidev.sh` 使用開發模式運行後端，自動開啓熱加載功能。

### Discord Bot 機器人

#### 方式 1：使用 VSCode **單獨** 運行機器人：

- 使用 Run and Debug 功能運行：
  - `Jurigged: Hot Reload` (熱加載模式) **[開發 Bot 時推薦，但速度較慢]**  
    或
  - `Python: Build and Run` (普通模式) **[速度較快]**。

#### 方法 2：使用命令行運行機器人 + 後端 **[入門最推薦]**

```bash
. script/run.sh
```

上面這個命令在部署 Docker 容器時會自動運行。

設置環境變數

```py
RIKA_DISCORD_BOT_TOKEN = {your discord bot token}
RIKA_DISCORD_BOT_TYPE = {staged or production}
RIKA_DISCORD_BOT_DB_STRING = {your mongoDB link}
```

### 强制停止後端

```bash
. script/kill_backend.sh
```

### 部署

使用 Dockerfile 部署。

## 結構（概覽）

```bash
src
├── api # Bot 用於與後端 API 通信的函數（非必要，可以直接用 requests，httpx，curl 等等的方式跟後端交互）
├── backend # 後端主要邏輯
│   ├── crud # 操作 MongoDB 的封裝函數
│   ├── db # MongoDB 連接配置
│   ├── services # 後端服務的業務邏輯
│   │  ├── search.py # Youtube 影片關鍵字搜索功能
│   ├── utils # 工具函數
│   ├── app.py # FastAPI 主入口，包含路由（API）
├── commands # Bot 指令
│   ├── gizmo.py # 無歸類的有趣指令
│   ├── music.py # 音樂功能指令
│   ├── voice.py # 語音頻道有關的指令
├── messages # Bot 推送給用戶的消息
├── modules # Bot 業務邏輯
├── utils # 工具函數
├── bot.py # Bot 加載功能 cogs 的地方 (雖然 cogs 已經在本專案中部分廢棄，但還是有部分遺留 cogs 的設計模式)
├── main.py # 主入口
```
