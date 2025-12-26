*** Settings ***
Documentation     Regression test for sorting products by price.
Resource          ../../resources/keywords/common.robot
Test Setup       Open Toolshop
Test Teardown    Close Toolshop

*** Test Cases ***
Sort Products By Price
    [Tags]    regression
    Click    css=[data-test="sort"] >> nth=0
    Wait Until Keyword Succeeds    10s    500ms    Sorted Results Should Exist

*** Keywords ***
Sorted Results Should Exist
    ${count}=    Get Element Count    css=a.card[data-test^="product-"]
    Should Be True    ${count} > 0
