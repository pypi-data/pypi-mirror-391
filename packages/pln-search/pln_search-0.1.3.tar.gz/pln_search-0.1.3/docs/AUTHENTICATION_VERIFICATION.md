# Authentication Verification

## Summary

We successfully verified that the `authToken` cookie value works as a Bearer token for API authentication.

## Actual API URL

**Correct**: `https://api-directory.plnetwork.io`
**Not**: `https://api.plnetwork.io` or `https://api.pln.network`

Discovered via browser network inspection.

## How Authentication Works

1. **Web Frontend**: Uses Privy for authentication
2. **Tokens Stored in Cookies**:
   - `authToken` - JWT access token
   - `refreshToken` - JWT refresh token
   - `userInfo` - User details (JSON)

3. **API Requests**: Frontend extracts `authToken` cookie value and sends as:
   ```
   Authorization: Bearer <authToken_value>
   ```

## Verification Tests

### Test 1: Public Endpoint (No Auth Required)
```bash
GET /health
Status: 200 OK
```
✓ API is accessible

### Test 2: Basic Member Data (Works With Token)
```bash
GET /v1/members?limit=1
Authorization: Bearer <token>
Status: 200 OK
Response: { "count": 2545, "members": [...] }
```
✓ Token works for basic requests

### Test 3: Protected Endpoint - Office Hours Follow-ups

**Without Token:**
```bash
GET /v1/members/cldvoeb84073du21k5k3eaw1u/interactions/follow-ups
Status: 401 Unauthorized
Response: {"statusCode":401,"message":"Invalid Session. Please login and try again"}
```

**With Token:**
```bash
GET /v1/members/cldvoeb84073du21k5k3eaw1u/interactions/follow-ups
Authorization: Bearer eyJhbGc...
Status: 200 OK
Response: [{ "uid": "...", "status": "PENDING", ... }]  // 7 follow-ups returned
```

✓ **Token successfully authenticates protected endpoints**

### Test 4: User Profile Data

```bash
GET /v1/members/cldvoeb84073du21k5k3eaw1u
Authorization: Bearer <token>
Status: 200 OK
Response:
{
  "name": "Danny O'Brien",
  "email": "danny@fil.org",
  "accessLevel": "L6",
  ...
}
```
✓ Token retrieves authenticated user data including email

## Conclusion

The manual token extraction workflow is **fully functional**:

1. User logs into https://directory.plnetwork.io/
2. User copies `authToken` cookie value from DevTools
3. User runs `pln-search auth token --interactive`
4. User pastes token
5. CLI uses token as Bearer auth for API requests
6. ✓ Authentication works!

## Note on `/v1/members/search` Endpoint

The `/v1/members/search` endpoint returns 404, suggesting it may not exist in production or is under a different path. The standard `/v1/members` endpoint with query parameters works fine for searching members.
