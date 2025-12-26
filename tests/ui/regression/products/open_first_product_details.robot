*** Settings ***
Documentation     Regression: open first product details from product listing (home).
Resource          ../../resources/keywords/common.robot
Test Setup       Open Toolshop
Test Teardown    Close Toolshop
Suite Setup       Open Toolshop

*** Test Cases ***
Open First Product Details
    [Tags]    regression
    Wait For At Least One Product Card
    Click    css=a.card[data-test^="product-"] >> nth=0
    Wait For Elements State    text=Add to cart    visible    timeout=15s
