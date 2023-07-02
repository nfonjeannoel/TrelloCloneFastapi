# Trello Backend Fastapi clone

## Description

This is a clone of the backend of Trello, made with Fastapi and sql databases.

## Project database requirements

1. A User can sign up to the application
2. A User can Login to the application securely with a password and email.
3. JWT is used for authentication
4. A User can create boards (public or private)
5. A User can create lists in a board. (columns) and they can be moved, renamed and deleted.
6. A User can create cards in a list. (tasks) and they can be moved, renamed and deleted.
7. Comments can be added to cards by users who have access to the board
8. A checklist can be added to cards by users who have access to the board
9. users can be added as members to card to see card updates
10. Any activity on the card should be tracked
11. a card can be archived so that it is not visible on the board but is still accessible
12. A user can add labels to a card, edit label names and colors, create new labels and delete labels
13. A card can have a due date, and a reminder date and time
14. User can attach files and images to cards