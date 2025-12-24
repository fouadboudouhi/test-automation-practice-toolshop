*** Settings ***
Documentation     Smoke test verifying that search is present.
Resource          ../resources/keywords/common.robot
Suite Setup       Open Toolshop
Suite Teardown    Close Toolshop

*** Test Cases ***
Search Field Is Available
    [Documentation]
    ...    Pass criteria:
    ...    - Search input is visible on the landing page
    Wait For Elements State    css=[data-test="search-query"]    visible    timeout=20s