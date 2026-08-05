# Agnes AI Pricing and Limits

## Current Pricing (Free Tier)

| Type | Standard Price | Current Price |
|------|---------------|---------------|
| Image generation | $0.003/image | **$0/image** |
| Video duration | $0.005/second | **$0/second** |

Both image and video generation are currently free.

## Access Types

| Type | Description |
|------|-------------|
| Free / Default | No subscription, no enterprise verification |
| Enterprise Verified | Completed enterprise verification, higher baseline limits |
| Token Plan | Subscribed to a Token Plan, higher RPM + quotas |

Each API key type uses a separate limit pool.

## Text Model RPM Limits

| User Type | Allowed RPM | Effective RPM |
|-----------|-------------|---------------|
| default | 30 | 20 |
| enterprise | 60 | 40 |
| TokenPlan | 1000 | 1000 |

## Image Model RPM Limits

RPM varies by resolution tier. Higher resolutions have lower limits.

| User Type | 1K | 2K | 3K | 4K |
|-----------|-----|-----|-----|-----|
| default | 30 (eff. 20) | 20 (eff. 10) | 2 (eff. 1) | 1 (eff. 1) |
| enterprise | 60 (eff. 40) | 40 (eff. 20) | 2 (eff. 1) | 2 (eff. 1) |
| TokenPlan | 120 (eff. 100) | 120 (eff. 80) | 2 (eff. 1) | 2 (eff. 1) |

## Video Model RPM Limits

| User Type | Allowed RPM | Effective RPM |
|-----------|-------------|---------------|
| default | 2 | 1 |
| enterprise | 2 | 2 |
| TokenPlan | 6 | 5 |

## Token Plan Quotas

| Plan | Text (agnes-2.5-flash) | Image (2.1-flash) | Video (v2.0) |
|------|----------------------|-------------------|--------------|
| Starter | 1,500 req / 5hr; 15,000 / week | 4,000 images / day | 500 seconds / day |
| Plus | 7,500 req / 5hr; 75,000 / week | 4,000 images / day | 500 seconds / day |
| Pro | 30,000 req / 5hr; 300,000 / week | 4,000 images / day | 500 seconds / day |

### Counting Method

- Text models: counted by **request count**
- Image models: counted by **generated image count**
- Video models: counted by **generated video duration in seconds**

Both RPM limits and subscription quotas apply simultaneously.

## Limit Pool Rules

- Limits are shared by **API key type**, not by individual key
- Creating multiple keys of the same type does NOT increase total limits
- Different key types (free, enterprise, TokenPlan) use separate pools

## Key Takeaways

- Image and video generation are currently **free** ($0)
- Free users get 20 effective RPM for 1K images, 1 RPM for video
- For production use, subscribe to a Token Plan for higher limits
- 3K/4K image resolutions have very strict limits across all user types
- Use `size: "2K"` with `ratio: "16:9"` for 1080p-class output (2624x1472)
