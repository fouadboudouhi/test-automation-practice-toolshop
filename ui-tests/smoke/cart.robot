*** Settings ***
Resource    ../resources/keywords/common.robot

*** Test Cases ***
Add To Cart Works
    Open Toolshop
    Click    css=.card >> nth=0
    Click    text=Add to cart
    Wait For Elements State    text=Shopping cart    visible
    Close Toolshop
