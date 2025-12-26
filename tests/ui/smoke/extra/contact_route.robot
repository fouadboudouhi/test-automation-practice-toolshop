*** Settings ***
Resource          ../../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop

*** Test Cases ***
Contact Page Is Reachable
    [Tags]    smoke
    Go To    ${BASE_URL}/contact
    # Contact can render slower in headless CI; also heading level may differ.
    Wait Until Keyword Succeeds    60s    2s    Contact Page Should Be Ready


*** Keywords ***
Contact Page Should Be Ready
    ${ok}=    Run Keyword And Return Status    Wait For Elements State    css=h1:has-text("Contact")    visible    2s
    Run Keyword If    ${ok}    Return From Keyword
    ${ok}=    Run Keyword And Return Status    Wait For Elements State    css=h2:has-text("Contact")    visible    2s
    Run Keyword If    ${ok}    Return From Keyword
    ${ok}=    Run Keyword And Return Status    Wait For Elements State    css=form    visible    2s
    Should Be True    ${ok}
