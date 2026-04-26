# demo.tape — VHS recording script  (v3)
# Generates docs/demo.gif for the README
# Tool: https://github.com/charmbracelet/vhs

Output docs/demo.gif

Set Shell "bash"
Set FontSize 13
Set Width 900
Set Height 560
Set Theme "Dracula"
Set Padding 20

Hide
  Type "clear"
  Enter
  Sleep 500ms
Show

Type "python examples/demo_run.py"
Enter
Sleep 60s
