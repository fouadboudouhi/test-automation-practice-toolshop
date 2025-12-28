*** Settings ***
Documentation     Regression: verify the privacy page renders a heading containing "Privacy".
Resource          ../../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop


*** Test Cases ***
Privacy Page Shows Heading
    [Documentation]    Navigate to the privacy page and assert the H1 heading contains "Privacy".
    [Tags]    regression

    Go To    ${BASE_URL}/privacy
    Wait For Elements State    css=h1    visible

    ${h}=    Get Text    css=h1
    Should Contain    ${h}    Privacy