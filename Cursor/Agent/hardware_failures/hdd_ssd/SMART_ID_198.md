# SMART Attribute ID 198: Offline_Uncorrectable

**Understanding Scan Errors and Their Relationship to SMART Attribute 198**

**Document Date:** November 27, 2025  
**Version:** 1.0

---

## Table of Contents

1. [Overview](#overview)
2. [The Sector Failure Lifecycle](#the-sector-failure-lifecycle)
3. [What is Offline_Uncorrectable?](#what-is-offline_uncorrectable)
4. [What are Scan Errors?](#what-are-scan-errors)
5. [The Direct Relationship](#the-direct-relationship)
6. [The "Unhealthy Sector" Trio](#the-unhealthy-sector-trio)
7. [How They Interact](#how-they-interact)
8. [Technical Deep Dive](#technical-deep-dive)
9. [Warning Signs & Actions](#warning-signs--actions)
10. [Testing and Monitoring](#testing-and-monitoring)
11. [Real-World Examples](#real-world-examples)
12. [Quick Reference](#quick-reference)

---

## Overview

**SMART Attribute ID 198 (Offline_Uncorrectable)** is a critical indicator of drive health that counts sectors which failed during offline scanning and could not be corrected even with Error Correction Code (ECC).

**Key Points:**
- This attribute is directly related to scan errors found during self-tests
- A non-zero value indicates uncorrectable read errors
- It's one of three key attributes for predicting drive failure
- For HDDs: Check ID 198 specifically
- For NVMe SSDs: Check "Media and Data Integrity Errors" instead

---

## The Sector Failure Lifecycle

Understanding how sectors progress from healthy to failed:

```
┌─────────────────────────────────────────────────────────────┐
│         HOW DRIVE SECTORS FAIL (Step by Step)               │
└─────────────────────────────────────────────────────────────┘

Stage 1: ✅ Healthy Sector
         └─ Reads/writes normally, no errors
         
Stage 2: 🟡 Weak/Unstable Sector
         └─ Occasional soft errors during read/write
         └─ ECC can still correct errors
         └─ Drive marks sector for monitoring
         
Stage 3: ⚠️ Current_Pending_Sector (SMART ID 197)
         └─ Sector marked as unstable
         └─ Waiting for reallocation
         └─ Still readable but unreliable
         
Stage 4: 🔴 Offline_Uncorrectable (SMART ID 198)
         └─ Failed during offline scan
         └─ Cannot be read even with ECC
         └─ Waiting for write to trigger reallocation
         
Stage 5: Final State (One of Two Outcomes)
         ├─ ✅ Reallocated_Sector_Ct (SMART ID 5)
         │  └─ Successfully remapped to spare area
         │  └─ Sector now working (transparently)
         │  └─ Offline_Uncorrectable decreases
         │
         └─ ❌ Permanent Bad Sector
            └─ No spare sectors available (CRITICAL)
            └─ Data loss at this location
            └─ Drive should be replaced immediately
```

---

## What is Offline_Uncorrectable?

### Definition

**SMART Attribute ID:** 198  
**Attribute Name:** Offline_Uncorrectable  
**Alternative Names:** Offline Uncorrectable Sector Count, Off-Line Scan Uncorrectable Sector Count  
**Type:** Old_age (non-critical by default, but failure indicator)  
**Update:** Offline (only during background scans/self-tests)

### What It Counts

This attribute counts the **total number of uncorrectable sectors** found during:
- Offline scans (`smartctl -t offline`)
- Background media scans (automatic)
- Long self-tests (`smartctl -t long`)
- Any scan that reads the entire disk surface

### How It Works

```
┌──────────────────────────────────────────────────┐
│ Offline Scan Process                             │
├──────────────────────────────────────────────────┤
│ 1. Drive initiates background scan               │
│ 2. Systematically reads every sector             │
│ 3. For each sector:                              │
│    ├─ Attempt to read data                       │
│    ├─ If read fails, apply ECC correction        │
│    ├─ If ECC succeeds → Log soft error, continue │
│    └─ If ECC fails → Increment ID 198            │
│                                                   │
│ 4. Report final count in SMART attributes        │
└──────────────────────────────────────────────────┘
```

### Attribute Details

```
ID# ATTRIBUTE_NAME          FLAG     VALUE WORST THRESH TYPE      UPDATED  WHEN_FAILED RAW_VALUE
198 Offline_Uncorrectable   0x0030   100   253   000    Old_age   Offline      -       0
```

**Field Breakdown:**
- **VALUE:** Normalized value (100 = good, lower = worse)
- **WORST:** Worst value ever recorded
- **THRESH:** Failure threshold (000 = no pre-fail threshold)
- **TYPE:** Old_age (not a pre-fail attribute)
- **UPDATED:** Offline (only during background operations)
- **RAW_VALUE:** Actual count of uncorrectable sectors

**Important:** The RAW_VALUE is what matters most!

---

## What are Scan Errors?

### Definition

**Scan errors** are any errors detected during drive self-testing or background scanning operations, as opposed to errors during normal read/write operations.

### Types of Scan Errors

#### 1. Read Errors
- **What:** Inability to read sector data
- **Cause:** Magnetic degradation, physical damage
- **Detection:** During sector-by-sector scan
- **Result:** Increments Offline_Uncorrectable if ECC fails

#### 2. ECC Uncorrectable Errors
- **What:** Error Correction Code cannot fix corrupted data
- **Cause:** Too many bit errors in sector
- **Detection:** After read attempt fails
- **Result:** Primary cause of Offline_Uncorrectable increase

#### 3. Seek Errors (during scan)
- **What:** Read/write head positioning failures
- **Cause:** Mechanical issues, servo problems
- **Detection:** During head positioning for scan
- **Result:** May prevent scanning certain sectors

#### 4. Servo Errors
- **What:** Track following problems
- **Cause:** Mechanical wear, shock damage
- **Detection:** During continuous scanning
- **Result:** Multiple sectors may become unreadable

### Where Scan Errors Come From

```
Sources of Scan Errors:

User-Initiated Tests:
├─ smartctl -t offline /dev/sdX    → Offline scan
├─ smartctl -t short /dev/sdX      → Quick scan (sample sectors)
└─ smartctl -t long /dev/sdX       → Full surface scan

Automatic Background Operations:
├─ Drive's built-in background scan (vendor-specific)
├─ Idle-time media scans
└─ S.M.A.R.T. automatic offline data collection

Operating System:
├─ RAID consistency checks
├─ File system scrubbing (ZFS, Btrfs)
└─ TRIM/UNMAP operations (SSDs)
```

---

## The Direct Relationship

### Scan Errors → Offline_Uncorrectable

```
┌───────────────────────────────────────────────────────────┐
│  HOW SCAN ERRORS BECOME OFFLINE_UNCORRECTABLE             │
└───────────────────────────────────────────────────────────┘

Step 1: Scan Initiated
        └─ Offline test, background scan, or long test starts

Step 2: Sector-by-Sector Reading
        ├─ Sector N: Read attempt
        │  ├─ Success? → Continue to N+1
        │  └─ Failure? → Go to Step 3
        
Step 3: Error Correction Attempt
        ├─ Apply ECC (Error Correction Code)
        │  ├─ ECC Success? → Log soft error, continue
        │  └─ ECC Failure? → Go to Step 4
        
Step 4: Mark as Uncorrectable
        ├─ Increment Offline_Uncorrectable counter
        ├─ Log sector address
        └─ Continue scan

Step 5: Scan Complete
        └─ Report total Offline_Uncorrectable count
```

### Mathematical Relationship

```
Offline_Uncorrectable (Raw Value) = 
    Total Sectors Scanned 
    - Readable Sectors
    - Soft Errors (ECC corrected)
    = Sectors that FAILED both read AND ECC correction
```

### Example Scenario

```
Drive: 1TB HDD (1,953,525,168 sectors)
Scan Type: Long self-test

Results:
├─ Sectors successfully read:        1,953,525,165
├─ Sectors with soft errors (fixed):           2
├─ Sectors unreadable (ECC failed):            1
└─ Offline_Uncorrectable RAW_VALUE:            1  ← Scan error count
```

---

## The "Unhealthy Sector" Trio

Three SMART attributes work together to track sector health:

### Attribute Comparison

| SMART ID | Name | What It Counts | Detection Method | Severity |
|----------|------|----------------|------------------|----------|
| **197** | **Current_Pending_Sector** | Unstable sectors waiting to be remapped | **Real-time** during normal I/O | 🟡 Medium |
| **198** | **Offline_Uncorrectable** | Sectors that failed offline scans | **During tests** and background scans | 🔴 High |
| **5** | **Reallocated_Sector_Ct** | Bad sectors successfully moved to spare area | **After remapping** (post-write) | 🟢 Low (if stable) |

### The Progression

```
Normal Operation:
├─ ID 197 (Current_Pending) detects problems during READ/WRITE
└─ ID 198 (Offline_Uncorrectable) detects problems during SCANNING

Remediation:
└─ ID 5 (Reallocated) shows successful fixes of both ID 197 and ID 198
```

### Key Differences

**Current_Pending_Sector (197) vs Offline_Uncorrectable (198):**

| Aspect | ID 197 | ID 198 |
|--------|--------|--------|
| **Discovered** | During active use | During background scans |
| **Update Frequency** | Real-time | Only during tests |
| **User Impact** | May cause I/O errors | Transparent (during scan) |
| **Urgency** | Higher (affecting active data) | Lower (detected proactively) |
| **Can overlap?** | Yes - same sector can be in both | Yes - same sector can be in both |

---

## How They Interact

### Scenario 1: Scan Finds New Bad Sector

```
Timeline:

Day 1 - 00:00: Healthy System
├─ Current_Pending_Sector:    0
├─ Offline_Uncorrectable:     0
└─ Reallocated_Sector_Ct:     0

Day 1 - 02:00: Automatic Background Scan Runs
├─ Scans sector 123,456
├─ Read fails, ECC fails
├─ ⚠️ Offline_Uncorrectable:  0 → 1
├─ Current_Pending_Sector:    Still 0 (not accessed normally)
└─ Reallocated_Sector_Ct:     Still 0 (not yet remapped)

Day 2 - 10:00: User Writes to Sector 123,456
├─ Drive attempts reallocation
├─ Success! Moved to spare sector 999,999
├─ ✅ Reallocated_Sector_Ct:  0 → 1
├─ ✅ Offline_Uncorrectable:  1 → 0 (sector fixed)
└─ Current_Pending_Sector:    Still 0 (never entered pending)
```

### Scenario 2: User Encounters Bad Sector First

```
Timeline:

Day 1 - 09:00: User Reads File
├─ Application reads sector 456,789
├─ Read error occurs
├─ ⚠️ Current_Pending_Sector: 0 → 1
├─ Offline_Uncorrectable:     Still 0 (no scan yet)
└─ Reallocated_Sector_Ct:     Still 0

Day 1 - 12:00: Offline Scan Runs
├─ Scans sector 456,789
├─ Confirms sector is bad
├─ ⚠️ Offline_Uncorrectable:  0 → 1
├─ Current_Pending_Sector:    Still 1
└─ Reallocated_Sector_Ct:     Still 0

Day 1 - 15:00: User Writes to Different File
├─ OS writes to sector 456,789
├─ Drive remaps to spare sector
├─ ✅ Reallocated_Sector_Ct:  0 → 1
├─ ✅ Current_Pending_Sector: 1 → 0
└─ ✅ Offline_Uncorrectable:  1 → 0
```

### Scenario 3: Multiple Bad Sectors (Critical)

```
Timeline:

Week 1: First Warning
├─ Offline scan finds 3 bad sectors
├─ Offline_Uncorrectable:     3
└─ Action: Monitor closely

Week 2: More Problems
├─ Normal use encounters 2 more bad sectors
├─ Current_Pending_Sector:    2
├─ Offline_Uncorrectable:     3
└─ Action: Plan for replacement

Week 3: Accelerating Failure
├─ Another scan finds 5 more
├─ Offline_Uncorrectable:     8
├─ Current_Pending_Sector:    5
├─ Reallocated_Sector_Ct:     10 (trying to fix)
└─ 🔴 Action: URGENT backup and replace!
```

---

## Technical Deep Dive

### Error Correction Code (ECC)

**How ECC Works:**

```
Data Storage with ECC:
┌─────────────────────────────────────────┐
│ Sector (512 bytes):                     │
│ ├─ User Data:      512 bytes            │
│ └─ ECC Parity:      50-100 bytes        │
│                                          │
│ ECC can correct:                        │
│ ├─ Up to N bit errors (typically 5-10)  │
│ └─ Beyond N bits → Uncorrectable        │
└─────────────────────────────────────────┘
```

**When ECC Fails:**
1. Too many bit errors (beyond correction capability)
2. Entire sector unreadable (magnetic failure)
3. ECC parity data itself is corrupted
4. Result: **Offline_Uncorrectable increases**

### The Offline Scan Process

```
Detailed Offline Scan Algorithm:
┌──────────────────────────────────────────────────┐
│ START: smartctl -t offline /dev/sdX              │
├──────────────────────────────────────────────────┤
│ Initialize:                                      │
│ ├─ sector_count = 0                              │
│ ├─ uncorrectable_count = 0                       │
│ └─ start_time = now()                            │
│                                                   │
│ For each sector from 0 to max_sectors:          │
│   ├─ position_head(sector)                       │
│   ├─ attempt_read(sector)                        │
│   │                                               │
│   ├─ IF read_successful:                         │
│   │   ├─ verify_checksum()                       │
│   │   └─ continue to next sector                 │
│   │                                               │
│   ├─ ELSE IF read_failed:                        │
│   │   ├─ retry_read() (3-5 attempts)             │
│   │   ├─ apply_ecc_correction()                  │
│   │   │                                           │
│   │   ├─ IF ecc_successful:                      │
│   │   │   ├─ log_soft_error()                    │
│   │   │   └─ continue                            │
│   │   │                                           │
│   │   └─ ELSE IF ecc_failed:                     │
│   │       ├─ uncorrectable_count++               │
│   │       ├─ log_sector_address()                │
│   │       └─ mark_for_reallocation()             │
│   │                                               │
│   └─ sector_count++                              │
│                                                   │
│ COMPLETE:                                        │
│ ├─ Update SMART ID 198 = uncorrectable_count    │
│ ├─ Log completion time                           │
│ └─ Return status                                 │
└──────────────────────────────────────────────────┘
```

### Reallocation Trigger

```
Sector Reallocation Process:
┌────────────────────────────────────────┐
│ Trigger Conditions:                    │
│ ├─ Offline_Uncorrectable > 0           │
│ │  AND                                  │
│ │  Write operation to bad sector       │
│ │                                       │
│ └─ Current_Pending_Sector > 0          │
│    AND                                  │
│    Write operation to pending sector   │
│                                         │
│ Process:                                │
│ 1. Find spare sector in reserve pool   │
│ 2. Write data to spare sector          │
│ 3. Update sector mapping table         │
│ 4. Mark original sector as bad         │
│ 5. Increment Reallocated_Sector_Ct     │
│ 6. Decrement Offline_Uncorrectable     │
│                                         │
│ Result:                                 │
│ ✅ Sector transparently remapped        │
│ ✅ OS sees no change                    │
│ ✅ Performance unchanged                │
└────────────────────────────────────────┘
```

---

## Warning Signs & Actions

### Severity Levels

#### Level 0: Healthy ✅

```
Offline_Uncorrectable:    0
Current_Pending_Sector:   0
Reallocated_Sector_Ct:    0-5 (and stable)

Status:   Healthy
Action:   Continue normal monitoring
Schedule: Run long test quarterly
```

#### Level 1: Early Warning ⚠️

```
Offline_Uncorrectable:    1-5
Current_Pending_Sector:   0-2
Reallocated_Sector_Ct:    0-10 (slowly increasing)

Status:   Early degradation
Action:   Increase monitoring frequency
Schedule: Run long test monthly
Alert:    Plan for replacement in 6-12 months
```

#### Level 2: Moderate Risk 🟠

```
Offline_Uncorrectable:    6-20
Current_Pending_Sector:   3-10
Reallocated_Sector_Ct:    11-50 (increasing)

Status:   Moderate failure risk
Action:   Verify backups are current
Schedule: Run long test weekly
Alert:    Plan for replacement in 1-3 months
```

#### Level 3: High Risk 🔴

```
Offline_Uncorrectable:    >20
Current_Pending_Sector:   >10
Reallocated_Sector_Ct:    >50 (rapidly increasing)

Status:   High failure risk
Action:   BACKUP IMMEDIATELY
Schedule: Daily monitoring
Alert:    Replace within 30 days
```

#### Level 4: Critical ❌

```
Offline_Uncorrectable:    >100 OR rapidly increasing
Current_Pending_Sector:   >50 OR not decreasing
Reallocated_Sector_Ct:    >200 OR approaching limit

Status:   Imminent failure
Action:   STOP using for critical data
         BACKUP NOW if possible
         REPLACE IMMEDIATELY
Alert:    Drive may fail at any time
```

### Critical Combinations

**Danger Pattern 1: Escalating Failures**
```
Day 1:  Offline_Uncorrectable = 5
Day 7:  Offline_Uncorrectable = 15  (+10 in a week)
Day 14: Offline_Uncorrectable = 40  (+25 in a week)

→ Accelerating failure rate
→ Replace immediately
```

**Danger Pattern 2: Reallocation Exhaustion**
```
Reallocated_Sector_Ct approaching drive limit:
├─ Small drives (< 500GB):  ~1,000-2,000 spare sectors
├─ Medium drives (1-2TB):   ~2,000-4,000 spare sectors
└─ Large drives (> 4TB):    ~4,000-8,000 spare sectors

If Reallocated approaching limit:
└─ Drive will fail when spares exhausted
   → Replace immediately
```

**Danger Pattern 3: Persistent Uncorrectable**
```
Offline_Uncorrectable = 10 (constant)
Write operations occur
BUT value doesn't decrease

→ Reallocation is failing
→ No spare sectors OR firmware issue
→ Replace immediately
```

---

## Testing and Monitoring

### Running Tests

#### Offline Test (Checks ID 198)

```bash
# Start offline scan
sudo smartctl -t offline /dev/sdX

# Check status (completes in background)
sudo smartctl -a /dev/sdX | grep "Self-test execution status"

# View results
sudo smartctl -A /dev/sdX | grep "198 Offline_Uncorrectable"
```

**Duration:** Runs in background, doesn't block I/O

#### Short Self-Test

```bash
# Start short test (2 minutes)
sudo smartctl -t short /dev/sdX

# Wait 2 minutes, then check
sudo smartctl -a /dev/sdX | grep -A10 "Self-test log"
```

**What it checks:** Sample of sectors (not all)

#### Long Self-Test (Most Comprehensive)

```bash
# Start long test (4-12 hours for HDD)
sudo smartctl -t long /dev/sdX

# Check estimated completion time
sudo smartctl -a /dev/sdX | grep "Please wait"

# Monitor progress
watch -n 60 'sudo smartctl -a /dev/sdX | grep "Self-test execution status"'

# View final results
sudo smartctl -a /dev/sdX | grep -A15 "Self-test log"
sudo smartctl -A /dev/sdX | grep -E "197|198|5"
```

**What it checks:** All sectors, most thorough

### Monitoring Commands

#### Single Check

```bash
# Check all three critical attributes
sudo smartctl -A /dev/sdX | grep -E "^  5 |^197 |^198 "

# Output example:
#   5 Reallocated_Sector_Ct   0x0033   200   200   140    Pre-fail  Always       -       1
# 197 Current_Pending_Sector  0x0032   200   200   000    Old_age   Always       -       0
# 198 Offline_Uncorrectable   0x0030   100   253   000    Old_age   Offline      -       0
```

#### Continuous Monitoring

```bash
# Watch for changes (updates every 30 seconds)
watch -n 30 'sudo smartctl -A /dev/sdX | grep -E "^  5 |^197 |^198 "'

# Or with highlighting
watch -n 30 --color 'sudo smartctl -A /dev/sdX | grep -E --color "^  5 |^197 |^198 "'
```

#### Logging Over Time

```bash
# Create monitoring script
cat > /tmp/smart_monitor.sh << 'EOF'
#!/bin/bash
LOGFILE="/var/log/smart_monitor.log"
DEVICE="/dev/sda"

echo "=== $(date) ===" >> $LOGFILE
sudo smartctl -A $DEVICE | grep -E "^  5 |^197 |^198 " >> $LOGFILE
echo "" >> $LOGFILE
EOF

chmod +x /tmp/smart_monitor.sh

# Run daily via cron
# Add to crontab: 0 2 * * * /tmp/smart_monitor.sh
```

#### Alert on Changes

```bash
# Create alert script
cat > /tmp/smart_alert.sh << 'EOF'
#!/bin/bash
DEVICE="/dev/sda"
PREV_FILE="/tmp/smart_prev.txt"
CURR_FILE="/tmp/smart_curr.txt"

# Get current values
sudo smartctl -A $DEVICE | grep -E "^  5 |^197 |^198 " > $CURR_FILE

# Compare with previous
if [ -f "$PREV_FILE" ]; then
    if ! diff -q $PREV_FILE $CURR_FILE > /dev/null; then
        echo "SMART ALERT: Values changed on $DEVICE"
        echo "Previous:"
        cat $PREV_FILE
        echo "Current:"
        cat $CURR_FILE
        
        # Send email or notification here
        # mail -s "SMART Alert" admin@example.com < $CURR_FILE
    fi
fi

# Save current as previous
cp $CURR_FILE $PREV_FILE
EOF

chmod +x /tmp/smart_alert.sh
```

### Automated Monitoring with smartd

```bash
# Install smartmontools (if not installed)
sudo dnf install smartmontools

# Configure smartd
sudo nano /etc/smartmontools/smartd.conf

# Add this line for monitoring:
/dev/sda -a -o on -S on -s (S/../.././02|L/../../6/03) -m admin@example.com -M exec /usr/local/bin/smart-notify

# Explanation:
# -a          : Monitor all attributes
# -o on       : Enable automatic offline testing
# -S on       : Enable automatic attribute autosave
# -s (...)    : Schedule tests (Short daily 2AM, Long Saturday 3AM)
# -m email    : Send alerts to this address
# -M exec     : Run custom script on alert

# Start and enable smartd
sudo systemctl enable --now smartd
sudo systemctl status smartd
```

---

## Real-World Examples

### Example 1: Healthy Drive

```
$ sudo smartctl -A /dev/sda | grep -E "^  5 |^197 |^198 "

  5 Reallocated_Sector_Ct   0x0033   100   100   010    Pre-fail  Always       -       0
197 Current_Pending_Sector  0x0012   100   100   000    Old_age   Always       -       0
198 Offline_Uncorrectable   0x0010   100   100   000    Old_age   Offline      -       0

Analysis:
✅ All values at 0 (RAW_VALUE column)
✅ No scan errors detected
✅ No sectors waiting for reallocation
✅ Drive is healthy
Action: Continue normal monitoring
```

### Example 2: Early Warning

```
$ sudo smartctl -A /dev/sdb | grep -E "^  5 |^197 |^198 "

  5 Reallocated_Sector_Ct   0x0033   200   200   140    Pre-fail  Always       -       3
197 Current_Pending_Sector  0x0032   200   200   000    Old_age   Always       -       0
198 Offline_Uncorrectable   0x0030   100   253   000    Old_age   Offline      -       0

Analysis:
⚠️ 3 sectors have been reallocated (past failures, now fixed)
✅ No current pending or uncorrectable sectors
✅ Drive successfully handled past errors
Action: 
  - Monitor for increasing Reallocated_Sector_Ct
  - If number stays stable: OK
  - If number increases weekly: Plan replacement
```

### Example 3: Active Problem

```
$ sudo smartctl -A /dev/sdc | grep -E "^  5 |^197 |^198 "

  5 Reallocated_Sector_Ct   0x0033   190   190   140    Pre-fail  Always       -       25
197 Current_Pending_Sector  0x0032   199   199   000    Old_age   Always       -       5
198 Offline_Uncorrectable   0x0030   095   253   000    Old_age   Offline      -       8

Analysis:
🔴 25 sectors reallocated (significant wear)
🔴 5 sectors currently pending reallocation
🔴 8 sectors found uncorrectable during scans
🔴 Drive is actively failing
Action:
  1. Backup immediately
  2. Run long test to trigger reallocation
  3. Schedule replacement within 30 days
```

### Example 4: Critical Failure

```
$ sudo smartctl -A /dev/sdd | grep -E "^  5 |^197 |^198 "

  5 Reallocated_Sector_Ct   0x0033   001   001   140    Pre-fail  FAILING_NOW  -       1,247
197 Current_Pending_Sector  0x0032   001   001   000    Old_age   Always       -       156
198 Offline_Uncorrectable   0x0030   001   001   000    Old_age   Offline      -       243

Analysis:
❌ 1,247 sectors reallocated (approaching spare limit)
❌ 156 sectors pending (massive active failure)
❌ 243 uncorrectable sectors (cannot be fixed)
❌ Pre-fail attribute below threshold
❌ "FAILING_NOW" status
Action:
  1. STOP using this drive immediately
  2. Attempt data recovery if possible
  3. Replace drive urgently
  4. Drive will fail completely soon
```

### Example 5: NVMe SSD (Healthy)

```
$ sudo smartctl -a /dev/nvme0n1 | grep -A5 "Media and Data"

Media and Data Integrity Errors:    0
Error Information Log Entries:      0

Analysis:
✅ NVMe equivalent of Offline_Uncorrectable = 0
✅ No media errors detected
✅ No logged errors
✅ SSD is healthy
Note: NVMe uses different attributes than HDDs
```

---

## Quick Reference

### Command Cheat Sheet

```bash
# Quick health check
sudo smartctl -H /dev/sdX

# View ID 198 specifically
sudo smartctl -A /dev/sdX | grep "198"

# View all three critical attributes
sudo smartctl -A /dev/sdX | grep -E "5 Reallocated|197 Current|198 Offline"

# Run offline test
sudo smartctl -t offline /dev/sdX

# Run comprehensive test
sudo smartctl -t long /dev/sdX

# Check test status
sudo smartctl -a /dev/sdX | grep "Self-test execution status"

# View test history
sudo smartctl -a /dev/sdX | grep -A10 "Self-test log"

# View error log
sudo smartctl -a /dev/sdX | grep -A10 "Error Log"

# Full detailed report
sudo smartctl -x /dev/sdX > smart_report_$(date +%Y%m%d).txt
```

### Value Interpretation Guide

| RAW_VALUE | Meaning | Action |
|-----------|---------|--------|
| **0** | Perfect, no uncorrectable sectors | ✅ Continue monitoring |
| **1-5** | Few sectors failed scans | ⚠️ Monitor weekly |
| **6-20** | Moderate sector failures | 🟠 Plan replacement |
| **21-50** | Significant failures | 🔴 Backup & replace soon |
| **51-100** | Heavy degradation | ❌ Replace urgently |
| **>100** | Massive failure | ❌ Imminent total failure |
| **Increasing** | Progressive failure | ❌ Replace immediately |

### When to Act

```
Action Thresholds:

Monitor Closely:
└─ Offline_Uncorrectable: 1-5 AND stable
   Action: Monthly long tests

Plan Replacement:
└─ Offline_Uncorrectable: 6-20 OR slowly increasing
   Action: Backup verified, replacement in 3-6 months

Replace Soon:
└─ Offline_Uncorrectable: 21-50 OR steadily increasing
   Action: Replacement in 30-90 days

Replace Immediately:
├─ Offline_Uncorrectable: >50
├─ OR rapidly increasing (doubles weekly)
├─ OR Combined with Current_Pending > 10
└─ Action: Emergency replacement within days
```

### Monitoring Schedule

```
Recommended Testing Schedule:

New Drive (0-1 year):
├─ Offline test: Quarterly
├─ Long test: Bi-annually
└─ SMART check: Monthly

Mature Drive (1-3 years):
├─ Offline test: Monthly
├─ Long test: Quarterly
└─ SMART check: Weekly

Aging Drive (3-5 years):
├─ Offline test: Weekly
├─ Long test: Monthly
└─ SMART check: Daily

Old Drive (>5 years):
├─ Offline test: Daily
├─ Long test: Weekly
└─ SMART check: Continuous monitoring
```

---

## Appendix A: Technical Specifications

### SMART Attribute 198 Specification

```
Attribute ID:     198 (0xC6)
Attribute Name:   Offline_Uncorrectable
Alternative Names:
  - Off-Line Scan Uncorrectable Sector Count
  - Offline Uncorrectable
  - Uncorrectable Sector Count

Attribute Type:   Old_age (non-critical, but failure predictor)
Update Method:    Offline (background scans only)
Pre-fail:         No (typically not a pre-fail attribute)
Threshold:        Usually 0 (no failure threshold)

Value Format:
├─ Normalized VALUE:  0-100 or 0-253 (vendor specific)
├─ WORST:            Lowest VALUE ever recorded
├─ THRESH:           Failure threshold (often 0)
└─ RAW_VALUE:        Actual count of uncorrectable sectors

Vendor Implementation:
├─ Western Digital:   Reports actual sector count
├─ Seagate:          Reports actual sector count
├─ Hitachi:          Reports actual sector count
├─ Toshiba:          Reports actual sector count
└─ Samsung:          May not report (use ID 5 instead)
```

### Error Correction Codes

```
HDD ECC Types:

Reed-Solomon Code:
├─ Used by most modern HDDs
├─ Can correct: 5-10 bit errors per sector
├─ Parity overhead: ~15-20% of sector size
└─ Detection: Up to 20 bit errors

LDPC (Low-Density Parity-Check):
├─ Used by advanced HDDs and SSDs
├─ Can correct: 10-20 bit errors
├─ Parity overhead: ~20-30%
└─ Better performance than Reed-Solomon

BCH Code:
├─ Used by some SSDs
├─ Can correct: Variable (5-40 bits)
├─ Parity overhead: 15-25%
└─ Faster decoding than LDPC
```

---

## Appendix B: For Different Drive Types

### Hard Disk Drives (HDDs)

**Attributes to Monitor:**
- SMART ID 5: Reallocated_Sector_Ct
- SMART ID 197: Current_Pending_Sector
- SMART ID 198: Offline_Uncorrectable
- SMART ID 199: UDMA_CRC_Error_Count

**Typical Spare Sectors:**
- 500GB drive: ~1,000-1,500 spares
- 1TB drive: ~2,000-3,000 spares
- 2TB drive: ~3,000-4,000 spares
- 4TB+ drive: ~4,000-8,000 spares

**Test Duration:**
- Offline: Background (no impact)
- Short: 1-2 minutes
- Long: 1-2 hours per TB

### Solid State Drives (SATA SSDs)

**Attributes to Monitor:**
- SMART ID 5: Reallocated_Block_Count
- SMART ID 170: Available Reserved Space
- SMART ID 184: End-to-End Error
- SMART ID 187: Reported Uncorrectable Errors

**Note:** Many SSDs don't report ID 198 separately

**Test Duration:**
- Short: 1-2 minutes
- Long: 10-30 minutes

### NVMe SSDs

**Attributes to Monitor (NVMe Log Page):**
- Media and Data Integrity Errors (replaces ID 198)
- Percentage Used (wear indicator)
- Available Spare
- Critical Warning field

**No traditional SMART IDs!**

**Test Duration:**
- Short: < 2 minutes
- Extended: 10-20 minutes

---

## Appendix C: Additional Resources

### Official Specifications

- **SMART Specification:** T13/1321D
- **ATA/ATAPI Standard:** T13 Technical Committee
- **NVMe Specification:** NVM Express Organization
- **SCSI Primary Commands:** T10 Technical Committee

### Tools

```
Command-Line:
├─ smartmontools (smartctl, smartd)
├─ hdparm
├─ nvme-cli (for NVMe drives)
└─ badblocks (low-level sector testing)

GUI Tools:
├─ GSmartControl (Linux)
├─ CrystalDiskInfo (Windows)
├─ DriveDx (macOS)
└─ Hard Disk Sentinel

Monitoring Services:
├─ Nagios SMART plugin
├─ Zabbix with smartmontools
├─ Prometheus node_exporter
└─ Custom scripts with email alerts
```

### Further Reading

- smartmontools documentation: https://www.smartmontools.org/
- T13 ATA/ATAPI standards: http://www.t13.org/
- Understanding SMART: https://www.kernel.org/doc/html/latest/admin-guide/abi-testing.html
- Drive reliability studies: Backblaze drive stats

---

## Document Information

**Author:** Linux System Administrator  
**Created:** November 27, 2025  
**Version:** 1.0  
**License:** Educational use only  
**Last Updated:** November 27, 2025

**Tested Systems:**
- RHEL 10 (Linux 6.12.0)
- smartmontools 7.4
- Various HDD and NVMe SSD models

**Disclaimer:** This document is for educational purposes. Always consult drive manufacturer specifications and maintain proper backups. Drive failure can occur without warning despite healthy SMART values.

---

**End of Document**

