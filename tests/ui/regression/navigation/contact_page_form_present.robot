*** Settings ***
Documentation     Regression: verify the contact page exposes a form with at least one input field.
Resource          ../../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop


*** Test Cases ***
Contact Page Has A Form
    [Documentation]    Navigate to the contact page and assert a form with input fields is present.
    [Tags]    regression

    Go To    ${BASE_URL}/contact
    Wait For Elements State    css=form    visible

    ${count}=    Get Element Count    css=form input
    Should Be True    ${count} > 0