*** Settings ***
Documentation     Regression: first product card image src is not empty.
Resource          ../../resources/keywords/common.robot
Test Setup       Open Toolshop
Test Teardown    Close Toolshop
Suite Setup       Open Toolshop

*** Test Cases ***
Product Card Image Src Is Not Empty
    [Tags]    regression
    Wait For At Least One Product Card
    ${src}=    Get Attribute    css=a.card[data-test^="product-"] img >> nth=0    src
    Should Not Be Empty    ${src}
