import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="WiMAX Interactive Simulator", layout="wide")

st.title("📡 WiMAX Interactive Network Simulator")
st.markdown("A real-time demo of **WiMAX concepts**: Coverage, Modulation, QoS, OFDM, Scheduling, QoS Metrics")

# --- Coverage Area Calculator ---
st.header("1️⃣ Coverage Area Calculator")
freq = st.slider("Carrier Frequency (GHz)", 2.3, 3.5, 2.5, 0.1)
tx_power = st.slider("Transmit Power (dBm)", 10, 40, 20)
path_loss_exp = st.slider("Path Loss Exponent (n)", 2.0, 5.0, 3.5, 0.1)

# Friis equation-based range estimation
c = 3e8
wavelength = c / (freq * 1e9)
rx_thresh = -90  # dBm typical threshold
max_distance = (wavelength / (4 * np.pi)) * 10 ** ((tx_power - rx_thresh) / (10 * path_loss_exp))

st.metric("Estimated Coverage Radius", f"{max_distance/1000:.2f} km")

# --- Spectral Efficiency ---
st.header("2️⃣ Spectral Efficiency & Data Rate")
mod_scheme = st.radio("Choose Modulation", ["QPSK (2 bits/sym)", "16-QAM (4 bits/sym)", "64-QAM (6 bits/sym)"])
bw = st.slider("Channel Bandwidth (MHz)", 1.25, 20.0, 10.0)

bits_per_sym = {"QPSK (2 bits/sym)": 2, "16-QAM (4 bits/sym)": 4, "64-QAM (6 bits/sym)": 6}[mod_scheme]
data_rate = bw * 1e6 * bits_per_sym / 7  # simple approx with OFDM overhead
st.metric("Approx. Data Rate", f"{data_rate/1e6:.2f} Mbps")

# --- QoS Analyzer ---
st.header("3️⃣ QoS Class Analyzer")
qos_class = st.selectbox("Select Service Class", ["UGS", "rtPS", "nrtPS", "BE"])

if qos_class == "UGS":
    st.write("✅ Unsolicited Grant Service: Low delay, constant bit rate (e.g. VoIP)")
    metrics = {"Delay": "Very Low", "Jitter": "Low", "Throughput": "High", "BER": "Low", "PLR": "Very Low"}
elif qos_class == "rtPS":
    st.write("✅ Real-Time Polling Service: Variable rate, real-time (e.g. video)")
    metrics = {"Delay": "Low", "Jitter": "Medium", "Throughput": "Medium-High", "BER": "Medium", "PLR": "Low"}
elif qos_class == "nrtPS":
    st.write("✅ Non-Real-Time Polling Service: Bursty traffic (e.g. FTP)")
    metrics = {"Delay": "High", "Jitter": "Medium", "Throughput": "Medium", "BER": "Medium", "PLR": "Medium"}
else:
    st.write("✅ Best Effort: No guarantee (e.g. web browsing)")
    metrics = {"Delay": "Variable", "Jitter": "Variable", "Throughput": "Low-Medium", "BER": "High", "PLR": "High"}

st.json(metrics)

# --- OFDM Subcarrier Visualization ---
st.header("4️⃣ OFDM Subcarrier Visualization")
N = 64
subcarriers = np.arange(-N//2, N//2)
power = np.zeros(N)
power[::4] = 1  # allocate every 4th subcarrier
fig, ax = plt.subplots()
ax.stem(subcarriers, power)  # fixed (no use_line_collection)
ax.set_title("OFDMA Subcarrier Allocation")
ax.set_xlabel("Subcarrier Index")
ax.set_ylabel("Power")
st.pyplot(fig)

# --- Scheduling Demo ---
st.header("5️⃣ WiMAX Scheduling Demo")
traffic_classes = ["UGS", "rtPS", "nrtPS", "BE"]
slots = 20
schedule = np.random.choice(traffic_classes, slots, p=[0.3, 0.3, 0.2, 0.2])
fig2, ax2 = plt.subplots(figsize=(10, 2))
ax2.bar(range(slots), [1]*slots, tick_label=schedule, color='lightblue')
ax2.set_title("Simplified WiMAX Slot Scheduling")
ax2.set_yticks([])
st.pyplot(fig2)

# --- QoS Metrics (Unit V Concepts) ---
st.header("6️⃣ QoS Metrics Visualization")
snr_db = st.slider("Signal-to-Noise Ratio (dB)", 0, 30, 10)
snr_lin = 10 ** (snr_db/10)

# Bit Error Rate (QPSK approximation)
ber = 0.5 * np.exp(-snr_lin)
throughput = data_rate * (1 - ber)
delay = np.random.uniform(10, 50) / (snr_db + 1)
jitter = np.random.uniform(1, 10) / (snr_db + 1)
plr = ber * 100

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("BER", f"{ber:.6f}")
col2.metric("Throughput", f"{throughput/1e6:.2f} Mbps")
col3.metric("Delay", f"{delay:.2f} ms")
col4.metric("Jitter", f"{jitter:.2f} ms")
col5.metric("PLR", f"{plr:.2f} %")

# BER Curve Plot
snr_range = np.linspace(0, 30, 50)
ber_curve = 0.5 * np.exp(-10 ** (snr_range/10))
fig3, ax3 = plt.subplots()
ax3.semilogy(snr_range, ber_curve, 'r-')
ax3.set_xlabel("SNR (dB)")
ax3.set_ylabel("BER (log scale)")
ax3.set_title("BER vs SNR (QPSK Approximation)")
ax3.grid(True, which="both")
st.pyplot(fig3)

# --- Real-time Network Monitoring Demo ---
st.header("7️⃣ Real-Time Network Monitoring")
run_button = st.button("Start Live Simulation")

if run_button:
    chart_placeholder = st.empty()
    x_vals, ber_vals, thr_vals = [], [], []
    for t in range(30):  # simulate 30 time steps
        snr_dynamic = snr_db + np.random.uniform(-2, 2)
        snr_lin_dynamic = 10 ** (snr_dynamic/10)
        ber_dynamic = 0.5 * np.exp(-snr_lin_dynamic)
        thr_dynamic = data_rate * (1 - ber_dynamic)

        x_vals.append(t)
        ber_vals.append(ber_dynamic)
        thr_vals.append(thr_dynamic/1e6)

        fig4, ax4 = plt.subplots(2, 1, figsize=(6, 4))
        ax4[0].plot(x_vals, ber_vals, 'r-o')
        ax4[0].set_title("BER over Time")
        ax4[0].set_ylabel("BER")
        ax4[0].grid(True)

        ax4[1].plot(x_vals, thr_vals, 'g-o')
        ax4[1].set_title("Throughput over Time")
        ax4[1].set_ylabel("Mbps")
        ax4[1].set_xlabel("Time (s)")
        ax4[1].grid(True)

        chart_placeholder.pyplot(fig4)
        time.sleep(0.3)

st.success("✅ Full WiMAX Simulator covering **all 5 units** is ready!")
