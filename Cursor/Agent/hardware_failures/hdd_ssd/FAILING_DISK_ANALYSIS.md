# Disk Health Assessment Report - RHEL10 System

**Assessment Date:** Wednesday, November 26, 2025 - 15:37 JST  
**Duration:** 60 seconds continuous monitoring  
**System:** Red Hat Enterprise Linux 10  
**Overall Risk Level:** 🔴 **HIGH**

---

## Executive Summary

**CRITICAL:** `/dev/sdb` (2TB WD Red HDD) is experiencing severe I/O errors with "Logical unit access not authorized" messages, indicating USB enclosure failure or drive lock state. The drive has exceeded its rated lifespan at **8.3 years** of continuous operation. The NVMe boot drive is healthy with 97% life remaining but shows concerning unsafe shutdown patterns.

**Immediate Action Required:** Replace `/dev/sdb` within 24-48 hours. Backup any critical data immediately.

---

## Devices Analyzed

| Device | Model | Type | Capacity | Risk Level | Status |
|--------|-------|------|----------|------------|--------|
| `/dev/sdb` | WDC WD20EFRX-68AX9N0 | HDD | 2.00 TB | 🔴 HIGH | FAILING |
| `/dev/nvme0n1` | INTEL SSDPEKKF256G8L | NVMe SSD | 256 GB | 🟢 LOW | HEALTHY |

---

## Device 1: `/dev/sdb` - Western Digital Red HDD

### Overview

- **Model:** WDC WD20EFRX-68AX9N0
- **Serial Number:** WD-WCC1T0550486
- **Capacity:** 2.00 TB (2,000,398,934,016 bytes)
- **Connection:** USB/UAS (USB Attached SCSI)
- **Firmware:** 80.00A80
- **Risk Level:** 🔴 **HIGH**
- **SMART Health:** PASSED (with critical warnings)

### Critical Findings

#### 🚨 CRITICAL ISSUES

1. **Multiple I/O Errors with "Logical unit access not authorized"**
   - Drive is refusing read access to sectors
   - Indicates USB enclosure failure, drive lock, or bridge chip malfunction

2. **USB Device Reset Events Detected**
   - Unstable connection requiring multiple device resets
   - Suggests failing USB-SATA bridge or power delivery issues

3. **Unable to Read Partition Table**
   - Persistent errors on sector 0 (MBR/GPT location)
   - Drive may be inaccessible or locked

#### ⚠️ WARNING INDICATORS

4. **Extreme Age: 72,766 Power-On Hours**
   - Equivalent to **8.3 years** of continuous operation
   - Far exceeds WD Red rated lifespan of 5 years (66% beyond rated life)
   - Drive is statistically at very high risk of failure

5. **1 Reallocated Sector Detected**
   - Minor issue currently, but indicates beginning of media degradation
   - Trend may accelerate with age

6. **Errors on Critical Sectors**
   - Sector 0 (partition table)
   - Sector 3,907,028,992 (near end of disk)

### SMART Attributes Analysis

| Attribute | Value | Raw | Threshold | Status | Assessment |
|-----------|-------|-----|-----------|--------|------------|
| Reallocated_Sector_Ct | 200 | 1 | 140 | PASS | Low concern - only 1 sector |
| Current_Pending_Sector | 200 | 0 | - | GOOD | No pending sectors |
| Offline_Uncorrectable | 100 | 0 | - | GOOD | No uncorrectable errors |
| Temperature_Celsius | 123 | 27°C | - | NORMAL | Acceptable temperature |
| Power_On_Hours | 1 | 72,766 | - | 🔴 CRITICAL | Far exceeds lifespan |
| UDMA_CRC_Error_Count | 200 | 0 | - | GOOD | No cable/interface errors |
| Spin_Retry_Count | 100 | 0 | - | GOOD | No spinup issues |

### Kernel Error Log

