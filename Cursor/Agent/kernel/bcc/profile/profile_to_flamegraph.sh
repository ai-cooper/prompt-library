#!/bin/bash

# === CONFIGURATION ===
BCC_DIR="/usr/share/bcc/tools"
FLAMEGRAPH_DIR="$HOME/FlameGraph"
OUT_DIR="$HOME/profile_results"
SAMPLES=99
DURATION=10

# === PREPARE OUTPUT DIR ===
mkdir -p "$OUT_DIR"
cd "$BCC_DIR" || { echo "BCC tools not found"; exit 1; }

echo "[+] Running BCC profile for $DURATION seconds at $SAMPLES hz..."

# === RUN PROFILE ===
sudo ./profile -F $SAMPLES $DURATION > "$OUT_DIR/raw_profile.stacks"

# === CHECK FLAMEGRAPH TOOL ===
if [ ! -d "$FLAMEGRAPH_DIR" ]; then
  echo "[!] FlameGraph repo not found in $FLAMEGRAPH_DIR"
  echo "    Clone it using:"
  echo "    git clone https://github.com/brendangregg/FlameGraph.git $FLAMEGRAPH_DIR"
  exit 1
fi

# === GENERATE COLLAPSED STACKS ===
echo "[+] Collapsing stack traces..."
"$FLAMEGRAPH_DIR/stackcollapse.pl" "$OUT_DIR/raw_profile.stacks" > "$OUT_DIR/profile.folded"

# === GENERATE FLAME GRAPH ===
echo "[+] Generating flame graph..."
"$FLAMEGRAPH_DIR/flamegraph.pl" "$OUT_DIR/profile.folded" > "$OUT_DIR/profile_flamegraph.svg"

# === DONE ===
echo "[✔] Flame graph saved to: $OUT_DIR/profile_flamegraph.svg"
echo "    You can open it with: firefox $OUT_DIR/profile_flamegraph.svg"

