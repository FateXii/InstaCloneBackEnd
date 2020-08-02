# Endpoints

## /profiles/

### Method: `POST`

Create a profile also creates a user without admin privileges

#### Auth:

Access is only given when the following is criteria is met:

Requesting User:

- Everyone

### Method: `GET`

Lists all profiles

#### Auth:

Access is only given when the following is criteria is met:

Requesting User:

- IsAdmin

## /profiles/\${ID}/

### Method: `POST`

Not Allowed

### Method: `GET`

Returns a detailed view of profile with id `${ID}`

#### Auth:

Access is only given when the following is criteria is met:

Requesting profile:

- IsAdmin, or
- IsAuthenticated, and is following Profile with `id == ${ID}`, or
- Profile with `id == ${ID}` is not private

### Method: `PUT`

Makes a full update of profile with `id == ${ID}`

#### Auth:

Access is only given when the following is criteria is met:

Requesting profile:

- IsAdmin, or
- IsAuthenticated, and is Profile with `id == ${ID}`

### Method: `PATCH`

Makes a partial update of profile with `id == ${ID}`

#### Auth:

Access is only given when the following is criteria is met:

Requesting profile:

- IsAdmin, or
- IsAuthenticated, and is Profile with `id == ${ID}`

### Method: `DELETE`

Destroys profile with `id == ${ID}`

#### Auth:

Access is only given when the following is criteria is met:

Requesting profile:

- IsAdmin, or
- IsAuthenticated, and is Profile with `id == ${ID}`

## /profiles/\${ID}/follow

### Method: `POST`

Add profile with `id == ${ID}` to current profiles following list
if profile with `id == ${ID}` is private add to requests table

#### Auth:

Access is only given when the following criteria is met:

Requesting profile:

- IsAuthenticated, and is not Profile with `id == ${ID}`

## /profiles/\${ID}/following

### Method: `POST`

Not Allowed

### Method: `GET`

Returns a list view of all Profiles followed by profile with id `${ID}`

#### Auth:

Access is only given when the following is criteria is met:

Requesting profile:

- IsAdmin, or
- IsCurrentProfile, or
- IsAuthenticated, and is following Profile with `id == ${ID}`, or
- Profile with `id == ${ID}` is not private

### Method: `PUT`

Not Allowed

### Method: `PATCH`

Not allowed

### Method: `DELETE`

Not allowed

## /profiles/\${ID}/following/posts

### Method: `POST`

Not Allowed

### Method: `GET`

Returns a list view of all posts by profiles followed by Profile with id `${ID}`

#### Auth:

Access is only given when the following is criteria is met:

Requesting profile:

- IsAdmin, or
- IsCurrentProfile

### Method: `PUT`

Not Allowed

### Method: `PATCH`

Not allowed

### Method: `DELETE`

Not allowed

## /profiles/\${ID}/followed_by

### Method: `POST`

Not Allowed

### Method: `GET`

Returns a list view of all Profiles currently following profile with id `${ID}`

#### Auth:

Access is only given when the following is criteria is met:

Requesting profile:

- IsAdmin, or
- IsCurrentProfile, or
- IsAuthenticated, and is following Profile with `id == ${ID}`, or
- Profile with `id == ${ID}` is not private

### Method: `PUT`

Not Allowed

### Method: `PATCH`

Not allowed

### Method: `DELETE`

Not allowed

## /profiles/\${ID}/follow_requests

### Method: `POST`

Not Allowed

### Method: `GET`

Returns a list view of all Profiles that have requested to follow profile with id `${ID}`

#### Auth:

Access is only given when the following is criteria is met:

Requesting profile:

- IsAdmin, or
- IsCurrentProfile

### Method: `PUT`

Not Allowed

### Method: `PATCH`

Not allowed

### Method: `DELETE`

Not allowed

## /profiles/\${ID}/follow_requests/accept/\${Request-ID}

### Method: `POST`

Accept follow request with `id == ${Request-ID}`

#### Auth:

Access is only given when the following is criteria is met:

Requesting profile:

- IsCurrentProfile

### Method: `GET`

Not Allowed

### Method: `PUT`

Not Allowed

### Method: `PATCH`

Not allowed

### Method: `DELETE`

Not allowed

## /profiles/\${ID}/follow_requests/reject/\${Request-ID}

### Method: `POST`

Reject follow request with `id == ${Request-ID}`

#### Auth:

Access is only given when the following is criteria is met:

Requesting profile:

- IsCurrentProfile

### Method: `GET`

Not Allowed

### Method: `PUT`

Not Allowed

### Method: `PATCH`

Not allowed

### Method: `DELETE`

Not allowed

## /profiles/\${ID}/posts

### Method: `POST`

Not Allowed

### Method: `GET`

Returns a list view of all posts by profile with id `${ID}`

#### Auth:

Access is only given when the following is criteria is met:

Requesting profile:

- IsAdmin, or
- IsAuthenticated, and is following Profile with `id == ${ID}`, or
- Profile with `id == ${ID}` is not private

### Method: `PUT`

Not Allowed

### Method: `PATCH`

Not allowed

### Method: `DELETE`

Not Allowed

## /profiles/\${Profile-ID}/posts/\${Post-ID}/

### Method: `POST`

Not Allowed

### Method: `GET`

Returns a single post with `id == ${Post-ID}` from profile with `id == ${Profile-ID}`

#### Auth:

Access is only given when the following is criteria is met:

Requesting profile:

- IsAdmin, or
- IsAuthenticated, and is following Profile with `id == ${ID}`, or
- Profile with `id == ${ID}` is not private

### Method: `PUT`

Not Allowed

### Method: `PATCH`

Not allowed

### Method: `DELETE`

Access is only given when the following is criteria is met:

Requesting profile:

- IsAdmin

## /profiles/\${Profile-ID}/posts/\${Post-ID}/comments

### Method: `POST`

Not Allowed

### Method: `GET`

Returns a list view of all comments on post with id `${Post-ID}`

#### Auth:

Access is only given when the following is criteria is met:

Requesting profile:

- IsAdmin, or
- IsAuthenticated, and is following Profile with `id == ${ID}`, or
- Profile with `id == ${ID}` is not private

### Method: `PUT`

Not Allowed

### Method: `PATCH`

Not allowed

### Method: `DELETE`

## /profiles/\${Profile-ID}/posts/\${Post-ID}/comments/\${Comment-ID}/

### Method: `POST`

Not Allowed

### Method: `GET`

Returns a single comment with `id == ${Comment-ID}` from post with `id == ${Post-ID}`

#### Auth:

Access is only given when the following is criteria is met:

Requesting profile:

- IsAdmin, or
- IsAuthenticated, and is following Profile with `id == ${Profile-ID}`, or
- Profile with `id == ${ID}` is not private

### Method: `PUT`

Not Allowed

### Method: `PATCH`

Not allowed

### Method: `DELETE`
