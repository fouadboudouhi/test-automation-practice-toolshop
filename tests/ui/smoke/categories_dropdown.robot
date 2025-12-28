*** Settings ***
Documentation     Smoke: verify the categories dropdown can be opened and contains at least one entry.
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop


*** Test Cases ***
Categories Dropdown Opens
    [Documentation]    Open the categories dropdown in the navbar and assert it shows one or more links.
    [Tags]    smoke

    Wait For Elements State    css=[data-test="nav-categories"]    visible
    Click    css=[data-test="nav-categories"]
    Wait For Elements State    css=.dropdown-menu.show    visible

    ${count}=    Get Element Count    css=.dropdown-menu.show a
    Should Be True    ${count} > 0