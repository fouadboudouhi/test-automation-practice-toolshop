*** Settings ***
Resource          ../../resources/keywords/common.robot
Test Setup       Open Toolshop
Test Teardown    Close Toolshop
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop

*** Test Cases ***
Privacy Page Shows Heading
    [Tags]    regression
    Go To    ${BASE_URL}/privacy
    Wait For Elements State    css=h1    visible
    ${h}=    Get Text    css=h1
    Should Contain    ${h}    Privacy
