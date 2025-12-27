*** Settings ***
Documentation     Regression: navigate back after opening product details.
Resource          ../../resources/keywords/common.robot
Suite Setup       Open Toolshop

*** Test Cases ***
Navigate Back To Products From Details
    [Tags]    regression
    Wait For At Least One Product Card
    Click    css=a.card[data-test^="product-"] >> nth=0
    Wait For Elements State    text=Add to cart    visible    timeout=15s
    Go Back
    Wait For At Least One Product Card