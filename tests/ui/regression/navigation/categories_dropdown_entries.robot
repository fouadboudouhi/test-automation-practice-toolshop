*** Settings ***
Documentation     Regression: verify the categories dropdown contains at least one entry.
...               Opens the categories dropdown in the navigation and asserts it lists one or more links.
Resource          ../../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop


*** Test Cases ***
Categories Dropdown Contains Entries
    [Documentation]    Open the categories dropdown and assert it contains at least one link.
    [Tags]    regression

    Wait For Elements State    css=[data-test="nav-categories"]    visible
    Click    css=[data-test="nav-categories"]
    Wait For Elements State    css=.dropdown-menu.show    visible

    ${count}=    Get Element Count    css=.dropdown-menu.show a
    Should Be True    ${count} > 0