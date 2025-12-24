*** Settings ***
Resource    ../resources/keywords/common.robot

*** Test Cases ***
Search Returns Results
    Open Toolshop
    Fill Text    css=input[type="search"]    hammer
    Press Keys  css=input[type="search"]    Enter
    Wait For Elements State    css=.card    visible
    Close Toolshop
