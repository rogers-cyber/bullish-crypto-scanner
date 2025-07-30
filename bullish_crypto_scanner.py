import ccxt
import pandas as pd
from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

# =============================
# Streamlit UI
# =============================
st.set_page_config(page_title="Bullish Crypto Scanner", layout="wide")
st.title("📊 Bullish Crypto Screener")

timeframe = st.selectbox("Select timeframe", ["15m", "30m", "1h", "2h", "3h", "4h", "1d"], index=2)

# =============================
# Exchange Setup
# =============================
exchange = ccxt.kucoin({
    'enableRateLimit': True,
    'headers': {
        'User-Agent': 'Mozilla/5.0 (compatible; StreamlitBot/1.0)'
    }
})

limit = 200

symbols = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "USDC/USDT",
    "XRP/USDT", "DOGE/USDT", "TRX/USDT", "TON/USDT", "ADA/USDT",
    "AVAX/USDT", "SHIB/USDT", "LINK/USDT", "BCH/USDT", "DOT/USDT",
    "NEAR/USDT", "SUI/USDT", "LEO/USDT", "DAI/USDT", "APT/USDT",
    "LTC/USDT", "UNI/USDT", "TAO/USDT", "PEPE/USDT", "ICP/USDT",
    "FET/USDT", "KAS/USDT", "FDUSD/USDT", "XMR/USDT", "RENDER/USDT",
    "ETC/USDT", "POL/USDT", "XLM/USDT", "STX/USDT", "WIF/USDT",
    "IMX/USDT", "OKB/USDT", "AAVE/USDT", "FIL/USDT", "OP/USDT",
    "INJ/USDT", "HBAR/USDT", "FTM/USDT", "MNT/USDT", "CRO/USDT",
    "ARB/USDT", "VET/USDT", "SEI/USDT", "ATOM/USDT", "RUNE/USDT",
    "GRT/USDT", "BONK/USDT", "BGB/USDT", "FLOKI/USDT", "TIA/USDT",
    "THETA/USDT", "WLD/USDT", "OM/USDT", "POPCAT/USDT", "AR/USDT",
    "PYTH/USDT", "MKR/USDT", "ENA/USDT", "JUP/USDT", "BRETT/USDT",
    "HNT/USDT", "ALGO/USDT", "ONDO/USDT", "LDO/USDT", "KCS/USDT",
    "MATIC/USDT", "JASMY/USDT", "BSV/USDT", "CORE/USDT", "AERO/USDT",
    "BTT/USDT", "NOT/USDT", "FLOW/USDT", "GT/USDT", "W/USDT",
    "STRK/USDT", "NEIRO/USDT", "BEAM/USDT", "QNT/USDT", "GALA/USDT",
    "ORDI/USDT", "CFX/USDT", "FLR/USDT", "USDD/USDT", "EGLD/USDT",
    "NEO/USDT", "AXS/USDT", "EOS/USDT", "MOG/USDT", "XEC/USDT",
    "CHZ/USDT", "MEW/USDT", "XTZ/USDT", "CKB/USDT"
]

# =============================
# Cached OHLCV Fetching
# =============================
@st.cache_data(ttl=300)
def fetch_ohlcv(symbol, timeframe, limit):
    return exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

# =============================
# Main Screener Logic
# =============================
bullish_symbols = []

progress = st.progress(0)
status_text = st.empty()

for i, symbol in enumerate(symbols):
    try:
        ohlcv = fetch_ohlcv(symbol, timeframe, limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

        if len(df) < 200:
            continue  # Not enough data for EMA200

        df['ema50'] = EMAIndicator(df['close'], window=50).ema_indicator()
        df['ema200'] = EMAIndicator(df['close'], window=200).ema_indicator()
        macd = MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        adx = ADXIndicator(df['high'], df['low'], df['close'], window=14)
        df['adx'] = adx.adx()
        df['rsi'] = RSIIndicator(df['close']).rsi()

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        # Screening conditions
        if (
            latest['ema50'] > latest['ema200'] and
            latest['macd'] > latest['macd_signal'] and
            latest['adx'] > 25 and
            50 < latest['rsi'] < 70  # RSI in bullish but not overbought zone
        ):
            price = latest['close']
            prev_price = previous['close']
            change_pct = ((price - prev_price) / prev_price) * 100

            bullish_symbols.append({
                "symbol": symbol,
                "price": price,
                "change_pct": change_pct,
                "adx": latest['adx'],
                "rsi": latest['rsi']
            })

    except Exception as e:
        print(f"❌ Error processing {symbol}: {e}")

    progress.progress((i + 1) / len(symbols))
    status_text.text(f"Processing {symbol} ({i+1}/{len(symbols)})")

# =============================
# Final Output
# =============================
st.subheader(f"📈 Bullish Coins Detected ({timeframe})")

if bullish_symbols:
    # Sort results
    bullish_symbols = sorted(bullish_symbols, key=lambda x: x["change_pct"], reverse=True)
    df_results = pd.DataFrame(bullish_symbols)

    # st.dataframe(df_results)

    for coin in bullish_symbols:
        direction = "↑" if coin["change_pct"] >= 0 else "↓"
        color = "🟢" if coin["change_pct"] >= 0 else "🔴"
        st.markdown(
            f"- ✅ **{coin['symbol']}** • Price: `${coin['price']:.4f}` • {color} Change: `{coin['change_pct']:.2f}% {direction}` • ADX: `{coin['adx']:.1f}` • RSI: `{coin['rsi']:.1f}`"
        )
else:
    st.info("No strong bullish signals detected.")

# =============================
# Timestamp
# =============================
time_now = datetime.now(ZoneInfo("Asia/Phnom_Penh")).strftime('%Y-%m-%d %I:%M %p')
st.caption(f"🕒 Updated at: {time_now}")
