*** Settings ***
Documentation     Regression: apply and clear brand filter; list should still show results.
Resource          ../../resources/keywords/common.robot
Test Setup       Open Toolshop
Test Teardown    Close Toolshop
Suite Setup       Open Toolshop

*** Test Cases ***
Clear Brand Filter Restores Results
    [Tags]    regression
    Wait For At Least One Product Card

    Wait For Elements State    css=input[data-test^="brand-"] >> nth=0    visible    timeout=15s
    Scroll To Element          css=input[data-test^="brand-"] >> nth=0

    ${before}=    Get Element Count    css=a.card[data-test^="product-"]

    Click    css=input[data-test^="brand-"] >> nth=0
    Wait For At Least One Product Card
    ${after_filter}=    Get Element Count    css=a.card[data-test^="product-"]

    # clear (toggle again)
    Click    css=input[data-test^="brand-"] >> nth=0
    Wait For At Least One Product Card
    ${after_clear}=    Get Element Count    css=a.card[data-test^="product-"]

    Should Be True    ${after_clear} >= 1
    Should Be True    ${before} >= 1
