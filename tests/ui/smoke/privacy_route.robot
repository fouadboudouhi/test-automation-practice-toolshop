*** Settings ***
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop

*** Test Cases ***
Privacy Page Is Reachable
    [Tags]    smoke
    Go To    ${BASE_URL}/privacy
    Wait For Elements State    css=h1    visible
    ${h}=    Get Text    css=h1
    Should Contain    ${h}    Privacy
