# MonoLuck-pi

## 系統需求
- Raspberry Pi 3B+ 以上
- SARY485 鎖控板
- USB 讀卡機 / PN532 (I2C Mode)
- Python 3.8 以上 (建議使用 venv)
- pm2 (建議)
---
## 執行腳本說明
- `ReadCard.py`：鎖櫃主程式（讀卡機）
- `ReadCardUsePN532.py`：鎖櫃主程式（PN532）
- `ReadLockerStatus.py`：鎖櫃狀態監控
- `Unlock.py`：鎖櫃強制解鎖
- `OfflineData.py`：離線資料處理

## 其他檔案說明
- `KeyeventReader.py`：讀卡機讀卡模組
- `Locker.py`：鎖櫃控制模組
- `MonoLock.py`：伺服器資料處理模組
- `PN532_test.py`：PN532 讀卡測試程式
- `.env.example`：環境變數範例
- `ecosystem.config.json`：pm2 設定檔
- `requirements.txt`：python 套件清單

---
## 快速部屬
1. 啟用 I2C （若要使用 PN532）
```bash
sudo raspi-config
```
2. 安裝相關套件
```bash
# python
sudo apt install python3 python3-pip python3-venv python3-dev gcc 
# nodejs
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - &&sudo apt-get install -y nodejs
# pm2 + 開機自啟
npm i -g pm2
pm2 startup
```
3. 建立 venv （建議）
```bash
python3 -m venv .venv
source .venv/bin/activate
```
4. 安裝 python 套件
```bash
pip install -r requirements.txt
```
5. 填寫 env
```bash
cp .env.example .env
```

- 環境變數相關說明，請參考 [Wiki](https://github.com/monosparta/MonoLock-cms-Back/wiki/env#%E6%A8%B9%E8%8E%93%E6%B4%BE)  
6. 修改 pm2 啟動腳本  （若要使用 PN532）  
- 將 `ecosystem.config.json` 內 `MonoLock - ReadCard` 的 `script` 從 `ReadCard.py` 改為 `ReadCardUsePN532.py`  
```json
{
    "name": "MonoLock - ReadCard",
    "script": "ReadCardUsePN532.py",
    ...
}
```
7. 啟動專案
```bash
pm2 relaod ecosystem.config.json
```
