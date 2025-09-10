You are a Linux eBPF/XDP engineer on RHEL10. Create a tiny XDP program that increments a counter by 1 for every RX packet, returns XDP_PASS, and verifies the count with bpftool. Provide commands I can copy-paste. Use a per-CPU array map (size=1, __u64 value) for fast increments. Keep it minimal—no userspace loader; attach with ip link.

0) Prereqs (RHEL10)
Give me a single block of commands to install tools:
sudo dnf -y install clang llvm bpftool libbpf libbpf-devel kernel-headers make git jq

1) Project layout
Create a directory xdp-counter with:
xdp_count_kern.c – eBPF program (CO-RE friendly includes).
Makefile – builds xdp_count_kern.o.
README.md – steps to build/attach/verify/cleanup.

2) Kernel program (xdp_count_kern.c)
Use a per-CPU array map named pkt_cnt with max_entries = 1. In the SEC("xdp") function, look up key 0 and increment the per-CPU value by 1. Return XDP_PASS. Include license and version. Use __sync_fetch_and_add() (emits a BPF_XADD) or a plain increment for per-CPU values. Provide exactly this code:

// xdp_count_kern.c
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_endian.h>

char LICENSE[] SEC("license") = "GPL";
__u32 VERSION SEC("version") = 1;

// Per-CPU array[1] holding counts; each CPU increments its own slot 0
struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
    __uint(max_entries, 1);
    __type(key, __u32);
    __type(value, __u64);
} pkt_cnt SEC(".maps");

SEC("xdp")
int xdp_count(struct xdp_md *ctx)
{
    __u32 key = 0;
    __u64 *val = bpf_map_lookup_elem(&pkt_cnt, &key);
    if (val) {
        // On per-CPU maps, a plain increment is safe; using atomic add also works:
        // __sync_fetch_and_add(val, 1);
        (*val)++;
    }
    return XDP_PASS; // Allow the packet to continue up the stack
}

3) Makefile
Produce a simple Makefile that builds with clang for BPF:
# Makefile
BPF_CLANG ?= clang
BPF_CFLAGS ?= -O2 -g -Wall -Werror -target bpf

all: xdp_count_kern.o

xdp_count_kern.o: xdp_count_kern.c
	$(BPF_CLANG) $(BPF_CFLAGS) -c $< -o $@

clean:
	rm -f xdp_count_kern.o

4) Build
Give me the exact commands:
cd xdp-counter
make

5) Pick NIC and attach
Detect the default outbound interface and let me override it if needed. Provide commands for driver mode first, with fallback to generic if unsupported.
# Choose interface (auto-detect default route; change IFACE if needed)
IFACE=$(ip -o route get 1.1.1.1 | awk '/dev/ {for(i=1;i<=NF;i++) if ($$i=="dev") {print $$(i+1); exit}}')
echo "Using IFACE=$IFACE"

# Attach in driver mode (preferred)
sudo ip link set dev "$IFACE" xdp obj xdp_count_kern.o sec xdp 2>/tmp/xdp.err || {
  echo "Driver mode failed, trying generic mode..."
  sudo ip link set dev "$IFACE" xdpgeneric obj xdp_count_kern.o sec xdp
}

# Verify attachment
ip -d link show dev "$IFACE" | sed -n '1,10p'

6) Verify with bpftool
Confirm program is loaded and attached:
sudo bpftool prog show | grep -A2 xdp_count
sudo bpftool net

Read the map and sum per-CPU counts for key 0:
# The map is named 'pkt_cnt'; key 0 is four zero bytes
sudo bpftool -j map lookup name pkt_cnt key hex 00 00 00 00 \
  | jq '[.value[] | tonumber] | add'

Generate a bit of RX traffic (replace 8.8.8.8 if you want):
ping -c 20 8.8.8.8 >/dev/null 2>&1
sudo bpftool -j map lookup name pkt_cnt key hex 00 00 00 00 \
  | jq '[.value[] | tonumber] | add'
You should see the number increase.

7) Cleanup / detach
Provide commands to detach regardless of mode:
# Try both off switches; only the active one will succeed
sudo ip link set dev "$IFACE" xdp off 2>/dev/null || true
sudo ip link set dev "$IFACE" xdpgeneric off 2>/dev/null || true
ip -d link show dev "$IFACE" | sed -n '1,10p'

8) README.md
Document the above steps (prereqs → build → attach → verify → cleanup), including:
Note that per-CPU array returns multiple values, so we sum with jq.
Mention that xdpdrv may require NIC/driver support; otherwise xdpgeneric is fine.
Warn that attaching XDP may impact traffic; do this on a test box/maintenance window.

Acceptance criteria
Successful make produces xdp_count_kern.o.
ip -d link show dev $IFACE shows a loaded XDP program.
bpftool -j map lookup name pkt_cnt key 00 00 00 00 | jq ... returns a non-decreasing integer as packets arrive.

Detach leaves the interface with no XDP program attached.
Use these exact filenames, commands, and code. Once you generate everything, run the commands for me in order (ask for confirmation before attaching), then show the map value before and after a quick ping to prove it counts.
