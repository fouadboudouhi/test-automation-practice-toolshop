*** Settings ***
Documentation     Smoke test verifying that navigation is present.
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop

*** Test Cases ***
Navigation Is Visible
    [Documentation]
    ...    Pass criteria:
    ...    - Navbar is visible
    ...    - Navbar text contains key navigation entries
    Wait For Elements State    css=nav.navbar    visible    timeout=20s
    ${nav_text}=    Get Text    css=nav.navbar
    Should Contain    ${nav_text}    Home
    Should Contain    ${nav_text}    Categories
    Should Contain    ${nav_text}    Contact