```
[Wed Nov 26 15:33:57 2025] sd 1:0:0:0: [sdb] tag#21 FAILED Result: hostbyte=DID_ERROR driverbyte=DRIVER_OK
[Wed Nov 26 15:33:57 2025] sd 1:0:0:0: [sdb] tag#21 Sense Key : Data Protect [current]
[Wed Nov 26 15:33:57 2025] sd 1:0:0:0: [sdb] tag#21 Add. Sense: Logical unit access not authorized
[Wed Nov 26 15:33:57 2025] I/O error, dev sdb, sector 0 op 0x0:(READ) flags 0x0 phys_seg 1 prio class 0
[Wed Nov 26 15:33:57 2025] Buffer I/O error on dev sdb, logical block 0, async page read
[Wed Nov 26 15:33:58 2025] scsi host1: uas_eh_device_reset_handler (USB device reset)
[Wed Nov 26 15:33:58 2025] sdb: unable to read partition table
```

### Root Cause Analysis

The drive is experiencing "Logical unit access not authorized" SCSI errors. This typically indicates:

1. **USB Bridge/Enclosure Failure** - Most likely cause, USB-SATA chip malfunction
2. **Drive Encryption Lock** - Hardware ATA security feature may be enabled
3. **USB Power Delivery Problems** - Insufficient power causing drive protection mode
4. **Failing USB Controller** - Motherboard USB port or cable issues

Combined with the extreme age (8.3 years), this drive is **unreliable and should not be trusted** for production data storage.

---

## Device 2: `/dev/nvme0n1` - Intel NVMe SSD

### Overview

- **Model:** INTEL SSDPEKKF256G8L
- **Serial Number:** BTHH845203LJ256B
- **Capacity:** 256 GB (256,060,514,304 bytes)
- **Connection:** NVMe PCIe (Direct)
- **Firmware:** L08P
- **Risk Level:** 🟢 **LOW**
- **SMART Health:** PASSED

### Health Status

#### ✅ EXCELLENT INDICATORS

1. **97% Life Remaining** (Percentage Used: 3%)
2. **No Media Errors** (0 media and data integrity errors)
3. **100% Spare Capacity Available** (threshold: 12%)
4. **No Error Log Entries** (clean error log)
5. **Optimal Temperature** (26-27°C, warning threshold: 75°C)
6. **No Thermal Throttling Events**

#### ⚠️ AREAS OF CONCERN

7. **206 Unsafe Shutdowns Detected**
   - Suggests improper system shutdown procedures
   - May indicate power outages, kernel panics, or aggressive power management
   - **Not a drive failure indicator** - investigate system power management

### SMART/Health Information

| Attribute | Value | Status | Assessment |
|-----------|-------|--------|------------|
| Critical Warning | 0x00 | ✅ PASS | No critical warnings |
| Temperature | 26-27°C | ✅ OPTIMAL | Well within limits |
| Available Spare | 100% | ✅ EXCELLENT | Maximum spare capacity |
| Spare Threshold | 12% | ✅ EXCELLENT | Well above threshold |
| Percentage Used | 3% | ✅ EXCELLENT | 97% life remaining |
| Data Units Read | 7,393,150 | ✅ GOOD | 3.78 TB total read |
| Data Units Written | 12,145,760 | ✅ GOOD | 6.21 TB total written |
| Power On Hours | 2,752 hrs | ✅ GOOD | ~115 days, relatively new |
| Unsafe Shutdowns | 206 | ⚠️ INVESTIGATE | Check power management |
| Media Errors | 0 | ✅ EXCELLENT | No media failures |
| Error Log Entries | 0 | ✅ EXCELLENT | Clean error log |

### Root Cause Analysis

This Intel NVMe SSD is in **excellent health** with 97% of its rated lifespan remaining. The drive shows no signs of hardware failure or degradation.

The **206 unsafe shutdowns** warrant investigation but are not indicative of drive failure. Possible causes:
- Improper shutdown procedures (forced power-off)
- Power outages without UPS backup
- Kernel panics or system crashes
- Aggressive power management settings

**Recommendation:** Investigate power management and consider UPS installation. The drive itself does not require replacement.

---

## Evidence Summary

### `/dev/sdb` (HIGH RISK)

- ✗ 72,766 power-on hours (8.3 years) - **far exceeds** WD Red rated lifespan of 5 years
- ✗ Multiple "Logical unit access not authorized" errors preventing read access
- ✗ USB device reset events indicating connection instability
- ✗ Unable to read partition table due to persistent I/O errors
- ✗ 1 reallocated sector - early sign of media degradation
- ✗ Connected via USB enclosure - adds additional failure point vs. direct SATA

