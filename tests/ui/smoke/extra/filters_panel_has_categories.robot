*** Settings ***
Resource          ../../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop

*** Test Cases ***
Filters Show Category Options
    [Tags]    smoke
    Go To    ${BASE_URL}
    Wait For At Least One Product Card

    # Strict-mode safe: wait for ONE matching element
    Wait Until Keyword Succeeds    60s    2s
    ...    Wait For Elements State    xpath=(//*[@data-test and starts-with(@data-test,"category-")])[1]    visible    timeout=2s

    ${count}=    Get Element Count    css=[data-test^="category-"]
    Should Be True    ${count} > 0