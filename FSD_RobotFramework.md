# Functional Specification: Robot Framework End-to-End Test Suite

## Purpose

Automated end-to-end testing of embedded controller devices via MQTT over AWS IoT.
The test runner (PC) injects commands into a device and verifies responses via two independent verification paths:

- **Inner loop** — direct TRU response over MQTT (`verify/tru`)
- **Outer loop** — telemetry data polled by the telematic unit and stored as JSON files in blob storage (`verify/cloud`)

---

## Directory Structure

```
End2EndTestingV2/
├── Blopstorage/                          # Blob storage root (written by telematic unit)
│   └── {DeviceID}/
│       └── {OperationHours}/
│           └── xxxx.json                 # Polled telemetry data (filename unknown)
└── RobotFramework/
    ├── TestScenes.robot                  # Example test suite (copy to create new scenarios)
    ├── resources/
    │   └── test_keywords.robot           # Reusable Robot Framework keywords (do not edit)
    ├── lib/
    │   ├── config.py                     # Infrastructure config: endpoint, certs, paths
    │   ├── ExcelCommandRepository.py     # Robot library: loads commands from Excel; holds RMU protocol constants
    │   ├── MqttClient.py                 # Robot library: MQTT connect, publish, subscribe, wait
    │   ├── BlobStorage.py                # Robot library: polls and reads blob JSON files
    │   ├── aws_secrets.py                # AWS endpoint reference (not committed)
    │   └── certs/                        # TLS certificates for AWS IoT
    ├── PythonFunctions/
    │   ├── calc_checksum.py              # Shared checksum: sum of ASCII bytes & 0xFF → 2-digit hex
    │   ├── Command_set.py                # Builds RMU SET command string
    │   ├── command_read.py               # Builds RMU READ command string
    │   ├── Read_Expected.py              # Builds expected READ response string (with ACK prefix)
    │   └── SetOperationHours.py          # Builds operation-hours SET command (hardcoded parameters)
    └── TestRepository/
        └── 00-Dev06_CommandGeneration.xlsm   # Excel file: command definitions and limits
```

---

## Test Suite Files — Naming Convention

Each test scenario for a specific controller type is defined in its own `.robot` file:

```
{controller-type}_{Scenario}.robot
```

**Examples:**
- `ML5p2_AllCommandsTest.robot`
- `ML5p2_MinMaxValues.robot`
- `ML3_BasicConnectivity.robot`

To create a new test suite, copy `TestScenes.robot` and modify only the `*** Variables ***` section and `*** Test Cases ***` section. No other files need to be changed.

---

## Per-Suite Configuration (user edits here only)

Each `.robot` suite file defines at the top:

```robot
*** Variables ***
${DEVICE_ID}       ESPTESTSIMULATOR      # Change this to target a different device
${INJECT_TOPIC}    e2e/${DEVICE_ID}/inject
${VERIFY_TRU}      e2e/${DEVICE_ID}/verify/tru
${VERIFY_TELE}     e2e/${DEVICE_ID}/verify/tele
${VERIFY_CLOUD}    e2e/${DEVICE_ID}/verify/cloud
${SCENE_ID}        1
${CLOUD_TIMEOUT}   60
```

`${DEVICE_ID}` is the single value to change when targeting a different device. All MQTT topics and the blob storage lookup path derive from it automatically. `${DEVICE_ID}` is also used as the `DeviceID` field inside the JSON payloads sent to the device.

`${CLOUD_TIMEOUT}` controls how many seconds to wait for a blob file to appear after each test case. Increase it if the telematic unit polling interval is longer than 60 seconds.

---

## Infrastructure Configuration (`lib/config.py`)

Contains settings that are the same for all test suites and never need editing:

| Variable     | Description                                      |
|--------------|--------------------------------------------------|
| `ENDPOINT`   | AWS IoT broker hostname                          |
| `PORT`       | MQTT port (8883 for TLS)                         |
| `CERT_FILE`  | Path to device certificate (relative to lib/)    |
| `KEY_FILE`   | Path to private key (relative to lib/)           |
| `CA_FILE`    | Path to Amazon Root CA (relative to lib/)        |
| `EXCEL_FILE` | Absolute path to the Excel command repository    |
| `BLOB_ROOT`  | Absolute path to the `Blopstorage/` root         |

All paths are resolved relative to `config.py` itself, so the suite works correctly when invoked from any working directory.

---

## RMU Protocol Constants (`lib/ExcelCommandRepository.py`)

The four constants at the top of `ExcelCommandRepository.py` define the RMU message protocol. Change these when targeting a different controller type:

| Constant       | Value  | Description                                     |
|----------------|--------|-------------------------------------------------|
| `COMMAND_ID`   | `'99'` | Command identifier included in every message    |
| `MSG_TYPE_SET` | `'@'`  | Message type character for SET commands         |
| `MSG_TYPE_READ`| `'?'`  | Message type character for READ commands        |
| `DEST_ADDR`    | `0x30` | Destination address of the controller (48 dec)  |

---

## RMU Command Frame Format

All commands and expected responses are ASCII strings with the following structure:

```
SET / READ command:
  ^ {MSG_TYPE} {CMD_ID} {DEST_ADDR} {TABLE} {BLOCK} {OFFSET} {BYTES} [VALUE_PAYLOAD] {CHECKSUM} ~

Expected READ response:
  % ^ {MSG_TYPE} {CMD_ID} {DEST_ADDR} {TABLE} {BLOCK} {OFFSET} {BYTES} {VALUE_PAYLOAD} {CHECKSUM} ~
```

