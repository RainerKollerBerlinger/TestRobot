*** Settings ***
Resource          resources/test_keywords.robot
Suite Setup       Suite Connect
Suite Teardown    Disconnect From Broker

*** Variables ***
# ── Edit DEVICE_ID to target a different device ────────────────────────────────
${DEVICE_ID}       ESPTESTSIMULATOR
# ───────────────────────────────────────────────────────────────────────────────
${INJECT_TOPIC}    e2e/${DEVICE_ID}/inject
${VERIFY_TRU}      e2e/${DEVICE_ID}/verify/tru
${VERIFY_TELE}     e2e/${DEVICE_ID}/verify/tele
${VERIFY_CLOUD}    e2e/${DEVICE_ID}/verify/cloud
${SCENE_ID}        1
${CLOUD_TIMEOUT}   60

*** Test Cases ***
Set Four Commands To Minimum
    Start Test Case    test_case_id=1    test_case=Set Low Values    scene_id=${SCENE_ID}    device_id=${DEVICE_ID}
    Inject Step    ML5p2_99_ASC_ASCEN    Min
    Inject Step    ML5p2_99_Parameter_CO2SET   Min
    Inject Step    ML5p2_99_Parameter_DFR   Min
    Inject Step    ML5p2_99_Parameter_O2SET   Min
    End Test Case

Set Four Commands To Maximum
    Start Test Case    test_case_id=2    test_case=Set High Values    scene_id=${SCENE_ID}    device_id=${DEVICE_ID}
    Inject Step    ML5p2_99_ASC_ASCEN    Max
    Inject Step    ML5p2_99_Parameter_CO2SET   Max
    Inject Step    ML5p2_99_Parameter_O2SET   Max
    End Test Case
