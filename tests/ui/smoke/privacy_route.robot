*** Settings ***
Documentation     Smoke: verify the privacy page is reachable and renders a "Privacy" heading.
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop


*** Test Cases ***
Privacy Page Is Reachable
    [Documentation]    Navigate to /privacy and assert the H1 heading contains "Privacy".
    [Tags]    smoke

    Go To    ${BASE_URL}/privacy
    Wait For Elements State    css=h1    visible

    ${h}=    Get Text    css=h1
    Should Contain    ${h}    Privacy