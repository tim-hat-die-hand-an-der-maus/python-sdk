## v6.0.0 (2025-05-28)

### Feat

- add close method to release client resources
- migrate client to asyncio

## v5.0.0 (2025-05-28)

### BREAKING CHANGE

- removed discontinued metadata update method
- Naming of request model properties now follows Python
conventions. They are serialized as camelCase, but should be populated
by their snake_case name.

### Feat

- allow updating/creating telegram users in API
- add get_canonical_user method
- allow passing user ID for queue items

### Perf

- use Pydantic to deserialize json


- remove metadata update method

## v4.0.0 (2025-04-20)

### Feat

- make MovieResponse.imdb optional

### Fix

- use preferred metadata in fuzzy_search_movie

## v3.5.4 (2025-04-19)

### Fix

- escape dots in markdown

## v3.5.3 (2025-04-19)

### Fix

- escape dots in markdown

## v3.5.2 (2025-04-19)

### Fix

- escape dash

## v3.5.1 (2025-04-19)

### Fix

- escape parens in markdown

## v3.5.0 (2025-04-19)

### Feat

- show and prefer TMDB metadata in markdown

## v3.4.0 (2025-04-19)

### Feat

- include tmdb in movie response

## v3.3.1 (2025-04-18)

### Fix

- handle camelcase aliases

## v3.3.0 (2025-04-17)

### Feat

- mark info page URL as required

## v3.2.0 (2025-04-17)

### Feat

- use infoPageUrl if available

## v3.1.1 (2025-04-16)

### Fix

- **deps**: update dependency pydantic to ==2.11.*

## v3.1.0 (2025-01-10)

### Feat

- Allow base URL customization

## v3.0.1 (2025-01-10)

### Fix

- Add py.typed marker

## v3.0.0 (2025-01-10)

### Feat

- Update to Poetry 2
- Update a bunch of deps

## v2.0.4 (2024-01-25)

### Fix

- **deps**: update dependency thefuzz to ^0.22.0

## v2.0.3 (2023-12-20)

### Fix

- **deps**: update dependency httpx to ^0.26.0

## v2.0.2 (2023-12-17)

### Fix

- **#20**: raise HTTP errors for unsuccessful responses

## v2.0.1 (2023-12-17)

### Fix

- Fix test names

## v2.0.0 (2023-12-17)

### Feat

- **TimApi**: Use httpx.Client

### Fix

- **TimApi**: Make token propery non-public

## v1.0.0 (2023-12-17)

- Initial stable release