| Field           | Size      | Notes                                            |
|-----------------|-----------|--------------------------------------------------|
| `^`             | 1 char    | Start character (0x5E)                           |
| `MSG_TYPE`      | 1 char    | `@` = SET, `?` = READ                            |
| `CMD_ID`        | 2 chars   | Command ID, e.g. `99`                            |
| `DEST_ADDR`     | 2 hex     | Destination address, e.g. `30` (= 48 dec)       |
| `TABLE`         | 2 hex     | From Excel column `Table`                        |
| `BLOCK`         | 2 hex     | From Excel column `Block`                        |
| `OFFSET`        | 2 hex     | From Excel column `ByteOffset`                   |
| `BYTES`         | 2 hex     | From Excel column `Bytes`                        |
| `VALUE_PAYLOAD` | 64 chars  | Value as 2-digit hex, zero-padded to 32 bytes    |
| `CHECKSUM`      | 2 hex     | `sum(ASCII bytes of MSG_TYPE…last payload) & 0xFF` |
| `~`             | 1 char    | Stop character (0x7E)                            |
| `%` (response)  | 1 char    | ACK prefix on expected READ response only        |

---

## Reusable Keywords (`resources/test_keywords.robot`)

Shared across all test suites. Provides:

| Keyword           | Description                                                        |
|-------------------|--------------------------------------------------------------------|
| `Suite Connect`   | Connects to the MQTT broker and subscribes to verify topics        |
| `Start Test Case` | Initialises suite variables for a new test case                    |
| `Inject Step`     | Publishes a SET/READ command pair and verifies both TRU responses  |
| `End Test Case`   | Publishes tele summary, runs outer blob loop, verifies cloud fields|

---

## Two-Loop Verification Architecture

### Inner Loop — TRU Response (`verify/tru`)

For every `Inject Step`, the test publishes a command to `e2e/{DeviceID}/inject` and waits for the TRU's direct acknowledgement on `e2e/{DeviceID}/verify/tru`. This verifies that the device received and processed each command correctly.

### Outer Loop — Cloud / Telemetry (`verify/cloud`)

After all steps in a test case are complete, `End Test Case`:

1. Publishes the collected telemetry summary to `e2e/{DeviceID}/verify/tele`
2. Polls `Blopstorage/{DeviceID}/{OperationHours}/` for a `.json` file written by the telematic unit
3. When the file appears (within `${CLOUD_TIMEOUT}` seconds), reads its contents and publishes them to `e2e/{DeviceID}/verify/cloud`
4. Deletes the consumed file
5. Verifies each step's `CloudField` value (dot-notation for nested fields) against `CloudExpected`

This verifies the full end-to-end data path: device → telematic unit → cloud storage → test runner.

```
Blopstorage/
└── {DeviceID}/
    └── {OperationHours}/
        └── xxxx.json    ← written by telematic unit, consumed and deleted by test runner
```

Nested cloud fields are specified with dot notation in the Excel `CloudField` column, e.g.:
`RefeerOperatingMode.AutomaticColdTreatmentMode` → `data["RefeerOperatingMode"]["AutomaticColdTreatmentMode"]`

---

## MQTT Topics per Suite

| Variable          | Topic                         | Direction   | Purpose                          |
|-------------------|-------------------------------|-------------|----------------------------------|
| `${INJECT_TOPIC}` | `e2e/{DeviceID}/inject`       | Publish     | Send SET/READ commands to device |
| `${VERIFY_TRU}`   | `e2e/{DeviceID}/verify/tru`   | Subscribe   | Receive direct TRU responses     |
| `${VERIFY_TELE}`  | `e2e/{DeviceID}/verify/tele`  | Publish     | Send telemetry summary           |
| `${VERIFY_CLOUD}` | `e2e/{DeviceID}/verify/cloud` | Publish     | Forward blob data from storage   |

---

## Test Flow

```
Suite Setup
  └── Connect To Broker → Subscribe to ${VERIFY_TRU} → Load Commands from Excel

For each Test Case:
  Start Test Case  (initialise metadata, reset CLOUD_CHECKS list)
    └── Inject Step × N                         ← inner loop
          ├── Publish SET command  → ${INJECT_TOPIC}
          ├── Wait for SET response ← ${VERIFY_TRU}
          ├── Publish READ command → ${INJECT_TOPIC}
          ├── Wait for READ response ← ${VERIFY_TRU}
          └── Append (CloudField, CloudExpected) to CLOUD_CHECKS
  End Test Case
    ├── Publish tele summary        → ${VERIFY_TELE}
    └── Outer loop                              ← outer loop
          ├── Poll Blopstorage/{DeviceID}/{OperationHours}/ for xxxx.json
          ├── Read and delete file
          ├── Publish blob contents → ${VERIFY_CLOUD}
          └── Verify each CLOUD_CHECKS entry using dot-notation field lookup

Suite Teardown
  └── Disconnect From Broker
```

---

## Running Tests

From any directory:

```cmd
robot RobotFramework\ML5p2_AllCommandsTest.robot
```

Results (`log.html`, `report.html`, `output.xml`) are written to the working directory by default. To write to a specific folder:

```cmd
robot --outputdir RobotFramework\results RobotFramework\ML5p2_AllCommandsTest.robot
```
