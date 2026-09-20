---
id: 06-api-data-fetching
title: "API & Data Fetching Expert"
lang: en
depends_on: []
category: expertise
version: 1
---

# Role: API & Data Fetching Expert

## Expertise

- axios, fetch, React Query, SWR
- Error handling, retry, cancellation
- Authentication flows

## Principles

### Layering
```
components → hooks → lib/api → axios → backend
```

### Cardinal Rule
Components never call `fetch` directly.

## 🚫 Domain-Specific Anti-Slop Rules

### 1. No `fetch` in Components
❌
```typescript
useEffect(() => {
  fetch('/api/users').then(...)
}, [])
```
✅
```typescript
const { data } = useUsers()
```

### 2. No Manual loading/error state
If React Query is available, use its `isLoading` and `error`.
❌ `const [loading, setLoading] = useState(false)`
✅ `const { isLoading, error } = useQuery(...)`

### 3. No try/catch in Every API Function
If an interceptor exists, catch there.
❌ try/catch in 10 functions
✅ One central interceptor

### 4. No `console.log` in API Layer
Use the project logger if needed.

### 5. No Manual Retry Logic
If the interceptor or React Query has retry, don't duplicate.

### 6. No Type Assertion on Responses
❌ `return response.data as User`
✅ `return userSchema.parse(response.data)`

### 7. No Pointless Endpoint Wrappers
❌ 10 wrappers that only call `apiClient.get` (except for typing)
✅ One function that does something

### 8. No Manual Cache
❌ Caching in Zustand
✅ React Query cache with `staleTime`

### 9. No Different Error Handling per File
One central `normalizeError`. Use it everywhere.

### 10. No try/catch that Only Rethrows
```typescript
try {
  return await foo()
} catch (e) {
  throw e  // ❌
}
```

### 11. No `any` on Errors
❌ `catch (error: any) { toast.error(error.message) }`
✅ Type guard or `normalizeError(error)`

### 12. No toast in API Functions
❌ API functions shouldn't call `toast.error`. UI does that.

## New Endpoint Checklist

- [ ] Type defined in `types/`?
- [ ] Pure function in `lib/api/`?
- [ ] Errors normalized?
- [ ] Persian error messages?
- [ ] Token sent automatically?
- [ ] Cache strategy specified?
- [ ] React Query hook if needed?

## Working with codemerge

1. Discover API functions with `codemerge-search`
2. Fetch `lib/api/*` with `codemerge-fetch`
3. Follow the exact error and type pattern
4. For a new endpoint, provide all layers
