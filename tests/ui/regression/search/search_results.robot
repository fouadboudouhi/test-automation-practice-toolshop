*** Settings ***
Documentation     Regression test for search functionality.
Resource          ../../resources/keywords/common.robot

*** Test Cases ***
Search Returns Matching Products
    [Tags]    regression
    Open Toolshop
    Fill Text    css=[data-test="search-query"]    hammer
    Click        css=[data-test="search-submit"]
    Wait Until Keyword Succeeds    10s    500ms    Search Results Should Exist
    Close Toolshop

*** Keywords ***
Search Results Should Exist
    ${count}=    Get Element Count    css=a.card[data-test^="product-"]
    Should Be True    ${count} > 0
