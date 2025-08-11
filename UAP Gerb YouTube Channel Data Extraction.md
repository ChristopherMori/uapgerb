# UAP Gerb YouTube Channel Data Extraction

## 📊 Data Overview

- **Total Videos Extracted:** 43 unique videos
- **Channel:** [@UAPGerb](https://www.youtube.com/@UAPGerb)
- **Channel Focus:** UFO/UAP documentaries, crash retrievals, government programs, whistleblower testimonies
- **Extraction Date:** August 11, 2025

## 📁 Generated Files

### 1. `uap_gerb_complete_results.json`
**Format:** JSON  
**Purpose:** Complete structured data for programmatic use  
**Contents:** All video metadata in machine-readable format

### 2. `uap_gerb_results.csv`
**Format:** CSV (Comma-Separated Values)  
**Purpose:** Spreadsheet-compatible format  
**Columns:**
- Title
- Video URL
- Video ID
- Embed URL
- HTML Embed Code
- Transcript Status

### 3. `uap_gerb_report.html`
**Format:** HTML  
**Purpose:** Professional web report for viewing  
**Features:**
- Clickable links to each video
- Copy-paste HTML embed codes
- Responsive design
- Summary statistics

### 4. `transcript_extraction_guide.md`
**Format:** Markdown  
**Purpose:** Guide for extracting transcripts using alternative methods  
**Includes:** Code examples, tool recommendations, batch processing instructions

## 📺 Data Structure

Each video entry contains the following fields:

```json
{
  "title": "Video title as it appears on YouTube",
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "video_id": "YouTube video identifier",
  "embed_url": "https://www.youtube.com/embed/VIDEO_ID",
  "html_embed": "<iframe>Complete HTML embed code</iframe>",
  "transcript_status": "Status of transcript extraction"
}
```

## 📋 Sample Video Data

```json
{
  "title": "The 1948 Aztec, New Mexico UFO Crash Retrieval",
  "url": "https://www.youtube.com/watch?v=QJxbyu-9Tj0",
  "video_id": "QJxbyu-9Tj0",
  "embed_url": "https://www.youtube.com/embed/QJxbyu-9Tj0",
  "html_embed": "<iframe width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/QJxbyu-9Tj0\" title=\"The 1948 Aztec, New Mexico UFO Crash Retrieval\" frameborder=\"0\" allow=\"accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share\" allowfullscreen></iframe>",
  "transcript_status": "Transcript extraction requires additional API access or tools like yt-dlp with proper configuration"
}
```

## 🎯 Content Categories

The 43 videos cover these main themes:

### UFO Crash Retrievals
- The 1948 Aztec, New Mexico UFO Crash Retrieval
- 1997 Peru UFO Crash Retrieval - the Story of Jonathan Weygandt
- The 1965 Kecksburg, Pennsylvania UFO Crash
- The 1974 Coyame, Mexico UFO Crash
- The 1933 Magenta, Italy UFO Crash
- The 1953 Kingman, Arizona UFO Crash
- The 1950s Del Rio, Texas UFO Crashes

### Government & Military Programs
- UFO Legacy Programs - Science Applications International Corporation (SAIC)
- US Navy UFO Crash Retrieval & Reverse Engineering Programs
- Deep Underground Military Bases (D.U.M.Bs.) - UFO Legacy Programs
- Dugway Proving Ground - UFO Legacy Programs
- UFO Legacy Programs - Northrop Grumman
- MOON DUST - The Pentagon's Secret UFO Programs

### Private Sector Involvement
- UFOs in the Private Sector - Lockheed Martin
- UFOs in the Private Sector - Battelle Memorial Institute

### Technology & Reverse Engineering
- Alien Reproduction Vehicle - TR-3B and the Flying Triangles
- Alien Reproduction Vehicle - the Testimony of Mark McCandlish
- UAP Reverse Engineering at Edwards Air Force Base [Redacted List Vol.2]
- Off-World Technologies Division – UAP Technology Reverse Engineering
- Philip J. Corso - US Army UFO Technology Research & Development

### Whistleblowers & Testimonies
- UFO Whistleblowers [Vol.1]
- UFO Whistleblowers [Vol.2]
- Michael Herrera - Insights into UAP Encounter and Black Program Insiders
- Michael Herrera: UFO Whistleblower (ft. Joeyisnotmyname)
- "US Special Forces Confession - I Recovered Crashed UFOs": Fact or Fiction?

### Historical Documents & Analysis
- The Majestic-12 Documents [With Ryan S. Wood]
- The Wilson Davis Memo and US Secret UFO Reverse Engineering Programs
- Dr. Robert Sarbacher & the US Government's Secret UFO Crash Retrieval Group

### Phenomena & Encounters
- USO Case Book: Unidentified Submerged Objects Throughout History
- USO - Unidentified Submerged Objects
- Global Air Force UFO Encounters You've Probably Never Heard of
- UFOs and Nuclear Weapons - A Fascinating Connection
- The Marines Who Got too Close to UFOs
- The First Commercial Flight Grounded Due to UFOs
- FASTWALKERS – UFOs Outside Earth

### Analysis & Commentary
- The Physics of UFOs– Dr. Kevin Knuth
- SOL Foundation: Karl Nell - A Key Figure in UAP Disclosure
- The Modern Day UFO Disinformation Agent - Dr. Sean Kirkpatrick's Lies
- The Origin of the UFO Stigma

### Video Evidence
- Incredible UFO Footage - METAPOD
- Incredible UFO Footage - FLYBY

### Comprehensive Studies
- The Alien and UFO Obscure Oddities Iceberg (Level 1)
- The Alien and UFO Obscure Oddities Iceberg (Level 2)

## 💡 How to Use This Data

### For Website Embedding
```html
<!-- Copy the html_embed field directly -->
<iframe width="560" height="315" src="https://www.youtube.com/embed/QJxbyu-9Tj0" title="The 1948 Aztec, New Mexico UFO Crash Retrieval" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
```

### For Direct Links
```markdown
[Watch: The 1948 Aztec, New Mexico UFO Crash Retrieval](https://www.youtube.com/watch?v=QJxbyu-9Tj0)
```

### For API Integration
```javascript
const videoId = "QJxbyu-9Tj0";
const embedUrl = `https://www.youtube.com/embed/${videoId}`;
```

### For Batch Processing
- Use the CSV file for spreadsheet operations
- Use the JSON file for programmatic processing
- Use video IDs for API calls

## ⚠️ Transcript Status

**Current Status:** Transcripts were not extracted due to API limitations

**Alternative Methods:**
1. **yt-dlp** (recommended for batch processing)
2. **youtube-transcript-api** (local environment)
3. **Browser extensions**
4. **Manual extraction**

See `transcript_extraction_guide.md` for detailed instructions.

## 📈 Statistics

- **Total Videos:** 43
- **Successful URL Extraction:** 100%
- **HTML Embed Generation:** 100%
- **Transcript Extraction:** 0% (due to API limitations)
- **Data Formats Generated:** 4 (JSON, CSV, HTML, Markdown)

## 🔗 Quick Access

All videos are from the UAP Gerb channel focusing on:
- Government UFO programs and cover-ups
- Military encounters and testimonies
- Historical crash retrievals
- Reverse engineering efforts
- Whistleblower accounts
- Scientific analysis of UFO phenomena

The data provides a comprehensive collection of one of YouTube's most thorough UFO research channels, with all necessary information for embedding, linking, and further analysis.

