# Catalog write-path contract

| Request | Condition | Response |
|---------|-----------|----------|
| POST /food | CatalogItem invalid | 400 with a ProblemDetails body |
| POST /food | CatalogItem valid | 201 with a Location header |
| PUT /food | CatalogItem invalid | 400 with a ProblemDetails body |
| PUT /food | ID does not exist | 404 |
| PUT /food | otherwise | 200 |
| DELETE /food/{id} | ID does not exist | 404 |
| DELETE /food/{id} | otherwise | 204 |
| GET /food/{id} | ID does not exist | 404 |

Invalid means Name is null, empty or whitespace, Price is negative, or InStock is negative.

GET /food stays untouched. The implementer owns Controllers/ and Shared/ and changes nothing else.
