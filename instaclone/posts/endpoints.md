# Endpoints

## /posts/

### Method: `POST`

Create a profile also creates a user without admin privileges

#### Auth:

Access is only given when the following is criteria is met:

Requesting User:

- Everyone

### Method: `GET`

Lists all posts

#### Auth:

Access is only given when the following is criteria is met:

Requesting User:

- IsAdmin

## /posts/\${ID}/

### Method: `POST`

Not Allowed

### Method: `GET`

Returns a detailed view of post with id `${ID}`

#### Auth:

Access is only given when the following is criteria is met:

Requesting profile:

- IsAdmin, or
- IsAuthenticated, and is following Profile that owns post with `id == ${ID}`, or
- Profile that owns post with `id == ${ID}` is not private

### Method: `PUT`

Makes a full update of post with `id == ${ID}`

#### Auth:

Access is only given when the following is criteria is met:

Requesting profile:

- IsAdmin, or
- IsAuthenticated, and is Profile that owns post with `id == ${ID}`

### Method: `PATCH`

Makes a partial update of post with `id == ${ID}`

#### Auth:

Access is only given when the following is criteria is met:

Requesting profile:

- IsAdmin, or
- IsAuthenticated, and is Profile that owns post with `id == ${ID}`

### Method: `DELETE`

Destroys post with `id == ${ID}`

#### Auth:

Access is only given when the following is criteria is met:

Requesting profile:

- IsAdmin, or
- IsAuthenticated, and is Profile that owns post with `id == ${ID}`
