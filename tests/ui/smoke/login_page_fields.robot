*** Settings ***
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop

*** Test Cases ***
Login Page Shows Required Fields
    [Tags]    smoke
    Click    css=[data-test="nav-sign-in"]
    Wait For Elements State    css=[data-test="email"]       visible
    Wait For Elements State    css=[data-test="password"]    visible
    Wait For Elements State    css=[data-test="login-submit"]    visible
