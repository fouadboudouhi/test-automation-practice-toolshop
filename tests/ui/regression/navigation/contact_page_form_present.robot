*** Settings ***
Resource          ../../resources/keywords/common.robot
Test Setup       Open Toolshop
Test Teardown    Close Toolshop
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop

*** Test Cases ***
Contact Page Has A Form
    [Tags]    regression
    Go To    ${BASE_URL}/contact
    Wait For Elements State    css=form    visible
    ${count}=    Get Element Count    css=form input
    Should Be True    ${count} > 0
