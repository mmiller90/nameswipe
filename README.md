# NameSwipe

A private web app for swiping through baby names together. Swipe right to keep a name, left to pass. Names that both Michael and Rebecca keep show up under **Our matches**.

- **Names:** every name that made the U.S. Social Security Administration's top 1,000 for boys or girls in any year from 1890 to 2025 (3,588 boy names, 4,175 girl names). Source: [SSA baby names](https://www.ssa.gov/oact/babynames/limits.html).
- **Data and password:** stored in Supabase. The keys in `config.js` are public by design; the database only answers to someone signed in with the family password.
- **Install:** open the site on a phone, then use Safari's Share → *Add to Home Screen* (iPhone) or Chrome's ⋮ menu → *Add to Home screen* / *Install app* (Android).

## Files

| File | What it is |
|---|---|
| `index.html` | The whole app: screens, styles, and swipe logic |
| `names.json` | Boy and girl name lists |
| `config.js` | Supabase address and public key |
| `supabase_setup.sql` | One-time database setup (run in Supabase's SQL Editor) |
| `vendor/` | Supabase's JavaScript library (MIT license) |
| `icons/`, `manifest.webmanifest` | Home-screen icon and install settings |

## Getting your data into R

In Supabase: **Table Editor → decisions → Export → CSV**. Columns: `user_id`, `gender`, `name`, `keep` (1 = keep, 0 = not keep), `updated_at`.

```r
library(readr); library(dplyr)
d <- read_csv("decisions.csv")
d |> filter(keep == 1) |> count(user_id, gender)
```
