# Chapter 1: Mental Model

## Think of a table as a spreadsheet with rules

A spreadsheet lets you type anything anywhere. A database table is a
spreadsheet where the *columns have locked-in types and rules*, and some
columns are cross-referenced against other sheets.

```
Spreadsheet:  any cell, any type, no cross-sheet guarantees
Database:     typed columns + constraints + enforced cross-table references
```

## Think of a primary key as a row's permanent address

Everything else in the database that needs to "point at" a row uses the
primary key, never the row's position or its other column values (those can
change; the primary key shouldn't).

## Think of a foreign key as a promise the database keeps for you

`orders.user_id REFERENCES users(id)` is a standing promise: "every order
belongs to a user that exists." You don't have to check this in application
code — the database rejects any write that would break the promise. This is
the core value of relational integrity: you stop trusting your own
application code to never have a bug, and let the database enforce the
invariant at the lowest possible layer.

## Think of normalization as "each fact lives in exactly one place"

If a fact (a user's email, a product's price) is duplicated across rows,
you now have N places that can disagree about the truth. Normalization is
the discipline of storing each fact once and referencing it everywhere
else. Denormalization is the deliberate, measured trade of that discipline
for read speed — done consciously, not by accident.
