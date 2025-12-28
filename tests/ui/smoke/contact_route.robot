*** Settings ***
Documentation     Smoke: verify the contact page is reachable and renders expected elements.
...               Uses a tolerant readiness check because the page can render slower in headless CI
...               and the heading level may differ.
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop


*** Test Cases ***
Contact Page Is Reachable
    [Documentation]    Navigate to /contact and wait until the page is considered ready.
    [Tags]    smoke

    Go To    ${BASE_URL}/contact
    # Contact can render slower in headless CI; also heading level may differ.
    Wait Until Keyword Succeeds    60s    2s    Contact Page Should Be Ready


*** Keywords ***
Contact Page Should Be Ready
    [Documentation]    Determine contact page readiness by checking common indicators:
    ...                - h1 Contact, or
    ...                - h2 Contact, or
    ...                - a form element.
    ${ok}=    Run Keyword And Return Status    Wait For Elements State    css=h1:has-text("Contact")    visible    2s
    Run Keyword If    ${ok}    Return From Keyword

    ${ok}=    Run Keyword And Return Status    Wait For Elements State    css=h2:has-text("Contact")    visible    2s
    Run Keyword If    ${ok}    Return From Keyword

    ${ok}=    Run Keyword And Return Status    Wait For Elements State    css=form    visible    2s
    Should Be True    ${ok}