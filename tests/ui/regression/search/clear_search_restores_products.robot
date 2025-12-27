*** Settings ***
Documentation     Regression: search then clear search and products are shown again.
Resource          ../../resources/keywords/common.robot
Suite Setup       Open Toolshop

*** Test Cases ***
Clearing Search Restores Product List
    [Tags]    regression
    Wait For At Least One Product Card

    Wait For Elements State    css=[data-test="search-query"]    visible    timeout=15s
    Fill Text    css=[data-test="search-query"]    hammer
    Click        css=[data-test="search-submit"]

    # Clear
    Fill Text    css=[data-test="search-query"]    ${EMPTY}
    Click        css=[data-test="search-submit"]

    Wait For At Least One Product Card