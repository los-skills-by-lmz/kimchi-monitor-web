import streamlit as st
import requests
from datetime import datetime
import time

# ========== 页面配置 ==========
st.set_page_config(
    page_title="泡菜溢价监控器",
    page_icon="🥟",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ========== 自定义CSS（美化） ==========
st.markdown("""
<style>
    .stApp {
        background-color: #1a1a2e;
    }
    .metric-card {
        background-color: #16213e;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    .premium-high {
        color: #ff4757;
        font-size: 48px;
        font-weight: bold;
    }
    .premium-mid {
        color: #ffa502;
        font-size: 48px;
        font-weight: bold;
    }
    .premium-low {
        color: #4ecdc4;
        font-size: 48px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ========== 标题区域 ==========
st.title("🥟 泡菜溢价监控器")
st.caption("韩国加密市场套利信号 | Upbit vs Binance | 实时监控BTC价差")

# ========== 数据获取函数 ==========
@st.cache_data(ttl=1800)  # 缓存30分钟
def get_binance_price():
    """获取币安BTC/USDT价格"""
    try:
        response = requests.get(
            "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
            timeout=10
        )
        data = response.json()
        return float(data['price'])
    except Exception as e:
        st.error(f"获取币安价格失败: {e}")
        return None

@st.cache_data(ttl=1800)
def get_upbit_price():
    """获取Upbit BTC/KRW价格"""
    try:
        response = requests.get(
            "https://api.upbit.com/v1/ticker?markets=KRW-BTC",
            timeout=10
        )
        data = response.json()
        return float(data[0]['trade_price'])
    except Exception as e:
        st.error(f"获取Upbit价格失败: {e}")
        return None

@st.cache_data(ttl=1800)
def get_exchange_rate():
    """获取美元兑韩元汇率"""
    try:
        response = requests.get(
            "https://api.exchangerate-api.com/v4/latest/USD",
            timeout=10
        )
        data = response.json()
        return float(data['rates']['KRW'])
    except Exception as e:
        st.error(f"获取汇率失败: {e}")
        return 1350.0  # 备用默认值

# ========== 手动刷新按钮 ==========
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button("🔄 手动刷新数据", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()

# ========== 数据获取 ==========
with st.spinner("正在获取最新数据..."):
    binance_price = get_binance_price()
    upbit_price_krw = get_upbit_price()
    rate = get_exchange_rate()

# ========== 价格显示区域 ==========
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="🇺🇸 Binance BTC/USDT",
        value=f"${binance_price:,.2f}" if binance_price else "--",
        delta=None
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="🇰🇷 Upbit BTC/KRW",
        value=f"₩{upbit_price_krw:,.0f}" if upbit_price_krw else "--",
        delta=None
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="💱 USD/KRW 汇率",
        value=f"{rate:.2f}" if rate else "--",
        delta=None
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ========== 溢价计算 ==========
st.markdown("---")

if binance_price and upbit_price_krw and rate:
    upbit_price_usd = upbit_price_krw / rate
    premium = (upbit_price_usd / binance_price - 1) * 100
    
    # 根据溢价显示不同样式
    st.subheader("🔥 泡菜溢价 (Kimchi Premium)")
    
    if premium >= 3:
        st.markdown(f'<p class="premium-high">{premium:.2f}%</p>', unsafe_allow_html=True)
        st.error("⚠️ 套利机会！价差超过3%，建议关注")
        st.info("💡 套利提示：在Binance买入 → 提币到Upbit → 卖出为KRW")
    elif premium >= 1:
        st.markdown(f'<p class="premium-mid">{premium:.2f}%</p>', unsafe_allow_html=True)
        st.warning("⚡ 接近阈值，继续观察")
    else:
        st.markdown(f'<p class="premium-low">{premium:.2f}%</p>', unsafe_allow_html=True)
        st.info("📊 价差较小，暂不适合套利")
else:
    st.error("❌ 数据获取失败，请检查网络后点击「手动刷新」")

# ========== 更新时间 ==========
st.markdown("---")
st.caption(f"⏱️ 最后更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption(f"🔄 自动刷新频率: 每30分钟")

# ========== 说明区域 ==========
with st.expander("📖 什么是泡菜溢价？"):
    st.markdown("""
    **泡菜溢价 (Kimchi Premium)** 是指韩国交易所（如Upbit）的比特币价格比全球交易所（如Binance）高出一定比例的现象。
    
    **产生原因**：
    - 韩国严格的资本管制
    - 韩国市场对加密货币的强烈需求
    - 交易所之间的流动性差异
    
    **套利条件**：
    - 价差 > 3% 才有套利空间（需扣除手续费和转账费）
    - 需要同时拥有Binance和Upbit账号
    - 需要韩国本地银行账户
    
    **风险提示**：
    - BTC转账需要30-60分钟，期间价差可能消失
    - 提币手续费约0.0005 BTC (~30美元)
    - 跨境资金流动需遵守外汇管理规定
    """)

with st.expander("🔧 套利操作步骤"):
    st.markdown("""
    1. 在Binance用USDT买入BTC
    2. 提币到Upbit的BTC充值地址（耗时30-60分钟）
    3. 在Upbit卖出BTC为KRW
    4. 用KRW在Upbit买入USDT
    5. 将USDT提币回Binance，完成一轮套利
    
    **当前费用估算**：
    - Binance交易费: 0.1%
    - Binance提币费: ~0.0005 BTC (~30美元)
    - Upbit交易费: 0.05%
    - 总成本约: 0.5-1%
    """)

# ========== 自动刷新（每30分钟） ==========
st.caption("💡 页面会自动刷新，或点击上方按钮手动刷新")