### `/dev/nvme0n1` (LOW RISK)

- ✓ Only 3% wear - expected to last many more years
- ✓ No media errors or data integrity issues
- ✓ No kernel errors detected - stable PCIe connection
- ⚠ 206 unsafe shutdowns - non-critical but indicates power management issues

---

## Recommendations

### IMMEDIATE ACTIONS (Within 24 Hours)

1. **🚨 STOP using `/dev/sdb` for new data** - drive is unreliable and may be locked/failing

2. **🚨 Test `/dev/sdb` with direct SATA connection** - bypass USB enclosure to rule out enclosure failure

3. **🚨 Check for drive password lock:**
   ```bash
   sudo hdparm -I /dev/sdb | grep -i 'security|locked|frozen'
   ```

4. **🚨 Emergency data backup** - if `/dev/sdb` contains important data:
   ```bash
   sudo ddrescue -n /dev/sdb /path/to/new/drive /tmp/sdb_recovery.log
   ```

### URGENT ACTIONS (Within 48 Hours)

5. **Replace `/dev/sdb` with new drive** - at 8.3 years, drive has far exceeded safe operational lifespan

6. **Implement proper backup strategy** - do not rely on aging USB-connected storage

### RECOMMENDED ACTIONS

7. **Investigate unsafe NVMe shutdowns:**
   ```bash
   sudo journalctl -k --since '30 days ago' | grep -i 'panic|oops|segfault'
   ```

8. **Review shutdown patterns:**
   ```bash
   sudo journalctl --since '30 days ago' | grep -i 'shutdown|reboot|power'
   ```

9. **Enable SMART monitoring daemon:**
   ```bash
   sudo systemctl enable --now smartd
   sudo smartctl -s on /dev/sdb
   sudo smartctl -s on /dev/nvme0n1
   ```

10. **Consider disabling aggressive power management** if causing unsafe shutdowns

11. **Install UPS battery backup** to prevent unsafe shutdowns and data loss

### OPTIONAL ENHANCEMENTS

12. **Enable automated SMART monitoring with email alerts:**
    ```bash
    echo 'DEVICESCAN -a -o on -S on -n standby,q -s (S/../.././02|L/../../6/03) -m root@localhost' | \
    sudo tee -a /etc/smartmontools/smartd.conf
    sudo systemctl restart smartd
    ```

---

## Next Steps - Detailed Commands

### 1. Check `/dev/sdb` Drive Lock Status
```bash
sudo hdparm -I /dev/sdb | grep -i 'security\|locked\|frozen'
```

### 2. Extended SMART Test (Run When System Idle)
```bash
# For HDD (takes ~279 minutes)
sudo smartctl -t long /dev/sdb

# For NVMe (much faster)
sudo smartctl -t long /dev/nvme0n1

# Check test results after completion
sudo smartctl -a /dev/sdb
```

### 3. Emergency Data Clone (If Needed)
```bash
# Clone failing drive to new drive
sudo ddrescue -n /dev/sdb /dev/NEW_DRIVE /tmp/sdb_recovery.log

# If first pass fails, retry with direct mode
sudo ddrescue -d -r3 /dev/sdb /dev/NEW_DRIVE /tmp/sdb_recovery.log
```

### 4. Monitor for Kernel Panics
```bash
sudo journalctl -k --since '30 days ago' | grep -i 'panic\|oops\|segfault'
```

### 5. Install Hardware Reliability Monitoring
```bash
sudo dnf install -y rasdaemon
sudo systemctl enable --now rasdaemon
sudo ras-mc-ctl --summary
```

### 6. Check UPS Status (If Available)
```bash
upsc ups@localhost 2>/dev/null || echo 'No UPS detected - consider installing battery backup'
```

### 7. Review USB Subsystem Errors
```bash
sudo dmesg | grep -iE "usb.*error|usb.*reset|uas" | tail -50
```

### 8. Filesystem Integrity Check (If Drive Becomes Accessible)
```bash
# For ext4
sudo fsck.ext4 -n /dev/sdb1

# For XFS
sudo xfs_repair -n /dev/sdb1
```

---

## Additional Diagnostics Recommended

If the issue persists or you need deeper analysis, consider:

### System-Level Diagnostics

