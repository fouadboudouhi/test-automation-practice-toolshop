*** Settings ***
Documentation     Smoke test verifying that navigation is present.
...               Pass criteria: the main navbar is visible within a reasonable timeout.
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop


*** Test Cases ***
Navigation Is Visible
    [Documentation]    Pass criteria: navbar is visible.
    [Tags]    smoke    navigation

    Wait For Elements State    css=nav.navbar    visible    timeout=20s