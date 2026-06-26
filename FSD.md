# Functional Specification Document
## Robot Framework E2E Test Automation — TRU Simulator & MQTT Test Framework

---

## 1. Purpose

This framework automates end-to-end testing of a Transport Refrigeration Unit (TRU) via MQTT. Robot Framework orchestrates the test execution by injecting serial commands through an MQTT broker and verifying the responses from the TRU (or a simulator). Test steps are defined in Robot Framework and their command parameters are looked up from a central command repository (Excel).

---

## 2. System Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Robot Framework (PC)                  │
│  TestScenes.robot + resources/test_keywords.robot       │
│  Reads Excel → calculates commands → publishes/verifies │
└───────────────────┬─────────────────────────────────────┘
                    │ MQTT (e2e/inject)
                    ▼
         ┌──────────────────┐
         │   MQTT Broker    │  (Home Assistant / Mosquitto)
         └──────────────────┘
                    │ MQTT (e2e/verify/tru)
                    ▼
┌─────────────────────────────────────────────────────────┐
│              TRU / Simulator (ESP32 or PC)              │
│  Receives inject → sends serial command → publishes     │
│  response on e2e/verify/tru                             │
└─────────────────────────────────────────────────────────┘
```

---

## 3. MQTT Topics

| Topic             | Publisher        | Subscriber       | Purpose                                      |
|-------------------|------------------|------------------|----------------------------------------------|
| `e2e/inject`      | Robot Framework  | TRU / Simulator  | Delivers write or read commands to the TRU   |
| `e2e/verify/tru`  | TRU / Simulator  | Robot Framework  | Returns the TRU's response to each command   |
| `e2e/verify/tele` | Robot Framework  | External systems | Aggregated test case results after each case |

---

## 4. Test Flow

### Inner Loop (per step)
1. RF publishes a **write inject** payload to `e2e/inject`
2. TRU executes the serial write command and publishes result to `e2e/verify/tru`
3. RF asserts `WriteValue == SetExpected`
4. RF publishes a **read inject** payload to `e2e/inject`
5. TRU executes the serial read command and publishes result to `e2e/verify/tru`
6. RF asserts `ReadValue == ReadExpected`
7. Step result is accumulated into the tele payload

### Test Case Boundary
After all steps of a test case complete:
- RF publishes the aggregated tele payload to `e2e/verify/tele` including `OperationHours = TestCaseID`
- RF moves to the next test case

### Pass / Fail Logic
- A step **FAILS** if `WriteValue` or `ReadValue` does not match the expected value
- The test case continues even if individual steps fail (`Run Keyword And Continue On Failure`)
- The test case is marked **PASS** only if all steps passed

---

## 5. File Reference

### Robot Framework Files

#### `TestScenes.robot`
The main test file. Defines the test cases by listing which commands (BlockCmdIDs) to run and at which limit (Min/Max). This is the only file that needs to be edited when adding new test cases. Imports `variables.py` for broker credentials and Excel path.

#### `resources/test_keywords.robot`
Contains the reusable Robot Framework keywords that implement the test flow:
- **`Suite Connect`** — connects to the MQTT broker and loads the command repository
- **`Start Test Case`** — initialises state variables (TestCaseID, step counter, tele accumulator)
- **`Inject Step`** — looks up command data, publishes write+read inject payloads, verifies responses, accumulates tele data
- **`End Test Case`** — adds OperationHours to the tele payload and publishes it to `e2e/verify/tele`

#### `TestInnerLoop.robot`
A standalone test file used during development to validate the inner loop with a single hardcoded test step. Not used in production test runs.

#### `TestMQTTcom.robot`
An early test file used to verify basic MQTT publish/subscribe connectivity. Not used in production test runs.

#### `example.robot`
A basic Robot Framework example used for initial learning. Not part of the test framework.

---

### Python Libraries (`lib/`)

#### `lib/MqttClient.py`
A custom Robot Framework library that wraps `paho-mqtt`. Provides all MQTT-related keywords:
- **`Connect To Broker`** — connects to the broker with username/password authentication and waits for CONNACK
- **`Subscribe`** — subscribes to a topic and waits for the broker to confirm
- **`Publish Message`** — publishes a plain text message
- **`Publish Json Message`** — serialises a Python dict to JSON and publishes it
- **`Wait For Json Message`** — blocks until a JSON message containing a specified key arrives on a topic, then returns it as a dict
- **`Disconnect From Broker`** — cleanly stops the network loop and disconnects

`ROBOT_LIBRARY_SCOPE = 'SUITE'` ensures one shared connection is used across all test cases in a suite.

#### `lib/ExcelCommandRepository.py`
A custom Robot Framework library that loads the command repository from Excel and provides command lookup. Designed so that the data source can be replaced by a SharePoint API later — only this file changes.
- **`Load Commands`** — reads the Excel file and calculates all command strings using the Python functions
- **`Get Step`** — returns the full command data dict for a given `BlockCmdID` and `LimitType`
- **`Get Operation Hours Command`** — returns the SetOperationHours hex command for a given TestCaseID
- **`_calculate_commands`** *(internal)* — calls the four Python calculation functions; contains clear TODO markers where they can be replaced or extended

`ROBOT_LIBRARY_SCOPE = 'SUITE'` ensures the Excel is only loaded once per suite.

---

### Python Calculation Functions (`PythonFunctions/`)

These functions calculate the hex command strings from the raw parameters stored in the command repository. They are called by `ExcelCommandRepository._calculate_commands()`.

#### `PythonFunctions/Command_set.py` — `command_set()`
Calculates the **write command** hex string (`SetCommand`).
Inputs: `HeaderSet`, `Table`, `Block`, `ByteOffset`, `Bytes`, `MeasValue`
Output: hex string with checksum, e.g. `^@99300F2B00010020~`

#### `PythonFunctions/command_read.py` — `command_read()`
Calculates the **read command** hex string (`ReadCommand`).
Inputs: `HeaderRead`, `Table`, `Block`, `ByteOffset`, `Bytes`
Output: hex string with checksum, e.g. `^?99300F2B0001BF~`

#### `PythonFunctions/Read_Expected.py` — `read_expected()`
Calculates the **expected read response** hex string. Prepended with `SetExpected` to form `ReadExpected`.
Inputs: `HeaderRead`, `Table`, `Block`, `ByteOffset`, `Bytes`, `MeasValue`
Output: hex string with checksum, e.g. `^?99300F2B0001001F~`

#### `PythonFunctions/SetOperationHours.py` — `SetOperationHours()`
Calculates the **write operation hours** command. The value written equals the TestCaseID, which allows downstream systems to correlate telemetry data with test cases.
Input: `MeasValue` (= TestCaseID)
Output: hex string with checksum, e.g. `^@993012060002001D~`

---

### Command Repository

#### `TestRepository/00-Dev06_CommandGeneration.xlsm`
The central command repository. Each row defines one command entry. The framework reads the raw parameters (`Table`, `Block`, `ByteOffset`, `Bytes`, `MeasValue`, `HeaderSet`, `HeaderRead`) and calculates all command strings at runtime using the Python functions.

Key columns used at runtime:

| Column       | Used for                                      |
|--------------|-----------------------------------------------|
| `BlockCmdID` | Lookup key — referenced by name in robot files |
| `LimitType`  | Lookup key — `Min` or `Max`                   |
| `Table` … `MeasValue` | Inputs to calculation functions      |
| `HeaderSet` / `HeaderRead` | Inputs to calculation functions  |
| `SetExpected` | Expected write response from TRU             |
| `TeleField` / `TeleExpected` | Telemetry field name and expected value |
| `CloudField` / `CloudExpected` | Cloud field name and expected value |

---

### Simulator & Support Files

#### `main.py`
MicroPython program for the ESP32. Simulates the TRU by subscribing to `e2e/inject`, parsing the command payload, and publishing a simulated response to `e2e/verify/tru`. Introduces a 1-in-10 random failure to test the framework's error handling. Credentials and broker details are loaded from `secrets.py` on the device.

#### `tru_simulator.py`
PC-based version of the TRU simulator using standard Python and `paho-mqtt`. Functionally identical to `main.py` but runs on Windows without an ESP32. Useful for development and CI.

#### `test_mqtt.py`
A one-off connectivity test script used to verify that the PC can connect to the MQTT broker before running the full framework.

---

### Configuration Files

#### `variables.py`
Holds all sensitive and environment-specific configuration. **Excluded from version control** via `.gitignore`.

| Variable     | Purpose                        |
|--------------|--------------------------------|
| `BROKER`     | IP address of the MQTT broker  |
| `PORT`       | MQTT port (default 1883)       |
| `USERNAME`   | MQTT broker username           |
| `PASSWORD`   | MQTT broker password           |

#### `.vscode/settings.json`
VS Code workspace settings for the RobotCode extension. Adds `lib/` and `PythonFunctions/` to the Python path so the extension can resolve all libraries and keyword definitions.

#### `.gitignore`
Excludes `variables.py` (credentials) and generated RF output files (`output.xml`, `log.html`, `report.html`) from version control.

---

## 6. Future Extensions

| Item | Description |
|------|-------------|
| SharePoint API | Replace `ExcelCommandRepository` with `SharePointCommandRepository` implementing the same `load_commands()` / `get_step()` interface |
| Outer loop | After `End Test Case`, subscribe to `e2e/verify/cloud`, wait for a matching `TestCaseID`, and verify cloud field values against `CloudExpected` |
| WiFi setup | Add WiFi connection logic to `main.py` before the MQTT connect section |
| Results reporting | Parse `results/output.xml` to generate a structured test report per SceneID |
