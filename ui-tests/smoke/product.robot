*** Settings ***
Resource    ../resources/keywords/common.robot

*** Test Cases ***
Product Detail Page Loads
    Open Toolshop
    Click    css=.card >> nth=0
    Wait For Elements State    css=button    visible
    Close Toolshop
