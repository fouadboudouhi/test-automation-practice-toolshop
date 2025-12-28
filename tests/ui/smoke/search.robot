*** Settings ***
Documentation     Smoke test verifying that search is present.
...               Pass criteria: the search input is visible within a reasonable timeout.
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop


*** Test Cases ***
Search Field Is Available
    [Documentation]    Pass criteria: search input is visible.
    [Tags]    smoke    search

    Wait For Elements State    css=[data-test="search-query"]    visible    timeout=20s