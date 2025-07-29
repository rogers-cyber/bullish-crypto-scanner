import ccxt
import pandas as pd
from ta.trend import EMAIndicator, MACD, ADXIndicator
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

# =============================
# Streamlit UI
# =============================
st.set_page_config(page_title="Bullish Crypto Scanner", layout="wide")
st.title("📊 Bullish Crypto Screener")
timeframe = st.selectbox("Select timeframe", ["1h", "4h", "1d"], index=1)

# =============================
# Exchange Setup
# =============================
exchange = ccxt.binance({
    'enableRateLimit': True,
    'headers': {
        'User-Agent': 'Mozilla/5.0 (compatible; StreamlitBot/1.0)'
    }
})

limit = 200

symbols = [
    "BTC/USDT","ETH/USDT","BNB/USDT","SOL/USDT","USDC/USDT",
    "XRP/USDT","DOGE/USDT","TRX/USDT","TON/USDT","ADA/USDT",
    "AVAX/USDT","SHIB/USDT","LINK/USDT","BCH/USDT","DOT/USDT",
    "NEAR/USDT","SUI/USDT","LEO/USDT","DAI/USDT","APT/USDT",
    "LTC/USDT","UNI/USDT","TAO/USDT","PEPE/USDT","ICP/USDT",
    "FET/USDT","KAS/USDT","FDUSD/USDT","XMR/USDT","RENDER/USDT",
    "ETC/USDT","POL/USDT","XLM/USDT","STX/USDT","WIF/USDT",
    "IMX/USDT","OKB/USDT","AAVE/USDT","FIL/USDT","OP/USDT",
    "INJ/USDT","HBAR/USDT","FTM/USDT","MNT/USDT","CRO/USDT",
    "ARB/USDT","VET/USDT","SEI/USDT","ATOM/USDT","RUNE/USDT",
    "GRT/USDT","BONK/USDT","BGB/USDT","FLOKI/USDT","TIA/USDT",
    "THETA/USDT","WLD/USDT","OM/USDT","POPCAT/USDT","AR/USDT",
    "PYTH/USDT","MKR/USDT","ENA/USDT","JUP/USDT","BRETT/USDT",
    "HNT/USDT","ALGO/USDT","ONDO/USDT","LDO/USDT","KCS/USDT",
    "MATIC/USDT","JASMY/USDT","BSV/USDT","CORE/USDT","AERO/USDT",
    "BTT/USDT","NOT/USDT","FLOW/USDT","GT/USDT","W/USDT",
    "STRK/USDT","NEIRO/USDT","BEAM/USDT","QNT/USDT","GALA/USDT",
    "ORDI/USDT","CFX/USDT","FLR/USDT","USDD/USDT","EGLD/USDT",
    "NEO/USDT","AXS/USDT","EOS/USDT","MOG/USDT","XEC/USDT",
    "CHZ/USDT","MEW/USDT","XTZ/USDT","CKB/USDT"
]

# =============================
# Main Screener Logic
# =============================
bullish_symbols = []

progress = st.progress(0)
status_text = st.empty()

for i, symbol in enumerate(symbols):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

        df['ema50'] = EMAIndicator(df['close'], window=50).ema_indicator()
        df['ema200'] = EMAIndicator(df['close'], window=200).ema_indicator()
        macd = MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        adx = ADXIndicator(df['high'], df['low'], df['close'], window=14)
        df['adx'] = adx.adx()

        latest = df.iloc[-1]
        if (
            latest['ema50'] > latest['ema200'] and
            latest['macd'] > latest['macd_signal'] and
            latest['adx'] > 25
        ):
            bullish_symbols.append(symbol)

    except Exception as e:
        print(f"Error processing {symbol}: {e}")

    progress.progress((i + 1) / len(symbols))
    status_text.text(f"Processing {symbol} ({i+1}/{len(symbols)})")

# =============================
# Final Output
# =============================
st.subheader(f"📈 Bullish Coins Detected ({timeframe})")
if bullish_symbols:
    for sym in bullish_symbols:
        st.markdown(f"- ✅ **{sym}**")
else:
    st.info("No strong bullish signals detected.")

time_now = datetime.now(ZoneInfo("Asia/Phnom_Penh")).strftime('%Y-%m-%d %I:%M %p')
st.caption(f"🕒 Updated at: {time_now}")

# --- Donation Section ---
st.markdown("---")
st.markdown("## 💖 Crypto Donations Welcome")
st.markdown("""
If this app helped you, consider donating:

- **BTC:** `bc1qlaact2ldakvwqa7l9xd3lhp4ggrvezs0npklte`
- **TRX / USDT (TRC20):** `TBMrjoyxAuKTxBxPtaWB6uc9U5PX4JMfFu`

You can also scan the QR code below 👇
""")

try:
    st.image("eth_qr.png", width=180, caption="ETH / USDT QR")
except:
    st.warning("⚠️ eth_qr.png not found. Add it to your project folder to display donation QR.")
