# Objective
Assist kindergarden teacher in filling their work plan for next month.
Site and AI response are in Polish.

# Workflow
Teacher (user) enteres (one or several) "aktywność" (activity planed for next lesson).
The website fills (using AI) "moduł" (one of standard educational modules ie. emotions, art forms), "podstawa programowa" (list of number of paragraphs refering to core curriculum document) and "cele" (educational objectives).

All is represented in tabular form and is easily copied to text file in google docs.

# UI 

We are focusing on single page with below elements:

1) Text field for theme of the week
2) Table with:
    - Moduł
    - Podstawa Programowa
    - Cele
    - Aktywność
3) Buttons allowing to autofill all rows or single row

Additional effects - Numbers from podstawa programowa should show corresponding textx paragraph on ouse over.

# Simplicity
Project is to be run localy.
We are creating a MVP.
Keep it simple.
No authorisation, user accounts.

# Technologies to use
Python + Django for UI
Python + LangGraph to run AI workflow in the backend