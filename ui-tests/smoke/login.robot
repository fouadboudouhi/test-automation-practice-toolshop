*** Settings ***
Documentation     Smoke test verifying that login is possible with demo credentials.
...               Authentication correctness and authorization are not validated.
Resource          ../resources/keywords/common.robot

*** Variables ***
${EMAIL}           %{DEMO_EMAIL}
${PASSWORD}        %{DEMO_PASSWORD}

*** Test Cases ***
Login Is Possible
    [Documentation]    Verifies that a user can log in and reach the account area.
    Open Toolshop

    Click    css=[data-test="nav-sign-in"]

    Wait For Elements State    css=input#email       visible    timeout=15s
    Wait For Elements State    css=input#password    visible    timeout=15s

    Fill Text    css=input#email       ${EMAIL}
    Fill Text    css=input#password    ${PASSWORD}

    Click    css=[data-test="login-submit"]

    # Smoke-level verification: unique page title element exists
    Wait For Elements State    css=[data-test="page-title"]    visible    timeout=15s

    Close Toolshop