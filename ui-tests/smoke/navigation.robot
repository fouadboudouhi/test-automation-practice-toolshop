*** Settings ***
Resource    ../resources/keywords/common.robot

*** Test Cases ***
Navigation Works
    Open Toolshop
    Click    text=Categories
    Wait For Elements State    css=.card    visible
    Close Toolshop