- **Full dmesg output** for USB subsystem errors
- **rasdaemon** for ECC memory errors (may correlate with system crashes)
- **ipmitool sensor list** (if server hardware) for PSU/temperature issues
- **BIOS/UEFI logs** for hardware errors

### Drive-Level Diagnostics

- Test `/dev/sdb` with **different USB cable** and enclosure
- Connect `/dev/sdb` directly to **motherboard SATA port**
- Run manufacturer's diagnostic tools (Western Digital Data Lifeguard)
- Check for **firmware updates** for USB enclosure

### Power Management Analysis

- Audit **systemd power management** settings
- Review **laptop-mode-tools** or **tlp** configuration
- Check **BIOS/UEFI power settings**
- Monitor with **powertop** for aggressive power saving

---

## Data Backup Priority

| Device | Priority Level | Rationale |
|--------|---------------|-----------|
| `/dev/sdb` | 🔴 **URGENT** | Data at high risk, backup immediately if accessible |
| `/dev/nvme0n1` | 🟢 **ROUTINE** | Drive healthy, maintain regular backup schedule |

---

## Replacement Timeline

| Device | Timeline | Action |
|--------|----------|--------|
| `/dev/sdb` | ⏰ **IMMEDIATE** | Replace within 24-48 hours |
| `/dev/nvme0n1` | ✓ **NOT NEEDED** | Drive has years of life remaining |

---

## Monitoring Setup Guide

To prevent future failures and detect issues early, set up continuous monitoring:

### Enable smartd

```bash
# Enable and start the SMART monitoring daemon
sudo systemctl enable --now smartd

# Configure email alerts (edit /etc/smartmontools/smartd.conf)
sudo nano /etc/smartmontools/smartd.conf

# Add this line:
# DEVICESCAN -a -o on -S on -n standby,q -s (S/../.././02|L/../../6/03) -m root@localhost

# Restart service
sudo systemctl restart smartd
```

### Monitor Logs

```bash
# Watch SMART daemon logs
sudo journalctl -u smartd -f

# Check SMART status daily
sudo smartctl -H /dev/nvme0n1
```

---

## Appendix: Technical Details

### System Configuration

```
OS: Red Hat Enterprise Linux 10
Kernel: 6.12.0-55.14.1.el10_0.x86_64
smartctl Version: 7.4 2023-08-01 r5530
```

### Storage Topology

```
nvme0n1 (Boot Drive - 238.5G)
├── nvme0n1p1  (600M)   → /boot/efi
├── nvme0n1p2  (1G)     → /boot
└── nvme0n1p3  (236.9G) → LUKS encrypted
    └── luks-f5351be9-a884-4b6b-88c5-01bf7f9ee38b
        ├── rhel-root (70G)    → /
        ├── rhel-swap (7.8G)   → [SWAP]
        └── rhel-home (159.1G) → /home

sdb (USB Storage - 1.8T) - INACCESSIBLE
```

### Files Generated

- **Detailed Report (JSON):** `/tmp/disk_health_assessment_report.json`
- **Summary (JSON):** `/tmp/disk_health_summary.json`
- **Raw Data Log:** `/tmp/disk_health_data_20251126_153728.log`
- **This Report (Markdown):** `/tmp/disk_health_assessment_report.md`

---

## Conclusion

Your RHEL10 system has **one critical issue** requiring immediate attention: the `/dev/sdb` external USB drive is failing due to extreme age (8.3 years) and experiencing access authorization errors. This drive should be replaced within 24-48 hours and any data on it should be backed up immediately if accessible.

The primary system drive (`/dev/nvme0n1` Intel NVMe SSD) is in excellent health with 97% of its rated lifespan remaining. The only concern is the high number of unsafe shutdowns (206), which suggests investigating power management settings or installing UPS backup, but does not indicate drive failure.

**Final Verdict: HIGH RISK** due to `/dev/sdb` instability and extreme age. Immediate replacement recommended.

---

**Report Generated:** Wednesday, November 26, 2025 - 15:37 JST  
**Assessment Method:** 60-second continuous SMART monitoring + kernel log analysis  
**Tools Used:** smartctl, nvme-cli, journalctl, dmesg, iostat

---

*For questions or additional diagnostics, refer to the "Next Steps" section above.*

