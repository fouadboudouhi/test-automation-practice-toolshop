*** Settings ***
Documentation     Smoke: verify brand filter options are present on the products page.
...               Uses a strict-mode safe wait by targeting the first matching brand element via XPath.
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop


*** Test Cases ***
Filters Show Brand Options
    [Documentation]    Open the products page and assert at least one brand filter option is visible.
    [Tags]    smoke

    Go To    ${BASE_URL}
    Wait For At Least One Product Card

    # Strict-mode safe: wait for ONE matching element.
    Wait Until Keyword Succeeds    60s    2s
    ...    Wait For Elements State    xpath=(//*[@data-test and starts-with(@data-test,"brand-")])[1]    visible    timeout=2s

    ${count}=    Get Element Count    css=[data-test^="brand-"]
    Should Be True    ${count} > 0