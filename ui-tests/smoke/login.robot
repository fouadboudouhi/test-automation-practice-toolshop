*** Settings ***
Documentation     Smoke test verifying that login is possible with demo credentials.
...               The test validates successful authentication by URL change,
...               not by UI rendering details.
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop

*** Test Cases ***
Login Is Possible
    [Tags]    smoke    login

    Click Sign In
    Wait For Login Form

    Fill Login Credentials
    Submit Login Form

    Verify Login Successful


*** Keywords ***
Click Sign In
    Wait For Elements State
    ...    css=[data-test="nav-sign-in"]
    ...    visible
    ...    timeout=20s
    Click    css=[data-test="nav-sign-in"]

Wait For Login Form
    Wait For Elements State
    ...    css=input#email
    ...    visible
    ...    timeout=20s
    Wait For Elements State
    ...    css=input#password
    ...    visible
    ...    timeout=20s

Fill Login Credentials
    Fill Text    css=input#email       ${EMAIL}
    Fill Text    css=input#password    ${PASSWORD}

Submit Login Form
    Click    css=[data-test="login-submit"]

Verify Login Successful
    # CI-stable assertion:
    # Login is considered successful once the user is redirected
    # to the account area.
    Wait Until Location Contains    /account    timeout=20s