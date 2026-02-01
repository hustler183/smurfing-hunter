import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

st.set_page_config(page_title="Smurfing Hunter", layout="wide")

st.title("🔍 Smurfing Hunter – Blockchain AML Graph Tool")

st.markdown("""
This tool detects **fan-out / fan-in money laundering patterns** in blockchain transaction ledgers.
Upload a CSV file to begin analysis.
""")

uploaded_file = st.file_uploader("📂 Upload Transaction CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("Dataset loaded successfully!")

    st.subheader("📊 Sample Transactions")
    st.dataframe(df.head())

    # FAN-OUT
    fan_out = defaultdict(set)
    for _, row in df.iterrows():
        fan_out[row["Source_Wallet"]].add(row["Dest_Wallet"])
    fan_out_count = {k: len(v) for k, v in fan_out.items()}

    # FAN-IN
    fan_in = defaultdict(set)
    for _, row in df.iterrows():
        fan_in[row["Dest_Wallet"]].add(row["Source_Wallet"])
    fan_in_count = {k: len(v) for k, v in fan_in.items()}

    # BUILD GRAPH
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row["Source_Wallet"], row["Dest_Wallet"], amount=row["Amount"])

    # DETECT SUSPICIOUS WALLETS
    suspicious_senders = [w for w, c in fan_out_count.items() if c > 3]
    suspicious_receivers = [w for w, c in fan_in_count.items() if c > 3]

    st.subheader("🚨 Suspicious Wallets")
    st.write("High Fan-Out (Potential Smurfers):", suspicious_senders)
    st.write("High Fan-In (Collectors):", suspicious_receivers)

    # TRACE PATHS
    st.subheader("🔗 Laundering Paths")
    for s in suspicious_senders:
        for r in suspicious_receivers:
            try:
                paths = list(nx.all_simple_paths(G, s, r, cutoff=4))
                for p in paths:
                    st.write(" → ".join(p))
            except:
                pass

    # VISUALIZATION
    st.subheader("🕸 Transaction Graph")
    fig, ax = plt.subplots(figsize=(10, 6))
    nx.draw(G, with_labels=True, node_size=500, font_size=8, ax=ax)
    st.pyplot(fig)
