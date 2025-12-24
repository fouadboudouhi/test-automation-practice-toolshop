*** Settings ***
Documentation     Smoke test verifying availability of the search input.
...               Search execution and result correctness are explicitly out of scope.
Resource          ../resources/keywords/common.robot

*** Test Cases ***
Search Field Is Available
    [Documentation]    Checks that the search input field is present and visible.
    Open Toolshop
    Wait For Elements State    css=[data-test="search-query"]    visible    timeout=15s
    Close Toolshop