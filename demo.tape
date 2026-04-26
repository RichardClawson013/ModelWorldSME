# demo.tape — VHS recording script
# Generates docs/demo.gif for the README
# Tool: https://github.com/charmbracelet/vhs

Output docs/demo.gif

Set Shell "bash"
Set FontSize 13
Set Width 900
Set Height 540
Set Theme "Dracula"
Set TypingSpeed 20ms
Set Padding 20

Hide
  Type "pip install -e . -q && clear"
  Enter
  Sleep 3s
Show

Type "python examples/demo_run.py"
Enter
Sleep 15s
