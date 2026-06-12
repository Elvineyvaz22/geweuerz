# EyDost eSIM Influencer Scoring Tool

This tool analyzes influencer CSV exports and scores travel/eSIM partnership candidates for EyDost eSIM.

It does not search the internet. The first version works with CSV exports from tools such as Wednesday, Modash, Heepsy, TikTok, Instagram, YouTube, or manual research lists.

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

Score a CSV and export Excel:

```bash
python src/main.py filter --input influencers.csv --output filtered_influencers.xlsx
```

Create an empty CSV template:

```bash
python src/main.py template --output influencers_template.csv
```

Run tests:

```bash
pytest
```

## CSV Columns

The script accepts different source column names and maps them automatically.

Supported canonical columns:

```csv
name,username,platform,followers,engagement_rate,country,bio,email,avg_views,posts,profile_url
```

Accepted aliases include:

- `name`, `full_name`, `creator_name`
- `username`, `handle`, `profile`
- `platform`, `social_network`, `channel`
- `followers`, `followers_count`, `audience_size`
- `engagement_rate`, `engagement`, `er`
- `country`, `location`, `audience_country`
- `bio`, `description`, `about`
- `email`, `contact_email`, `business_email`
- `avg_views`, `views`, `average_views`
- `posts`, `post_count`
- `url`, `profile_url`, `link`

Example:

```csv
creator_name,handle,social_network,audience_size,er,audience_country,description,business_email,average_views,post_count,link
Lena Travels,@lenatravels,Instagram,42K,4.8%,Germany,"Budget travel, Europe travel and airport tips",lena@example.com,21000,240,https://instagram.com/lenatravels
```

## Scoring Logic

Total score is 100 points.

### Niche Match - 30 points

Positive keywords:

`travel`, `traveler`, `travelling`, `backpacking`, `digital nomad`, `airport`, `flight`, `visa`, `trip`, `hotel`, `itinerary`, `europe travel`, `turkey travel`, `esim`, `roaming`, `internet abroad`, `data`, `remote work`, `expat`

Negative keywords reduce score:

`crypto`, `forex`, `casino`, `betting`, `adult`, `giveaway only`, `meme only`, `fake followers`

### Audience Size - 20 points

- 5,000-150,000 followers: 20
- 150,001-500,000: 14
- 500,001-1,000,000: 8
- 1,000,000+: 4
- 1,000-4,999: 8
- 0-999: 2

### Engagement - 20 points

- 5%+: 20
- 3%-5%: 16
- 1.5%-3%: 10
- 0.5%-1.5%: 5
- 0%-0.5%: 1

### Contactability - 10 points

- Email exists: 10
- Bio has `DM for collab`, `partnership`, `business`, or similar: 6
- No contact signal: 0

### Geography Fit - 10 points

Strong fit:

EU, UK, Turkey, USA, UAE, Azerbaijan, Germany, France, Italy, Spain, Netherlands, Poland, Georgia.

### View Efficiency - 10 points

If `avg_views` exists:

- `avg_views / followers > 0.5`: 10
- `0.2-0.5`: 7
- `0.1-0.2`: 4
- `<0.1`: 1

If `avg_views` is missing: 3.

## Grades

- `A - priority partner`: score >= 75
- `B - good candidate`: 60-74
- `C - maybe test`: 45-59
- `D - skip`: <45

## Excel Output

The workbook has two sheets:

1. `Filtered Influencers`
2. `Summary`

The influencer sheet is sorted by score descending. Headers are bold, first row is frozen, columns are auto-sized, and grade rows are color-coded.

## EyDost Ideal Influencer Profile

Best candidates are micro and mid-level creators with:

- Travel, airport, flight, eSIM, roaming, remote work, expat, Europe travel, Turkey travel, budget travel, solo travel, family travel, or student travel content.
- 5,000-150,000 followers as the primary sweet spot.
- 3%+ engagement rate, ideally 5%+.
- Good avg views relative to follower count.
- Audience in EU, UK, Turkey, USA, UAE, Azerbaijan, Germany, France, Italy, Spain, Netherlands, Poland, or Georgia.
- Public business email or clear partnership signal in bio.

## Outreach Approach

EyDost is not only buying customers directly. The goal is to recruit partner creators.

Suggested offer:

- Creator posts a video, story, tag, or travel tip mentioning EyDost eSIM.
- EyDost adds ad budget to the creator's content, for example `$100-$150`.
- Creator can also receive commission, bonus, or recurring partnership terms.
- Start with A and B grade creators, then test selected C grade creators with small budgets.

