import yfinance as yf
import talib
import numpy as np
import pandas as pd
import time
import telegram
import asyncio
from datetime import datetime, timedelta

# Configuración de Telegram
TELEGRAM_BOT_TOKEN = "7958747455:AAGF_uU4Bi0kY4TaW7AstlSI5IJ0-t7_kWI"
TELEGRAM_CHAT_ID = "483653236"
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# Diccionario para controlar el último envío de "cerca de zona favorable"
last_near_zone_alert = {}

# Función asincrónica para enviar mensajes a Telegram
async def send_telegram_message(message):
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        print(f"Error al enviar mensaje de Telegram: {e}")

def analyze_stock(stock_data, ticker):
    global last_near_zone_alert
    
    close_prices = stock_data["Close"].dropna()  

    if close_prices.empty or len(close_prices) < 14:
        print(f"❌ Datos insuficientes para calcular RSI en {ticker}")
        return []  

    rsi = talib.RSI(close_prices.to_numpy().flatten(), timeperiod=14)  
    sma50 = stock_data["Close"].rolling(window=50).mean().dropna()
    
    if len(rsi) == 0 or sma50.empty:
        print(f"❌ No se pudo calcular RSI o SMA50 para {ticker}")
        return []  

    latest_rsi = rsi[-1]
    latest_price = close_prices.iloc[-1].item()  
    latest_sma50 = sma50.iloc[-1].item()  
    
    print(f"📊 {ticker} RSI: {latest_rsi:.2f}, Precio: {latest_price:.2f}, SMA50: {latest_sma50:.2f}")
    
    messages = []
    now = datetime.now()

    # 🚀 COMPRA RECOMENDADA
    if latest_rsi < 40 and latest_price > latest_sma50 * 0.98:
        message = f"🔥🔥🔥 COMPRA RECOMENDADA! {ticker} RSI: {latest_rsi:.2f}, Precio: {latest_price:.2f}, SMA50: {latest_sma50:.2f}"
        print(message)  # 🔹 IMPRIMIR EN CMD
        messages.append(message)

    # ⚠️ POSIBLE COMPRA (Cerca de zona favorable)
    elif latest_rsi < 45 and latest_price > latest_sma50 * 0.95:
        last_alert_time = last_near_zone_alert.get(ticker, None)
        if last_alert_time is None or now - last_alert_time > timedelta(hours=6):
            message = f"⚠️ Posible compra: {ticker} RSI: {latest_rsi:.2f}, Precio: {latest_price:.2f}, SMA50: {latest_sma50:.2f}. Cerca de zona favorable."
            print(message)  # 🔹 IMPRIMIR EN CMD
            messages.append(message)
            last_near_zone_alert[ticker] = now

    # ⚠️⚠️⚠️ POSIBLE VENTA
    if latest_rsi > 75 and latest_price > latest_sma50 * 0.98:
        last_alert_time = last_near_zone_alert.get(f"SELL_{ticker}", None)
        if last_alert_time is None or now - last_alert_time > timedelta(hours=6):
            message = f"⚠️⚠️⚠️ Posible venta: ⚠️⚠️⚠️ {ticker} RSI: {latest_rsi:.2f}, Precio: {latest_price:.2f}, SMA50: {latest_sma50:.2f}. En zona de venta."
            print(message)  # 🔹 IMPRIMIR EN CMD
            messages.append(message)
            last_near_zone_alert[f"SELL_{ticker}"] = now
   
    print("\n")  # 🔹 Espacio entre cada acción
    return messages

async def trading_bot(tickers):
    while True:
        for ticker in tickers:
            print(f"🔍 Analizando {ticker}...")
            stock_data = yf.download(ticker, period="3mo", interval="1d")
            if stock_data.empty:
                print(f"❌ No se pudieron descargar datos para {ticker}")
                continue
            
            messages = analyze_stock(stock_data, ticker)

            # Enviar todas las señales encontradas en Telegram
            for msg in messages:
                asyncio.create_task(send_telegram_message(msg))
        
        print("⏳ Esperando 1 hora antes del siguiente análisis...\n")
        await asyncio.sleep(3600)

async def run_bot():
    tickers = ["NVDA", "IAG.MC", "TTWO", "MSFT", "MA", "AMZN", "AAPL", "GOOG", "TSLA", "META", "V", "TSM", "INTC", "MAP.MC", "TEF.MC", "UBER", "AEDAS.MC", "ENG.MC", "CABK.MC", "SAN.MC", "REP.MC", "BBVA.MC", "GM", "ASML", "HOME.MC", "RYCEY", "FORD", "NOWVF", "TALK", "MBGAF", "EW", "SAND", "NEM", "VRSN", "SPI", "SPGC", "CRAWA", "ADBE", "KO", "COST", "AXP", "LVMHF", "ITX.MC", "ACS.MC", "HESAY", "SBUX", "BABA", "BRK-B", "UNH", "JNJ", "HD", "ASML.AS", "MCD", "SHOP", "NKE", "ABNB", "NET", "ETSY", "GEST.MC", "UN0.DE", "BIDU", "OKLO", "HLUN-B.CO", "AMP.MC", "NXT.MC", "XPEV", "1211.HK", "1810.HK"]
    
    print(f"🚀 Iniciando bot para analizar {', '.join(tickers)}...\n")
    
    await send_telegram_message(f"🔵 Bot iniciado. Analizando {len(tickers)} acciones.")
    
    await trading_bot(tickers)

if __name__ == "__main__":
    asyncio.run(run_bot())