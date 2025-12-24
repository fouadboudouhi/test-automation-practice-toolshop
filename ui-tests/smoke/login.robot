*** Settings ***
Documentation     Smoke test verifying that login is possible.
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop

*** Test Cases ***
Login Is Possible
    [Documentation]
    ...    Pass criteria:
    ...    - Sign-in entry is clickable
    ...    - Login form fields are visible
    ...    - After submit, the email input disappears (detached)
    Wait For Elements State    css=[data-test="nav-sign-in"]    visible    timeout=20s
    Click    css=[data-test="nav-sign-in"]

    Wait For Elements State    css=input#email       visible    timeout=20s
    Wait For Elements State    css=input#password    visible    timeout=20s

    Fill Text    css=input#email       ${EMAIL}
    Fill Text    css=input#password    ${PASSWORD}
    Click        css=[data-test="login-submit"]

    Wait For Elements State    css=input#email    detached    timeout=20s
    Wait For Elements State    css=nav.navbar     visible     timeout=20s