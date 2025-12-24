*** Settings ***
Documentation     Regression test for invalid login handling.
Resource          ../../resources/keywords/common.robot

*** Test Cases ***
Login With Invalid Credentials
    Open Toolshop
    Click    css=[data-test="nav-sign-in"]
    Fill Text    css=input#email       invalid@example.com
    Fill Text    css=input#password    wrongpassword
    Click        css=[data-test="login-submit"]
    Wait For Elements State    text=Invalid credentials    visible    timeout=10s
    Close Toolshop
