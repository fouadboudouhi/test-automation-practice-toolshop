*** Settings ***
Resource    ../resources/keywords/common.robot

*** Variables ***
${EMAIL}     %{DEMO_EMAIL}
${PASSWORD}  %{DEMO_PASSWORD}

*** Test Cases ***
Login Works
    Open Toolshop
    Click    text=Sign in
    Fill Text    id=email    ${EMAIL}
    Fill Text    id=password ${PASSWORD}
    Click    text=Login
    Wait For Elements State    text=My account    visible
    Close Toolshop
