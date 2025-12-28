*** Settings ***
Documentation     Smoke: verify the login page renders the required fields and submit control.
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop


*** Test Cases ***
Login Page Shows Required Fields
    [Documentation]    Open the login page and assert email, password, and submit elements are visible.
    [Tags]    smoke

    Click    css=[data-test="nav-sign-in"]
    Wait For Elements State    css=[data-test="email"]           visible
    Wait For Elements State    css=[data-test="password"]        visible
    Wait For Elements State    css=[data-test="login-submit"]    visible