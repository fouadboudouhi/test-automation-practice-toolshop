*** Settings ***
Documentation     Regression: product details shows Add to cart.
Resource          ../../resources/keywords/common.robot
Suite Setup       Open Toolshop

*** Test Cases ***
Product Details Has Add To Cart Button
    [Tags]    regression
    Wait For At Least One Product Card
    Click    css=a.card[data-test^="product-"] >> nth=0
    Wait For Elements State    text=Add to cart    visible    timeout=15s