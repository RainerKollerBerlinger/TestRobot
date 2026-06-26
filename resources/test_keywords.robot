*** Settings ***
Library      ../lib/MqttClient.py
Library      ../PythonFunctions/SharePointCommandRepository.py
Library      ../lib/BlobStorage.py
Library      ../PythonFunctions/SetOperationHours.py
Library      Collections
Variables    ../lib/config.py    # provides ${BLOB_ROOT} and connection settings

*** Variables ***
${STEP_TIMEOUT}    30

*** Keywords ***
Suite Connect
    Connect To Broker    port=8883
    Subscribe    ${VERIFY_TRU}
    Load Commands

Start Test Case
    [Arguments]    ${test_case_id}    ${test_case}    ${scene_id}    ${device_id}
    Set Suite Variable    ${TC_ID}          ${test_case_id}
    Set Suite Variable    ${TC_NAME}        ${test_case}
    Set Suite Variable    ${SCENE_ID}       ${scene_id}
    Set Suite Variable    ${DEVICE_ID}      ${device_id}
    Set Suite Variable    ${STEP}           ${0}
    ${CLOUD_CHECKS}=    Create List
    Set Suite Variable    ${CLOUD_CHECKS}
    &{tele}=    Create Dictionary
    ...    DeviceID=${device_id}    SceneID=${scene_id}
    ...    TestCaseID=${test_case_id}    TestCase=${test_case}
    Set Suite Variable    ${TELE}    ${tele}

Inject Step
    [Arguments]    ${block_cmd_id}    ${limit_type}
    ${step_data}=    Get Step    ${block_cmd_id}    ${limit_type}
    ${STEP}=    Evaluate    ${STEP} + 1
    Set Suite Variable    ${STEP}

    &{write_payload}=    Create Dictionary
    ...    DeviceID=${DEVICE_ID}    SceneID=${SCENE_ID}
    ...    TestCaseID=${TC_ID}      TestCase=${TC_NAME}
    ...    Step=${STEP}             BlockCmdID=${block_cmd_id}
    ...    SetCommand=${step_data}[SetCommand]
    ...    SetExpected=${step_data}[SetExpected]

    Publish Json Message    ${INJECT_TOPIC}    ${write_payload}
    ${write_result}=    Wait For Json Message    ${VERIFY_TRU}    required_key=SetCommand    timeout=${STEP_TIMEOUT}
    Run Keyword And Continue On Failure    Should Be Equal    ${write_result}[WriteValue]    ${step_data}[SetExpected]

    &{read_payload}=    Create Dictionary
    ...    DeviceID=${DEVICE_ID}    SceneID=${SCENE_ID}
    ...    TestCaseID=${TC_ID}      TestCase=${TC_NAME}
    ...    Step=${STEP}             BlockCmdID=${block_cmd_id}
    ...    ReadCommand=${step_data}[ReadCommand]
    ...    ReadExpected=${step_data}[ReadExpected]
    ...    TeleField=${step_data}[TeleField]
    ...    TeleExpected=${step_data}[TeleExpected]
    ...    CloudField=${step_data}[CloudField]
    ...    CloudExpected=${step_data}[CloudExpected]

    Publish Json Message    ${INJECT_TOPIC}    ${read_payload}
    ${read_result}=    Wait For Json Message    ${VERIFY_TRU}    required_key=ReadCommand    timeout=${STEP_TIMEOUT}
    Run Keyword And Continue On Failure    Should Be Equal    ${read_result}[ReadValue]    ${step_data}[ReadExpected]

    &{tele_entry}=    Create Dictionary
    ...    Step=${STEP}
    ...    ReadCommand=${step_data}[ReadCommand]
    ...    ReadExpected=${step_data}[ReadExpected]
    ...    ReadValue=${read_result}[ReadValue]
    ...    TeleField=${step_data}[TeleField]
    ...    TeleExpected=${step_data}[TeleExpected]
    ...    CloudField=${step_data}[CloudField]
    ...    CloudExpected=${step_data}[CloudExpected]
    Set To Dictionary    ${TELE}    ${block_cmd_id}=${tele_entry}

    &{cloud_check}=    Create Dictionary
    ...    field=${step_data}[CloudField]    expected=${step_data}[CloudExpected]
    Append To List    ${CLOUD_CHECKS}    ${cloud_check}

End Test Case
    ${op_hours_cmd}=    Set Operation Hours    ${TC_ID}
    Publish Message    ${INJECT_TOPIC}    ${op_hours_cmd}
    Set To Dictionary    ${TELE}    OperationHours=${TC_ID}
    Publish Json Message    ${VERIFY_TELE}    ${TELE}
    ${cloud_data}=    Wait For Blob File    ${BLOB_ROOT}    ${DEVICE_ID}    ${TC_ID}    timeout=${CLOUD_TIMEOUT}
    Publish Json Message    ${VERIFY_CLOUD}    ${cloud_data}
    FOR    ${check}    IN    @{CLOUD_CHECKS}
        ${cloud_value}=    Get Nested Value    ${cloud_data}    ${check}[field]
        Run Keyword And Continue On Failure
        ...    Should Be Equal As Strings    ${cloud_value}    ${check}[expected]
    END
